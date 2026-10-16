"""Bounded documentary PDF screen. NOT G6 chemical/graph admission and NOT fresh holdout."""
from __future__ import annotations
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from operate import write,event
TASK="TASK-016-P7";DIR="outputs/task016-p7/v1/manual_grabbed_intake_20261011"
M=ROOT/DIR/"custody_manifest.json"
# Positive anchors only: source scope classification is explicitly limited to the cited passages.
# Report a paragraph's reported pathway, never assert the whole paper contains no other relevant route.
CASES={
 "01":("C","C_GWAS_indirect_biosynthetic_context","C-glycosylation",
       "Mungbean isovitexin genomic association and pathway discussion; no direct C6 single-step admitted from this screen."),
 "02":("SS","reported_flavonol_aglycone_O3_outside_SS_O2","catalyzes 3-O-glycosylation of quercetin and kaempferol",
       "Reported enzyme converts aglycone flavonols at O3; not the frozen SS sugar-residue O2 step."),
 "03":("SS","rutin_multisite_requires_site_product_graph_review","glucosylation of rutin at multiple sites",
       "Rutin substrate and K3R at 7-OH are reported; must resolve each product site from figures/standards before ruling SS O2 in or out."),
 "04":("SS","reported_aglycone_glycosylation_outside_SS_O2","glycosylation of flavonol aglycones",
       "Reported LbUGTs act on flavonol aglycones; 523 metabolite annotations alone are not independent O2 reaction records."),
 "05":("SS","reported_flavonol_aglycone_O3_outside_SS_O2","flavonol 3-O-galactosyltransferase",
       "Reported apple F3GT enzymes act on flavonol 3-OH with sugar donors; not established sugar-residue O2 reglycosylation."),
 "06":("C","precursor_hydroxynaringenin_then_dehydration","C-glucosylation of 2-hydroxynaringenin",
       "First bond formation is to a 2-hydroxyflavanone precursor followed by later steps; endpoint di-C-flavone is not a direct frozen flavone-C6 enzyme reaction."),
 "07":("C","organic_multistep_synthesis_not_frozen_direct_C6_enzyme","Sc(OTf)3",
       "Chemical multistep 6,8-di-C-glycosylflavone synthesis; not evidence of direct frozen C6 glycosyltransferase action."),
 "08":("C","dihydrochalcone_phloretin_C3prime_outside_C6","phloretin",
       "O-to-C rearrangement on dihydrochalcone phloretin toward nothofagin, not direct flavone C6."),
 "09":("C","dihydrochalcone_phloretin_C3prime_outside_C6","nothofagin",
       "Nothofagin is phloretin 3'-C glucoside and process example; not direct flavone C6."),
 "10":("SS","SI_only_main_context_already_project_reported","UGT707B2",
       "Figures/MS spectra supplement only; project reportedly already has main HTML and figures, but linking is not verified here."),
 "11":("C","historical_2hydroxyflavanone_C_then_dehydration","2-hydroxynaringenin",
       "Historical PMC study of CGTa/CGTb and 2-hydroxyflavanone intermediates then dehydration; permanently exposed, not fresh."),
 "12":("C","historical_2hydroxyflavanone_C_then_dehydration","2-hydroxyflavanone",
       "Historical OsCGT recognizes 2-hydroxyflavanones which dehydrate to flavone C-glycosides; cannot treat endpoint as direct C6 enzyme step.")
}
DOI_IMPRINT={"11":"10.1073/pnas.202012745","12":"10.1074/jbc.M109.009258"}
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as fh:
  for b in iter(lambda:fh.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def emit(name,obj):
 rel=f"{DIR}/{name}";p=ROOT/rel
 if p.exists():raise RuntimeError(f"immutable {rel} exists")
 write(TASK,rel,json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
 return {"path":rel,"sha256":sha(p)}
def main():
 inventory=json.loads(M.read_text())
 # Must materialize disclosure + frozen inputs BEFORE new whole-document scientific reading.
 prec={"task":TASK,"event":"documentary_review_registration_not_retroactive_G5",
       "at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "agent_role":"A0_documentary_stage_registration",
       "input_manifest":{"path":str(M.relative_to(ROOT)),"sha256":sha(M)},
       "G4":inventory["G4_current_sha"],"no_scope_or_model_changes":True,
       "input_condition":"owner files already locally available; metadata + excerpts from first PDF pages already read this turn",
       "time_order_not_eligible_for_fresh":True,
       "now_authorized_read":"bounded publisher imprint and page-level textual reactions; no exact atomgraphs or holdout use",
       "source_exposure_rule":"all reviewed items permanently development-exposed; not prospective fresh evaluation",
       "reader_count":1,"A4_A5_independent_graph_extraction":"not_performed",
       "G5_formal_fresh_holdout_freeze":"not_asserted",
       "human_reviewed":False}
 preg=emit("documentary_review_precontract.json",prec)
 reviews=[]; identity_pass=0
 for no,(family,category,needle,meaning) in CASES.items():
  matches=[r for r in inventory["source_files"] if r["number"]==no and r["role"] in ("main_article_pdf","supporting_pdf")]
  if no=="10":matches=[r for r in matches if r["role"]=="supporting_pdf"]
  else:matches=[r for r in matches if r["role"]=="main_article_pdf"]
  if len(matches)!=1:raise RuntimeError(f"expected exactly one designated PDF for {no}, got {len(matches)}")
  row=matches[0];p=ROOT/row["local_custody"]
  if sha(p)!=row["sha256"]:raise RuntimeError(f"raw custody drift: {no}")
  proc=subprocess.run(["pdftotext","-layout",str(p),"-"],capture_output=True)
  if proc.returncode or not proc.stdout: raise RuntimeError(f"failed PDF text extraction {no}:{proc.stderr[:200]!r}")
  txt=proc.stdout.decode("utf-8",errors="replace")
  pages=txt.split("\f")
  pages=[pg for pg in pages if pg.strip()]
  positions=[]
  for pi,page in enumerate(pages):
   mt=re.search(re.escape(needle),page,re.I)
   if mt:
    excerpt=" ".join(page[max(0,mt.start()-160):min(len(page),mt.end()+260)].split())[:500]
    positions.append({"pdf_page":pi+1,"anchor_literal":needle,
                      "original_page_extracted_text_sha256":hashlib.sha256(page.encode()).hexdigest(),
                      "page_excerpt":excerpt})
  if not positions: raise RuntimeError(f"missing mandatory anchor {no}/{needle!r}")
  expected=DOI_IMPRINT.get(no,inventory["slot_summary"][no]["identifier"])
  doi_found=bool(re.search(re.escape(expected),txt,re.I))
  doi_status="imprint_DOI_text_found" if doi_found else "DOI_not_found_in_extracted_text_pending_other_identity"
  if doi_found:identity_pass+=1
  review={"number":no,"requested_identifier":inventory["slot_summary"][no]["identifier"],
          "imprint_identifier_expected":expected,"imprint_match_status":doi_status,
          "source_main_or_SI":row["role"],"sha256":row["sha256"],"bytes":row["bytes"],
          "raw_pointer":row["local_custody"],"family":family,"screen_category":category,
          "cited_observation":positions[:3],"limited_screen_interpretation":meaning,
          "title_or_DOI_alone_not_chemical_qualification":True,
          "scientific_content_read_now":True,"this_read_registered_by":preg,
          "not_a_first_scientific_read_for_fresh_purposes":True,
          "preexisting_exposure_closure":"unknown_or_previously_exposed",
          "fresh_target_admitted":False,"scope_bank_changed":False,
          "source_identity_A3_full_verified":False,
          "full_product_acceptor_donor_site_stereo_reference_graphs_verified":False,
          "A4_A5_independent_full_graph_extractions":False,
          "G6_disposition":"development_source_scope_screen_only",
          "do_not_interpret_as_all_reactions_of_article_screened":True}
  reviews.append(review)
  event(TASK,"documentary_source_screened",number=no,original_sha256=row["sha256"],scope_category=category,
        cited_pdf_page=positions[0]["pdf_page"],fresh_admitted=False)
 out={"task":TASK,"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
      "status":"bounded_documentary_screen_completed_not_A3_full_or_G6_chemistry",
      "review_precontract":preg,"reviews":reviews,
      "requested_sources":16,"numbered_sources_locally_present":12,"main_PDF_slots":11,
      "SI_only_slots":1,"imprint_DOI_text_matches":identity_pass,
      "imprint_DOI_unmatched_or_unprinted":12-identity_pass,
      "local_unavailable_no_access_numbers":["13","14","15","16"],
      "new_source_scientific_eligible_reactions":0,
      "qualified_fresh_C":0,"qualified_fresh_SS":0,
      "new_G7":False,"new_G9":False,"scientific_ABE_cells":0,
      "scope_conclusions_provisional":True,
      "follow_up":"A3 DOI/front verification for unprinted cases, A4/A5 independent original figure+graph extraction where scope-relevant (especially 03), A6 leakage/closure; keep previous exposures excluded."}
 receipt=emit("source_scope_screen.json",out)
 print(json.dumps({"reviewed":len(reviews),"DOI_imprint_text_matches":identity_pass,"categories":{r["number"]:r["screen_category"] for r in reviews},"report":receipt["path"],"fresh_admitted":0},ensure_ascii=False))
if __name__=="__main__":main()
