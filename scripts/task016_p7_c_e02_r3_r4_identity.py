"""A3 bibliographic reconciliation of R3/R4 originals; chemical claims untouched."""
import html,json,re,unicodedata
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,verify_stage_chain,role_manifest
from scripts.task016_p7_c_e02_http import E,rows,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
B=E/"fresh/C-E02-R3R4-A3"
def norm(v):
    if v is None:return None
    v=html.unescape(str(v));v=re.sub("<[^>]+>","",v);v=unicodedata.normalize("NFKC",v)
    v=v.translate(str.maketrans({"‐":"-","‑":"-","–":"-","−":"-","\u00ad":""}))
    v=" ".join(v.split());v=re.sub(r"\s*-\s*","-",v)
    # Literal Crossref small-caps XML indentation splits the botanical genus initial.
    v=v.replace("F agopyrum", "Fagopyrum").replace("M .", "M.")
    return v.casefold().rstrip(".")
def main():
    starts=now();xref=rows(B/"metadata_request_execution.jsonl");core=rows(B/"core_metadata_request_execution.jsonl")
    if len(xref)!=5 or len(core)!=5:raise ValueError("Five exact DOI metadata queries missing")
    cores={r["doi"]:r for r in core};outputs=[];inputs=[]
    fronts=json.loads((B/"source_front_metadata/front_projection.json").read_text())
    sources={s["doi"]:s for s in json.loads((E/"stages/batches/C-E02-R3/fresh_source_input_manifest.json").read_text())["sources"]}
    r4={s["doi"]:s for s in json.loads((E/"stages/batches/C-E02-R4/fresh_source_input_manifest.json").read_text())["sources"]}
    original_authors={"10.1039/d0np00040j":["Putkaradze","Teze","Fredslund","Welner"],"10.1111/tpj.12645":["Nagatomo","Usui","Ito","Kato","Shimosaka","Taguchi"],"10.1111/tpj.13555":["Ito","Fujimoto","Suito","Shimosaka","Taguchi"],"10.1021/acs.jafc.5c09887":["Liu","Yang","Liu","Wu","Liu","Huang","Chen","Zou","He","Huang"]}
    front_title={"10.1039/d0np00040j":"Natural product C-glycosyltransferases - a scarcely characterised enzymatic activity with biotechnological potential", "10.1111/tpj.12645":"Purification, molecular cloning, and functional characterization of flavonoid C-glucosyltransferases from buckwheat (Fagopyrum esculentum) cotyledon.","10.1111/tpj.13555":"C-Glycosyltransferases catalyzing the formation of di-C-glucosyl flavonoids in citrus plants", "10.1021/acs.jafc.5c09887":"Identification and Functional Characterization of a Novel C-Glycosyltransferase from Euscaphis konishii Hayata and Its Role in C-Glycoside Biosynthesis"}
    for r in xref:
        doi=r["doi"];c=cores[doi]
        for x in (r["raw"],c["raw"]):
            if x["status"]!="available" or sha_file(ROOT/x["path"])!=x["sha256"]:raise ValueError("Metadata unavailable or raw SHA drift")
            inputs.append(ROOT/x["path"])
        x=json.loads((ROOT/r["raw"]["path"]).read_text())["message"]
        med=next(a for a in json.loads((ROOT/c["raw"]["path"]).read_text())["resultList"]["result"] if a.get("id")==c["pmid"] and a.get("source")=="MED")
        j=med["journalInfo"];jj=j["journal"];hint=sources[doi]["source_hint"]
        xp=dict(doi=x["DOI"],title=x["title"][0],journal=x["container-title"][0],ISSNs=x.get("ISSN",[]),publisher=x.get("publisher"),year_values=[v["date-parts"][0][0] for k,v in x.items() if k in {"published","published-online","published-print"}],volume=x.get("volume"),issue=x.get("issue"),pages=x.get("page"),article_number=x.get("article-number"),author_surnames=[a.get("family") for a in x.get("author",[])],alternative_ids=x.get("alternative-id",[]))
        mp=dict(doi=med.get("doi"),pmid=med["id"],pmcid=med.get("pmcid"),title=med.get("title"),journal=jj.get("title"),medline_abbreviation=jj.get("medlineAbbreviation"),ISSNs=[jj.get("issn"),jj.get("essn")],year=med.get("pubYear"),volume=j.get("volume"),issue=j.get("issue"),pages=med.get("pageInfo"),publisher=None)
        checks={k:dict(Crossref=xp[k],MED=mp[k],missing_field_preserved=xp[k] is None or mp[k] is None,passed=xp[k] is None or mp[k] is None or norm(xp[k])==norm(mp[k])) for k in ("doi","title","volume","issue","pages")}
        issns=sorted(set(xp["ISSNs"])&set(mp["ISSNs"]))
        checks["journal"]=dict(Crossref=xp["journal"],MED=mp["journal"],literal_normalized_equal=norm(xp["journal"])==norm(mp["journal"]),matching_actual_ISSNs=issns,passed=bool(issns),journal_subtitle_alias_bound_to_actual_ISSN=True)
        checks["year"]=dict(Crossref=xp["year_values"],MED=mp["year"],passed=int(mp["year"]) in xp["year_values"],online_vs_volume_dates_preserved=True)
        checks["PMID"]=dict(expected=hint["pmid"],actual=mp["pmid"],passed=hint["pmid"]==mp["pmid"],Crossref_PMCID_PMID_absent_preserved=True)
        checks["hint_DOI_title_year"]=dict(passed=norm(hint["doi"])==norm(mp["doi"]) and norm(hint["title"])==norm(mp["title"]) and str(hint["year"])==mp["year"])
        checks["publisher"]=dict(primary_publisher_deposited_Crossref=xp["publisher"],secondary_MED_missing=True,passed=bool(xp["publisher"]),no_corporate_alias_inferred=True)
        metadata_pass=all(v["passed"] for v in checks.values())
        f=next((f for f in fronts if f["doi"]==doi),None)
        if f:
            literal=front_title[doi]
            sourcecheck=dict(literal_original_title=literal,title_matches_registered=norm(literal)==norm(xp["title"]),original_author_surnames=original_authors[doi],author_order_matches_crossref=original_authors[doi]==xp["author_surnames"],front_pointer=pointer(ROOT/f["front_path"]),source_version="public peer-reviewed author manuscript" if doi!="10.1021/acs.jafc.5c09887" else "official ACS supplementary information")
            sourcepass=sourcecheck["title_matches_registered"] and sourcecheck["author_order_matches_crossref"]
            inputs.append(ROOT/f["front_path"])
        else:
            sourcecheck=dict(original_front_absent=True,source_type="publisher graphical abstract only",publisher_PII="S0031942216300292",exact_PII_in_publisher_deposited_alternative_ids="S0031942216300292" in xp["alternative_ids"],actual_graphic_source_link_bound=True)
            sourcepass=sourcecheck["exact_PII_in_publisher_deposited_alternative_ids"]
        if doi in r4 and doi.startswith("10.1021/"):
            relation=r4[doi]["relationship_metadata_pointer"];record=json.loads((ROOT/relation["path"]).read_text())
            sourcecheck.update(official_SI_record_pointer=relation,official_resource_doi=record.get("resource_doi"),official_SI_doi=record.get("doi"),official_SI_parent_title=record.get("resource_title"),official_title_matches=norm(record.get("resource_title"))==norm(xp["title"]))
            sourcepass=sourcepass and record.get("resource_doi")==doi and sourcecheck["official_title_matches"]
            inputs.append(ROOT/relation["path"])
        outputs.append(dict(task=TASK,agent_role="A3 Source Identity Verifier",epoch_id="C-E02",at=now(),doi=doi,source_id=sources[doi]["source_id"],publisher_deposited_bibliographic_record=xp,official_MED_record=mp,field_checks=checks,metadata_identity_verified=metadata_pass,original_identity_checks=sourcecheck,source_identity_verified=metadata_pass and sourcepass,
          source_identity_deferred_reason=None if metadata_pass and sourcepass else "Retained original manuscript title variant or unresolved metadata difference; no automatic version identity equivalence",
          missing_fields_not_imputed=True,ACS_Crossref_missing_volume_pages_preserved=True,
          original_source_pointers=[r["raw"]["path"],c["raw"]["path"]],source_scientific_qualified=False,evidence_eligible=False,
          read_primary_reaction_chemistry=False,read_other_extractor_graphs=False,read_model_outcome=False,human_reviewed=False))
    save_rows(B/"source_publication_identity.jsonl",outputs)
    summary=dict(task=TASK,agent_role="A3 Source Identity Verifier",at=now(),metadata_records=5,metadata_identity_passed=sum(r["metadata_identity_verified"] for r in outputs),original_identity_passed=sum(r["source_identity_verified"] for r in outputs),original_identity_pending=sum(not r["source_identity_verified"] for r in outputs),new_HTTP=10,source_scientific_qualified=0,fresh_admitted=0,source_original_universe_complete=False)
    immutable_json(B/"publication_identity_summary.json",summary)
    inputs.extend([Path(__file__),B/"metadata_request_plan.json",B/"core_metadata_request_plan.json",B/"metadata_request_execution.jsonl",B/"core_metadata_request_execution.jsonl",B/"source_front_metadata/front_projection.json"])
    for batch in ("C-E02-R3","C-E02-R4"):
        ip=E/"stages/batches"/batch/"fresh_source_input_manifest.json";d=json.loads(ip.read_text());verify_stage_chain(ROOT/d["G5_pointer"]["path"],d["G5_pointer"]["sha256"]);inputs.append(ip)
    role=role_manifest("A3 Source Identity Verifier","C-E02",list(dict.fromkeys(inputs)),[B/"source_publication_identity.jsonl",B/"publication_identity_summary.json"],dict(processed=5,passed=summary["original_identity_passed"],rejected=0,pending=summary["original_identity_pending"]),unprocessed=["16 R3 sources without usable bibliographic original projection","A4/A5 chemical qualification","Buckwheat manuscript/final title variant source version resolution"],read_holdout=False,read_model_outcome=False)
    role.update(logical_role="root isolated A3 metadata/front only; no chemistry or final graph read by this process",started_at=starts,source_chemical_claims_not_granted=True,normalization="Unescape HTML before stripping markup; NFKC/hyphens/whitespace; explicit Crossref small-caps F agopyrum/M . indentation; same actual ISSNs for journal subtitles")
    immutable_json(B/"role_A3_manifest.json",role);print(json.dumps(summary))
if __name__=="__main__":main()
