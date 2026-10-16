"""A3 R5 bounded source-publication identity; original reaction qualification separate."""
import json,urllib.parse,subprocess,re,html,unicodedata
from pathlib import Path
from html.parser import HTMLParser
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import E,immutable_json,acquire,require_active,rows
from scripts.task016_p7_c_e02_fresh import pointer
B=E/"fresh/C-E02-R5-A3";I=E/"stages/batches/C-E02-R5/fresh_source_input_manifest.json"
CP=B/"source_identity_intake_plan.json"
def prepare():
 p=json.loads((E/"fresh/C-E02-R5/supplemental_raw_file_request_plan.v2.json").read_text())
 files=dict(p["files_sha256"])
 for f in [I,ROOT/"scripts/task016_p7_c_e02_r5_identity.py",E/"stages/batches/C-E02-R5/G5_FRESH_HOLDOUT_ACQUIRE.json"]:files[str(f.relative_to(ROOT))]=sha_file(f)
 url="https://api.crossref.org/works/"+urllib.parse.quote("10.1093/pcp/pcz164",safe="")
 p.update(preregistered_at=now(),files_sha256=files,batch_id="C-E02-R5-A3",requests=[dict(url=url,doi="10.1093/pcp/pcz164",source_id="C-E02-R5-PMID-31418788",kind="metadata")],raw_chemistry_read=False)
 immutable_json(CP,p);require_active(CP)
def acquire_identity():
 p=require_active(CP);q=p["requests"][0]
 r=acquire(CP,q["url"],"metadata","R5-A3 exact observed DOI authoritative publisher-deposited Crossref identity",object_limit=8*1024**2)
 immutable_json(B/"Crossref_original_response.json",r)
 print(json.dumps(dict(status=r["status_code"],bytes=r["bytes"])))
def project():
 r=json.loads((B/"Crossref_original_response.json").read_text());assert r["status"]=="available"
 raw=ROOT/r["path"];d=json.loads(raw.read_text())["message"];assert d["DOI"].lower()=="10.1093/pcp/pcz164"
 i=json.loads(I.read_text());src=next(x for x in i["sources"] if x["source_id"]=="C-E02-R5-PMID-31418788")
 medraw=ROOT/src["metadata_response_pointers"][0]["path"];med=next(x for x in json.loads(medraw.read_text())["resultList"]["result"] if x.get("id")=="31418788")
 pdf=next(x for x in src["original_objects"] if x["actual_content_type"]=="PDF")["raw_pointer"]
 text=subprocess.run(["pdftotext","-f","1","-l","1","-layout",str(ROOT/pdf["path"]),"-"],check=True,capture_output=True,text=True).stdout
 def norm(s):return re.sub(r"[^a-z0-9]+","",unicodedata.normalize("NFKC",html.unescape(re.sub(r"<[^>]+>","",s))).lower())
 title=d["title"][0];mtitle=med["title"]
 checks=dict(DOI_Crossref_equals_MED=d["DOI"].lower()==med["doi"].lower(),title_Crossref_equals_MED=norm(title)==norm(mtitle),title_in_original_firstpage=norm(title) in norm(text),all_author_surnames_in_original_firstpage=all(norm(x["family"]) in norm(text) for x in d["author"]),DOI_in_original_firstpage=norm(d["DOI"]) in norm(text))
 p=B/"original_first_page_identity_text.txt"
 from scripts.operate import write
 write(TASK,str(p.relative_to(ROOT)),text)
 jr=med["journalInfo"];authoritative=dict(Crossref_title=title,Crossref_author_surnames=[x["family"] for x in d["author"]],Crossref_journal=d.get("container-title"),Crossref_year_fields={k:d.get(k) for k in ["published","published-online","published-print"]},Crossref_volume=d.get("volume"),Crossref_issue=d.get("issue"),Crossref_pages=d.get("page"),MED_title=mtitle,MED_authors=med.get("authorString"),MED_journalInfo=jr,MED_pages=med.get("pageInfo"),MED_pubYear=med.get("pubYear"))
 result=dict(task=TASK,agent_role="A3 root-authored isolated source identity process",at=now(),approval_type="agent_delegated",human_reviewed=False,source_id=src["source_id"],doi=d["DOI"].lower(),metadata_identity_verified=checks["DOI_Crossref_equals_MED"] and checks["title_Crossref_equals_MED"],source_original_identity_verified=all(checks.values()),identity_checks=checks,authoritative_metadata=authoritative,raw_Crossref_pointer=pointer(raw),raw_MED_pointer=pointer(medraw),raw_original_pointer=pdf,original_firstpage_text_pointer=pointer(p),original_type="public author manuscript; version differences retained",source_qualified_reaction=False,new_MCTS=0)
 immutable_json(B/"source_original_identity_verification.json",result)
 print(json.dumps(dict(metadata=result["metadata_identity_verified"],original=result["source_original_identity_verified"],checks=checks)))
if __name__=="__main__":
 import sys
 {"prepare":prepare,"acquire":acquire_identity,"project":project}[sys.argv[1]]()
