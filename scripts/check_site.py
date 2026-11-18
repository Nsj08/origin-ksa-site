"""Fail the build on broken links, unapproved claims, fixture leakage or incomplete localisation."""
import copy
import gzip
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit
from review import ROOT, ledger, project


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def main():
    out = ROOT / "dist"
    failures = []
    en, ar = [json.loads((ROOT / f"src/i18n/{lang}.json").read_text()) for lang in ("en","ar")]
    if set(en) != set(ar) or not all(isinstance(v, str) and v.strip() for v in [*en.values(),*ar.values()]):
        failures.append("Translation dictionaries differ or contain empty values")
    for f in (ROOT / "src").rglob("*"):
        if not f.is_file() or f.suffix not in (".ts",".astro",".js",".json",".css"):
            continue
        raw = f.read_text()
        if re.search(r"(?:^|[/'\".])(?:tests/fixtures|pipeline/cache|review/(?:makers|lcgpa_matches)\.csv)", raw):
            failures.append(f"Production input references a private build input: {f.relative_to(ROOT)}")
        if f.suffix == ".astro":
            template = raw.split("---",2)[-1]
            template = re.sub(r"<(script|style)\b.*?</\1>","",template,flags=re.S|re.I)
            literals = re.findall(r">\s*([^<>{}\n]*[a-zA-Z\u0621-\u064a][^<>{}\n]*)\s*<",template)
            for literal in literals:
                literal = literal.strip()
                if literal and literal not in {"Origin KSA","منشأ"} and not re.search(r"[=;%]|=>",literal):
                    failures.append(f"Move interface text into i18n/content: {f.name}: {literal[:90]}")
    products = json.loads((ROOT/"src/data/products.json").read_text())
    from jsonschema import Draft202012Validator, FormatChecker
    Draft202012Validator(json.loads((ROOT/"pipeline/products.schema.json").read_text()), format_checker=FormatChecker()).validate(products)
    makers, lists = ledger("makers"), ledger("lcgpa_matches")
    approved = project(copy.deepcopy(products),makers,lists)
    if products != approved:
        failures.append("Published product approval data diverges from the owner ledgers")
    by_code = {p["hs6"]:p for p in products}
    raws = [f for f in (ROOT/"tests/fixtures").rglob("*") if f.is_file()]
    fixture_digests = {hashlib.sha256(f.read_bytes()).digest() for f in raws}
    # Detect fixture canaries even if a file was renamed, copied or included in a JS bundle.
    canaries = set(re.findall(r'ORIGINKSA_TEST_ONLY_[A-Z0-9_]+', ''.join(f.read_text(errors="ignore") for f in raws)))
    if not canaries:
        failures.append("Fixture isolation requires at least one fixture canary")
    private_terms = {r[k].casefold() for r in makers+lists for k in ("name","name_ar","claim","claim_ar") if r[k] and r["approved"]!="yes"}
    accepted_terms = {r[k].casefold() for r in makers+lists for k in ("name","name_ar","claim","claim_ar") if r[k] and r["approved"]=="yes"}
    settings = json.loads((ROOT/"site.config.json").read_text())
    domain = urlsplit(os.environ.get("SITE_URL", settings["url"]))
    base = domain.path.rstrip("/")
    pages = {}
    for f in out.rglob("*"):
        if not f.is_file(): continue
        data=f.read_bytes()
        rel=f.relative_to(out).as_posix()
        if hashlib.sha256(data).digest() in fixture_digests or any(x.encode() in data for x in canaries) or re.search(r'(?:^|/)(?:fixtures|cache|review|tests)(?:/|$)',rel):
            failures.append("Private/test material shipped: "+rel)
        if f.suffix not in {".html",".js",".json",".csv",".xml",".svg"}: continue
        raw=html.unescape(data.decode("utf8"))
        if any(term in raw.casefold() for term in private_terms - accepted_terms):
            failures.append("Unapproved source statement in "+rel)
        if f.suffix==".html":
            pages[f]=Page(data.decode())
    paths={p:{attrs["id"] for _,attrs in pg.tags if "id" in attrs} for p,pg in pages.items()}
    for f,pg in pages.items():
        rel=f.relative_to(out).as_posix()
        address = '/'+rel.removesuffix("index.html")
        origin=domain.scheme+"://"+domain.netloc
        js_size=0
        product_match=re.search(r"/(en|ar)/product/(\d{6})/",address)
        if product_match:
            lang, code = product_match.groups()
            public_product = by_code[code]
            locale = en if lang == "en" else ar
            expected_makers = sorted(m["name"] for m in public_product["makers"])
            seen_makers = sorted(a.get("data-maker-name","") for _,a in pg.tags if "data-maker-hs" in a)
            if seen_makers != expected_makers: failures.append("Maker section deviates from approved rows: "+rel)
            expected_list = public_product["lcgpa"]
            texts = " ".join(pg.text).casefold()
            if not expected_list["approved"] and any(locale[key].casefold() in texts for key in ("product.listed","product.notFound")):
                failures.append("Unapproved national-list language in "+rel)
            for row in makers:
                if row["name"] not in expected_makers and (row["name"].casefold() in texts or (row["name_ar"] and row["name_ar"].casefold() in texts)):
                    failures.append("Maker outside approved product scope in "+rel)

        if len([1 for tag,_ in pg.tags if tag=="h1"])!=1: failures.append("H1 count: "+rel)
        if any(re.search(r'\b(?:article|product|home|browse|search|common|footer)\.[A-Za-z]+',s.strip()) for s in pg.text if not s.lstrip().startswith("{")):
            failures.append("Unresolved translation key: "+rel)
        meta = {a.get("http-equiv", a.get("name", "")).lower(): a.get("content", "") for tag,a in pg.tags if tag == "meta"}
        policy = {parts[0]: parts[1:] for directive in meta.get("content-security-policy", "").split(";") if (parts := directive.split())}
        required = {"default-src": ["'none'"], "script-src": ["'self'"], "script-src-attr": ["'none'"], "object-src": ["'none'"], "base-uri": ["'none'"], "form-action": ["'self'"]}
        if any(policy.get(k) != v for k, v in required.items()) or meta.get("referrer") != "no-referrer":
            failures.append("Missing strict CSP or referrer policy: "+rel)
        for tag, a in pg.tags:
            if any(name.startswith("on") for name in a):
                failures.append("Inline event handler: "+rel)
            if tag == "script" and not a.get("src"):
                failures.append("Inline script: "+rel)
            if tag == "form" and (a.get("method", "get").lower() != "get" or urlsplit(urljoin(origin+base+address, a.get("action", ""))).netloc != domain.netloc):
                failures.append("Disallowed form destination or method: "+rel)
            if "formaction" in a or "formmethod" in a:
                failures.append("Unexpected form submit override: "+rel)
            if tag == "link" and set(a.get("rel","").lower().split()) & {"stylesheet","preload","modulepreload","icon","manifest","apple-touch-icon"}:
                resource = a.get("href", "")
            elif tag in {"img","script","source","audio","video","iframe","embed","object"}:
                resource = a.get("data" if tag == "object" else "src", "")
            else:
                resource = ""
            if resource and urlsplit(urljoin(origin+base+address, resource)).netloc != domain.netloc:
                analytics = settings["analytics"]
                optional_counter = analytics["provider"] == "goatcounter" and tag == "img" and resource.startswith("https://"+analytics["id"]+".goatcounter.com/count?")
                if not optional_counter:
                    failures.append("External embedded resource: "+rel)
            if 'data-maker-hs' in a and a.get('data-maker-name') not in {m["name"] for m in by_code.get(a['data-maker-hs'],{}).get("makers",[])}:
                failures.append("Unauthorized maker: "+rel)
            if 'data-list-status' in a:
                result=by_code.get(a.get('data-list-hs'),{}).get("lcgpa",{})
                if not result.get("approved") or result["status"]!=a["data-list-status"]: failures.append("Unauthorized list status: "+rel)
            ref = a.get('href') if tag in ('a','link') else a.get('src') if tag in ('img','script') else None
            if not ref or ref.startswith(('mailto:','tel:','data:')):continue
            target=urlsplit(urljoin(origin+base+address,ref))
            if target.netloc != domain.netloc:
                if tag=='a' and not {'noopener','noreferrer'}<=set(a.get('rel','').split()):
                    failures.append("External link lacks rel protections: "+rel+" "+ref)
                continue
            local=unquote(target.path)
            if base and not(local.startswith(base+'/') or local==base): failures.append("Preview-base escape: "+ref);continue
            dest=out/local[len(base):].lstrip('/')
            if dest.is_dir(): dest=dest/'index.html'
            if not dest.is_file(): failures.append("Missing internal target: "+rel+" "+ref)
            elif tag=="script": js_size+=len(gzip.compress(dest.read_bytes()))
            elif target.fragment and dest in paths and unquote(target.fragment) not in paths[dest]:
                failures.append("Missing fragment: "+rel+" "+ref)
        if '/product/' in address and js_size>=60000: failures.append("Product JS exceeds 60KB gzip: "+rel)
    for lang in ('en','ar'):
        for code in by_code:
            if out/lang/'product'/code/'index.html' not in pages: failures.append('Missing '+lang+'/'+code)
    if failures: sys.exit('\n'.join(sorted(set(failures))))
    print(f"Checked {len(pages)} HTML files, all internal links, both dictionaries, approval projections, fixture isolation and product JS budget.")


if __name__=="__main__":
    main()
