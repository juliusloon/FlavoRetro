"""C-E02-R7 bounded A6. Source scope exclusion is independent of unrelated gaps."""
import json,xml.etree.ElementTree as ET
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,verify_hashes,verify_stage_chain,role_manifest,freeze_stage_manifest
from scripts.task016_p7_c_e02_http import E,BASE,immutable_json,append,rows
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
from scripts.task016_p7_closure_harness import canonical
from scripts.task016_p7_source_alias_closure import assert_fresh
B=E/"fresh/C-E02-R7";O=B/"A6_source_reconciliation_v1"
def js(p):return json.loads(p.read_text())
def main():
    r4=B/"A4_raw_extraction_v1/role_A4_fixed_manifest.json";r5=B/"A5_raw_extraction_v1/role_A5_manifest.json"
    ad4=B/"A4_contract_adapter_v1/role_A4_contract_adapter.json";ad5=B/"A5_contract_adapter_v1/role_A5_contract_adapter.json"
    ins=[Path(__file__),ROOT/"scripts/task016_p7_c_e02_r7_literal_reconcile_v2.py",r4,r5,ad4,ad5]
    for p in (ad4,ad5):
        r=js(p)
        for field in ("input_manifest_sha","output_file_sha"):
            m=r[field];assert isinstance(m,dict);verify_hashes(m);ins.extend(ROOT/q for q in m)
        assert r["read_model_outcome"] is False
    g5=E/"stages/batches/C-E02-R7/G5_FRESH_HOLDOUT_ACQUIRE.json"
    verify_stage_chain(g5,"d7cc6a2e0a3835d7a3aeb2fa6c37b408eb8667c949589ff185f4e6cbe5ace8e4");ins.append(g5)
    ip=E/"stages/batches/C-E02-R7/fresh_source_input_manifest.json";ins.append(ip)
    ident=B/"root_A3_publication_identity_v2/A3_summary.json";ins.append(ident)
    identrole=B/"root_A3_publication_identity_v2/role_A3_manifest.json";ins.append(identrole)
    ir=js(identrole);verify_hashes(ir["input_manifest_sha"]);verify_hashes(ir["output_file_sha"]);assert ir["counts"]==dict(passed=3,pending=6,processed=9,rejected=0)
    for p in [B/"root_A6_precomparison_input_SHA_v2.json",B/"root_A6_graph_comparison_v1.json",O/"378_literal_comparisons_v1.json"]:
        ins.append(p)
    comp=js(O/"378_literal_comparisons_v1.json");verify_hashes(comp["input_file_sha256"]);assert comp["equal_records"]==378 and comp["differences"]==[]
    graphcmp=js(B/"root_A6_graph_comparison_v1.json");assert graphcmp["canonical_full_graph_matches"]==11 and all(x["formula_agree"] for x in graphcmp["comparisons"])
    s4=rows(B/"A4_raw_extraction_v1/A4_complete_nine_source_dispositions.jsonl")
    s5={x["source_id"]:x for x in js(B/"A5_raw_extraction_v1/all9_source_dispositions.json")["dispositions"]}
    assert len(s4)==len(s5)==9 and {x["source_id"] for x in s4}==set(s5)
    reasons={
      "PMC13273386":dict(scope_applicable=False,reason="Actual glycal1 donor is not UDP-glucose. Phloretin is dihydrochalcone; apigenin yields keto products followed by spontaneous isomerization and separate reduction. C6 reduced product is author-putative, C8 coelution evidence retained. None is a demonstrated single UDP-glucose to ordinary flavone C6 glucoside reaction.",product_site_ambiguity_preserved=True,unrelated_gap_is_not_exclusion_basis=True),
      "PMC11663222":dict(scope_applicable=False,reason="Protected glucal metalation, organoboron and iodine/NaOMe Zweifel sequence is chemical synthesis. Distinct donor/core/steps from frozen direct enzymatic UDP-glucose flavone C6 scope.",unrelated_gap_is_not_exclusion_basis=True),
      "PMC7904931":dict(scope_applicable=False,reason="Membrane potential/fluorescence measurements are not glycosylation yields. Source resveratrol synthesis uses protected phenol/glucosyl donor and TMSOTf multistep route; previously prepared nothofagin/isoflavone compounds are not new direct flavone C6 source assays.",unrelated_gap_is_not_exclusion_basis=True)}
    disp=[];evidence=[]
    for x in s4:
        sid=x["source_id"];y=s5[sid];n=x["original_objects_count"]
        assert n==y["original_count"] and (n>0)==x["scientific_original_read"]
        d=dict(source_id=sid,doi=x["doi"],pmid=x.get("pmid"),original_objects=n,A4_disposition=x["A4_source_disposition"],A5_disposition=y["disposition"],source_original_identity_verified=n>0,source_qualified_for_current_scope=False,fresh_admitted=False,disposition="retained_outside_frozen_scope" if n else "pending_primary_original_access",scope_decision=reasons.get(sid,dict(scope_applicable=None,reason="metadata only is not reaction evidence")),unprocessed=x["unprocessed"],no_absence_or_saturation_inference=True)
        disp.append(d)
        if n:
            raw=ROOT/x["originals"][0]["path"];ins.append(raw);tree=ET.fromstring(raw.read_bytes())
            ps=[" ".join("".join(p.itertext()).split()) for p in tree.findall(".//body//p")]
            selected=[dict(paragraph_index_in_body_descendants=i+1,source_literal=t) for i,t in enumerate(ps) if any(s.casefold() in t.casefold() for s in ("glucal","apigenin","putativ","AtRED","NaBH","organobor","metalation","TMSOTf","dipole potential","synthesis"))]
            evidence.append(dict(source_id=sid,raw_pointer=pointer(raw),direct_XML_paragraphs=selected,comparison_context=reasons[sid],not_new_chemical_experiment=True))
    assert sum(x["original_objects"] for x in disp)==27
    save_rows(O/"9_source_disposition_reconciliation.jsonl",disp)
    immutable_json(O/"actual_original_paragraphs_and_scope_exclusion.json",dict(task=TASK,at=now(),source_records=evidence,exclusion_does_not_require_full_unrelated_product_encoding=True,no_universal_NMR_or_authentic_standard_gate=True))
    scope=E/"scope_bank.json";ins.append(scope);bank=js(scope);assert len(bank)==1 and bank[0]["required_context"]["donor_name"]=="UDP-glucose"
    gdon=js(ROOT/next(x for x in graphcmp["comparisons"] if x["A4_label"]=="donor1")["A4_pointer"]["path"])
    assert canonical(gdon["canonical_isomeric_SMILES"])!=canonical(bank[0]["donor"])
    immutable_json(O/"actual_complete_donor_graph_scope_comparison.json",dict(source_donor_pointer=next(x for x in graphcmp["comparisons"] if x["A4_label"]=="donor1")["A4_pointer"],source_donor_canonical=canonical(gdon["canonical_isomeric_SMILES"]),source_donor_formula=gdon["formula_derived_from_source_graph"],frozen_donor_canonical=canonical(bank[0]["donor"]),frozen_scope_pointer=pointer(scope),full_donor_equal=False,no_inferred_model_applicability=True))
    exposures=[]
    for x in graphcmp["comparisons"]:
        p=ROOT/x["A4_pointer"]["path"];g=js(p);ins.append(p);sm=canonical(g["canonical_isomeric_SMILES"])
        exposures.append(dict(task=TASK,epoch_id="C-E02",batch_id="C-E02-R7",exposure_id="C-E02-R7:dual-graph:"+x["A4_label"],source_id="PMC13273386",doi="10.1039/d6cc01584k",pmid="42305022",exposure_type="post_G5_dual_source_depiction_reconciliation",development_exposed=True,future_fresh_eligible=False,eligible_for_fresh_holdout=False,product_smiles=sm,closure_tokens=["article:PMC13273386","doi:10.1039/d6cc01584k","pmid:42305022","target:"+sm],object_role=x["A4_label"],object_is_not_necessarily_assay_product=True,source_pointer=x["A4_source_pointer"],graph_pointer=x["A4_pointer"],dual_full_graph_formula_agree=True,actual_assay_identity_not_implied=True,chemical_qualification=False,human_reviewed=False,actual_registered_at=now(),first_global_chemical_observation_timestamp=None,registration_not_backdated=True,current_batch_not_retroactively_rejected_from_this_registration=True))
    for x in disp:
        if x["original_objects"]:
            exposures.append(dict(task=TASK,epoch_id="C-E02",batch_id="C-E02-R7",exposure_id="C-E02-R7:source:"+x["source_id"],exposure_type="post_G5_source_scientific_read",development_exposed=True,eligible_for_fresh_holdout=False,future_fresh_eligible=False,source_id=x["source_id"],doi=x["doi"],pmid=x["pmid"],closure_tokens=["article:"+x["source_id"],"doi:"+x["doi"],"pmid:"+x["pmid"]],source_pointer=pointer(B/"A4_raw_extraction_v1/A4_complete_nine_source_dispositions.jsonl"),actual_registered_at=now(),registration_not_backdated=True,chemical_qualification=False,human_reviewed=False))
    save_rows(O/"permanent_source_and_graph_exposures.jsonl",exposures)
    probes=[]
    for d in disp:
        if d["original_objects"]:
            try:assert_fresh(dict(doi=d["doi"],reaction_id="future-renamed"),exposures)
            except ValueError as exc:probes.append(dict(source_id=d["source_id"],actually_rejected=True,error=str(exc),future_intake_guard_only=True))
            else:raise ValueError("future source alias not rejected")
    immutable_json(O/"actual_future_source_rename_probes.json",probes)
    summary=dict(task=TASK,agent_role="A6 Reconciliation & Closure Auditor",at=now(),epoch_id="C-E02",batch_id="C-E02-R7",source_dispositions=9,primary_original_sources=3,original_objects=27,metadata_only_access_pending=6,current_scope_outside_sources=3,current_scope_qualified_reactions=0,complete_source_depiction_graph_pairs=11,canonical_full_graph_and_formula_matches=11,actual_assay_identity_not_implied=True,compared_literal_records=378,independently_equal_literal_records=378,compared_measurement_cells=297,other_compared_ratio_and_yield_labels=81,raw_literal_differences_after_explicit_comparison_projection=0,SI_last_column_label_projection_documented=True,source_conflicts_and_author_putative_retained=True,A4_graph_v1_failure_preserved=True,A5_map_CIP_corrections_preserved=True,A5_log3900_source_metadata_exposure_disclosed=True,A3_root_authored_source_only_identity=True,A6_root_authored_not_independent_chemistry=True,full_chemical_round_complete=False,source_saturation=False,source_access_exhausted=False,scope_changed=False,fresh_admitted=0,scientific_ABE_cells=0,metrics=None,new_HTTP=0,new_MCTS=0,human_reviewed=False,approval_type="agent_delegated")
    immutable_json(O/"A6_source_reconciliation_summary.json",summary)
    prior=B/"source_exposure_custodian_v1/permanent_exposure_manifest.json";ins.append(prior)
    ins=list(dict.fromkeys(ins));outs=[p for p in sorted(O.glob("*.json*")) if p.is_file()]
    pm=O/"permanent_exposure_manifest.json";immutable_json(pm,dict(task=TASK,created_at=now(),inherited_source_custodian=pointer(prior),input_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in ins},output_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in outs},new_dual_graph_exposure_records=11,new_source_registration_records=3,source_exposures_already_in_custodian=True,future_intake_must_bind=True,chemical_qualification_granted=False,human_reviewed=False));outs.append(pm)
    role=role_manifest("A6 Reconciliation & Closure Auditor","C-E02",ins,outs,dict(processed=9,passed=0,rejected=3,pending=6),pointers=[pointer(O/"actual_original_paragraphs_and_scope_exclusion.json")],read_holdout=True,read_model_outcome=False,errors=["root literal v1 relative-path error and failed failure-journal path; preserved in literal_comparison_failure_v1.json; corrected v2"],unprocessed=["6 primary original access gaps","Unrelated chemical product series and upstream intermediates not fully encoded","No fresh panel","No full source/name closure-universe or saturation claim"])
    role.update(root_authored_reconciliation=True,independent_chemical_validation=False,rejected_definition="retained outside current frozen scope; not invalid scientific source",A4_A5_original_pack_not_modified=True)
    rp=O/"role_A6_manifest.json";immutable_json(rp,role)
    stage_dir=E/"stages/batches/C-E02-R7"
    freeze_stage_manifest(stage_dir,"G6_IDENTITY_STRUCTURE_ADMIT",ins+outs+[rp],g5,expected_previous_sha=sha_file(g5),family="C",epoch_id="C-E02")
    stage=stage_dir/"G6_IDENTITY_STRUCTURE_ADMIT.json";verify_stage_chain(stage,sha_file(stage))
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R7",event_type="verified_existing_stage_registration",stage="G6_IDENTITY_STRUCTURE_ADMIT",stage_manifest_path=str(stage.relative_to(ROOT)),stage_manifest_sha256=sha_file(stage),registered_at=now(),admitted_count=0,formal_panel_frozen=False,approval_type="agent_delegated",human_reviewed=False,backdated=False))
    previous=BASE/"epochs/C-E02/epoch_state.v6.json";state=js(previous)
    state.update(actual_created_at=now(),previous_state_pointer=pointer(previous),G6_batches=5,R7_chemical_extraction_started=True,R7_A4_A5_status="fixed_and_A6_reconciled_3_scope_outside_6_missing_original",R7_A6_pointer=pointer(O/"A6_source_reconciliation_summary.json"),R7_observed_source_exposure_pointer=pointer(pm),source_complete_rounds=None,source_saturation=False)
    state["pending"]=["Fresh executable panel >=6 / groups>=2; no floor reduction","Six R7 sources still primary-original access pending","R6/R8 no usable new originals or G5","No reuse of design/exposed objects as future fresh"]
    state["stage_branch_pointers"].append(pointer(stage));ep=BASE/"epochs/C-E02/epoch_state.v7.json";immutable_json(ep,state)
    print(json.dumps(dict(summary=pointer(O/"A6_source_reconciliation_summary.json"),role=pointer(rp),G6=pointer(stage),epoch=pointer(ep),fresh=0)))
if __name__=="__main__":main()
