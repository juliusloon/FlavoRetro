"""Immutable A4 source-only scientific review of ten exposed C-E02 design reactions."""
from pathlib import Path
import json,hashlib,subprocess,xml.etree.ElementTree as ET,zipfile
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import save_json,sha_file,now
ROOT=Path.cwd()
BASE=ROOT/"outputs/task016-p7/v1/C/E02/design_source_qualification/v1"
OUT=BASE/"science_source_review_v1"
TASK="TASK-016-P7"
def ptr(p,location=None):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 r=dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
 if location is not None:r["location"]=location
 return r
def save(n,x):save_json(OUT/n,x,immutable=True)
def lines(n,rs):
 p=OUT/n
 if p.exists():raise RuntimeError("IMMUTABLE_EXISTS:"+str(p))
 write(TASK,str(p.relative_to(ROOT)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rs));p.chmod(0o444)
 return ptr(p)
def readrows(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
SOURCE={
 "FcCGT":dict(xml="data/raw/task016-p1/2026-10-06/pmc/PMC11975207-v1-0/fullTextXML.attempt-1",si="data/raw/task016-p1/2026-10-06/pmc/PMC11975207-v1-1/supplement.attempt-1",figure="data/raw/task016-p7/C/d5707e6b549efcd6c02ae500ef06d5408e86c410b35a4ef41ef0feb3adae22b4.attempt-1.jpg"),
 "KQ":dict(xml="data/raw/task016-p2/2026-10-06/pmc/292a07cb963f4db6ebbb9d8c/fullTextXML.attempt-1",si="data/raw/task016-p7/C/3a58f593bcf67a1bdcdbda9d957a768eedb505accb532e89d328649485bd965f.attempt-1.docx",figure="data/raw/task016-p7/C/ef5a4c5375c27a6fccf2ef13f2207bb86fcfb4ad26e11b751a60d63f53ffb49e.attempt-1.jpg"),
 "GA":dict(xml="data/raw/task016-p6/2026-10-07/1aab5f18e846c9f2b6a8b15e4958d02af388b875fa4cdb2c8b704de9d0f0becc.fullTextXML",si="data/raw/task016-p7/C/6ad11a8efb81d84f96b4daffbbe778c00bce1fe149d5fde2547de187cda9354f.attempt-1.pdf",figure="data/raw/task016-p6/2026-10-07/932d1dbf8ca75ff20cd8f549b0af0b758ed666564b80e5f5b9f572a7ec00f853.jpg",assay_figure="data/raw/task016-p7/C/d7c8002986d456f728210360cec50309b919e048b0366c7c42fc4157d5d0c2d9.attempt-1.jpg"),
 "603":dict(xml="data/raw/task016-p2/2026-10-06/pmc/ed29f9488d7098a6749b2d1f/fullTextXML.attempt-1",si="data/raw/task016-p7/C/7346eb0d2217d66c02db4b1a7b926f3a77db16a84ab3f447f96f6c15a674815d.attempt-1.docx",figure="data/raw/task016-p6/2026-10-07/5e09eea1ec2021aae9f6e91708a01628eeca02dc0f83d0762f94240f636a86a0.jpg"),
 "CHR":dict(si="data/raw/task016-p7/C/49056885bcaba1963c3a7ff01a249f287f9de32db4d786dd526c14653ec87b65.attempt-2.pdf",figure="data/raw/task016-p7/C/d47ce587bbd6371fc976a3a165d8ff0bed7c546441be070bb8b4197f4ad14d99.attempt-1.gif")
}
INPUT=BASE/"common_source_input_manifest.v3.json"
assert sha_file(INPUT)=="201c28783be80daa6086b931d1b3bce6d2c3d00d8ac901c3701516aec8a9d8c1"
oldhash={p:sha_file(BASE/p) for p in ("extractor_A4_complete.jsonl","extractor_A4_deferred.jsonl","role_A4_manifest.json","A4_graph_validation.json")}
universe=readrows(BASE/"source_exact_reaction_universe.v3.jsonl")
derived=[]
for name,s in SOURCE.items():
 if "xml" in s:
  t=ET.parse(ROOT/s["xml"]); pp=t.findall(".//body//p")
  derived.append(lines(name+".main_paragraphs.zero_based.jsonl",[dict(index_zero_based=i,normalized_text=" ".join("".join(p.itertext()).split()),source_pointer=ptr(s["xml"],".//body//p, Python list index "+str(i))) for i,p in enumerate(pp)]))
 if s["si"].endswith(".docx"):
  with zipfile.ZipFile(ROOT/s["si"]) as z:t=ET.fromstring(z.read("word/document.xml"))
  ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
  pp=t.findall(".//w:p",ns)
  derived.append(lines(name+".SI_docx_paragraphs.zero_based.jsonl",[dict(index_zero_based=i,text="".join(p.itertext()),source_pointer=ptr(s["si"],"ZIP word/document.xml .//w:p, Python list index "+str(i))) for i,p in enumerate(pp)]))
 else:
  pages=subprocess.check_output(["pdftotext","-layout",str(ROOT/s["si"]),"-"]).decode().split("\f")
  if not pages[-1].strip():pages.pop()
  derived.append(lines(name+".SI_physical_pages.one_based.jsonl",[dict(physical_page_one_based=i+1,text=p,source_pointer=ptr(s["si"],"physical PDF page "+str(i+1))) for i,p in enumerate(pages)]))
def e(source,member,loc):return ptr(SOURCE[source][member],loc)
UDP=ptr("data/raw/task016-p7/root/udp-glucose-attempt-1.json","PropertyTable.Properties[0]: CID8629 SMILES, full Standard InChI/key; identity only, not substitute for missing reaction donor")
review=[]
for row in universe:
 rid=row["reaction_id"]
 source="KQ" if rid in ("P3R-C05","P3R-C06") else "603" if rid in ("P3R-C03","P3R-C04") else "GA" if rid.startswith("P5R") else "FcCGT" if "FcCGT" in rid else "CHR"
 r=dict(reaction_id=rid,candidate_epoch_id="C-E02",review_role="A4 source-only scientific evidence review",qualified=False,evidence_eligible=False,human_reviewed=False,permanent_design_exposed=True,future_fresh_eligible=False,
   common_input_sha256=sha_file(INPUT),source_graph_extraction_files_preserved=True,source_acceptor_name=row["source_acceptor_name"],site=row["site"],source_evidence_pointers=[ptr(p) for p in SOURCE[source].values()],supports=[],conflicts=[],missing=[],pending_independent_A6_decision=True)
 if source=="KQ":
  k=rid=="P3R-C05"
  r.update(donor=dict(source_name="UDP-glucose",actual_reaction_context="TcCGT whole-cell glycosylation with UDP-Glc biosynthesized in situ by Cep/UgpA; not direct added-donor purified-enzyme assay",identity_reference=UDP,evidence=[e("KQ","xml","0-based body paragraphs 12 and 24; SI S2 biosynthesis")]),
   assay_standards=dict(acceptor="kaempferol/quercetin commercial Shanxi Huike Botanical Development Co.; SI S4 authentic substrate chromatograms",product="fed-batch products isolated by HPD100/80% ethanol and characterized LCMS/NMR; no commercial product standard claim",evidence=[e("KQ","xml","0-based body paragraphs 6,18,19,46"),e("KQ","si","S4 caption word/document.xml paragraph 89; S5 caption paragraph96")]),
   source_mass=dict(ion="[M-H]-",product_measured="447.0957" if k else "463.0908",acceptor_measured="285.0417" if k else "301.0369",instrument="LTQ Orbitrap XL LC/MS negative mode and an ion trap analyzer; main paragraph19",precision_and_acceptance_tolerance=None,source_calc_not_measured=True,evidence=e("KQ","si","S5"+("a/b" if k else "c/d")+"; actual original image"+("8.png/image9.png" if k else "10.png/image11.jpeg")+" ZIP members")),
   stereo=dict(source_sugar_relative_centres="drawn C2-C5 wedge/dash and textual D-glucose; original Figure9 and S5",anomeric_C1_aryl_bond="ordinary straight line; no unambiguous wedge in original source",explicit_beta_name_located=False,H1_H2_assignment="K overlapping 4.72-4.55 m,3H without isolated J1,2" if k else "Q 4.68 d,J9.9 Hz,2H; signal not individually assigned as J1,2 in source text",anomer_status="pending; neither enzyme name/shared donor nor unlabeled coupling alone proves beta",prior_A4_beta_encoding_is_source_review_pending=True),
   recommendation="defer source stereo qualification pending primary source ref32 and independent A6; keep previous candidate/beta graph files unchanged")
  r["supports"]=["actual K/Q acceptor substrates, UDP-Glc donor, C8 site via H6 retained/H8 lost and C13 NMR", "source-isolated corresponding product and original mass spectra"]
  r["missing"]=["unambiguous published C1 anomer assignment in inspected source", "individual anomeric J1,2 assignment/explicit beta naming not located"]
  r["conflicts"]=["common universe/A4 candidate specifies beta; current original-source evidence does not yet establish beta. This is an evidence gap, not proof of alpha."]
 elif source=="603":
  r.update(donor=dict(source_name=None,full_structure=None,actual_source_UDP_occurrences=0,identity_reference_cannot_fill_source_donor=True),recommendation="defer; donor remains null; historical qualification retained as historical record only")
  r["supports"]=["source drawn direct C6 product/acceptor"]
  r["missing"]=["actual donor identity for direct source reaction in original main/SI"]
 elif source=="GA":
  ga=rid=="P5R-C01"
  r.update(donor=dict(source_name="UDP-glucose",supplier="Beijing BGbiotech",identity_reference=UDP,evidence=e("GA","xml","0-based body paragraphs35,43")),
   assay=dict(purified_enzyme="AjCGT1/AjCGT2",buffer="100uL,50mM Tris-HCl pH7",donor="0.8mM UDP-Glc",acceptor="0.4mM",temperature_time="40C,1h",main_method_enzyme_mass="20ug",SI_figure_experiment_enzyme_mass="50ug",amount_difference_unresolved=True,boiled_control=True,evidence=[e("GA","xml","0-based body paragraph43"),e("GA","si","physical pages24-25, FiguresS15-S16")]),
   assay_standards=dict(acceptor="GA2/4OMGA3 purchased Beijing InnoChem",product="GA5: main paragraph7 blanket same-RT-as-standards statement; GA5 preparation/NMR provenance and standard trace not located in supplied SI" if ga else "4OMGAglc4 authentic standard generated from bergenin by1MNaOH3h,neutralization/prepHPLC;82mg; explicit4(std) trace and1H/13C NMR",norbergenin6_not_open_product5=True,evidence=[e("GA","xml","0-based body paragraphs7,35,39"),e("GA","si","physical page2 Methods1/2; FiguresS15/S16,S43-S46")]),
   source_mass=dict(ion="[M-H]-",product_measured="331.02" if ga else "345.08",source_graph_MW_annotation="332.07" if ga else "346.09",graph_annotation_not_measured_ion=True,source_fragment_labels=["211.08 [M-H-120]"] if ga else ["225.05 [M-H-120]","255.04 [M-H-90]"],instrument="LCQ Fleet ion trap ESI",precision_and_acceptance_tolerance=None,evidence=[e("GA","assay_figure","Figure2f" if ga else "Figure2i"),e("GA","si","physical page24 FigureS15" if ga else "physical page25 FigureS16")]),
   stereo=dict(source_explicit_name="2-C-beta-D-glycoside",source_C1_stereo_drawn=True,full_sugar_wedge_graph="original Figure1A",target_NMR="GA5 standalone NMR not located in SI; do not substitute lactone norbergenin6" if ga else "4 standard:1H H1'=5.09 d,J9.6 Hz; C1'=76.7; FiguresS45/S46 actual1H/13C",evidence=[e("GA","figure","Figure1A"),e("GA","xml","0-based body paragraph34"),e("GA","si","physical page2 and pages52-55")]),
   recommendation="source publication specifies donor/site/beta-D but GA5 authentic-standard/NMR provenance gap requires independent A6" if ga else "strong original-source candidate with donor/standard/NMR/site/stereo; source qualification reserved for independent A6")
  r["supports"]=["purified CGT UDP-Glc assay with source controls and LCMS product/C-glycoside fragments", "source-assigned C2 beta-D full graph"]
  r["conflicts"]=["main enzyme20ug vs SI captions50ug; preserve as source protocol/context difference, do not silently choose or assert same assay"]
  if ga:r["missing"]=["GA5 authentic standard trace/preparation not located despite main blanket statement", "GA5 standalone NMR not located; NMR norbergenin6 is different lactone"]
 elif source=="FcCGT":
  gal="GAL-" in rid
  r.update(donor=dict(source_name="UDP-glucose added for second step only",supplier="Carbosynth UDP-Glc>98%",identity_reference=UDP,second_step_excludes_first_donor="UDP-Gal or UDP-Xyl/UDP-GlcA-hUXS1 donor cascade",evidence=[e("FcCGT","xml","0-based body paragraphs16-20"),e("FcCGT","si","physical pages2-5, FigureS2page14")]),
   assay=dict(second_step_acceptor="fully converted in situ mono-C-Gal phloretin" if gal else "fully converted in situ mono-C-Xyl phloretin",acceptor_concentration="1mM",first_step_donor="2mM UDP-Gal" if gal else "2mM UDP-Xyl",second_step_donor="2mM UDP-Glc",enzyme="FcCGT5mg/mL" if gal else "FcCGT0.1mg/mL",conditions="100uL,50mM potassium phosphate pH8,10mM2-mercaptoethanol,30C",specific_activity="5.05+-0.49mU/mg" if gal else "167+-1mU/mg",ND_not_zero_and_slash_not_performed=True,evidence=e("FcCGT","si","physical page3 activity assays,page9TableS1")),
   preparative=dict(first_step="Gal2mM phloretin/UDP-Gal5mM48h" if gal else "Xyl2mM phloretin/UDP-GlcA4mM/hUXS1/NAD4mM10h",second_step="UDPGlc4mM12h" if gal else "UDPGlc4mM2h",isolated_mass="2.1mg" if gal else "3.5mg",isolated_yield="22%" if gal else "31%",purity=">=98% byHPLC",quantitative_conversion_not_isolated_yield=True,evidence=[e("FcCGT","si","physical pages4-5 preparative synthesis"),e("FcCGT","xml","0-based body paragraph32")]),
   assay_standards=dict(acceptor="mono-C-Gal/Xyl intermediates generated and tracked by HPLC; no separately purified precursor NMR packet located",product="isolated di-C-glycan product; full assigned1H,COSY,13C originals",commercial_mono_acceptor_standard_not_claimed=True),
   source_mass=dict(ion="[M+H]+",source_calculated="599.5" if gal else "569.5",source_found="599.2" if gal else "569.3",source_instrument="Shimadzu LCMS-2020 ESI" if gal else "Agilent1200 single-quadrupole6120LC/MS ESI",instrument_evidence=e("FcCGT","si","physical page7" if gal else "physical page6"),precision_calibration_resolution=None,average_or_monoisotopic_calculation_basis=None,HRMS_claim=False,additional_source_peak_unassigned=[] if gal else ["551.4; no invented species/adduct/loss assignment"],temporary_tolerance_created=False,evidence=e("FcCGT","si","physical page15 FigureS3" if gal else "physical page20 FigureS8")),
   stereo=dict(existing_glycan_preserved=True,source_full_numbered_product_structure=True,C1_aryl_wedge_drawn=True,Gal_vs_Glc_C4_difference_or_Xyl_C5_CH2="source diagrams distinguish C4 GalOH/GlcOH stereo; Xyl lacks C6OH",NMR_experiments=["1H400MHz methanol-d4 S4","COSY400MHz S5","13C101MHz S6"] if gal else ["1H500MHz D2O S9","COSY500MHz S10","13C126MHz S11"],anomer_observations=["H1'''4.95-4.93m,H1''4.93-4.91m; no isolated J1,2 stated","C1'''76.7,C1''76.6,C3'105.0,C5'104.2"] if gal else ["H1'''4.97dd,J9.5/2.4Hz,H1''4.86-4.82m","C1''75.5,C1'''74.9,C5''69.7,C6'''60.3,C3'102.7,C5'102.6"],chiralanalysis_or_HSQC_HMBC_NOESY_not_claimed=True,evidence=e("FcCGT","si","physical pages16-18 FiguresS4-S6" if gal else "physical pages21-23 FiguresS9-S11")),
   site_numbering=dict(source_symmetric_ring=True,drawn_existing_C3prime_Gal_or_Xyl_new_C5prime_Glc=True,conventional_Xyl_product_name_may_swap_C3prime_C5prime=True,not_a_second_species_or_glycan_exchange=True,evidence=e("FcCGT","xml","0-based body paragraph19 and Figure1b")),
   recommendation="original donor/staged second step/full source graph and six product NMR support candidate; low-precision mass basis remains pending independent A6 using existing rules; no new tolerance")
  r["supports"]=["actual second UDP-Glc transfer to tracked mono-C-glycan acceptor", "source fully drawn stereochemical graph/site; isolated final product1H/COSY/13C original spectra"]
  r["missing"]=["mass calibration/resolution/acceptance tolerance and average-vs-monoisotopic basis not stated", "separately isolated monoacceptor NMR not located"]
  r["conflicts"]=["source calculated vs found decimal mass preserved; not automatically exact-mass pass", "auxiliary hUXS1 assay SIpage4=2.0mg/L vs S16page28=2.0mg/mL; main0-basedp28/SIpage4 NAD0.5mM vs S16page28NAD2.0mM; keep auxiliary donor-cascade context separate"]
 else:
  ch=rid=="C-CHRYSIN-CH6"
  r.update(donor=dict(source_name="UDP-glucose explicit Figure2 and SI FigureS9",identity_reference=UDP,evidence=e("CHR","figure","Figure2 enzymatic transfer arrow")),
   source_mass=dict(ion="[M+H]+",table_observed="417.1166" if ch else "449.1063",table_calculated="417.1186" if ch else "449.1063",separate_spectrum_observed="417.1221" if ch else None,observed_conflict_unresolved=ch,temporary_tolerance_created=False,evidence=e("CHR","si","physical page2 TableS1"+(";page6FigureS4" if ch else ""))),
   stereo=dict(source_explicit_C6_beta_D_graph=True,NMR_source="SI S7/S8 forCH; S12/S13 forLU",evidence=e("CHR","figure","Figure2 source R1/R2=H forCH orOH forLU")),
   recommendation="source full donor/site/stereo/NMR candidate but two CH observed mass values require independent A6; retain both" if ch else "source full donor/site/stereo/NMR candidate; source qualification reserved for independent A6")
  r["supports"]=["original explicit UDP-Glc flavone C6 transfer and beta-D graph", "original assigned NMR/site and mass table"]
  if ch:r["conflicts"]=["same source CH observed417.1166 TableS1 vs417.1221 FigureS4, calculated417.1186 preserved"]
 review.append(r)
assert len(review)==10 and {r["reaction_id"] for r in review}=={r["reaction_id"] for r in universe}
assert all(not r["qualified"] and not r["evidence_eligible"] for r in review)
lines("source_scientific_review.10rows.jsonl",review)
views={}
for name,pages in {"FcCGT":[6,7,14,15,16,17,18,20,21,22,23],"GA":[2,24,25,52,53,54,55]}.items():
 views[name]=[dict(**ptr(OUT/"original_views"/(name+".SI.physical_page"+str(p).zfill(2)+".png")),physical_page_one_based=p,actually_visually_inspected=True) for p in pages]
views["KQ"]=[dict(**ptr(OUT/"original_views"/n),actually_visually_inspected=True) for n in ("KQ.image8.png","KQ.image9.png","KQ.image10.png","KQ.image11.jpeg")]
save("actual_original_inspection_record.json",dict(timestamp=now(),FcCGT_main_complete_read_paragraphs=38,FcCGT_SI_complete_text_read_physical_pages=30,
 FcCGT_complete_NMR_originals_inspected=["S4","S5","S6","S9","S10","S11"],FcCGT_coverage="all main body paragraphs and all SI physical pages text;11 original rendered pages visually inspected",
 KQ_coverage="main relevant methods/results paragraphs and complete SI DOCX text;Figure9 original and S5a-d original ZIP image members visually inspected",
 GA_coverage="main methods/results and fullSI text searched; selected7 pages including assay,standard synthesis and all original SI NMR pages visually inspected",
 CHR_coverage="earlier own A4 original Fig2/SI original mass/NMR review retained; no repeat publisher acquisition",original_views=views,derived_text_pointers=derived,
 source_pointer_location_convention="New main paragraph locators are Python .//body//p list 0-based; original universe ambiguous older labels preserved; PDF physical pages 1-based",
 raw_instrument_information_correction="Fc earlier instrument unknown is supplemented by actual SIpages6/7 model evidence; mass resolution/calibration/calculation basis stillunknown",
 source_anomer_evidence_correction="Candidate universe/ownA4 beta encoding forK/Q is retained immutable; source beta assignment is pending, ordinary C1 line and unlabeled mixed-integral coupling not independent beta confirmation",
 read_other_extractor_outputs=False,read_root_A6_final_graphs=False))
for p,h in oldhash.items():assert sha_file(BASE/p)==h
bound=[ptr(INPUT),ptr(BASE/"source_exact_reaction_universe.v3.jsonl")]+[ptr(BASE/p) for p in oldhash]+[ptr(p) for s in SOURCE.values() for p in s.values()]+[UDP]+derived
for n in ("FcCGT_original_view_manifest.json","KQ_original_SI_image_extraction_manifest.json","GA_original_view_manifest.json","GA_original_assay_evidence_request_plan.json","GA_original_assay_evidence_request_execution.json","source_scientific_review.10rows.jsonl","actual_original_inspection_record.json"):bound.append(ptr(OUT/n))
save("role_A4_source_scientific_review_manifest.json",dict(task=TASK,candidate_epoch_id="C-E02",role="A4 source-only scientific evidence review",approval_type="agent_delegated",human_reviewed=False,
 timestamp=now(),processed_reaction_count=10,source_qualified_count=0,permanent_exposed_design_sources_only=True,read_other_extractor_outputs=False,read_root_A6_final_graphs=False,
 previously_read_exposed_E01_own_graphs_and_runtime_diagnostic=True,prior_history_and_role_correction_retained=True,no_current_or_future_holdout_read_for_this_activity=True,
 scope_built_or_modified=False,fresh_extraction=False,MCTS_started=False,source_admission_reserved_for_independent_A6=True,
 old_A4_output_SHA_preserved=oldhash,source_recommendations_are_not_admission=True,raw_values_conflicts_nulls_retained=True,
 no_new_mass_tolerance_or_precision_inferred=True,new_HTTP_requests_for_this_scientific_review=2,
 new_source_acquisition="official public PMC11053098 Figure2/SI, same permanent exposed source closure; preregistered plans and physical HTTP ledger retained",
 bound_files=bound,budget_snapshot=json.loads((ROOT/"outputs/task016-p7/v1/C/raw_manifest.json").read_text()) | {"objects":[]}))
event(TASK,"C_E02_A4_source_scientific_review_completed",processed=10,qualified=0,scope_modified=False,fresh=False,manifest=ptr(OUT/"role_A4_source_scientific_review_manifest.json"))
print(json.dumps(dict(manifest=ptr(OUT/"role_A4_source_scientific_review_manifest.json"),recommendations=ptr(OUT/"source_scientific_review.10rows.jsonl"),inspection=ptr(OUT/"actual_original_inspection_record.json")),ensure_ascii=False,indent=2))
