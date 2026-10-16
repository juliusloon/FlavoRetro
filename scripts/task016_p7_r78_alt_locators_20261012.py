"""R78 extension: preregistered alternative lawful locators for PMC3425182."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from scripts.operate import ROOT, write
from scripts.task016_p7_r78_trapero_custody_20261012 import (OUT, RAW, http_get, save_obj_row, _rows, canonical, counter)

T = "TASK-016-P7"

def now(): return datetime.now(timezone.utc).isoformat()

def prereg():
    p = ROOT / OUT / "query_plan.json"
    plan = json.loads(p.read_text())
    if "alt_locator_slots" in plan:
        print(json.dumps(dict(status="already_preregistered"))); return
    plan["alt_locator_slots"] = [
        dict(query_id="R78-CANON-01", kind="article_version",
             url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3425182/",
             reason="canonical PMC article page (R66 precedent: publicly viewable HTML for articles outside the OA bulk subset); custody of public page bytes; no content projection"),
        dict(query_id="R78-UPV-01", kind="article_version",
             url="http://hdl.handle.net/10251/87409",
             reason="UPV institutional repository handle advertised by Unpaywall; plain HTTP GET, no credentials; redirects NOT followed (no-redirect policy) so a 30x/Location is terminal and recorded"),
    ]
    write(T, str(OUT / "query_plan.json"), json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(status="preregistered", slots=len(plan["alt_locator_slots"]))))

def run():
    plan = json.loads((ROOT / OUT / "query_plan.json").read_text())
    for slot in plan["alt_locator_slots"]:
        if any(r["query_id"] == slot["query_id"] and r.get("status_code") for r in _rows("query_execution.jsonl")): continue
        rec = http_get(slot["url"], slot["kind"], slot["reason"])
        save_obj_row(slot["query_id"], rec)
        print(json.dumps(dict(q=slot["query_id"], status=rec.get("status_code"), bytes=rec.get("bytes"), err=rec.get("error"))), flush=True)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    if mode == "prereg": prereg()
    elif mode == "run": run()
    else: raise SystemExit("prereg | run")
