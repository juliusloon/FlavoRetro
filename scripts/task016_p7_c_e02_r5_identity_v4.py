"""Correct A3 author-footnote tokenization using exact original author block."""
import json,re,subprocess
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
B=ROOT/"outputs/task016-p7/v1/C/E02/fresh/C-E02-R5-A3"
def main():
 prior=json.loads((B/"source_original_identity_verification.v3.json").read_text())
 cross=json.loads((ROOT/prior["raw_Crossref_pointer"]["path"]).read_text())["message"]
 pdf=ROOT/prior["raw_original_pointer"]["path"];assert sha_file(pdf)==prior["raw_original_pointer"]["sha256"]
 text=subprocess.run(["pdftotext","-f","2","-l","2","-layout",str(pdf),"-"],check=True,capture_output=True,text=True).stdout
 block=text.split("Authors:",1)[1].split("Authors’ Addresses:",1)[0].strip()
 footnotes=re.findall(r"[A-Za-z]+(\d+)",block)
 projection=" ".join(re.sub(r"\d+","",block).split())
 names=[" ".join(x.split()) for x in projection.split(",")]
 registered=[x["given"]+" "+x["family"] for x in cross["author"]]
 assert names==registered and footnotes==["1","1","2","1","1"]
 corrected=dict(prior);corrected.update(at=now(),PDF_complete_author_list=names,PDF_reported_author_names=names,PDF_unreported_author_surnames=[],PDF_author_page_1based=2,PDF_literal_author_block=block,PDF_affiliation_footnotes=footnotes,explicit_author_field_projection="Remove numeric affiliation footnotes only within explicitly labelled Authors block; collapse line breaks, preserve raw block and digits separately",prior_v3_result=pointer(B/"source_original_identity_verification.v3.json"),v3_missing_author_field_claim_corrected=True,reason_for_revision="Actual PDF page2 explicitly lists all5 authors in registered order. v2 word-boundary matcher rejected surnames attached to affiliation digits; v3 mistakenly called those4 fields absent. Preserve both errors; exact source block now verified. PDF DOI remains unreported in inspected cover/title pages, resolved through exact official repository DOI-to-file link.")
 corrected["checks"]=dict(prior["checks"],PDF_full_ordered_author_names_match_Crossref=True)
 immutable_json(B/"source_original_identity_verification.v4.json",corrected)
 immutable_json(B/"author_footnote_parser_correction.v4.json",dict(task=TASK,at=now(),old_v2_failure_pointer=pointer(B/"first_author_page_adapter_failure.v2.json"),old_v3_wrong_absence_claim_pointer=pointer(B/"source_original_identity_verification.v3.json"),actual_corrected_source_fields=4,complete_ordered_original_authors=names,source_original_identity_passed_remains=True,chemical_qualification_changed=False,source_originals_unchanged=True,reason="Numeric affiliation digits immediately follow surnames; word boundary requires nonword and therefore failed. Absence conclusion from that negative regex was wrong.",scope_changed=False,new_HTTP=0,new_MCTS=0))
 files=[Path(__file__),pdf,B/"source_original_identity_verification.v3.json",ROOT/prior["raw_Crossref_pointer"]["path"],ROOT/prior["raw_MED_pointer"]["path"],ROOT/prior["raw_repository_pointer"]["path"]]
 immutable_json(B/"role_A3_manifest.v4.json",dict(task=TASK,approval_type="agent_delegated",human_reviewed=False,agent_role="A3 publication identity correction; no chemistry authority",at=now(),input_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in files},output_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in [B/"source_original_identity_verification.v4.json",B/"author_footnote_parser_correction.v4.json"]},metadata_passed=1,original_passed=1,new_HTTP=0,new_MCTS=0,source_qualified_reaction=0))
 print(json.dumps(dict(original_ordered_authors=names,corrected_wrong_absence_fields=4,original_identity_passed=True,qualification=0)))
if __name__=="__main__":main()
