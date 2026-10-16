"""R6 exact public-location follow-up for eight still metadata-only R5 sources."""
import json,urllib.parse,sys
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import E,BASE,acquire,immutable_json,require_active,physical_attempts,rows,append
from scripts.task016_p7_c_e02_fresh import pointer,save_rows,hint_tokens
from scripts.task016_p7_source_alias_closure import closure_tokens
B=E/"fresh/C-E02-R6";P=B/"exact_primary_location_query_plan.json"
def prepare():
    old=E/"fresh/C-E02-R5/query_plan.json";p=require_active(old);p=dict(p)
    additions=[E/"fresh/C-E02-R5/A6_source_reconciliation_v3/permanent_exposure_manifest.json",E/"fresh/C-E02-R5/A6_source_reconciliation_v3/permanent_postscope_source_graph_exposures.jsonl",E/"fresh/C-E02-R5/source_exposure_custodian_v1/permanent_exposure_manifest.json",E/"fresh/C-E02-R5/source_exposure_custodian_v1/permanent_postscope_source_exposures.jsonl",BASE/"epochs/C-E02/epoch_state.v5.json",E/"stages/batches/C-E02-R5/G6_IDENTITY_STRUCTURE_ADMIT.json",E/"fresh/C-E02-R5/exact_13_MED_primary_hint_metadata.jsonl",Path(__file__)]
    files=dict(p["files_sha256"])
    tokens=set(p["historical_source_tokens"])
    for q in additions:
        files[str(q.relative_to(ROOT))]=sha_file(q)
        if q.name in ["permanent_postscope_source_graph_exposures.jsonl","permanent_postscope_source_exposures.jsonl"]:
            for x in rows(q):tokens.update(closure_tokens(x))
    hints=[x for x in rows(E/"fresh/C-E02-R5/exact_13_MED_primary_hint_metadata.jsonl") if x["source_original_eligible_for_download"] and x["metadata_hint"]["pmid"]!="31418788"]
    assert len(hints)==8
    attempts=physical_attempts();qq=[]
    for h in hints:
        doi=h["metadata_hint"]["doi"];assert not hint_tokens(h["metadata_hint"])&tokens
        bases=[("Crossref_registered_public_links","https://api.crossref.org/works/"+urllib.parse.quote(doi,safe="")),("SemanticScholar_exact_DOI_OA_locator","https://api.semanticscholar.org/graph/v1/paper/DOI:"+urllib.parse.quote(doi,safe="")+"?fields="+urllib.parse.quote("title,externalIds,openAccessPdf,url,year",safe=",")),("OpenAIRE_exact_DOI_repository_locator","https://api.openaire.eu/search/publications?"+urllib.parse.urlencode(dict(doi=doi,format="json")))]
        for route,url in bases:
            prior=[r for r in attempts if r["url"]==url and r.get("status_code")==200 and not r.get("error")]
            qq.append(dict(query_id="C-E02-R6-LOC-%02d"%(len(qq)+1),source_id=h["source_id"],doi=doi,pmid=h["metadata_hint"]["pmid"],route=route,url=url,kind="metadata",reuse_pointer=pointer(ROOT/prior[-1]["path"]) if prior else None,source_hint_pointer=pointer(E/"fresh/C-E02-R5/exact_13_MED_primary_hint_metadata.jsonl"),read_abstract=False,chemical_extraction_permitted=False))
    p.update(batch_id="C-E02-R6",preregistered_at=now(),files_sha256=files,historical_source_tokens=sorted(tokens),requests=qq,query_routes=sorted({x["route"] for x in qq}),query_universe=len(qq),source_universe=8,sources=hints,source_ids_reused_from_R5=True,source_chemical_extraction_permitted=False,chemical_extraction_permitted=False,exact_queries_not_full_chemical_rounds=True,unknown_name_identity_fail_closed=True,source_qualified=0,fresh_admitted=0,no_scope_or_model_change=True)
    immutable_json(P,p);require_active(P)
    print(json.dumps(dict(plan=pointer(P),queries=len(qq),reuse=sum(x["reuse_pointer"] is not None for x in qq),sources=8,chemical_extracted=0)))
def run():
    p=require_active(P);done={x["query_id"] for x in rows(B/"exact_location_query_execution.jsonl")}
    for q in p["requests"]:
        if q["query_id"] in done:continue
        raw=q["reuse_pointer"];resp=None;error=None
        if raw is None:
            try:
                resp=acquire(P,q["url"],"metadata","R6 exact DOI public original locator: "+q["route"],object_limit=8*1024**2);raw=pointer(ROOT/resp["path"])
            except ValueError as exc:error=str(exc)
        if raw is not None:
            assert sha_file(ROOT/raw["path"])==raw["sha256"]
            try:json.loads((ROOT/raw["path"]).read_text())
            except Exception as exc:error=type(exc).__name__+": response is not valid metadata JSON"
        row=dict(query_id=q["query_id"],source_id=q["source_id"],doi=q["doi"],route=q["route"],raw_pointer=raw,reused=q["reuse_pointer"] is not None,HTTP=0 if resp is None else 1,status_code=resp["status_code"] if resp else None,error=error,finished_at=now(),chemical_extracted=False,source_qualified=0)
        append(B/"exact_location_query_execution.jsonl",row)
        print(json.dumps({k:row[k] for k in ["query_id","route","reused","HTTP","status_code","error"]}),flush=True)
    rr=rows(B/"exact_location_query_execution.jsonl");assert len(rr)==len(p["requests"])==24 and len({x["query_id"] for x in rr})==24
    immutable_json(B/"exact_location_query_conservation.json",dict(task=TASK,at=now(),planned=24,terminal=24,pending=0,source_ids_reused=8,reused_responses=sum(x["reused"] for x in rr),actual_HTTP=sum(x["HTTP"] for x in rr),raw_metadata_only=True,primary_articles_obtained=0,full_chemical_round_complete=False,source_saturation=False,scientific_ABE_cells=0,metrics=None))
if __name__=="__main__":{"prepare":prepare,"run":run}[sys.argv[1]]()
