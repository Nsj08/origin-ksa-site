"""Retrieve UN Comtrade observations and publish the site data snapshot."""

import argparse
import csv
import io
import hashlib
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from pipeline.analysis import Partner, annual_indicators, headroom, sensitivity


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "pipeline/cache"
API = "https://comtradeapi.un.org/"
SOURCE = "https://comtradeplus.un.org/en/"
REFS = API + "files/v1/app/reference/"
RIYADH = ZoneInfo("Asia/Riyadh")
YEARS_REQUIRED = 5
PREVIEW_LIMIT = 500
SCOPE_REVISIONS = {"H4": "HS 2012", "H5": "HS 2017", "H6": "HS 2022"}
NONCOUNTRY_CODES = {129, 221, 290, 471, 472, 473, 490, 527, 568, 577, 636, 637,
                    697, 711, 837, 838, 839, 879, 899}
UNSPECIFIED_NAME = {"en": "Unspecified", "ar": "غير محدد"}
DOMESTIC_NOTE = {
    "en": "No domestic production volumes are available here, so the share of Saudi demand met by imports is unknown.",
    "ar": "لا تتوفر هنا بيانات عن حجم الإنتاج المحلي، لذلك لا نعرف حصة الواردات من الطلب السعودي.",
}


def load_json(path):
    return json.loads(path.read_bytes(), parse_float=Decimal)


