"""Append source-supported bibliographic rendering/ISSN resolution; retain v1."""
import copy,json,re,html,unicodedata,xml.etree.ElementTree as ET
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,role_manifest,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
from scripts.task016_p7_c_e02_fresh import rows,save_rows,pointer
O=ROOT/"outputs/task016-p7/v1/C/E02/fresh/C-E02-R1/A3_source_identity_v1"
def title_norm(value):
    value=html.unescape(html.unescape(value))
    value=re.sub("<[^>]+>","",value)
    value=unicodedata.normalize("NFKC",value)
    value=value.translate(str.maketrans({"′":"'","’":"'","‐":"-","‑":"-","–":"-","−":"-","\u00ad":""}))
    return " ".join(value.split()).casefold().rstrip(".")
def issn(value):return re.sub(r"[^0-9X]","",str(value).upper())
def main():
    path=O/"source_publication_identity.jsonl"
    original=rows(path);output=[];changes=[];raws=[]
    for before in original:
        after=copy.deepcopy(before)
        for field,check in after["field_checks"].items():
            if check["passed"]:continue
            if field=="title" and title_norm(check["primary"])==title_norm(check["secondary"]):
                check.update(passed=True,normalized_equal_after_explicit_rendering_resolution=True,
                    resolution="Decode encoded HTML before stripping tags; Unicode prime/apostrophe glyph alias; source literal preserved")
                changes.append(dict(pmcid=before["pmcid"],field=field,original=before["field_checks"][field],resolution=check))
            elif field=="journal":
                xp=ROOT/before["source_evidence_pointers"][0]["path"]
                cp=ROOT/before["source_evidence_pointers"][2]["path"]
                doc=ET.fromstring(xp.read_bytes())
                primary=sorted({issn(n.text) for n in doc.findall("./front/journal-meta/issn") if n.text})
                data=json.loads(cp.read_text())
                core=next(r for r in data["resultList"]["result"] if r.get("pmcid")==before["pmcid"])
                journal=core["journalInfo"]["journal"]
                secondary=sorted({issn(journal[k]) for k in ("issn","essn") if journal.get(k)})
                overlap=sorted(set(primary)&set(secondary))
                if overlap:
                    check.update(passed=True,literal_journal_difference_retained=True,
                       primary_ISSNs=primary,secondary_ISSNs=secondary,actual_same_ISSNs=overlap,
                       resolution="Same source-linked ISSN establishes geographic disambiguation subtitle alias; not publisher/corporate equivalence")
                    changes.append(dict(pmcid=before["pmcid"],field=field,original=before["field_checks"][field],resolution=check))
        after.update(source_identity_verified=all(c["passed"] for c in after["field_checks"].values()),
                     supersedes_for_bibliographic_rendering_only=pointer(path),
                     resolution_at=now(),raw_values_unchanged=True,
                     source_scientific_qualified=False,evidence_eligible=False)
        output.append(after)
        raws.extend(ROOT/p["path"] for p in before["source_evidence_pointers"])
    p2=O/"source_publication_identity.v2.jsonl"
    save_rows(p2,output)
    correction=dict(task=TASK,agent_role="A3 Source Identity Verifier",created_at=now(),original_pointer=pointer(path),
       corrected_fields=changes,original_4_failed_identity_records_preserved=True,no_new_HTTP=0,no_chemical_extraction=True,
       normalization_change="Explicit bibliographic HTML-order fix and literal prime glyph handling; journal aliases require actual same ISSNs",
       processed=len(output),passed=sum(r["source_identity_verified"] for r in output),
       pending=sum(not r["source_identity_verified"] for r in output),source_scientific_qualified=0,
       human_reviewed=False,read_model_outcome=False)
    immutable_json(O/"bibliographic_resolution.v2.json",correction)
    role=role_manifest("A3 Source Identity Verifier","C-E02",[path,Path(__file__)]+list(dict.fromkeys(raws)),
          [p2,O/"bibliographic_resolution.v2.json"],
          dict(processed=len(output),passed=correction["passed"],rejected=0,pending=correction["pending"]),
          unprocessed=["Reaction science and A4/A5/A6 closure"],read_holdout=False,read_model_outcome=False)
    role.update(read_fresh_source_front_only=True,read_primary_reaction_chemistry=False)
    immutable_json(O/"role_A3_manifest.v2.json",role)
    print(json.dumps(dict(identities=len(output),passed=correction["passed"],pending=correction["pending"],fields_resolved=len(changes),source_qualified=0)))
if __name__=="__main__":main()
