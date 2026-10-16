#!/usr/bin/env python3
"""Bounded A8-style independent replay review of P7 Petunia SS proposal.
No network, fresh holdout, model outcomes, scientific admission or production edits.
Uses independently authored checks but the proposer-supplied isolated dispatcher.
"""
from __future__ import annotations
import ast, copy, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
BASE="outputs/task016-p7/v1/SS/E02_design/Petunia_scope_proposal_v1/"
OUT="outputs/task016-p7/v1/SS/E02_design/Petunia_A8_chatgpt_bounded_v1/"
FILES=[
 BASE+"scope_bank.json",BASE+"build_supports.json",
 BASE+"pre_execution_contract.v3.json",BASE+"build_replay.json",
 BASE+"boundary_results.json",BASE+"exact_templates.json",
 BASE+"final_engineering_check_results.json",BASE+"role_A7_final_manifest.json",
 "scripts/task016_p7_ss_petunia_scope_guard_v1.py",
 "flavoretro/glycoside_library_v7.py",
 "scripts/task016_p7_ss_petunia_a8_chatgpt_v1.py",
]
def sha(path):
 return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):
 return json.loads((ROOT/path).read_text())
def put(name,obj):
 from scripts.operate import write
 path=ROOT/OUT/name
 if path.exists(): raise RuntimeError("immutable A8 artifact exists "+str(path))
 write("TASK-016-P7",OUT+name,json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def utc():
 return datetime.now(timezone.utc).isoformat()
def register():
 for f in FILES:
  if not (ROOT/f).is_file(): raise FileNotFoundError(f)
  if f.endswith(".py"): ast.parse((ROOT/f).read_text())
 put("A8_pre_execution_manifest.json",dict(task="TASK-016-P7",
  role="A8 bounded independent reviewer, separate from A7",
  as_of=utc(),frozen_inputs={f:sha(f) for f in FILES},
  tests=["source support/family/identity/closure and role boundary",
   "two source support full precursor replay plus mapped reaction identity",
   "20 preregistered graph negatives replay independently",
   "A7 supplemental two synthetic positive controls replay",
   "disabled runtime and context fail-closed",
   "verify no promotion to G4/G9 or scientific transfer"],
  a7_outputs_seen=True,blind_review=False,
  no_new_chemical_source_review=True,read_holdout=False,read_model_outcome=False,
  no_network=True,no_git=True,no_runtime_mutations=True,expected_scientific_fresh=0))
 print("A8 preregistered",len(FILES),"SHA-bound files")
def check():
 from rdkit import Chem
 from scripts.task016_p7_ss_petunia_scope_guard_v1 import (
  apply_template,mapped_reference_path,side,dispatch_guard,raw_outcomes)
 from flavoretro.glycoside_library_v7 import apply_template as v7_apply
 m=read(OUT+"A8_pre_execution_manifest.json")
 for file,digest in m["frozen_inputs"].items():
  if sha(file)!=digest: raise RuntimeError("SHA drift: "+file)
 bank=read(BASE+"scope_bank.json")
 supports=read(BASE+"build_supports.json")
 plan=read(BASE+"pre_execution_contract.v3.json")
 controls=read(BASE+"boundary_results.json")
 synthetic=read(BASE+"final_engineering_check_results.json")
 a7=read(BASE+"role_A7_final_manifest.json")
 checks=[]
 def record(name,passed,detail):
  checks.append(dict(check=name,pass_check=bool(passed),detail=detail))
 t=bank[0] if len(bank)==1 else None
 record("unique_candidate_scope",t is not None,len(bank))
 if t is None: raise RuntimeError("invalid scope bank cardinality")
 src_ids=sorted({r["source_id"] for r in supports})
 groups=sorted({(r["source_id"],r["doi"]) for r in supports})
 acceptor_canon=sorted({Chem.MolToSmiles(Chem.MolFromSmiles(r["acceptor"]),isomericSmiles=True) for r in supports})
 record("source_support_cardinality",len(supports)==2 and len(acceptor_canon)==2,
  dict(supports=len(supports),distinct_acceptors=len(acceptor_canon)))
 record("source_role_provenance",all(
  r["source_qualified_design_support"] and r["dual_full_graph_complete"]
  and r["source_identity_verified"] and r["template_role"]=="development_build"
  and not r["fresh_eligible"] and not r["human_reviewed"] for r in supports),
  dict(source_ids=src_ids,source_groups=len(groups)))
 record("limited_scientific_scope",len(src_ids)==1 and len(groups)==1,
  "Single Petunia paper/assay closure; two acceptors do NOT imply two source groups or independent aglycones")
 record("pre_registered_negative_plan",len(plan["controls"])==20 and len(controls)==20
  and {x["control_id"] for x in plan["controls"]}=={x["control_id"] for x in controls},
  dict(planned=len(plan["controls"]),seen=len(controls)))
 role=t.get("template_role")=="scope_template" and t["scope"]["family"]=="SS"
 record("separate_exact_and_scope",role and "smarts" in t and len(read(BASE+"exact_templates.json"))==2,
  dict(template_role=t.get("template_role"),family=t["scope"].get("family")))
 support_details=[]
 for r in supports:
  expected=side([Chem.MolFromSmiles(r["acceptor"]),Chem.MolFromSmiles(r["donor"])])
  actual=apply_template(t,r["target"],context=r["required_context"])
  mapped=mapped_reference_path(t,r["target"])
  found=any(x["precursors"]==expected for x in actual)
  mapped_found=any(x["precursors"]==expected
   and x["original_target_maps_preserved"]
   and x["original_target_maps_unique"]
   and x["all_output_maps_nonzero"]
   and x["all_output_maps_unique"] for x in mapped)
  support_details.append(dict(id=r["instance_id"],matched=found,mapped_matched=mapped_found,
   outcome_count=len(actual),mapped_count=len(mapped)))
 record("independent_complete_support_replay",
  len(support_details)==2 and all(x["matched"] and x["mapped_matched"] for x in support_details),
  support_details)
 negative=[]
 for row in controls:
  target=row["target"]
  op=row["operation"]
  if op in ("namespace","center"):
   variant=copy.deepcopy(t)
   variant["scope"]["namespace" if op=="namespace" else "center_class"]="invalid_for_a8_negative"
   observed=apply_template(variant,target)
   ok=not observed
  elif row.get("precursor_override"):
   precursors=[Chem.MolFromSmiles(s) for s in row["precursor_override"].split(".")]
   raw=list(raw_outcomes(t,target))
   ok=all(p is not None for p in precursors) and bool(raw) and not dispatch_guard(
    t,Chem.MolFromSmiles(target),tuple(precursors))
   observed=[] if ok else ["failed_precursor_guard"]
  else:
   observed=apply_template(t,target)
   ok=not observed
   mapped=mapped_reference_path(t,target)
   ok=ok and not mapped
  negative.append(dict(id=row["control_id"],operation=op,
   checked_from_pre_registered_input=True,passed=ok,
   producer_reported_violation=row["violated"],observed_count=len(observed)))
 record("replayed_20_negative_controls",len(negative)==20 and all(x["passed"] for x in negative),negative)
 extra=[]
 for row in synthetic["results"][:2]:
  observed=apply_template(t,row["target"])
  mapped=mapped_reference_path(t,row["target"])
  accepted=any(x["precursors"]==row["expected_precursors"] for x in observed)
  mapped_ok=any(x["precursors"]==row["expected_precursors"] and x["all_output_maps_unique"]
   and x["original_target_maps_preserved"] for x in mapped)
  extra.append(dict(id=row["control_id"],passed=accepted and mapped_ok,
   is_source_support=False,is_fresh_holdout=False))
 record("independent_synthetic_OH_probe_replay",len(extra)==2 and all(x["passed"] for x in extra),extra)
 record("wrong_context_is_rejected",not apply_template(t,supports[0]["target"],
  context={"mode":"chemical","donor_name":"UDP-glucose"}),"Isolated dispatcher only")
 old=[v7_apply(t,r["target"]) for r in supports]
 record("production_not_yet_integrated",all(not x for x in old) and a7["formal_runtime_connected"] is False,
  "0/2 in existing v7, which is expected; not G9 passed")
 record("no_fresh_or_scientific_metrics",
  synthetic["MCTS"]==0 and a7["scientific_ABE_cells"]==0 and a7["scope_frozen"] is False,
  "design-only isolated verification, scientific panel=0")
 result=dict(task="TASK-016-P7",role="A8 independent bounded engineering review",
  timestamp=utc(),preregistered_manifest_sha256=sha(OUT+"A8_pre_execution_manifest.json"),
  status="pass_bounded_engineering_review" if all(x["pass_check"] for x in checks)
   else "failed_bounded_engineering_review",
  passed=sum(x["pass_check"] for x in checks),total=len(checks),checks=checks,
  source_closure_groups=len(groups),source_qualified_design_supports=len(supports),
  distinct_canonical_acceptors=len(acceptor_canon),source_supported_aglycones=1,
  G2_G3_G4_not_decided=True,A8_not_authorized_to_freeze_scope=True,
  source_identity_not_independently_re_read=True,
  A7_dispatcher_reused_for_replay=True,
  not_blind_to_A7_results=True,read_holdout=False,read_model_outcome=False,
  formally_registered_runtime=False,fresh_holdout=0,scientific_ABE_cells=0,
  metrics=None,actionable=False,evidence_closed=False,
  human_reviewed=False,independent_chemical_validation=False,
  unprocessed=["root G2/G3/G4 scientific and governance decision",
   "separate future fresh holdout sourced only AFTER genuine scope freeze",
   "at least 6 eligible fresh targets and 2 independent closure groups",
   "new runtime integration and scientific A/B/E"],
  outputs_from_A7_not_mutated=True)
 put("role_A8_bounded_review_manifest.json",result)
 if not all(x["pass_check"] for x in checks):
  raise SystemExit("A8 BOUNDED AUDIT HAS FAILURES: "+",".join(x["check"] for x in checks if not x["pass_check"]))
 print(json.dumps(dict(status=result["status"],passed=result["passed"],total=result["total"],
  ready_for_root_decision_only=True,scientific_fresh=0),ensure_ascii=False))
if __name__=="__main__":
 {"preregister":register,"audit":check}[sys.argv[1]]()
