#!/usr/bin/env python3
"""SS-E02 post-G4 PMC11125054 first scientific text triage, not full graph admission.
Explicitly records irreversible source exposure on first chemistry-body read.
"""
from __future__ import annotations
import json,sys,hashlib,re,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,ContractError
TASK="TASK-016-P7"
A3="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-A3/"
SRC="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-original/"
G5="outputs/task016-p7/v1/SS/E02/stages/batches/SS-E02-R2-PMC11125054/G5_FRESH_HOLDOUT_ACQUIRE.json"
O="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-science-screen/"
SELF="scripts/task016_p7_ss_e02_pmc11125054_science_screen_v1.py"
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return sha_file(ROOT/p)
def save(p,r):
 if (ROOT/p).exists():raise ContractError("immutable artifact already exists "+p)
 write(TASK,p,json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def read(p):return json.loads((ROOT/p).read_text())
def original():
 rows=read(SRC+"raw_manifest.json")["objects"]
 return next(r for r in rows if r["kind"]=="article_version")
def pre():
 verify_stage_chain(G5,sha(G5))
 a3=read(A3+"A3_publication_identity.json")
 if not a3["publication_identity_verified"]:raise ContractError("A3 identity not qualified")
 raw=original()
 save(O+"science_screen_pre_execution.json",dict(
  task=TASK,epoch_id="SS-E02",role="bounded source reading/triage; not full dual independent graph extraction",
  preregistered_at=now(),source_id="PMC11125054",frozen_scope_G5_SHA=sha(G5),
  original_article_path=raw["path"],original_SHA256=sha(raw["path"]),
  A3_verification_SHA256=sha(A3+"A3_publication_identity.json"),
  executing_code_sha256=sha(SELF),
  actual_body_read_has_not_started=True,
  chemistry_screen_decision_rules={
   "in_domain_possible":"original evidence must establish same flavonol 3-O-betaD-Glcp/Galp parent O2 betaGlcp, UDP-glucose, full substrate/product and assay; any missing remains deferred",
   "automated_signals":"paragraph strings only; are NOT compound or covalent graph evidence",
   "numeric_mass":"never infer values; missing remains null",
   "figures":"image labels/captions only; full drawn stereochemistry unvalidated",
   "negative":"absence of text token does not prove chemistry nonexistent",
   "future_exposure":"after first scientific text read this entire article becomes exposed and cannot later be recycled as unseen-fresh in another epoch"},
  read_holdout=False,read_model_outcome=False,read_ABE=False,
  never_reclassify_metadata_as_G6_without_independent_A4_A5_and_A6=True))
 print("pre-registered source scientific screen; will mark entire article permanently exposed")
def screen():
 verify_stage_chain(G5,sha(G5))
 p=read(O+"science_screen_pre_execution.json")
 raw=original()
 if p["original_SHA256"]!=sha(raw["path"]) or p["executing_code_sha256"]!=sha(SELF):
  raise ContractError("pre-read SHA drift")
 if p["A3_verification_SHA256"]!=sha(A3+"A3_publication_identity.json"):
  raise ContractError("A3 drift")
 exposure=O+"permanent_postfreeze_source_exposure.json"
 if (ROOT/exposure).exists():raise ContractError("source review has already started")
 started=now()
 # The following step is the first chemical body read by this role.
 doc=ET.parse(ROOT/raw["path"]).getroot()
 body=doc.find("body")
 if body is None:raise ContractError("original lacks body; cannot screen")
 save(exposure,dict(task=TASK,family="SS",epoch_id="SS-E02",
  exposure_id="SS-E02-G5-R2:PMC11125054:first_scientific_read",
  source_id="PMC11125054",pmid="38794460",doi="10.3390/plants13101390",
  closure_tokens=["article:PMC11125054","pmid:38794460","doi:10.3390/plants13101390"],
  first_scientific_body_read_started_at=started,development_exposed=True,
  exposure_type="post_scope_first_chemical_source_review",
  eligible_for_fresh_holdout_in_next_epoch=False,
  current_epoch_G6_pending=True,current_epoch_fresh_admitted=False,
  raw_original_sha256=sha(raw["path"]),G5_frozen_before_read=True,
  source_closure_applies_to_whole_article=True,human_reviewed=False))
 sections=[];hits=[]
 terms=[("explicit_flavonol_3O_parent",re.compile("flavonol.{0,30}3.{0,6}O.{0,12}(?:gluc|galact)",re.I)),
        ("explicit_1to2_or_parent_O2",re.compile(r"(?:1\s*(?:[→\->]|to)\s*2|2.{0,7}(?:O|″|''|\\u2033).{0,12}glucosyl)",re.I)),
        ("glycosyltransferase",re.compile(r"glycosyltransferase|glucosyltransferase",re.I)),
        ("UDP_glucose",re.compile(r"UDP.{0,3}glucose|UDP.{0,3}Glc",re.I))]
 for sect in body.findall(".//sec"):
  title=sect.find("title")
  heading=" ".join(title.itertext()).strip() if title is not None else ""
  paragraphs=[(" ".join(el.itertext())).strip() for el in sect.findall("p")]
  sections.append(dict(heading=heading,paragraphs=len(paragraphs)))
  for i,t in enumerate(paragraphs):
   met=[k for k,rx in terms if rx.search(t)]
   if met:
    hits.append(dict(section=heading,paragraph_index=i,matched_signal_names=met,
       text_excerpt=t[:1050],excerpt_is_not_stereochemical_graph_evidence=True))
 figs=[]
 for fig in body.findall(".//fig"):
  label=fig.findtext("label") or ""
  caption=fig.find("caption")
  txt=(" ".join(caption.itertext())).strip() if caption is not None else ""
  figs.append(dict(label=label,caption_excerpt=txt[:850],graph_source_not_transcribed=True))
 tables=[]
 for tw in body.findall(".//table-wrap"):
  cap=tw.find("caption");label=tw.findtext("label")
  tables.append(dict(label=label,caption_excerpt=" ".join(cap.itertext())[:850] if cap is not None else "",
    machine_readable_covalent_graph_verified=False))
 counts={k:sum(k in r["matched_signal_names"] for r in hits) for k,_ in terms}
 # Never infer a negative enzyme claim from an absent term; recommend defer.
 result=dict(task=TASK,epoch_id="SS-E02",role="A4 bounded scientific original-text screening",
  timestamp=now(),original_sha256=sha(raw["path"]),exposure_sha256=sha(exposure),
  source_id="PMC11125054",status="textual_triage_complete_scientific_admission_deferred",
  sections=sections,signal_counts=counts,context_evidence=hits,
  captions_figures=figs,captions_tables=tables,
  full_acceptor_and_product_graph_extracted=False,donor_graph_verified=False,
  all_original_figures_double_transcribed=False,complete_stereo_verified=False,
  structure_complete=False,reference_precursor_complete=False,
  scope_applicability=None,source_assay_specific_eligibility=None,
  A5_independent_extraction_completed=False,A6_closure_adjudication_completed=False,
  eligible_for_fresh_holdout=False,G6_admitted=0,
  source_saturation=False,human_reviewed=False,read_ABE=False,
  note="Text hits are findability aids, not measured products, novel enzyme proof, chemical graph, or transferable holdouts")
 save(O+"A4_bounded_original_text_screen.json",result)
 print(json.dumps(dict(source="PMC11125054",sections=len(sections),
  signal_counts=counts,figures=len(figs),tables=len(tables),
  G6=0,chemistry_source_exposed=True),ensure_ascii=False))
if __name__=="__main__":
 {"pre":pre,"screen":screen}[sys.argv[1]]()
