"""A3 independent identity check of three SS raw originals; no chemical qualification."""
import json,re,unicodedata,subprocess,sys
from pathlib import Path
import xml.etree.ElementTree as ET
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,verify_hashes,role_manifest
from scripts.task016_p7_c_e02_http import immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
B=ROOT/"outputs/task016-p7/v1/SS/E02_design/new_source_discovery_v1";O=ROOT/"outputs/task016-p7/v1/SS/E02_design/new_source_A3_identity_v2"
def txt(e):return "".join(e.itertext()).strip() if e is not None else None
def n(v):return re.sub(r"\s+","",unicodedata.normalize("NFKC",re.sub(r"<[^>]+>","",v or "")).casefold()).rstrip(".")
def main():
    ip=B/"common_raw_only_source_input_v1.json";d=json.loads(ip.read_text());verify_hashes(d["raw_input_files_sha256"])
    result=[];inputs=[ip,Path(__file__),B/"role_A2_raw_only_source_discovery_manifest.json"]+[ROOT/p for p in d["raw_input_files_sha256"]];out=[]
    for s in d["sources"]:
        if not s["valid_fulltext_originals"]:continue
        xp=ROOT/next(x for x in s["valid_fulltext_originals"] if x.endswith(".xml"));pdf=ROOT/next(x for x in s["valid_fulltext_originals"] if x.endswith(".original_pdf"));a=ET.fromstring(xp.read_bytes());fm=a.find(".//front/article-meta");jm=a.find(".//front/journal-meta")
        identifiers={e.get("pub-id-type"):txt(e) for e in fm.findall("article-id")};title=txt(fm.find("title-group/article-title"));ja=txt(jm.find(".//journal-title"));jissn=[txt(x) for x in jm.findall("issn")];pub=txt(jm.find("publisher/publisher-name"))
        authors=[]
        for c in [c for g in fm.findall("contrib-group") if g.get("content-type") != "editor" for c in g.findall("contrib")]:
            if c.get("contrib-type") not in [None,"author"]:continue
            z=c.find("name")
            if z is not None:authors.append(dict(given=txt(z.find("given-names")),family=txt(z.find("surname"))))
        records=[]
        for r in s["raw_inputs"]:
            if r["HTTP_status"]!=200:continue
            try:data=json.loads((ROOT/r["path"]).read_text())
            except Exception:continue
            for x in data.get("resultList",{}).get("result",[]):
                if str(x.get("pmid") or x.get("id"))==s["pmid"]:records.append((x,r))
        assert records,"Official MED source metadata missing"
        m,mr=records[0];medauthors=[dict(given=x.get("firstName"),family=x.get("lastName"),initials=x.get("initials")) for x in m["authorList"]["author"]]
        assert len(authors)==len(medauthors)>0
        name_checks=[]
        for x,y in zip(authors,medauthors):
            family=n(x["family"])==n(y["family"]);given=n(x["given"])==n(y["given"])
            assert family and given,(s["source_id"],x,y)
            name_checks.append(dict(JATS=x,MED=y,family_equal=True,given_equal=True))
        ji=m["journalInfo"];mj=ji["journal"];same_issn=bool(set(jissn)&{mj.get("issn"),mj.get("essn")})
        journal_literal_equal=n(ja)==n(mj["title"])
        assert journal_literal_equal or (same_issn and ja=="Molecules" and mj["title"]=="Molecules (Basel, Switzerland)")
        volume=txt(fm.find("volume"));issue=txt(fm.find("issue"));f=txt(fm.find("fpage"));last=txt(fm.find("lpage"));eloc=txt(fm.find("elocation-id"));pages=eloc or (f+"-"+last if f and last else f)
        years=[txt(x.find("year")) for x in fm.findall("pub-date")];dates=[dict(attributes=x.attrib,year=txt(x.find("year")),month=txt(x.find("month")),day=txt(x.find("day"))) for x in fm.findall("pub-date")]
        checks=dict(doi=identifiers.get("doi","").lower()==s["doi"]==m["doi"].lower(),PMID=identifiers.get("pmid")==s["pmid"]==m["pmid"],PMCID=identifiers.get("pmcid")==s["pmcid"]==m["pmcid"],title=n(title)==n(m["title"]),year=str(m["pubYear"]) in years,volume=volume==ji["volume"],issue=True if issue is None else issue==ji["issue"],pages_or_article_number=pages==m["pageInfo"],authors=True,journal=True)
        assert all(checks.values()),(s["source_id"],checks)
        command=["python3","-B","scripts/operate.py",TASK,"pdftotext","-f","1","-l","2","-layout",str(pdf),"-"]
        cp=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False);assert cp.returncode==0,cp.stderr.decode(errors="replace")
        header=cp.stdout.decode("utf-8");hp=O/(s["source_id"]+"_PDF_first2_pages_identity_text.txt");assert not hp.exists();write(TASK,str(hp.relative_to(ROOT)),header);out.append(hp)
        pdfchecks=dict(title_exact_after_explicit_typographic_projection=n(title) in n(header),doi_exact=s["doi"].casefold() in header.casefold(),magic_PDF=pdf.read_bytes().startswith(b"%PDF"))
        assert all(pdfchecks.values()),(s["source_id"],pdfchecks)
        row=dict(task=TASK,role="A3 root publication identity",source_id=s["source_id"],doi=s["doi"],JATS_pointer=pointer(xp),PDF_pointer=pointer(pdf),MED_pointer={k:mr[k] for k in ["path","sha256"]},JATS_identifiers=identifiers,metadata_title_literals=dict(JATS=title,MED=m["title"]),ordered_author_checks=name_checks,journal_literals=dict(JATS=ja,MED=mj["title"],same_ISSN=same_issn),JATS_publisher=pub,publisher_comparison="Official PMC original front + official MED; no missing MED publisher invented",bibliographic_literals=dict(JATS_volume=volume,MED_volume=ji["volume"],JATS_issue=issue,MED_issue=ji.get("issue"),JATS_pages=pages,MED_pages=m["pageInfo"],JATS_pubdates=dates,MED_dateOfPublication=ji["dateOfPublication"],MED_firstPublicationDate=m.get("firstPublicationDate"),MED_electronicPublicationDate=m.get("electronicPublicationDate")),checks=checks,PDF_checks=pdfchecks,PDF_identity_text_pointer=pointer(hp),PDF_author_order_not_separately_adjudicated=True,unreported_original_issue_not_filled=issue is None,all_raw_date_representations_retained=True,source_original_identity_verified=True,source_chemical_qualification=False,human_reviewed=False)
        result.append(row)
    assert len(result)==3
    p=O/"three_original_publication_identity_checks.json";immutable_json(p,result);out.append(p)
    summary=O/"A3_identity_summary.json";immutable_json(summary,dict(task=TASK,at=now(),role="A3 independent publication identity",input_manifest=pointer(ip),processed_original_sources=3,metadata_identities_passed=3,XML_original_identities_passed=3,PDF_title_DOI_identities_passed=3,source_original_versions_checked=6,remaining_sources_without_complete_primary_original_identity=9,whole_source_universe=12,full_assay_graph_or_source_qualification_granted=0,human_reviewed=False,raw_date_qualifiers_not_collapsed=True,missing_issue_and_MED_publisher_not_invented=True,new_HTTP=0,new_MCTS=0));out.append(summary)
    role=role_manifest("A3 independent publication identity","SS-E02",inputs,out,dict(processed=12,passed=3,rejected=0,pending=9),read_holdout=False,read_model_outcome=False,unprocessed=["9 source-associated entries without complete primary originals","Independent A4/A5 chemical and specific assay-product evidence"])
    role.update(root_authored=True,independent_chemical_validation=False,new_HTTP=0,new_MCTS=0)
    rp=O/"role_A3_manifest.json";immutable_json(rp,role)
    print(json.dumps(dict(summary=pointer(summary),role=pointer(rp),source_identity_passed=3,chemical_qualification=0)))
if __name__=="__main__":main()
