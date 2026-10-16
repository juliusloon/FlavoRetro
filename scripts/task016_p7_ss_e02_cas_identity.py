"""Source CAS identity supplement, immutable raw-only v3 input, inherited budget."""
from pathlib import Path
import hashlib,json,urllib.parse
import scripts.task016_p7_ss_sources as io
from scripts.operate import write
BASE=io.ROOT/"outputs/task016-p7/v1/SS/E02_design"
SUP=BASE/"cas_identity_supplement_v1"
io.OUT=SUP
SUP.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    names=[("142451-65-8","Kaempferol-3-O-neohesperidoside","K3Neo","C27H30O15"),("28053-08-9","UDP-glucose","UDP-Glc","C15H22N2Na2O17P2")]
    plan=[]
    for cas,name,abbr,formula in names:
        base="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"+urllib.parse.quote(cas,safe="")
        plan.append(dict(source_id="PMC13084081",source_CAS_literal=cas,source_name_literal=name,source_abbreviation_literal=abbr,source_formula_literal=formula,source_location="complete SI Table6 physical page33",registered_at=io.now(),phase="design",epoch_id="SS-E02",approval_type="agent_delegated",reason="Explicit source CAS query requested by root; do not silently replace source with prior name lookup",property_url=base+"/property/Title,IUPACName,MolecularFormula,InChI,InChIKey,IsomericSMILES/JSON",synonym_url=base+"/synonyms/JSON"))
    if (SUP/"CAS_identity_query_plan.json").exists():raise RuntimeError("immutable plan exists")
    io.save("CAS_identity_query_plan.json",plan)
    before=[r for p in (io.ROOT/"outputs/task016-p7/v1/SS").rglob("http_ledger.jsonl") if "superseded" not in p.parts for r in io.rows(p)]
    io.save("inherited_axis_budget_before.json",dict(registered_at=io.now(),http_used=len(before),bytes_used=sum(x["bytes"] for x in before),http_limit=2500,bytes_limit=2*1024**3,reset=False))
    records=[]
    for p in plan:
        rec={k:v for k,v in p.items() if not k.endswith("_url")}
        rec["properties"]=io.request(p["property_url"],"structure_database",p["reason"],phase="design",epoch_id="SS-E02",route="official_source_CAS_identity")
        rec["synonyms"]=io.request(p["synonym_url"],"metadata",p["reason"],phase="design",epoch_id="SS-E02",route="official_source_CAS_identity")
        rec.update(contains_A4_final_graphs=False,contains_A5_final_graphs=False,evidence_eligible=False)
        records.append(rec);io.save("CAS_identity_intake.json",records)
        print(p["source_CAS_literal"],rec["properties"]["status_code"],rec["synonyms"]["status_code"],flush=True)
    old=BASE/"common_source_raw_only_input_v2.json";v3=json.loads(old.read_text())
    v3["supersedes_common_input"]={"path":str(old.relative_to(io.ROOT)),"sha256":sha(old),"reason":"New actual source-CAS raw identity supplement acquired after v2 A4/A5 fixed; original extractions retained. Neither CAS nor source formula silently changed."}
    v3["frozen_at"]=io.now();v3["version"]="v3 source-CAS raw-only supplement"
    v3["source_CAS_official_database_raw_identity_candidates"]=records
    for x in records:
        for r in (x["properties"],x["synonyms"]):v3["raw_input_files_sha256"][r["path"]]=r["sha256"]
    v3["contains_A4_final_structures"]=False;v3["contains_A5_final_structures"]=False
    out=BASE/"common_source_raw_only_input_v3.json"
    if out.exists():raise RuntimeError("immutable common v3 exists")
    write(io.TASK,str(out.relative_to(io.ROOT)),json.dumps(v3,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    io.save("role_A2_source_CAS_raw_only_manifest.json",dict(agent_role="A2 Source Scout",task_id=io.TASK,epoch_id="SS-E02",fixed_at=io.now(),input_files_sha256={str(old.relative_to(io.ROOT)):sha(old)},output_files_sha256={str(out.relative_to(io.ROOT)):sha(out),**{str(p.relative_to(io.ROOT)):sha(p) for p in SUP.glob("*.json")}},read_other_extractor_output=False,read_model_outcomes=False,read_future_fresh=False,contains_A4_final_structures=False,contains_A5_final_structures=False,evidence_eligible=False,approval_type="agent_delegated"))
    print("common_v3",str(out.relative_to(io.ROOT)),sha(out),len(v3["raw_input_files_sha256"]))
if __name__=="__main__":main()
