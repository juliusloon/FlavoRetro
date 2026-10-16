"""Append-only C-E02 A3 publisher corroboration from actual official raw metadata."""
from __future__ import annotations
import json,re,html,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from scripts.task016_p7_c_e02_source_qualification import Meta,normalize,ptr,load,rows,js,save,OUT,ROOT,EXPECTED,text
from scripts.task016_p7_orchestrate import now,sha_file
from scripts.task016_p7_c_sources import rows as ledger_rows,OUT as COUT
P=OUT/"publisher_crosscheck_v1"
class Visible(HTMLParser):
 def __init__(self):super().__init__();self.suppress=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag in ("script","style"):self.suppress+=1
 def handle_endtag(self,tag):
  if tag in ("script","style") and self.suppress:self.suppress-=1
 def handle_data(self,data):
  if not self.suppress:self.parts.append(data)
def body(pointer):
 p=ROOT/pointer["path"]
 if sha_file(p)!=pointer["sha256"]:raise ValueError("actual acquired raw SHA drift")
 return p.read_text()
def html_fields(pointer):
 m=Meta();m.feed(body(pointer));v=Visible();v.feed(body(pointer))
 return m.fields," ".join(" ".join(v.parts).split())
def literal(pointer,phrase):
 _,s=html_fields(pointer)
 if phrase not in s:raise ValueError("official legal/journal literal absent: "+phrase)
 return dict(value=phrase,source_pointer=pointer,extraction="literal visible official page text; no substring from unrelated script")
def title_normalize(s):
 s=html.unescape(re.sub(r"<[^>]+>","",s))
 s=re.sub(r"\s*([‐‑–−-])\s*",r"\1",s)
 return normalize(s)
