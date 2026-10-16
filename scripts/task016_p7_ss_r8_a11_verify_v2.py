"""SS-R8 A11 independent original-source SHA, site, phase and evidence audit.

Reparse original XML independently, do not trust A6 site claims without raw
paragraph witnesses. No new acquisition, MCTS or scoped structure prediction.
"""
import json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain
TASK="TASK-016-P7"; B=Path("outputs/task016-p7/v1")
R8=B/"SS/E02/fresh/SS-E02-R8-science-screen-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G6_IDENTITY_STRUCTURE_ADMIT.json"
V19=B/"report_snapshots/progress-v19.json"
OUT=B/"verification-v20-ss-r8-v2"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def local(e):return e.tag.rsplit("}",1)[-1]
def witness(path,ordinal):
 root=ET.parse(ROOT/path).getroot()
 body=next(e for e in root.iter() if local(e)=="body")
 p=[e for e in body.iter() if local(e)=="p"]
 t=" ".join("".join(p[ordinal-1].itertext()).split())
 return hashlib.sha256(t.encode()).hexdigest(),t
def main():
 if (ROOT/OUT).exists():raise RuntimeError("INDEPENDENT_R8_VERIFICATION_ALREADY_EXISTS")
 files=[V19,G4,G5,G6,R8/"A0_science_read_precontract.json",
   R8/"pre_read_exposure.json",R8/"A4/pre_execution.json",R8/"A4/source_body_screen.json",
   R8/"A5/pre_execution.json",R8/"A5/independent_body_scope_screen.json",
   R8/"A6/pre_execution.json",R8/"A6/source_scope_reconciliation.json"]
 inputs={str(p):sha(p) for p in files}
 prior=load(V19); a0=load(R8/"A0_science_read_precontract.json")
 a4=load(R8/"A4/source_body_screen.json")
 a5=load(R8/"A5/independent_body_scope_screen.json")
 a6=load(R8/"A6/source_scope_reconciliation.json")
 pre=load(R8/"pre_read_exposure.json")
 checks={};fail=[]
 def check(k,ok):
  checks[k]=bool(ok)
  if not ok:fail.append(k)
 check("v19_REPORT_baseline",sha(Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"))==prior["current_REPORT_sha"])
 check("v19_STATE_baseline",sha(Path("STATE.md"))==prior["current_STATE_sha"])
 check("all_v19_evidence_unchanged",all(sha(Path(p))==s for p,s in prior["evidence_SHA256"].items()))
 for name,path in (("G4",G4),("G5",G5),("G6",G6)):
  m=verify_stage_chain(ROOT/path,sha(path))
  check(name+"_stage_replay",m["stage"].startswith(name+"_"))
 check("R8_G5_is_new_not_rewritten",load(G5)["input_manifest_sha"]==sha(G4) and
   load(G6)["input_manifest_sha"]==sha(G5))
 check("G5_preread_exposure_SHA_bound",str(R8/"pre_read_exposure.json") in load(G5)["files"])
 check("A0_2_source_original_SHA",len(a0["planned_sources"])==2 and all(
   sha(Path(s["raw_original"]["path"]))==s["raw_original"]["sha256"] for s in a0["planned_sources"]))
 check("both_sources_permanently_pre_exposed",len(pre["source_universe"])==2 and
   all(s["source_exposure"]=="permanently_science_exposed_before_first_read" for s in pre["source_universe"]))
 check("dual_reader_source_identity", {s["source_id"] for s in a4["sources"]}=={
       s["source_id"] for s in a5["sources"]}=={"PMC5517534","PMC13387883"})
 evidence_ok=True;raw_ids={s["source_id"]:Path(s["raw_original"]["path"]) for s in a0["planned_sources"]}
 for row in a6["sources"]:
  raw=raw_ids[row["source_id"]]
  for e in row["evidence_pointers"]:
   digest,txt=witness(raw,e["paragraph_ordinal"])
   if digest!=e["paragraph_sha256"] or any(t.casefold() not in txt.casefold() for t in e["observed_literal_features"]):
    evidence_ok=False
 check("original_paragraph_SHA_and_required_context",evidence_ok)
 tea=next(r for r in a6["sources"] if r["source_id"]=="PMC5517534")
 t14=witness(raw_ids["PMC5517534"],14)[1].casefold()
 t18=witness(raw_ids["PMC5517534"],18)[1].casefold()
 check("tea_flavonol_7O_site_not_sugar_O2",("3,7" in t14 and "3-o-glucoside" in t14
  and "7-hydroxy" in t18 and "7_o" in tea["scope_disposition"].casefold()))
 carn=next(r for r in a6["sources"] if r["source_id"]=="PMC13387883")
 c36=witness(raw_ids["PMC13387883"],36)[1].casefold()
 check("carnation_transgenic_observation_not_reaction_certificate",
       "transgenic" in c36 and "sophorobiose" in c36 and carn["full_reaction_stereo_donor_structure_qualified"] is False)
 check("no_false_structural_qualification",a6["dual_complete_chemical_structure_extraction"] is False
  and all(not row["eligible_for_SS_E02_panel"] for row in a6["sources"]))
 check("zero_fresh_and_MCTS",a6["counts"]["fresh_admitted"]==a6["counts"]["new_MCTS"]==0)
 check("this_batch_no_HTTP_source_fetch",a0["new_HTTP"]==0 and a5["new_HTTP"]==0 and a4["no_new_HTTP"])
 check("global_budget_not_changed",prior["global_budget"]=={"HTTP":973,"bytes":1210583689})
 result={"task":TASK,"agent_role":"A11","timestamp":datetime.now(timezone.utc).isoformat(),
  "source_claim_scope":"only R8 two original source text screens; not full chemical graph qualification",
  "input_SHA256":inputs,"checks":checks,"passed":sum(checks.values()),"failed":len(fail),
  "errors":fail,"raw_verified_sources":2,"evidence_witnesses_verified":sum(len(x["evidence_pointers"]) for x in a6["sources"]),
  "source_O2_reaction_qualified":0,"new_fresh":0,"scientific_ABE_cells":0,
  "scientific_metrics":None,"source_exposure_irreversible":True,
  "human_reviewed":False,"P7_completed":False}
 write(TASK,str(OUT/"independent_R8_verification.json"),json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"independent_checks":len(checks),"passed":result["passed"],
   "failed":result["failed"],"evidence_witnesses":result["evidence_witnesses_verified"],
   "fresh":0},ensure_ascii=False))
 if fail:raise RuntimeError("INDEPENDENT_R8_FAILED "+",".join(fail))
if __name__=="__main__":main()
