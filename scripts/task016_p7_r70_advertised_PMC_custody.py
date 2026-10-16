"""R70: custody of five actually advertised PMC OA JATS originals, no science read."""
import hashlib,json,re,sys,urllib.parse
from pathlib import Path
from scripts.operate import ROOT,write
from scripts import task016_p7_c_e02_http as h
from scripts.task016_p7_r18_PMC_originals import put,sha,load,now,lines
T="TASK-016-P7"; B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R70-five-advertised-PMC-JATS-custody-v1"
R=Path("data/raw/task016-p7/C/E02/C-E02-R70-five-advertised-PMC-JATS-custody-v1")
M=B/"C/E02/fresh/C-E02-R69-A1-priority-primary-metadata-v1"
G4=B/"C/E02/stages/G4_SCOPE_FREEZE.json"
def equivalent(url):
    for _ in range(3):
        n=urllib.parse.unquote(url)
        if n==url: break
        url=n
    return url
def pre(role):
    assert not (ROOT/O).exists()
    role=Path(role); wrapper=load(role); assert wrapper["agent_role"]=="A1"
    locators=M/"actual_advertised_public_original_locators.json"
    sources=load(locators)["sources"]; assert len(sources)==5
    physical=h.physical_attempts()
    assert len(physical)==1220 and sum(x["bytes"] for x in physical)==1243183397
    seen={equivalent(x["url"]) for x in physical}
    files=[locators,role,G4,Path("scripts/task016_p7_c_e02_http.py"),Path(__file__).resolve().relative_to(ROOT)]
    query=[]
    for i,source in enumerate(sources,1):
        pid=source["PMCID"]; options=[]
        # Exact advertised numeric version keys only; the maximum-version rule is frozen here.
        qp=M/"query_results"/("R69-Q%02d.json"%(2*i))
        index=load(qp); assert index["HTTP_status"]==200 and index["parse_error"] is None
        files.append(qp)
        raw=index["raw_pointer"] if "raw_pointer" in index else index.get("raw")
        if raw:
            p=Path(raw["path"]); assert sha(p)==raw["sha256"]; files.append(p)
        for item in index["projection"]["Contents"]:
            match=re.fullmatch(re.escape(pid)+r"\.(\d+)/"+re.escape(pid)+r"\.\1\.xml",item["Key"])
            if match: options.append((int(match.group(1)),item))
        assert options
        _,selected=max(options,key=lambda x:x[0])
        key=selected["Key"]
        adverts=[x for x in source["PMC_actual_returned_Key_locators"] if x["Key"]==key]
        assert len(adverts)==1
        url=adverts[0]["url"]
        assert url=="https://pmc-oa-opendata.s3.amazonaws.com/"+key
        assert equivalent(url) not in seen
        size=int(selected["Size"]); assert 0<size<8*1024**2
        etag=selected["ETag"].strip('"')
        assert re.fullmatch(r"[0-9a-f]{32}",etag)
        query.append(dict(query_id="R70-XML-%02d"%i,source_id=source["source_id"],pmcid=pid,doi=source["DOI"],url=url,kind="article_version",selected_key=key,expected_size=size,expected_md5=etag,all_advertised_XML_keys=[z[1]["Key"] for z in options],selection_rule="highest actually advertised numeric PMC version, before any original-content read; not content/outcome ranking",object_limit=8*1024**2,previous_exact_or_decoded_equivalent_URL_attempts=0,source_index_pointer=dict(path=str(qp),sha256=sha(qp))))
    files_sha={str(p):sha(p) for p in files}
    put(O/"precontract.json",dict(task=T,epoch_id="C-E02",family="C",batch_id=O.name,agent_role="A0_raw_custody",approval_type="agent_delegated",human_reviewed=False,created_at=now(),G4_pointer=dict(path=str(G4),sha256=sha(G4)),files_sha256=files_sha,chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,max_HTTP=5,no_redirect=True,no_automatic_retry=True,no_credentials=True,no_login_or_challenge_bypass=True,no_scientific_read=True,source_identity_verified=False,source_qualified=0,fresh_admitted=0,reason="Acquire advertised public JATS originals for five new conditional enzyme metadata leads; A3 and prospective scientific G5 remain required",physical_HTTP_before=1220,physical_bytes_before=1243183397))
    put(O/"query_plan.json",dict(task=T,queries=query,planned=5,source_universe=[x["source_id"] for x in sources],max_HTTP=5,all_queries_previously_unattempted=True))
    print(json.dumps(dict(planned=5,contract_sha256=sha(O/"precontract.json"),query_plan_sha256=sha(O/"query_plan.json"))),flush=True)
