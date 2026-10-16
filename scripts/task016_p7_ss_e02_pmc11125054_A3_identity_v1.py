#!/usr/bin/env python3
"""A3 official JATS front versus NCBI MED identity. NEVER reads article body."""
from __future__ import annotations
import sys,json,re,hashlib,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,ContractError
TASK="TASK-016-P7"
G="outputs/task016-p7/v1/SS/E02/stages/batches/SS-E02-R2-PMC11125054/G5_FRESH_HOLDOUT_ACQUIRE.json"
SRC="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-original/"
OUT="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-A3/"
SELF="scripts/task016_p7_ss_e02_pmc11125054_A3_identity_v1.py"
def sha(p):return sha_file(ROOT/p)
def at():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads((ROOT/p).read_text())
def save(p,r):
 if (ROOT/p).exists():raise ContractError("A3 immutable output exists")
 write(TASK,p,json.dumps(r,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def norm(s):
 if not isinstance(s,str):return ""
 return re.sub(r"[\W_]+","",s.casefold())
def prereg():
 verify_stage_chain(G,sha(G))
 objs=read(SRC+"raw_manifest.json")["objects"]
 if sorted(x["kind"] for x in objs)!=["article_version","metadata"]:
  raise ContractError("missing two independent original identity sources")
 save(OUT+"A3_pre_execution_manifest.json",dict(task=TASK,epoch_id="SS-E02",
  role="A3 Source Identity Verifier, no chemical reading",
  timestamp=at(),input_shas={x["path"]:sha(x["path"]) for x in objs},
  source_raw_manifest_sha=sha(SRC+"raw_manifest.json"),
  G5_stage_sha=sha(G),code_sha=sha(SELF),
  fields=["PMCID","PMID","DOI","ordered authors","title","journal",
   "publication year","volume","issue","article number or pages"],
  no_scientific_body_read=True,no_structure_extract=True,
  no_chemical_qualification=True,fulltext_identity_only=True,
  no_fresh_admission=True,read_holdout=False,read_model_outcome=False))
 print("A3 original front and MED SHA-bound before verification")
def verify():
 verify_stage_chain(G,sha(G))
 plan=read(OUT+"A3_pre_execution_manifest.json")
 if sha(SELF)!=plan["code_sha"] or sha(G)!=plan["G5_stage_sha"]:
  raise ContractError("A3 code/stage changed after prereg")
 objs=read(SRC+"raw_manifest.json")["objects"]
 for x in objs:
  if plan["input_shas"][x["path"]]!=sha(x["path"]):
   raise ContractError("raw source drift")
 original=next(x for x in objs if x["kind"]=="article_version")
 metadata=next(x for x in objs if x["kind"]=="metadata")
 doc=ET.parse(ROOT/original["path"]).getroot()
 medall=json.loads((ROOT/metadata["path"]).read_text())
 med=medall["result"].get("38794460")
 if med is None:raise ContractError("official MED absent")
 front=doc.find("front")
 if front is None:raise ContractError("original JATS front missing")
 ids={x.attrib.get("pub-id-type"):x.text for x in front.findall("article-meta/article-id")}
 title_node=front.find("article-meta/title-group/article-title")
 if title_node is None:raise ContractError("title original missing")
 title=" ".join(title_node.itertext())
 medids={x["idtype"]:x["value"] for x in med.get("articleids",[])}
 source_authors=[dict(surname=a.findtext("name/surname"),
  given=a.findtext("name/given-names")) for a in front.findall("article-meta/contrib-group/contrib")
  if a.attrib.get("contrib-type")=="author"]
 official_authors=[a["name"] for a in med.get("authors",[])]
 surnames_ok=len(source_authors)==len(official_authors) and all(
  n["surname"].casefold()==m.split()[0].casefold() for n,m in zip(source_authors,official_authors))
 journal=front.findtext("journal-meta/journal-title-group/journal-title")
 medjournal=med.get("fulljournalname")
 year=front.findtext("article-meta/pub-date/year")
 issue=front.findtext("article-meta/issue")
 volume=front.findtext("article-meta/volume")
 article_locator=front.findtext("article-meta/elocation-id") or front.findtext("article-meta/fpage")
 checks=dict(
  original_DOI_matches_MED=(ids.get("doi")==medids.get("doi")=="10.3390/plants13101390"),
  original_PMCID_matches_MED=(ids.get("pmcid")==medids.get("pmc")=="PMC11125054"),
  original_PMID_matches_MED=(ids.get("pmid")==medids.get("pubmed")=="38794460"),
  ordered_author_surnames_equal=surnames_ok,
  normalized_title_equal=(norm(title)==norm(med.get("title"))),
  journal_identity_base_equal=(norm(journal or "")==norm((medjournal or "").split("(")[0].strip())),
  year_equal=(str(year)=="2024" and str(med.get("pubdate","")).startswith("2024")),
  volume_equal=(volume==str(med.get("volume"))=="13"),
  issue_equal=(issue==str(med.get("issue"))=="10"),
  article_number_original_present=(article_locator=="1390"))
 status="verified_original_and_med_bibliography" if all(checks.values()) else "deferred_identity_conflict"
 result=dict(task=TASK,family="SS",epoch_id="SS-E02",source_id="PMC11125054",
  role="A3",timestamp=at(),status=status,
  original_front=dict(ids={k:ids.get(k) for k in ("pmcid","pmid","doi")},title=title,
   journal=journal,year=year,volume=volume,issue=issue,article_locator=article_locator,
   ordered_author_surnames=[x["surname"] for x in source_authors]),
  MED_summary=dict(ids={k:medids.get(k) for k in ("pubmed","pmc","doi")},title=med.get("title"),
   journal=medjournal,volume=med.get("volume"),issue=med.get("issue"),
   published_date=med.get("pubdate"),ordered_authors=official_authors,
   pages_unavailable_or_empty=(med.get("pages") in (None,""))),
  checks=checks,passed=sum(checks.values()),total=len(checks),
  original_raw_SHA=sha(original["path"]),official_med_raw_SHA=sha(metadata["path"]),
  publication_identity_verified=all(checks.values()),
  original_article_locator_not_MED_independently_corroborated=True,
  independent_chemical_validation=False,
  chemistry_body_or_graph_read=False,
  fulltext_present_but_scientific_assay_unreviewed=True,
  source_applicability=None,source_eligible_for_G6=False,
  evidence_fresh_eligibility_not_established=True,source_saturation=False,
  human_reviewed=False)
 save(OUT+"A3_publication_identity.json",result)
 save(OUT+"role_A3_manifest.json",dict(task=TASK,epoch_id="SS-E02",
  agent_role="A3 Source Identity Verifier",timestamp=at(),
  preregistered_manifest_sha=sha(OUT+"A3_pre_execution_manifest.json"),
  source_article_SHA=sha(original["path"]),MED_SHA=sha(metadata["path"]),
  output_sha=sha(OUT+"A3_publication_identity.json"),counts=dict(
  processed=len(checks),passed=sum(checks.values()),
  rejected=0,pending=len(checks)-sum(checks.values())),
  read_holdout=False,read_model_outcome=False,body_science_read=False,
  G6_admitted=0,metric=None,source_saturation=False,
  human_reviewed=False,independent_chemical_validation=False))
 if not all(checks.values()):raise ContractError("A3 identity disagreement; no promotion")
 print(json.dumps(dict(status=status,passed=sum(checks.values()),total=len(checks),
  G6=0,science_body_read=False),ensure_ascii=False))
if __name__=="__main__":
 {"pre":prereg,"verify":verify}[sys.argv[1]]()
