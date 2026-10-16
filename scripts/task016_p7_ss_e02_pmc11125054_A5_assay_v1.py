#!/usr/bin/env python3
"""A5 independent XML-DOM source assay crosscheck for PMC11125054.
No reading A4 outputs, no figure graph reconstruction or G6 admission.
"""
from __future__ import annotations
import json,sys,re
from datetime import datetime,timezone
from pathlib import Path
from xml.dom import minidom
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,ContractError
TASK="TASK-016-P7"
SOURCE="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-original/"
A3="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-A3/A3_publication_identity.json"
G5="outputs/task016-p7/v1/SS/E02/stages/batches/SS-E02-R2-PMC11125054/G5_FRESH_HOLDOUT_ACQUIRE.json"
OUT="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-A5/"
SELF="scripts/task016_p7_ss_e02_pmc11125054_A5_assay_v1.py"
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return sha_file(ROOT/p)
def save(p,x):
 if (ROOT/p).exists():raise ContractError("immutable A5 exists")
 write(TASK,p,json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def original():
 rr=json.loads((ROOT/(SOURCE+"raw_manifest.json")).read_text())["objects"]
 return next(r["path"] for r in rr if r["kind"]=="article_version")
def prereg():
 verify_stage_chain(G5,sha(G5))
 p=json.loads((ROOT/A3).read_text())
 if not p["publication_identity_verified"]:raise ContractError("A3 prerequisite not passed")
 path=original()
 save(OUT+"A5_pre_execution.json",dict(task=TASK,epoch_id="SS-E02",
  role="A5 independent code-path assay reading",
  at=now(),G5_sha256=sha(G5),A3_sha256=sha(A3),
  original_path=path,original_sha256=sha(path),code_sha256=sha(SELF),
  check_method="2.11 named donor and starting acceptors",
  check_result="3.9 named product classes and reported m/z",
  check_discussion="4.2 self-described reaction group",
  no_read_of_A4_output=True,no_read_of_model_outcome=True,
  no_HOLDOUT_reuse_next_epoch=True,
  text_only_not_full_graph=True,expect_A6_final_adjudication=True))
 print("A5 distinct XML DOM source check preregistered")
def node_text(node):
 return " ".join("".join(n.data for n in node.childNodes if n.nodeType==n.TEXT_NODE).split()) if node else ""
def deeptext(node):
 if node.nodeType==node.TEXT_NODE:return node.data
 return "".join(deeptext(n) for n in node.childNodes)
def run():
 verify_stage_chain(G5,sha(G5))
 p=json.loads((ROOT/(OUT+"A5_pre_execution.json")).read_text())
 if sha(G5)!=p["G5_sha256"] or sha(SELF)!=p["code_sha256"] or sha(p["original_path"])!=p["original_sha256"]:
  raise ContractError("A5 preregistered bound source/code changed")
 dom=minidom.parse(str(ROOT/p["original_path"]))
 by_section={}
 for sec in dom.getElementsByTagName("sec"):
  direct_titles=[c for c in sec.childNodes if c.nodeType==c.ELEMENT_NODE and c.tagName=="title"]
  if not direct_titles:continue
  label=" ".join(deeptext(direct_titles[0]).split())
  if label.startswith(("2.11.","3.9.","4.2.")):
   paras=[c for c in sec.childNodes if c.nodeType==c.ELEMENT_NODE and c.tagName=="p"]
   by_section[label]=[" ".join(deeptext(c).split()) for c in paras]
 method=next((x for k,v in by_section.items() if k.startswith("2.11.") for x in v if "UDP-Glc" in x),None)
 results=next((x for k,v in by_section.items() if k.startswith("3.9.") for x in v if "kaempferol" in x),None)
 discussion=next((x for k,v in by_section.items() if k.startswith("4.2.") for x in v if "RchUGT169" in x and "quercetin" in x),None)
 checks=dict(
  method_names_UDPGlc=(method is not None and bool(re.search(r"UDP.Glc",method,re.I))),
  method_uses_aglycones=(method is not None and "kaempferol or quercetin" in method.casefold()),
  result_reports_flavonol_glucosides=(results is not None and "kaempferol glucoside" in results and "quercetin glucoside" in results),
  discussion_classifies_first_3O=(discussion is not None and "flavonol 3-O-glucosyltransferase" in discussion),
  method_does_not_claim_preexisting_3O_parent=(method is not None and not re.search(
    r"(?:kaempferol|quercetin).{0,12}3.O.(?:glucoside|galactoside)",method,re.I)))
 status="primary_assay_out_of_scope_SS_O2" if all(checks.values()) else "insufficient_for_out_of_scope_decision"
 out=dict(task=TASK,epoch_id="SS-E02",role="A5 independent original assay text review",
  source="PMC11125054",at=now(),status=status,
  source_original_sha256=sha(p["original_path"]),pre_execution_sha256=sha(OUT+"A5_pre_execution.json"),
  checks=checks,passed=sum(checks.values()),total=len(checks),
  source_quoted_evidence=dict(
   methods_2_11=method[:2600] if method else None,
   results_3_9=results[:2300] if results else None,
   discussion_4_2=discussion[:2300] if discussion else None),
  assay_acceptors_are_source_named_aglycones=True if all(checks.values()) else None,
  source_assay_not_3O_pre_glycosylated_acceptor=True if all(checks.values()) else None,
  source_reported_products_no_O2_SugarSugar_assignment=True if all(checks.values()) else None,
  source_chemical_reviewed_at_this_epoch=True,subsequent_epoch_exposed=True,
  no_full_graph_reconstruction=True,not_independent_human_review=True,
  does_not_read_A4_outputs=True,read_model_outcome=False,
  G6_admitted=0,SS_fresh=0,scientific_ABE_cells=0)
 save(OUT+"A5_independent_source_assay_screen.json",out)
 print(json.dumps(dict(status=status,checks=checks,G6=0),ensure_ascii=False))
if __name__=="__main__":
 {"pre":prereg,"run":run}[sys.argv[1]]()
