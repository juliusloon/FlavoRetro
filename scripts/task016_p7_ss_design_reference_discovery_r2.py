"""Preregistered SS design metadata/reference discovery; no chemical body extraction."""
import json,urllib.parse,importlib.util
from pathlib import Path
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json,physical_attempts
O=ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2"
def ptr(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def main():
    assert not O.exists()
    old=ROOT/"outputs/task016-p7/v1/SS/E02_design/new_source_locations_v1/ss_locator_transport_v1.py"
    transport=old.read_text().replace("new_source_locations_v1","reference_discovery_r2").replace("SS-LOC-R2","SS-DISC-R2").replace("SS-new-source-locations-v1","SS-reference-discovery-r2")
    tp=O/"ss_reference_transport_v1.py";write(TASK,str(tp.relative_to(ROOT)),transport)
    queries=[]
    def q(route,label,url,source_id=None):
        queries.append(dict(query_id="SS-REF-R2-Q%02d"%(len(queries)+1),route=route,label=label,url=url,source_id=source_id or label,kind="metadata",object_limit=2*1024**2))
    ep="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
    for term in ['"UGT79B31"','"UGT79B6"','"flavonol" AND "galactoside" AND ("2-glucosyltransferase" OR "diglycoside")']:
        q("EuropePMC bibliographic title/abstract metadata discovery",term,ep+urllib.parse.urlencode(dict(query=term,format="json",resultType="core",pageSize=100)))
    for title in ["UGT79B31 is responsible for the final modification step of pollen-specific flavonoid biosynthesis in Petunia hybrida","flavonol 3-O-glycoside 2-O glucosyltransferase"]:
        q("Crossref independent title metadata discovery",title,"https://api.crossref.org/works?"+urllib.parse.urlencode({"query.title":title,"rows":25}))
    q("NCBI official referenced-primary metadata resolution","29214446 32156687","https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"+urllib.parse.urlencode(dict(db="pubmed",id="29214446,32156687",retmode="xml")))
    for pmid in ["29214446","32156687"]:
        q("EuropePMC exact referenced-primary identity resolution",pmid,ep+urllib.parse.urlencode(dict(query="EXT_ID:"+pmid+" AND SRC:MED",format="json",resultType="core",pageSize=1)),pmid)
    inputs=[old,ROOT/"outputs/task016-p7/v1/SS/E02_design/new_source_actual_exposure_custodian_v3/permanent_exposure_manifest.json",ROOT/"outputs/task016-p7/v1/SS/E02_design/new_source_A6_reconciliation_v3/role_A6_manifest.json",ROOT/"outputs/task016-p7/v1/SS/E02_design/new_source_locations_v1/role_A2_fixed_raw_only_locator_manifest.json",ROOT/"outputs/task016-p7/v1/report_snapshots/progress-v11-budget-prefix.json",ROOT/"data/raw/task016-p7/SS/353d259fb942119acf91815dc6c6f29696354614a378d8cbccbcba0d4e30e3f6.attempt-1.xml"]
    immutable_json(O/"preregistered_locator_plan.json",dict(task=TASK,created_at=now(),approval_type="agent_delegated",human_reviewed=False,phase="SS source-first design raw metadata only",queries=queries,query_routes=3,reference_chain=dict(source_pointer=ptr(inputs[-1]),reference_ids=["kiaf556-B25","kiaf556-B18"],raw_reference_DOIs=["10.1007/s00425-017-2822-5","10.1105/tpc.19.00801"],raw_reference_PMCIDs=["PMC5856881","PMC7203936"],bibliographic_chase_only_not_reaction_evidence=True),files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in inputs},target_full_graphs_read=False,source_chemical_extraction=False,no_qualification_or_fresh=True,scope_strata_not_merged=True,batch_budget=dict(HTTP=100,bytes=512*1024**2,article_versions=30,attachments=0),all_original_byte_requests_require_separate_preregistration=True))
    print(json.dumps(dict(plan=ptr(O/"preregistered_locator_plan.json"),queries=8,routes=3,transport=ptr(tp))))
if __name__=="__main__":main()
