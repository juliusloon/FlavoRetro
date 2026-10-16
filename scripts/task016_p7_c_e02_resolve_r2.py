"""Preregistered C-E02-R2 exact identifier resolution of R1 metadata-only hints."""
from __future__ import annotations
import html,json,re,sys,urllib.parse
from pathlib import Path
from scripts.task016_p7_c_e02_http import acquire,immutable_json,require_active
from scripts.task016_p7_c_e02_fresh import E,ROOT,TASK,rows,source_hint,hint_tokens,save_rows,pointer
from scripts.task016_p7_orchestrate import now,sha_file,verify_stage_chain
from scripts.task016_p7_source_harness import validate_query_accounting
OLD=E/"fresh/C-E02-R1"
B=E/"fresh/C-E02-R2"
def prepare():
    original=json.loads((OLD/"query_plan.json").read_text())
    g5=E/"stages/batches/C-E02-R1/G5_FRESH_HOLDOUT_ACQUIRE.json"
    verify_stage_chain(g5,sha_file(g5))
    hints=rows(OLD/"source_dispositions.jsonl")
    ids=sorted({str(d["source_hint"]["pmid"]) for d in hints if d["disposition"]=="metadata_only" and not d["source_hint"].get("pmcid") and
                d["source_hint"].get("pmid") and re.search(original["metadata_title_selection_regex"],d["source_hint"].get("title") or "",re.I)})
    queries=[]
    for start in range(0,len(ids),20):
        group=ids[start:start+20]
        query="("+" OR ".join("EXT_ID:"+pid for pid in group)+") AND SRC:MED"
        queries.append(dict(query_id="C-E02-R2-Q%02d"%(len(queries)+1),query=query,route="exact_identifier_resolution",
           database="EuropePMC",family="C",scope_id="p7-C-E02:flavone_6_C_glucoside_C3_H",
           reason="Resolve R1 metadata citation PMID aliases before original chemistry; no model or static scope outcomes",
           max_pages=1,max_objects=100,PMID_universe=group,
           url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query=query,format="json",resultType="lite",pageSize=100))))
    plan=dict(original)
    files=dict(plan["files_sha256"])
    for p in (g5,OLD/"source_dispositions.jsonl",OLD/"query_audit.json",OLD/"article_acquisition.json",Path(__file__)):
        files[str(p.relative_to(ROOT))]=sha_file(p)
    acquired=json.loads((OLD/"article_acquisition.json").read_text())
    seen=sorted(set().union(*(hint_tokens(a["source_hint"]) for a in acquired)))
    plan.update(batch_id="C-E02-R2",preregistered_at=now(),queries=queries,files_sha256=files,
                prior_G5_pointer=pointer(g5),prior_same_epoch_source_dedup_tokens=seen,identifier_universe=ids,
                metadata_title_selection_regex=r"C[-‐‑– ](?:glycosyl|glucosyl)|glycosylflavonoid|UGT708",
                metadata_title_normalization="HTML markup/entity decoding solely for title matching; provider literal retained",
                primary_discovery_routes=["exact_identifier_resolution"],chemical_round_complete=False,saturation=False,
                maximum_primary_original_sources=20)
    immutable_json(B/"query_plan.json",plan)
    require_active(B/"query_plan.json")
    print(json.dumps(dict(identifier_PMIDs=len(ids),planned_queries=len(queries),chemical_extracted=0)))

def run():
    plan=require_active(B/"query_plan.json")
    if (B/"query_execution.jsonl").exists():raise ValueError("R2 already fixed")
    discoveries=[];executions=[];raws=[];resolved=set()
    hist=set(plan["historical_source_tokens"]);same=set(plan["prior_same_epoch_source_dedup_tokens"])
    for q in plan["queries"]:
        request=acquire(B/"query_plan.json",q["url"],"metadata",q["query_id"]+" exact source identifier resolution",object_limit=8*1024**2)
        raws.append(pointer(ROOT/request["path"]))
        records=[];error=request["error"]
        if request["status"]=="available":
            try:
                data=json.loads((ROOT/request["path"]).read_text())
                records=data["resultList"]["result"]
            except (ValueError,KeyError,UnicodeError) as exc:error=type(exc).__name__+": "+str(exc)
        unique={}
        for r in records:
            if r.get("source")!="MED" or str(r.get("id")) not in q["PMID_universe"]:
                raise ValueError("exact PMID response contains unregistered result")
            unique.setdefault(str(r["id"]),r)
            resolved.add(str(r["id"]))
        per=[]
        for i,r in enumerate(unique.values(),1):
            h=source_hint(r)
            h["provider_title_literal"]=h["title"]
            h["title"]=html.unescape(re.sub("<[^>]+>","",html.unescape(h["title"] or "")))
            overlap=sorted(hint_tokens(h)&hist)
            dedup=sorted(hint_tokens(h)&same)
            d=dict(record_id=q["query_id"]+"-D%03d"%i,query_id=q["query_id"],source_hint=h,
                disposition="rejected" if overlap or dedup else "metadata_only",metadata_only=True,
                chemical_extracted=False,evidence_eligible=False,source_identity_verified=False,
                historical_source_overlap=overlap,prior_same_epoch_source_duplicate=dedup,
                reason="Historical design source" if overlap else "Prior R1 source; dedup, not a new independent source" if dedup else "Resolved metadata-only identity; original/A3/A4/A5/A6 pending",
                raw_pointer=pointer(ROOT/request["path"]))
            per.append(d)
        discoveries.extend(per)
        rejected=sum(d["disposition"]=="rejected" for d in per)
        executions.append(dict(query_id=q["query_id"],status="executed",returned_count=len(records),deduplicated_count=len(per),
           pending_identity_count=len(per)-rejected,admitted=0,deferred=0,rejected=rejected,metadata_only=len(per)-rejected,new_closure_groups=0,
           error=error,reported_hit_count=data.get("hitCount") if request["status"]=="available" and error is None else None,
           chemical_review_complete=False,http_attempt_id=request["attempt_id"]))
        print(json.dumps(dict(query=q["query_id"],returned=len(records),rejected=rejected,error=error)),flush=True)
    save_rows(B/"query_execution.jsonl",executions);save_rows(B/"source_dispositions.jsonl",discoveries)
    audit=validate_query_accounting(plan,executions,discoveries)
    audit.update(chemical_review_complete=False,new_qualified_groups=0,saturation=False,identifier_PMIDs=len(plan["identifier_universe"]),
                 resolved_PMIDs=len(resolved),unresolved_PMIDs=sorted(set(plan["identifier_universe"])-resolved))
    immutable_json(B/"query_audit.json",audit)
    immutable_json(B/"metadata_raw_manifest.json",dict(files_sha256={p["path"]:p["sha256"] for p in raws},contains_final_reaction_graphs=False))
if __name__=="__main__":{"prepare":prepare,"run":run}[sys.argv[1]]()
