"""Fresh post-scope panel gates, with static reference reconstruction."""
from __future__ import annotations

from datetime import datetime
from rdkit import Chem

from scripts.task016_p7_closure_harness import assert_zero_leakage, canonical, closure_groups, target_graph
from scripts.task016_p7_orchestrate import ContractError, require_fields, sha_json

FLAGS = ("runtime_complete","source_identity_verified","structure_complete",
         "reference_precursor_complete","scope_applicability")


def validate_panel(records, epoch, scopes, exposures=(), build=(), runtime_instances=(),
                   *, enforce_floor=True):
    state=epoch.as_dict() if hasattr(epoch,"as_dict") else epoch
    require_fields(state,("family","epoch_id","scope_sha","scope_frozen_at","status"))
    if state["status"]!="active" or state["scope_sha"] is None:
        raise ContractError("panel requires active frozen scope epoch")
    if sha_json(scopes)!=state["scope_sha"]:
        raise ContractError("panel scope bank drift")
    require_fields(scopes,("family","epoch_id","scopes"))
    if scopes["family"]!=state["family"] or scopes["epoch_id"]!=state["epoch_id"]:
        raise ContractError("scope family/epoch mismatch")
    scope_ids={}
    for scope in scopes["scopes"]:
        require_fields(scope,("scope_id","scope_sha","qualified"))
        if scope["qualified"] is not True:
            raise ContractError("panel cannot use unqualified scope")
        if scope["scope_id"] in scope_ids:
            raise ContractError("duplicate scope id")
        scope_ids[scope["scope_id"]]=scope["scope_sha"]
    ids=set()
    graphs=set()
    for row in records:
        require_fields(row,("target_id","family","epoch_id","product_smiles","acceptor_smiles",
                           "donor_smiles","reference_precursors","closure_group","extracted_at",
                           "extraction_scope_sha","leakage","exact_seed_instance_match",
                           "scope_applicability_records")+FLAGS)
        if row["family"]!=state["family"] or row["epoch_id"]!=state["epoch_id"]:
            raise ContractError("panel target from wrong family/epoch")
        if any(row[flag] is not True for flag in FLAGS):
            raise ContractError("panel runtime/identity/structure/reference/applicability incomplete")
        if row["leakage"] is not False or row["exact_seed_instance_match"] is not False:
            raise ContractError("panel leakage/exact instance")
        if row["extraction_scope_sha"]!=state["scope_sha"]:
            raise ContractError("holdout extracted under another scope")
        if datetime.fromisoformat(row["extracted_at"])<=datetime.fromisoformat(state["scope_frozen_at"]):
            raise ContractError("fresh holdout extracted before scope freeze")
        product_graph=canonical(row["product_smiles"])
        for participant in (row["acceptor_smiles"],row["donor_smiles"],row["product_smiles"]):
            mol=Chem.MolFromSmiles(canonical(participant))
            if len(Chem.GetMolFrags(mol))!=1:
                raise ContractError("panel participant is not one complete covalent graph")
        if row["target_id"] in ids or product_graph in graphs:
            raise ContractError("duplicate panel identity/product graph")
        ids.add(row["target_id"]);graphs.add(product_graph)
        full_reference=sorted([canonical(row["acceptor_smiles"]),canonical(row["donor_smiles"])])
        if sorted(canonical(s) for s in row["reference_precursors"])!=full_reference:
            raise ContractError("panel lacks full canonical reference")
        qualified=False
        for probe in row["scope_applicability_records"]:
            require_fields(probe,("scope_id","scope_sha","complete_reference","precursors",
                                  "static_only","scope_modified"))
            if probe["scope_id"] not in scope_ids or probe["scope_sha"]!=scope_ids[probe["scope_id"]]:
                raise ContractError("static applicability scope drift")
            if probe["static_only"] is not True or probe["scope_modified"] is not False:
                raise ContractError("applicability may not consume model outcome or change scope")
            if probe["complete_reference"] is True and sorted(canonical(p) for p in probe["precursors"])==full_reference:
                qualified=True
        if not qualified:
            raise ContractError("no frozen scope reconstructs full reference")
    leakage=assert_zero_leakage(build,records,exposures,runtime_instances)
    groups=closure_groups(records)
    if enforce_floor and (len(records)<6 or len(groups)<2):
        raise ContractError("fresh panel below >=6 targets / >=2 independent closures")
    if enforce_floor and len(records)>9:
        raise ContractError("panel exceeds frozen first-matrix 9-target budget")
    return dict(family=state["family"],epoch_id=state["epoch_id"],N=len(records),
                closure_groups=len(groups),groups=groups,scope_sha=state["scope_sha"],
                runtime_complete_count=len(records),scope_applicable_count=len(records),
                all_flags_passed=True,leakage=leakage,completion_floor_passed=len(records)>=6 and len(groups)>=2,
                operational_buffer_passed=len(records)>=8 and len(groups)>=3)
