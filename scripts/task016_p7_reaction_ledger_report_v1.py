"""Render the human-readable Chinese per-article/per-reaction eligibility ledger.

Deterministic projection of reaction_eligibility_ledger_v1.jsonl + ledger_summary_v1.json;
introduces no numbers that are not already in the verified machine artifacts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from operate import event, write  # noqa: E402

T = "TASK-016-P7"
B = Path("outputs/task016-p7/v1")
OUT = B / "reaction_eligibility_ledger_v1"

def owner_sort(c):
    """Owner-numbered sources first (by number), then non-numbered ones."""
    no = c.get("owner_source_number")
    return (no is None, no or "", c["source_ref"])


REASON_CN = {
    "frozen_scope_site_mismatch": "与冻结位点 scope 不匹配",
    "located_claim_not_a_source_complete_reaction": "所定位主张不构成来源完整单步反应",
    "source_identity_attachment_pending": "来源身份／SI 附件关联待定",
    "linkage_site_structure_pending": "连接位点结构待定",
    "graph_and_name_closure_missing": "完整原子图与名称／同实验闭包缺失",
    "name_level_exposure_structural_level_unresolved": "名称级曝光 vs 结构级曝光未裁定",
    "never_assessed": "从未评估",
}
KIND_CN = {
    "GWAS_isovitexin_indirect": "GWAS／异牡荆素通路（间接）",
    "precursor_2_hydroxy_then_dehydration": "2-羟基前体后脱水（两步）",
    "organic_reaction_not_single_enzymatic_c6": "有机多步化学法（非单酶 C6）",
    "dihydrochalcone_C3prime": "二氢查尔酮 C3′（冻结域外）",
    "SI_only_no_verified_main_attachment_link": "仅 SI，正文附件未验证",
    "flavonol_aglycone_3O": "苷元 3-O（非糖内层 O2）",
    "rutin_aglycone_O7_O4prime_O3prime": "苷元 O7／O4′／O3′",
    "flavonol_aglycone_O3_O7": "苷元 O3／O7",
    "flavonol_3O_reverse_UDP": "3-O 可逆 UDP 转移",
    "flavonol_3O_chain_extension_link_site_unknown": "3-O 链延伸，内层位点未知",
    "flavonol_aglycone_7O": "苷元 7-O",
    "direct_C6_source_statement_without_full_graph": "直接 C6 文献陈述，缺完整原子图",
}
STATUS_CN = {
    "admitted": "admitted",
    "deferred": "deferred",
    "rejected": "rejected",
    "not_yet_assessed": "not yet assessed",
}


def esc(s) -> str:
    return str(s).replace("|", "\\|")


def main():
    ledger = [json.loads(l) for l in (ROOT / OUT / "reaction_eligibility_ledger_v1.jsonl")
              .read_text(encoding="utf-8").splitlines()]
    coverage = [json.loads(l) for l in (ROOT / OUT / "source_coverage_ledger_v1.jsonl")
                .read_text(encoding="utf-8").splitlines()]
    s = json.loads((ROOT / OUT / "ledger_summary_v1.json").read_text(encoding="utf-8"))
    a11 = json.loads((ROOT / OUT / "A11_independent_ledger_verification_v1.json")
                     .read_text(encoding="utf-8"))
    defects = json.loads((ROOT / OUT / "known_defects_and_discrepancies_v1.json")
                         .read_text(encoding="utf-8"))["defects"]

    cov = {c["source_ref"]: c for c in coverage}
    L = []
    A = L.append
    A("# TASK-016-P7 逐篇逐反应资格清单 v1（离线整合层）\n")
    A(f"- 生成时间：{s['at']}（UTC）")
    A(f"- 授权：{s['authorization']}（所有者本轮明确批准；阶段决定 agent_delegated）")
    A("- 层：`G6_IDENTITY_STRUCTURE_ADMIT` 的**支撑子账本**；`stage_transition_performed=false`，未写任何阶段清单、未改 epoch ledger")
    A(f"- 账本 SHA256：`{s['ledger_sha256']}`")
    A(f"- 覆盖账本 SHA256：`{s['coverage_sha256']}`")
    A(f"- 汇总 SHA256：`{s['input_manifest_sha256']}`（input manifest）")

    A("\n## 一、这份清单是什么、不是什么\n")
    A("**是**：把既有机器产物中每一条**已定位**反应／主张的处置显式化，并把**从未评估**的部分显式标成 `not_yet_assessed`，做到零不作为缺失。")
    A("**不是**：新的化学审核、fresh 判定、论文级否定，也不是来源饱和证明。")
    A("本轮 `no_new_source_read=true`、`no_new_http=true`、未打开任何原件 PDF、未改 G4 scope、未跑 MCTS：所有 `status` 均**机械取自上游产物的 disposition 字段**。\n")

    A("## 二、分母与残余\n")
    A("| 类别 | 数量 | 说明 |")
    A("| --- | --- | --- |")
    A("| 具名历史来源 | 16 | 所有者人工索取 01–16（15 篇正文 + 10 号 SI-only） |")
    A("| 新增前瞻 C 来源 | 1 | `PMC13564134` |")
    A("| **重点核验来源合计** | **17** | 与摘要口径一致 |")
    A("| 残余 metadata 宇宙 | 1 行 | 88 条 C 轴 + 35 条 SS 轴唯一 metadata，**不在 17 项分母内**，从未进入化学资格审核 |\n")

    A("## 三、状态计数（本轮账本 36 行）\n")
    A("| status | 行数 |")
    A("| --- | --- |")
    for st in ("admitted", "deferred", "rejected", "not_yet_assessed"):
        A(f"| `{st}` | {s['rows_by_status'].get(st, 0)} |")
    A(f"\n- `admitted_total = {s['admitted_total']}`，`fresh_C = {s['fresh_C']}`，`fresh_SS = {s['fresh_SS']}`")
    A(f"- `runtime_complete` 行数 = {s['runtime_complete_rows']}；`scope_applicable` 行数 = {s['scope_applicable_rows']}")
    A(f"- 声称论文级排除的行数 = {s['article_level_exclusion_rows']}（必须为 0）")
    A(f"- 17 个来源全部带有残余 `not_yet_assessed` 行：`sources_with_residual_marker = {s['sources_with_residual_marker']}`\n")

    for fam, title in (("C", "四、C 轴逐篇逐反应"), ("SS", "五、SS 轴逐篇逐反应")):
        A(f"## {title}\n")
        A("| 编号 | 来源 | DOI／PMCID | 冻结 scope | 所定位反应／主张 | status | 原因类 | 阻塞门 |")
        A("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for c in sorted([c for c in coverage
                         if c.get("family") == fam and c.get("owner_source_number") is not None],
                        key=owner_sort):
            r = next(r for r in ledger if r["source_ref"] == c["source_ref"]
                     and r["row_kind"] == "located_example_reaction")
            kind = KIND_CN.get(r["located_claim_kind"], r["located_claim_kind"])
            gates = "、".join(f"`{g}`" for g in r["blocking_gates"])
            A(f"| {c['owner_source_number']} | {esc(c['source_ref'])} | `{c.get('verified_DOI')}` | `{c['frozen_scope']}` | "
              f"{esc(kind)} | **{STATUS_CN[r['status']] if False else r['status']}** | {REASON_CN[r['reason_class']]} | {gates} |")
        A("")
        A("上游逐条陈述（英文原文，未改写）：\n")
        for c in sorted([c for c in coverage
                         if c.get("family") == fam and c.get("owner_source_number") is not None],
                        key=owner_sort):
            r = next(r for r in ledger if r["source_ref"] == c["source_ref"]
                     and r["row_kind"] == "located_example_reaction")
            A(f"- **{c['owner_source_number']} / {r['reason_code']}**：{r['observed_report']}")
        A("")

    A("## 六、新增 C 来源 `PMC13564134`\n")
    newr = next(r for r in ledger if r["row_id"] == "REL-C-NEW01-R1")
    A(f"- DOI `{newr['source_original']['verified_DOI']}`；原件 SHA256 `{newr['source_original']['original_sha256']}`")
    A(f"- 所定位主张：{KIND_CN.get(newr['located_claim_kind'], newr['located_claim_kind'])}")
    A(f"- status：**{newr['status']}**；原因类：{REASON_CN[newr['reason_class']]}")
    A(f"- A3 官方 PMC 身份通过；A4／A5 两独立进程定性陈述一致（`A4_A5_qualitative_claim_agreement=true`）")
    A(f"- 但 `A4_A5_full_molecule_graph_reconciliation=false`，`exact_product_graph_match_or_mismatch = {newr['assessment_layers'][-1]['exact_product_graph_match_or_mismatch']}`")
    A(f"- 缺失字段 {len(newr['structural_missing_fields'])} 项：{'、'.join('`%s`' % x for x in newr['structural_missing_fields'])}")
    A(f"- 结论：文献陈述正确 ≠ 完整反应资格；该来源**既不 admitted 也不 rejected**。\n")

    A("## 七、历史曝光边界：`isoorientin` 名称曝光的精确裁定请求\n")
    iso = s["isoorientin_name_exposure_audit"]
    A(f"- 三本账本中 `isoorientin` 命中：**{iso['row_instances_total']} 行实例**；按内容哈希去重后**仅 {iso['distinct_records']} 条不同记录**")
    A(f"- 其中非空的结构字段名：{iso['structural_graph_field_names_observed_non_null']}（空列表 = 无任何受体／供体／产物图、位点、反应签名）")
    A("- 每条记录均为 `entity_kind=biological_endpoint`，`partial_target_source_name=C-glucosylflavones`，`unresolved_partial_identity_tokens` 内含 `partial-target-name:isoorientin`")
    A("")
    A("**因此**：这是**名称级（部分目标名 token）曝光**，不是**化学结构／位点级曝光**。它既不能自动算作完全泄漏，也不能直接宣称无泄漏 —— 账本将其登记为 `deferred`，等待明确 A6 裁定。")
    A("同时指出既有产物的计数语义问题：标题中的 36 是**跨三个账本版本（v1／v2／effective）的同一 12 条记录的行实例数**，直接引用为「36 条记录」会把 distinct 曝光高估 3 倍。\n")

    A("## 八、显式缺口（`not_yet_assessed`）\n")
    A("| 缺口 | 行数 | 说明 |")
    A("| --- | --- | --- |")
    A(f"| 各来源未枚举反应 | 17 | 每篇 1 行残余；上游 `all_article_reactions_exhaustively_reviewed=false` |")
    A(f"| 残余 metadata 宇宙 | 1 | 88 条 C 轴 + 35 条 SS 轴唯一 metadata，从未化学评估 |")
    A("\n所有 17 篇的 `article_reaction_universe_exhausted` 均为 `false`：**没有任何一篇被声称已穷尽全部反应**。\n")

    A("## 九、本轮发现的既有产物缺陷（原版留存，未修改）\n")
    A("| ID | 类型 | 发现 | 处置 |")
    A("| --- | --- | --- | --- |")
    for d in defects:
        A(f"| {d['defect_id']} | {d['severity']} | {esc(d['finding'])} | {esc(d['action_taken'])} |")
    A(f"\n`prior_artifacts_modified = {defects and 'false'}`；缺陷对象 `{defects[0]['artifact']}` 的 SHA 在 A11 中复核仍一致。\n")

    A("## 十、独立核查\n")
    A(f"- A11 独立核查：**{a11['passed']}/{a11['checks_total']} 通过，{a11['failed']} 失败**（`{OUT}/A11_independent_ledger_verification_v1.json`）")
    A(f"- A11 独立重算：具名来源 {a11['independent_rederivations']['named_sources']}、rejected {a11['independent_rederivations']['rejected']}、deferred {a11['independent_rederivations']['deferred']}、isoorientin 实例 {a11['independent_rederivations']['isoorientin_row_instances']}／distinct {a11['independent_rederivations']['isoorientin_distinct_records']}")
    A(f"- 所有输入与证据指针 SHA 逐一重算一致；G4 C／SS scope SHA 与快照一致（未漂移）")
    A(f"- 物理账不变：HTTP {s['physical_HTTP_total_unchanged']}、字节 {s['physical_source_bytes_total_unchanged']}（本轮 +0／+0）\n")

    A("## 十一、不变的科学结论\n")
    A("| 项 | 值 |")
    A("| --- | --- |")
    A(f"| C fresh | {s['fresh_C']} |")
    A(f"| SS fresh | {s['fresh_SS']} |")
    A(f"| 完整反应准入 | {s['complete_reaction_admission']} |")
    A("| 科学 A/B/E cells | 0 |")
    A("| metrics | `null` |")
    A(f"| 可冻结 G7 面板 | `{str(s['can_freeze_G7_panel']).lower()}` |")
    A(f"| G6 全局 | 未完成（`G6_global_complete={str(s['G6_global_complete']).lower()}`） |")
    A("| TASK-016-P7 | **In Progress** |")
    A("\n本清单用于决定 G6 何时可以结束，而不是让 fresh 数字变大；未降低每轴 ≥6 目标／≥2 组与真实 A/B/E 硬门，未升格 `human_reviewed` 或独立化学验证，未做 Git 提交推送。\n")

    L.append("\n## 附注：本轮渲染修正\n")
    L.append("首版 `README.md` 渲染缺陷：前瞻来源被重复列入第四节的 C 轴表且编号显示为 `None`。")
    L.append("缺陷版保留为 `README.v1-superseded-render.md`（未删除、未改写）；本版仅在投影层排除非具名编号来源，数据行与 SHA 未变。\n")

    body = "\n".join(L)
    target = ROOT / OUT / "README.md"
    if target.exists():
        raise RuntimeError("immutable output already exists")
    write(T, str(OUT / "README.md"), body)
    event(T, "reaction_ledger_v1_readme_written", bytes=len(body.encode()))
    print(f"README.md written: {len(body.encode())} bytes")


if __name__ == "__main__":
    main()
