"""Publication-front-only validation of six unread SS sources; no chemistry."""
import json,re,html,unicodedata,xml.etree.ElementTree as E
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,role_manifest
from scripts.task016_p7_c_e02_http import immutable_json
B=ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2";O=B/"A3_publication_identity_v1"
def ptr(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def norm(s):
 if s is None:return None
 return re.sub(r"\s+","",unicodedata.normalize("NFKC",re.sub(r"<[^>]+>","",html.unescape(html.unescape(s)))).replace("–","-").replace("—","-")).casefold().rstrip(".")
def text(e):return "".join(e.itertext()).strip() if e is not None else None
def main():
 assert not O.exists()
 metaexec=[json.loads(l) for l in (B/"metadata_query_execution.jsonl").read_text().splitlines()]
 med={};inputs=[B/"metadata_query_execution.jsonl",B/"prechemical_read_allocation.json",B/"originals/preregistered_locator_plan.json",ROOT/"scripts/task016_p7_ss_reference_publication_identity_r2.py"]
 for q in metaexec:
  for p in q["physical_attempt_pointers"]:
   if not p.get("path"):continue
   path=ROOT/p["path"]
   try:d=json.loads(path.read_text())
   except Exception:continue
   inputs.append(path)
   for x in d.get("resultList",{}).get("result",[]):
    if x.get("source")=="MED":med.setdefault(str(x["id"]),(x,path))
 orig=[json.loads(l) for l in (B/"originals/original_query_execution.jsonl").read_text().splitlines()]
 records=[]
 for o in orig:
  if o["kind"]!="article_version":continue
  rp=o["physical_attempts"][-1];p=ROOT/rp["path"];assert sha_file(p)==rp["sha256"];inputs.append(p)
  f=E.parse(p).getroot().find("front");am=f.find("article-meta");jm=f.find("journal-meta")
  ids={x.get("pub-id-type"):text(x) for x in am.findall("article-id")}
  m,mp=med[ids["pmid"]];mj=m["journalInfo"];j=mj["journal"]
  authors=[dict(surname=x.findtext("name/surname"),given_names=x.findtext("name/given-names")) for g in am.findall("contrib-group") if g.get("content-type")!="editor" for x in g.findall("contrib") if x.get("contrib-type")=="author"]
  ma=m.get("authorList",{}).get("author",[])
  ac=[dict(position=i,original=a,MED=dict(lastName=b.get("lastName"),firstName=b.get("firstName")),same=norm(a["surname"])==norm(b.get("lastName")) and (norm(a["given_names"]) or "").replace(".","")==(norm(b.get("firstName")) or "").replace(".","")) for i,(a,b) in enumerate(zip(authors,ma),1)]
  issns=[text(x) for x in jm.findall("issn")];shared=bool(set(issns)&{j.get("issn"),j.get("essn")})
  title=text(am.find("title-group/article-title"));jt=text(jm.find("journal-title-group/journal-title"));vol=am.findtext("volume")
  fp=am.findtext("fpage");lp=am.findtext("lpage");eloc=am.findtext("elocation-id");loc=(fp+"-"+lp if fp and lp else eloc or fp)
  dates=[dict(attributes=x.attrib,year=x.findtext("year"),month=x.findtext("month"),day=x.findtext("day")) for x in am.findall("pub-date")]
  ck=dict(doi=norm(ids.get("doi"))==norm(m.get("doi")),pmid=ids.get("pmid")==str(m["id"]),pmcid=ids.get("pmcid")==o["source_id"],title=norm(title)==norm(m["title"]),full_ordered_authors=len(authors)==len(ma) and all(x["same"] for x in ac),shared_ISSN=shared,journal_name_or_exact_shared_ISSN=norm(jt)==norm(j["title"]) or shared,volume=vol==mj.get("volume"),pages_or_article_number=norm(loc)==norm(m.get("pageInfo")),year=str(mj.get("yearOfPublication")) in [x["year"] for x in dates])
  records.append(dict(source_id=o["source_id"],original_pointer=ptr(p),official_MED_pointer=ptr(mp),original_literals=dict(ids=ids,title=title,journal=jt,ISSNs=issns,publisher=jm.findtext("publisher/publisher-name"),volume=vol,issue=am.findtext("issue"),first_page=fp,last_page=lp,article_number=eloc,publication_dates=dates,authors=authors),MED_literals=dict(title=m["title"],journalInfo=mj,pageInfo=m.get("pageInfo"),authors=ma,doi=m.get("doi"),pmcid=m.get("pmcid"),publisher=m.get("publisher")),ordered_author_checks=ac,checks=ck,publication_identity_passed=all(ck.values()),shared_ISSN_journal_qualifier_projection_explicit=True,chemistry_body_or_graph_read=False,chemical_qualification=False,fresh=False))
 assert len(records)==6
 p=O/"six_original_publication_identity_checks.json";immutable_json(p,dict(task=TASK,created_at=now(),records=records,body_science_read=False,chemical_qualification=0))
 summary=O/"A3_summary.json";passed=sum(x["publication_identity_passed"] for x in records)
 immutable_json(summary,dict(task=TASK,created_at=now(),processed=6,passed=passed,pending=6-passed,failed_field_checks=[dict(source_id=x["source_id"],fields=[k for k,v in x["checks"].items() if not v]) for x in records if not x["publication_identity_passed"]],PDF_not_separately_checked=True,chemical_body_or_graph_read=False,source_chemical_qualified=0,fresh=0,originals_acquired_before_any_chemical_allocation=True,metadata_only_hints_not_scientific_exposure=True))
 role=role_manifest("A3 root bibliographic original-front validator","SS-E02-design-reference-r2",list(dict.fromkeys(inputs)),[p,summary],dict(processed=6,passed=passed,rejected=0,pending=6-passed),unprocessed=["No chemical/structure/assay qualification; metadata/front only","PDF versions not separately identity checked","Other5 sources remain scientifically unread under preregistered allocation"],read_holdout=False,read_model_outcome=False)
 role.update(human_reviewed=False,approval_type="agent_delegated",chemical_body_read=False,new_HTTP=0)
 rp=O/"role_A3_manifest.json";immutable_json(rp,role)
 print(json.dumps(dict(role=ptr(rp),summary=ptr(summary),passed=passed,pending=6-passed)))
if __name__=="__main__":main()
