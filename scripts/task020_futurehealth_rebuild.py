#!/usr/bin/env python3
"""TASK-020 FutureHealth M0+P0 受控迁移工具（在服务端 /home/ljx 主机上运行）。

约束：
- 只读 /home/ljx/FlavoRetro（含 outputs/restructure 预迁移包）；
- 只写 /home/ljx/FutureHealth；
- 不对旧库做任何 glob 扫描（避免 AppleDouble 旁车），P0 文件全部显式列出；
- 仅用标准库；以主脚本直接运行，不在旧库产生 __pycache__。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FLAVOR = Path("/home/ljx/FlavoRetro")
PKG = FLAVOR / "outputs" / "restructure" / "future-health-20261015"
TARGET = Path("/home/ljx/FutureHealth")
SNAP = "reference/flavoretro-snapshot"

# P0 CORE_REUSE（23 个源文件；目标 = SNAP 下保持原相对路径）
P0_SOURCES = [
    "LICENSE",
    "LICENSES/README.md",
    "data/derived/v3/manifest.json",
    "data/derived/v3/records.json",
    "environment/requirements-linux-py310.lock",
    "flavoretro/contracts.py",
    "flavoretro/database.py",
    "flavoretro/policies.py",
    "flavoretro/resources.py",
    "flavoretro/reviewed_resources.py",
    "flavoretro/search.py",
    "flavoretro/service.py",
    "flavoretro/topology.py",
    "flavoretro/worker.py",
    "flavoretro/workspace.py",
    "metadata/active.json",
    "metadata/note-relocations.json",
    "metadata/release.json",
    "metadata/sources.json",
    "outputs/researchwrite/flavoretro-future-health-20261015/02_evidence_table.md",
    "outputs/researchwrite/flavoretro-future-health-20261015/exports/FlavoRetro_FutureHealth_Feasibility_20261015.md",
    "outputs/researchwrite/flavoretro-future-health-20261015/sources/README.md",
    "pyproject.toml",
]
assert len(set(P0_SOURCES)) == 23, "P0 清单必须恰好 23 项"

# 受控副本中禁入 Git 的数据层（原始/受限数据不入 Git）
GIT_IGNORED_COPY_PREFIXES = (
    "reference/flavoretro-snapshot/data/",
    "reference/flavoretro-snapshot/metadata/",
)

SKELETON_DIRS = [
    "docs/decision",
    "docs/curriculum",
    "docs/cases/isoquercitrin",
    "docs/policy/ilab-2026",
    "src/futurehealth/chemistry",
    "src/futurehealth/evidence",
    "src/futurehealth/experiment",
    "src/futurehealth/teaching",
    "src/futurehealth/platform",
    "frontend/student",
    "frontend/teacher",
    "tests",
    "migrations",
    "data/registries",
    "data/private/sources",
    "data/private/cases/isoquercitrin",
]
# data/private/ 整目录 Git 忽略，不放 .gitkeep（保持 Git 树内不出现该路径）
GITKEEP_DIRS = [d for d in SKELETON_DIRS if not d.startswith("data/private/")]

PACKAGE_FILES = [
    "DELIVERY_HASHES.json",
    "DIRECTORY_DECISION_SUMMARY.csv",
    "EXACT_TARGET_PRODUCT_REACTIONS.csv",
    "HIGH_PRIORITY_MIGRATION_LIST.csv",
    "INVENTORY_SUMMARY.json",
    "MASTER_FILE_INVENTORY.csv",
    "NON_MIGRATION_POLICY.md",
    "PUBLICATIONS_AND_GAPS.md",
    "REACTION_CANDIDATE_SCREEN.csv",
    "README.md",
    "REBUILD_EXECUTION_LIST.md",
    "SOURCE_INTAKE_123.csv",
    "TARGET_SCREEN_SUMMARY.json",
    "VERIFIED_PRIORITY_HASHES.csv",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str, cwd: Path = FLAVOR) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True
    ).stdout


def is_git_ignored_copy(rel: str) -> bool:
    return rel.startswith(GIT_IGNORED_COPY_PREFIXES)


def copy_targets(rel: str) -> list[str]:
    targets = [f"{SNAP}/{rel}"]
    if rel == "LICENSE":
        targets.append("LICENSE")  # 新仓库顶层许可 = 同一 Apache-2.0 文本
    return targets


def phase_build() -> int:
    # 0. 预检：目标必须不存在或为空；输入必须齐全
    known_artifacts = {f"{SNAP}/{rel}" for rel in P0_SOURCES} | {"LICENSE"} | {
        f"{d}/.gitkeep" for d in GITKEEP_DIRS} | {
        "migrations/mapping.csv", "migrations/p1_pending_review.csv",
        "migrations/flavoretro-baseline.json", "migrations/verification-m0p0.json",
        "data/registries/source_registry.csv", "data/registries/case_admission.csv"}
    if TARGET.exists() and any(TARGET.iterdir()):
        unknown = [str(p.relative_to(TARGET)) for p in TARGET.rglob("*")
                   if p.is_file() and not p.name.startswith("._") and p.name != ".DS_Store"
                   and str(p.relative_to(TARGET)) not in known_artifacts]
        if unknown:
            print(json.dumps({"phase": "build", "ok": False,
                              "error": "target_has_unknown_files", "unknown": unknown}))
            return 2
    TARGET.mkdir(parents=True, exist_ok=True)
    problems = []
    for rel in PACKAGE_FILES:
        if not (PKG / rel).is_file():
            problems.append(f"package_file_missing:{rel}")
    for rel in P0_SOURCES:
        if not (FLAVOR / rel).is_file():
            problems.append(f"p0_source_missing:{rel}")
    if problems:
        print(json.dumps({"phase": "build", "ok": False,
                          "error": "preflight_failed", "problems": problems}))
        return 2

    with (PKG / "VERIFIED_PRIORITY_HASHES.csv").open(newline="", encoding="utf-8-sig") as f:
        verified = {r["source_path"]: r for r in csv.DictReader(f)}
    with (PKG / "HIGH_PRIORITY_MIGRATION_LIST.csv").open(newline="", encoding="utf-8-sig") as f:
        high = {r["source_relative_path"]: r for r in csv.DictReader(f)}

    # 1. 骨架
    for d in SKELETON_DIRS:
        (TARGET / d).mkdir(parents=True, exist_ok=True)
    for d in GITKEEP_DIRS:
        (TARGET / d / ".gitkeep").write_text("", encoding="utf-8")

    # 2. P0 复制 + SHA 验证（先验源，mismatch 则该文件不复制并登记）
    copy_results = []
    mismatch = []
    for rel in P0_SOURCES:
        src = FLAVOR / rel
        expected = verified.get(rel, {}).get("current_sha256", "")
        actual = sha256_file(src)
        ok = (not expected) or (actual == expected)
        entry = {"source": rel, "source_sha256": actual,
                 "expected_sha256": expected or None,
                 "source_match_verified": ok, "targets": []}
        if not ok:
            mismatch.append(rel)
        else:
            for trel in copy_targets(rel):
                tpath = TARGET / trel
                tpath.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, tpath)
                tsha = sha256_file(tpath)
                entry["targets"].append({"target": trel, "sha256": tsha,
                                         "match": tsha == actual,
                                         "git_tracked": not is_git_ignored_copy(trel)})
        copy_results.append(entry)

    # 3. mapping.csv（每 (源,目标) 一行）
    with (TARGET / "migrations" / "mapping.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["source_repo", "source_relative_path", "target_relative_path",
                    "decision", "priority", "sha256", "size_bytes", "license_gate",
                    "copied", "git_tracked", "note"])
        for rel in P0_SOURCES:
            h = high.get(rel, {})
            v = verified.get(rel, {})
            for trel in copy_targets(rel):
                copied = rel not in mismatch
                w.writerow([
                    "/home/ljx/FlavoRetro", rel, trel,
                    h.get("decision", "CORE_REUSE"), h.get("priority", "P0"),
                    sha256_file(TARGET / trel) if copied else (v.get("current_sha256") or ""),
                    (TARGET / trel).stat().st_size if copied else h.get("size_bytes", ""),
                    h.get("license_gate", ""), str(copied).lower(),
                    str(not is_git_ignored_copy(trel)).lower(),
                    "受控参考副本（TASK-020 M0+P0）；复用需新合同" if copied
                    else "SHA mismatch，未复制，等待处置",
                ])

    # 4. p1_pending_review.csv（只登记，不复制）
    p1_rows = sorted((h for h in high.values() if h.get("decision") == "SELECTIVE_REVIEW"),
                     key=lambda r: r["source_relative_path"])
    with (TARGET / "migrations" / "p1_pending_review.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["source_relative_path", "size_bytes", "priority", "sha256_if_known",
                    "status", "copied", "review_gate", "reason"])
        p1_written = []
        for h in p1_rows:
            row = [h["source_relative_path"], h["size_bytes"], h["priority"],
                   h["sha256_if_known"], "pending_review", "false",
                   "teacher_or_owner_review_required_before_copy", h["reason"]]
            p1_written.append(row)
            w.writerow(row)

    # 5. source_registry.csv（与包内 SOURCE_INTAKE_123.csv 字节一致）
    reg_src_sha = sha256_file(PKG / "SOURCE_INTAKE_123.csv")
    shutil.copyfile(PKG / "SOURCE_INTAKE_123.csv",
                    TARGET / "data" / "registries" / "source_registry.csv")
    reg_tgt_sha = sha256_file(TARGET / "data" / "registries" / "source_registry.csv")
    with (PKG / "SOURCE_INTAKE_123.csv").open(newline="", encoding="utf-8-sig") as f:
        n_sources = sum(1 for _ in csv.DictReader(f))

    # 6. case_admission.csv（1 案例头 + 21 条产物结构命中；全部待教师审）
    summary = json.loads((PKG / "TARGET_SCREEN_SUMMARY.json").read_text(encoding="utf-8"))
    adm_rows = [{
        "admission_id": "FH-CASE-001", "item_kind": "teaching_case",
        "name_or_case": summary["target_name"], "ref_id": summary["matched_molecule_id"],
        "source_path": "", "source_sha256": "", "locator": "TARGET_SCREEN_SUMMARY.json",
        "reference_doi_if_recorded": "", "historical_yield_raw": "", "yield_status": "",
        "identity_or_review_status": summary["molecule_identity_status"],
        "admission_status": "pending_teacher_review", "human_review_status": "not_performed",
        "limitation": "主教学案例为调研推荐，待教师论证；分子身份人工核对待完成",
        "provenance": "FlavoRetro/outputs/restructure/future-health-20261015/TARGET_SCREEN_SUMMARY.json",
    }]
    with (PKG / "EXACT_TARGET_PRODUCT_REACTIONS.csv").open(newline="", encoding="utf-8-sig") as f:
        for i, r in enumerate(csv.DictReader(f), start=1):
            adm_rows.append({
                "admission_id": f"FH-R-{i:03d}", "item_kind": "reaction_record",
                "name_or_case": summary["target_name"], "ref_id": r["record_id"],
                "source_path": r["source_path"], "source_sha256": r["source_sha256"],
                "locator": r["locator"],
                "reference_doi_if_recorded": r["reference_doi_if_recorded"],
                "historical_yield_raw": r["historical_yield_raw"],
                "yield_status": r["yield_status"],
                "identity_or_review_status": r["review_status"],
                "admission_status": "pending_teacher_review",
                "human_review_status": r["human_review_status"],
                "limitation": r["limitation"],
                "provenance": "FlavoRetro/outputs/restructure/future-health-20261015/EXACT_TARGET_PRODUCT_REACTIONS.csv",
            })
    with (TARGET / "data" / "registries" / "case_admission.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(adm_rows[0].keys()))
        w.writeheader()
        w.writerows(adm_rows)

    # 7. P1 零复制断言
    p1_leaks = []
    for h in p1_rows:
        rel = h["source_relative_path"]
        for cand in (TARGET / SNAP / rel, TARGET / rel):
            if cand.exists():
                p1_leaks.append(str(cand))

    # 8. M0 基线（旧库事实，只读采集）
    head = git("rev-parse", "HEAD").strip()
    status = git("status", "--porcelain")
    baseline = {
        "captured_at_utc": now_utc(),
        "flavor_repo": "/home/ljx/FlavoRetro",
        "flavor_head": head,
        "flavor_dirty_entries": len(status.splitlines()),
        "flavor_porcelain_sha256": hashlib.sha256(status.encode("utf-8")).hexdigest(),
        "restructure_package_dir": str(PKG),
        "restructure_package_files_sha256": {rel: sha256_file(PKG / rel) for rel in PACKAGE_FILES},
        "uncommitted_workspace_preserved": True,
        "notes": "M0：旧库未提交工作区原样保全，不清理不重置；本文件只登记事实，不改变旧库。",
    }
    (TARGET / "migrations" / "flavoretro-baseline.json").write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 9. verification-m0p0.json
    verification = {
        "verified_at_utc": now_utc(),
        "phase": "build",
        "p0_all_match": not mismatch,
        "p0_mismatch": mismatch,
        "p0_targets": copy_results,
        "p1_rows": len(p1_rows),
        "p1_all_pending": all(r[4] == "pending_review" for r in p1_written),
        "p1_content_copied": bool(p1_leaks),
        "p1_leaks": p1_leaks,
        "source_registry": {"rows": n_sources, "sha256": reg_tgt_sha,
                            "byte_equal_to_package": reg_src_sha == reg_tgt_sha},
        "case_admission": {"rows": len(adm_rows),
                           "all_pending_teacher_review": all(
                               r["admission_status"] == "pending_teacher_review" for r in adm_rows)},
        "skeleton_dirs": SKELETON_DIRS,
        "gitkeep_dirs": GITKEEP_DIRS,
        "ok": (not mismatch) and (not p1_leaks) and len(p1_rows) == 49
              and n_sources == 123 and len(adm_rows) == 22
              and all(t["match"] for e in copy_results for t in e["targets"]),
    }
    (TARGET / "migrations" / "verification-m0p0.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "build", "ok": verification["ok"],
                      "p0_mismatch": mismatch, "p1_rows": len(p1_rows),
                      "source_registry_rows": n_sources,
                      "case_admission_rows": len(adm_rows)}))
    return 0 if verification["ok"] else 2


def phase_verify_post() -> int:
    head = git("rev-parse", "HEAD", cwd=TARGET).strip()
    tracked = git("ls-files", cwd=TARGET).splitlines()
    checks = [{"check": "head_present", "pass": bool(head), "head": head}]

    forbidden = [p for p in tracked if p.startswith(
        ("data/private/", "reference/flavoretro-snapshot/data/",
         "reference/flavoretro-snapshot/metadata/"))]
    checks.append({"check": "no_forbidden_paths_tracked", "pass": not forbidden,
                   "violations": forbidden})

    snap_expected = sorted(f"{SNAP}/{rel}" for rel in P0_SOURCES
                           if not is_git_ignored_copy(f"{SNAP}/{rel}"))
    snap_actual = sorted(p for p in tracked if p.startswith(SNAP + "/"))
    checks.append({"check": "snapshot_tracked_set", "pass": snap_actual == snap_expected,
                   "expected_count": len(snap_expected), "actual_count": len(snap_actual),
                   "missing": sorted(set(snap_expected) - set(snap_actual)),
                   "extra": sorted(set(snap_actual) - set(snap_expected))})
    checks.append({"check": "top_level_license_tracked",
                   "pass": "LICENSE" in tracked and (TARGET / "LICENSE").is_file()})
    checks.append({"check": "migrations_tracked",
                   "pass": all(p in tracked for p in (
                       "migrations/mapping.csv", "migrations/p1_pending_review.csv",
                       "migrations/flavoretro-baseline.json", "migrations/verification-m0p0.json"))})
    checks.append({"check": "registries_tracked",
                   "pass": "data/registries/source_registry.csv" in tracked
                           and "data/registries/case_admission.csv" in tracked})
    checks.append({"check": "authored_docs_tracked",
                   "pass": all(p in tracked for p in (
                       "README.md", "LICENSES/README.md",
                       "docs/decision/ADR-0001-futurehealth-rebuild.md", ".gitignore"))})

    # 数据副本在工作区存在但未跟踪（受控副本层完整，Git 边界同时成立）
    checks.append({"check": "v3_copy_present_untracked",
                   "pass": (TARGET / "reference/flavoretro-snapshot/data/derived/v3/records.json").is_file()
                           and "reference/flavoretro-snapshot/data/derived/v3/records.json" not in tracked})

    # 通过标记审计
    markers = []
    for p in sorted(TARGET.rglob("*")):
        if p.is_file() and p.suffix in {".md", ".csv", ".json"} and not p.name.startswith("._"):
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                markers.append(f"undecodable:{p}")
                continue
            for bad in ("human_reviewed=true", "human_reviewed: true",
                        "teacher_approved", "教师已审通过"):
                if bad in text:
                    markers.append(f"{p}:{bad}")
    checks.append({"check": "no_approval_markers", "pass": not markers, "violations": markers})

    ok = all(c["pass"] for c in checks)
    verification = {"verified_at_utc": now_utc(), "phase": "verify_post", "head": head,
                    "tracked_file_count": len(tracked), "checks": checks, "ok": ok}
    (TARGET / "migrations" / "verification-final.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "verify_post", "ok": ok,
                      "tracked_file_count": len(tracked), "head": head}))
    return 0 if ok else 2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["build", "verify-post"], required=True)
    args = ap.parse_args()
    sys.exit(phase_build() if args.phase == "build" else phase_verify_post())


if __name__ == "__main__":
    main()
