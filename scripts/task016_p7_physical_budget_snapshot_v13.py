"""Capture an append-only physical source budget prefix without exposing HTTP headers."""
import json,hashlib
from pathlib import Path
from collections import Counter
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import BASE,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer

def capture(out):
    started=now(); prefix={}; found={}; ledger=[]
    paths=sorted(p for p in BASE.rglob("*") if p.is_file() and p.suffix in {".json",".jsonl"} and (p.name=="http_ledger.jsonl" or "http_attempt" in p.name))
    paths += [ROOT/"operations/events.jsonl",BASE/"run_ledger.jsonl",BASE/"epoch_ledger.jsonl"]
    for p in dict.fromkeys(paths):
        b=p.read_bytes(); rel=str(p.relative_to(ROOT))
        prefix[rel]=dict(prefix_byte_count=len(b),prefix_sha256=hashlib.sha256(b).hexdigest(),captured_at=now())
        rr=[json.loads(x) for x in b.splitlines() if x] if p.suffix==".jsonl" else json.loads(b)
        if p.name=="events.jsonl":rr=[r for r in rr if r.get("task")==TASK and r.get("action")=="source_http"]
        elif p.name in {"run_ledger.jsonl","epoch_ledger.jsonl"}:continue
        if not isinstance(rr,list):raise ValueError("HTTP ledger is not row list")
        ledger.append(dict(path=rel,record_count=len(rr)))
        for r in rr:
            key=(r["url"],r["started_at"],r["path"])
            if key in found and any(found[key].get(k)!=r.get(k) for k in ["sha256","bytes"]):raise ValueError("physical HTTP conflict")
            found[key]=r
    keys=["url","started_at","finished_at","path","sha256","bytes","kind","role","phase","status_code","status","error","batch_id"]
    records=[{k:r[k] for k in keys if k in r} for r in found.values()]
    total=Counter();families={f:Counter() for f in ["C","SS","root"]}
    for r in records:
        parts=Path(r["path"] or "").parts; f="SS" if "SS" in parts else "C" if "C" in parts else "root";c=families[f]; kind=r.get("kind",r.get("role"))
        c["HTTP"]+=1;c["bytes"]+=r["bytes"]
        c["article_legacy"]+=int(kind in {"xml","article_version"})
        c["article_expanded"]+=int(kind in {"xml","article_version","original_pdf"})
        c["attachments"]+=int(kind=="attachment")
        c["failed_or_redirect"]+=int(r.get("error") is not None or r.get("status_code")!=200)
    for c in families.values():total.update(c)
    ended=now()
    d=dict(task=TASK,approval_type="agent_delegated",human_reviewed=False,capture_started_at=started,capture_finished_at=ended,non_atomic_append_only_capture_window=True,source_intake_may_continue_after_capture=True,physical_prefixes=prefix,http_ledgers=ledger,physical_event_identity=["url","started_at","path"],physical_records=records,totals=dict(total),families={f:dict(v) for f,v in families.items()},article_counts_are_request_kinds_not_usable_papers=True,scientific_source_universe_denominator_pending=True,external_web_internal_HTTP="unobservable_separate",scientific_ABE_cells=0,metrics=None,new_HTTP=0,new_MCTS=0)
    immutable_json(out,d)
    print(json.dumps(dict(pointer=pointer(out),as_of=ended,totals=dict(total),families=d["families"])))
    return d
if __name__=="__main__":
    import sys
    capture(ROOT/sys.argv[1])
