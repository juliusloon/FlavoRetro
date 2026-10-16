"""P7 A11 independent R12 audit: recompute from frozen raw originals, not A6 counts."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R12-original-science-review-v3"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G6_IDENTITY_STRUCTURE_ADMIT.json"
OUT=B/"verification-v22-ss-r12/independent_R12_verification.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def paragraphs(p):
    tree=ET.parse(ROOT/p)
    body=next(e for e in tree.getroot().iter() if e.tag.rsplit("}",1)[-1]=="body")
    return [" ".join("".join(e.itertext()).split()) for e in body.iter() if e.tag.rsplit("}",1)[-1]=="p"]
def audit():
    checks={}
    p=read(R/"A0_science_read_precontract.json");pre=read(R/"pre_read_exposure.json")
    a3=read(R/"A3_front_identity.json")
    a4=read(R/"A4/source_body_screen.json");a5=read(R/"A5/independent_body_scope_screen.json")
    a6=read(R/"A6/source_scope_reconciliation.json")
    g4=read(G4);g5=read(G5);g6=read(G6)
    checks["G4_original_SHA"]=sha(G4)=="a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f"
    checks["G4_G5_G6_stage_chain"]=all(verify_stage_chain(ROOT/x,sha(x))["stage"]==s for x,s in [
        (G4,"G4_SCOPE_FREEZE"),(G5,"G5_FRESH_HOLDOUT_ACQUIRE"),(G6,"G6_IDENTITY_STRUCTURE_ADMIT")])
    checks["G5_precedes_independent_chemistry"]=p["registered_at"]<a4["timestamp"] and p["registered_at"]<a5["timestamp"]
    checks["exposure_pre_registered"]=pre["registered_at"]<a4["timestamp"] and pre["registered_at"]<a5["timestamp"] and pre["permanently_exposed_before_new_scientific_read"] is True
    checks["precontract_sha_inputs_replay"]=all(sha(Path(f))==s for f,s in p["input_SHA256"].items())
    checks["A3_dual_original_front_publication_identity"]=len(a3["results"])==2 and all(
      len(x["checks"])>=8 and all(x["checks"].values()) for x in a3["results"])
    checks["A4_A5_two_independent_reader_universe"]={x["source_id"] for x in a4["sources"]}=={x["source_id"] for x in a5["sources"]}=={"PMC5444469","PMC6813240"}
    checks["A4_A5_no_peer_read_claim"]=a4["read_model_outcome"] is False and a5["read_other_extractor"] is False
    checks["A6_no_automatic_graph_admission"]=a6["counts"]["full_dual_graph_qualified"]==0 and a6["counts"]["fresh_admitted"]==0 and a6["counts"]["outside_current_O2_scope"]==2
    checks["A6_anchor_original_SHA_and_exact_text"]=True
    checks["two_originals_distinct"]=True
    raw_hashes=[]
    for x in a6["sources"]:
        matching=[y for y in p["planned_sources"] if y["source_id"]==x["source_id"]]
        if len(matching)!=1:checks["two_originals_distinct"]=False;continue
        raw=Path(matching[0]["raw_original"]["path"])
        raw_hashes.append(sha(raw))
        if sha(raw)!=matching[0]["raw_original"]["sha256"]:
            checks["A6_anchor_original_SHA_and_exact_text"]=False
        paras=paragraphs(raw)
        for e in x["anchors"]:
            idx=e["paragraph_ordinal"]
            if idx<1 or idx>len(paras):
                checks["A6_anchor_original_SHA_and_exact_text"]=False;continue
            text=paras[idx-1]
            if e["original_sha256"]!=sha(raw) or e["text_sha256"]!=hashlib.sha256(text.encode()).hexdigest() or any(k.casefold() not in text.casefold() for k in e["literal_features"]):
                checks["A6_anchor_original_SHA_and_exact_text"]=False
    checks["two_originals_distinct"]=checks["two_originals_distinct"] and len(set(raw_hashes))==2
    checks["source_dispositions_no_fresh"]=all(x["current_epoch_fresh_qualified"] is False and x["exact_frozen_O2_reaction_supported"] is False for x in a6["sources"])
    checks["scope_SHA_unchanged"]=sha(B/"SS/E02/scope_manifest.json")=="c173c0e6aaee7dacfcb9195cbd481577703ecdebcd18aaf506b76b84e74e53b6"
    checks["G6_disposition_bound"]=any(str(R/"A6/source_scope_reconciliation.json")==k and sha(Path(k))==v for k,v in g6["files"].items())
    checks["no_new_science_ABE_or_MCTS"]=len((ROOT/B/"run_ledger.jsonl").read_text().splitlines())==214
    return checks
def main():
    if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_A11_EXISTS")
    checks=audit()
    x=dict(task=TASK,role="A11_independent_R12_source_science_audit",
       at=datetime.now(timezone.utc).isoformat(),checks=checks,passed=sum(checks.values()),
       failed=len(checks)-sum(checks.values()),fresh_admitted=0,
       scientific_ABE_cells=0,full_scientific_qualification=False,human_reviewed=False,
       evidence_SHA={str(p):sha(p) for p in [G4,G5,G6,R/"A3_front_identity.json",
       R/"A4/source_body_screen.json",R/"A5/independent_body_scope_screen.json",
       R/"A6/source_scope_reconciliation.json"]},
       no_G7_G8_or_new_runtime=True,
       limitations="R12 two-original source screen only; no global exposure alias clearance or full dual structure qualification")
    write(TASK,str(OUT),json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(dict(A11_pass=x["passed"],A11_fail=x["failed"],fresh=0)))
    if x["failed"]:raise RuntimeError([k for k,v in checks.items() if not v])
if __name__=="__main__":main()

