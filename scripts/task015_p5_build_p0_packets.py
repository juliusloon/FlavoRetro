# -*- coding: utf-8 -*-
"""TASK-015-P5 阶段 B：P0 遗留三包。

B1  249 条 note_reaction token 命中的内容预筛（记录事实 vs 定位文件命中上下文，
    RDKit 规范化比较 SMILES；代理预筛，reviewer=agent）+ 固定种子 30 条所有者样本
    （种子先于任何人审核登记）+ 全部不一致项并入样本表。
B2  259 条 token 未命中的定位复核（文件存在性/漂移、全文件规范化再检索、
    difflib 模糊候选）。
B3  名称冲突决议表（冻结数据 2 组 duplicate_names、4 个 FGM ID；含
    「文档 3 条 vs 冻结 2 组」对账）。

输入（只读）：data/derived/v3/records.json、metadata/sources.json。
输出：outputs/evidence/task015-p5-p0/。确定性构建；需 RDKit（.venv-foundation）。
"""

import csv
import difflib
import hashlib
import json
import random
import re
from pathlib import Path

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "data/derived/v3/records.json"
SOURCES = ROOT / "metadata/sources.json"
OUT = ROOT / "outputs/evidence/task015-p5-p0"
SEED = 20260929
SAMPLE_N = 30


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(s):
    return re.sub(r"\s+", "", s or "").lower()


def canon_smiles(s):
    m = Chem.MolFromSmiles(s or "")
    return Chem.MolToSmiles(m) if m else None


def canon_set(smiles_str):
    parts = (smiles_str or "").split(".")
    out = []
    for p in parts:
        c = canon_smiles(p)
        if c is None:
            return None
        out.append(c)
    return frozenset(out)


def record_sides(rec):
    """返回 (reactant_canon_set, product_canon_set, 原始 smiles 字符串或 None)。"""
    reacts, prods = set(), set()
    for comp in rec.get("components") or []:
        smi = (comp.get("structure") or {}).get("canonical_smiles")
        c = canon_smiles(smi)
        if c is None:
            return None, None, None
        (reacts if comp.get("role") == "reactant" else prods).add(c)
    return frozenset(reacts), frozenset(prods), None


SMILES_RE = re.compile(r"\$smiles=([^\s`\"']+)")


class FileCache:
    def __init__(self, root):
        self.root = root
        self.lines = {}
        self.text = {}
        self.tokens = {}

    def get_lines(self, rel):
        if rel not in self.lines:
            p = self.root / rel
            if not p.exists():
                self.lines[rel] = None
            else:
                self.lines[rel] = p.read_text(encoding="utf-8", errors="replace").splitlines()
                self.text[rel] = norm("\n".join(self.lines[rel]))
        return self.lines[rel]

    def get_text(self, rel):
        self.get_lines(rel)
        return self.text.get(rel)

    def get_tokens(self, rel):
        """文件内全部 $smiles 反应 token，规范化为 (原始串, 反应物集, 产物集)。"""
        if rel not in self.tokens:
            lines = self.get_lines(rel)
            toks = []
            if lines:
                for i, line in enumerate(lines):
                    for m in SMILES_RE.finditer(line):
                        raw = m.group(1)
                        if ">>" not in raw:
                            continue
                        a, _, b = raw.partition(">>")
                        toks.append({"line1": i + 1, "raw": raw, "r": canon_set(a), "p": canon_set(b), "rs": a, "ps": b})
            self.tokens[rel] = toks
        return self.tokens[rel]


def condition_snippet(rec):
    raw = rec.get("raw") or {}
    cond = (raw.get("conditions") or {}).get("condition_text") or ""
    head = cond.strip().split("。")[0]
    return head[:120]


