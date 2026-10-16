"""Independent molecular extraction reconciliation, without name-based reconstruction."""
from __future__ import annotations

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

from scripts.task016_p7_closure_harness import canonical
from scripts.task016_p7_orchestrate import ContractError, ROOT, require_fields, sha_file, sha_json

FIELDS = ("reaction_id","acceptor_smiles","donor_smiles","product_smiles","bond_atoms","site",
          "sugar_identity","anomer_stereo","direction","step_count","evidence_location",
          "structure_origin","structure_evidence_pointer","reference_precursors",
          "agent_role","input_manifest_sha","read_other_extractor_output","extraction_id")
ALLOWED_ORIGINS = {
    "original_machine_readable", "official_supplementary_machine_readable",
    "authoritative_structure_database_identity_chain", "dual_independent_source_graph_transcription",
}


def _validated(row, *, root=ROOT, validate_files=True):
    require_fields(row,FIELDS)
    if row["read_other_extractor_output"] is not False:
        raise ContractError("extractors must not read each other's output")
    if row["structure_origin"] not in ALLOWED_ORIGINS:
        raise ContractError("handwritten/name/memory-based complex structure prohibited")
    if not row["evidence_location"] or not row["structure_evidence_pointer"]:
        raise ContractError("structure needs source location and immutable pointer")
    require_fields(row["structure_evidence_pointer"],("path","sha256"))
    pointer=row["structure_evidence_pointer"]
    if validate_files and (not (root/pointer["path"]).is_file() or sha_file(root/pointer["path"])!=pointer["sha256"]):
        raise ContractError("structure source pointer SHA mismatch")
    if row["structure_origin"]=="authoritative_structure_database_identity_chain":
        if not row.get("identity_chain"):
            raise ContractError("database graph requires unambiguous identity chain")
    if row["direction"] not in ("acceptor+donor->product","forward") or row["step_count"]!=1:
        raise ContractError("only explicitly source-bound single step is runtime complete")
    if not row["anomer_stereo"] or normalize_unknown(row["anomer_stereo"]):
        raise ContractError("source-unknown anomer/stereo cannot be guessed")
    if not row["sugar_identity"] or not row["site"]:
        raise ContractError("source sugar/site identity incomplete")
    graphs={name:canonical(row[name+"_smiles"]) for name in ("acceptor","donor","product")}
    if sorted(canonical(p) for p in row["reference_precursors"]) != sorted([graphs["acceptor"],graphs["donor"]]):
        raise ContractError("reference precursor must contain full acceptor and full donor")
    if not isinstance(row["bond_atoms"],dict):
        raise ContractError("bond atom identities missing")
    require_fields(row["bond_atoms"],("acceptor_atom","donor_atom","product_atoms"))
    # Stable atom identities are source/map identities, not unverified local indices.
    for field in ("acceptor_atom","donor_atom"):
        if not isinstance(row["bond_atoms"][field],str) or not row["bond_atoms"][field]:
            raise ContractError("bond atoms must have explicit stable source/map identity")
    if not isinstance(row["bond_atoms"]["product_atoms"],list) or len(row["bond_atoms"]["product_atoms"])!=2:
        raise ContractError("formed bond requires two product atom identities")
    if row["structure_origin"]=="dual_independent_source_graph_transcription":
        require_fields(row,("source_product_formula","source_product_exact_mass","source_naming_check"))
        mol=Chem.MolFromSmiles(graphs["product"])
        if rdMolDescriptors.CalcMolFormula(mol)!=row["source_product_formula"]:
            raise ContractError("transcribed source formula mismatch")
        if abs(Descriptors.ExactMolWt(mol)-float(row["source_product_exact_mass"]))>0.01:
            raise ContractError("transcribed source exact mass mismatch")
        if row["source_naming_check"] is not True:
            raise ContractError("transcribed graph/source name consistency unresolved")
    return graphs


def normalize_unknown(value):
    return str(value).strip().casefold() in ("unknown","unspecified","unresolved","inferred","?")


def reconcile(extractor_a,extractor_b, *, root=ROOT, validate_files=True):
    graph_a=_validated(extractor_a,root=root,validate_files=validate_files)
    graph_b=_validated(extractor_b,root=root,validate_files=validate_files)
    if extractor_a["agent_role"]!= "A4" or extractor_b["agent_role"]!="A5":
        raise ContractError("dual extraction roles must be distinct A4/A5")
    if extractor_a["extraction_id"]==extractor_b["extraction_id"]:
        raise ContractError("same extraction cannot serve two roles")
    if extractor_a["input_manifest_sha"]!=extractor_b["input_manifest_sha"]:
        raise ContractError("extractors must consume same frozen source input")
    compared = ("reaction_id","bond_atoms","site","sugar_identity","anomer_stereo","direction","step_count")
    differences=[name for name in compared if extractor_a[name]!=extractor_b[name]]
    differences += [name+"_graph" for name in graph_a if graph_a[name]!=graph_b[name]]
    if differences:
        return dict(reaction_id=extractor_a["reaction_id"],structure_complete=False,
                    reference_precursor_complete=False,status="reconciliation_required",
                    differences=differences,extractor_a_sha=sha_json(extractor_a),extractor_b_sha=sha_json(extractor_b),
                    agent_role="A6 Reconciliation & Closure Auditor",human_reviewed=False)
    return dict(reaction_id=extractor_a["reaction_id"],structure_complete=True,
                reference_precursor_complete=True,status="reconciled",
                acceptor_smiles=graph_a["acceptor"],donor_smiles=graph_a["donor"],
                product_smiles=graph_a["product"],
                reference_precursors=sorted([graph_a["acceptor"],graph_a["donor"]]),
                site=extractor_a["site"],sugar_identity=extractor_a["sugar_identity"],
                anomer_stereo=extractor_a["anomer_stereo"],bond_atoms=extractor_a["bond_atoms"],
                differences=[],extractor_a_sha=sha_json(extractor_a),extractor_b_sha=sha_json(extractor_b),
                evidence_pointers=[extractor_a["structure_evidence_pointer"],extractor_b["structure_evidence_pointer"]],
                evidence_locations=[extractor_a["evidence_location"],extractor_b["evidence_location"]],
                agent_role="A6 Reconciliation & Closure Auditor",human_reviewed=False)
