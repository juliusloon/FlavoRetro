"""R41 transport-schema correction: actual original PDF uses article_version kind."""
import copy,json
from scripts import task016_p7_c_r41_A6_figures as b
from scripts.task016_p7_r18_PMC_originals import put,sha,load,now
from scripts.operate import ROOT,write
def pre():
 c=copy.deepcopy(load(b.O/"precontract.json"))
 assert not (ROOT/b.O/"precontract.v2.json").exists()
 c.update(at=now(),supersedes_precontract=dict(path=str(b.O/"precontract.json"),sha256=sha(b.O/"precontract.json")),reason_for_revision="First run rejected unsupported original_pdf kind before any HTTP. Use supported article_version request kind; PDF is verified by magic, exact advertised size and parser. Preserve original failure.",transport_kind_is_not_content_claim=True)
 c["queries"][0]["kind"]="article_version"
 c["files_sha256"]["scripts/task016_p7_c_r41_A6_figures_v2.py"]=sha("scripts/task016_p7_c_r41_A6_figures_v2.py")
 put(b.O/"precontract.v2.json",c)
 print("zero-HTTP schema rejection preserved; corrected contract frozen")
def run():
 assert not (ROOT/b.O/"execution.jsonl").exists()
 c=load(b.O/"precontract.v2.json");x=c["queries"][0]
 r=b.transport.acquire(ROOT/b.O/"precontract.v2.json",x["url"],x["kind"],"A6 exact advertised public original PDF; article_version request kind, actual content checked independently.",object_limit=x["limit"])
 row=dict(query_id=x["query_id"],raw_pointer={k:r[k] for k in ["path","sha256","bytes"]},status=r["status"],HTTP_status=r["status_code"],advertised_size=x["advertised_size"],actual_size_match=r["bytes"]==x["advertised_size"],kind="article_version",actual_content_type="unverified_until_magic_and_parser")
 write(b.T,str(b.O/"execution.jsonl"),json.dumps(row,sort_keys=True)+"\n")
 print(json.dumps({k:row[k] for k in ["HTTP_status","status","actual_size_match"]}))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run,"render":b.render}[sys.argv[1]]()