def main():
 if sha_file(OUT/"common_source_input_manifest.v3.json")!=EXPECTED:raise ValueError("raw common manifest drift")
 executions=[]
 for name in ("article_metadata_request_execution.json","publisher_journal_request_execution.json","Wiley_source_linked_metadata_request_execution.json","Wiley_registry_supplement_request_execution.json"):
  executions+=load(P/name)["executions"]
 executions.append(load(P/"BMC_brand_alias_request_execution.json"))
 for r in executions:
  p=r["HTTP_result"]
  if sha_file(ROOT/p["path"])!=p["sha256"]:raise ValueError("HTTP raw SHA mismatch")
 def get(source,route):
  return next(r["HTTP_result"] for r in executions if r["query"]["source"]==source and route in r["query"].get("route",r["query"].get("purpose","")))
 article={r["query"]["source"]:r["HTTP_result"] for r in executions if r["query"]["source"] in ("PMC9700910","PMC6036675","PMC11053098") and "official article citation" in r["query"].get("purpose","")}
 article["CHRYSIN"]=get("CHRYSIN","same-day publisher")
 journal={k:get(k,"journal official") for k in ("PMC9700910","PMC6036675","CHRYSIN","PMC11053098")}
 raw_pointers=[]
 for r in executions:
  h=r["HTTP_result"];raw_pointers.append(dict(path=h["path"],sha256=h["sha256"],status_code=h["status_code"],attempt_id=h["attempt_id"],url=h["url"]))
 original=rows(OUT/"A3_source_publication_identity.v2.jsonl")
 for r in original:raw_pointers+=r["source_evidence_pointers"]
 files=[ptr(P/n) for n in ("article_metadata_request_plan.json","article_metadata_request_execution.json","publisher_journal_request_plan.json","publisher_journal_request_execution.json","Wiley_source_linked_metadata_request_plan.json","Wiley_source_linked_metadata_request_execution.json","Wiley_registry_supplement_request_plan.json","Wiley_registry_supplement_request_execution.json","BMC_brand_alias_request_plan.json","BMC_brand_alias_request_execution.json")]
 input_doc=dict(task="TASK-016-P7",candidate_epoch_id="C-E02",phase="design",agent_role="A3 source-only publisher verifier",timestamp=now(),
  common_design_raw_input_pointer=ptr(OUT/"common_source_input_manifest.v3.json"),previous_identity_pointer=ptr(OUT/"A3_source_publication_identity.v2.jsonl"),
  previous_publisher_raw_input_pointer=ptr(P/"publisher_raw_input_manifest.json"),
  previous_failed_generation_preserved=True,
  source_original_pointers=raw_pointers,preregistered_acquisition_plan_execution_pointers=files,
  no_final_molecular_graphs=True,read_A5_finalgraphs=False,chemistry_extraction=False,human_reviewed=False)
 save(P/"publisher_raw_input_manifest.v2.json",input_doc)
 supplemental_sha=sha_file(P/"publisher_raw_input_manifest.v2.json")
 output=[]
 for index,r in enumerate(original,1):
  old_fields={k:r.get(k) for k in ("publisher_primary_value","publisher_secondary_value","publisher_cross_check_status","missing_publisher_legal_entity_preserved")}
  key=r["pmcid"] or "CHRYSIN"
  r["previous_identity_record_pointer"]=dict(**ptr(OUT/"A3_source_publication_identity.v2.jsonl"),jsonl_line=index)
  r["publisher_previous_fields_preserved"]=old_fields
  r["publisher_supplemental_raw_input_manifest_sha"]=supplemental_sha
  r["publisher_source_levels_not_conflated"]=True
  r["publisher_corporate_identity_not_inferred_from_name_similarity"]=True
  if key!="PMC11975207":
   ap=article[key];md,_=html_fields(ap)
   meta={k:md.get(k) for k in ("citation_publisher","dc.publisher","dc.rights","citation_doi","citation_journal_title")}
   citation=meta["citation_publisher"][0];prim=r["publisher_primary_value"]
   doi_match=normalize(meta["citation_doi"][0])==normalize(r["doi"])
   journal_match=normalize(meta["citation_journal_title"][0])==normalize(r["field_checks"]["journal"]["primary"])
   name_match=normalize(prim)==normalize(citation)
   alias=None
   if key in ("PMC9700910","PMC6036675") and prim=="BMC" and citation=="BioMed Central":
    alias=literal(get("BMC_brand_alias","official actual article footer"),"BMC (formerly BioMed Central)")
   if not (doi_match and journal_match and (name_match or alias is not None)):raise ValueError("publisher article identity fields disagree "+key)
   r["publisher_secondary_value"]=citation
   r["publisher_cross_check_status"]="verified publication publisher against official same-DOI article citation metadata; explicit first-party brand rename evidence where literal names differ; legal/copyright/operator fields separately retained"
   r["publisher_identity_verified"]=True
   r["publisher_checks"]=dict(primary_value=prim,secondary_value=citation,normalized_same_field_match=name_match,
    DOI_match=doi_match,journal_match=journal_match,official_article_literal_fields=meta,official_article_pointer=ap,
    official_journal_pointer=journal[key],publication_publisher_legal_entity_missing=key!="CHRYSIN",
    literal_publisher_name_difference_preserved=not name_match,explicit_official_brand_rename_pointer=alias,
    same_field_publisher_verified_by_literal_or_source_supported_brand_history=name_match or alias is not None)
   if key in ("PMC9700910","PMC6036675"):
    r["publisher_checks"]["journal_current_copyright_holder"]=literal(journal[key],"BioMed Central Ltd., part of Springer Nature")
    r["publisher_checks"]["journal_current_brand_explicit_BMC"]=literal(journal[key],"BMC")
    r["publisher_checks"]["current_platform_operator"]=literal(get("Springer legal","official legal"),"Springer Nature Limited")
    r["publisher_checks"]["current_journal_legal_entity_not_promoted_to_historical_paper_legal_entity"]=True
   elif key=="CHRYSIN":
    owner="Springer-Verlag GmbH Germany, part of Springer Nature"
    r["publisher_checks"]["article_publication_legal_copyright_holder"]=dict(value=owner,raw_dc_rights=meta["dc.rights"],source_pointer=ap)
    if owner not in meta["dc.rights"][0]:raise ValueError("article legal holder not literal")
    r["publisher_checks"]["journal_current_legal_copyright_holder"]=literal(journal[key],owner)
    r["publisher_checks"]["same_level_legal_copyright_holder_literal_match"]=True
    r["publisher_checks"]["current_platform_operator"]=literal(get("Springer legal","official legal"),"Springer Nature Limited")
   else:
    r["publisher_checks"]["current_platform_operator"]=literal(get("Nature legal","official legal"),"Springer Nature Limited")
    r["publisher_checks"]["official_journal_about_page_current_dc_rights"]=html_fields(journal[key])[0].get("dc.rights")
    r["publisher_checks"]["historical_NPG_legal_identity_equals_current_operator_not_asserted"]=True
  else:
   cross=get(key,"Crossref exact");msg=json.loads(body(cross))["message"]
   nlm=get(key,"NLM official");t=ET.fromstring(body(nlm));rec=t.find("NLMCatalogRecord")
   publisher=text(rec.find("PublicationInfo/Imprint[@ImprintType='Current']/Entity"))
   catalog_title=text(rec.find("TitleMain/Title"));issn=[text(e) for e in rec.findall("ISSN")]
   member=get(key,"Crossref registered");membership=json.loads(body(member))["message"]
   front_ptr=next(p for p in r["source_evidence_pointers"] if "fullTextXML" in p["path"]);front=ET.fromstring(body(front_ptr))
   copyright=text(front.find("front/article-meta/permissions/copyright-statement"))
   m=re.search(r"published by (.+?)\.$",copyright)
   if not m:raise ValueError("Wiley source publication legal statement missing")
   legal=m.group(1)
   am=front.find("front/article-meta")
   prim_title=text(am.find("title-group/article-title"))
   authors=[text(e.find("surname")) for e in am.findall("contrib-group/contrib/name")]
   checks=dict(DOI_match=normalize(msg["DOI"])==normalize(r["doi"]),
    journal_match=normalize(msg["container-title"][0])==normalize(r["field_checks"]["journal"]["primary"]),
    title_match_after_literal_inline_HTML_and_hyphen_whitespace_format_normalization=title_normalize(msg["title"][0])==title_normalize(prim_title),
    volume_match=str(msg["volume"])==r["field_checks"]["volume"]["primary"],
    issue_match=str(msg["issue"])==r["field_checks"]["issue"]["primary"],
    pages_match=normalize(msg["page"])==normalize(r["field_checks"]["pages_or_article_number"]["primary"]),
    publication_year_match=str(msg["published-print"]["date-parts"][0][0])==r["field_checks"]["year"]["primary"],
    author_order_match=[normalize(a.get("family")) for a in msg["author"]]==[normalize(a) for a in authors],
    exact_DOI_publisher_matches_official_NLM_current_journal_imprint=normalize(msg["publisher"])==normalize(publisher),
    NLM_journal_title_match=normalize(catalog_title)==normalize(msg["container-title"][0]),
    NLM_electronic_ISSN_match="1097-0290" in issn and "1097-0290" in msg["ISSN"],
    registered_member_id_match=str(membership["id"])==str(msg["member"]),
    registered_member_publisher_match=normalize(membership["primary-name"])==normalize(msg["publisher"]),
    registered_DOI_prefix_match="10.1002" in membership["prefixes"],
    original_article_publication_legal_entity_explicit=legal=="Wiley Periodicals LLC")
   if not all(checks.values()):raise ValueError("Fc bibliographic/publisher supplement differs "+json.dumps(checks))
   r["publisher_primary_value"]=legal
   r["publisher_primary_field"]="original front/article-meta/permissions/copyright-statement: explicitly published by; journal-meta/publisher remains absent"
   r["publisher_secondary_value"]=msg["publisher"]
   r["publisher_identity_verified"]=True
   r["missing_journal_meta_publisher_preserved"]=True
   r["publisher_cross_check_status"]="verified official same-DOI registered publisher Wiley equals official NLM journal current publication imprint Wiley; original paper explicitly names legal publisher Wiley Periodicals LLC; brand and legal entity remain distinct fields"
   r["publisher_checks"]=dict(checks=checks,original_article_copyright_statement=copyright,
    publication_legal_entity=legal,publication_legal_entity_original_pointer=front_ptr,
    original_journal_meta_publisher_missing=True,
    same_level_publisher_name_primary_registered_DOI=msg["publisher"],same_level_publisher_name_secondary_NLM=publisher,
    exact_DOI_metadata_raw_fields={k:msg.get(k) for k in ("DOI","title","publisher","container-title","volume","issue","page","published-print","published-online","ISSN","member")},
    Crossref_pointer=dict(**cross,json_pointer="/message"),
    NLM_pointer=dict(**nlm,XML_path="/NLMCatalogRecordSet/NLMCatalogRecord/PublicationInfo/Imprint[@ImprintType='Current']/Entity"),
    NLM_catalog_title=catalog_title,NLM_ISSNs=issn,
    registered_member_pointer=dict(**member,json_pointer="/message"),
    legal_entity_second_independent_corporate_document_available=False,
    corporate_brand_legal_entity_string_equality_not_asserted=True,
    direct_official_Wiley_article_and_journal_access="403 preserved; public registry/PMC metadata used; no access-control bypass",
    source_input_allows_missing_legal_corporate_fields=True)
  r["source_identity_verified"]=bool(r["source_publication_identity_matches"] and r["publisher_identity_verified"])
  r["chemical_qualification_not_granted"]=True;r["evidence_eligible"]=False
  r["schema_version"]="v3_append_only_publisher_source_fields"
  output.append(r)
 js(OUT/"A3_source_publication_identity.v3.jsonl",output)
 budget=ledger_rows(COUT/"http_ledger.jsonl")
 failures=[dict(source=x["query"]["source"],url=x["HTTP_result"]["url"],status_code=x["HTTP_result"]["status_code"],
  path=x["HTTP_result"]["path"],sha256=x["HTTP_result"]["sha256"]) for x in executions if x["HTTP_result"]["status_code"]!=200]
 save(OUT/"role_A3_manifest.v3.json",dict(task="TASK-016-P7",candidate_epoch_id="C-E02",agent_role="A3 Source Identity Verifier",timestamp=now(),
  input_manifest_sha=EXPECTED,publisher_raw_input_manifest_pointer=ptr(P/"publisher_raw_input_manifest.v2.json"),
  previous_A3_manifest_pointer=ptr(OUT/"role_A3_manifest.v2.json"),
  counts=dict(sources_processed=len(output),bibliographic_identity_matches=sum(r["source_publication_identity_matches"] for r in output),
   publication_publisher_identity_verified=sum(r["publisher_identity_verified"] for r in output),HTTP_requests_executed=len(executions),
   actual_HTTP200=sum(x["HTTP_result"]["status_code"]==200 for x in executions),actual_access_failures=len(failures)),
  output_file_sha={str((OUT/"A3_source_publication_identity.v3.jsonl").relative_to(ROOT)):sha_file(OUT/"A3_source_publication_identity.v3.jsonl")},
  source_evidence_pointers=raw_pointers,failed_requests_preserved=failures,
  unresolved_or_missing=["Wiley direct official article/journal403; official public Crossref/NLM and PMC copyright fields used",
   "Missing independent corporate legal-entity document preserved; brand/imprint/legal publisher/platform operator never treated as equal solely by name",
   "Nature historical legal corporate identity not asserted equal to current Springer Nature Limited website operator"],
  C_budget_after=dict(HTTP_requests=len(budget),bytes=sum(r["bytes"] for r in budget),article_versions=sum(r["kind"]=="article_version" for r in budget),
   attachments=sum(r["kind"]=="attachment" for r in budget),hard_limits=dict(HTTP_requests=2500,bytes=2*1024**3,article_versions=120,attachments=200)),
  evidence_eligible_granted=False,chemical_qualification_not_granted=True,read_A5_finalgraphs=False,
  read_current_or_future_holdout=False,read_model_outcomes=False,scope_built_or_modified=False,fresh_source_discovery=False,
  mass_originals_and_prior_A4_files_unchanged=True,human_reviewed=False,approval_type="agent_delegated"))
 print(json.dumps(dict(manifest=ptr(OUT/"role_A3_manifest.v3.json"),identity=ptr(OUT/"A3_source_publication_identity.v3.jsonl"),
  raw_input=ptr(P/"publisher_raw_input_manifest.v2.json"),sources=len(output),publisher_name_verified=sum(r["publisher_identity_verified"] for r in output))))
if __name__=="__main__":main()
