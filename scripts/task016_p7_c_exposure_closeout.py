"""A1 permanent exposure closeout and source-first design raw inputs; no scope build."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET
from rdkit import Chem
from scripts.operate import write, event
from scripts.task016_p7_orchestrate import now, sha_file, save_json
ROOT=Path.cwd(); TASK="TASK-016-P7"; BASE=ROOT/"outputs/task016-p7/v1/C/E01"
OUT=BASE/"permanent_exposure_closeout_v1"
DESIGN=BASE/"source_scout_next_epoch/design_inputs_v1"
inputs={}; raw={}
def rel(p):return str(Path(p).relative_to(ROOT))
def bind(p):
 p=Path(p)
 if not p.is_absolute():p=ROOT/p
 s=sha_file(p);inputs[rel(p)]=s
 return {"path":rel(p),"sha256":s}
def read(p):
 q=ROOT/p if not Path(p).is_absolute() else Path(p)
 bind(q);return json.loads(q.read_text())
def rows(p):
 q=ROOT/p if not Path(p).is_absolute() else Path(p)
 bind(q);return [json.loads(t) for t in q.read_text().splitlines() if t.strip()]
def pointers(v):
 found={}
 def visit(x):
  if isinstance(x,list):
   for y in x:visit(y)
  elif isinstance(x,dict):
   if x.get("path") and x.get("sha256"):
    p=ROOT/x["path"]
    if p.exists():
     if sha_file(p)!=x["sha256"]:raise ValueError("pointer drift "+str(p))
     inputs[x["path"]]=x["sha256"]
     if x["path"].startswith("data/raw/"):raw[x["path"]]=x["sha256"]
     found[x["path"]]=x["sha256"]
    else:raise ValueError("missing pointer "+str(p))
   for y in x.values():visit(y)
 visit(v);return [{"path":p,"sha256":s} for p,s in sorted(found.items())]
def save(p,v):save_json(p,v,immutable=True)
def jsonl(p,rs):
 if p.exists():raise RuntimeError("immutable exists "+str(p))
 write(TASK,rel(p),"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rs))
 p.chmod(0o444)
def tokens(pid=None,doi=None,pmid=None):
 return sorted(set(([f"article:{pid}"] if pid else [])+([f"doi:{doi.lower()}"] if doi else [])+([f"pmid:{pmid}"] if pmid else [])))
def object_identity(row):
 h=row.get("source_hint",row)
 return h.get("pmcid"),h.get("doi") or h.get("DOI"),h.get("pmid")
def jats_ids(p):
 rt=ET.fromstring((ROOT/p).read_bytes());d={}
 for e in rt.findall(".//article-meta/article-id"):
  k=e.get("pub-id-type");v="".join(e.itertext()).strip()
  if k in ("pmcid","pmc"):d["pmcid"]=v if v.startswith("PMC") else "PMC"+v
  elif k in ("doi","pmid"):d[k]=v
 return d
def main():
 if OUT.exists() or DESIGN.exists():raise RuntimeError("immutable package exists")
 guard=ROOT/"flavoretro/glycoside_scope_c_v7.py";bank=BASE/"scope_bank.json";sm=BASE/"scope_manifest.json"
 before={rel(p):sha_file(p) for p in (guard,bank,sm)}
 assert before[rel(guard)]=="564a24b0d7bc1b64f8a7c755ef9316c08ec97b3b58a3eb65ca06b810f86e18f0"
 assert before[rel(sm)]=="79cb657bfb9eacac10fe976485793c43d3dfdcabe045bd436f181c6a0d192de0"
 for p in before:bind(ROOT/p)
 inherited=bind(ROOT/"outputs/task016-p7/v1/exposure_ledger.jsonl")
 bind(ROOT/"outputs/task016-p7/v1/historical_exposure_inventory.json")
 http=rows("outputs/task016-p7/v1/C/http_ledger.jsonl")
 plan=rows("outputs/task016-p7/v1/C/acquisition_plan.jsonl")
 collision=read(BASE/"http_audit/request_id_collision_v1/request_id_alias_resolution.json")
 # Snapshot physical events, preserving the historical ID collision.
 jsonl(OUT/"acquisition_plan.snapshot.jsonl",plan)
 jsonl(OUT/"http_ledger.snapshot.jsonl",http)
 source_map={}; reaction_records=[];timeline=[];meta_events=[];g5=[]
 def source(pid,doi=None,pmid=None,kind="chemical",reason=None,pointer=None):
  key=pid or ("doi:"+doi.lower() if doi else "pmid:"+str(pmid))
  s=source_map.setdefault(key,dict(source_id=key,pmcid=pid,doi=doi,pmid=pmid,
    exposure_kind=kind,actual_original_chemical_review=True,permanent_design_exposed=True,
    future_fresh_eligible=False,human_reviewed=False,source_identity_qualification_not_claimed=True,
    source_tokens=[],closure_tokens=[],review_events=[],raw_evidence_pointers=[]))
  if doi:s["doi"]=doi
  if pmid:s["pmid"]=pmid
  s["source_tokens"]=tokens(s["pmcid"],s["doi"],s["pmid"])
  s["closure_tokens"]=[f"closure:{pid}" if pid else f"closure:doi:{doi.lower()}"]
  if pid=="PMC6064065":s["closure_tokens"]=["closure:PMC6036675"]
  if reason:s["review_events"].append(reason)
  if pointer:
   pointers(pointer)
   if pointer not in s["raw_evidence_pointers"]:s["raw_evidence_pointers"].append(pointer)
  return s
 # Current chemistry actually inspected by A4.
 for roundid in ("R1","R2"):
  review_path=BASE/f"fresh/{roundid}/A4_source_review/A4_source_chemical_dispositions.jsonl"
  reviews=rows(review_path);rolepath=review_path.parent/"role_A4_source_review_manifest.json"
  role=read(rolepath);pointers(role)
  intakepath=BASE/f"stages/batches/{roundid}/fresh_source_input_manifest.json"
  intake=read(intakepath);pointers(intake)
  acq=read(BASE/f"fresh/{roundid}/article_acquisition.json")
  hints={x["pmcid"]:x["source_hint"] for x in acq}
  for row in reviews:
   h=hints[row["pmcid"]];ptr=row["structure_evidence_pointer"]
   source(row["pmcid"],h.get("doi"),h.get("pmid"),reason=dict(
    type="source_chemistry_review",round_id=roundid,recorded_review_completion=role.get("timestamp"),
    first_read_timestamp_exact=None,reason=row["reason"],proposal=row["source_disposition_proposal"],
    review_pointer=bind(review_path),role_manifest_pointer=bind(rolepath)),pointer=ptr)
   pointers(row)
   reaction_records.append(dict(record_type="source_level_chemical_inspection",
    pmcid=row["pmcid"],reaction_id=None,contains_final_graphs=False,
    actual_original_chemistry_read=True,permanent_design_exposed=True,future_fresh_eligible=False,
    evidence_locations=row.get("evidence_locations"),review_pointer=bind(review_path),
    reason=row["reason"],evidence_eligible_not_claimed=True))
  timeline.append(dict(event_type="A4_source_review_completed",round_id=roundid,
   timestamp=role.get("timestamp"),timestamp_basis="immutable role manifest completion; exact first-read unknown",
   inspected_sources=[r["pmcid"] for r in reviews],input_frozen_at=intake.get("created_at"),
   pointers=[bind(rolepath),bind(review_path),bind(intakepath)]))
 # Original E01 design: 8 read reactions, including explicit deferred benz/mac.
 design_input=read(BASE/"design_source_input_manifest.json")
 design_role=read(BASE/"role_A4_design_manifest.json");pointers(design_role);pointers(design_input)
 for r in design_input["objects"]:
  ids=jats_ids(r["xml_pointer"]["path"])
  source(r["pmcid"],ids.get("doi"),ids.get("pmid"),reason=dict(type="historical_E01_design_original_review",
   reaction_id=r["reaction_id"],first_read_timestamp_exact=None,
   original_design_input_created_at=design_input["created_at"],role_manifest_pointer=bind(BASE/"role_A4_design_manifest.json")),
   pointer=r["xml_pointer"])
  source_map[r["pmcid"]]["raw_evidence_pointers"].append(r["figure_pointer"])
  reaction_records.append(dict(record_type="design_source_reaction_inspection",reaction_id=r["reaction_id"],
   pmcid=r["pmcid"],site=r["site"],source_evidence_pointers=[r["xml_pointer"],r["figure_pointer"]],
   structure_complete_not_claimed=True,permanent_design_exposed=True,future_fresh_eligible=False))
 own_graph_inputs=[(BASE/"design_extractor_A4.jsonl",None),
  (BASE/"fresh/alternate/A4_WASABI_product_graphs.jsonl","10.1007/s10529-021-03165-3"),
  (BASE/"fresh/alternate/A4_CHRYSIN/extractor_A4.jsonl","10.1007/s00253-017-8694-6")]
 for p,doi in own_graph_inputs:
  rr=rows(p)
  for i,r in enumerate(rr,1):
   pointers(r);cid=r.get("reaction_id");smi=r.get("product_smiles")
   graph={}
   for k in ("acceptor_smiles","donor_smiles","product_smiles"):
    v=r.get(k);m=Chem.MolFromSmiles(v) if v else None
    canonical=Chem.MolToSmiles(m,isomericSmiles=True) if m else None
    graph[k]=dict(raw_value=v,canonical_isomeric_smiles=canonical,
      canonical_sha256=hashlib.sha256(canonical.encode()).hexdigest() if canonical else None)
   reaction_records.append(dict(record_type="own_A4_molecular_endpoint_inspection",reaction_id=cid,
    source_doi=r.get("source_doi") or doi,site=r.get("site"),molecular_endpoints=graph,
    read_other_extractor_output=False,independent_qualification_not_claimed=True,
    permanent_design_exposed=True,future_fresh_eligible=False,
    record_pointer=dict(**bind(p),line_number=i)))
  if doi:
   pid=None;pmid="34302563" if "03165" in doi else "29308528"
   rp=BASE/"fresh/alternate/role_A4_WASABI_manifest.json" if "03165" in doi else BASE/"fresh/alternate/A4_CHRYSIN/role_A4_manifest.json"
   role=read(rp);pointers(role)
   for ep in role["source_evidence_pointers"]:source(pid,doi,pmid,reason=None,pointer=ep)
   source_map["doi:"+doi]["review_events"].append(dict(type="A4_endpoint_transcription",
     reaction_ids=[r["reaction_id"] for r in rr],recorded_review_completion=role.get("timestamp"),
     first_read_timestamp_exact=None,role_manifest_pointer=bind(rp),review_pointer=bind(p)))
   timeline.append(dict(event_type="A4_endpoint_transcription_completed",timestamp=role.get("timestamp"),
    source_doi=doi,reaction_ids=[r["reaction_id"] for r in rr],
    timestamp_basis="immutable A4 role manifest completion; exact first-read unknown",pointer=bind(rp)))
 # Additional source molecules actually inspected in AbCGT SI; no fabricated full structures.
 ab=read(BASE/"stages/batches/R1_ATTACHMENTS/attachment_intake.json");pointers(ab)
 for ep in ab["objects"]:source("PMC12844164",pointer={"path":ep["path"],"sha256":ep["sha256"]})
 for compound,description in [
  ("1-3a","chalcone C product outside frozen core"),
  ("1-6a","acacetin C-hexoside; exact C6 versus C8 bond unresolved"),
  ("1-4a","chrysin glycoside retains both source aromatic H6/H8; O-linked"),
  ("1-11a","methoxyflavone glycoside retains both source aromatic H6/H8; O-linked"),
  ("2-1a","xanthone 5-O-glucoside explicitly assigned in SI Figure S8")]:
  reaction_records.append(dict(record_type="source_named_product_inspection",pmcid="PMC12844164",
   source_compound_id=compound,description=description,full_structures_not_encoded=True,
   permanent_design_exposed=True,future_fresh_eligible=False,
   review_pointer=bind(BASE/"fresh/R1/A4_source_review/A4_source_chemical_dispositions.jsonl")))
 conflict=read(BASE/"source_internal_conflicts.json");pointers(conflict)
 for ep in (conflict["SI_pointer"],conflict["main_figure_pointer"]):source("PMC11480083",pointer=ep)
 # Runtime investigation was a separate role, with the original incorrect A7 label retained.
 corrected=read(BASE/"postfreeze_diagnostics/C3H_semantic_audit/role_label_correction.json")
 pointers(corrected)
 timeline.append(dict(event_type="runtime_diagnostic_role_label_correction",timestamp=corrected["timestamp"],
  actual_role=corrected["actual_role"],read_holdout=True,read_model_outcome=True,
  scope_built_or_modified=False,pointer=bind(BASE/"postfreeze_diagnostics/C3H_semantic_audit/role_label_correction.json")))
 boundary=read(BASE/"boundary_plan.json")
 for r in boundary["controls"]:
  m=Chem.MolFromSmiles(r["target"]);can=Chem.MolToSmiles(m,isomericSmiles=True) if m else None
  reaction_records.append(dict(record_type="registered_design_fixture_inspection",
    fixture_only=True,source_evidence=False,control_id=r["control_id"],target=r["target"],
    canonical_isomeric_smiles=can,permanent_design_exposed=True,future_fresh_eligible=False,
    plan_pointer=bind(BASE/"boundary_plan.json")))
 # Prepare permitted next-epoch raw-only design input, 6 original supports + 2 FcCGT.
 phl_xml=Path("data/raw/task016-p1/2026-10-06/pmc/PMC11975207-v1-0/fullTextXML.attempt-1")
 phl_si=Path("data/raw/task016-p1/2026-10-06/pmc/PMC11975207-v1-1/supplement.attempt-1")
 phl_meta=Path("data/raw/task016-p1/2026-10-06/pmc/PMC11975207-b1b74dd0/metadata.attempt-1")
 phl_ptrs=[bind(ROOT/p) for p in (phl_xml,phl_si,phl_meta)]
 for ep in phl_ptrs:source("PMC11975207","10.1002/bit.28948","39918272",
   reason=dict(type="historical_design_source_input_prepare",read_at_recorded=now(),
    future_design_only=True,not_new_holdout_extraction=True),pointer=ep)
 # SI raw rendered without editing source images.
 rendered=[]
 for page in (14,16,18,21,23):
  target=DESIGN/f"PMC11975207.SI.page{page}.png"
  target.parent.mkdir(parents=True,exist_ok=True)
  event(TASK,"derive_source_view",input_path=str(phl_si),input_sha256=sha_file(ROOT/phl_si),
        physical_pdf_page=page,output_path=rel(target))
  subprocess.run(["pdftoppm","-f",str(page),"-l",str(page),"-singlefile","-scale-to","2500",
   "-png",str(ROOT/phl_si),str(target.with_suffix(""))],check=True,stdout=subprocess.DEVNULL)
  target.chmod(0o444);rendered.append(dict(**bind(target),physical_pdf_page=page,
   original_pdf_pointer=bind(ROOT/phl_si),derivation="pdftoppm raw PDF page, no structure redraw"))
 universe=[]
 name_map={"P3R-C03":("apigenin","flavone C6 with explicit pyrone C3-H"),
  "P3R-C04":("luteolin","flavone C6 with explicit pyrone C3-H"),
  "P3R-C05":("kaempferol","flavonol C8 with explicit pyrone C3-OH"),
  "P3R-C06":("quercetin","flavonol C8 with explicit pyrone C3-OH"),
  "P5R-C01":("gallic acid","gallic acid aryl C2; C2/C6 source symmetry"),
  "P5R-C02":("4-O-methylgallic acid","4-O-methylgallic acid aryl C2; C2/C6 source symmetry")}
 for r in design_input["objects"]:
  if r["reaction_id"] not in name_map:continue
  name,range_name=name_map[r["reaction_id"]]
  v={k:r[k] for k in ("reaction_id","pmcid","site","bond_atoms","evidence_locations","figure_pointer","xml_pointer","sugar_identity","anomer_stereo")}
  v.update(source_acceptor_name=name,proposed_source_range=range_name,
    donor_source_name="UDP-alpha-D-glucose",design_only=True,new_epoch_qualified=False,
    qualification="renewed independent raw-source A3/A4/A5/A6 required; E01 historical qualification retained",
    permanent_design_exposed=True,future_fresh_eligible=False)
  universe.append(v)
 for sugar,pnum,sifigs,pages in (
  ("galactose",17,["S3","S4","S5","S6"],[15,16,17,18]),
  ("xylose",20,["S8","S9","S10","S11"],[20,21,22,23])):
  rid="C-E02-SOURCE-FcCGT-"+("GAL" if sugar=="galactose" else "XYL")+"-SECOND-GLC"
  v=dict(reaction_id=rid,pmcid="PMC11975207",doi="10.1002/bit.28948",
   source_acceptor_name=f"3'-C-beta-{sugar[:3]}osyl phloretin" if sugar=="galactose" else "3'-C-beta-xylosyl phloretin",
   donor_source_name="UDP-glucose",added_sugar_name="beta-D-glucopyranose",
   source_product_name="3'-C-beta-galactosyl-5'-C-beta-glucosyl phloretin" if sugar=="galactose" else "3'-C-beta-glucosyl-5'-C-beta-xylosyl phloretin",
   site="source:unsubstituted opposite C3prime/C5prime",site_numbering_convention=
    "Source p20 explicitly symmetric phloroglucinol ring; retain existing C-glycan and assign newly formed bond to opposite unsubstituted carbon. Source product conventional naming may swap 3prime/5prime labels.",
   donor_anomeric_site="source:Glc-C1",required_single_step=
    "Start with fully specified mono-C-glycosyl phloretin + UDP-glucose; retain staged second step only, exclude full two-step phloretin-to-diglycoside trajectory",
   proposed_source_range="phloretin second C-glucosylation with conserved pre-existing beta-galactosyl or beta-xylosyl residue",
   original_xml_pointer=bind(ROOT/phl_xml),original_SI_pointer=bind(ROOT/phl_si),
   official_metadata_pointer=bind(ROOT/phl_meta),
   evidence_locations=[f"body//p[{pnum}]","body//p[16]","SI physical PDF p3 enzyme activity assays","SI p9 TableS1"]+[f"SI {fig} physical PDF p{page}" for fig,page in zip(sifigs,pages)],
   stereo_status="requires independent raw source figure and NMR transcription; not inferred from historical encoded SMILES",
   design_only=True,new_epoch_qualified=False,permanent_design_exposed=True,future_fresh_eligible=False)
  if sugar=="galactose":v["source_acceptor_name"]="3'-C-beta-galactosyl phloretin"
  universe.append(v)
 jsonl(DESIGN/"source_exact_reaction_universe.jsonl",universe)
 raw_input=dict(task=TASK,role="A1 Source Scout",created_at=now(),candidate_next_epoch="C-E02",
  origin_epoch="C-E01",status="design_input_only; not epoch initialized; no scope constructed",
  contains_final_graphs=False,source_exact_reaction_universe_pointer=bind(DESIGN/"source_exact_reaction_universe.jsonl"),
  reaction_ids=[r["reaction_id"] for r in universe],reaction_count=8,
  range_universe=[
   dict(range_id="flavone_C6_C3H",reactions=["P3R-C03","P3R-C04"],source_acceptor_names=["apigenin","luteolin"],
    intended_semantic_boundaries=["C3-H required","C3-OH outside this declared subclass"],formal_preregistered=False),
   dict(range_id="flavonol_C8_C3OH",reactions=["P3R-C05","P3R-C06"],source_acceptor_names=["kaempferol","quercetin"],
    intended_semantic_boundaries=["C3-OH required","C3-H outside this declared subclass"],formal_preregistered=False),
   dict(range_id="gallic_C2",reactions=["P5R-C01","P5R-C02"],source_acceptor_names=["gallic acid","4-O-methylgallic acid"],formal_preregistered=False),
   dict(range_id="phloretin_second_CGlc",reactions=[r["reaction_id"] for r in universe[-2:]],
    source_acceptor_names=[r["source_acceptor_name"] for r in universe[-2:]],
    intended_semantic_boundaries=["existing C-glycan conserved","source single second formation only","no bare phloretin admitted by this second-step range"],formal_preregistered=False)],
  authoritative_donor_identity_raw_pointer=bind(ROOT/"data/raw/task016-p7/root/udp-glucose-attempt-1.json"),
  inherited_raw_design_input_pointer=bind(BASE/"design_source_input_manifest.json"),
  source_original_pointers=sorted({p["path"]:p for r in universe for p in pointers(r) if p["path"].startswith("data/raw/")}.values(),key=lambda p:p["path"]),
  source_rendered_original_views=rendered,
  explicit_next_gates=["root formal E01 expose/invalidate first","independent A3 publication identity","A4/A5 independently transcribe same immutable original source inputs","A6 molecule/donor/site/stereo reconciliation","A7 new scope and boundary universe only after independent qualification","G3/G4 freeze before next-epoch fresh chemistry"],
  scope_built_or_modified=False,read_other_extractor_output=False,human_reviewed=False,approval_type="agent_delegated")
 # Raw manifest contains no final graph serializations, template SMARTS or guard rules.
 banned={"acceptor_smiles","product_smiles","donor_smiles","smarts","mandatory_core_query"}
 def check(v):
  if isinstance(v,dict):
   assert not (set(v)&banned),set(v)&banned
   for x in v.values():check(x)
  elif isinstance(v,list):
   for x in v:check(x)
 check(universe);check(raw_input)
 save(DESIGN/"design_source_input_manifest.json",raw_input)
 # Full discovery event universe, preserving metadata-only versus original chemistry reads.
 for rnd in ("R1","R2","R3"):
  dp=BASE/f"fresh/{rnd}/source_dispositions.jsonl";discovered=rows(dp)
  queryplan=read(BASE/f"fresh/{rnd}/query_plan.json");routes={q["query_id"]:q["route"] for q in queryplan["queries"]}
  for i,r in enumerate(discovered,1):
   pid,doi,pmid=object_identity(r)
   chemically_inspected=bool(pid in source_map or ("doi:"+doi.lower() if doi else None) in source_map)
   meta_events.append(dict(event_type="metadata_discovery",round_id=rnd,query_id=r["query_id"],
     route=routes[r["query_id"]],discovered_at=r.get("discovered_at"),source_id=r["record_id"],
     pmcid=pid,doi=doi,pmid=pmid,title=r["source_hint"].get("title"),
     source_tokens=tokens(pid,doi,pmid),metadata_only_event=True,
     source_had_original_chemical_read_elsewhere=chemically_inspected,
     historical_source_exposed=r["historical_source_exposed"],
     source_eligibility=False,raw_pointer=r["raw_pointer"],
     original_discovery_row_pointer=dict(**bind(dp),line_number=i)))
   pointers(r["raw_pointer"])
  for name in ("query_plan.json","query_execution.jsonl","query_audit.json","round_manifest.json",
   "article_plan.json","article_acquisition.json","identifier_resolution_plan.json","identifier_resolution_results.json"):
   p=BASE/f"fresh/{rnd}/{name}"
   if p.exists():bind(p)
 # Batch manifests are named explicitly; do not read any independent second extractor outputs.
 for batch in ("R1","R2","R3","R1_ATTACHMENTS","WASABI_PUBLIC_SI","CHRYSIN_PUBLIC_SI",
  "ACS_PUBLIC_SI","ACS_PUBLIC_SI_RETRY2","ACS_PUBLIC_API","TROLLIUS_PUBLIC_SI"):
  folder=BASE/"stages/batches"/batch
  gp=folder/"G5_FRESH_HOLDOUT_ACQUIRE.json"
  if gp.exists():g5.append(bind(gp))
  ip=folder/("attachment_intake.json" if batch=="R1_ATTACHMENTS" else "fresh_source_input_manifest.json")
  if ip.exists():pointers(read(ip))
 for h in http:
  pointers({"path":h["path"],"sha256":h["sha256"]})
  timeline.append(dict(event_type="observable_HTTP_event",timestamp=h.get("started_at"),
   finished_at=h.get("finished_at"),source_request_id=h["attempt_id"],url=h["url"],
   source_phase=h["phase"],kind=h["kind"],status=h["status"],HTTP_status=h["status_code"],
   bytes=h["bytes"],raw_pointer={"path":h["path"],"sha256":h["sha256"]},
   timing_is_acquisition_not_chemical_read=True,
   duplicate_legacy_id_requires_alias_resolution=h["attempt_id"]=="C-HTTP-00111"))
 jsonl(OUT/"chemical_source_exposures.jsonl",sorted(source_map.values(),key=lambda x:x["source_id"]))
 jsonl(OUT/"chemical_objects_and_fixtures_exposures.jsonl",reaction_records)
 jsonl(OUT/"metadata_discovery_events.jsonl",meta_events)
 grouped=defaultdict(list)
 for r in meta_events:
  key=r["pmcid"] or ("doi:"+r["doi"].lower() if r["doi"] else ("pmid:"+str(r["pmid"]) if r["pmid"] else r["source_id"]))
  grouped[key].append(r)
 metadata_only=[]
 for key,rs in sorted(grouped.items()):
  if any(r["source_had_original_chemical_read_elsewhere"] for r in rs):continue
  metadata_only.append(dict(source_id=key,source_tokens=sorted({t for r in rs for t in r["source_tokens"]}),
   metadata_only=True,actual_original_chemical_read_by_this_agent=False,
   conservative_next_epoch_fresh_exclusion=True,
   exclusion_is_metadata_policy_not_chemical_evidence=True,discovery_event_count=len(rs),
   rounds=sorted({r["round_id"] for r in rs}),
   historical_source_exposed=any(r["historical_source_exposed"] for r in rs),
   sample_event_pointer={"path":rel(OUT/"metadata_discovery_events.jsonl"),"source_id":key},
   qualification_not_claimed=True))
 jsonl(OUT/"metadata_only_source_hints.jsonl",metadata_only)
 # Explicit physical access failure versus actually inspected originals.
 access=[dict(attempt_id=h["attempt_id"],url=h["url"],kind=h["kind"],HTTP_status=h["status_code"],
  status=h["status"],raw_pointer={"path":h["path"],"sha256":h["sha256"]},
  raw_is_not_original_chemical_evidence=True) for h in http if h["status"]!="available"]
 save(OUT/"access_deferred_events.json",dict(events=access,
  R3_PMC2709393_original_fulltext_read=False,
  ACS_GcCGT_SI_original_bytes_read=False,Trollius_SI_original_bytes_read=False,
  tool_browser_HTTP_count_unknown=True,not_chemical_absence_or_saturation_evidence=True))
 timeline.append(dict(event_type="design_input_preparation_completed",timestamp=now(),
  original_source_read=["PMC11975207"],future_epoch_chemical_holdout_extraction=False,
  scope_built_or_modified=False,pointer=bind(DESIGN/"design_source_input_manifest.json")))
 jsonl(OUT/"exposure_timeline.jsonl",sorted(timeline,key=lambda r:r.get("timestamp") or ""))
 jsonl(OUT/"permanent_source_blocklist.jsonl",[
  dict(source_id=s["source_id"],source_tokens=s["source_tokens"],closure_tokens=s["closure_tokens"],
   block_reason="original chemistry actually inspected; permanent design corpus",
   applies_to_future_epochs=True,fresh_eligible=False,
   source_exposure_pointer={"path":rel(OUT/"chemical_source_exposures.jsonl"),"source_id":s["source_id"]})
  for s in sorted(source_map.values(),key=lambda x:x["source_id"])])
 assert before=={p:sha_file(ROOT/p) for p in before},"frozen scientific artifact drift"
 counts=dict(actual_chemically_inspected_source_ids=len(source_map),
  unique_normalized_source_closures=len({c for s in source_map.values() for c in s["closure_tokens"]}),
  original_source_inspection_records=sum(r["record_type"]=="source_level_chemical_inspection" for r in reaction_records),
  own_A4_endpoint_records=sum(r["record_type"]=="own_A4_molecular_endpoint_inspection" for r in reaction_records),
  design_fixture_records=sum(r["record_type"]=="registered_design_fixture_inspection" for r in reaction_records),
  all_object_records=len(reaction_records),metadata_discovery_events=len(meta_events),
  metadata_only_source_ids=len(metadata_only),observable_HTTP_events=len(http),
  query_rounds=3,design_source_exact_reactions=len(universe),future_fresh_self_admissions=0)
 generated={rel(p):sha_file(p) for p in sorted(OUT.glob("*")) if p.is_file()}
 design_files={rel(p):sha_file(p) for p in sorted(DESIGN.glob("*")) if p.is_file()}
 manifest=dict(task=TASK,role="A1 Source Scout exposure preservation",epoch_id="C-E01",
  created_at=now(),approval_type="agent_delegated",human_reviewed=False,
  status="permanent exposure package; scientific stop/epoch invalidation belongs to root",
  inherited_historical_exposure_ledger=inherited,counts=counts,
  required_future_source_exclusion="inherit all historical exposure; block all current chemically inspected source closures forever; metadata-only exclusions are explicitly conservative policy",
  chemical_source_universe_complete_for_this_agent=True,
  metadata_only_never_promoted_to_chemical_evidence=True,
  read_A5_finalgraphs=False,scope_built_or_modified=False,
  all_frozen_scientific_artifact_SHA_unchanged=True,frozen_artifact_SHAs=before,
  G5_batch_pointers=g5,raw_original_and_response_objects_SHA=raw,
  input_files_SHA=inputs,output_files_SHA=generated,design_only_package_files_SHA=design_files,
  chronology="recorded acquisition, intake freeze and role completion retained; exact first-read unknown is never filled from filesystem mtime",
  original_request_ID_uniqueness=False,physical_event_alias_resolution_pointer=bind(BASE/"http_audit/request_id_collision_v1/request_id_alias_resolution.json"),
  evidence_eligibility_granted=False,no_source_saturation_claim=True,
  closure_threshold_not_lowered=True)
 save(OUT/"manifest.json",manifest)
 save(DESIGN/"role_A1_input_preparation_manifest.json",dict(task=TASK,role="A1 Source Scout",
  approval_type="agent_delegated",human_reviewed=False,created_at=now(),
  processed_reaction_candidates=8,independently_qualified_new_epoch=0,
  contains_final_graphs=False,read_holdout_previously=True,read_other_extractor_output=False,
  scope_built_or_modified=False,epoch_initialized=False,
  prerequisite="root E01 formal expose/invalidate and renewed source qualification before A7 construction",
  input_manifest_pointer=bind(DESIGN/"design_source_input_manifest.json"),
  source_universe_pointer=bind(DESIGN/"source_exact_reaction_universe.jsonl"),
  permanent_exposure_manifest_pointer=bind(OUT/"manifest.json")))
 # Independently recompute hashes of all files actually bound by the package.
 checked={**inputs,**generated,**design_files}
 assert all(sha_file(ROOT/p)==s for p,s in checked.items())
 print(json.dumps(dict(exposure_manifest=bind(OUT/"manifest.json"),
  design_input_manifest=bind(DESIGN/"design_source_input_manifest.json"),
  source_universe=bind(DESIGN/"source_exact_reaction_universe.jsonl"),
  counts=counts,all_bound_file_SHA_recomputed=True,bound_files=len(checked)),ensure_ascii=False))
if __name__=="__main__":main()
