"""Archive current official PMC access documentation; no article chemical content."""
import json
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,role_manifest
from scripts.task016_p7_c_e02_http import E,immutable_json,acquire,append,rows,require_active
B=E/"fresh/C-E02-R8"
def ptr(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def main():
 p=B/"query_plan.v3.json"
 if not p.exists():
  prev=B/"query_plan.v2.json";x=json.loads(prev.read_text());ep=B/"official_oa_api_execution.jsonl"
  assert len(rows(ep))==2 and all(r["terminal"] for r in rows(ep))
  x.update(preregistered_at=now(),parent_query_plan=ptr(prev),prior_terminal_execution=ptr(ep),stage="official current PMC documentation archive, no scientific source extraction",maximum_HTTP_this_plan=3,maximum_cumulative_HTTP_R8_preregistered=7,primary_discovery_routes=["current_official_PMC_access_documentation"],queries=[dict(query_id=a,source_id="PMC_OFFICIAL_DOCUMENTATION",url=u,route="official current PMC access documentation; not scientific article",object_limit=2*1024**2) for a,u in [("PMC-OA-SERVICE-RETIREMENT-DOC","https://pmc.ncbi.nlm.nih.gov/tools/oa-service/"),("PMC-ARTICLE-DATASETS-DOC","https://pmc.ncbi.nlm.nih.gov/tools/textmining/"),("PMC-AWS-README-DOC","https://pmc-oa-opendata.s3.amazonaws.com/README.txt")]],automated_PMC_article_HTML_retrieval_forbidden=True,retired_OA_API_must_not_be_retried=True)
  x["files_sha256"].update({str(prev.relative_to(ROOT)):sha_file(prev),str(ep.relative_to(ROOT)):sha_file(ep),str(Path(__file__).relative_to(ROOT)):sha_file(Path(__file__))})
  immutable_json(p,x)
 plan=require_active(p);done={r["query_id"] for r in rows(B/"official_documentation_execution.jsonl")}
 for q in plan["queries"]:
  if q["query_id"] in done:continue
  r=acquire(p,q["url"],"metadata",q["route"],object_limit=q["object_limit"])
  append(B/"official_documentation_execution.jsonl",dict(query_id=q["query_id"],source_id=q["source_id"],plan_pointer=ptr(p),raw_pointer={k:r.get(k) for k in ["attempt_id","path","sha256","bytes","status_code","error","started_at","finished_at"]},terminal=True,chemical_read=False,scientific_article=False))
  print(json.dumps(dict(query_id=q["query_id"],status=r["status_code"],bytes=r["bytes"])),flush=True)
 out=B/"raw_only_fallback_closeout_v1.json"
 if out.exists():return
 a=rows(B/"official_index_execution.jsonl");b=rows(B/"official_oa_api_execution.jsonl");c=rows(B/"official_documentation_execution.jsonl")
 assert len(a)==2 and len(b)==2 and len(c)==3 and all(r["terminal"] for r in a+b+c)
 for r in a+b+c:
  pp=ROOT/r["raw_pointer"]["path"];assert sha_file(pp)==r["raw_pointer"]["sha256"]
 docs={r["query_id"]:(ROOT/r["raw_pointer"]["path"]).read_text(errors="replace") for r in c if r["raw_pointer"]["status_code"]==200 and not r["raw_pointer"]["error"]}
 checks=dict(retirement_notice_literal_found="no longer available" in docs.get("PMC-OA-SERVICE-RETIREMENT-DOC",""),automated_retrieval_service_terms_found="only services" in docs.get("PMC-ARTICLE-DATASETS-DOC",""),current_AWS_layout_readme_found="STRUCTURE OF THE DATASET" in docs.get("PMC-AWS-README-DOC",""))
 assert all(checks.values()),checks
 ins=[B/n for n in ["query_plan.json","query_plan.v2.json","query_plan.v3.json","official_index_execution.jsonl","official_oa_api_execution.jsonl","official_documentation_execution.jsonl","official_OA_service_documentation_lookup_plan.json","official_OA_service_documentation_findings_v1.json","official_dataset_documentation_lookup_plan_v2.json","official_dataset_documentation_lookup_plan_v3.json"]]+[ROOT/r["raw_pointer"]["path"] for r in a+b+c]+[Path(__file__)]
 immutable_json(out,dict(task=TASK,created_at=now(),approval_type="agent_delegated",human_reviewed=False,scope="R8 exact two existing metadata hints, raw-only lawful fallback and official access diagnostics",inputs_sha256={str(z.relative_to(ROOT)):sha_file(z) for z in ins},planned_HTTP=7,executed_HTTP=7,terminal_HTTP=7,pending_HTTP=0,bytes=sum(r["raw_pointer"]["bytes"] for r in a+b+c),two_empty_official_indexes=[dict(source_id=r["source_id"],advertised_objects=len(r["advertised_objects"]),is_truncated_literal=r["is_truncated_literal"]) for r in a],retired_API_404_requests=2,official_documentation_requests=3,official_documentation_checks=checks,external_web_explicit_invocations=3,external_web_explicit_pages=5,external_internal_HTTP_unobservable=True,external_not_in_precise_HTTP_count=True,old_failure_bytes_preserved=True,empty_cloud_prefix_not_article_absence=True,retired_endpoint_404_not_article_absence=True,current_official_automated_retrieval_services=["PMC Cloud Service","PMC OAI-PMH","E-Utilities","BioC API"],no_automated_PMC_article_public_HTML_retrieval=True,no_article_scientific_body_read=True,source_original_objects=0,new_G5=False,source_qualified=0,fresh_admitted=0,complete_chemical_round=False,source_saturation=False,scientific_ABE_cells=0,metrics=None,new_MCTS=0,goal_completed=False))
 rp=B/"role_A2_raw_only_fallback_manifest_v1.json";role=role_manifest("A2 deterministic official-source fallback and access diagnostics","C-E02-R8",ins,[out],dict(processed=2,passed=0,rejected=0,pending=2),read_holdout=False,read_model_outcome=False,unprocessed=["No usable original bytes from two source prefixes; empty cloud listing is not article absence","Other authorized API routes or independent publisher/repository originals remain to assess; no access exhaustion or saturation claim"])
 role.update(approval_type="agent_delegated",human_reviewed=False,new_HTTP=7,new_MCTS=0,source_chemical_content_read=False,read_only_official_documentation_and_index_metadata=True)
 immutable_json(rp,role)
 print(json.dumps(dict(closeout=ptr(out),role=ptr(rp),HTTP=7,new_original_objects=0)),flush=True)
if __name__=="__main__":main()
