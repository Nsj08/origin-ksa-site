"""Read the owner's review ledgers. Only the literal 'yes' grants publication."""
import csv
import datetime
import json
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FIELDS = "hs6 claim source evidence checked confidence approved name claim_ar name_ar document document_date page status".split()
PUBLISHED_FIELDS = {
    "makers": ("name", "name_ar", "claim", "claim_ar", "source", "checked"),
    "lcgpa_matches": ("status", "claim", "claim_ar", "source", "document", "document_date", "page", "checked"),
}


def published_columns(name):
    return ("hs6", "approved", *PUBLISHED_FIELDS[name])


def ledger(name, folder=None):
    path = (folder or ROOT / "review") / (name + ".csv")
    published = False
    # A shortened CSV in the owner's review folder must never waive evidence validation.
    # Earlier release trees used the same full ledger format as the private project.
    if folder is None and not path.exists():
        pin = ROOT / "pipeline/release-pin.json"
        if pin.is_file() and json.loads(pin.read_text()).get("review_format") == "approved-v1":
            path = ROOT / "review/approved" / (name + ".csv")
            published = True
    columns = published_columns(name) if published else FIELDS
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != list(columns):
            raise ValueError(f"{path.name}: incorrect column names")
        rows = list(reader)
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"{path.name}: malformed row")
        if row["approved"] not in ("yes", "no", ""):
            raise ValueError(f"{path.name}: approval must be blank, no or yes")
        if published and row["approved"] != "yes":
            raise ValueError(f"{path.name}: public release rows must have owner approval")
        if not row["hs6"].isdigit() or len(row["hs6"]) != 6:
            raise ValueError(f"{path.name}: invalid product code")
        if not published and not 0 < len(row["evidence"].split()) < 15:
            raise ValueError(f"{path.name}: evidence must contain 1–14 words")
        if urlsplit(row["source"]).scheme != "https" or not urlsplit(row["source"]).hostname:
            raise ValueError(f"{path.name}: a secure source URL is required")
        datetime.date.fromisoformat(row["checked"])
        if name == "lcgpa_matches":
            host = urlsplit(row["source"]).hostname
            if not (host == "lcgpa.gov.sa" or host.endswith(".lcgpa.gov.sa")):
                raise ValueError("List evidence must come from LCGPA")
            if not row["document"] or not row["page"] or row["status"] not in ("listed", "not_found"):
                raise ValueError("List decisions require a document, page and result")
            datetime.date.fromisoformat(row["document_date"])
        elif not row["name"]:
            raise ValueError("Maker name missing")
        if not row["claim"] or not row["claim_ar"]:
            raise ValueError("Bilingual source description missing")
    if published:
        # Keep the same keys for build checks that consume both types of record.
        return [{key: row.get(key, "") for key in FIELDS} for row in rows]
    return rows


def project(products, makers, matches):
    indexed = {p["hs6"]: p for p in products}
    for p in products:
        p["makers"] = []
        p["lcgpa"] = {"approved": False, "status": "pending"}
    for row in makers + matches:
        if row["hs6"] not in indexed:
            raise ValueError("Review refers to an unknown product: " + row["hs6"])
    for row in makers:
        if row["approved"] == "yes":
            p = indexed[row["hs6"]]
            if any(m["name"] == row["name"] for m in p["makers"]):
                raise ValueError("Duplicate approved maker")
            p["makers"].append({k: row[k] for k in PUBLISHED_FIELDS["makers"]})
    for row in matches:
        if row["approved"] == "yes":
            p = indexed[row["hs6"]]
            if p["lcgpa"]["approved"]:
                raise ValueError("Multiple approved list decisions for one product")
            p["lcgpa"] = {k: row[k] for k in PUBLISHED_FIELDS["lcgpa_matches"]}
            p["lcgpa"]["approved"] = True
    return products


def main():
    makers, matches = ledger("makers"), ledger("lcgpa_matches")
    print(f"Awaiting owner: {sum(not r['approved'] for r in makers)} maker rows, "
          f"{sum(not r['approved'] for r in matches)} list rows.")
    if sys.argv[1:] == ["count"]:
        return
    if sys.argv[1:] != ["apply"]:
        raise SystemExit("Usage: review.py count | apply")
    path = ROOT / "src/data/products.json"
    original = json.loads(path.read_text())
    result = project(json.loads(path.read_text()), makers, matches)
    if original != result:
        with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(f.name, path)


if __name__ == "__main__":
    main()
