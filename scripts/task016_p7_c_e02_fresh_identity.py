"""Isolated source identity verifier for already G5-frozen C-E02-R1 originals."""
from __future__ import annotations
import html
import json
import re
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,role_manifest,verify_stage_chain
from scripts.task016_p7_c_e02_http import acquire,immutable_json,require_active
from scripts.task016_p7_c_e02_fresh import pointer,save_rows

B=ROOT/"outputs/task016-p7/v1/C/E02"
SOURCE=B/"stages/batches/C-E02-R1/fresh_source_input_manifest.json"
O=B/"fresh/C-E02-R1/A3_source_identity_v1"

def literal(node):
    return "".join(node.itertext()).strip() if node is not None else None

def norm(value):
    if value is None:return None
    value=html.unescape(re.sub("<[^>]+>","",str(value)))
    value=unicodedata.normalize("NFKC",value)
    value=value.translate(str.maketrans({"‐":"-","‑":"-","–":"-","−":"-","\u00ad":""}))
    return " ".join(value.split()).casefold().rstrip(".")

def main():
    inputs=json.loads(SOURCE.read_text())
    verify_stage_chain(ROOT/inputs["G5_pointer"]["path"],inputs["G5_pointer"]["sha256"])
    oldplan=B/"fresh/C-E02-R1/original_intake_plan.json"
    p=json.loads(oldplan.read_text())
    plan={k:p[k] for k in ("task","family","epoch_id","G4_pointer","scope_pointer","chemical_extraction_permitted","unknown_name_identity_fail_closed")}
    plan.update(batch_id="C-E02-R1-A3",registered_at=now(),
                input_G5_pointer=inputs["G5_pointer"],contains_final_graphs=False,
                files_sha256=dict(p["files_sha256"],**{str(SOURCE.relative_to(ROOT)):sha_file(SOURCE),
                      str(Path(__file__).relative_to(ROOT)):sha_file(Path(__file__))}),
                requests=[dict(pmcid=s["pmcid"],query="EXT_ID:"+str(s["source_hint"]["pmid"])+" AND SRC:MED",
                    url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(
                        dict(query="EXT_ID:"+str(s["source_hint"]["pmid"])+" AND SRC:MED",format="json",resultType="core",pageSize=10)))
                          for s in inputs["sources"]])
    pp=O/"metadata_request_plan.json"
    immutable_json(pp,plan)
    require_active(pp)
    output=[]
    raw=[]
    primarypointers=[]
    errors=[]
    for s,req in zip(inputs["sources"],plan["requests"]):
        if not s["xml_pointer"]:continue
        xp=ROOT/s["xml_pointer"]["path"]
        if sha_file(xp)!=s["xml_pointer"]["sha256"]:raise ValueError("primary raw drift")
        doc=ET.fromstring(xp.read_bytes())
        front=doc.find("./front")
        if front is None:raise ValueError("original lacks JATS front")
        am=front.find("./article-meta")
        jm=front.find("./journal-meta")
        ids={n.attrib.get("pub-id-type"):literal(n) for n in am.findall("./article-id")}
        pid=ids.get("pmcid") or ids.get("pmc")
        if pid and pid.isdigit():pid="PMC"+pid
        title=literal(am.find("./title-group/article-title"))
        journal=literal(jm.find("./journal-title-group/journal-title")) or literal(jm.find("./journal-title"))
        years=[literal(n) for n in am.findall("./pub-date/year")]
        fpage=literal(am.find("./fpage"));lpage=literal(am.find("./lpage"));eloc=literal(am.find("./elocation-id"))
        pages=eloc or ((fpage+"-"+lpage) if fpage and lpage else fpage)
        prim=dict(pmcid=pid,pmid=ids.get("pmid"),doi=ids.get("doi"),title=title,journal=journal,
                  year_values=years,volume=literal(am.find("./volume")),issue=literal(am.find("./issue")),
                  pages=pages,publisher=literal(jm.find("./publisher/publisher-name")),
                  author_surnames=[literal(n) for n in am.findall("./contrib-group/contrib/name/surname")],
                  publication_dates=[dict(attributes=dict(n.attrib),text=literal(n)) for n in am.findall("./pub-date")])
        reqraw=acquire(pp,req["url"],"metadata","A3 C-E02-R1 exact official publication metadata "+s["pmcid"],object_limit=8*1024**2)
        raw.append(reqraw)
        sec=None
        parse_error=None
        if reqraw["status"]=="available":
            try:
                matches=json.loads((ROOT/reqraw["path"]).read_text())["resultList"]["result"]
                sec=next((r for r in matches if str(r.get("id"))==str(s["source_hint"]["pmid"]) and r.get("source")=="MED"),None)
            except (ValueError,KeyError,UnicodeError) as exc:parse_error=type(exc).__name__+": "+str(exc)
        errors.extend([e for e in (reqraw["error"],parse_error) if e])
        second=None
        checks={}
        if sec:
            info=sec.get("journalInfo") or {}
            fulljournal=(info.get("journal") or {}).get("title")
            second=dict(pmcid=sec.get("pmcid"),pmid=sec.get("id"),doi=sec.get("doi"),title=sec.get("title"),
                        journal=fulljournal,year=sec.get("pubYear"),volume=info.get("volume"),issue=info.get("issue"),
                        pages=sec.get("pageInfo"),publisher=(info.get("journal") or {}).get("publisher"))
            for key in ("pmcid","pmid","doi","title","journal","volume","issue","pages"):
                a=prim[key];other=second[key]
                checks[key]=dict(primary=a,secondary=other,raw_equal=a==other,normalized_equal=norm(a)==norm(other),
                                 missing_field_preserved=a is None or other is None,
                                 passed=a is None or other is None or norm(a)==norm(other))
            y=second["year"]
            checks["year"]=dict(primary_year_values=years,secondary=y,passed=y is None or not years or str(y) in years,
                               online_and_collection_values_preserved=True)
            checks["publisher"]=dict(primary=prim["publisher"],secondary=second["publisher"],
                                     passed=prim["publisher"] is None or second["publisher"] is None or norm(prim["publisher"])==norm(second["publisher"]),
                                     missing_secondary_preserved=second["publisher"] is None,
                                     primary_PMC_authoritative_source=True,no_corporate_alias_inference=True)
        passed=bool(sec and prim["pmcid"]==s["pmcid"] and all(c["passed"] for c in checks.values()))
        r=dict(task=TASK,agent_role="A3 Source Identity Verifier",family="C",epoch_id="C-E02",batch_id="C-E02-R1",
               at=now(),pmcid=s["pmcid"],doi=prim["doi"],raw_JATS_publication_fields=prim,
               exact_EuropePMC_metadata_fields=second,field_checks=checks,source_identity_verified=passed,
               source_scientific_qualified=False,evidence_eligible=False,human_reviewed=False,
               source_evidence_pointers=[s["xml_pointer"],s["metadata_pointer"],pointer(ROOT/reqraw["path"])],
               normalization_scope="HTML entity/markup, NFKC, documented literal hyphen glyphs, soft-hyphen join, case/whitespace/terminal period; original literal values preserved",
               absent_fields_not_invented=True,source_chemical_content_read=False,read_model_outcome=False,errors=[e for e in (reqraw["error"],parse_error) if e])
        output.append(r)
        primarypointers.extend(ROOT/a["path"] for a in (s["xml_pointer"],s["metadata_pointer"]))
        print(json.dumps(dict(pmcid=s["pmcid"],identity_passed=passed,failed_fields=[k for k,c in checks.items() if not c["passed"]])),flush=True)
    save_rows(O/"source_publication_identity.jsonl",output)
    immutable_json(O/"metadata_request_execution.json",raw)
    summary=dict(task=TASK,agent_role="A3 Source Identity Verifier",created_at=now(),sources=len(inputs["sources"]),processed=len(output),
                 publication_identity_passed=sum(r["source_identity_verified"] for r in output),
                 publication_identity_pending=sum(not r["source_identity_verified"] for r in output),
                 source_scientific_qualified=0,source_reaction_graphs_extracted=0,no_missing_field_imputation=True,
                 primary_source_is_official_PMC=True,human_reviewed=False)
    immutable_json(O/"publication_identity_summary.json",summary)
    role=role_manifest("A3 Source Identity Verifier","C-E02",[SOURCE,pp]+primarypointers,
            [O/"source_publication_identity.jsonl",O/"metadata_request_execution.json",O/"publication_identity_summary.json"],
            dict(processed=len(output),passed=summary["publication_identity_passed"],rejected=0,pending=summary["publication_identity_pending"]),
            errors=errors,unprocessed=["Chemical claim qualification and A4/A5/A6 closure"],read_holdout=False,read_model_outcome=False)
    role.update(read_fresh_source_front_only=True,read_primary_reaction_chemistry=False)
    immutable_json(O/"role_A3_manifest.json",role)
if __name__=="__main__":main()
