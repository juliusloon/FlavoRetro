"""TASK-016-P7 reaction-level eligibility ledger (v1, offline consolidation).

Purpose: make the CURRENT disposition of every located reaction/claim under the
named 16 historical sources plus the 1 prospective new C source EXPLICIT, using
only already-existing machine artifacts. No source file is read again, no HTTP is
issued, no scope is modified, and no new chemical judgement is introduced: every
row's status is derived from an upstream artifact field, and rows that were never
assessed are marked `not_yet_assessed` instead of being silently dropped.

Hard constraints honoured here:
  * G4 scope SHAs untouched;
  * no new curation exposure (no raw source read);
  * no fresh/scientific promotion (admitted_total stays 0);
  * every source carries an explicit residual `not_yet_assessed` row;
  * prior artifacts are never rewritten, only cited by path+SHA.

Outputs are immutable: any pre-existing output path aborts the run.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from operate import event, write  # noqa: E402

T = "TASK-016-P7"
B = Path("outputs/task016-p7/v1")
OUT = B / "reaction_eligibility_ledger_v1"

# ---------------------------------------------------------------- inputs ----
V2 = B / "G6_owner_16_historical_source_review_v2"
PRO = B / "prospective_G6_round_20261011_v1"
R68 = B / "C/E02/fresh/C-E02-R68-two-historical-PMC-science-v1"
R3DOC = B / "manual_grabbed_R3_A3_reconciled_20261011/R3_A3_4original_crosscheck_and_G6_documentary_questions.json"
V32INV = B / "verification-v32-pending-original-source-inventory/named_pending_original_inventory.json"
PROG = B / "report_snapshots/progress-G6-new-source-v1.json"

INPUTS = [
    V2 / "C/G6_bounded_scientific_dispositions.json",
    V2 / "SS/G6_bounded_scientific_dispositions.json",
    V2 / "C/role_A6_G6_bounded_screen.json",
    V2 / "SS/role_A6_G6_bounded_screen.json",
    V2 / "A11_original_source_verification.json",
    PRO / "C_PMC13564134_A3_original_front_and_exposure.json",
    PRO / "C_PMC13564134_A4_independent_source_read.json",
    PRO / "C_PMC13564134_A5_independent_source_read.json",
    PRO / "C_PMC13564134_A6_source_name_closure_and_graph_gaps.json",
    R68 / "A6/scientific_reconciliation_completed.json",
    R68 / "A6/PMC2709393/source_evidence_and_eligibility.json",
    R68 / "A6/PMC7720146/source_evidence_and_eligibility.json",
    R3DOC,
    V32INV,
    PROG,
    B / "C/E02/stages/G4_SCOPE_FREEZE.json",
    B / "SS/E02/stages/G4_SCOPE_FREEZE.json",
    B / "epoch_ledger.jsonl",
]

# isoorientin name-exposure ledgers (read-only, for the structural-vs-name audit)
EXPOSURE_LEDGERS = [
    B / "SS/E01_permanent_exposure/permanent_chemical_exposure_ledger.jsonl",
    B / "SS/E01_permanent_exposure/v2/permanent_chemical_exposure_ledger.jsonl",
    B / "epochs/SS-E01/closure_resolution_v1/effective_permanent_exposure_ledger.jsonl",
]

# --------------------------------------------------- judgement-free maps ----
REASON_CLASS = {
    "source_reaction_not_qualified": "located_claim_not_a_source_complete_reaction",
    "scope_mismatch_c6_direct": "frozen_scope_site_mismatch",
    "scope_mismatch_SS_O2": "frozen_scope_site_mismatch",
    "source_identity_attachment_pending": "source_identity_attachment_pending",
    "linkage_O2_structure_pending": "linkage_site_structure_pending",
}

GATES_BY_CLASS = {
    "frozen_scope_site_mismatch": [
        "G6-structure-complete",
        "G6-runtime-complete",
        "G6-scope-applicable",
    ],
    "located_claim_not_a_source_complete_reaction": [
        "G6-A4A5-dual-independent-graph",
        "G6-structure-complete",
        "G6-runtime-complete",
        "G6-scope-applicable",
    ],
    "source_identity_attachment_pending": [
        "G6-source-identity-closure",
        "G6-structure-complete",
        "G6-A4A5-dual-independent-graph",
    ],
    "linkage_site_structure_pending": [
        "G6-bond-atom-identity",
        "G6-stereo-anomer-confirmation",
        "G6-structure-complete",
        "G6-runtime-complete",
        "G6-scope-applicable",
    ],
    "graph_and_name_closure_missing": [
        "G6-A4A5-dual-independent-graph",
        "G6-structure-complete",
        "G6-source-identity-closure",
        "G6-runtime-complete",
        "G7-leakage-zero",
    ],
    "name_level_exposure_structural_level_unresolved": [
        "G7-leakage-zero",
        "G6-source-identity-closure",
    ],
    "never_assessed": [
        "G6-source-identity-closure",
        "G6-A4A5-dual-independent-graph",
        "G6-structure-complete",
        "G6-runtime-complete",
        "G6-scope-applicable",
        "G7-leakage-zero",
    ],
}

# upstream `disposition` -> ledger `status` (mechanical, no re-judgement)
STATUS_FROM_UPSTREAM = {
    "rejected_for_current_scope_example": "rejected",
    "deferred": "deferred",
    "excluded_from_fresh": "rejected",
}

NEW_C_SOURCE = {
    "source_ref": "PROSPECTIVE:C:PMC13564134",
    "family": "C",
    "source_kind": "prospective_new_original",
    "source_id": "PMC13564134",
    "verified_DOI": "10.1016/j.abiote.2026.100085",
    "frozen_scope": "C-E02",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(p: Path) -> str:
    return str(Path(p))


def load(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def put(path: Path, obj, *, jsonl: bool = False) -> None:
    target = ROOT / path
    if target.exists():
        raise RuntimeError("immutable output already exists: " + str(path))
    if jsonl:
        body = "".join(
            json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in obj
        )
    else:
        body = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    write(T, str(path), body)


# --------------------------------------------------------- isoorientin ----
def audit_isoorientin() -> dict:
    """Raw-ledger re-derivation: row instances vs distinct records vs graph content."""
    per_file = {}
    keys = {}
    graph_fields_present = set()
    for f in EXPOSURE_LEDGERS:
        lines = Path(f).read_text(encoding="utf-8").splitlines()
        rows = []
        for i, line in enumerate(lines, 1):
            if "isoorientin" not in line.lower():
                continue
            rec = json.loads(line)
            sig = json.dumps(
                {
                    k: rec.get(k)
                    for k in (
                        "assay_id",
                        "closure_tokens",
                        "record_type",
                        "acceptor_source_name",
                        "donor_source_name",
                    )
                },
                sort_keys=True,
            )
            h = hashlib.sha256(sig.encode()).hexdigest()
            keys.setdefault(h, []).append(f"{f}:{i}")
            rows.append(i)
            for gf in ("acceptor_smiles", "donor_smiles", "product_smiles",
                       "target_graph", "site", "reaction_signature", "reaction_id"):
                if rec.get(gf) is not None:
                    graph_fields_present.add(gf)
        per_file[str(f)] = {"file_lines": len(lines), "isoorientin_rows": len(rows),
                            "row_lines": rows}
    return {
        "row_instances_total": sum(v["isoorientin_rows"] for v in per_file.values()),
        "distinct_records": len(keys),
        "per_file": per_file,
        "structural_graph_field_names_observed_non_null": sorted(graph_fields_present),
        "declared_count_in_upstream_A6": 36,
        "enumerated_rows_in_upstream_A6": 32,
    }


# -------------------------------------------------------------- builder ----
def build():
    pre = {
        "task": T,
        "layer": "reaction_eligibility_ledger_v1",
        "kind": "offline_consolidation_of_existing_dispositions",
        "at": now(),
        "stage_context": "G6_IDENTITY_STRUCTURE_ADMIT",
        "stage_transition_performed": False,
        "authorization": "human_direct",
        "authorization_note": "Owner selected option A (offline per-article per-reaction eligibility ledger) and human_direct record for this round.",
        "purpose": "Make every located reaction/claim disposition explicit, including explicit not_yet_assessed residuals.",
        "scope": {
            "denominator_named_historical": 16,
            "denominator_prospective_new": 1,
            "total_sources": 17,
            "families": ["C", "SS"],
        },
        "no_new_source_read": True,
        "no_new_http": True,
        "no_raw_pdf_opened": True,
        "scope_modified": False,
        "mcts_untouched": True,
        "new_chemistry_judgement_introduced": False,
        "status_source": "derived_from_upstream_disposition_fields_only",
        "immutable_outputs": True,
        "prior_artifacts_never_rewritten": True,
        "stop_conditions": [
            "any input SHA mismatch",
            "any evidence pointer SHA mismatch or missing file",
            "any admitted>0 without full A4/A5/A6 + runtime completeness",
            "any row asserting article-level exclusion",
        ],
        "non_goals": [
            "creating a fresh holdout",
            "modifying G4 frozen scope",
            "running A/B/E or MCTS",
            "promoting human_reviewed or independent chemistry",
            "Git commit/push",
        ],
    }
    put(OUT / "precontract.json", pre)

    input_manifest = {
        "task": T,
        "layer": "reaction_eligibility_ledger_v1",
        "at": now(),
        "inputs": [
            {"path": rel(p), "sha256": sha256_file(ROOT / p), "bytes": (ROOT / p).stat().st_size}
            for p in INPUTS
        ],
        "exposure_ledgers_read_only": [
            {"path": rel(p), "sha256": sha256_file(ROOT / p)} for p in EXPOSURE_LEDGERS
        ],
    }
    put(OUT / "INPUT_MANIFEST.json", input_manifest)
    in_sha = {r["path"]: r["sha256"] for r in input_manifest["inputs"]}

    rows: list[dict] = []
    coverage: list[dict] = []

    # ---- 16 named historical sources -------------------------------------
    for family in ("C", "SS"):
        disp_path = V2 / family / "G6_bounded_scientific_dispositions.json"
        role_path = V2 / family / "role_A6_G6_bounded_screen.json"
        disp = load(disp_path)
        role = load(role_path)
        disp_sha = in_sha[rel(disp_path)]
        role_sha = in_sha[rel(role_path)]

        for src in disp["sources"]:
            no = src["owner_source_number"]
            sref = f"OWNER16:{family}:{no}"
            upstream = src["disposition"]
            status = STATUS_FROM_UPSTREAM[upstream]
            gate = src["bounded_reaction_scope_gate"]
            rclass = REASON_CLASS[gate]
            gates = list(GATES_BY_CLASS[rclass]) + ["G7-fresh-definition-historical-exposure"]

            layers = [
                {
                    "role": "A6",
                    "layer": "owner16_bounded_source_reaction_disposition",
                    "path": rel(disp_path),
                    "sha256": disp_sha,
                    "upstream_disposition": upstream,
                    "upstream_scope_gate": gate,
                }
            ]
            # C-11 / C-12 carry a second, independent-text-agreement assessment
            if family == "C" and no in {"11", "12"}:
                pmc = src["owner_historical_DOI_or_PMC"]
                ev = R68 / f"A6/{pmc}/source_evidence_and_eligibility.json"
                rec = R68 / "A6/scientific_reconciliation_completed.json"
                layers.append(
                    {
                        "role": "A6",
                        "layer": "R68_historical_PMC_dual_text_agreement",
                        "path": rel(ev),
                        "sha256": in_sha[rel(ev)],
                        "upstream_disposition": load(ev)["fresh_disposition"],
                        "exact_dual_text_agreement": load(ev)["exact_dual_text_agreement"],
                        "fresh_admitted": load(ev)["fresh_admitted"],
                        "reconciliation_path": rel(rec),
                        "reconciliation_sha256": in_sha[rel(rec)],
                    }
                )

            row = {
                "row_id": f"REL-{family}-{no}-R1",
                "row_kind": "located_example_reaction",
                "source_ref": sref,
                "family": family,
                "frozen_scope": src["scope"],
                "status": status,
                "status_source": "upstream_disposition_field",
                "upstream_disposition": upstream,
                "reason_code": gate,
                "reason_class": rclass,
                "observed_report": src["observed_report"],
                "located_claim_kind": src["bounded_example_kind"],
                "evidence_pointers": [
                    {
                        "path": rel(disp_path),
                        "sha256": disp_sha,
                        "locator": f"PDF_page={l['PDF_page']};anchor={l['anchor_pattern']}",
                        "source_page_SHA256": l.get("source_page_SHA256"),
                    }
                    for l in src.get("original_evidence_loci", [])
                ],
                "source_original": {
                    "path": src["source_pdf"],
                    "sha256": src["source_sha256"],
                    "A3_publication_identity": src["source_A3_publication_identity"],
                    "verified_DOI": src.get("verified_DOI"),
                },
                "assessment_layers": layers,
                "structural_missing_fields": src.get("structural_missing_fields", []),
                "blocking_gates": gates,
                "runtime_complete": False,
                "scope_applicable": bool(src.get("scope_applicable_full_reaction_pass")),
                "fresh_eligible": bool(src.get("fresh_post_scope_eligible")),
                "article_level_exclusion_claimed": False,
                "human_reviewed": False,
                "raw_source_read_in_this_round": False,
                "new_chemistry_judgement": False,
                "notes": (
                    "Disposition applies ONLY to the located example/claim; the article is "
                    "not declared devoid of other chemistry."
                ),
            }
            rows.append(row)

            # explicit residual: everything not located in this article
            rows.append(
                {
                    "row_id": f"REL-{family}-{no}-RESIDUAL",
                    "row_kind": "article_residual_unassessed",
                    "source_ref": sref,
                    "family": family,
                    "frozen_scope": src["scope"],
                    "status": "not_yet_assessed",
                    "status_source": "explicit_gap_marker",
                    "upstream_disposition": None,
                    "reason_code": "article_reaction_universe_not_enumerated",
                    "reason_class": "never_assessed",
                    "observed_report": (
                        "Reactions in this article other than the located example were not "
                        "enumerated; upstream flags all_article_reactions_exhaustively_reviewed=false."
                    ),
                    "evidence_pointers": [
                        {
                            "path": rel(disp_path),
                            "sha256": disp_sha,
                            "locator": "sources[owner_source_number=%s]" % no,
                        }
                    ],
                    "source_original": {
                        "path": src["source_pdf"],
                        "sha256": src["source_sha256"],
                    },
                    "assessment_layers": [],
                    "structural_missing_fields": src.get("structural_missing_fields", []),
                    "blocking_gates": list(GATES_BY_CLASS["never_assessed"]),
                    "runtime_complete": False,
                    "scope_applicable": False,
                    "fresh_eligible": False,
                    "article_level_exclusion_claimed": False,
                    "human_reviewed": False,
                    "raw_source_read_in_this_round": False,
                    "new_chemistry_judgement": False,
                    "notes": "Zero-as-omission marker: unenumerated reactions are recorded, not assumed absent.",
                }
            )

            coverage.append(
                {
                    "source_ref": sref,
                    "source_kind": "owner_named_historical",
                    "family": family,
                    "owner_source_number": no,
                    "verified_DOI": src.get("verified_DOI"),
                    "owner_historical_DOI_or_PMC": src.get("owner_historical_DOI_or_PMC"),
                    "source_A3_publication_identity": src["source_A3_publication_identity"],
                    "source_file": src["source_pdf"],
                    "source_sha256": src["source_sha256"],
                    "frozen_scope": src["scope"],
                    "historical_development_exposure": True,
                    "current_epoch_fresh_eligible": False,
                    "located_reaction_rows": 1,
                    "located_reaction_status_counts": {status: 1},
                    "admitted_rows": 0,
                    "article_reaction_universe_exhausted": False,
                    "complete_article_all_reactions_negatively_screened": bool(
                        src.get("complete_article_all_reactions_negatively_screened")
                    ),
                    "residual_unassessed_row_id": f"REL-{family}-{no}-RESIDUAL",
                    "runtime_completeness_verified": False,
                    "scope_applicability_verified": False,
                    "full_G6_passed": 0,
                    "G7_eligible": bool(src.get("G7_eligibility")),
                    "next_action": (
                        "G5 prospective novel-source A3/A4/A5/A6 only; this source can serve as "
                        "design/build support, never as fresh holdout."
                    ),
                }
            )

        assert len(disp["sources"]) == 8, family
        assert role["counts"]["processed"] == 8, family
        assert role["counts"]["passed"] == 0, family
        assert role["counts"]["rejected"] == 7 and role["counts"]["pending"] == 1, family

    # ---- prospective new C source: PMC13564134 ---------------------------
    a6p = PRO / "C_PMC13564134_A6_source_name_closure_and_graph_gaps.json"
    a6 = load(a6p)
    a6_sha = in_sha[rel(a6p)]
    sref = NEW_C_SOURCE["source_ref"]
    rows.append(
        {
            "row_id": "REL-C-NEW01-R1",
            "row_kind": "located_example_reaction",
            "source_ref": sref,
            "family": "C",
            "frozen_scope": NEW_C_SOURCE["frozen_scope"],
            "status": "deferred",
            "status_source": "upstream_disposition_field",
            "upstream_disposition": "G6_scope_claim:" + a6["G6_scope_claim"],
            "reason_code": "graph_and_name_closure_missing",
            "reason_class": "graph_and_name_closure_missing",
            "observed_report": (
                "GyCGT1 luteolin -> isoorientin one-step 6-C enzymatic statement present in the "
                "original, but no source-bound full atom/bond graph and no completed historical "
                "name/same-assay closure."
            ),
            "located_claim_kind": "direct_C6_source_statement_without_full_graph",
            "evidence_pointers": [
                {"path": rel(a6p), "sha256": a6_sha, "locator": "documented_direct_flavone_C6_step"},
                {
                    "path": rel(PRO / "C_PMC13564134_A4_independent_source_read.json"),
                    "sha256": in_sha[rel(PRO / "C_PMC13564134_A4_independent_source_read.json")],
                    "locator": "A4 independent read",
                },
                {
                    "path": rel(PRO / "C_PMC13564134_A5_independent_source_read.json"),
                    "sha256": in_sha[rel(PRO / "C_PMC13564134_A5_independent_source_read.json")],
                    "locator": "A5 independent read",
                },
            ],
            "source_original": {
                "source_id": NEW_C_SOURCE["source_id"],
                "verified_DOI": NEW_C_SOURCE["verified_DOI"],
                "A3_publication_identity": "official_PMC_identity_pass",
                "original_sha256": load(PROG)["original_sha256"],
            },
            "assessment_layers": [
                {
                    "role": "A3",
                    "layer": "official_PMC_identity",
                    "path": rel(PRO / "C_PMC13564134_A3_original_front_and_exposure.json"),
                    "sha256": in_sha[rel(PRO / "C_PMC13564134_A3_original_front_and_exposure.json")],
                },
                {
                    "role": "A4",
                    "layer": "independent_source_read",
                    "path": rel(PRO / "C_PMC13564134_A4_independent_source_read.json"),
                    "sha256": in_sha[rel(PRO / "C_PMC13564134_A4_independent_source_read.json")],
                    "output_SHA": a6["A4_output_SHA"],
                },
                {
                    "role": "A5",
                    "layer": "independent_source_read",
                    "path": rel(PRO / "C_PMC13564134_A5_independent_source_read.json"),
                    "sha256": in_sha[rel(PRO / "C_PMC13564134_A5_independent_source_read.json")],
                    "output_SHA": a6["A5_output_SHA"],
                },
                {
                    "role": "A6",
                    "layer": "closure_and_graph_gap_ruling",
                    "path": rel(a6p),
                    "sha256": a6_sha,
                    "A4_A5_qualitative_claim_agreement": a6["A4_A5_qualitative_claim_agreement"],
                    "A4_A5_full_molecule_graph_reconciliation": a6[
                        "A4_A5_full_molecule_graph_reconciliation"
                    ],
                    "exact_product_graph_match_or_mismatch": a6[
                        "exact_product_graph_match_or_mismatch"
                    ],
                },
            ],
            "structural_missing_fields": a6["reconciliation_unresolved_fields"],
            "blocking_gates": list(GATES_BY_CLASS["graph_and_name_closure_missing"]),
            "runtime_complete": False,
            "scope_applicable": False,
            "fresh_eligible": bool(a6["fresh_admitted"]),
            "article_level_exclusion_claimed": False,
            "human_reviewed": False,
            "raw_source_read_in_this_round": False,
            "new_chemistry_judgement": False,
            "notes": (
                "A correct source statement is NOT a complete reaction qualification; the source "
                "is neither admitted nor rejected."
            ),
        }
    )

    # ---- historical name-exposure boundary ruling request ----------------
    iso = audit_isoorientin()
    rows.append(
        {
            "row_id": "REL-C-NEW01-NAME-EXPOSURE",
            "row_kind": "name_exposure_boundary",
            "source_ref": sref,
            "family": "C",
            "frozen_scope": NEW_C_SOURCE["frozen_scope"],
            "status": "deferred",
            "status_source": "explicit_boundary_ruling_required",
            "upstream_disposition": None,
            "reason_code": "name_level_exposure_structural_level_unresolved",
            "reason_class": "name_level_exposure_structural_level_unresolved",
            "observed_report": (
                "Historical ledgers contain isoorientin only as a partial target NAME token on "
                "C-glucosylflavone biological-endpoint rows with all graph/site fields null; this "
                "is name-level, not chemical-structure-level, exposure. Whether it closes the "
                "prospective C6 reaction still requires an explicit A6 ruling."
            ),
            "evidence_pointers": [
                {"path": r["path"], "sha256": r["sha256"], "locator": "isoorientin rows"}
                for r in input_manifest["exposure_ledgers_read_only"]
            ],
            "source_original": {},
            "assessment_layers": [
                {
                    "role": "A6",
                    "layer": "upstream_name_exposure_enumeration",
                    "path": rel(a6p),
                    "sha256": a6_sha,
                    "declared_count": a6["prior_named_target_row_count"],
                    "enumerated_rows": len(a6["named_target_isoorientin_prior_exposure_rows"]),
                }
            ],
            "structural_missing_fields": [
                "acceptor_graph",
                "donor_graph",
                "product_graph",
                "site",
                "reaction_signature",
            ],
            "blocking_gates": list(GATES_BY_CLASS["name_level_exposure_structural_level_unresolved"]),
            "runtime_complete": False,
            "scope_applicable": False,
            "fresh_eligible": False,
            "article_level_exclusion_claimed": False,
            "human_reviewed": False,
            "raw_source_read_in_this_round": False,
            "new_chemistry_judgement": False,
            "audit": iso,
            "notes": (
                "Neither auto-exclude nor declare leakage-free: recorded as an open ruling with "
                "row-instance vs distinct-record counts separated."
            ),
        }
    )

    rows.append(
        {
            "row_id": "REL-C-NEW01-RESIDUAL",
            "row_kind": "article_residual_unassessed",
            "source_ref": sref,
            "family": "C",
            "frozen_scope": NEW_C_SOURCE["frozen_scope"],
            "status": "not_yet_assessed",
            "status_source": "explicit_gap_marker",
            "upstream_disposition": None,
            "reason_code": "article_reaction_universe_not_enumerated",
            "reason_class": "never_assessed",
            "observed_report": (
                "Reactions in PMC13564134 other than the located C6 claim were not enumerated."
            ),
            "evidence_pointers": [{"path": rel(a6p), "sha256": a6_sha, "locator": "G6_scope_claim"}],
            "source_original": {
                "source_id": NEW_C_SOURCE["source_id"],
                "verified_DOI": NEW_C_SOURCE["verified_DOI"],
            },
            "assessment_layers": [],
            "structural_missing_fields": a6["reconciliation_unresolved_fields"],
            "blocking_gates": list(GATES_BY_CLASS["never_assessed"]),
            "runtime_complete": False,
            "scope_applicable": False,
            "fresh_eligible": False,
            "article_level_exclusion_claimed": False,
            "human_reviewed": False,
            "raw_source_read_in_this_round": False,
            "new_chemistry_judgement": False,
            "notes": "Zero-as-omission marker.",
        }
    )

    coverage.append(
        {
            "source_ref": sref,
            "source_kind": "prospective_new_original",
            "family": "C",
            "owner_source_number": None,
            "source_id": NEW_C_SOURCE["source_id"],
            "verified_DOI": NEW_C_SOURCE["verified_DOI"],
            "source_A3_publication_identity": "official_PMC_identity_pass",
            "original_sha256": load(PROG)["original_sha256"],
            "frozen_scope": NEW_C_SOURCE["frozen_scope"],
            "historical_development_exposure": False,
            "post_read_permanent_exposure": True,
            "current_epoch_fresh_eligible": False,
            "located_reaction_rows": 1,
            "located_reaction_status_counts": {"deferred": 1},
            "admitted_rows": 0,
            "article_reaction_universe_exhausted": False,
            "residual_unassessed_row_id": "REL-C-NEW01-RESIDUAL",
            "runtime_completeness_verified": False,
            "scope_applicability_verified": False,
            "full_G6_passed": 0,
            "G7_eligible": bool(a6["G7_panel_allowed"]),
            "next_action": (
                "complete source-bound atom/bond graph, anomer stereo, reference precursor, and "
                "A6 name/assay closure; then static runtime applicability."
            ),
        }
    )

    # ---- residual metadata-only discovery universe (not in denominator) --
    prog = load(PROG)
    md = prog["G5_metadata_original_round"]
    ss = prog["SS_R2_metadata"]
    rows.append(
        {
            "row_id": "REL-RESIDUAL-METADATA-HINTS",
            "row_kind": "residual_metadata_universe",
            "source_ref": "RESIDUAL:metadata_only",
            "family": None,
            "frozen_scope": None,
            "status": "not_yet_assessed",
            "status_source": "explicit_gap_marker",
            "upstream_disposition": None,
            "reason_code": "metadata_only_never_chemically_assessed",
            "reason_class": "never_assessed",
            "observed_report": (
                "Discovery metadata for the G6 round (%d unique C-axis, %d unique SS-axis) was "
                "never taken into chemical qualification; metadata hits are not evidence."
            )
            % (md["unique"], ss["unique"]),
            "evidence_pointers": [
                {"path": rel(PROG), "sha256": in_sha[rel(PROG)], "locator": "G5_metadata_original_round"},
                {"path": rel(PROG), "sha256": in_sha[rel(PROG)], "locator": "SS_R2_metadata"},
            ],
            "source_original": {},
            "assessment_layers": [],
            "structural_missing_fields": list(GATES_BY_CLASS["never_assessed"]),
            "blocking_gates": list(GATES_BY_CLASS["never_assessed"]),
            "runtime_complete": False,
            "scope_applicable": False,
            "fresh_eligible": False,
            "article_level_exclusion_claimed": False,
            "human_reviewed": False,
            "raw_source_read_in_this_round": False,
            "new_chemistry_judgement": False,
            "counts": {
                "C_axis_unique_metadata": md["unique"],
                "SS_axis_unique_metadata": ss["unique"],
                "openalex_429": prog["G5_metadata_original_round"]["openalex_429"],
                "SS_axis_historically_exposed_PMCS": prog["SS_R2_Historical_O2_group_exposed_PMCS"],
            },
            "notes": "Outside the 17-source denominator; listed so nothing is silently dropped.",
        }
    )

    put(OUT / "reaction_eligibility_ledger_v1.jsonl", rows, jsonl=True)
    put(OUT / "source_coverage_ledger_v1.jsonl", coverage, jsonl=True)

    # ---- defects / discrepancies found while consolidating ---------------
    defects = [
        {
            "defect_id": "REL-D1",
            "severity": "pointer_integrity",
            "artifact": rel(a6p),
            "artifact_sha256": a6_sha,
            "finding": (
                "named_target_isoorientin_prior_exposure_rows records line numbers 2306-2482 and "
                "3323-3344, but the three referenced ledgers have 100/119/119 lines, so every "
                "recorded line pointer is out of range."
            ),
            "verification": "line counts re-derived from the files; pointers do not resolve",
            "impact": "name-exposure rows cannot be re-located from the artifact alone",
            "action_taken": "recorded, not silently fixed; ledger re-derives rows from raw ledgers",
            "prior_artifact_modified": False,
        },
        {
            "defect_id": "REL-D2",
            "severity": "enumeration_under_count",
            "artifact": rel(a6p),
            "artifact_sha256": a6_sha,
            "finding": (
                "upstream declares prior_named_target_row_count=36 but enumerates only 32 rows; the "
                "effective ledger contributes 12 isoorientin rows of which only 8 are enumerated."
            ),
            "verification": "enumerated rows counted per file and compared with raw ledger scan",
            "impact": "4 row instances were not enumerated in the prior artifact",
            "action_taken": "recorded; ledger carries the complete 12/12/12 re-derivation",
            "prior_artifact_modified": False,
        },
        {
            "defect_id": "REL-D3",
            "severity": "counting_semantics",
            "artifact": rel(a6p),
            "artifact_sha256": a6_sha,
            "finding": (
                "the headline count 36 equals row INSTANCES across three ledger versions (v1, v2, "
                "effective) of the SAME 12 distinct records; distinct exposure records = 12."
            ),
            "verification": "content-hash dedup of the isoorientin rows across the three ledgers: 12 distinct",
            "impact": (
                "quoting 36 as '36 records' overstates distinct historical exposure by 3x; it does "
                "not by itself establish structure-level leakage"
            ),
            "action_taken": "recorded; ledger separates instances from distinct records",
            "prior_artifact_modified": False,
        },
    ]
    put(OUT / "known_defects_and_discrepancies_v1.json", {
        "task": T, "layer": "reaction_eligibility_ledger_v1", "at": now(),
        "prior_artifacts_modified": False, "defects": defects,
    })

    # ---- summary ---------------------------------------------------------
    def tally(key):
        out: dict = {}
        for r in rows:
            v = r.get(key)
            v = "<none>" if v is None else v
            out[v] = out.get(v, 0) + 1
        return out

    summary = {
        "task": T,
        "layer": "reaction_eligibility_ledger_v1",
        "at": now(),
        "stage": "G6_IDENTITY_STRUCTURE_ADMIT",
        "stage_transition_performed": False,
        "authorization": "human_direct",
        "denominator": {
            "named_historical_sources": 16,
            "prospective_new_sources": 1,
            "total_sources": 17,
            "residual_metadata_universe_rows": 1,
        },
        "rows_total": len(rows),
        "rows_by_status": tally("status"),
        "rows_by_kind": tally("row_kind"),
        "rows_by_family": tally("family"),
        "admitted_total": sum(1 for r in rows if r["status"] == "admitted"),
        "fresh_C": 0,
        "fresh_SS": 0,
        "complete_reaction_admission": 0,
        "metrics": None,
        "scientific_ABE_cells": 0,
        "runtime_complete_rows": sum(1 for r in rows if r["runtime_complete"]),
        "scope_applicable_rows": sum(1 for r in rows if r["scope_applicable"]),
        "article_level_exclusion_rows": sum(
            1 for r in rows if r["article_level_exclusion_claimed"]
        ),
        "source_coverage_rows": len(coverage),
        "sources_with_residual_marker": sum(
            1 for c in coverage if c.get("residual_unassessed_row_id")
        ),
        "article_reaction_universe_exhausted_any": any(
            c["article_reaction_universe_exhausted"] for c in coverage
        ),
        "can_freeze_G7_panel": False,
        "G6_global_complete": False,
        "scope_modified": False,
        "MCTS_untouched": True,
        "no_new_source_read": True,
        "no_new_http": True,
        "raw_source_read_in_this_round": False,
        "physical_HTTP_total_unchanged": load(PROG)["HTTP_total"],
        "physical_source_bytes_total_unchanged": load(PROG)["physical_source_bytes_total"],
        "human_reviewed": False,
        "independent_chemistry": False,
        "git_commit_push": False,
        "isoorientin_name_exposure_audit": iso,
        "defect_ids": [d["defect_id"] for d in defects],
        "input_manifest_sha256": sha256_file(ROOT / OUT / "INPUT_MANIFEST.json"),
        "ledger_sha256": sha256_file(ROOT / OUT / "reaction_eligibility_ledger_v1.jsonl"),
        "coverage_sha256": sha256_file(ROOT / OUT / "source_coverage_ledger_v1.jsonl"),
        "status": "In Progress",
        "no_promotion_note": (
            "fresh C/SS remain 0, metrics remain null, G6 remains incomplete, G7-G10 not started."
        ),
    }
    put(OUT / "ledger_summary_v1.json", summary)
    event(T, "reaction_ledger_v1_built", rows=len(rows), sources=len(coverage),
          inputs=len(input_manifest["inputs"]), defects=len(defects))
    print(json.dumps({k: summary[k] for k in (
        "rows_total", "rows_by_status", "admitted_total", "fresh_C", "fresh_SS",
        "sources_with_residual_marker", "can_freeze_G7_panel")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    build()
