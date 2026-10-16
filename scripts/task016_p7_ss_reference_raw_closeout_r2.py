"""Close raw-only 90-request SS reference intake; whitelist one source for design."""
import json
from pathlib import Path
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,role_manifest
from scripts.task016_p7_c_e02_http import immutable_json
B=ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2";O=B/"raw_closeout_v1"
def rows(p):return [json.loads(l) for l in p.read_text().splitlines()]
def ptr(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def main():
 assert not O.exists()
 http=rows(B/"http_ledger.jsonl")+rows(B/"originals/http_ledger.jsonl")
 plans=rows(B/"physical_request_preregistration.jsonl")+rows(B/"originals/physical_request_preregistration.jsonl")
 assert len(http)==len(plans)==90 and {x["attempt_id"] for x in http}=={x["attempt_id"] for x in plans}
 for x in http:assert sha_file(ROOT/x["path"])==x["sha256"] and (ROOT/x["path"]).stat().st_size==x["bytes"]
 snap=[]
 for n,rr in [("closed_HTTP_snapshot.jsonl",http),("closed_request_preregistration_snapshot.jsonl",plans)]:
  p=O/n;write(TASK,str(p.relative_to(ROOT)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rr));snap.append(p)
 v2=json.loads((B/"originals/official_byte_execution.v2.json").read_text())["records"]
 orig=rows(B/"originals/original_query_execution.jsonl")
 items=[]
 for x in orig:
  if x["kind"]!="article_version":continue
  r=x["physical_attempts"][-1]
  assert x["projection"]["body_element_present"]
  items.append(dict(source_id=x["source_id"],role="original_XML",raw_pointer=r,original_identity_verified=True,chemical_read=False))
 for x in v2:
  assert x["usable_bytes_container_only"]
  items.append(dict(source_id=x["source_id"],role="main_PDF" if x["kind"]=="article_version" else "attachment",raw_pointer=x["physical_attempts"][-1],container=x["container"],advertised_key=x["advertised_key"],container_QC=x["container_QC"],original_identity_verified=False,chemical_read=False))
 assert len(items)==70
 ss=json.loads((B/"originals/preregistered_locator_plan.json").read_text())["sources"]
 sources=[]
 for s in ss:
  pp=[x for x in items if x["source_id"]==s["source_id"]]
  sources.append(dict(source_id=s["source_id"],metadata_hint=s["metadata_hint"],originals=pp,original_body_XML_versions=1,original_main_PDF_versions=1,attachments=sum(x["role"]=="attachment" for x in pp),publication_identity_original_XML_verified=True,chemical_qualification=False,scientific_body_read=False,allocation="design_source_only" if s["source_id"]=="PMC5856881" else "raw_only_scientifically_unread",fresh_eligibility=None))
 inputs=[p for p in B.rglob("*") if p.is_file() and O not in p.parents and p.suffix in [".json",".jsonl",".py"]]
 inputs+=[ROOT/x["path"] for x in http]
 allocation=B/"prechemical_read_allocation.json"
 oldss=ROOT/"outputs/task016-p7/v1/SS/E02_design/new_source_actual_exposure_custodian_v3/permanent_exposure_manifest.json"
 oldc=ROOT/"outputs/task016-p7/v1/C/E02/fresh/C-E02-R7/source_exposure_custodian_v1/permanent_exposure_manifest.json"
 donor=ROOT/"data/raw/task016-p7/SS/2225d8d5f54187a2d6b3985267ed57cf553c3f322dc07f1e951a05fc217e9952.attempt-1.structure_database"
 inputs += [allocation,oldss,oldc,donor,Path(__file__)]+snap
 raw=O/"raw_only_source_intake_manifest.json"
 immutable_json(raw,dict(task=TASK,created_at=now(),approval_type="agent_delegated",human_reviewed=False,HTTP=90,bytes=sum(x["bytes"] for x in http),metadata_occurrences=180,source_ids=6,XML_versions=6,main_PDF_versions=6,attachments=58,valid_original_objects=70,source_publication_front_identities_verified=6,sources=sources,files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in dict.fromkeys(inputs)},source_scientific_qualification=0,fresh=0,chemical_science_read=False,complete_chemical_round=False,source_saturation=False,EPS_binary_header_v1_false_defer_corrected_in_v2=True,original_NCBI_404_responses_retained=6,metadata_page_truncation_recorded=True))
 design=O/"Petunia_only_design_common_raw_input.json"
 selected=[s for s in sources if s["source_id"]=="PMC5856881"]
 dpointers=[ROOT/x["raw_pointer"]["path"] for x in selected[0]["originals"]]
 approved_donor=dict(path=str(donor.relative_to(ROOT)),sha256=sha_file(donor),species_identity_reference_only=True,actual_assay_species_unknown=True)
 immutable_json(design,dict(task=TASK,created_at=now(),approval_type="agent_delegated",human_reviewed=False,phase="SS source-first design raw only",sources=selected,chemical_read_whitelist=["PMC5856881"],forbidden_scientific_read_sources=["PMC4494776","PMC4762388","PMC9786081","PMC12313340","PMC10940802"],raw_intake_parent_pointer=ptr(raw),prechemical_read_allocation_pointer=ptr(allocation),official_existing_donor_raw_references=[approved_donor],permanent_exposure_pointers=[ptr(oldss),ptr(oldc)],files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in dpointers+[donor,raw,allocation,oldss,oldc]},contains_final_graphs=False,source_chemical_qualified=0,fresh_admitted=0,other5_raw_metadata_not_fresh_eligibility_claim=True,first_scientific_read_must_be_recorded=True))
 rp=O/"role_A2_raw_only_intake_manifest.json"
 role=role_manifest("A2 root SS reference metadata and raw-only custodian","SS-E02-design-reference-r2",inputs,[raw,design]+snap,dict(processed=6,passed=0,rejected=0,pending=6),unprocessed=["Petunia-only independent A4/A5 design extraction and A6 source/graph/value reconciliation","Other5 sources scientifically unread until post-scope acquisition/input freeze or explicit design reallocation; no present fresh eligibility","Metadata query limited first-page universe not source saturation"],read_holdout=False,read_model_outcome=False)
 role.update(approval_type="agent_delegated",human_reviewed=False,physical_HTTP=90,chemical_body_read=False,scientific_qualification=0,fresh=0,raw_only=True)
 immutable_json(rp,role)
 print(json.dumps(dict(raw=ptr(raw),design_input=ptr(design),role=ptr(rp),HTTP=90,bytes=sum(x["bytes"] for x in http),originals=70)))
if __name__=="__main__":main()
