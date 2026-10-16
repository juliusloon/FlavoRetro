"""Bounded A6 reconciliation of the frozen new-SS pair; no scope/fresh advancement."""
import json,re
from pathlib import Path
from decimal import Decimal
import xml.etree.ElementTree as ET
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,Descriptors
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,role_manifest
from scripts.task016_p7_c_e02_http import immutable_json
D=ROOT/"outputs/task016-p7/v1/SS/E02_design"
A=D/"new_source_A4_v1";B=D/"new_source_A5_v1";S=D/"new_source_A4_acceptor_supplement_v1"
O=D/"new_source_A6_reconciliation_v1"
def load(p):return json.loads(p.read_text())
def ptr(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def save(n,x):p=O/n;immutable_json(p,x);return p
def compact(x):return re.sub(r"\s+","",str(x))
def main():
    assert not O.exists()
    ar=A/"role_A4_fixed_manifest.json";br=B/"role_A5_manifest.json";sr=S/"role_A4_acceptor_supplement_manifest.json"
    bindings={}
    for rp,key in [(ar,"output_sha256"),(br,"all_output_files_sha256_excluding_this_role_manifest"),(sr,"output_sha256")]:
        role=load(rp);bindings.update(role[key])
        for name,h in role[key].items():assert sha_file(ROOT/name)==h,(name,"fixed output drift")
    for rp in [ar,sr]:
        for n,h in load(rp)["input_sha256"].items():assert sha_file(ROOT/n)==h,(n,"input drift")
    allinputs=[ar,br,sr]+[ROOT/n for n in bindings]
    cells=[json.loads(l) for l in (A/"A4_source_table_literal_cells.jsonl").read_text().splitlines()]
    checks=[];differences=[];records=[]
    def check(name,ok,**details):
        checks.append(dict(name=name,passed=bool(ok),**details))
    def subset(sid,table):return [x for x in cells if x["source_id"]==sid and x["table"]==table]
    # 46 independent actual assay metric literals, not 169 table/header fields.
    t1=subset("PMC6181985","Table 1");tab={(x["row"],x["column"]):x["raw_literal"] for x in t1}
    b1=load(B/"A5_PMC6181985_Table1_46_assay_cells.json")
    byenz={tab[(r,0)]:r for r in range(2,25)}
    for x in b1["cells"]:
        r=byenz[x["enzyme_literal"]];c=5 if x["metric"]=="relative_sucrose_activity" else 6
        literal=tab[(r,c)]
        nums=re.findall(r"\d+(?:\.\d+)?",literal)
        ok=compact(literal)==compact(x["literal"]) and Decimal(nums[0])==Decimal(str(x["value"]))
        if x["SD"] is not None:ok=ok and len(nums)>1 and Decimal(nums[1])==Decimal(str(x["SD"]))
        records.append(dict(table="PMC6181985 Table1",row=x["enzyme_literal"],column=x["metric"],A4=literal,A5=x["literal"],same=ok))
    check("Table1 independent assay metric literals",len(records)==46 and all(x["same"] for x in records),cells=46,table_fields_including_headers=169)
    # 43 peak rows x 3 fields. NA, ranges, zeros remain literals.
    s3={(x["row"],x["column"]):x["raw_literal"] for x in subset("PMC6181985","SI TableS3")}
    s3b=load(B/"A5_PMC6181985_SI_TableS3_43_rows.json")["rows"];s3r=[]
    for x in s3b:
        for col,key in [("retention_time_min","retention_time_literal"),("m/z","mz_literal"),("number_of_glucosyl_units","glucosyl_units_literal")]:
            v=s3[(x["name_literal"],col)];w=x[key]
            s3r.append(dict(row=x["name_literal"],column=col,A4=v,A5=w,same=compact(v)==compact(w)))
    records.extend(s3r)
    check("SI TableS3 independent peak field literals",len(s3r)==129 and all(x["same"] for x in s3r),fields=129,peaks=43,not_reaction_count=True)
    # Figure3E: source displays B with four-residue superscript. A4 records suffix;
    # A5 records B+suffix. An explicit observed typography mapping, not name guessing.
    f4=subset("PMC12611259","Figure3E")
    f5=load(B/"A5_PMC12611259_Fig3E_52_ordinal_assay_cells.json")["cells"]
    colmap={("kaempferol","UDP-glucose"):"K + Glu",("quercetin","UDP-glucose"):"Q + Glu",("kaempferol","UDP-galactose"):"K + Gal",("quercetin","UDP-galactose"):"Q + Gal"}
    fidx={(x["row"],x["column"]):x for x in f4};fr=[];crosswalk=[]
    for x in f5:
        rawlabel=x["enzyme_label_plain_projection"]
        assert rawlabel.startswith("B")
        label=compact(rawlabel[1:]);col=colmap[(x["acceptor"],x["donor"])]
        y=fidx[(label,col)]
        fr.append(dict(A4_row=y["row"],A5_row=rawlabel,column=col,A4=y["raw_literal"],A5=x["literal"],same=y["raw_literal"]==x["literal"],status_A4=y["status"],status_A5=x["status"]))
        if rawlabel not in [z["A5"] for z in crosswalk]:crosswalk.append(dict(A4=y["row"],A5=rawlabel,source="Figure3E B superscript four-residue sequence, observed root view; WT parentheses spacing"))
    records.extend(fr)
    check("Figure3E independent ordinal assay cells",len(fr)==52 and all(x["same"] for x in fr),cells=52,ND=sum(x["status_A5"]=="ND" for x in fr),no_numeric_yields_inferred=True,explicit_typographic_crosswalk=crosswalk)
    ab4={(x["row"],x["column"]):x for x in subset("PMC12611259","SI FigureS2A table")}
    ab5=load(B/"A5_PMC12611259_SI_FigS2A_66_abundance_cells.json")["cells"];abr=[]
    for x in ab5:
        y=ab4[(x["organ"],x["compound_acronym"])]
        if x["status"]=="ND":
            ok=compact(y["raw_literal"]).lower() in ["n.d.","nd","n.d"] and x["value"] is None and x["SD"] is None
        else:
            ok=Decimal(y["raw_literal"])==Decimal(str(x["value"])) and Decimal(y["raw_SD_literal"])==Decimal(str(x["SD"]))
        abr.append(dict(organ=x["organ"],compound=x["compound_acronym"],A4_literal=y["raw_literal"],A4_SD=y["raw_SD_literal"],A5_literal=x["literal_compacted"],status=x["status"],same=ok))
    records.extend(abr)
    check("SI FigS2A independent abundance values and SD",len(abr)==66 and all(x["same"] for x in abr),cells=66,ND=sum(x["status"]=="ND" for x in ab5),SD_zero=sum(x["SD"]==0 for x in ab5),mean_zero=sum(x["value"]==0 for x in ab5),not_enzyme_activity=True)
    # Full graph identity, exact stereo, formula, Standard and FixedH InChI.
    bgraphs=load(B/"A5_source_graphs_and_donor_reference.json")["graphs"]
    ak2=load(A/"PMC12611259_K2_source_drawn_atom_graph.v1.json")
    akg=load(S/"PMC12611259_Kgal_source_derived_graph.json")
    adonor=load(A/"official_donor_raw_reference_graph_inventory.json")[0]
    graphs=[]
    for name,x,y in [("K2",ak2,bgraphs[0]),("Kgal",akg,bgraphs[1]),("UDPglucose_reference",adonor,bgraphs[2])]:
        ma=Chem.MolFromSmiles(x["canonical_isomeric_SMILES"]);mb=Chem.MolFromSmiles(y["SMILES"])
        sa=Chem.MolToSmiles(ma,isomericSmiles=True);sb=Chem.MolToSmiles(mb,isomericSmiles=True)
        ia=Chem.MolToInchi(ma);ib=Chem.MolToInchi(mb)
        fa=Chem.MolToInchi(ma,options="/FixedH");fb=Chem.MolToInchi(mb,options="/FixedH")
        centers=Chem.FindMolChiralCenters(ma,includeUnassigned=True)
        potentials=[dict(atom=int(p.centeredOn),element=ma.GetAtomWithIdx(p.centeredOn).GetSymbol(),specified=str(p.specified),type=str(p.type)) for p in Chem.FindPotentialStereo(ma)]
        roundtrips={}
        for typ,m in [("SMILES",Chem.MolFromSmiles(sa)),("MolBlock",Chem.MolFromMolBlock(Chem.MolToMolBlock(ma))),("StandardInChI",Chem.MolFromInchi(ia))]:
            roundtrips[typ]=m is not None and Chem.MolToSmiles(m,isomericSmiles=True)==sa
        g=dict(name=name,A4_SMILES=sa,A5_SMILES=sb,canonical_equal=sa==sb,Standard_InChI=ia,Standard_InChI_equal=ia==ib,FixedH_InChI=fa,FixedH_InChI_equal=fa==fb,InChIKey=Chem.InchiToInchiKey(ia),formula=rdMolDescriptors.CalcMolFormula(ma),calculated_neutral_exact_mass=Descriptors.ExactMolWt(ma),heavy_atoms=ma.GetNumHeavyAtoms(),bonds=ma.GetNumBonds(),carbon_stereocenters=len(centers),unassigned_carbon_stereocenters=sum(c=="?" for _,c in centers),potential_stereo=potentials,roundtrips=roundtrips,actual_assay_physical_species="unknown; reference/literal representations not normalized")
        graphs.append(g);check(name+" full independent graph reconciliation",sa==sb and ia==ib and fa==fb and all(roundtrips.values()) and not g["unassigned_carbon_stereocenters"])
    # Two unspecified potential P centers are a diagnostic, not carbon-stereo absence.
    check("UDPglucose reported-name to authoritative complete reference",adonor["raw_property"]["CID"]==8629 and adonor["raw_property"]["InChIKey"]==graphs[2]["InChIKey"],actual_salt_counterion_hydrate_unknown=True,potential_P_is_not_automatic_gate=True,source_chain=adonor["source_chain"])
    # Compare source tiers without converting access failures to chemical negatives.
    da=load(A/"A4_complete_12_source_dispositions.json")["dispositions"];db=load(B/"A5_complete_12_source_dispositions.json")["dispositions"]
    aids={x["source_id"]:x for x in da};bids={x["source_id"]:x for x in db};dispositions=[]
    check("12 source dispositions conserved",set(aids)==set(bids) and len(aids)==12)
    for sid,x in aids.items():
        y=bids[sid]
        atier="fulltext_with_SI" if x["valid_fulltext_originals"] else ("SI_only_primary_body_missing" if x["public_attachment_count"] else "metadata_abstract_only_access_deferred")
        dispositions.append(dict(source_id=sid,A4_raw_disposition=x["A4_disposition"],A4_structural_tier=atier,A5_tier=y["source_tier"],tier_agree=atier==y["source_tier"],A4_pending=x["pending"],A5_raw_disposition=y,chemical_absence_inferred=False))
    check("source availability tiers agree",all(x["tier_agree"] for x in dispositions),full=3,SI_only=2,metadata_only=7)
    # Actual source link and parent-ion transcription sanity, preserving conflicts.
    xml=ROOT/"data/raw/task016-p7/SS/353d259fb942119acf91815dc6c6f29696354614a378d8cbccbcba0d4e30e3f6.attempt-1.xml"
    rt=ET.parse(xml).getroot();ps=rt.findall(".//body//p")
    evidence=[dict(locator="body paragraph "+str(i),literal="".join(ps[i-1].itertext())) for i in [10,16,27,28,48]]
    p16=evidence[1]["literal"]
    check("actual direct Kgal UDPglucose K2 source relation","using K-gal and UDP-glucose" in p16 and "2″" in p16 and "79-A did not" in p16,root_viewed_Fig2E=True,root_viewed_SI_S1B_full_graph=True)
    product=graphs[0];acceptor=graphs[1]
    check("full product minus acceptor formula residue",product["formula"]=="C27H30O16" and acceptor["formula"]=="C21H20O11" and abs(product["calculated_neutral_exact_mass"]-acceptor["calculated_neutral_exact_mass"]-162.05282342)<1e-6,net_residue="C6H10O5",terminal_Glu1_to_retained_GalO2_explicit=True,linkage_bonds=[b for b in ak2["bonds"] if "bridgeO2" in [b["from"],b["to"]]])
    proton=1.007276466621
    parent_checks=[dict(source_literal=v,ion="[M+H]+",calculated_from_neutral_graph=product["calculated_neutral_exact_mass"]+proton,delta_Da=float(v)-(product["calculated_neutral_exact_mass"]+proton),within_existing_0_01_Da_transcription_sanity=abs(float(v)-(product["calculated_neutral_exact_mass"]+proton))<.01) for v in ["611.1594","611.1597"]]
    check("parent masses within existing transcription sanity",all(x["within_existing_0_01_Da_transcription_sanity"] for x in parent_checks),not_analytical_QC=True)
    # No product standard/NMR universal requirement. Evaluate the actual published chain.
    support=dict(support_id="SS-DESIGN-PMC12611259-Kgal-O2-UDPglucose-K2",source_id="PMC12611259",doi="10.1093/plphys/kiaf556",source_publication_identity=ptr(D/"new_source_A3_identity_v3/role_A3_manifest.json") if (D/"new_source_A3_identity_v3/role_A3_manifest.json").exists() else None,source_relation="recombinant SlUGT79B-B Kgal + UDPglucose -> K2; 79-A negative",acceptor_full_graph=acceptor,product_full_graph=product,donor_complete_reference_graph=graphs[2],donor_physical_species_unknown=True,acceptor_aglycone_site="flavonol 3-O-beta-D-galactopyranoside",acceptor_reaction_site="Gal O2 / 2-double-prime oxygen",new_bond="terminal beta-D-Glcp anomeric C1 to retained beta-D-Galp O2",original_figures=["Figure1C","Figure2E","SI FigureS1B"],source_assigned_identity_chain=["body10 isolated plant peak1 parent MS and fragments", "retention-time and UV match against Petunia KgalGlu extract, no authentic pure K2 standard", "SI S1B full graph explicitly labeled K2", "body16 and Figure2E enzyme product explicitly labeled same K2"],measurement_class="reported positive enzymatic product with source-linked full structure",numeric_yield=None,qualified_for_design_source_support=True,qualification_authority="A6 agent_delegated source/reaction qualification; not independent chemical validation or human review",scope_stratum="flavonol3-O-beta-D-Gal / GalO2 / UDPglucose -> terminal beta-D-Glc",distinct_acceptors_this_stratum=1,scope_support_floor_met=False,merged_with_apigenin7-O-glucose_UDPapiose_scope=False,future_fresh_eligible=False,runtime_executable_verified=False,not_new_fresh=True)
    pending=["Additional second distinct acceptor within each exact SS scope stratum", "No SS G2/G3/G4 executable scope has been established", "Qgal->Q2 author claim in paragraph27 retained; whole pollen Figure6D donor/step count unknown; do not promote to isolated79B assay full-link qualification", "Other two primary sources lack exact SS product linkage/site/stereo for the inspected candidate contexts", "Fg4 SI positives retain missing primary donor/reaction provenance; Fg1 sequence-only SI", "Other7 sources metadata/abstract-only; access remains deferred", "Complete plotted screening/reaction universe is not fully independently extracted; this is a bounded reconciliation, not complete chemical acquisition round", "928 expression cells and other nonreaction tables retained; outside this bounded four-table pair reconciliation"]
    conflicts=[
      dict(field="K2 parent",literals=["611.1594 body10","611.1597 body48","610.1521 author-inferred neutral"],computed_neutral=product["calculated_neutral_exact_mass"],disposition="preserve all; parent passes existing0.01Da transcription sanity only"),
      dict(field="fragment",literals=["449.1073 body10","465.1009 SI FigureS1A"],disposition="unresolved conflict; no correction or pretend fragment QC; source full product drawing and direct relation independently retained"),
      dict(field="Figure2F caption monohexose",literals=["Kgal referred to as glucoside in caption","body16 Kgal/Gal graph and Figure2E"],disposition="retain wording conflict; do not change Gal to Glc"),
      dict(field="actual species",literals=["neutral SI S1B K2","O1-protonated S1A monohexose alternate"],disposition="separate graphs; no automatic neutralization or actual assay salt claim"),
      dict(field="blindness",literals=["A4 and A5 fixed independently before A6","A4 Kgal supplement requested by root after fixedA4 using source-derived cleavage instructions, without sharing A5 graph"],disposition="coordination disclosed; no stronger blind claim")
    ]
    tablep=save("independent_table_value_reconciliation.json",dict(task=TASK,created_at=now(),records=records,checked_fields=len(records),assay_metric_cells=46,ordinal_cells=52,abundance_cells=66,peak_fields=129,raw_literal_differences=differences,zero_not_missing=True,ND_not_zero=True,counts_not_distinct_reactions=True))
    graphp=save("independent_graph_reconciliation.json",dict(graphs=graphs,neutral_to_protonated_not_normalized=True,source_alternate_graph=ptr(A/"PMC12611259_S1_monohexose_ion_source_graph.json"),graph_comparison_is_not_new_chemical_validation=True))
    disp=save("complete_12_source_dispositions_reconciliation.json",dict(dispositions=dispositions,source_qualified_design_supports=1,chemical_absence_rejections=0,complete_chemical_round=False))
    evp=save("actual_primary_source_identity_reaction_graph_mass_chain.json",dict(original_pointer=ptr(xml),evidence=evidence,root_actual_views=[ptr(ROOT/"data/raw/task016-p7/SS/e49e766f0b61ac73aed7e0e8722c7e94900ca525078b414ae7ce6743ac79b0c4.attempt-1.attachment"),ptr(ROOT/"data/raw/task016-p7/SS/31836d0ffa6f0a9e2e31ecef645d30a7ff48db0fcbe904d3053deca4f4ec49bf.attempt-1.attachment"),ptr(B/"images/PMC126_SI_p1_neutral_complete_v2.png")],parent_mass_checks=parent_checks,conflicts=conflicts,not_assay_QC=True))
    chk=save("bounded_reconciliation_checks.json",dict(checks=checks,passed=sum(x["passed"] for x in checks),failed=sum(not x["passed"] for x in checks),unprocessed=pending,zero_misclassified_as_missing=0))
    assert all(x["passed"] for x in checks),[(x["name"]) for x in checks if not x["passed"]]
    sp=save("qualified_design_source_support.json",support)
    summary=save("A6_summary.json",dict(task=TASK,created_at=now(),approval_type="agent_delegated",human_reviewed=False,independent_fixed_A4_A5_core_graphs=2,independent_full_donor_reference_graph=1,new_qualified_design_support_records=1,new_distinct_acceptor_within_new_flavonol3Gal_scope=1,old_apigenin7Glc_acceptor_remains_separate=1,any_scope_has_two_distinct_qualified_acceptors=False,SS_G2_created=False,SS_fresh_admitted=0,C_fresh_admitted=0,scientific_ABE_cells=0,scientific_metrics=None,source_saturation=False,complete_chemical_round=False,checks=ptr(chk),support=ptr(sp),pending=pending,outputs=[ptr(p) for p in [tablep,graphp,disp,evp,chk,sp]],physical_HTTP=0,no_whole_NMR_standard_purified_enzyme_new_gate=True))
    allinputs.extend([xml,Path(__file__)])
    # Role manifest only binds successful bounded result; scientific gaps stay pending.
    rp=O/"role_A6_manifest.json"
    role=role_manifest("A6 new SS source/graph/value reconciler","SS-E02-design",allinputs,[tablep,graphp,disp,evp,chk,sp,summary],dict(processed=12,passed=1,rejected=0,pending=11),unprocessed=pending,read_holdout=False,read_model_outcome=False)
    role.update(approval_type="agent_delegated",human_reviewed=False,complete_chemical_round=False,source_saturation=False,fresh_admitted=0,SS_G2_created=False)
    immutable_json(rp,role)
    print(json.dumps(dict(summary=ptr(summary),role=ptr(rp),checks=len(checks),qualified_design_supports=1,SS_G2=False,fresh=0),ensure_ascii=False))
if __name__=="__main__":main()
