"""Root A3: independently parse original JATS fronts and official MED, no chemical body."""
import json,re,html,unicodedata,xml.etree.ElementTree as ET
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,verify_stage_chain,role_manifest
from scripts.task016_p7_c_e02_http import immutable_json
B=ROOT/"outputs/task016-p7/v1/C/E02/fresh/C-E02-R7"
D=ROOT/"outputs/task016-p7/v1/C/E02/stages/batches/C-E02-R7"
O=B/"root_A3_publication_identity_v2"
def load(p):return json.loads(p.read_text())
def ptr(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def txt(n):return "".join(n.itertext()).strip() if n is not None else None
def norm(s):
    if s is None:return None
    x=html.unescape(html.unescape(s))
    x=re.sub(r"<[^>]+>","",x)
    x=unicodedata.normalize("NFKC",x).replace("–","-").replace("—","-")
    return re.sub(r"\s+","",x).casefold().rstrip(".")
def given(s):return norm(s).replace(".","") if s else None
def main():
    assert not O.exists()
    ip=D/"fresh_source_input_manifest.json";g5=D/"G5_FRESH_HOLDOUT_ACQUIRE.json"
    verify_stage_chain(g5,sha_file(g5))
    si=B/"source_metadata_identity_inventory.v2.json";sources=load(si)["sources"]
    mp=ROOT/"data/raw/task016-p7/C/E02/C-E02-RAW-9a496608e4dc40b09ea9380b666bcba2.metadata"
    med=load(mp)["resultList"]["result"];allinputs=[B/"root_A3_publication_identity_failure_v1/failure.json",si,mp,ip,g5,ROOT/"scripts/task016_p7_c_e02_r7_root_identity_v2.py"]
    checks=[];dispositions=[]
    for s in sources:
        if not s["source_front_metadata"]:
            matches=[x for x in med if x.get("source")=="MED" and str(x["id"])==s["pmid"]]
            dispositions.append(dict(source_id=s["source_locator_id"],source_hint=dict(doi=s["doi"],pmid=s["pmid"],pmcid=s["pmcid"]),actual_MED_records=matches,MED_raw_pointer=ptr(mp) if matches else None,original_publication_front_available=False,source_identity_qualification="pending_original_or_second_authoritative_identity_chain",chemical_qualification=False,fresh=False,missing_hint_fields_not_filled_implicitly=True))
            continue
        m=next(x for x in med if x.get("source")=="MED" and str(x["id"])==s["pmid"])
        assert m["doi"].lower()==s["doi"].lower() and m.get("pmcid")==s["pmcid"],s["source_locator_id"]
        meta=dict(pmid=m["id"],pmcid=m.get("pmcid"),doi=m.get("doi"),title=m.get("title"),authors=m.get("authorList",{}).get("author",[]),journalInfo=m.get("journalInfo"),pageInfo=m.get("pageInfo"),publisher=m.get("publisher"),pubYear=m.get("pubYear"),firstPublicationDate=m.get("firstPublicationDate"))
        if not s["source_front_metadata"]:
            dispositions.append(dict(source_id=s["source_locator_id"],doi=s["doi"],pmid=s["pmid"],pmcid=s["pmcid"],MED_raw_pointer=ptr(mp),actual_MED_row_identity_match=True,original_publication_front_available=False,source_identity_qualification="pending_original_or_second_authoritative_identity_chain",metadata_literal=meta,chemical_qualification=False,fresh=False))
            continue
        p=ROOT/s["source_front_metadata"]["raw_original_pointer"]["path"];assert sha_file(p)==s["source_front_metadata"]["raw_original_pointer"]["sha256"]
        allinputs.append(p);f=ET.parse(p).getroot().find("front");am=f.find("article-meta");jm=f.find("journal-meta")
        ids={x.get("pub-id-type"):txt(x) for x in am.findall("article-id")}
        authors=[dict(surname=x.findtext("name/surname"),given_names=x.findtext("name/given-names")) for x in am.findall("contrib-group/contrib") if x.get("contrib-type")=="author"]
        title=txt(am.find("title-group/article-title"));journal=txt(jm.find("journal-title-group/journal-title"))
        issns=[txt(x) for x in jm.findall("issn")];mj=m["journalInfo"];mja=mj["journal"]
        missing_issn=not issns
        original=dict(ids=ids,title=title,authors=authors,journal=journal,ISSNs=issns,publisher=jm.findtext("publisher/publisher-name"),volume=am.findtext("volume"),issue=am.findtext("issue"),fpage=am.findtext("fpage"),lpage=am.findtext("lpage"),elocation_id=am.findtext("elocation-id"),publication_dates=[dict(attributes=x.attrib,year=x.findtext("year"),month=x.findtext("month"),day=x.findtext("day")) for x in am.findall("pub-date")])
        ma=meta["authors"];order=[]
        for i,(a,b) in enumerate(zip(authors,ma),1):
            ok=norm(a["surname"])==norm(b.get("lastName")) and given(a["given_names"])==given(b.get("firstName"))
            order.append(dict(position=i,original=a,MED=dict(lastName=b.get("lastName"),firstName=b.get("firstName")),same_after_explicit_initial_period_projection=ok))
        location=(original["fpage"]+"-"+original["lpage"] if original["fpage"] and original["lpage"] else original["elocation_id"] or original["fpage"])
        fieldchecks=dict(doi=norm(ids.get("doi"))==norm(s["doi"]),pmid=ids.get("pmid")==s["pmid"],pmcid=ids.get("pmcid")==s["pmcid"],title=norm(title)==norm(m["title"]),full_ordered_authors=len(authors)==len(ma) and all(x["same_after_explicit_initial_period_projection"] for x in order),journal_title=norm(journal)==norm(mja["title"]),shared_ISSN=bool(set(issns)&{mja.get("issn"),mja.get("essn")}) if not missing_issn else None,volume=original["volume"]==mj["volume"],page_or_article_number=location==m.get("pageInfo"),year=str(mj["yearOfPublication"]) in [x["year"] for x in original["publication_dates"]])
        assert all(v for v in fieldchecks.values() if v is not None),(s["source_locator_id"],fieldchecks)
        row=dict(source_id=s["source_locator_id"],doi=s["doi"],pmid=s["pmid"],pmcid=s["pmcid"],original_pointer=ptr(p),MED_pointer=ptr(mp),original_front_literals=original,MED_literals=meta,field_checks=fieldchecks,ordered_author_comparison=order,source_publication_identity_passed=True,projections=["HTML unescape twice then remove actual inline markup; NFKC, explicit typography dash and whitespace/case; final title period only", "Given-name initial periods removed for comparison, original literals retained; full surname and ordered full names preserved"],missing_and_differences_preserved=dict(original_issue=original["issue"],MED_issue=mj.get("issue"),original_publisher=original["publisher"],MED_publisher=meta["publisher"],dates_have_distinct_publication_collection_semantics=True),body_chemical_content_read=False,chemical_evidence_qualification=False,fresh_admitted=False)
        checks.append(row);dispositions.append(dict(source_id=s["source_locator_id"],doi=s["doi"],pmid=s["pmid"],pmcid=s["pmcid"],source_publication_identity="passed_original_JATS_vs_official_MED",source_chemical_qualification="pending_A4_A5_A6",fresh=False))
    assert len(checks)==3 and len(dispositions)==9
    out=[]
    for n,x in [
      ("three_original_publication_identity_checks.json",dict(task=TASK,created_at=now(),checks=checks,chemical_body_read=False,identity_only=True)),
      ("complete_nine_source_dispositions.json",dict(task=TASK,sources=dispositions,processed=9,original_identity_passed=3,pending=6,chemical_qualification=0)),
      ("A3_summary.json",dict(task=TASK,created_at=now(),G5_pointer=ptr(g5),input_pointer=ptr(ip),passed_original_sources=3,pending_original_sources=6,full_ordered_author_counts=[len(x["original_front_literals"]["authors"]) for x in checks],raw_source_versions=3,verified_JATS_front_versions=3,PDF_identity_not_separately_checked=True,new_HTTP=0,chemical_body_read=False,source_qualified=0,fresh_admitted=0,human_reviewed=False,source_saturation=False))]:
        p=O/n;immutable_json(p,x);out.append(p)
    rp=O/"role_A3_manifest.json"
    role=role_manifest("A3 root source-original publication identity","C-E02-R7",allinputs,out,dict(processed=9,passed=3,rejected=0,pending=6),unprocessed=["Six sources lack usable original publication front in current raw package","PDF versions not separately identity-checked; JATS original matches source DOI/PMID/PMCID front","Chemical/reaction/full-graph/fresh identity closure remains A4/A5/A6"],read_holdout=False,read_model_outcome=False)
    role.update(approval_type="agent_delegated",human_reviewed=False,new_HTTP=0,original_chemical_body_read=False,chemical_evidence_qualification=0,fresh_admitted=0)
    immutable_json(rp,role)
    print(json.dumps(dict(role=ptr(rp),summary=ptr(out[-1]),passed=3,pending=6,chemical_qualification=0),ensure_ascii=False))
if __name__=="__main__":main()
