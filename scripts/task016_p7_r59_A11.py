"""A11: independent raw custody, worksheet and immutable-chain verification for v31."""
import json,hashlib,zipfile,posixpath,decimal,os,uuid
from pathlib import Path
from xml.dom import minidom
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now,gate
from scripts.task016_p7_c_e02_http import physical_attempts
from scripts.task016_p7_orchestrate import verify_hashes,verify_stage_chain,STAGES
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"verification-v31-official-tabular-SI-v1"
F=B/"SS/E02/fresh"
R54=F/"SS-E02-R54-Laportea-tabular-SI-custody-v1"
R55=F/"SS-E02-R55-Laportea-tabular-SI-custody-v1"
R56=F/"SS-E02-R56-Laportea-tabular-science-v1"
R57=F/"SS-E02-R57-Laportea-tabular-SI-custody-v1"
R58=F/"SS-E02-R58-declared-primary-PDF-custody-v1"
D=B/"governance/R54-SS-scope-registration-field-supplement-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R56-Laportea-tabular-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=G5.with_name("G6_IDENTITY_STRUCTURE_ADMIT.json")
BUD=B/"report_snapshots/progress-v31-physical-budget.v2.json"
NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
checks=[];inputs={}
def ck(n,ok,e=None):checks.append(dict(check=n,passed=bool(ok),evidence=e))
def inp(p):p=Path(p);inputs[str(p)]=sha(p);return p
def pre():
 assert not (ROOT/O).exists()
 ps=[R56/"pre_science_exposure_contract.json",R55/"raw_custody_summary.json",D/"agent_delegated_scope_field_supplement_decision.json",G5,G6,BUD,Path(__file__).resolve().relative_to(ROOT)]
 for r in (R54,R55,R57,R58):ps.extend([r/"precontract.json",r/"http_ledger.jsonl",r/"query_execution.jsonl"])
 for role in ("A4","A5","A6"):ps.append(R56/role/"role_manifest.json")
 ps.append(R56/"scientific_exposure_reads.jsonl")
 put(O/"pre_audit_contract.json",dict(task=T,agent_role="A11",approval_type="agent_delegated",human_reviewed=False,at=now(),family="SS",epoch_id="SS-E02",inputs={str(p):sha(p) for p in ps},raw_XLSX=load(R55/"raw_custody_summary.json")["raw_pointer"],G5=dict(path=str(G5),sha256=sha(G5)),new_source=False,new_chemical_qualification=False,read_holdout=True,read_model_outcome=False,future_epoch_fresh_eligible=False,source_current_epoch_eligibility="not_granted_by_audit",read_scope="Raw HTTP custody, all14 original named worksheet cells and immutable evidence chains; no external workbook fetching, formula evaluation, new graphs or science admission."))
 print(json.dumps(dict(preregistered=True,HTTP=0)))
def text(node):
 return "".join(n.data for n in node.childNodes if n.nodeType in (n.TEXT_NODE,n.CDATA_SECTION_NODE)) if node is not None else None
def elem(node,name,ns=NS):
 return [n for n in node.childNodes if n.nodeType==n.ELEMENT_NODE and n.localName==name and n.namespaceURI==ns]
def val(node,name):
 z=elem(node,name);return text(z[0]) or None if z else None