def atomic_write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(body)
        name = temporary.name
    try:
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def save_json(path, document):
    atomic_write(path, (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode())


def query(year, hs6, api_key=None):
    params = {
        "period": year, "reporterCode": 682, "flowCode": "M", "cmdCode": hs6,
        "partner2Code": 0, "customsCode": "C00", "motCode": 0,
        "maxRecords": 100000 if api_key else PREVIEW_LIMIT, "includeDesc": "true",
    }
    endpoint = "data/v1/get" if api_key else "public/v1/preview"
    return f"{API}{endpoint}/C/A/HS?{urlencode(params)}"


def dataset(document):
    rows = document.get("data")
    if document.get("error") or not isinstance(rows, list) or document.get("count") != len(rows):
        raise ValueError("Invalid or incomplete Comtrade response")
    if len(rows) >= PREVIEW_LIMIT:
        raise ValueError("Record cap reached or unexpected rows for one HS-6/period")
    return rows


class Source:
    """Persist original successful responses, with rate limiting and retry."""

    def __init__(self, cache, offline=False, refresh=False):
        self.cache = cache
        self.offline = offline
        self.refresh = refresh
        self.key = os.environ.get("COMTRADE_API_KEY")
        self.last_request = 0.0

    def get(self, filename, url, validate, *, keyed=False):
        path = self.cache / filename
        if path.exists() and (not self.refresh or self.offline):
            return validate(load_json(path)), path
        if self.offline:
            return None, path

        headers = {"Accept": "application/json"}
        if keyed and self.key:
            headers["Ocp-Apim-Subscription-Key"] = self.key
        for attempt in range(4):
            time.sleep(max(0.0, self.last_request + 3.0 - time.monotonic()))
            self.last_request = time.monotonic()
            try:
                with urlopen(Request(url, headers=headers), timeout=25) as response:
                    body = response.read()
            except HTTPError as error:
                if error.code not in {429, 500, 502, 503, 504} or attempt == 3:
                    raise RuntimeError(f"{filename}: UN Comtrade returned HTTP {error.code}") from error
                retry_after = error.headers.get("Retry-After", "")
                time.sleep(max(5 * (attempt + 1), int(retry_after) if retry_after.isdigit() else 0))
                continue
            except (URLError, TimeoutError) as error:
                if attempt == 3:
                    raise RuntimeError(f"{filename}: UN Comtrade could not be reached") from error
                time.sleep(5 * (attempt + 1))
                continue
            result = validate(json.loads(body, parse_float=Decimal))
            if path.exists():
                previous = path.read_bytes()
                if previous != body:
                    accessed = datetime.fromtimestamp(path.stat().st_mtime, RIYADH).date()
                    digest = hashlib.sha256(previous).hexdigest()
                    archived = self.cache / "history" / str(accessed) / f"{path.stem}-{digest}.json"
                    if not archived.exists():
                        atomic_write(archived, previous)
            atomic_write(path, body)
            return result, path
        raise RuntimeError(f"{filename}: retrieval exhausted")


def reference(document):
    rows = document.get("results")
    if not isinstance(rows, list) or not rows:
        raise ValueError("UN Comtrade reference table has no results")
    return {str(row["id"]): row for row in rows}


def partner_for(row, partner_ref, arabic_names):
    code = str(row["partnerCode"])
    lookup = partner_ref.get(code)
    if lookup is None:
        raise ValueError(f"Partner {code} is absent from the Comtrade reference table")
    if lookup.get("isGroup") and int(code) not in NONCOUNTRY_CODES:
        # Group aggregates overlap underlying country observations and cannot
        # be a second partner. Their presence in this API query is unexpected.
        raise ValueError(f"Unexpected overlapping trade group for partner {code}")
    value = Decimal(str(row["primaryValue"]))
    if not value.is_finite() or value < 0:
        raise ValueError(f"Invalid trade value for partner {code}")

    if int(code) in NONCOUNTRY_CODES:
        return Partner(code, UNSPECIFIED_NAME, value, unspecified=True)
    english = lookup["text"].strip()
    iso = (lookup.get("PartnerCodeIsoAlpha2") or "").strip()
    if code == "412":
        iso = "XK"  # Kosovo in the Comtrade partner reference
    arabic = arabic_names.get(iso)
    if not arabic:
        raise ValueError(f"Partner {code} ({english}) needs an Arabic display name")
    return Partner(code, {"en": english, "ar": arabic}, value)


def verify_references(config, commodity_refs):
    """Confirm that every configured code exists in the reference revisions."""
    by_heading = {}
    for product in config:
        code = product["hs6"]
        if len(code) != 6 or not code.isascii() or not code.isdigit():
            raise ValueError(f"Invalid HS-6 code {code}")
        by_heading.setdefault(code[:4], set()).add(code)
    if sum(map(len, by_heading.values())) != len(config):
        raise ValueError("Duplicate HS-6 code in catalog")
    for revision, rows in commodity_refs.items():
        for heading, codes in by_heading.items():
            official = {code for code, row in rows.items()
                        if row.get("parent") == heading and row.get("aggrlevel") == 6}
            if not codes <= official:
                raise ValueError(f"Codes absent from reference {revision}: {', '.join(sorted(codes - official))}")


def observations(rows, year, hs6, references, arabic_names):
    """Validate one original-classification annual Saudi import series."""
    if not rows:
        return [], None, None
    revisions = set()
    by_code = {}
    for row in rows:
        if (row.get("reporterCode"), row.get("flowCode"), row.get("freqCode"),
            row.get("refYear"), row.get("cmdCode"), row.get("aggrLevel"),
            row.get("partner2Code"), row.get("customsCode"), row.get("motCode")) != (
                682, "M", "A", year, hs6, 6, 0, "C00", 0):
            raise ValueError("Unexpected Comtrade response dimensions")
        revision = row.get("classificationCode")
        if (revision not in SCOPE_REVISIONS or not row.get("isOriginalClassification")
                or hs6 not in references[revision]):
            raise ValueError(f"Unexpected or unverified classification {revision}")
        revisions.add(revision)
        code = row["partnerCode"]
        if code and (row.get("isReported") is not True or row.get("isAggregate") is not False):
            raise ValueError(f"Non-reported partner record {code} for {year} HS {hs6}")
        if code in by_code:
            raise ValueError(f"Duplicate partner {code} for {year} HS {hs6}")
        by_code[code] = row

    if len(revisions) != 1:
        raise ValueError(f"Mixed original classifications for {year} HS {hs6}")
    world_row = by_code.pop(0, None)
    if not world_row:
        raise ValueError(f"World check unavailable for {year} HS {hs6}")
    world = Decimal(str(world_row["primaryValue"]))
    if not world.is_finite() or world < 0:
        raise ValueError(f"Invalid World check for {year} HS {hs6}")
    partners = [partner_for(row, references["partner"], arabic_names) for row in by_code.values()]
    return partners, world, SCOPE_REVISIONS[revisions.pop()]


def make_product(config, notes, years, history):
    code = config["hs6"]
    revisions = sorted({year["revision"] for year in years})
    accessed = max((year["accessed"] for year in years), default=None)
    name = {lang: config["name"][lang] for lang in ("en", "ar")}
    scope_note = config.get("notes", notes.get(code, {}))
    return {
        "hs6": code, "family": config["family"], "name": name,
        "notes": {lang: f"{scope_note.get(lang, '')} {DOMESTIC_NOTE[lang]}".strip()
                  for lang in ("en", "ar")},
        "classification": "HS 2022",
        "content_type": "guidance",
        "source": {"url": SOURCE, "accessed": accessed, "revision": " / ".join(revisions) or None},
        "years": years, "makers": [], "lcgpa": {"approved": False, "status": "pending"},
        "headroom": headroom(history),
    }


def build(source, ending_year, lookback):
    config = load_json(ROOT / "pipeline/products.yaml")
    notes = load_json(ROOT / "src/content/products.json")
    arabic_names = load_json(ROOT / "pipeline/partners-ar.json")
    references = {
        revision: source.get(f"{file}.json", f"{REFS}{file}.json", reference)[0]
        for revision, file in [("partner", "partnerAreas")] + [(rev, rev) for rev in SCOPE_REVISIONS]
    }
    verify_references(config, {code: rows for code, rows in references.items()
                               if code != "partner" and rows is not None})

    products = []
    reconciliation = []
    for entry in config:
        hs6 = entry["hs6"]
        history = {}
        years = []
        for year in range(ending_year, ending_year - lookback, -1):
            rows, path = source.get(
                f"trade-{year}-{hs6}.json", query(year, hs6, source.key), dataset, keyed=True,
            )
            audit = {"hs6": hs6, "year": year, "status": "not_cached"}
            reconciliation.append(audit)
            if rows is None:
                continue
            accessed = datetime.fromtimestamp(path.stat().st_mtime, RIYADH).date().isoformat()
            audit.update({
                "status": "no_data", "rows": len(rows), "accessed": accessed,
                "input": f"pipeline/cache/{path.name}", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            })
            if not rows:
                continue
            absent = [code for code, table in references.items() if table is None]
            if absent:
                raise RuntimeError(f"Reference file(s) unavailable: {', '.join(absent)}")
            try:
                partners, world, revision = observations(rows, year, hs6, references, arabic_names)
            except ValueError as error:
                audit.update(status="invalid_observations", error=str(error))
                continue
            total = sum(p.value for p in partners)
            delta = total - world
            audit.update({
                "revision": revision, "world_usd": str(world),
                "partners_usd": str(total), "difference_usd": str(delta),
                "country_rows": sum(not p.unspecified for p in partners),
                "unspecified_rows": sum(p.unspecified for p in partners),
            })
            if total <= 0:
                audit["status"] = "no_positive_partner_values"
                continue
            if world <= 0 or abs(delta) / world > Decimal("0.01"):
                audit["status"] = "world_mismatch"
                continue
            result = annual_indicators(year, partners)
            if abs(sum(p["share"] for p in result["partners"]) - 1) > 0.01:
                raise ValueError(f"Shares do not sum to 1 for {hs6} in {year}")
            result.update({"accessed": accessed, "revision": revision})
            audit["status"] = "accepted"
            history[year] = partners
            years.append(result)
            if len(history) == YEARS_REQUIRED:
                break
        products.append(make_product(entry, notes, list(reversed(years)), history))
    return products, reconciliation


def write_fingerprints(records):
    output = io.StringIO(newline="")
    columns = ("hs6", "year", "accessed", "revision", "sha256")
    writer = csv.DictWriter(output, columns, extrasaction="ignore")
    writer.writeheader()
    for row in sorted(records, key=lambda r: (r["hs6"], r["year"])):
        if row["status"] == "accepted":
            writer.writerow(row)
    atomic_write(ROOT / "public/source-fingerprints.csv", output.getvalue().encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--offline", action="store_true", help="Use only existing raw cache files")
    modes.add_argument("--refresh", action="store_true", help="Refetch the raw files from the provider")
    parser.add_argument("--end-year", type=int, default=datetime.now(RIYADH).year - 1)
    parser.add_argument("--lookback", type=int, default=8, help="Maximum complete calendar years to query")
    args = parser.parse_args()
    if args.lookback < YEARS_REQUIRED:
        parser.error(f"--lookback must be at least {YEARS_REQUIRED}")
    try:
        products, audit = build(Source(CACHE, args.offline, args.refresh), args.end_year, args.lookback)
    except (RuntimeError, ValueError, KeyError) as error:
        sys.exit(str(error))
    from jsonschema import Draft202012Validator, FormatChecker
    schema = json.loads((ROOT / "pipeline/products.schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(products)
    save_json(ROOT / "src/data/products.json", products)
    save_json(ROOT / "src/data/sensitivity.json", sensitivity(products))
    save_json(ROOT / "docs/TRADE_RECONCILIATION.json", audit)
    # A public release carries the original fingerprints from its private review.
    if not (ROOT / "pipeline/release-pin.json").exists():
        write_fingerprints(audit)
    accepted = sum(item["status"] == "accepted" for item in audit)
    print(f"Accepted {accepted} product-years across {len(products)} products")
    for item in audit:
        if item["status"] in {"world_mismatch", "invalid_observations"}:
            print(f"Skipped {item['hs6']} in {item['year']}: {item['status']} {item.get('error', '')}")


if __name__ == "__main__":
    main()
