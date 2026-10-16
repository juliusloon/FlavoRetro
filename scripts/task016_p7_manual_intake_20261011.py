"""TASK-016-P7 manual owner-provided source custody: metadata-only, non-scientific admission."""
from __future__ import annotations
import hashlib, json, os, re, shutil, sys, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from operate import write, event

TASK = "TASK-016-P7"
ORIGIN = ROOT / "temp/manual_grabbed"
DEST = ROOT / "data/raw/task016-p7/manual_grabbed_20261011"
OUT = ROOT / "outputs/task016-p7/v1/manual_grabbed_intake_20261011"
DOCS = {
 "01":("10.1111/tpj.70932","C","main_and_support"),
 "02":("10.1021/acs.jafc.5c06227","SS","main"),
 "03":("10.1021/acs.jafc.4c03824","SS","main"),
 "04":("10.1021/acs.jafc.4c00488","SS","main"),
 "05":("10.1111/tpj.16898","SS","main"),
 "06":("10.1039/c5ob01926e","C","main_and_support"),
 "07":("10.1039/c0ob00011f","C","main_and_support"),
 "08":("10.1039/c4cc00536h","C","main_and_support"),
 "09":("10.1002/bit.26491","C","main"),
 "10":("10.1002/cbic.70486","SS","support_only"),
 "11":("PMC7720146","C","historical_main"),
 "12":("PMC2709393","C","historical_main"),
 "13":("10.1016/0003-9861(75)90485-3","unknown","unavailable_owner"),
 "14":("10.1515/znc-1979-9-1014","unknown","unavailable_owner"),
 "15":("10.1515/znc-1984-0609","unknown","unavailable_owner"),
 "16":("10.1515/znc-1997-3-403","unknown","unavailable_owner"),
}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def emit(name,obj):
 rel=f"outputs/task016-p7/v1/manual_grabbed_intake_20261011/{name}"
 dst=ROOT/rel
 if dst.exists():raise RuntimeError(f"immutable destination already exists: {dst}")
 write(TASK,rel,json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
 return {"path":rel,"sha256":sha(dst)}
def classify(path):
 stem=path.name.lower()
 if path.suffix.lower()==".pdf":
  return "supporting_pdf" if ("si-" in stem or "suppl" in stem or "suppdata" in stem) else "main_article_pdf"
 if path.suffix.lower() in {".xlsx",".xls",".doc",".docx",".tif",".tiff"}:return "supplementary_other"
 return "unclassified"
def main():
 if not ORIGIN.is_dir():raise FileNotFoundError(ORIGIN)
 if OUT.exists() or DEST.exists():raise RuntimeError("intake namespace already exists; preserve and version instead")
 paths=sorted(p for p in ORIGIN.rglob("*") if p.is_file() and p.name not in {".DS_Store"} and not p.name.startswith("._"))
 rows=[]
 for i,p in enumerate(paths):
  rel=p.relative_to(ORIGIN)
  m=re.match(r"^(\d{2})",rel.parts[0])
  if not m or m.group(1) not in DOCS:raise RuntimeError(f"unknown slot: {rel}")
  no=m.group(1); doi,family,expected=DOCS[no]
  file_sha=sha(p); dst=DEST/rel
  dst.parent.mkdir(parents=True,exist_ok=True)
  # Preserve owner originals, create private checksum-verified immutable copies.
  shutil.copyfile(p,dst)
  if sha(dst)!=file_sha: raise RuntimeError(f"copy checksum drift: {rel}")
  dst.chmod(0o444)
  role=classify(p)
  row={"number":no,"requested_identifier":doi,"family_triage_hint_only":family,
       "role":role,"source_original":str(p.relative_to(ROOT)),
       "local_custody":str(dst.relative_to(ROOT)),"sha256":file_sha,
       "bytes":p.stat().st_size,"permission":"0444","redistribute":False,
       "source_license":"inherited_not_cleared_for_redistribution",
       "scientific_admission":"not_assessed","fresh_admission":False,
       "historical_alias_and_graph_closure":"not_verified",
       "pre_G5_read_disclosure":"assistant inspected limited first-page excerpts before this intake registration; not retrospectively cured"}
  rows.append(row)
  event(TASK,"copy_verified",source=row["source_original"],destination=row["local_custody"],sha256=file_sha,bytes=row["bytes"],purpose="owner_manual_primary_and_support_intake",index=i)
 for no,(_,_,kind) in DOCS.items():
  if int(no)<=12 and not any(r["number"]==no for r in rows):raise RuntimeError(f"missing expected numbered slot: {no}")
 byno={}
 for no,(id_,family,kind) in DOCS.items():
  entries=[r for r in rows if r["number"]==no]
  byno[no]={"identifier":id_,"family_hint":family,"requested_kind":kind,
    "main_pdf_files":sum(r["role"]=="main_article_pdf" for r in entries),
    "support_pdf_files":sum(r["role"]=="supporting_pdf" for r in entries),
    "other_support_files":sum(r["role"]=="supplementary_other" for r in entries),
    "manual_access":"unavailable_owner_reported_no_access" if no in {"13","14","15","16"} else "local_present",
    "source_identity":"pending_pdf_imprint_crosscheck" if entries else "access_unavailable",
    "scope_reaction_evidence":"not_admitted",
    "fresh_qualified":False}
 for no in [f"{i:02d}" for i in range(1,10)]+["11","12"]:
  if byno[no]["main_pdf_files"]<1:raise RuntimeError(f"no main PDF in {no}")
 if byno["10"]["support_pdf_files"]<1:raise RuntimeError("missing 10 SI")
 g4={}
 for family in ("C","SS"):
  p=ROOT/f"outputs/task016-p7/v1/{family}/E02/stages/G4_SCOPE_FREEZE.json"
  g4[family]={"path":str(p.relative_to(ROOT)),"sha256":sha(p)}
 at=datetime.datetime.now(datetime.timezone.utc).isoformat()
 base={"task":TASK,"at":at,"approval":"owner_current_turn_provided_manual_sources_to_advance_existing_P7",
       "agent_role":"A0_local_source_custodian","input_root":"temp/manual_grabbed",
       "source_inputs_already_in_user_workspace":True,
       "read_holdout":False,"read_model_outcome":False,
       "fresh_evaluation_role":"excluded_pending_prospective_exposure_and_complete_identity_qualification",
       "prior_limited_pdf_front_page_reads":"already_occurred_before_intake; no retroactive G5 claimed",
       "latest_scientific_ABE_cells":0,
       "historical_ledger_and_28_exposure_names":"must_be_checked_before_any_future_holdout",
       "G4_current_sha":g4,"source_files":rows,"slot_summary":byno,
       "copied_files":len(rows),"copied_bytes":sum(r["bytes"] for r in rows),
       "unavailable_source_numbers":["13","14","15","16"],
       "missing_preexisting_SI":[],
       "altered_scientific_assets":False}
 receipt=emit("custody_manifest.json",base)
 verify={"task":TASK,"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "custody_manifest":receipt,"source_count":len(rows),
         "complete_sha_matches":all(sha(ROOT/r["local_custody"])==r["sha256"] for r in rows),
         "originals_unchanged":all(sha(ROOT/r["source_original"])==r["sha256"] for r in rows),
         "main_pdf_available_numbers":[n for n,v in byno.items() if v["main_pdf_files"]],
         "support_only_numbers":[n for n,v in byno.items() if v["support_pdf_files"] and not v["main_pdf_files"]],
         "unavailable_numbers":["13","14","15","16"],
         "fresh_admitted":0,"G7_panel_frozen":False,"scientific_ABE_cells":0}
 emit("verification.json",verify)
 print(json.dumps({"files":len(rows),"bytes":base["copied_bytes"],"main_numbers":verify["main_pdf_available_numbers"],"support_only":verify["support_only_numbers"],"unavailable":verify["unavailable_numbers"],"verified":verify["complete_sha_matches"],"manifest":receipt["path"]},ensure_ascii=False))
if __name__=="__main__":main()