def run():
 assert not (ROOT/O/"independent_A11_tabular_and_access_audit.json").exists()
 contract=load(inp(O/"pre_audit_contract.json"));verify_hashes(contract["inputs"])
 for p in contract["inputs"]:inp(p)
 verify_stage_chain(ROOT/G5,sha(G5));verify_stage_chain(ROOT/G6,sha(G6))
 reader="A11-"+str(os.getpid())+"-"+uuid.uuid4().hex
 common=dict(task=T,reader_role="A11",reader_id=reader,approval_type="agent_delegated",human_reviewed=False,family="SS",epoch_id="SS-E02",source_id="10.1021/acs.jafc.4c00488",raw_files=[contract["raw_XLSX"]],G5=contract["G5"],development_exposed=True,prior_design=False,exposure_type="current_epoch_evaluation",current_epoch_eligibility="conditional_only_not_granted_by_audit",future_fresh_eligible=False,closure_tokens=["doi:10.1021/acs.jafc.4c00488","doi:10.1021/acs.jafc.4c00488.s001"])
 start=dict(common,event_type="scientific_audit_started",timestamp=now(),scientific_content_read=False)
 put(O/"scientific_audit_started.json",start)
 allnew=[]
 for folder,expected in [(R54,[200,302,403]),(R55,[302,200]),(R57,[200,200,200,200]),(R58,[403,403])]:
  rr=lines(inp(folder/"http_ledger.jsonl"));allnew+=rr
  ck(folder.name+"_physical_status_conservation",[r["status_code"] for r in rr]==expected)
  for r in rr:
   p=inp(r["path"]);data=(ROOT/p).read_bytes()
   ck(r["attempt_id"]+"_raw_SHA_bytes",sha(p)==r["sha256"] and len(data)==r["bytes"] and (ROOT/p).stat().st_mode&0o222==0)
  registrations=lines(inp(folder/"physical_request_preregistration.jsonl"))
  ck(folder.name+"_every_physical_request_preregistered",len(registrations)==len(rr) and {x["attempt_id"] for x in registrations}=={x["attempt_id"] for x in rr} and all(next(x["at"] for x in registrations if x["attempt_id"]==r["attempt_id"])<=r["started_at"] for r in rr))
 old=lines(R54/"http_ledger.jsonl");new=lines(R55/"http_ledger.jsonl")
 ck("expired_signed_URL_actual_XML_retained",b"Request has expired" in (ROOT/old[2]["path"]).read_bytes())
 ck("refresh_public_base_once_exact_Locations_no_signature_change",old[1]["url"]==new[0]["url"] and old[1]["headers"]["location"]==old[2]["url"] and new[0]["headers"]["location"]==new[1]["url"] and old[2]["url"]!=new[1]["url"])
 meta=load(Path(old[0]["path"]));official=next(x for x in meta["files"] if x["id"]==45398313)
 rp=contract["raw_XLSX"];raw=(ROOT/inp(rp["path"])).read_bytes()
 ck("official_DOI_file_size_MD5_bound",meta["resource_doi"].lower()=="10.1021/acs.jafc.4c00488" and meta["doi"].lower()=="10.1021/acs.jafc.4c00488.s001" and official["name"]=="jf4c00488_si_001.xlsx" and len(raw)==official["size"]==68338 and hashlib.md5(raw).hexdigest()==official["computed_md5"]=="30aa6648c27369368949a9032b031502")
 decision=load(D/"agent_delegated_scope_field_supplement_decision.json");prefix=decision["original_ledger_prefix"];ledger=(ROOT/Path(prefix["path"])).read_bytes()
 ck("R54_original_epoch_ledger_prefix_unchanged",hashlib.sha256(ledger[:prefix["bytes"]]).hexdigest()==prefix["sha256"])
 ck("R54_same_actual_R47_G5_and_scope_not_retroactive_repair",sha(decision["original_registration"]["stage_manifest_path"])==decision["original_registration"]["stage_manifest_sha256"] and sha(decision["actual_scope"]["path"])==decision["actual_scope"]["sha256"] and decision["prior_HTTP"]==0 and decision["not_retroactive_G5_time_repair"] and not decision["original_manifests_modified"])
 ck("legacy_SS_raw_gate_still_enforced_and_passes",gate("SS")["current_scope_SHA"]==decision["actual_scope"]["sha256"])
 c=load(R56/"pre_science_exposure_contract.json");verify_hashes(c["input_manifest_sha"])
 ck("R56_inherits_existing_source_read_not_new_fresh_group",c["source_science_already_read_in_R34"] and c["not_a_new_independent_source_group"] and c["original_worksheet_cell_content_unread_before_this_G5"] and not c["future_epoch_fresh_reuse_allowed"] and c["fresh_admitted"]==0)
 roles={};ids=[]
 for role in ("A4","A5"):
  m=load(inp(R56/role/"role_manifest.json"));verify_hashes(m["input_manifest_sha"]);verify_hashes(m["output_file_sha"])
  st=load(inp(R56/role/"scientific_read_started.json"));en=load(inp(R56/role/"scientific_read_completed.json"));ids.append(m["reader_id"])
  ck(role+"_actual_G5_before_first_XLSX_read_and_role_separation",load(G5)["timestamp"]<st["timestamp"]<en["timestamp"] and m["read_other_extractor_output"] is False and m["read_model_outcome"] is False and m["counts"]==dict(processed=1,passed=1,rejected=0,pending=0) and not m["independent_graph_transcription"] and not m["unprocessed"])
  roles[role]=load(inp(R56/role/"all_original_stored_cells.json"))["worksheets"]
 ck("A4_A5_separate_actual_processes_and_parser_implementations",ids[0]!=ids[1] and ids[0].split("-")[1]!=ids[1].split("-")[1] and load(R56/"A4/role_manifest.json")["parser"]!=load(R56/"A5/role_manifest.json")["parser"])
 ck("exact_A4_A5_full_named_sheet_cells_and_metadata_equal",roles["A4"]==roles["A5"])
 # Independent DOM reader checks source cell lexical values and relationship metadata.
 with zipfile.ZipFile(ROOT/rp["path"]) as z:
  def dom(p):
   b=z.read(p);assert b"<!DOCTYPE" not in b.upper() and len(b)<8*1024**2
   return minidom.parseString(b)
  shared=["".join(text(t) or "" for t in n.getElementsByTagNameNS(NS,"t")) for n in dom("xl/sharedStrings.xml").getElementsByTagNameNS(NS,"si")]
  rels={n.getAttribute("Id"):n.getAttribute("Target") for n in dom("xl/_rels/workbook.xml.rels").getElementsByTagName("Relationship")}
  wb=dom("xl/workbook.xml");original=[]
  for s in wb.getElementsByTagNameNS(NS,"sheet"):
   target=rels[s.getAttributeNS(REL,"id")];path=target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/"+target)
   d=dom(path);cells=[]
   for n in d.getElementsByTagNameNS(NS,"c"):
    rv=val(n,"v");typ=n.getAttribute("t") or None;resolved=rv
    if typ=="s":resolved=shared[int(rv)] if rv is not None else None
    if typ=="inlineStr":resolved="".join(text(x) or "" for x in n.getElementsByTagNameNS(NS,"t"))
    cells.append(dict(reference=n.getAttribute("r"),cell_type=typ,style=n.getAttribute("s") or None,raw_value=rv,resolved_value=resolved,formula=val(n,"f")))
   dims=d.getElementsByTagNameNS(NS,"dimension")
   original.append(dict(name=s.getAttribute("name"),state=s.getAttribute("state") or None,sheet_path=path,dimension=dims[0].getAttribute("ref") if dims else None,merged_cells=[n.getAttribute("ref") for n in d.getElementsByTagNameNS(NS,"mergeCell")],cells=cells))
  for i,s in enumerate(original):ck(s["name"]+"_every_original_cell_style_formula_and_sheet_metadata_matches_both",s==roles["A4"][i]==roles["A5"][i])
  ck("only14_named_worksheet_files_dual_read_not_all_embedded_package_cache",len(original)==14 and len(z.namelist())==27 and sum(len(x["cells"]) for x in original)==4994)
 cells=[dict(sheet=s["name"],**n) for s in original for n in s["cells"]]
 zero=[x for x in cells if x["cell_type"] in (None,"n") and x["raw_value"] is not None and decimal.Decimal(x["raw_value"])==0]
 blanks=[x for x in cells if x["resolved_value"] is None and x["formula"] is None]
 formulas=[x for x in cells if x["formula"] is not None]
 ck("43_numeric_zero269_explicit_blank15_formula_cache_pairs_retained",len(zero)==43 and len(blanks)==269 and len(formulas)==15 and all(x["sheet"]=="TableS12" and x["formula"].startswith("'[1]0901'!") and x["raw_value"] is not None for x in formulas))
 annotations=lines(inp(R56/"A6/all523_metabolite_annotation_rows.jsonl"))
 ck("all523_original_metabolite_rows_retained_not_reactions",len(annotations)==523 and len(original[2]["cells"])==2100)
 am=load(inp(R56/"A6/role_manifest.json"));verify_hashes(am["input_manifest_sha"]);verify_hashes(am["output_file_sha"])
 a=load(inp(R56/"A6/source_scientific_assessment.json"))
 ck("A6_source_processed_deferred_full_graphs0_no_whole_paper_rejection",a["chemical_qualification"]=="deferred" and a["complete_acceptor_product_donor_graphs"]==0 and not a["whole_source_scientific_qualification_complete"] and not a["source_whole_paper_no_SS_or_C_claim"] and a["source_science_new_independent_group_increment"]==0 and not a["frozen_SS_O2_enzymatic_reaction_established"])
 ck("A6_no_external_formula_recalculation_or_new_identity_claim",a["formulas_not_evaluated"] and a["external_workbook_not_accessed"] and not a["all_prior_source_graph_alias_and28_names_review_complete"] and not a["eligible_as_source_saturation_complete_round"] and a["fresh_admitted"]==0 and all(not x["source_identity_or_complete_structure_verified"] for x in a["source_specific_literal_contexts"]))
 exp=lines(inp(R56/"scientific_exposure_reads.jsonl"))
 ck("all5_actual_R56_permanent_read_exports_kept",len(exp)==5 and all(x["development_exposed"] and not x["future_fresh_eligible"] and x["exposure_type"]=="current_epoch_evaluation" for x in exp))
 allowed={"id","type","mainTitle","publicationDate","publisher","pids","pid","scheme","value","instances","bestAccessRight","accessRight","accessRights","url","urls","license","licenses","hostedBy","collectedFrom","instanceType","label","key"}
 def clean(x):
  if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k in allowed}
  if isinstance(x,list):return [clean(v) for v in x]
  return x
 for row in lines(R57/"query_execution.jsonl"):
  obj=load(inp(row["raw_pointer"]["path"]))
  ck(row["query_id"]+"_exact_PID_raw_metadata_projection_no_science",row["header"]==obj["header"] and row["metadata"]==clean(obj["results"]) and obj["header"]["numFound"]==1 and row["metadata"][0]["bestAccessRight"]["label"]=="CLOSED" and not row["scientific_content_read"])
 ck("R57_all4_metadata_queries_not_full_chemical_round",load(R57/"metadata_access_locator_summary.json")["processed"]==4 and load(R57/"metadata_access_locator_summary.json")["unprocessed"]==[] and not load(R57/"metadata_access_locator_summary.json")["source_saturation"])
 for q in load(R58/"query_plan.json")["queries"]:
  m=load(inp(q["raw_declaration"]["path"]))["message"]
  ck(q["query_id"]+"_literal_declared_new_URL_no_previous_denial_reuse",q["url"] in {x["URL"] for x in m["link"]} and len([x for x in physical_attempts() if x["url"]==q["url"]])==1)
 ck("R58_two403_retained0_valid_original_no_science",load(R58/"raw_custody_summary.json")["valid_PDF"]==0 and not load(R58/"raw_custody_summary.json")["scientific_content_read"])
 active={}
 for x in lines(B/"epoch_ledger.jsonl"):
  if x.get("epoch_id") in ("C-E02","SS-E02") and x.get("status")=="active" and x.get("stage") in ("G5_FRESH_HOLDOUT_ACQUIRE","G6_IDENTITY_STRUCTURE_ADMIT"):active[x["stage_manifest_path"]]=x["stage_manifest_sha256"]
 for p,s in active.items():verify_stage_chain(ROOT/p,s)
 ck("all25_unique_active_G5_G6_chains_intact_duplicate_registration_not_new_stage",len(active)==25)
 for f,s in [("C","09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46"),("SS","a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f")]:
  ck(f+"_G4_unchanged",sha(B/f"{f}/E02/stages/G4_SCOPE_FREEZE.json")==s)
  ck(f+"_real_G7_G8_new_bank_G9_absent",all(not list((ROOT/B/f"{f}/E02/stages").rglob(stage+".json")) for stage in STAGES if stage.startswith(("G7_","G8_","G9_"))))
 ck("entire_MCTS214_row_SHA_unchanged",len(lines(B/"run_ledger.jsonl"))==214 and sha(B/"run_ledger.jsonl")=="7110e1d2fa44be133be6b9e8be79d2bcee4c5213e0287059c84e2f979dce9ed6")
 physical=physical_attempts();b=load(BUD);previous=load(B/"report_snapshots/progress-v30-physical-budget.v2.json")
 ck("physical_budget1206_HTTP1242653972bytes_conserved",len(physical)==b["totals"]["HTTP"]==1206 and sum(x["bytes"] for x in physical)==b["totals"]["bytes"]==1242653972)
 ck("new11_HTTP119758bytes_all_raw_preserved",len(allnew)==11 and len(physical)-previous["totals"]["HTTP"]==11 and sum(x["bytes"] for x in allnew)==b["totals"]["bytes"]-previous["totals"]["bytes"]==119758)
 ck("earlier1200_HTTP_snapshot_retained",load(B/"report_snapshots/progress-v31-physical-budget.json")["totals"]["HTTP"]==1200)
 end=dict(common,event_type="scientific_audit_completed",timestamp=now(),scientific_content_read=True,stored_cells_verified=4994,worksheet_count=14)
 put(O/"scientific_audit_completed.json",end)
 write(T,str(O/"scientific_exposure_reads.jsonl"),"".join(json.dumps(dict(x,source_event_pointer=dict(path=str(O/n),sha256=sha(O/n))),sort_keys=True)+"\n" for n,x in [("scientific_audit_started.json",start),("scientific_audit_completed.json",end)]))
 result=dict(task=T,agent_role="A11",at=now(),approval_type="agent_delegated",human_reviewed=False,input_manifest_sha=inputs,checks=checks,passed=sum(x["passed"] for x in checks),failed=sum(not x["passed"] for x in checks),errors=[x for x in checks if not x["passed"]],unprocessed=[],read_holdout=True,read_model_outcome=False,new_HTTP=11,new_bytes=119758,total_HTTP=1206,total_bytes=1242653972,worksheets=14,stored_cells=4994,numeric_zeroes=43,explicit_blanks=269,formula_cache_pairs=15,annotation_rows=523,registered_unique_G5_G6=len(active),new_complete_chemical_records=0,new_independent_source_groups=0,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,source_saturation=False,complete_qualification_round=False,independent_chemical_validation=False,actual_audit_read_exports=2)
 put(O/"independent_A11_tabular_and_access_audit.json",result)
 print(json.dumps({k:result[k] for k in ["passed","failed","new_HTTP","new_bytes","stored_cells","registered_unique_G5_G6"]}))
 if result["failed"]:raise RuntimeError("A11_FAILED")
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run}[sys.argv[1]]()
