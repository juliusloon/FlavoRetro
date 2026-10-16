"""Independent bounded TASK-016-P7 v31 source custody/OOXML/governance audit.

Not an independent chemical validation, not a fresh panel or reaction admission.
"""
import hashlib
import json
import posixpath
import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.operate import ROOT, write
from scripts.task016_p7_c_e02_http import physical_attempts

TASK = "TASK-016-P7"
B = Path("outputs/task016-p7/v1")
D = B / "SS/E02/fresh/SS-E02-R56-Laportea-tabular-science-v1"
R55 = B / "SS/E02/fresh/SS-E02-R55-Laportea-tabular-SI-custody-v1"
OUT = B / "verification-v31-ACS-tabular-original/independent_A11_raw_OOXML_stage_audit.json"
MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
checks = []


def load(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def check(name, test):
    passed = bool(test)
    checks.append({"check": name, "passed": passed})
    if not passed:
        raise AssertionError(name)


def main():
    contract = load(D / "pre_science_exposure_contract.json")
    verify = load(D / "A6/source_scientific_assessment.json")
    raw = Path(contract["raw_XLSX"]["path"])
    check("raw_original_exact_contract_sha", sha(raw) == contract["raw_XLSX"]["sha256"])
    check("R55_raw_exact_frozen_MD5", hashlib.md5((ROOT/raw).read_bytes()).hexdigest() == load(R55/"raw_custody_summary.json")["integrity"]["official_MD5"])
    check("SS_G4_scope_exact_frozen_SHA", sha(B/"SS/E02/stages/G4_SCOPE_FREEZE.json") == contract["input_manifest_sha"][str(B/"SS/E02/stages/G4_SCOPE_FREEZE.json")])
    check("SS_scope_manifest_exact_frozen_SHA", sha(B/"SS/E02/scope_manifest.json") == contract["input_manifest_sha"][str(B/"SS/E02/scope_manifest.json")])
    a = load(D/"A4/all_original_stored_cells.json")
    b = load(D/"A5/all_original_stored_cells.json")
    check("dual_distinct_role_outputs_exact_cell_equality", a["worksheets"] == b["worksheets"])
    check("different_reader_id", load(D/"A4/role_manifest.json")["reader_id"] != load(D/"A5/role_manifest.json")["reader_id"])
    for rel, digest in contract["input_manifest_sha"].items():
        check("frozen_input_"+hashlib.sha256(rel.encode()).hexdigest()[:10], sha(Path(rel)) == digest)

    with zipfile.ZipFile(ROOT/raw) as z:
        names=set(z.namelist())
        check("valid_xlsx_main_parts", {"xl/workbook.xml","xl/_rels/workbook.xml.rels"} <= names)
        check("bounded_archive_size", sum(t.file_size for t in z.infolist()) <= 32*1024*1024)
        nsroot=ET.fromstring(z.read("xl/workbook.xml"))
        relroot=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rels={rel.attrib["Id"]:rel.attrib["Target"] for rel in relroot}
        sheets=nsroot.find(MAIN+"sheets")
        sheet_data=[]
        for item in sheets:
            target=rels[item.attrib[RID+"id"]]
            path=target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/"+target)
            check("worksheet_zip_entry_"+item.attrib["name"], path in names and ".." not in path.split("/"))
            xml=ET.fromstring(z.read(path))
            dims=xml.find(MAIN+"dimension")
            cells=list(xml.iter(MAIN+"c"))
            sheet_data.append((item.attrib["name"], dims.attrib.get("ref") if dims is not None else None, cells))
        check("fourteen_original_worksheets", len(sheet_data)==14)
        check("original_sheet_titles_match_both_parsers", [s[0] for s in sheet_data] == [s["name"] for s in a["worksheets"]])
        check("original_sheet_dimensions_match_dual", all(dim == a["worksheets"][i]["dimension"] for i,(_,dim,_) in enumerate(sheet_data)))
        check("raw_cell_count_equals_4994", sum(len(cells) for _,_,cells in sheet_data)==4994)
        check("raw_cell_counts_equal_A4_A5", all(len(cells)==len(a["worksheets"][i]["cells"]) for i,(_,_,cells) in enumerate(sheet_data)))
        zeros=blanks=formulas=0
        for i,(_,_,cells) in enumerate(sheet_data):
            byref={c.attrib["r"]:c for c in cells}
            check("cell_ref_set_"+str(i), set(byref)=={x["reference"] for x in a["worksheets"][i]["cells"]})
            for c in cells:
                f=c.find(MAIN+"f");v=c.find(MAIN+"v");raw_value=None if v is None else v.text
                formulas+=f is not None
                blanks+=raw_value is None and c.find(MAIN+"is") is None
                if c.attrib.get("t") not in ("s","str","inlineStr","b","e") and raw_value is not None:
                    try:
                        zeros+=Decimal(raw_value)==0
                    except InvalidOperation:
                        pass
        check("actual_43_numeric_zeros_preserved",zeros==43)
        check("actual_269_explicit_blank_cells_preserved",blanks==269)
        check("actual_15_formula_cells_preserved",formulas==15)
        check("R56_A6_zero_blank_formula_agreement", (zeros,blanks,formulas)==tuple(load(D/"A6/zero_blank_and_external_formula_preservation.json")[k] for k in ("numeric_zero_count","explicit_blank_count","formula_count")))

    annotations=(ROOT/D/"A6/all523_metabolite_annotation_rows.jsonl").read_text().splitlines()
    check("all_523_annotation_rows_preserved",len(annotations)==523)
    check("all_annotation_rows_source_numbers_unique",len(set(json.loads(x)["source_row"] for x in annotations))==523)
    check("R56_full_14_sheet_disposition",load(D/"A6/all14_worksheet_evidence_dispositions.json")["processed_worksheets"]==14)
    for ev in verify["evidence"]:
        check("A6_evidence_"+Path(ev["path"]).name,sha(Path(ev["path"]))==ev["sha256"])
    check("A6_no_false_reaction_admission",verify["chemical_qualification"]=="deferred" and verify["complete_acceptor_product_donor_graphs"]==0 and verify["fresh_admitted"]==0)
    check("A6_no_source_scope_overclaim",verify["whole_source_scientific_qualification_complete"] is False and verify["frozen_SS_O2_enzymatic_reaction_established"] is False)
    check("raw_original_distinct_from_metadata_annotation",verify["source_specific_literal_contexts"][0]["evidence_kind"]=="metabolomics annotation, not enzymatic formation reaction")
    for r in ("R54-Laportea-tabular-SI-custody-v1","R55-Laportea-tabular-SI-custody-v1","R57-Laportea-tabular-SI-custody-v1","R58-declared-primary-PDF-custody-v1"):
        short={"R54":3,"R55":2,"R57":4,"R58":2}[r.split("-")[0]]
        path=B/"SS/E02/fresh"/("SS-E02-"+r)/"http_ledger.jsonl"
        check("actual_intake_HTTP_"+r,len((ROOT/path).read_text().splitlines())==short)
    r58=load(B/"SS/E02/fresh/SS-E02-R58-declared-primary-PDF-custody-v1/raw_custody_summary.json")
    check("publisher_403_protected_no_bypass",r58["HTTP_statuses"]==[403,403] and r58["valid_PDF"]==0)
    ledger=physical_attempts()
    check("physical_total_includes_all_new_transactions",len(ledger)>=1206)
    summary={
        "task":TASK, "stage":"progress-v31_source_specific_original_review",
        "purpose":"Independent bounded audit of new original tabular ACS SI acquired after progress-v30",
        "approval_type":"agent_delegated", "human_reviewed":False,
        "checks":checks, "passed":len(checks),"failed":0,
        "official_original":{"path":str(raw),"sha256":sha(raw),"bytes":(ROOT/raw).stat().st_size},
        "source_DOI":"10.1021/acs.jafc.4c00488",
        "source_SI_DOI":"10.1021/acs.jafc.4c00488.s001",
        "recovered_originals":1,"worksheets":14,"stored_cells":4994,
        "annotations_not_reactions":523,"numeric_zeros":43,"explicit_blanks":269,"formula_cells":15,
        "R54_R55_R57_R58_HTTP":11,"physical_HTTP_now":len(ledger),
        "source_scientific_qualification":"deferred",
        "complete_reaction_graph_admissions":0,"fresh_C":0,"fresh_SS":0,"scientific_ABE_cells":0,
        "source_saturation":False,"Roadmap_P2_Completed":False,
        "limitation":"A11 raw source and OOXML verification; not original main-body enzyme mechanism, full chemical structure/identity, independent chemical validation, or new fresh panel."
    }
    write(TASK,str(OUT),json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print(json.dumps({"status":"pass","checks":len(checks),"original_sha":sha(raw),"physical_HTTP":len(ledger),"fresh_C":0,"fresh_SS":0},sort_keys=True))


if __name__=="__main__":
    main()
