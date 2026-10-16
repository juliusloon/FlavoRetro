"""C-E02 exposed-source design A3 and independent A4 verification, no new guard."""
from __future__ import annotations
import json,hashlib,re,unicodedata,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
from rdkit import Chem
from rdkit.Chem import Descriptors,rdMolDescriptors
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import save_json,sha_file,now
from scripts.task016_p7_structure_harness import _validated
ROOT=Path.cwd();OUT=ROOT/"outputs/task016-p7/v1/C/E02/design_source_qualification/v1"
INPUT=OUT/"common_source_input_manifest.v3.json";EXPECTED="201c28783be80daa6086b931d1b3bce6d2c3d00d8ac901c3701516aec8a9d8c1"
def ptr(p):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def load(p):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 return json.loads(p.read_text())
def rows(p):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def save(p,x):save_json(p,x,immutable=True)
def js(p,rs):
 if p.exists():raise ValueError("immutable path exists")
 write("TASK-016-P7",str(p.relative_to(ROOT)),"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rs));p.chmod(0o444)
def text(e):return " ".join("".join(e.itertext()).split()) if e is not None else None
def normalize(t):
 if t is None:return None
 t=unicodedata.normalize("NFKC",str(t)).translate(str.maketrans({"‐":"-","‑":"-","–":"-","−":"-"}))
 return re.sub(r"\s+"," ",t).strip().rstrip(".").casefold()
def canonical(s):
 m=Chem.MolFromSmiles(s)
 if m is None:raise ValueError("invalid original graph transcription")
 return Chem.MolToSmiles(m,isomericSmiles=True)
def jats(p):
 t=ET.fromstring((ROOT/p).read_bytes());am=t.find("front/article-meta");jm=t.find("front/journal-meta")
 d={}
 for e in am.findall("article-id"):
  if e.get("pub-id-type") in ("pmcid","pmid","doi"):d[e.get("pub-id-type")]=text(e)
 d.update(title=text(am.find("title-group/article-title")),journal=text(jm.find("journal-title-group/journal-title")),
  year_values=[text(e.find("year")) for e in am.findall("pub-date")],volume=text(am.find("volume")),issue=text(am.find("issue")),
  fpage=text(am.find("fpage")),lpage=text(am.find("lpage")),article_number=text(am.find("elocation-id")),
  publisher=text(jm.find("publisher/publisher-name")),
  publisher_collection=[text(e.find("meta-value")) for e in jm.findall("custom-meta-group/custom-meta") if text(e.find("meta-name"))=="pmc-collection-title"],
  author_surnames=[text(e.find("surname")) for e in am.findall("contrib-group/contrib/name")])
 d["pages"]=d["fpage"]+("-"+d["lpage"] if d["lpage"] else "") if d["fpage"] else d["article_number"]
 return t,d
class Meta(HTMLParser):
 def __init__(self):super().__init__();self.fields={}
 def handle_starttag(self,tag,attrs):
  if tag=="meta":
   a=dict(attrs);key=a.get("name") or a.get("property")
   if key and a.get("content") is not None:self.fields.setdefault(key,[]).append(a["content"])
def identity():
 if sha_file(INPUT)!=EXPECTED:raise ValueError("common raw input SHA drift")
 old=rows("outputs/task016-p7/v1/C/E01/design_source_identity_inputs.jsonl")
 sources={}
 for r in old:
  if r["pmcid"] in ("PMC6036675","PMC9700910","PMC11053098"):
   sources[r["pmcid"]]=dict(xml=r["xml"]["path"],pmc_metadata=r["meta"]["path"],epmc=r["europepmc"]["path"])
 sources["PMC11975207"]=dict(xml="data/raw/task016-p1/2026-10-06/pmc/PMC11975207-v1-0/fullTextXML.attempt-1",
  pmc_metadata="data/raw/task016-p1/2026-10-06/pmc/PMC11975207-b1b74dd0/metadata.attempt-1",
  epmc="data/raw/task016-p7/C/ffb1efc4880f42ee70913306ffb1f4525af5bcb6d1940a026fa9e071ce8deb85.attempt-1.discovery")
 output=[]
 for pid,files in sources.items():
  _,front=jats(files["xml"]);m=load(files["pmc_metadata"]);core=load(files["epmc"])["resultList"]["result"]
  index=next(i for i,r in enumerate(core) if r.get("pmcid")==pid);e=core[index];j=e["journalInfo"]
  checked={}
  pairs=dict(pmcid=(front["pmcid"],e["pmcid"]),doi=(front["doi"],e["doi"]),pmid=(front["pmid"],e["id"]),
   title=(front["title"],e["title"]),journal=(front["journal"],j["journal"]["title"]),
   volume=(front["volume"],j["volume"]),pages_or_article_number=(front["pages"],e.get("pageInfo")),
   year=(front["year_values"][0],str(e["pubYear"])),
   author_surnames=(front["author_surnames"],[a.get("lastName") for a in e.get("authorList",{}).get("author",[])]))
  for field,(a,b) in pairs.items():
   if field=="author_surnames":passed=[normalize(x) for x in a]==[normalize(x) for x in b]
   else:passed=normalize(a)==normalize(b)
   checked[field]=dict(primary=a,secondary=b,raw_equal=a==b,normalized_equal=passed,
     normalized_equal_basis="NFKC, literal hyphen glyph aliases, case, whitespace and terminal period only; no chemical/name synonym substitution")
  checked["PMC_official_index"]=dict(pmcid=m["pmcid"],doi=m["doi"],title=m["title"],
    passed=m["pmcid"]==pid and normalize(m["doi"])==normalize(front["doi"]) and normalize(m["title"])==normalize(front["title"]))
  checked["issue"]=dict(primary=front["issue"],secondary=j.get("issue"),missing_primary_preserved=front["issue"] is None,
   passed=front["issue"] is None or normalize(front["issue"])==normalize(j.get("issue")))
  passed=all(v.get("normalized_equal",v.get("passed",False)) for v in checked.values())
  output.append(dict(agent_role="A3",candidate_epoch_id="C-E02",pmcid=pid,doi=front["doi"],
   source_publication_identity_matches=passed,source_identity_verified=passed,
   raw_JATS_metadata=front,field_checks=checked,
   publisher_primary_value=front["publisher"],publisher_collection_value=front["publisher_collection"],
   publisher_secondary_value=None,publisher_cross_check_status="unavailable in EuropePMC CORE; exact Crossref429 preserved; no fabricated publisher equality",
   publisher_collection_not_legal_entity=bool(front["publisher_collection"]),
   missing_publisher_legal_entity_preserved=front["publisher"] is None,
   official_PMC_license=m.get("license_code"),is_retracted=m.get("is_retracted"),
   source_evidence_pointers=[ptr(files["xml"]),ptr(files["pmc_metadata"]),dict(**ptr(files["epmc"]),json_pointer=f"/resultList/result/{index}")],
   input_manifest_sha=EXPECTED,evidence_eligible=False,chemical_qualification_not_granted=True,human_reviewed=False))
 # Original publisher literal citation metadata and independently acquired official CORE.
 html="data/raw/task016-p7/C/8f5e15f10c169f0258aeabfc065eea54d3eb10f8045d00840646f591a3aca4e6.attempt-1.metadata"
 core_path="data/raw/task016-p7/C/b179044c5b5b846769c6570d8e5f329bab85280f4a222c193fd710ef68a7b7f3.attempt-1.discovery"
 parser=Meta();parser.feed((ROOT/html).read_text());md=parser.fields;core=load(core_path)["resultList"]["result"]
 idx=next(i for i,r in enumerate(core) if r.get("id")=="29308528");e=core[idx];ji=e["journalInfo"]
 def first(k):return md.get(k,[None])[0]
 fields=dict(doi=(first("citation_doi"),e["doi"]),title=(first("citation_title"),e["title"]),
  journal=(first("citation_journal_title"),ji["journal"]["title"]),
  volume=(first("citation_volume"),ji["volume"]),
  pages=(str(first("citation_firstpage"))+"-"+str(first("citation_lastpage")),e["pageInfo"]))
 checked={k:dict(primary=a,secondary=b,raw_equal=a==b,normalized_equal=normalize(a)==normalize(b)) for k,(a,b) in fields.items()}
 authors=md.get("citation_author",[]);surnames=[x.split()[-1] for x in authors]
 checked["author_surnames"]=dict(primary=surnames,secondary=[a.get("lastName") for a in e["authorList"]["author"]],
  normalized_equal=[normalize(x) for x in surnames]==[normalize(a.get("lastName")) for a in e["authorList"]["author"]])
 date=first("citation_publication_date") or first("citation_date");checked["year"]=dict(primary=date,secondary=e["pubYear"],
  normalized_equal=str(date)[:4]==str(e["pubYear"]))
 output.append(dict(agent_role="A3",candidate_epoch_id="C-E02",pmcid=None,doi=e["doi"],pmid=e["id"],
  source_publication_identity_matches=all(v["normalized_equal"] for v in checked.values()),
  source_identity_verified=all(v["normalized_equal"] for v in checked.values()),
  field_checks=checked,publisher_primary_value=first("citation_publisher") or first("dc.publisher"),
  publisher_primary_route="official link.springer.com publisher article landing; literal citation metadata",
  publisher_secondary_value=None,publisher_cross_check_status="EuropePMC CORE missing; not asserted equal",
  source_evidence_pointers=[ptr(html),dict(**ptr(core_path),json_pointer=f"/resultList/result/{idx}")],
  input_manifest_sha=EXPECTED,evidence_eligible=False,chemical_qualification_not_granted=True,human_reviewed=False))
 js(OUT/"A3_source_publication_identity.jsonl",output)
 save(OUT/"role_A3_manifest.json",dict(task="TASK-016-P7",agent_role="A3 Source Identity Verifier",
  candidate_epoch_id="C-E02",timestamp=now(),input_manifest_sha=EXPECTED,human_reviewed=False,
  counts=dict(processed=len(output),bibliographic_identity_passed=sum(r["source_identity_verified"] for r in output),
   publisher_second_source_available=0,publisher_missing_secondary=len(output)),
  publisher_missing_and_failed_requests_preserved=True,Crossref_failed_request_pointer=ptr(OUT/"A3_Crossref_exact_metadata_results.json"),
  evidence_eligible_granted=False,read_A5_finalgraphs=False,read_model_outcomes_for_this_verification=False,
  output_file_sha={str((OUT/"A3_source_publication_identity.jsonl").relative_to(ROOT)):sha_file(OUT/"A3_source_publication_identity.jsonl")},
  source_original_pointers=[p for r in output for p in r["source_evidence_pointers"]]))
 print(json.dumps(dict(A3_sources=len(output),matched=sum(r["source_identity_verified"] for r in output),role_pointer=ptr(OUT/"role_A3_manifest.json"))))
# These graphs are independently transcribed from the actually viewed source figures.
AGLYCONE={
 "P3R-C03":"O=c1cc(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
 "P3R-C04":"O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
 "P3R-C05":"O=c1c(O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
 "P3R-C06":"O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
 "P5R-C01":"O=C(O)c1cc(O)c(O)c(O)c1",
 "P5R-C02":"O=C(O)c1cc(O)c(OC)c(O)c1",
 "C-CHRYSIN-CH6":"O=c1cc(-c2ccccc2)oc2cc(O)cc(O)c12",
 "C-CHRYSIN-LU6":"O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
}
GLC="[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O"
GAL="[C@@H]1O[C@H](CO)[C@H](O)[C@H](O)[C@H]1O"
XYL="[C@@H]1OC[C@@H](O)[C@H](O)[C@H]1O"
PHLORETIN="O=C(CCc1ccc(O)cc1)c1c(O)cc(O)cc1O"
def source_site(m,site):
 rings=m.GetRingInfo().AtomRings()
 if site in ("C6","C8"):
  fused=next(r for r in rings if any(m.GetAtomWithIdx(i).GetAtomicNum()==8 for i in r))
  ring_o=next(m.GetAtomWithIdx(i) for i in fused if m.GetAtomWithIdx(i).GetAtomicNum()==8)
  junction=next(n.GetIdx() for n in ring_o.GetNeighbors() if sum(n.GetIdx() in r for r in rings)==2)
  aryl=next(r for r in rings if junction in r and all(m.GetAtomWithIdx(i).GetAtomicNum()==6 for i in r))
  c8=next(n.GetIdx() for n in m.GetAtomWithIdx(junction).GetNeighbors() if n.GetIdx() in aryl and sum(n.GetIdx() in r for r in rings)==1)
  if site=="C8":return c8
  c7=next(n.GetIdx() for n in m.GetAtomWithIdx(c8).GetNeighbors() if n.GetIdx() in aryl and n.GetIdx()!=junction)
  return next(n.GetIdx() for n in m.GetAtomWithIdx(c7).GetNeighbors() if n.GetIdx() in aryl and n.GetIdx()!=c8)
 anchor=next(a.GetIdx() for a in m.GetAtoms() if a.GetIsAromatic() and any(not n.GetIsAromatic() and n.GetAtomicNum()==6 and any(b.GetBondType()==Chem.BondType.DOUBLE and b.GetOtherAtom(n).GetAtomicNum()==8 for b in n.GetBonds()) for n in a.GetNeighbors()))
 ring=next(r for r in rings if anchor in r and all(m.GetAtomWithIdx(i).GetAtomicNum()==6 for i in r))
 if site=="C2":return next(n.GetIdx() for n in m.GetAtomWithIdx(anchor).GetNeighbors() if n.GetIdx() in ring and n.GetTotalNumHs()==1)
 if site=="phloretin_remaining":return next(i for i in ring if m.GetAtomWithIdx(i).GetTotalNumHs()==1)
 raise ValueError("unassigned source site")
def attach(m,site,glycan):
 i=source_site(m,site);g=Chem.MolFromSmiles(glycan);n=m.GetNumAtoms()
 rw=Chem.RWMol(Chem.CombineMols(m,g));rw.AddBond(i,n,Chem.BondType.SINGLE)
 rw.GetAtomWithIdx(n).SetNumRadicalElectrons(0);rw.GetAtomWithIdx(n).SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CCW)
 p=rw.GetMol();Chem.SanitizeMol(p);return p
