"""Rebuild an approved public release's untracked chart inputs from the data provider."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / "pipeline/release-pin.json"


def digest(product):
    # Exclude mutable review decisions. Preserve every displayed trade value and its vintage.
    trade = {key: value for key, value in product.items() if key not in {"makers","lcgpa"}}
    return hashlib.sha256(json.dumps(trade,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()


def sensitivity_digest(sensitivity):
    view = {key: value for key, value in sensitivity.items() if key != "source"}
    return hashlib.sha256(json.dumps(view,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def verify(products, pins):
    if {p["hs6"] for p in products} != set(pins):
        raise ValueError("The reviewed product roster changed")
    for p in products:
        pin = pins[p["hs6"]]
        # The release retains the original review date after matching the economic content.
        p["source"]["accessed"] = pin["accessed"]
        for y in p["years"]:
            y["accessed"] = pin["years"].get(str(y["year"]))
        if digest(p) != pin["sha256"]:
            raise ValueError(f"Provider data no longer reproduce reviewed values for {p['hs6']}. Review the revision privately.")


def restore():
    if not PIN.exists():
        return
    pins = json.loads(PIN.read_text())
    path = ROOT / "src/data/products.json"
    if not path.exists():
        subprocess.run([sys.executable,"-m","pipeline.build","--end-year",str(pins["end_year"])],cwd=ROOT,check=True)
    products = json.loads(path.read_text())
    verify(products,pins["products"])
    path.write_text(json.dumps(products,ensure_ascii=False,indent=2)+"\n")
    sensitivity_path = ROOT/"src/data/sensitivity.json"
    sensitivity = json.loads(sensitivity_path.read_text())
    if sensitivity_digest(sensitivity) != pins["sensitivity_sha256"]:
        raise ValueError("Sensitivity results differ from the reviewed release")
    if "source" in sensitivity:
        sensitivity["source"]["accessed"]=max((p["source"]["accessed"] or "" for p in products),default="") or None
    sensitivity_path.write_text(json.dumps(sensitivity,ensure_ascii=False,indent=2)+"\n")

if __name__=="__main__":
    restore()
