"""Session source-loop stop review for TASK-016-P7 (both families).

Documents the 2026-10-12 session's independent discovery rounds, their evidence,
and the contract-6.3 saturation / access-boundary assessment. No scope change,
no epoch closure, no gate change, no chemistry admission, no new MCTS.
"""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

from scripts.operate import ROOT, write

TASK = "TASK-016-P7"
B = Path("outputs/task016-p7/v1")
OUT = B / "governance/R74-R75-source-loop-stop-review-v1"


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def pointer(p):
    return {"path": str(p), "sha256": sha(p)}


def main():
    if (ROOT / OUT).exists():
        raise RuntimeError("OUTPUT_ALREADY_EXISTS")
    created = datetime.now(timezone.utc).isoformat()

    # 1) Archive this session's two researcher discovery reports (web metadata only).
    src_c = Path(".zwork/runs/9cfff1fb/0-研究员.md")
    src_ss = Path(".zwork/runs/9cfff1fb/1-研究员.md")
    ev = B / "discovery_evidence/session_20261012"
    for src, name in ((src_c, "C_axis_researcher_report.md"), (src_ss, "SS_axis_researcher_report.md")):
        text = (ROOT / src).read_text(encoding="utf-8")
        write(TASK, str(ev / name), text)
        write(TASK, str(ev / (name + ".provenance.json")), json.dumps(
            dict(task=TASK, copied_at=created, source_path=str(src),
                 source_sha256=sha(src), archived_sha256=sha(ev / name),
                 role="A1/A2 discovery researcher (web metadata only; no chemistry, no local file writes)",
                 approval_type="agent_delegated", human_reviewed=False), ensure_ascii=False, sort_keys=True, indent=2) + "\n")

    # 2) Local exposure cross-check facts for this session's candidates.
    pea1982_doi = "10.1016/0003-9861(82)90569-0"
    r11 = [json.loads(l) for l in (ROOT / "outputs/task016-p7/v1/C/E02/fresh/C-E02-R11/all_metadata_observations_v2.jsonl").read_text().splitlines() if pea1982_doi in l]
    r11 = [r for r in r11 if r.get("doi") == pea1982_doi]
    if len(r11) != 1:
        raise RuntimeError("R11_PEA1982_HINT_NOT_UNIQUE")
    r11 = r11[0]
    if r11.get("source_hint_only") is not True or r11.get("historical_source_token_overlap") != []:
        raise RuntimeError("R11_HINT_STATUS_UNEXPECTED")

    # 3) R74 batch results (preregistered metadata round).
    r74dir = B / "SS/E02/fresh/SS-E02-R74-final-lead-metadata-v1"
    r74 = json.loads((ROOT / r74dir / "final_lead_dispositions.json").read_text())
    legal = [d["lead_id"] for d in r74["dispositions"] if d["legal_oa_copy_located"]]
    blocked = [d["lead_id"] for d in r74["dispositions"] if not d["legal_oa_copy_located"]]
    l06 = next(d for d in r74["dispositions"] if d["lead_id"] == "SS-R74-L06")
    l06_title = ((l06.get("openalex_oa") or {}).get("title")) or ""

    doc = dict(
        task=TASK, at=created, approval_type="agent_delegated", human_reviewed=False,
        scope_unchanged=True, epoch_closure_performed=False,
        new_MCTS=0, fresh_admitted=0, chemistry_examination_performed=False,
        C=dict(
            session_routes=[
                "researcher systematic web discovery (~40 leads verified: EPMC phrase/year-window queries, enzyme-name batch queries, DOI-resolution, full-text reads of LaCGT1/halophytic-CGTs/ScCGT1/PNAS2020; see archived report)",
                "root checks: Pueraria PlUGT43 exposure verification, Brassica napus enzyme search, Koester&Barz identity check, exact-phrase '6-C-glucosyltransferase' search",
            ],
            session_new_candidates=0,
            known_direct_type_CGT_literature="ScCGT1 (Microb Cell Fact 2022, PMC9563126) review statement: direct Type II CGTs on flavone/isoflavone aglycones reported only from Gentiana triflora, Eutrema japonicum, Trollius chinensis, Pueraria lobata",
            genus_status={
                "Gentiana triflora": "development-exposed (GtUF6CGT1, 10.1016/j.febslet.2014.11.045)",
                "Eutrema japonicum (wasabi)": "development-exposed historical C target (donor-deficient; WASABI ledger rows)",
                "Trollius chinensis": "consumed (TcCGT1 2-hydroxyflavanone route; Chong 2023 excluded)",
                "Pueraria lobata": "development-exposed (PlUGT43 examined in C-E02 design qualification: design_source_qualification/v1 + C-E02-R1 A4 extraction; isoflavone C-glycosylation, outside flavone-C6-C3H scope)",
            },
            pre2010_blind_spot="old unindexed literature (radiolabel era) lacks complete structure/stereo evidence and is largely paywalled; documented as known limitation, not evidence of absence",
            saturation_assessment="contract 6.3 condition 3 satisfied within executed legal routes: >=3 discovery route types executed historically and this session; consecutive complete rounds with zero new structure_complete+runtime_executable+leakage_free+scope_applicable closure groups (this session round: 0 candidates at metadata level; prior complete processing rounds each 0 admitted)",
        ),
        SS=dict(
            session_routes=[
                "researcher systematic web discovery (16 EPMC/Crossref/NCBI query routes, hitCounts recorded, exclusion list verified; see archived report)",
                "R74 preregistered metadata round (7 HTTP: Crossref identity + OpenAlex OA resolution for 6 final leads)",
            ],
            session_new_candidates=1,
            pea1982=dict(
                doi=pea1982_doi, pmid="6462109",
                r11_metadata_hint=r11.get("observation_id"),
                r11_status=dict(source_hint_only=r11.get("source_hint_only"),
                                identity_not_verified=r11.get("identity_not_verified"),
                                historical_source_token_overlap=r11.get("historical_source_token_overlap"),
                                inEPMC=r11.get("inEPMC"), inPMC=r11.get("inPMC"), isOpenAccess=r11.get("isOpenAccess")),
                r74_disposition=next(d["disposition"] for d in r74["dispositions"] if d["lead_id"] == "SS-R74-L01"),
                access_boundary="no legal OA copy located by OpenAlex (is_oa=false, any_repository_has_fulltext=false); continuing requires paywall/access-control bypass, which contract 6.3 condition 4 and 18.2 forbid",
                same_cohort_closure_risk="same Mansell pea enzyme system as development-exposed 1979 paper (manual intake #14, G6 bounded review DEFERRED_NOT_ESTABLISHED_IN_ORIGINAL_1979_PDF); A6 adjudication mandatory before any fresh use",
                even_if_admitted_ceiling="single closure group; Q-based steps at most a few targets; below the non-lowerable >=6 targets / >=2 independent groups floor",
            ),
            l06_note=dict(lead_id="SS-R74-L06", title=l06_title,
                          enzyme_class="hydroxycinnamoyl:CoA transferase (acylation step), not a UDP-glucose glycosyltransferase; outside SS-E02 donor/acceptor scope by title-level enzyme class",
                          legal_oa_copy_located=True, acquisition_planned=False,
                          reason="out-of-scope enzyme class; acquisition would not advance the frozen SS-E02 panel"),
            saturation_assessment="contract 6.3 conditions 3 and 4 both engaged within executed legal routes: >=3 route types; consecutive complete rounds zero-new qualified groups; the only mechanically fresh candidate is access-blocked at metadata level",
        ),
        conclusion=dict(
            panel_freeze_possible=False,
            gates_lowered=False, panel_floor_unchanged="C>=6/2, SS>=6/2; A/B/E floor unchanged",
            epochs_kept_open=True,
            epochs_kept_open_reason="C-E02/SS-E02 frozen scopes remain valid; future authorized resumption possible if legally obtained originals (e.g., owner-provided pea 1982) or new qualified sources emerge; closed epochs would forbid fresh acquisition by gate design",
            task_outcome_per_contract="contract 6.3: stopping under conditions 2-4 with insufficient panels requires Partial/Blocked, not gate reduction; scientific A/B/E remains 0 cells, metrics null",
            open_governance_items=[
                "G7 writer hard-binding of all late exposure supplements remains a precondition for any future panel freeze",
                "R73 five-source G5 contracts remain active-but-stopped (4 final scientific role slots pending); their sources stay permanently exposed",
            ],
        ),
        evidence=dict(
            C_researcher_report=pointer(ev / "C_axis_researcher_report.md"),
            SS_researcher_report=pointer(ev / "SS_axis_researcher_report.md"),
            R74_batch=pointer(r74dir / "final_lead_dispositions.json"),
            R74_summary=pointer(r74dir / "raw_custody_summary.json"),
            R11_pea1982_hint_path="outputs/task016-p7/v1/C/E02/fresh/C-E02-R11/all_metadata_observations_v2.jsonl",
            PlUGT43_exposure_paths=[
                "outputs/task016-p7/v1/C/E02/design_source_qualification/v1/science_source_review_v1/GA.main_paragraphs.zero_based.jsonl",
                "outputs/task016-p7/v1/C/E02/fresh/C-E02-R1/A4_fixed_extraction_v1/source_dispositions.jsonl",
            ],
            manual16_G6_review="outputs/task016-p7/v1/G6_owner_16_historical_source_review_v2/",
        ),
    )
    write(TASK, str(OUT / "source_loop_stop_review.json"),
          json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(written=str(OUT / "source_loop_stop_review.json"),
                          sha256=sha(OUT / "source_loop_stop_review.json"),
                          legal=legal, blocked=blocked), ensure_ascii=False))


if __name__ == "__main__":
    main()
