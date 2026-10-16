"""Execute each preregistered SS reference query once; raw responses, titles and IDs only."""
import json,importlib.util
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
O=ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2"
spec=importlib.util.spec_from_file_location("ss_ref_transport",O/"ss_reference_transport_v1.py")
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
def main():
    plan=json.loads((O/"preregistered_locator_plan.json").read_text());done={r["query_id"] for r in t.rows(O/"metadata_query_execution.jsonl")}
    for q in plan["queries"]:
        if q["query_id"] in done:continue
        responses=t.chain(q["url"],"metadata",q["route"],q["source_id"],{"query_id":q["query_id"],"plan_sha256":sha_file(O/"preregistered_locator_plan.json")},q["object_limit"])
        r=responses[-1];projection=[];error=None
        if r.get("status_code")==200 and not r.get("error"):
            p=ROOT/r["path"]
            try:
                if "efetch.fcgi" in q["url"]:
                    import xml.etree.ElementTree as E
                    root=E.fromstring(p.read_bytes())
                    for a in root.findall(".//PubmedArticle"):
                        projection.append(dict(pmid=a.findtext(".//MedlineCitation/PMID"),title="".join(a.find(".//ArticleTitle").itertext()),article_ids=[dict(type=x.get("IdType"),value=x.text) for x in a.findall(".//PubmedData/ArticleIdList/ArticleId")],metadata_only=True))
                else:
                    d=json.loads(p.read_text());rr=d.get("resultList",{}).get("result",[]) if "resultList" in d else d.get("message",{}).get("items",[])
                    for a in rr:
                        projection.append(dict(pmid=a.get("pmid") or (a.get("id") if a.get("source")=="MED" else None),pmcid=a.get("pmcid"),doi=a.get("doi") or a.get("DOI"),title=a.get("title"),publication_year=a.get("pubYear") or a.get("published"),open_access_flag=a.get("isOpenAccess"),metadata_only=True,abstract_science_read=False))
            except Exception as e:error=type(e).__name__+": "+str(e)
        t.append("metadata_query_execution.jsonl",dict(query_id=q["query_id"],route=q["route"],source_id=q["source_id"],physical_attempt_pointers=[dict(path=x.get("path"),sha256=x.get("sha256"),bytes=x.get("bytes"),status_code=x.get("status_code"),attempt_id=x.get("attempt_id")) for x in responses],projection=projection,parse_error=error,terminal=True,body_chemical_read=False,finished_at=now()))
        print(json.dumps(dict(query=q["query_id"],rows=len(projection),status=r.get("status_code"),parse_error=error)),flush=True)
    rows=t.rows(O/"metadata_query_execution.jsonl");assert {r["query_id"] for r in rows}=={q["query_id"] for q in plan["queries"]} and len(rows)==8
    p=O/"metadata_query_conservation.json"
    immutable_json(p,dict(task=TASK,created_at=now(),planned=8,executed=8,terminal=8,pending=0,HTTP=len(t.rows(O/"http_ledger.jsonl")),bytes=sum(r["bytes"] for r in t.rows(O/"http_ledger.jsonl")),metadata_occurrences=sum(len(r["projection"]) for r in rows),chemical_read=False,source_qualified=0,fresh=0,complete_chemical_round=False,source_saturation=False))
    print(json.dumps(dict(conservation_path=str(p.relative_to(ROOT)),sha256=sha_file(p))))
if __name__=="__main__":main()
