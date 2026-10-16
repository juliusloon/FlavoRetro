"""Preregister legal SS original XML and public OA locator acquisition from new metadata."""
import json,urllib.parse
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
B=ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2"
O=B/"originals"
def main():
 assert not O.exists()
 old=B/"ss_reference_transport_v1.py"
 s=old.read_text().replace("SS/E02_design/reference_discovery_r2","SS/E02_design/reference_discovery_r2/originals").replace("SS/reference_discovery_r2","SS/reference_discovery_r2/originals").replace("SS-DISC-R2","SS-REF-ORIG-R2").replace("SS-reference-discovery-r2","SS-reference-originals-r2")
 s=s.replace('{"metadata","article_version"}', '{"metadata","article_version","attachment"}').replace("{'metadata','article_version'}","{'metadata','article_version','attachment'}")
 s=s.replace("PRIMARY_ONLY_NO_ATTACHMENTS","UNKNOWN_SOURCE_KIND").replace("'attachments':0","'attachments':100")
 s=s.replace("projected['article_versions']+=int(kind=='article_version')","projected['article_versions']+=int(kind=='article_version');projected['attachments']+=int(kind=='attachment')")
 p=O/"ss_original_transport_v1.py";write(TASK,str(p.relative_to(ROOT)),s)
 executions=[json.loads(l) for l in (B/"metadata_query_execution.jsonl").read_text().splitlines()]
 pmcs=["PMC5856881","PMC4494776","PMC4762388","PMC9786081","PMC12313340","PMC10940802"]
 sources=[]
 for pmc in pmcs:
  match=next((q,x) for q in executions for x in q["projection"] if x.get("pmcid")==pmc)
  q,x=match;sources.append(dict(source_id=pmc,metadata_hint=x,query_id=q["query_id"],metadata_projection_pointer=dict(path=str((B/"metadata_query_execution.jsonl").relative_to(ROOT)),sha256=sha_file(B/"metadata_query_execution.jsonl")),publication_identity_verified=False,scientific_body_read=False,chemical_qualification=False))
 queries=[]
 for x in sources:
  pmc=x["source_id"]
  queries.append(dict(query_id=pmc+"-XML",source_id=pmc,url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pmc+"/fullTextXML",kind="article_version",object_limit=8*1024**2,route="official EuropePMC OA original XML"))
  queries.append(dict(query_id=pmc+"-OA",source_id=pmc,url="https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?"+urllib.parse.urlencode({"id":pmc}),kind="metadata",object_limit=1024**2,route="official NCBI OA availability/package locator"))
 plan=dict(task=TASK,created_at=now(),approval_type="agent_delegated",human_reviewed=False,phase="SS design raw-only original acquisition",sources=sources,queries=queries,queries_planned=12,all_source_metadata_queries_terminal=True,metadata_query_conservation_pointer=dict(path=str((B/"metadata_query_conservation.json").relative_to(ROOT)),sha256=sha_file(B/"metadata_query_conservation.json")),files_sha256={str(x.relative_to(ROOT)):sha_file(x) for x in [B/"preregistered_locator_plan.json",B/"metadata_query_conservation.json",B/"metadata_query_execution.jsonl",p]},download_bytes_not_chemical_evidence=True,new_qualified_sources=0,fresh=0,source_saturation=False)
 immutable_json(O/"preregistered_locator_plan.json",plan)
 print(json.dumps({"plan_path":str((O/"preregistered_locator_plan.json").relative_to(ROOT)),"sha256":sha_file(O/"preregistered_locator_plan.json"),"sources":6,"queries":12}))
if __name__=="__main__":main()
