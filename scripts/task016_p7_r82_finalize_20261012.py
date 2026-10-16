"""R82 finalize: persist the independent verification of the A6 determination."""
import json, re
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now

T = 'TASK-016-P7'; B = Path('outputs/task016-p7/v1')
R = B / 'SS/E02/fresh/SS-E02-R82-trapero-structural-evidence-read-v1'

def main():
    rep_src = ROOT / '.zwork/runs/54e3a8d4/0-审阅者.md'
    if not rep_src.exists():
        rep_src = Path('.zwork/runs/54e3a8d4/0-审阅者.md')
    text = (ROOT / rep_src).read_text(encoding='utf-8')
    det = load(R / 'A6_structural_evidence_determination.json')
    put(R / 'independent_verification_report.md', text)
    put(R / 'independent_verification_report.md.provenance.json', dict(
        task=T, at=now(), source_path=str(rep_src), source_sha256=sha(rep_src),
        role='independent verification of the R82 A6 structural-evidence determination (saved agent 审阅者, read-only)',
        determination=dict(path=str(R / 'A6_structural_evidence_determination.json'), sha256=sha(R / 'A6_structural_evidence_determination.json')),
        approval_type='agent_delegated', human_reviewed=False))
    m = re.search(r'\{[^{}]*"determination_acceptable"[^{}]*\}', text, re.S)
    verdict = json.loads(m.group(0)) if m else None
    assert verdict and verdict['determination_acceptable'] is True and verdict['quotes_verbatim_ok'] == verdict['quotes_checked'] == 12, verdict
    put(R / 'A6_determination_verification.json', dict(
        task=T, at=now(), batch='SS-E02-R82-trapero-structural-evidence-read',
        determination=dict(path=str(R / 'A6_structural_evidence_determination.json'), sha256=sha(R / 'A6_structural_evidence_determination.json')),
        determination_status_after_verification='verified_independent_agent_review',
        verifier='saved-agent 审阅者 (independent, read-only)',
        verification_report=dict(path=str(R / 'independent_verification_report.md'), sha256=sha(R / 'independent_verification_report.md')),
        verdict=verdict,
        scope_note='verifies quote fidelity and internal consistency only; not a human chemical review; no fresh eligibility granted',
        approval_type='agent_delegated', human_reviewed=False, errors=[]))
    ledger = B / 'epoch_ledger.jsonl'
    row = dict(task=T, epoch_id='SS-E02', family='SS', stage='G6_IDENTITY_STRUCTURE_ADMIT', status='active',
        event_type='R82_design_lane_structural_evidence_read_verified', at=now(),
        batch='SS-E02-R82-trapero-structural-evidence-read', source_id='SS-E02-R81-S01',
        G5_preregistration='outputs/task016-p7/v1/SS/E02/stages/batches/SS-E02-R81-owner-originals-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json',
        fresh_lane='closed_by_prior_design_exposure (execution-proven probe closed_by_harness)',
        linkage_structural_evidence='PRESENT_DIRECT_2D_NMR_HMBC', methylation_analysis='ABSENT',
        authentic_standard_cochromatography='ABSENT', in_vitro_enzyme_activity='NOT_DEMONSTRATED',
        fresh_admitted=0, design_corpus_only=True,
        approval_type='agent_delegated', human_reviewed=False)
    write(T, str(ledger), (ROOT / ledger).read_text() + json.dumps(row, sort_keys=True) + '\n')
    event(T, 'R82_finalized_verified', determination_acceptable=True)
    print(json.dumps(dict(verified=True, quotes=verdict['quotes_verbatim_ok'])))

if __name__ == '__main__':
    main()
