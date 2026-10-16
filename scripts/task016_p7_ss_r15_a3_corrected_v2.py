"""SS R15 A3-v2: correct date-parts parser; preserve incorrect v1 evidence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,html,json,re
from scripts.operate import ROOT,write
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"SS/E02/fresh/SS-E02-R15-four-new-primary-bibliography-v1"
R14=B/"SS/E02/fresh/SS-E02-R14-broad-title-discovery-v1"
P=O/"A3_two_route_bibliographic_preflight_v2.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def canon(t):
 t=html.unescape(re.sub(r"<[^>]*>","",str(t or "")))
 return re.sub(r"[^a-z0-9]+","",t.casefold())
def dates(obj):
 years=set()
 for k in ("issued","published","published-online","published-print","created"):
  value=obj.get(k)
  if isinstance(value,dict):
   for row in value.get("date-parts",[]):
    if row and type(row[0])==int and 1900<=row[0]<=2100:years.add(row[0])
 return sorted(years)
def main():
 if (ROOT/P).exists():raise RuntimeError("IMMUTABLE_R15_A3_V2")
 v1=read(O/"A3_two_route_bibliographic_preflight.json")
 a=read(R14/"discovered_title_identity_dispositions.json")
 old={r["doi"]:r for r in a["all_titles"]}
 out=[]
 for x in rows(O/"crossref_bibliography_projection.jsonl"):
  doi=x["DOI"];m=x["metadata"];a=old[doi]
  if not m:raise RuntimeError("MISSING_OFFICIAL_SOURCE")
  raw=x["original_raw"]
  if sha(raw["path"])!=raw["sha256"]:raise RuntimeError("CROSSREF_RAW_DRIFT")
  title=(m.get("title") or [""])[0];y=int(a["official_title_metadata"]["pubYear"])
  yy=dates(m)
  check=dict(exact_DOI=m.get("DOI","").casefold()==doi.casefold(),
   exact_normalized_title=canon(title)==canon(a["title"]),
   year_match=y in yy,
   source_is_primary_journal_article=m.get("type")=="journal-article",
   journal_present=bool(m.get("container-title")),
   publisher_present=bool(m.get("publisher")),
   EPMC_subscription_required=a["official_title_metadata"]["fullTextUrlList"]["fullTextUrl"][0]["availability"]=="Subscription required")
  out.append(dict(doi=doi,pmid=a["pmid"],Crossref_years=yy,EPMC_year=y,
    Crossref_title=title,EPMC_title=a["title"],
    Crossref_journal=m.get("container-title"),Crossref_publisher=m.get("publisher"),
    checks=check,metadata_identity_verified=all(check.values()),
    original_raw=raw,historical_source_exposure_literal_negative_only=True,
    previous_R10_title_cluster_absent=True,
    real_historical_chemical_exposure_alias_graph_status="unknown",
    original_full_scientific_article_present=False,
    original_A3_front_complete=False,
    full_donor_acceptor_product_structure_qualified=False,
    frozen_scope_site_evidence=None,scientific_reaction_qualified=False,
    fresh_eligible=False,access_status="subscription_required_in_EPMC_metadata"))
 original_errors=[x for x in v1["records"] if x["checks"].get("same_pub_year") is False]
 msg=dict(task=TASK,epoch_id="SS-E02",version="A3_two_route_bibliography_v2",
    corrected_at=datetime.now(timezone.utc).isoformat(),agent_role="A3_metadata_only",
    supersedes_v1_path=str(O/"A3_two_route_bibliographic_preflight.json"),
    supersedes_v1_SHA=sha(O/"A3_two_route_bibliographic_preflight.json"),
    correction_reason="v1 converted nested Crossref date-parts to strings before integer-year membership check; four false year conflicts, original bytes preserved",
    initial_false_year_conflict_count=len(original_errors),records=out,
    count=dict(processed=4,bibliography_verified=sum(r["metadata_identity_verified"] for r in out),
      original_publication_identity_verified=0,science_body_read=0,
      complete_chemical_reaction_qualified=0,fresh_admitted=0),
    original_R14_SHA=sha(R14/"discovered_title_identity_dispositions.json"),
    raw_originals_acquired=0,no_chemical_content_read=True,scope_bank_unchanged=True,
    approval_type="agent_delegated",human_reviewed=False)
 write(TASK,str(P),json.dumps(msg,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(corrected_A3=msg["count"],Crossref_years=[r["Crossref_years"] for r in out])))
 if msg["count"]["bibliography_verified"]!=4:raise RuntimeError("BIBLIOGRAPHIC_CONFLICT_PENDING")
if __name__=="__main__":main()

