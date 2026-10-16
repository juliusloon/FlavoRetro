"""Freeze TASK-015-P5 agent final decisions; preserve original human reviews.

Reads frozen evidence, writes only an additive local overlay. No network or
runtime resource mutation. Rebuilding with changed inputs fails closed.
"""
import json
from collections import Counter
from pathlib import Path

from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors
from scripts.operate import digest, write

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-015-P5"
OUT = "outputs/evidence/task015-p5-final-v1"
INPUT = "outputs/evidence/task015-p5-final-input"
AUTHORITY = {
    "decision_authority": "agent_delegated",
    "reviewer_type": "agent",
    "reviewer_id": "Cano/root",
    "owner_adopted_conclusions": True,
    "owner_instruction_date": "2026-10-05",
    "owner_instruction": "直接将你的结论作为最终结论，不要再让我审核这个",
    "new_human_reviews": 0,
    "further_owner_review_required": False,
}
RDLogger.DisableLog("rdApp.*")


def load(path):
    return json.loads((ROOT / path).read_text())


def lines(path):
    return [json.loads(s) for s in (ROOT / path).read_text().splitlines() if s.strip()]


def emit(name, value, jsonl=False):
    content = ("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in value)
               if jsonl else json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    p = f"{OUT}/{name}"
    if (ROOT / p).exists():
        if (ROOT / p).read_text() != content:
            raise ValueError(f"immutable final output differs: {p}")
    else:
        write(TASK, p, content)
    return p


def canon(smiles):
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise ValueError("unparseable structure")
    return Chem.MolToSmiles(m, isomericSmiles=True)


def reaction_sides(token):
    left, right = token.split(">>")
    return [sorted(canon(s) for s in side.split(".")) for side in (left, right)]


def component_sides(record):
    return [sorted(canon(c["structure"]["canonical_smiles"]) for c in record["components"]
                   if c["role"] == role) for role in ("reactant", "product")]


def main():
    baseline = load(f"{INPUT}/baseline.json")["protected_sha256"]
    assert all(digest(ROOT / p) == h for p, h in baseline.items()), "protected input drift"
    p1path = "outputs/review/task015-p1/final-v2/review.jsonl"
    packetpath = "outputs/review/task015-p5-axes/handoff-v3/packet.json"
    p1 = {x["id"]: x for x in lines(p1path)}
    packet = load(packetpath)
    goldpath = "outputs/review/task015-p3/gold-v1/gold.jsonl"
    exclpath = "outputs/review/task015-p3/gold-v1/excluded.jsonl"
    gold = {r["id"]: r for r in lines(goldpath)}
    excluded = {r["id"] for r in lines(exclpath)}
    final60 = {r["id"]: r for r in load("outputs/review/task015-p3/final/review-final-60.json")["records"]}
    axes = []
    for card in packet["cards"]:
        rid = card["id"]
        old = p1[rid]
        source = old["source_assessment"]
        y = old["conditions_yield_assessment"]
        src = source["status"]
        retained = rid in gold
        status = "excluded" if not retained else src
        numeric = retained and src == "primary_instance_verified" and y["status"] in {
            "assigned_primary", "assigned_primary_rounded_export", "assigned"}
        cy = dict(y)
        if numeric:
            cy.update(final_status="primary_numeric_supported",
                      primary_value=y.get("primary_reported_value", y["reported_value"]))
        elif retained and src == "primary_instance_verified" and card["card_number"] == 6:
            cy.update(final_status="primary_inequality_export_discrepancy", primary_value=None,
                      primary_expression=">99%", export_exact_value_confirmed=False)
        elif not retained:
            cy.update(final_status="excluded_record", primary_value=None)
        else:
            cy.update(final_status="final_" + y["status"], primary_value=None)
        axes.append({**card, **AUTHORITY, "split": "development_exposed", "final": True,
                     "structure_decision": "development_gold" if retained else "excluded",
                     "structure_gold": gold.get(rid),
                     "previous_owner_review": final60[rid]["review"],
                     "source_final_status": status, "source_evidence": source,
                     "yield_final": cy, "primary_source_supported": retained and src == "primary_instance_verified",
                     "numeric_yield_supported": numeric,
                     "decision_note": "结构结论采用既有 gold；来源/产率仅按所列证据定案，未知项不等待人工回填。",
                     "production_eligible": False})
    assert len(axes) == len(p1) == 60 and set(gold) | excluded == set(p1)
    assert set(gold).isdisjoint(excluded) and len(gold) == 53 and len(excluded) == 7

    records = {r["id"]: r for r in load("data/derived/v3/records.json")}
    notes = []
    foundpath = "outputs/evidence/task015-p5-p0/token_found_prescreen.jsonl"
    unmatchedpath = "outputs/evidence/task015-p5-p0/token_unmatched_relocation.jsonl"
    for old in lines(foundpath):
        status = "retain_note_provenance_only"
        strict = False
        checks = []
        if old["prescreen_verdict_agent"] != "parse_failure":
            try:
                for e in old["evidence"]:
                    if e.get("token_verbatim_present"):
                        checks.append(reaction_sides(e["token_reaction"]) == component_sides(records[old["id"]]))
                strict = bool(checks) and all(checks)
                status = "note_token_and_components_consistent" if strict else "exclude_exact_reaction_component_mismatch"
            except ValueError:
                status = "exclude_exact_reaction_parse_failure_retain_note"
        else:
            status = "exclude_exact_reaction_parse_failure_retain_note"
        notes.append({**AUTHORITY, "id": old["id"], "locator": old["locator"],
                      "final_decision": status, "strict_component_multiset_match": strict,
                      "primary_experimental_evidence": False, "evidence": old,
                      "scope": "笔记转录/定位一致性；不是文献实验验证或 gold"})
    for old in lines(unmatchedpath):
        exact = []
        for e in old["files"]:
            if e.get("canonical_reaction_found") and e.get("file_sha256_matches_sources_json"):
                for line1 in e["exact_lines1"]:
                    text = (ROOT / e["file"]).read_text().splitlines()[line1 - 1]
                    # Candidate tokens come from the prior relocation's line parser.
                    for candidate in e.get("fuzzy_top2", []):
                        if candidate["line1"] == line1 and candidate["raw"] in text:
                            if reaction_sides(candidate["raw"]) == component_sides(records[old["id"]]):
                                exact.append({"file": e["file"], "line1": line1})
        status = "note_canonical_match_confirmed" if exact else "retain_unmatched_not_verified"
        notes.append({**AUTHORITY, "id": old["id"], "locator": old["locator"],
                      "final_decision": status, "strict_component_multiset_match": bool(exact),
                      "confirmed_locators": exact, "primary_experimental_evidence": False,
                      "evidence": old, "scope": "模糊候选不自动挂接、不作为正面证据"})
    assert len(notes) == len({r["id"] for r in notes}) == 508

    prop_path = f"{INPUT}/pubchem-property-snapshot.json"
    name_path = f"{INPUT}/pubchem-name-snapshot.json"
    props = {r["CID"]: r for r in load(prop_path)["response"]["PropertyTable"]["Properties"]}
    named = {r["name"]: r for r in load(name_path)}
    groups = load("outputs/evidence/task015-p5-p0/name_conflict_evidence.json")["groups"]
    names = []
    for group in groups:
        a, b = group["peer"], group["candidate"]
        assert canon(a["canonical_smiles"]) == canon(b["canonical_smiles"])
        if a["query_name"] == "narirutin":
            assert a["inchikey"] == props[442431]["InChIKey"]
            decision = "same_structure_alias_use_narirutin_keep_both_ids"
            reason = "同一结构且 PubChem 将 Isonaringin 列作 Narirutin 同义词；覆盖层归并名称，不删除原记录。"
            details = {"canonical_name": "narirutin", "alias": "isonaringin",
                       "source_url": "https://pubchem.ncbi.nlm.nih.gov/compound/Isonaringin"}
        else:
            m = Chem.MolFromSmiles(a["canonical_smiles"])
            rings = [len(r) for r in m.GetRingInfo().AtomRings()
                     if sum(m.GetAtomWithIdx(i).GetSymbol() == "O" for i in r) == 1]
            p_o_c = sum(n.GetSymbol() == "O" and any(c.GetSymbol() == "C" for c in n.GetNeighbors())
                        for p in m.GetAtoms() if p.GetSymbol() == "P" for n in p.GetNeighbors())
            assert rings == [5, 5] and p_o_c == 1
            decision = "quarantine_both_udp_arabinose_name_assignments"
            reason = "不仅是名称环大小冲突：图中两糖环均五元，二磷酸仅有一个 P-O-C 端；第二糖经 C-C 接于核糖侧链，不是常规 UDP 糖的两端 O-磷酸连接。CID 自洽不证明名称正确。"
            details = {"oxygen_ring_sizes": rings, "phosphate_carbon_linked_oxygen_count": p_o_c,
                       "rejected_cid": 3082070, "pyranose_reference": props[644105],
                       "reference_scope": "正确连接的对照，不直接替换原记录或指定未知立体形态"}
        names.append({**AUTHORITY, "record_ids": [a["molecule_id"], b["molecule_id"]],
                      "final_decision": decision, "reason": reason, "details": details, "prior_evidence": group})
    assert len(names) == 2

    identity_path = "outputs/evidence/task015-p5-vendor/identity_packets.jsonl"
    vendor_path = "outputs/evidence/task015-p5-vendor/vendor_checks.jsonl"
    old_vendors = {r["stock_ref"]: r for r in lines(vendor_path)}
    bad_names = {
        "TBSCl": "编码图和 CID 6397 均为 TMSCl（C3H9ClSi），不是 TBSCl（C6H15ClSi）。",
        "naringenin": "编码 C9H8O5 图缺少 naringenin 的 B 芳环；正确名称所指分子为 C15H12O5。",
        "2,4-dihydroxy-6-methoxyacetophenone": "编码芳环为乙酰基邻位甲氧基、两个间位羟基；不匹配声明的 2,4-二羟基-6-甲氧基连接。",
        "neohesperidose": "编码第二糖的受糖位点为环 C4；不匹配 neohesperidose 所指的 rhamnosyl-(1→2)-glucose。",
    }
    identities, vendors = [], []
    for old in lines(identity_path):
        if old["kind"] == "template":
            identities.append({**AUTHORITY, "record_id": old["record_id"], "ref": old["ref"],
                               "kind": "template", "final_decision": "retain_candidate_not_primary_certified",
                               "reason": "断连模式可解析不等于已验证合成；未有绑定的具体正向实例与糖供体/操作条件，不晋级。",
                               "evidence": old, "production_eligible": False})
            continue
        name = old["name"]
        mol = Chem.MolFromSmiles(old["canonical_smiles"])
        assert mol is not None
        key = Chem.MolToInchiKey(mol)
        assert key == old["structure_inchikey"] == old["inchikey"]
        formula = rdMolDescriptors.CalcMolFormula(mol)
        cid = old.get("identity_evidence", {}).get("source_id")
        cid_match = bool(cid and props[int(cid.split(":")[1])]["InChIKey"] == key)
        ref = named.get(name)
        named_props = ref.get("response", {}).get("PropertyTable", {}).get("Properties", []) if ref else []
        named_key = named_props[0]["InChIKey"] if named_props else None
        exact_name = key == named_key
        connectivity_name = key.split("-")[0] == named_key.split("-")[0] if named_key else None
        decision = "quarantine_name_structure_mismatch" if name in bad_names else "retain_encoded_candidate"
        reason = bad_names.get(name, "保留编码结构；数据库自洽与名称/具体形态、供应证据分别评价，不补推立体化学。")
        if name == "rutinose":
            reason = "名称检索返回开链形态，库存为环形且糖立体形态未独立闭合；保留编码候选，不把泛名称商品等同此精确图。"
        if name == "dehydrated_rhamnopyranose_quercitrin_fragment":
            reason = "C6H12O4 缺少异头羟基，不是 C6H12O5 鼠李糖；旧名 dehydrated 也不代表真实脱水化学计量，作为历史内部片段保留，否决母体糖直接供应声明。"
        identities.append({**AUTHORITY, "record_id": old["record_id"], "ref": old["ref"],
                           "kind": "stock", "name": name, "formula": formula,
                           "computed_inchikey": key, "registered_cid_matches_graph": cid_match,
                           "name_reference_exact_graph": exact_name, "name_reference_connectivity": connectivity_name,
                           "name_reference": ref, "final_decision": decision, "reason": reason,
                           "evidence": old, "production_eligible": False})
        vendor = old_vendors[old["ref"]]
        if name in bad_names:
            vs = "reject_listing_for_mismatched_stock_graph"
        elif name == "dehydrated_rhamnopyranose_quercitrin_fragment":
            vs = "reject_parent_sugar_substitution"
        elif vendor["check_status"] == "not_commodity_internal_fragment":
            vs = "internal_candidate_no_verified_exact_vendor"
        else:
            vs = "catalog_claim_not_current_supply_certified"
        vendors.append({**AUTHORITY, "stock_ref": old["ref"], "name": name,
                        "final_decision": vs, "current_exact_supply_verified": False,
                        "prior_observation_date": vendor["retrieved_at"],
                        "evidence": vendor, "reason": "原汇编未逐条绑定产品 URL/快照；保留历史目录线索，不能把名称检索、数据库身份或母体替代当精确库存的当前可采购证据。"})
    assert len(identities) == 51 and len(vendors) == 49
    summary = {"task": TASK, "status": "Completed", "version": "task015-p5-final-v1", **AUTHORITY,
               "structure_gold": 53, "excluded_cards": 7,
               "source_final_status": dict(Counter(r["source_final_status"] for r in axes)),
               "primary_source_supported_cards": [r["card_number"] for r in axes if r["primary_source_supported"]],
               "numeric_yield_supported_cards": [r["card_number"] for r in axes if r["numeric_yield_supported"]],
               "yield_final_status": dict(Counter(r["yield_final"]["final_status"] for r in axes)),
               "notes": dict(Counter(r["final_decision"] for r in notes)),
               "name_conflict_groups": 2, "name_conflict_records": 4,
               "identity_decisions": dict(Counter(r["final_decision"] for r in identities)),
               "vendor_decisions": dict(Counter(r["final_decision"] for r in vendors)),
               "stock_name_quarantines": sorted(bad_names),
               "current_exact_vendor_supported": 0,
               "blind_protocol_status": "Proposed_delivered_no_blind_dataset_or_run",
               "runtime_consumes_this_overlay": False,
               "boundaries": ["所有对象已有最终决定；缺证据项不是人工待办", "53 条结构开发 gold 保持；来源/产率正面子集分别冻结，非全部轴全量 gold", "全部已见开发资料，非独立盲测；原件、v3、active、release、MCTS 未变"]}
    outputs = [emit("axes-final-60.jsonl", axes, True), emit("notes-final-508.jsonl", notes, True),
               emit("name-decisions.json", names), emit("identity-final-51.jsonl", identities, True),
               emit("vendor-final-49.jsonl", vendors, True),
               emit("primary-source-supported.jsonl", [r for r in axes if r["primary_source_supported"]], True),
               emit("numeric-yield-supported.jsonl", [r for r in axes if r["numeric_yield_supported"]], True),
               emit("summary.json", summary)]
    input_paths = list(baseline) + [p1path, prop_path, name_path,
                                  f"{INPUT}/pubchem-tbs-reference.json", f"{INPUT}/baseline.json",
                                  "scripts/task015_p5_finalize.py"]
    emit("manifest.json", {"task": TASK, "version": "task015-p5-final-v1", "authority": AUTHORITY,
                           "inputs_sha256": {p: digest(ROOT / p) for p in sorted(set(input_paths))},
                           "outputs_sha256": {p: digest(ROOT / p) for p in outputs}})
    assert all(digest(ROOT / p) == h for p, h in baseline.items()), "protected output drift"
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
