"""A3 append: original identity via repository DOI metadata plus full title/author pages."""
import json,re,html,unicodedata,subprocess
from html.parser import HTMLParser
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
from scripts.operate import write
B=ROOT/"outputs/task016-p7/v1/C/E02/fresh/C-E02-R5-A3";I=ROOT/"outputs/task016-p7/v1/C/E02/stages/batches/C-E02-R5/fresh_source_input_manifest.json"
def norm(s):return re.sub(r"[^a-z0-9]+","",unicodedata.normalize("NFKC",html.unescape(re.sub(r"<[^>]+>","",s))).lower())
class Meta(HTMLParser):
 def __init__(self):super().__init__();self.m={}
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=="meta" and d.get("name","").startswith("citation_"):self.m.setdefault(d["name"],[]).append(d.get("content"))
def main():
 old=json.loads((B/"source_original_identity_verification.json").read_text());raw=ROOT/old["raw_Crossref_pointer"]["path"];assert sha_file(raw)==old["raw_Crossref_pointer"]["sha256"]
 cross=json.loads(raw.read_text())["message"];medraw=ROOT/old["raw_MED_pointer"]["path"];assert sha_file(medraw)==old["raw_MED_pointer"]["sha256"]
 med=next(x for x in json.loads(medraw.read_text())["resultList"]["result"] if x["id"]=="31418788")
 src=next(x for x in json.loads(I.read_text())["sources"] if x["source_id"]=="C-E02-R5-PMID-31418788")
 htmlraw=next(x["raw_pointer"] for x in src["original_objects"] if x["actual_content_type"]=="HTML");hp=ROOT/htmlraw["path"];assert sha_file(hp)==htmlraw["sha256"]
 parser=Meta();parser.feed(hp.read_text());meta=parser.m
 pdf=old["raw_original_pointer"];pp=ROOT/pdf["path"];assert sha_file(pp)==pdf["sha256"]
 text=subprocess.run(["pdftotext","-f","1","-l","2","-layout",str(pp),"-"],check=True,capture_output=True,text=True).stdout
 textpath=B/"original_title_and_author_pages1_2.txt";write(TASK,str(textpath.relative_to(ROOT)),text)
 authors=[x["family"] for x in cross["author"]];reposurnames=[x.split(",")[0] for x in meta["citation_author"]]
 medauthors=[x.strip().split()[0] for x in med["authorString"].rstrip(".").split(",")]
 checks=dict(exact_repository_DOI_matches_Crossref_MED=meta["citation_doi"]==["https://doi.org/"+cross["DOI"]] and cross["DOI"].lower()==med["doi"].lower(),repository_title_matches_Crossref_MED=norm(meta["citation_title"][0])==norm(cross["title"][0])==norm(med["title"]),full_ordered_authors_match_repository_Crossref_MED=authors==reposurnames==medauthors,all_author_surnames_in_PDF_title_author_pages=all(re.search(r"\b"+re.escape(x)+r"\b",text,re.I) for x in authors),registered_title_in_PDF_title_pages=norm(cross["title"][0]) in norm(text),repository_journal_matches_Crossref=meta["citation_journal_title"]==cross["container-title"],repository_volume_issue_matches_Crossref_MED=meta["citation_volume"]==[cross["volume"]]==[med["journalInfo"]["volume"]] and meta["citation_issue"]==[cross["issue"]]==[med["journalInfo"]["issue"]],repository_pages_match_Crossref_MED=meta["citation_firstpage"][0]+"-"+meta["citation_lastpage"][0]==cross["page"]==med["pageInfo"],repository_date_matches_Crossref_online=meta["citation_publication_date"][0]=="-".join(str(v).zfill(2) if i else str(v) for i,v in enumerate(cross["published-online"]["date-parts"][0])),source_native_pdf_link_matches_retrieval=meta["citation_pdf_url"]==["https://soar-ir.repo.nii.ac.jp/record/2002392/files/PCP60-2733.pdf"])
 assert all(checks.values()),[k for k,v in checks.items() if not v]
 r=dict(task=TASK,agent_role="A3 root-authored isolated publication identity append",approval_type="agent_delegated",human_reviewed=False,at=now(),source_id=src["source_id"],doi=cross["DOI"].lower(),metadata_identity_verified=True,source_original_identity_verified=True,checks=checks,repository_literal_citation_metadata=meta,raw_repository_pointer=htmlraw,raw_original_pointer=pdf,raw_Crossref_pointer=pointer(raw),raw_MED_pointer=pointer(medraw),PDF_identity_pages_pointer=pointer(textpath),prior_limited_firstpage_result=pointer(B/"source_original_identity_verification.json"),prior_firstpage_result_retained=True,reason_for_revision="PDF page1 is a cover sheet listing only corresponding author and no DOI; full authors appear on next page. Official repository links this exact PDF to matching DOI/title/authors/journal/volume/issue/pages/date. Missing PDF-cover DOI was not an original conflict.",source_qualified_reaction=False,actual_donor_salt_certification=False,new_HTTP=0,new_MCTS=0)
 immutable_json(B/"source_original_identity_verification.v2.json",r)
 inputs=[I,raw,medraw,hp,pp,B/"source_original_identity_verification.json",Path(__file__)]
 immutable_json(B/"role_A3_manifest.v2.json",dict(task=TASK,approval_type="agent_delegated",human_reviewed=False,logical_role=r["agent_role"],at=now(),input_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in inputs},output_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in [textpath,B/"source_original_identity_verification.v2.json"]},metadata_passed=1,original_passed=1,source_qualified_reaction=0,new_HTTP=0,new_MCTS=0))
 print(json.dumps(dict(metadata_passed=1,original_passed=1,source_qualification=0,prior_pending_preserved=True)))
if __name__=="__main__":main()
