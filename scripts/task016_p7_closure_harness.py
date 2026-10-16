"""Historical chemical exposure inventory and conservative reaction/source closures."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

from rdkit import Chem, rdBase

from scripts.operate import write
from scripts.task016_p7_orchestrate import ContractError, ROOT, TASK, now, require_fields, sha_file, sha_json

CHEM_KEYS = {
    "reaction_id", "canonical_reaction_signature", "reaction_smiles", "product_smiles",
    "acceptor_smiles", "donor_smiles", "reference_precursors", "precursor_smiles",
    "target", "target_smiles", "smiles", "canonical_acceptor_signature",
    "template_smarts", "scoped_smarts", "reaction_signature",
}
SOURCE_KEYS = {"pmcid", "pmc", "doi", "source", "source_id", "source_article", "source_pmcid"}
PMC_RE = re.compile(r"PMC[0-9]+", re.I)
DOI_RE = re.compile(r"10\.[0-9]{4,9}/[^\s\"<>]+", re.I)
HISTORY_ROOTS = ["outputs/task016"] + [f"outputs/task016-p{i}" for i in range(1, 7)]


def canonical(smiles):
    if not isinstance(smiles, str) or not smiles.strip():
        raise ContractError("empty molecular graph")
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ContractError("invalid molecular graph")
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)


def source_tokens(record):
    tokens = set()
    def walk(value, key=""):
        if isinstance(value, dict):
            for child_key, child in value.items():
                walk(child, child_key)
        elif isinstance(value, list):
            for child in value:
                walk(child, key)
        elif isinstance(value, str):
            if key in SOURCE_KEYS or key in ("closure_group", "source_group", "url", "path", "source_binding"):
                tokens.update("article:"+match.upper() for match in PMC_RE.findall(value))
                if (key == "doi" or "doi.org/" in value
                        or (key in SOURCE_KEYS and re.match(r"^(?:doi:\s*)?10\.[0-9]{4,9}/", value.strip(), re.I))):
                    for match in DOI_RE.findall(value):
                        tokens.add("doi:"+match.rstrip(".,);").lower())
                if key in ("closure_group", "source_group") and value:
                    tokens.add("group:"+value)
    walk(record)
    return tokens


def target_graph(record):
    for name in ("product_smiles", "target_smiles", "target", "smiles"):
        value = record.get(name)
        if isinstance(value, str):
            try:
                return canonical(value)
            except ContractError:
                continue
    return None


def reaction_graph(record):
    product = target_graph(record)
    acceptor = record.get("acceptor_smiles")
    donor = record.get("donor_smiles")
    precursors = record.get("reference_precursors", record.get("precursor_smiles"))
    if precursors is None and acceptor and donor:
        precursors = [acceptor, donor]
    if product and isinstance(precursors, list) and precursors:
        try:
            return ".".join(sorted(canonical(p) for p in precursors))+">>"+product
        except ContractError:
            pass
    for field in ("canonical_reaction_signature", "reaction_signature", "reaction_smiles", "signature"):
        value = record.get(field)
        if isinstance(value, str) and ">>" in value:
            try:
                lhs, rhs = value.split(">>")
                return ".".join(sorted(canonical(p) for p in lhs.split(".")))+">>"+canonical(rhs)
            except (ContractError, ValueError):
                return "raw-reaction:"+value
    return None


def closure_tokens(record, *, include_target=True):
    tokens = source_tokens(record)
    signature = reaction_graph(record)
    if signature:
        tokens.add("reaction:"+signature)
    graph = target_graph(record)
    if include_target and graph:
        tokens.add("target:"+graph)
    acceptor = record.get("acceptor_smiles")
    donor = record.get("donor_smiles")
    site = record.get("site", record.get("linkage"))
    if acceptor and donor and site:
        tokens.add("acceptor-donor-site:"+canonical(acceptor)+"|"+canonical(donor)+"|"+str(site))
    for field in ("assay_id", "experimental_cohort", "source_assay", "scope_support_id",
                  "template_support_id", "reaction_id", "instance_id"):
        value = record.get(field)
        if value:
            tokens.add(field+":"+str(value))
    for value in record.get("closure_tokens", []):
        if not isinstance(value, str):
            raise ContractError("closure token must be a string")
        tokens.add(value)
    return tokens


def build_historical_ledger(root=ROOT):
    """Inventory every historical structured artifact, including superseded/failed runs.

    Metadata-only rows remain metadata-only. Any artifact carrying chemical fields is
    conservatively exposed, irrespective of a historical eligibility assertion.
    """
    index = {}
    inventory = []
    parse_errors = []
    skipped = []
    scanned_chemical_nodes = 0
    def register(node, path, digest, pointer):
        nonlocal scanned_chemical_nodes
        if not isinstance(node, dict):
            return
        present = sorted(CHEM_KEYS.intersection(node))
        if present:
            scanned_chemical_nodes += 1
            sources = source_tokens(node)
            graph = target_graph(node)
            reaction = reaction_graph(node)
            key_data = dict(target_graph=graph, reaction_signature=reaction,
                            reaction_id=node.get("reaction_id"), source_tokens=sorted(sources),
                            raw_chemical_fields={key: node[key] for key in present
                                                 if key not in ("template_smarts", "scoped_smarts")},
                            template_id=node.get("template_id"))
            key = sha_json(key_data)
            if key not in index:
                completeness = dict(target_graph=graph is not None,
                                    reaction_signature=reaction is not None and not reaction.startswith("raw-"),
                                    acceptor_graph=False, donor_graph=False, site=bool(node.get("site",node.get("linkage"))),
                                    source=bool(sources), evidence_pointer=True)
                for name in ("acceptor", "donor"):
                    try:
                        canonical(node.get(name+"_smiles"))
                        completeness[name+"_graph"] = True
                    except ContractError:
                        pass
                raw_tokens = closure_tokens(node)
                index[key] = dict(exposure_id="historical:"+key, task=TASK,
                                  exposure_type="historical_development_exposure",
                                  development_exposed=True, eligible_for_fresh_holdout=False,
                                  entity_kind="reaction" if reaction else "target_or_structure",
                                  **key_data, closure_tokens=sorted(raw_tokens),
                                  field_completeness=completeness, historical_assertions={
                                      key: node[key] for key in ("eligible_for_holdout", "exposure_grade",
                                      "structure_complete", "runtime_executable") if key in node},
                                  origins=[], first_registered_at=now())
            index[key]["origins"].append(dict(path=str(path.relative_to(root)), sha256=digest,
                                              json_pointer=pointer))
        # Preserve source exposure for artifact-level chemical review, even if
        # incomplete row structures put the identifier in a sibling node.
        if present or path.name.startswith(("source_identity", "identity_check", "reference_recon", "structure")):
            for token in source_tokens(node):
                key = "source:"+token
                if key not in index:
                    index[key] = dict(exposure_id=key, task=TASK,
                                      exposure_type="historical_development_exposure",
                                      development_exposed=True, eligible_for_fresh_holdout=False,
                                      entity_kind="source", source_tokens=[token],
                                      closure_tokens=[token], target_graph=None,
                                      reaction_signature=None, reaction_id=None,
                                      raw_chemical_fields={}, template_id=None,
                                      field_completeness=dict(target_graph=False,reaction_signature=False,
                                      acceptor_graph=False,donor_graph=False,site=False,source=True,evidence_pointer=True),
                                      historical_assertions={},origins=[],first_registered_at=now())
                index[key]["origins"].append(dict(path=str(path.relative_to(root)),sha256=digest,
                                                  json_pointer=pointer))
        for key, value in node.items():
            if isinstance(value, dict):
                register(value,path,digest,pointer+"/"+str(key))
            elif isinstance(value, list):
                for i, child in enumerate(value):
                    if isinstance(child, dict):
                        register(child,path,digest,pointer+"/"+str(key)+"/"+str(i))
    for folder in HISTORY_ROOTS:
        directory = root/folder
        if not directory.is_dir():
            raise ContractError(f"historical root missing: {folder}")
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.suffix not in (".json", ".jsonl") or path.name.startswith("._"):
                continue
            digest = sha_file(path)
            inventory.append(dict(path=str(path.relative_to(root)),sha256=digest,bytes=path.stat().st_size))
            # Protection/path hash manifests contain no chemical record.
            if path.name in ("protected_hashes.json", "original_hashes.json"):
                skipped.append(dict(path=str(path.relative_to(root)),reason="path-SHA-only protection manifest"))
                continue
            try:
                if path.suffix == ".jsonl":
                    for line_number, line in enumerate(path.read_text().splitlines(),1):
                        if line.strip():
                            value = json.loads(line)
                            register(value,path,digest,"line:"+str(line_number))
                else:
                    value = json.loads(path.read_text())
                    if isinstance(value,list):
                        for i,node in enumerate(value):
                            register(node,path,digest,"/"+str(i))
                    else:
                        register(value,path,digest,"")
            except (UnicodeError, json.JSONDecodeError, ContractError) as exc:
                parse_errors.append(dict(path=str(path.relative_to(root)),error=str(exc),sha256=digest))
    rows = sorted(index.values(),key=lambda row:row["exposure_id"])
    return rows, dict(task=TASK, timestamp=now(), history_roots=HISTORY_ROOTS,
                      scanned_files=len(inventory),chemical_nodes=scanned_chemical_nodes,
                      exposure_rows=len(rows),source_exposures=sum(row["entity_kind"]=="source" for row in rows),
                      parse_errors=parse_errors,nonchemical_skips=skipped,files=inventory,
                      complete=len(parse_errors)==0,conservative_source_closure=True,
                      chemistry_verification=False)


def assert_fresh(record, exposures):
    tokens = closure_tokens(record)
    for row in exposures:
        require_fields(row,("development_exposed","exposure_type","closure_tokens"))
        if row["development_exposed"]:
            overlap = tokens.intersection(row["closure_tokens"])
            if overlap:
                raise ContractError(f"historical/design exposure intersects holdout: {sorted(overlap)}")
    return True


def assert_zero_leakage(build, holdout, exposures=(), runtime_instances=()):
    build_tokens = set().union(*(closure_tokens(row) for row in build)) if build else set()
    runtime_targets = {target_graph(row) for row in runtime_instances}
    runtime_reactions = {reaction_graph(row) for row in runtime_instances}
    for row in holdout:
        overlap = build_tokens.intersection(closure_tokens(row))
        if overlap:
            raise ContractError(f"build/holdout closure leakage: {sorted(overlap)}")
        if target_graph(row) in runtime_targets-{None} or reaction_graph(row) in runtime_reactions-{None}:
            raise ContractError("holdout is an exact runtime instance")
        assert_fresh(row, exposures)
    return dict(reaction_leakage=0,source_assay_closure_leakage=0,
                exact_runtime_instance_leakage=0,scope_design_leakage=0,
                build_count=len(build),holdout_count=len(holdout))


def closure_groups(records):
    """Connected components across source, assay and reaction edges."""
    parent = list(range(len(records)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    owners = {}
    for i,row in enumerate(records):
        for token in closure_tokens(row,include_target=False):
            if token in owners:
                left,right = find(i),find(owners[token])
                parent[left] = right
            else:
                owners[token] = i
    groups = defaultdict(list)
    for i,row in enumerate(records):
        groups[find(i)].append(row.get("reaction_id") or row.get("target_id") or row.get("exposure_id") or str(i))
    return {"closure:"+sha_json(sorted(values))[:20]: sorted(values) for values in groups.values()}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out",default="outputs/task016-p7/v1")
    args = parser.parse_args()
    rows,audit = build_historical_ledger()
    output = Path(args.out)
    ledger = output/"exposure_ledger.jsonl"
    if (ROOT/ledger).exists():
        raise ContractError("historical ledger already frozen")
    write(TASK,str(ledger),"".join(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n" for row in rows))
    from scripts.task016_p7_orchestrate import save_json, role_manifest
    save_json(output/"historical_exposure_inventory.json",audit,immutable=True)
    manifest = role_manifest("A6 Reconciliation & Closure Auditor","historical",
        [item["path"] for item in audit["files"]],
        [ledger,output/"historical_exposure_inventory.json"],
        dict(processed=len(rows),passed=len(rows),rejected=0,pending=0),
        pointers=[item["path"] for item in audit["files"]],errors=audit["parse_errors"],
        unprocessed=[item["path"] for item in audit["parse_errors"]],
        read_holdout=True,read_model_outcome=True)
    save_json(output/"a6_historical_exposure_manifest.json",manifest,immutable=True)
    print(json.dumps({key:audit[key] for key in ("scanned_files","chemical_nodes","exposure_rows","source_exposures","complete")}))
    if not audit["complete"]:
        raise ContractError("historical inventory parse errors require reconciliation")


if __name__ == "__main__":
    main()