def prescreen_found(rec, cache, src_sha):
    """B1 内容预筛（口径与准入对齐）：
    ① 准入重验：raw_reaction_smiles 是否仍逐字在定位文件中；
    ② 行核对：token 实际所在行 vs 上游报告行；
    ③ 化学一致性：token 两侧规范化集合 vs 记录 components 规范化集合；
    ④ 条件文本在场。"""
    rels = rec.get("upstream_sources") or []
    raw = rec.get("raw") or {}
    token = raw.get("raw_reaction_smiles") or ""
    rs, ps, _ = record_sides(rec)
    tok_r, tok_p = (None, None)
    if ">>" in token:
        a, _, b = token.partition(">>")
        tok_r, tok_p = canon_set(a), canon_set(b)
    parse_ok = all(x is not None for x in (rs, ps, tok_r, tok_p))
    chem_match = parse_ok and tok_r == rs and tok_p == ps
    cond = norm(condition_snippet(rec))
    line_no = rec.get("upstream_reported_line")

    evidence = []
    verdict = "source_file_missing"
    for rel in rels:
        lines = cache.get_lines(rel)
        if lines is None:
            evidence.append({"file": rel, "present": False})
            continue
        cur_sha = sha(cache.root / rel)
        drift_meta = src_sha.get(rel) not in (None, cur_sha)
        actual_lines = [i + 1 for i, ln in enumerate(lines) if token and token in ln]
        cond_present = bool(cond) and cond in cache.get_text(rel)
        ctx = []
        anchor = actual_lines[0] if actual_lines else line_no
        if anchor:
            for i in range(max(0, anchor - 3), min(len(lines), anchor + 3)):
                ctx.append(f"{i+1}: {lines[i][:300]}")
        evidence.append({
            "file": rel, "present": True, "file_sha256_current": cur_sha,
            "file_sha256_matches_sources_json": not drift_meta,
            "token_verbatim_present": bool(actual_lines),
            "token_actual_lines1": actual_lines[:10],
            "reported_line1": line_no,
            "line_distance": None if (not actual_lines or not line_no) else min(abs(l - line_no) for l in actual_lines),
            "chemistry_consistent": chem_match,
            "condition_text_present": cond_present,
            "token_reaction": token[:400],
            "context": ctx,
        })
        if not actual_lines:
            verdict = "token_missing_from_file" if verdict == "source_file_missing" else verdict
        elif chem_match:
            dist = None if not line_no else min(abs(l - line_no) for l in actual_lines)
            verdict = "consistent_at_reported_line" if (dist is not None and dist <= 3) else "consistent_line_drifted"
        elif verdict in ("source_file_missing", "token_missing_from_file"):
            verdict = "token_verbatim_but_chemistry_mismatch" if parse_ok else "parse_failure"
    if not rels:
        verdict = "no_source_located"
    return verdict, {"parse_ok": parse_ok, "chemistry_consistent": chem_match}, evidence


def relocate_unmatched(rec, cache, src_sha, all_files):
    """B2 再定位：未命中记录在全部笔记文件中找规范化相同反应，其次模糊候选。"""
    raw = rec.get("raw") or {}
    token = raw.get("raw_reaction_smiles") or ""
    rs, ps, _ = record_sides(rec)
    tok_r, tok_p = (None, None)
    if ">>" in token:
        a, _, b = token.partition(">>")
        tok_r, tok_p = canon_set(a), canon_set(b)
    parse_ok = all(x is not None for x in (rs, ps, tok_r, tok_p))
    located = set(rec.get("upstream_sources") or [])
    cond = norm(condition_snippet(rec))
    results = []
    verdict = "no_candidate"
    for rel in sorted(all_files):
        lines = cache.get_lines(rel)
        if lines is None:
            continue
        cur_sha = sha(cache.root / rel)
        drift_meta = src_sha.get(rel) not in (None, cur_sha)
        toks = cache.get_tokens(rel)
        exact = [t["line1"] for t in toks if t["r"] == tok_r and t["p"] == tok_p]
        verbatim = [i + 1 for i, ln in enumerate(lines) if token and token in ln]
        fuzzy = sorted(
            ((difflib.SequenceMatcher(None, norm(t["raw"]), norm(token)).ratio(), t) for t in toks),
            key=lambda x: -x[0]) if token else []
        cond_present = bool(cond) and cond in cache.get_text(rel)
        entry = {
            "file": rel, "was_located": rel in located, "present": True,
            "file_sha256_current": cur_sha,
            "file_sha256_matches_sources_json": not drift_meta,
            "token_verbatim_present": bool(verbatim), "verbatim_lines1": verbatim[:5],
            "canonical_reaction_found": bool(exact), "exact_lines1": exact[:5],
            "fuzzy_top2": [{"line1": t["line1"], "raw": t["raw"][:220], "ratio": round(r, 4)} for r, t in fuzzy[:2]],
            "condition_text_present": cond_present,
        }
        if entry["was_located"] or verbatim or exact or (fuzzy and fuzzy[0][0] >= 0.6) or cond_present:
            results.append(entry)
        if exact or verbatim:
            verdict = "canonical_reaction_found_elsewhere" if rel not in located else "canonical_found_in_located_file"
        elif fuzzy and fuzzy[0][0] >= 0.6 and verdict == "no_candidate":
            verdict = "fuzzy_candidate"
    if not parse_ok:
        verdict = "parse_failure"
    return verdict, results


