"""R46: A3 metadata and exact advertised image/SI custody from actual public PMC HTML."""
import json,re,html as standard_html,urllib.parse
from pathlib import Path
from lxml import html
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import gate,put,sha,load,lines,now
from scripts import task016_p7_c_e02_http as h
T="TASK-016-P7";B=Path("outputs/task016-p7/v1");SID="PMC13422134";DOI="10.1002/cbic.70486"
O=B/"C/E02/fresh/C-E02-R46-Iris-advertised-assets-v1"
R44=B/"C/E02/fresh/C-E02-R44-Iris-original-custody-v1";R45=B/"C/E02/fresh/C-E02-R45-Iris-public-body-access-v1"
h.C=ROOT/O;h.RAW=ROOT/"data/raw/task016-p7/C/E02/C-E02-R46-Iris-advertised-assets-v1"
def pre():
 assert not (ROOT/O).exists()
 e=next(x for x in lines(R45/"query_execution.jsonl") if x["query_id"]=="R45-PMC-public-HTML");p=Path(e["raw_pointer"]["path"])
 assert e["status"]=="available" and sha(p)==e["raw_pointer"]["sha256"]
 tree=html.fromstring((ROOT/p).read_bytes())
 head={n:[x.get("content") for x in tree.xpath("//head/meta[@name='"+n+"']")] for n in ["citation_journal_title","citation_title","citation_publication_date","citation_volume","citation_issue","citation_firstpage","citation_doi","citation_pmid","citation_pdf_url"]}
 cex=next(x for x in lines(R44/"query_execution.jsonl") if x["query_id"]=="R44-Crossref");cross=load(Path(cex["raw_pointer"]["path"]))["message"];hint=load(R44/"precontract.json")["selected_metadata_hint"]["metadata"]
 def norm(x):return re.sub(r"[^a-z0-9]","",re.sub("<[^>]*>","",standard_html.unescape(x)).casefold())
 checks=dict(DOI=head["citation_doi"]==[DOI] and cross["DOI"].casefold()==DOI and hint["doi"]==DOI,title=norm(head["citation_title"][0])==norm(cross["title"][0])==norm(hint["title"]),journal=norm(head["citation_journal_title"][0])==norm(cross["container-title"][0])==norm(hint["journalTitle"]),year="2026" in head["citation_publication_date"][0] and cross["published"]["date-parts"][0][0]==int(hint["pubYear"])==2026,volume=head["citation_volume"]==[cross["volume"]]==[hint["journalVolume"]],issue=head["citation_issue"]==[cross["issue"]]==[hint["issue"]],article_number=head["citation_firstpage"]==[cross["article-number"]]==[hint["pageInfo"]],PMID=head["citation_pmid"]==[hint["pmid"]],publisher=cross["publisher"]=="Wiley")
 assert all(checks.values()),checks
 aliases=["article:"+SID,"doi:"+DOI,"pmid:"+head["citation_pmid"][0]]
 si=sorted(set(urllib.parse.urljoin("https://pmc.ncbi.nlm.nih.gov/articles/"+SID+"/",x.get("href")) for x in tree.xpath("//article//a[@href]") if re.search(r"\.(?:pdf|docx?|xlsx?|zip)(?:$|\?)",x.get("href"),re.I)))
 imgs=sorted(set(x.get("src") for x in tree.xpath("//article//img[@src]")))
 assert len(si)==1 and si[0].endswith("/CBIC-27-e70486-s001.pdf") and len(imgs)==6
 assert all(urllib.parse.urlsplit(x).hostname in ("pmc.ncbi.nlm.nih.gov","cdn.ncbi.nlm.nih.gov") for x in si+imgs)
 queries=[dict(query_id="R46-SI",url=si[0],kind="attachment",limit=16*1024**2,asset_role="advertised_SI")]
 queries += [dict(query_id="R46-image-"+str(i),url=u,kind="attachment",limit=2*1024**2,asset_role="advertised_original_figure") for i,u in enumerate(imgs,1)]
 ga=gate("C");inputs=[R44/"precontract.json",R45/"precontract.json",R45/"query_execution.jsonl",p,Path(cex["raw_pointer"]["path"]),Path(__file__).resolve().relative_to(ROOT),Path("scripts/task016_p7_c_e02_http.py"),B/"SS/E02/stages/G4_SCOPE_FREEZE.json"]
 put(O/"precontract.json",dict(task=T,family="C",epoch_id="C-E02",batch_id=O.name,at=now(),approval_type="agent_delegated",human_reviewed=False,G4_pointer=dict(path=ga["G4_path"],sha256=ga["G4_SHA"]),files_sha256={str(x):sha(x) for x in inputs},chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,max_HTTP=7,no_retry=True,no_automatic_redirect=True,source_id=SID,science_body_read=False,figures_decoded_or_scientifically_read=False,reason="Exact links actually advertised by the public PMC original, whose original front fields agree with Crossref and EPMC; bytes remain opaque until both C/SS G5 contracts are frozen.",metadata_OA_flag="N; public PMC original is available, not an OA license claim; local use only, no redistribution"))
 put(O/"A3_original_front_identity.json",dict(task=T,agent_role="A3_front_only",at=now(),approval_type="agent_delegated",human_reviewed=False,source_id=SID,PMCID=SID,DOI=DOI,PMID=head["citation_pmid"][0],official_aliases=aliases,original_raw=e["raw_pointer"],Crossref_raw=cex["raw_pointer"],fields=head,field_checks=checks,original_front_identity_verified=True,source_original_content_type="public_PMC_HTML",scientific_body_read=False,source_chemical_eligibility=None,prior_full_alias_graph_clearance=False,license_status="No OA grant established; Crossref Wiley VoR/TDM terms and EPMC non-OA preserved; local only."))
 put(O/"advertised_asset_plan.json",dict(task=T,at=now(),queries=queries,advertised_SI_links=si,advertised_image_links=imgs,original_HTML_SHA=e["raw_pointer"]["sha256"],scientific_content_read=False))
 print(json.dumps(dict(A3_front_verified=all(checks.values()),identity_fields=len(checks),advertised_images=len(imgs),advertised_SI=len(si))))
def run():
 for q in load(O/"advertised_asset_plan.json")["queries"]:
  if any(x["query_id"]==q["query_id"] for x in lines(O/"asset_execution.jsonl")):continue
  r=h.acquire(ROOT/O/"precontract.json",q["url"],q["kind"],"Only exact original-advertised public asset bytes, raw custody before both G5 freezes.",object_limit=q["limit"])
  row=dict(query_id=q["query_id"],source_id=SID,asset_role=q["asset_role"],raw_pointer={k:r[k] for k in ["path","sha256","bytes"]},status=r["status"],HTTP_status=r["status_code"],error=r.get("error"))
  p=O/"asset_execution.jsonl";write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(row,sort_keys=True)+"\n")
  print(json.dumps({k:row[k] for k in ["query_id","HTTP_status","status"]}),flush=True)
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run}[sys.argv[1]]()