def extraction():
 if sha_file(INPUT)!=EXPECTED:raise ValueError("common input SHA drift")
 inp=load(INPUT);universe=rows(inp["source_exact_reaction_universe_pointer"]["path"])
 # The full keto serialization is read directly from the authority's raw response.
 dp=inp["authoritative_donor_identity_raw_pointer"];donor_raw=load(dp["path"])["PropertyTable"]["Properties"][0]
 donor=canonical(donor_raw["SMILES"])
 donor_chain=dict(source_explicit_name="UDP-glucose",CID=donor_raw["CID"],InChI=donor_raw["InChI"],
  InChIKey=donor_raw["InChIKey"],official_raw_pointer=dp,representation="literal official raw SMILES keto; no identity from source product alone")
 output=[];partial=[];audit=[]
 for source in universe:
  rid=source["reaction_id"];site=source["site"]
  if rid.startswith("C-E02-SOURCE-FcCGT"):
   kind="GAL" if "-GAL-" in rid else "XYL"
   a=attach(Chem.MolFromSmiles(PHLORETIN),"phloretin_remaining",GAL if kind=="GAL" else XYL)
   p=attach(a,"phloretin_remaining",GLC)
   ap=Chem.MolToSmiles(a,isomericSmiles=True);pp=Chem.MolToSmiles(p,isomericSmiles=True)
   evidence=source["original_SI_pointer"]
   expected_formula="C27H34O15" if kind=="GAL" else "C26H32O14"
   locations=source["evidence_locations"]
   bond=dict(acceptor_atom=site,donor_atom="source:Glc-C1",product_atoms=[site,"source:Glc-C1"])
   measured=dict(adduct="[M+H+]+",source_calculated_mz=599.5 if kind=="GAL" else 569.5,
    source_observed_mz=599.2 if kind=="GAL" else 569.3,
    literal_source_location="SI FigS3 physical p15" if kind=="GAL" else "SI FigS8 physical p20",
    average_or_monoisotopic_basis_unknown=True,instrument_precision_unknown=True,
    low_precision_not_HR_exact_measurement=True)
   extra=dict(source_existing_glycan="beta-D-galactopyranosyl" if kind=="GAL" else "beta-D-xylopyranosyl",
    source_existing_glycan_conserved=True,source_first_glycosylation_excluded=True,
    source_forward_step="completed mono-C-Gal/Xyl substrate followed by UDP-Glc addition, second single C formation",
    site_symmetry_convention=source["site_numbering_convention"],
    additional_structure_evidence_pointer=source["original_main_Fig1_pointer"],
    source_isolated_recovery=dict(value=22 if kind=="GAL" else 31,unit="percent",
     source_location="main body//p[33]",interpretation="isolated recovery distinct from staged reaction conversion"))
  else:
   ap=canonical(AGLYCONE[rid]);p=attach(Chem.MolFromSmiles(ap),site,GLC);pp=Chem.MolToSmiles(p,isomericSmiles=True)
   evidence=source["figure_pointer"];locations=source["evidence_locations"];bond=source["bond_atoms"];extra={}
   expected_formula={"P3R-C03":"C21H20O10","P3R-C04":"C21H20O11","P3R-C05":"C21H20O11","P3R-C06":"C21H20O12",
    "P5R-C01":"C13H16O10","P5R-C02":"C14H18O10","C-CHRYSIN-CH6":"C21H20O9","C-CHRYSIN-LU6":"C21H20O11"}[rid]
   measured=None
   if rid=="P3R-C05":measured=dict(adduct="[M-H]-",source_observed_mz=447.0957,source_location="main body//p[47]")
   if rid=="C-CHRYSIN-CH6":
    measured=dict(adduct="[M+H]+",source_observed_mz=417.1166,source_calculated_mz=417.1186,
      source_location="SI TableS1 physical PDF p2",
      second_original_source_observed_mz=417.1221,second_original_source_location="SI FigS4 physical PDF p6",
      source_internal_measured_mass_difference=0.0055,resolution="unresolved independent A6 required; all source values retained",
      second_raw_source_view_pointer=ptr(OUT/"A4_original_views/CHRYSIN.SI.page6.png"))
    extra["additional_structure_evidence_pointer"]=source["SI_pointer"]
   if rid=="C-CHRYSIN-LU6":
    measured=dict(adduct="[M+H]+",source_observed_mz=449.1063,source_calculated_mz=449.1063,
      source_location="SI TableS1 physical PDF p2")
    extra["additional_structure_evidence_pointer"]=source["SI_pointer"]
   if rid in ("P3R-C03","P3R-C04"):
    # Retain endpoints; an identity database cannot repair a missing source reaction donor.
    r=dict(reaction_id=rid,agent_role="A4",candidate_epoch_id="C-E02",
      acceptor_smiles=ap,product_smiles=pp,donor_smiles=None,reference_precursors=None,
      site=site,bond_atoms=bond,sugar_identity="D-glucose",anomer_stereo="beta-D-glucopyranose",
      structure_complete=False,acceptor_product_graph_complete=True,
      source_donor_assignment_verified=False,evidence_eligible=False,
      reason="source main original and actual SI contain no explicitly assigned reaction UDP donor; GtUF6CGT1 protein identity and CID8629 identity do not supply missing source-assay donor",
      structure_evidence_pointer=evidence,evidence_location=locations,
      actual_direct_experiment_location="JATS .//body//p[30], Fig4; endpoint Fig1",
      additional_donor_absence_evidence_pointer=ptr(OUT/"C6_SI_request_result.json"),
      input_manifest_sha=EXPECTED,read_other_extractor_output=False,human_reviewed=False)
    partial.append(r);audit.append(dict(reaction_id=rid,status="deferred_source_donor_gap",schema_valid_complete=False));continue
  mol=Chem.MolFromSmiles(pp);formula=rdMolDescriptors.CalcMolFormula(mol)
  if formula!=expected_formula:raise ValueError("source independently counted atom inventory mismatch "+rid+" "+formula)
  row=dict(reaction_id=rid,agent_role="A4",candidate_epoch_id="C-E02",
   acceptor_smiles=ap,donor_smiles=donor,product_smiles=pp,reference_precursors=[ap,donor],
   site=site,bond_atoms=bond,sugar_identity="D-glucose",anomer_stereo="beta-D-glucopyranose",
   direction="acceptor+donor->product",step_count=1,evidence_location=locations,
   structure_origin="dual_independent_source_graph_transcription",structure_evidence_pointer=evidence,
   input_manifest_sha=EXPECTED,read_other_extractor_output=False,read_model_outcome_for_this_extraction=False,
   extraction_id="A4-C-E02-"+rid,independent_extraction_completed=True,
   dual_independent_reconciliation_completed=False,evidence_eligible=False,human_reviewed=False,
   source_product_formula=expected_formula,source_product_formula_basis="independently counted original source drawn atoms",
   source_product_exact_mass=Descriptors.ExactMolWt(mol),
   source_exact_mass_basis="theoretical source-graph/formula-derived consistency only; raw measured MS retained separately, never promoted to measured exact mass",
   source_measured_mass=measured,source_naming_check=True,
   source_donor_identity_chain=donor_chain,source_donor_assignment_verified=True,
   required_context=dict(mode="enzymatic",donor_name="UDP-alpha-D-glucose"),
   scope_built_or_modified=False,permanent_design_exposed=True,future_fresh_eligible=False,
   extraction_method="source original figure graph/chair/wedge transcription; source-numbered C linkage; official complete donor raw identity; no other extractor/model read")
  row.update(extra)
  if rid.startswith("P3R-C0") and site=="C8":
   row["donor_original_source_assignment"]=dict(location="JATS .//body//p[25], explicit TcCGT transfers UDP-glucose to kaempferol/quercetin",pointer=source["xml_pointer"])
  elif rid.startswith("P5R"):
   row["donor_original_source_assignment"]=dict(location="JATS .//body//p[44], in vitro 0.8mM UDP-Glc and0.4mM GA or4-OMGA",pointer=source["xml_pointer"])
  elif rid.startswith("C-CHRYSIN"):
   row["donor_original_source_assignment"]=dict(location="source mainFig2 actual UDP-glucose transfer arrow and SI FigS9 pathway",pointer=source["figure_pointer"])
  else:
   row["donor_original_source_assignment"]=dict(location="SI physical PDF p3: explicit UDP-Glc added to fully converted mono-C-Gal/Xyl phloretin; TableS1 p9",pointer=source["original_SI_pointer"])
  graphs=_validated(row)
  output.append(row);audit.append(dict(reaction_id=rid,status="complete_graph_A4_pending_A5_A6",schema_valid_complete=True,
    canonical_graph_fingerprints={k:hashlib.sha256(v.encode()).hexdigest() for k,v in graphs.items()},
    measured_mass_chemical_qualification_not_granted=True))
 js(OUT/"extractor_A4_complete.jsonl",output);js(OUT/"extractor_A4_deferred.jsonl",partial)
 save(OUT/"A4_graph_validation.json",dict(task="TASK-016-P7",input_manifest_sha=EXPECTED,checks=audit,
  schema_complete_passed=len(output),deferred_source_donor=len(partial),chemical_qualification_not_granted=True,
  all_input_raw_SHAs_verified=True,read_A5_finalgraphs=False,human_reviewed=False))
 save(OUT/"role_A4_manifest.json",dict(task="TASK-016-P7",agent_role="A4 Structure Extractor-1",
  candidate_epoch_id="C-E02",timestamp=now(),input_manifest_sha=EXPECTED,
  counts=dict(processed=10,complete_source_graph_transcriptions=len(output),deferred=len(partial),
   schema_validated=len(output),independently_A6_qualified=0),
  read_other_extractor_output=False,read_model_outcome_for_this_extraction=False,
  previously_read_exposed_E01_own_graphs_and_runtime_diagnostic=True,
  prior_source_transcription_history_retained=True,
  prior_role_label_correction_pointer=ptr("outputs/task016-p7/v1/C/E01/postfreeze_diagnostics/C3H_semantic_audit/role_label_correction.json"),
  no_current_or_future_holdout_read=True,fresh_holdout_extraction=False,scope_built_or_modified=False,
  source_evidence_pointers=[r["structure_evidence_pointer"] for r in output]+[r["structure_evidence_pointer"] for r in partial],
  outputs_SHA={str((OUT/n).relative_to(ROOT)):sha_file(OUT/n) for n in ("extractor_A4_complete.jsonl","extractor_A4_deferred.jsonl","A4_graph_validation.json")},
  mass_conflicts_and_low_precision_original_values_preserved=True,human_reviewed=False,approval_type="agent_delegated"))
 print(json.dumps(dict(A4_complete=len(output),A4_deferred=len(partial),manifest=ptr(OUT/"role_A4_manifest.json"),
  complete_rows=ptr(OUT/"extractor_A4_complete.jsonl"),deferred_rows=ptr(OUT/"extractor_A4_deferred.jsonl"))))
def main():
 inp=load(INPUT)
 for p in inp["source_original_pointers"]:
  if sha_file(ROOT/p["path"])!=p["sha256"]:raise ValueError("raw source SHA drift")
 identity();extraction()
if __name__=="__main__":main()