def main():
    recs = json.loads(RECORDS.read_text(encoding="utf-8"))
    src_meta = json.loads(SOURCES.read_text(encoding="utf-8"))
    src_sha = {f["path"]: f["sha256"] for f in src_meta["files"]}
    cache = FileCache(ROOT)

    nr = [r for r in recs if r["kind"] == "note_reaction"]
    tf = sorted([r for r in nr if r.get("upstream_reaction_token_found")], key=lambda r: r["id"])
    tn = sorted([r for r in nr if not r.get("upstream_reaction_token_found")], key=lambda r: r["id"])

    literature_files = sorted(
        f["path"] for f in src_meta["files"]
        if "/docs/literature/" in f["path"] and f["path"].endswith(".md")
    )

    prescreened = []
    for rec in tf:
        verdict, checks, evidence = prescreen_found(rec, cache, src_sha)
        if verdict == "consistent_smiles_file_drift":
            raise SystemExit("STOP: frozen literature file drifted vs metadata/sources.json: see " + rec["id"])
        prescreened.append({
            "id": rec["id"], "kind": "note_reaction", "locator": rec.get("locator"),
            "classification": (rec.get("raw") or {}).get("classification"),
            "outcome_status": (rec.get("outcome") or {}).get("status"),
            "upstream_reported_line": rec.get("upstream_reported_line"),
            "prescreen_verdict_agent": verdict, "checks": checks, "evidence": evidence,
            "reviewer": "Cano/agent-prescreen (TASK-015-P5-B1, seed-registered sample for owner)",
        })
    verdicts = {}
    for p in prescreened:
        verdicts[p["prescreen_verdict_agent"]] = verdicts.get(p["prescreen_verdict_agent"], 0) + 1

    good = {"consistent_at_reported_line", "consistent_line_drifted"}
    discordant = [p for p in prescreened if p["prescreen_verdict_agent"] not in good]
    rng = random.Random(SEED)
    sample_ids = sorted(rng.sample([p["id"] for p in prescreened], SAMPLE_N))
    by_id = {p["id"]: p for p in prescreened}
    sample_id_set = set(sample_ids)
    owner_ids = sorted(sample_id_set | {p["id"] for p in discordant})
    owner_rows = [by_id[i] for i in owner_ids]

    # B2
    relocated = []
    for rec in tn:
        verdict, results = relocate_unmatched(rec, cache, src_sha, literature_files)
        relocated.append({
            "id": rec["id"], "kind": "note_reaction", "locator": rec.get("locator"),
            "source_status": rec.get("source_status"),
            "classification": (rec.get("raw") or {}).get("classification"),
            "relocation_verdict_agent": verdict, "files": results,
        })
    reloc_verdicts = {}
    for p in relocated:
        reloc_verdicts[p["relocation_verdict_agent"]] = reloc_verdicts.get(p["relocation_verdict_agent"], 0) + 1

    # B3 名称冲突
    dups = [r for r in recs if r["kind"] == "molecule_duplicate_names"]
    mols = [r for r in recs if r["kind"] == "molecule"]
    groups = []
    for d in dups:
        raw = d.get("raw") or {}
        mid, dup_of = raw.get("molecule_id"), raw.get("duplicate_of")
        peer = next((m for m in mols if (m.get("raw") or {}).get("molecule_id") == dup_of), None)
        groups.append({
            "duplicate_record_locator": d.get("locator"),
            "candidate": {"molecule_id": mid, "query_name": raw.get("query_name"),
                          "cid": raw.get("cid"), "pubchem_title": raw.get("pubchem_title"),
                          "inchikey": raw.get("inchikey"), "formula": raw.get("formula"),
                          "expectation_status": raw.get("expectation_status"),
                          "expectation_basis": raw.get("expectation_basis"),
                          "identity_status": raw.get("identity_status"),
                          "canonical_smiles": (d.get("structure") or {}).get("canonical_smiles")},
            "peer": None if peer is None else {
                "molecule_id": dup_of, "query_name": (peer.get("raw") or {}).get("query_name"),
                "cid": (peer.get("raw") or {}).get("cid"),
                "inchikey": (peer.get("structure") or {}).get("inchikey"),
                "canonical_smiles": (peer.get("structure") or {}).get("canonical_smiles"),
                "identity_status": (peer.get("raw") or {}).get("identity_status")},
            "owner_decision": "",
            "owner_notes": "",
        })

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "token_found_prescreen.jsonl").write_text(
        "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n" for p in prescreened), encoding="utf-8")
    (OUT / "token_unmatched_relocation.jsonl").write_text(
        "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n" for p in relocated), encoding="utf-8")
    (OUT / "name_conflict_evidence.json").write_text(
        json.dumps({"seed_note": "n/a", "groups": groups}, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8")

    with open(OUT / "owner_sample30.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["record_id", "classification", "reported_line1", "prescreen_verdict_agent",
                    "in_owner_sample", "source_file", "token_actual_lines1", "line_distance",
                    "chemistry_consistent", "token_reaction_snippet",
                    "context_snippet", "condition_text_present",
                    "owner_verdict(agree/disagree)", "owner_notes"])
        for p in owner_rows:
            ev = (p["evidence"] or [{}])[0]
            ctx = " | ".join(ev.get("context", [])[:2])[:400]
            w.writerow([p["id"], p.get("classification"), p.get("upstream_reported_line"),
                        p["prescreen_verdict_agent"], "sample" if p["id"] in sample_id_set else "discordant_auto_added",
                        ev.get("file"), ";".join(map(str, ev.get("token_actual_lines1") or [])),
                        ev.get("line_distance"), ev.get("chemistry_consistent"),
                        ev.get("token_reaction", ""), ctx, ev.get("condition_text_present"), "", ""])

    summary = {
        "task": "TASK-015-P5-B", "seed": SEED, "sample_n": SAMPLE_N,
        "token_found_total": len(tf), "prescreen_verdicts": verdicts,
        "discordant_auto_added": len(discordant),
        "owner_rows_total": len(owner_rows),
        "token_unmatched_total": len(tn), "relocation_verdicts": reloc_verdicts,
        "duplicate_name_groups": len(groups),
        "reconciliation_note": "冻结数据自 TASK-003 起即为 2 组 duplicate_names；后续文档「3 条名称冲突」未见第三组冻结记录，登记为表述差异待所有者确认。",
        "boundary": "agent prescreen only; no human_reviewed field is filled by this build",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    decision_md = ["# 名称冲突决议表（TASK-015-P5-B3）", "",
                   "冻结数据（data/derived/v3，TASK-003 准入）共 2 组 molecule_duplicate_names，涉及 4 个 FGM 分子 ID。",
                   "后续文档（PAPER_ROADMAP、WORKBENCH_ROADMAP、REPORT-012）表述「3 条名称冲突」；本次核查未在冻结数据与其源 summary.json 中找到第三组，登记为文档表述差异，请所有者在决议时一并确认是否需要追溯。", ""]
    for i, g in enumerate(groups, 1):
        c, p = g["candidate"], g["peer"]
        decision_md += [f"## 组 {i}：{c['query_name']}（{c['molecule_id']}） vs {p['query_name'] if p else '?'}（{p['molecule_id'] if p else '?'}）",
                        "",
                        f"- 候选：query_name=`{c['query_name']}`，CID={c['cid']}，PubChem title={c['pubchem_title']}，InChIKey={c['inchikey']}，identity_status={c['identity_status']}",
                        f"- 对手：query_name=`{p['query_name'] if p else '?'}`，CID={p['cid'] if p else '?'}，InChIKey={p['inchikey'] if p else '?'}",
                        f"- 同 CID：{str(c['cid'] == (p['cid'] if p else None))}；同 InChIKey：{str(c['inchikey'] == (p['inchikey'] if p else None))}",
                        f"- expectation：{c['expectation_status']}（basis: {c['expectation_basis']}）",
                        f"- 候选 SMILES：`{c['canonical_smiles']}`",
                        f"- 对手 SMILES：`{p['canonical_smiles'] if p else '?'}`",
                        "",
                        "**可选项**：A) 合并为同一分子身份，保留同义词映射；B) 保持两条独立候选并标注同义/歧义关系；C) 否决其中一条的身份 resolution（请指明哪条与理由）。",
                        "",
                        f"**所有者决议**：{g['owner_decision'] or '（待填 A/B/C）'}",
                        f"**备注**：{g['owner_notes'] or '（待填）'}",
                        ""]
    decision_md += ["---", "决议交回方式：直接编辑本文件的「所有者决议/备注」两行，或由 Cano 按所有者会话指示代录（代录须引用会话原话，不冒充 human_reviewed）。", ""]
    (OUT / "name_conflict_decision.md").write_text("\n".join(decision_md), encoding="utf-8")

    manifest = {
        "task": "TASK-015-P5-B", "seed": SEED, "sample_n": SAMPLE_N,
        "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in [RECORDS, SOURCES]},
        "outputs_sha256": {f.name: sha(f) for f in sorted(OUT.iterdir()) if f.is_file() and f.name != "manifest.json"},
        "boundary": summary["boundary"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
