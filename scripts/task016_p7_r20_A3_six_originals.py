"""R20 independent A3 original-front identity of six R18/R19 raw PMC XML.
Preserves earlier R18 false magic result, no reading scientific bodies.
"""
import json,hashlib,xml.etree.ElementTree as ET,html,re
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R18=B/"governance/R18-eight-PMC-primary-original-access-v1"
R19=B/"governance/R19-three-PMC-targeted-original-access-v1"
O=B/"governance/R20-six-original-front-identity-v1"
def sha(p):return sha_file(ROOT/p)
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def js(p):return json.loads((ROOT/p).read_text())
def ptr(p):return dict(path=str(p),sha256=sha(p),bytes=(ROOT/p).stat().st_size)
def txt(p):return " ".join("".join(p.itertext()).split()) if p is not None else None
def save(p,x):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE")
 write(T,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE_FRONT_ID")
 for f in ("C","SS"):
  g4=B/f"{f}/E02/stages/G4_SCOPE_FREEZE.json"
  verify_stage_chain(ROOT/g4,sha(g4))
 allraw=[(R18,r) for r in rows(R18/"http_ledger.jsonl")]+[(R19,r) for r in rows(R19/"http_ledger.jsonl")]
 selected=[(base,r) for base,r in allraw if r.get("status_code")==200 and r.get("bytes",0)>1000]
 assert len(selected)==6
 out=[]
 for origin,r in selected:
  path=Path(r["path"]);bytes_=(ROOT/path).read_bytes()
  assert hashlib.sha256(bytes_).hexdigest()==r["sha256"]
  tree=ET.fromstring(bytes_);front=tree.find("./front")
  if front is None:raise RuntimeError("NO_FRONT "+r["source_id"])
  ids={v.get("pub-id-type"):txt(v) for v in front.findall(".//article-meta/article-id") if v.get("pub-id-type")}
  pmcid=ids.get("pmcid")
  if pmcid!=r["source_id"]:raise RuntimeError("PMCID_ORIGINAL_FRONT_MISMATCH "+str((pmcid,r["source_id"])))
  article=front.find("./article-meta")
  title=txt(article.find("./title-group/article-title")) if article is not None else None
  journal=txt(front.find("./journal-meta/journal-title-group/journal-title"))
  if not journal:journal=txt(front.find("./journal-meta/journal-title-group/journal-title"))
  if not journal:journal=txt(front.find("./journal-meta/journal-title"))
  doi=ids.get("doi")
  pub_years=sorted(set(txt(y) for y in front.findall(".//article-meta/pub-date/year") if txt(y)))
  licences=sorted(set(x.get("{http://www.w3.org/1999/xlink}href") or "" for x in front.findall(".//license")))
  source=origin.name
  results=dict(family=r["family"],PMCID=pmcid,PMID=ids.get("pmid"),DOI=doi,
    article_title=title,journal=journal,publication_years=pub_years,
    original_source_path=str(path),original_SHA=r["sha256"],
    original_bytes=r["bytes"],original_article_root=tree.tag,
    source_custody=source,license_links=licences,read_scope="front excluding abstract body",
    official_PMC_original_front_identity=bool(pmcid and doi and title and pub_years),
    not_yet_qualified_scientific_reaction=True,not_yet_dual_structure_extracted=True,
    not_fresh_by_original_alone=True)
  out.append(results)
 a={"task":T,"role":"A3_original_front_only","timestamp":datetime.now(timezone.utc).isoformat(),
    "source_universe":[ptr(R18/"raw_custody_summary.json"),ptr(R19/"raw_custody_summary.json")],
    "sources":out,"source_count":len(out),
    "front_identified":sum(x["official_PMC_original_front_identity"] for x in out),
    "no_abstract_or_body_read":True,"scientific_content_exposure_status":"some web excerpts seen before formal preread, permanently expose before body; not fresh",
    "no_new_HTTP":True,"no_new_MCTS":True,
    "prior_R18_classification_false_due_to_XML_DOCTYPE":True,
    "R18_original_false_summary_SHA":sha(R18/"raw_custody_summary.json"),
    "correction_reason":"JATS fullTextXML may begin with DOCTYPE rather than XML declaration or <article; original bytes parse as complete <article> with matching article-id PMCID.",
    "fresh_admitted":0,"human_reviewed":False}
 save(O/"A3_six_original_front_identity_v1.json",a)
 save(O/"source_RAW_custody_corrected_v2.json",dict(task=T,at=a["timestamp"],
    total_acquired_usable_source_originals=len(out),
    by_round={"R18":sum(x["source_custody"]==R18.name for x in out),
              "R19":sum(x["source_custody"]==R19.name for x in out)},
    by_family={fam:sum(x["family"]==fam for x in out) for fam in ("C","SS")},
    total_HTTP=len(rows(R18/"http_ledger.jsonl"))+len(rows(R19/"http_ledger.jsonl")),
    A3_six_SHA=sha(O/"A3_six_original_front_identity_v1.json"),
    no_chemical_admission=True,zero_fresh=True))
 print(json.dumps(dict(originals=len(out),front_verified=a["front_identified"],
  sources=[(x["family"],x["PMCID"],x["DOI"]) for x in out])))
 if a["front_identified"]!=6:raise RuntimeError("A3_PENDING_FIELDS")
if __name__=="__main__":main()