def run():
    contract=O/"precontract.json"; plan=load(O/"query_plan.json")
    assert not (ROOT/O/"query_execution.jsonl").exists()
    assert all(equivalent(q["url"]) not in {equivalent(p["url"]) for p in h.physical_attempts()} for q in plan["queries"])
    h.C=ROOT/O; h.RAW=ROOT/R
    result=[]
    for q in plan["queries"]:
        r=h.acquire(ROOT/contract,q["url"],"article_version",reason="P7 R70 first actual advertised PMC OA XML request, opaque original custody only; no scientific decoding or automatic qualification",object_limit=q["object_limit"])
        payload=(ROOT/r["path"]).read_bytes()
        prefix=payload[:2048].lower()
        md5=hashlib.md5(payload).hexdigest()
        item=dict(query_id=q["query_id"],source_id=q["source_id"],pmcid=q["pmcid"],doi=q["doi"],status_code=r["status_code"],raw_pointer={k:r[k] for k in ("path","sha256","bytes")},selected_key=q["selected_key"],index_size_match=len(payload)==q["expected_size"],index_md5_match=md5==q["expected_md5"],actual_md5=md5,XML_article_marker_present=b"<article" in prefix,potential_JATS_original_for_A3=(r["status_code"]==200 and r["error"] is None and len(payload)==q["expected_size"] and md5==q["expected_md5"] and b"<article" in prefix),no_scientific_read=True,source_identity_verified=False,evidence_eligible=False,fresh_admitted=False)
        result.append(item)
        write(T,str(O/"query_execution.jsonl"),"".join(json.dumps(x,sort_keys=True)+"\n" for x in result))
        print(json.dumps(dict(query_id=q["query_id"],status=r["status_code"],bytes=r["bytes"],size_match=item["index_size_match"],MD5_match=item["index_md5_match"])),flush=True)
    physical=h.physical_attempts()
    summary=dict(task=T,agent_role="A0_raw_custody",approval_type="agent_delegated",human_reviewed=False,at=now(),planned=5,processed=len(result),HTTP=len(result),unprocessed=[],sources=result,potential_originals_for_A3=sum(x["potential_JATS_original_for_A3"] for x in result),main_original_identity_pass=0,chemical_scientific_content_read=False,source_qualified=0,fresh_admitted=0,source_saturation=False,eligible_complete_round=False,physical_HTTP_global=len(physical),physical_bytes_global=sum(x["bytes"] for x in physical),raw_bytes_added=sum(x["raw_pointer"]["bytes"] for x in result),MCTS_added=0)
    put(O/"raw_custody_summary.json",summary)
    write(T,str(O/"physical_final_snapshot.jsonl"),"".join(json.dumps(x,sort_keys=True)+"\n" for x in physical))
    print(json.dumps({k:summary[k] for k in ("planned","processed","potential_originals_for_A3","physical_HTTP_global","physical_bytes_global","raw_bytes_added")}),flush=True)
if __name__=="__main__":
    if sys.argv[1]=="pre": pre(sys.argv[2])
    elif sys.argv[1]=="run": run()
    else: raise SystemExit("pre ROLE_PATH | run")
