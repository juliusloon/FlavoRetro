"""A4 complete literal source matrices and explicit substrate/control universes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,collections,xml.etree.ElementTree as ET
from scripts.operate import write
BASE=Path("outputs/task016-p7/v1/SS/E02_design");OUT=BASE/"A4_assay_universe_v1";TASK="TASK-016-P7"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(name,obj,lines=False):
 p=OUT/name
 if p.exists():raise RuntimeError("immutable artifact already exists: "+str(p))
 content="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in obj) if lines else json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
 write(TASK,str(p),content)
def pointer(p):return dict(path=str(p),sha256=sha(p))
def main():
 started=now(); common=BASE/"common_source_raw_only_input_v3.json";m=json.loads(common.read_text());source={x["source_id"]:x for x in m["sources"]}
 assert sha(common)=="2d01e38e8ee207bad274e9a973cbead84a35b626f43509e95eb42971e0c9e06d"
 for p,h in m["raw_input_files_sha256"].items():assert sha(p)==h,p
 native={s:json.loads((BASE/"source_native_text"/(s+".json")).read_text()) for s in source}
 rows=[];standards=[];catalog=[]
 def add(s,loc,index,**fields):
  row=dict(assay_id=f"SS-E02:A4:{s}:{loc}:{index}",source_id=s,source_location=loc,input_manifest_sha=sha(common),source_original_pointer=source[s]["full_original_xml"],reviewed_at=now(),agent_role="A4",development_exposed=True,evidence_eligible=False,human_reviewed=False,structure_complete=False,reference_precursor_complete=False,product_smiles=None,exact_product_identity_pending=True,read_other_extractor_output=False,read_model_outcomes=False,**fields)
  rows.append(row);return row
 p=BASE/"A4_native_source/PMC13084081/mmc1.pdf.pages.jsonl";pages=[json.loads(s) for s in p.read_text().splitlines()]
 headers4=["N7Glu","H7Glu","Q3Glu","Q7Glu","S3Glu","S7Glu","S4'Glu","A7Glu","D7Glu"]
 headers5=["N7Glu","H7Glu","Q3Glu","Q7Glu","K3Glu","K7Glu","K4'Glu","A7Glu","D7Glu"]
 table4=[]
 for line in pages[30]["literal_text"].splitlines():
  cells=re.split(r"\s{2,}",line.strip())
  if cells[0].startswith("Cg"):
   assert len(cells)==10,cells;table4.append(cells)
   for j,(a,v) in enumerate(zip(headers4,cells[1:])):
    assert v in ("+","-")
    add("PMC13084081","SI_Table4",f"{len(table4)}-{j+1}",native_review_pointer=pointer(p),raw_attachment_pointer=dict(path=pages[30]["raw_path"],sha256=pages[30]["raw_sha256"]),physical_page=31,enzyme_literal=cells[0],acceptor_literal=a,donor_literal=None,literal_outcome=v,outcome="detectable_catalytic_activity" if v=="+" else "no_observed_activity",value=None,unit=None,source_footnote_literal="+ detectable catalytic activity; - no observed activity",source_conflicts=["Source Table4 S3/S7/S4' headers conflict with K3/K7/K4' names used elsewhere; do not silently rename." ] if a.startswith("S") else [],assay_grain="enzyme x literal acceptor, donor unresolved in collapsed table")
 assert len(table4)==13
 table5=[]
 for line in pages[31]["literal_text"].splitlines():
  cells=re.split(r"\s{2,}",line.strip())
  if "(UDP-" not in cells[0]:continue
  assert len(cells)==10,cells;table5.append(cells)
  enzyme,donor=re.fullmatch(r"(.+?) \((UDP-.+?)\)",cells[0]).groups()
  for j,(a,v) in enumerate(zip(headers5,cells[1:])):
   q=re.fullmatch(r"(\d+(?:\.\d+)?)(?:±(\d+(?:\.\d+)?))?(?: ([a-z]+))?",v); assert q,v
   mean=float(q[1]);sd=float(q[2]) if q[2] is not None else None
   add("PMC13084081","SI_Table5",f"{len(table5)}-{j+1}",native_review_pointer=pointer(p),raw_attachment_pointer=dict(path=pages[31]["raw_path"],sha256=pages[31]["raw_sha256"]),physical_page=32,enzyme_literal=enzyme,donor_literal=donor,acceptor_literal=a,literal_outcome=v,value=mean,standard_deviation=sd,significance_letters=q[3],unit="conversion_rate_percent",n=3,outcome="explicit_numeric_zero" if mean==0 else "positive_conversion",zero_is_missing=False,source_conflicts=["Table5 UGT79B202 block donor printed UDP-Glc whereas matching Figure2F values are labelled UDP-Rha; retain literal donor, no silent reconciliation."] if enzyme in ["UGT79B202","N202F","N202L"] else [],assay_grain="enzyme/variant x literal acceptor x literal donor")
 assert len(table5)==20
 for line in pages[32]["literal_text"].splitlines():
  if not re.search(r"\d+-\d+-\d+",line):continue
  cells=re.split(r"\s{2,}",line.strip())
  name,abbr,formula,cas=(cells[-4:] if len(cells)>=4 and cells[-2].startswith("C") else [cells[-3],None,cells[-2],cells[-1]])
  standards.append(dict(source_id="PMC13084081",source_location="SI_Table6",physical_page=33,source_name_literal=name,source_abbreviation_literal=abbr,source_formula_literal=formula,source_CAS_literal=cas,literal_line=line,native_review_pointer=pointer(p),identity_is_reaction_evidence=False))
 assert len(standards)==25
 # The full declared initial screen dimensions are preserved without pretending its collapsed
 # table identifies donor-specific outcomes or proves every Cartesian combination was executed.
 dump("PMC13084081_initial_screen_declared_universe.json",dict(source_id="PMC13084081",source_locations=["body//p[13,21]","SI Table4"],enzymes=[x[0] for x in table4],acceptors_literal_Table4=headers4,acceptors_literal_main=headers5,donors_literal=["UDP-Glc","UDP-Rha","UDP-Xyl","UDP-Gal"],potential_cartesian_count=13*9*4,actual_condition_level_execution_not_explicitly_resolved=True,collapsed_table_actual_outcomes=117,donor_specific_outcomes_unknown_not_zero=True))
 # Actual Figure2H donor screen: no numeric magnitude inferred from plotted bars.
 donor2=[("UGT79B202","UDP-Glc","visible_activity"),("UGT79B202","UDP-Rha","visible_activity"),("UGT79B202","UDP-Xyl","explicit_ND"),("UGT79B202","UDP-Gal","explicit_ND"),("UGT79B203","UDP-Glc","visible_activity"),("UGT79B203","UDP-Rha","explicit_ND"),("UGT79B203","UDP-Xyl","explicit_ND"),("UGT79B203","UDP-Gal","small_graphical_activity_not_numeric_zero")]
 for k,(e,d,o) in enumerate(donor2,1):add("PMC13084081","Figure2H",k,enzyme_literal=e,donor_literal=d,acceptor_literal="K3Glu",outcome=o,value=None,unit="relative_activity_percent",literal_outcome="N.D." if o=="explicit_ND" else None,source_graphical_value_preserved_not_digitized=True)
 # Four-position saturation scan explicitly assayed all 19 substitutions with four donors.
 # Original figure P143 label and prose Phe143 identity conflict remains unresolved.
 for position in ("P143","W350","E371","N375"):
  original={"P143":"F","W350":"W","E371":"E","N375":"N"}[position]
  for aa in "ACDEFGHIKLMNPQRSTVWY":
   if aa==original:continue
   for d in ["UDP-Rha","UDP-Glc","UDP-Xyl","UDP-Gal"]:
    add("PMC13084081","Figure4E_saturation_scan",f"{position}-{aa}-{d}",enzyme_literal="Cm1,2RhaT:"+position+aa,acceptor_literal="N7Glu",donor_literal=d,outcome="reported_no_alternative_donor_activity" if d!="UDP-Rha" else "raw_graphical_patch_exact_outcome_not_transcribed",value=None,source_locations_additional=["body//p[40,46]"],source_conflicts=["Figure4 D/E prints P143 while prose names Phe143; source position alias not corrected"] if position=="P143" else [],assay_grain="source-reported saturation mutant x donor",graphical_raw_preserved=True)
 # Native Table1 acceptor and donor screening, retaining source footnote annotations.
 table=native["PMC4282749"]["tables"][0];section=None
 for r in table["raw_native_rows"]:
  if r["section"]!="tbody":continue
  cells=[x["literal_text"] for x in r["literal_cells"]]
  if len(cells)==1:section="acceptor" if cells[0].startswith("Sugar acceptor") else "donor";continue
  name,v=cells;nd=v=="ND";q=re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*±\s*(\d+(?:\.\d+)?)\s*",v) if not nd else None
  assert nd or q,(name,v)
  add("PMC4282749","Table1",r["source_row"],enzyme_literal="UGT79B6",screen_axis=section,acceptor_literal=name if section=="acceptor" else "kaempferol 3-O-glucoside",donor_literal="UDP-glucose" if section=="acceptor" else name,literal_outcome=v,outcome="not_detected" if nd else "positive_relative_activity",value=None if nd else float(q[1]),standard_deviation=None if nd else float(q[2]),unit="relative_activity_percent",ND_is_numeric_zero=False,product_standard_identification_explicit_source_footnote_b=(section=="acceptor" and name.strip()=="Kae 3-O-glucosideb"),source_footnotes_literal=table["literal_footnotes"],native_review_pointer=pointer(BASE/"source_native_text/PMC4282749.json"))
 # Full original Figure3A 28 acceptors and 3C six donors. Names transcribed by A4
 # from actual official original JPEG; no complex graph is reconstructed from the names.
 acceptors131=["Apigenin 7-O-glucoside","Luteoloside","Prunin","Viscumside A","Astragalin","Isoquercitrin","Hyperoside","Reinutrin","Genistin","Sophoricoside","Quercitrin","Avicularin","Quercetin 3-O-beta-D-glucuronide","Vitexin","Puerarin","Scutellarin","Baimaside","Calendoflavobioside","Apiin","Puerarin apioside","Naringenin","Homoeriodictyol","Apigenin","Chrysin","Genistein","Orobol","Dihydrokaempferol","Kaempferol"]
 graph131=next(x for x in source["PMC13140228"]["official_all_main_figures_and_complete_SI_raw"] if "g006.jpg" in x["url"])
 for i,a in enumerate(acceptors131,1):add("PMC13140228","Figure3A_B_acceptors",i,enzyme_literal="CaApiGT1",acceptor_source_number=i,acceptor_literal=a,donor_literal="UDP-Api generated in situ by AtUAXS1 from UDP-GlcA",coupled_donor_generation_preserved=True,outcome="reactive_red_source_label" if i<=10 else "source_reported_nonreactive",value=None,standard_deviation=None,unit="conversion_rate_percent",partial_product_source_label=str(i)+"a" if i<=10 else None,complete_product_named_from_original="apiin" if i==1 else "kaempferol-3-O-[beta-D-apiofuranosyl-(1->2)-beta-D-glucopyranoside]" if i==5 else None,graph_pointer=dict(path=graph131["path"],sha256=graph131["sha256"]),source_locations_additional=["body//p[17,19]"],graphical_numeric_bars_not_invented=True)
 for i,d in enumerate(["UDP-Api","UDP-Xyl","UDP-GlcA","UDP-Glc","UDP-Gal","UDP-Rha"],1):add("PMC13140228","Figure3C_D_donors",i,enzyme_literal="CaApiGT1",donor_literal=d,acceptor_literal="Apigenin 7-O-glucoside (1)",outcome="reactive_red_source_label" if d=="UDP-Api" else "source_reported_nonreactive",value=None,graph_pointer=dict(path=graph131["path"],sha256=graph131["sha256"]),unit="conversion_rate_percent")
 mutants131=["WT","W17A","H22A","E90A","D119A","L126A","F138A","Y139A","L140A","N141A","Y142A","L149A","F188A","Y193A","F199A","C200A","V203A","Q277A","R374A","P375A","T376A","D377A","H378A"]
 lost131={"W17A","H22A","E90A","D119A","Y139A","L149A","Y193A","F199A","V203A","Q277A","R374A","H378A"}
 for i,e in enumerate(mutants131,1):add("PMC13140228","Figure6A_variants",i,enzyme_literal="CaApiGT1:"+e,donor_literal="UDP-Api",acceptor_literal="Astragalin (5)",outcome="source_reported_activity_loss" if e in lost131 else "visible_graphical_activity",value=None,unit="relative_efficiency_percent",source_locations_additional=["body//p[27]"],graphical_numeric_bars_not_invented=True)
 # AgApiT complete original figure4 screening: GDP-Fuc remains GDP, no rename to UDP.
 donors106=["UDP-Api","UDP-Araf","UDP-Rha","UDP-Glc","UDP-GlcUA","UDP-Gal","UDP-GalUA","UDP-Xyl","UDP-GlcNAc","GDP-Fuc"]
 acceptors106=["Apigenin 7-O-glucoside","Quercetin 7-O-glucoside","Luteolin 7-O-glucoside","Chrysoeriol 7-O-glucoside","Naringenin 7-O-glucoside","Quercetin 3-O-glucoside","Kaempferol 3-O-glucoside","Apigenin","Apiin"]
 graph106=next(x for x in source["PMC10602602"]["official_all_main_figures_and_complete_SI_raw"] if "kiad402f4.jpg" in x["url"])
 for i,d in enumerate(donors106,1):add("PMC10602602","Figure4A_donors",i,enzyme_literal="AgApiT:WT",donor_literal=d,acceptor_literal="Apigenin 7-O-glucoside",outcome="source_reported_product_generated" if d=="UDP-Api" else "source_reported_no_product",value=None,unit="enzyme_activity_microU_per_microgram",graph_pointer=dict(path=graph106["path"],sha256=graph106["sha256"]),source_conflicts=["Text describes ten UDP-sugars but actual original Figure4A and methods include GDP-Fuc; retain actual donor label."] if d=="GDP-Fuc" else [])
 for i,a in enumerate(acceptors106,1):add("PMC10602602","Figure4B_acceptors",i,enzyme_literal="AgApiT:WT",donor_literal="UDP-Api",acceptor_literal=a,outcome="source_reported_activity" if i<=4 else "source_reported_negligible_activity_visible_small_bar" if i==5 else "source_reported_failed_to_react",value=None,unit="enzyme_activity_microU_per_microgram",product_source_name="apiin" if i==1 else None,graph_pointer=dict(path=graph106["path"],sha256=graph106["sha256"]),source_locations_additional=["body//p[18,35]"],graphical_numeric_bars_not_invented=True)
 mutant106=["WT","I139V","I139T","I139S","F140T","F140I","F140V","L356Q","L356I","L356T","I139T/L356Q","I139T/F140T/L356Q"]
 for e in mutant106:
  for d in ["UDP-Api","UDP-Glc","UDP-Xyl"]:
   positive=d=="UDP-Api" and e in ("WT","I139V","L356Q")
   add("PMC10602602","Figure5A_mutants_and_alternative_donor_tests",e+":"+d,enzyme_literal="AgApiT:"+e,donor_literal=d,acceptor_literal="Apigenin 7-O-glucoside",outcome="source_reported_activity" if positive else "source_reported_no_trace_activity",value=None,reported_relative_activity_percent_text=30 if positive and e=="I139V" else 15 if positive and e=="L356Q" else None,source_locations_additional=["body//p[24,31,45]"],ND_is_numeric_zero=False)
 # Table3 complete kinetic dataset: three enzymes x two scanned substrates x three parameters.
 kt=[];substrate=None
 for r in native["PMC10602602"]["tables"][2]["raw_native_rows"]:
  if r["section"]!="tbody":continue
  c=[x["literal_text"] for x in r["literal_cells"]]
  if len(c)==5:substrate=c.pop(0)
  assert len(c)==4
  for parameter,unit,v in zip(["Km","kcat","kcat_over_Km"],["microM","x10^-3 per_second","per_M_per_second"],c[1:]):
   q=re.fullmatch(r"(\d+(?:\.\d+)?)\s*±\s*(\d+(?:\.\d+)?)",v);assert q,v
   kt.append(dict(source_id="PMC10602602",source_location="Table3",scanned_substrate_literal=substrate,enzyme_literal=c[0],parameter=parameter,unit=unit,literal_value=v,value=float(q[1]),standard_deviation=float(q[2]),n_measurements_per_concentration=3,source_original_pointer=source["PMC10602602"]["full_original_xml"]))
 assert len(kt)==18
 # Retain every native original main figure/table/SI object; uncovered graphical condition
 # grids remain explicitly pending instead of being omitted from the denominator.
 for sid,x in native.items():
  raw=ET.fromstring(Path(x["source_path"]).read_bytes())
  for f in x["figures"]:catalog.append(dict(source_id=sid,kind="original_main_figure",object_id=f["id"],literal_caption=f["literal_caption"],raw_graphic_identifiers=f["graphic_attributes"],source_original_pointer=source[sid]["full_original_xml"]))
  for t in x["tables"]:catalog.append(dict(source_id=sid,kind="original_main_table",object_id=t["id"],literal_caption=t["literal_caption"],all_native_rows=t["raw_native_rows"],literal_footnotes=t["literal_footnotes"]))
  for k,s in enumerate(raw.findall(".//supplementary-material"),1):catalog.append(dict(source_id=sid,kind="source_declared_supplement",object_id=s.get("id",str(k)),literal_text="".join(s.itertext()),source_original_pointer=source[sid]["full_original_xml"]))
 for sid in source:
  for p in (BASE/"A4_native_source"/sid).glob("*.native.json"):
   data=json.loads(p.read_text())
   for t in data.get("tables",[]):catalog.append(dict(source_id=sid,kind="complete_native_SI_table",native_review_pointer=pointer(p),table=t,raw_path=data["raw_path"],raw_sha256=data["raw_sha256"]))
   seen=set()
   for q in data.get("paragraphs",[]):
    if re.match(r"\s*Figure S\d+",q["literal_text"]):
     key=re.match(r"\s*(Figure S\d+)",q["literal_text"])[1]
     if key in seen:continue
     seen.add(key);catalog.append(dict(source_id=sid,kind="complete_SI_figure_caption",object_id=key,native_review_pointer=pointer(p),paragraph=q,raw_path=data["raw_path"],raw_sha256=data["raw_sha256"]))
 dump("source_assay_universe.jsonl",rows,lines=True)
 dump("PMC13084081_Table6_all25_source_standards.json",standards)
 dump("PMC10602602_Table3_all18_kinetic_values.json",kt)
 dump("all_original_native_object_catalog.json",catalog)
 counts=dict(collections.Counter((x["source_id"]+":"+x["source_location"]) for x in rows))
 zeros=sum(x["source_location"]=="SI_Table5" and x["value"]==0 for x in rows)
 assert zeros==82 and len(rows)==750,(len(rows),zeros,counts)
 pending=[dict(source_id="PMC13084081",source_locations=["Figure4B/G/H/I/J","Figure5I/J","fullSI graphical profiles"],reason="Complete originals and all caption/native text retained; additional raw graphical chimeric and condition-level grids need explicit A4/A5 outcome transcription before claiming full every-experiment denominator."),dict(source_id="PMC4282749",source_location="DataSetS1 source tpj0079-0769-sd12.xls",reason="Complete legacy workbook retained; raw native parser unavailable; source Appendix identifies phylogenetic alignment, independent relevance check pending."),dict(source_id="PMC13140228",source_locations=["SI FigureS7 condition/kinetic curves","engineered-cell co-culture/Fig7+S26-S31"],reason="Source parameter and multistep cellular outcome panels retained separately; they cannot be counted as source single glycosyltransfer product-graph supports.")]
 dump("remaining_graphical_universe_review_items.json",pending)
 outputs={str(p):sha(p) for p in sorted(OUT.iterdir()) if p.is_file()}
 final=dict(task_id=TASK,epoch_id="SS-E02",family="SS",agent_role="A4",started_at=started,fixed_at=now(),input_manifest_path=str(common),input_manifest_sha=sha(common),script_path="scripts/task016_p7_ss_e02_assay_universe.py",script_sha256=sha("scripts/task016_p7_ss_e02_assay_universe.py"),input_files_sha256={str(p):sha(p) for p in [BASE/"source_native_text_inventory.json",BASE/"A4_native_source/source_preprocessing_manifest.json"]},output_files_sha256=outputs,actual_enumerated_source_assay_rows=len(rows),source_location_row_counts=counts,explicit_Table5_numeric_zeros=82,Table4_literal_summary_cells=117,Table5_literal_numeric_cells=180,Table1_PMC4282749_actual_screen_rows=19,Table6_source_standards=25,PMC106_Table3_kinetic_parameter_cells=18,native_objects_retained=len(catalog),reported_substrate_and_mutant_screen_row_universes_enumerated=True,full_every_experiment_universe_complete=False,remaining_universe_items=pending,read_other_extractor_output=False,read_model_outcomes=False,read_future_fresh=False,evidence_eligible=False,qualified_reactions=0,approval_type="agent_delegated",human_reviewed=False,guard_built=False,model_runs=0,counts_are_not_novel_reaction_support_counts=True)
 dump("role_A4_source_assay_universe_manifest.json",final)
 print(json.dumps(dict(manifest=str(OUT/"role_A4_source_assay_universe_manifest.json"),sha256=sha(OUT/"role_A4_source_assay_universe_manifest.json"),rows=len(rows),counts=counts,zeros=zeros,qualified=0)))
if __name__=="__main__":main()
