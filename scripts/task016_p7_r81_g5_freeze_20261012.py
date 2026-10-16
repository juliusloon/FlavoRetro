"""R81: Trapero 2012 (PMC3425182, UGT707B1) SS G5 preregistration freeze.
Content read REMAINS BLOCKED until after this freeze. The source carries
identifier-level design exposure (2 historical_design rows in the v4 prior
exposure inventory), so the fresh-qualification lane stays closed by policy
and the content read runs as a late-prior-design structural-evidence read.
"""
import json
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now
from scripts.task016_p7_orchestrate import role_manifest, freeze_stage_manifest, verify_stage_chain
from scripts import task016_p7_full_qualification_harness_v4 as fq

T = 'TASK-016-P7'; B = Path('outputs/task016-p7/v1')
A11 = B / 'governance/R81-owner-originals-A11-A6-v1/A11_independent_review.json'
A6R = B / 'governance/R81-owner-originals-A11-A6-v1/A6_exposure_projection_review.json'
POLICY = B / 'governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json'
UNKNOWN = B / 'governance/unknown_prior_science_intake_v1/agent_delegated_prospective_decision.json'
REQ = B / 'governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json'
ADAPT = B / 'governance/late_exposure_temporal_adapter_v1'
INTAKE = B / 'SS/E02/fresh/SS-E02-R78-trapero2012-raw-custody-v1/query_execution.jsonl'
PRECONTRACT = B / 'SS/E02/fresh/SS-E02-R78-trapero2012-raw-custody-v1/precontract.json'
RAW_PEA = Path('data/raw/task016-p7/SS/E02/SS-E02-R78-trapero2012-raw-custody-v1/R78-368f3ba8993540008fe51d793455e803.bin')
RAW_MOR = RAW_PEA

def base(f): return B / f'{f}/E02/fresh/{f}-E02-R81-owner-originals-full-qualification-v1'
def stage(f): return B / f'{f}/E02/stages/batches/{f}-E02-R81-owner-originals-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json'

SOURCES = [
 dict(source_id='SS-E02-R81-S01', pdf='PMC3425182.canonical-html',
      official_aliases=['doi:10.1104/pp.112.198069', 'pmid:22649274', 'article:PMC3425182'],
      raw_status='available', raw_files=[dict(path='data/raw/task016-p7/SS/E02/SS-E02-R78-trapero2012-raw-custody-v1/R78-368f3ba8993540008fe51d793455e803.bin', sha256='d41422e74fc01299bd7b8581fbc9cd7786e629b1f2cac46f8710a35222812e90')],
      title='Characterization of a glucosyltransferase enzyme involved in the formation of kaempferol and quercetin sophorosides in Crocus sativus',
      journal='Plant Physiol 159(4):1335-1354 (2012); UGT707B1, GenBank HE793682',
      prior_read_status='unknown',
      prior_note='R78 sealed custody (canonical PMC HTML, no content read); IDENTIFIER-LEVEL DESIGN EXPOSURE CONFIRMED: 2 rows in prior_exposure_inventory_v4 (E02_design custodian v3 permanent_scientific_design_source_exposure + new_source_discovery_v1 metadata_or_access_deferred_only) intersect doi:10.1104/pp.112.198069/pmid:22649274/article:PMC3425182, so the fresh-qualification lane is closed by policy (prior_design_or_historical_exposure_still_excludes); scientific content never read by the project; R29 caption-level mention documented as metadata hint; preregistered lead metadata explicitly claims sophoroside formation mechanism; this preregistration covers the structural-evidence design read only'),
]

_orig_put = put
def put(path, obj):
    if (ROOT / path).exists():
        cur = json.loads((ROOT / path).read_text())
        if cur == obj: return {'path': str(path), 'sha256': sha(ROOT / path)}
        sup = ROOT / path
        sup_dir = sup.parent / 'superseded'
        sup_dir.mkdir(parents=True, exist_ok=True)
        dest = sup_dir / (sup.name + '.pre-r81-counts-fix')
        if not dest.exists():
            import shutil as _sh; _sh.copyfile(sup, dest); dest.chmod(0o444)
            event(T, 'superseded_draft_archived', path=str(dest), reason='stale R80-inherited draft counts/notes (R81 G5 build); original preserved')
        sup.unlink()
        return _orig_put(path, obj)
    return _orig_put(path, obj)

def main():
    for s in SOURCES:
        assert sha(Path(s['raw_files'][0]['path'])) == s['raw_files'][0]['sha256'], 'SHA_DRIFT'
    # A11/A6 review evidence: the independent reviewer's report (verbatim copy) + verdict files
    rep_src = ROOT / '.zwork/runs/7466e54b/0-审阅者.md'
    if not (ROOT / '.zwork/runs/7466e54b').exists():
        rep_src = Path('.zwork/runs/7466e54b/0-审阅者.md')
    ev_dir = B / 'discovery_evidence/session3_20261012'
    if not (ROOT / ev_dir / 'independent_reviewer_report.md').exists():
        text = (ROOT / rep_src).read_text(encoding='utf-8')
        write(T, str(ev_dir / 'independent_reviewer_report.md'), text)
        write(T, str(ev_dir / 'independent_reviewer_report.md.provenance.json'), json.dumps(dict(
            task=T, at=now(), source_path=str(rep_src), source_sha256=sha(rep_src),
            role='A11+A6 independent reviewer (saved agent 审阅者, read-only)', approval_type='agent_delegated',
            human_reviewed=False), ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    if not (ROOT / A11).exists():
        put(A11, dict(task=T, at=now(), agent_role='A11', reviewer='saved-agent 审阅者 (independent, read-only)',
        report_pointer=pointer_of(ev_dir / 'independent_reviewer_report.md'),
        subject='owner-originals intake (manual_grabbed_1, 11 PDFs) and the two SS fresh candidates',
        safe_to_proceed_to_conditional_scientific_processing=True, errors=[],
        key_findings=['SHA recomputation matches manifest for all 11 files',
                      'first-page identity only; no scientific content read; no HTTP bypass',
                      'task-description correction: 112.198069 is Trapero 2012 DOI fragment, not pea 1982']))
    if not (ROOT / A6R).exists():
        put(A6R, dict(task=T, at=now(), agent_role='A6', reviewer='saved-agent 审阅者 (independent, read-only)',
        report_pointer=pointer_of(ev_dir / 'independent_reviewer_report.md'),
        identifier_overlap=dict(pea1982=0, morita2005=0),
        pea1982_same_cohort_adjudication=dict(verdict='not_blocked', conditions=[
            'kaempferol-pathway reactions matching exposed signatures are blocked by reaction signature regardless',
            'the 1982 paper content was never read by the project; only the 1979 companion was (G6 DEFERRED ruling)',
            'A4/A5 extraction must record which reactions are documented; reaction-level leakage check at A6']),
        morita2005=dict(identity='R10-metadata-corroborated', panel_flavonol_content='unknown',
                        both_branches_preregistered=True),
        safe_to_proceed_to_conditional_scientific_processing=True, errors=[]))
    contracts = {}
    for family in ('SS',):
        r = base(family); g4 = B / f'{family}/E02/stages/G4_SCOPE_FREEZE.json'
        sources = []; results = []
        for s in SOURCES:
            aliases = list(s['official_aliases'])
            precheck = [fq.pointer(A11), fq.pointer(A6R), fq.pointer(INTAKE), fq.pointer(PRECONTRACT)]
            sources.append(dict(source_id=s['source_id'], official_aliases=aliases, raw_status='available',
                raw_files=s['raw_files'], prior_scientific_read=None,
                prior_read_status=s['prior_read_status'],
                prior_uncertainty_blocks_qualification=True,
                prior_read_precheck_evidence=precheck,
                prior_scientific_read_recorded=False,
                prior_recorded_scope=s['prior_note'],
                planned_original_routes=['owner_supplied_pdf_immutable_intake_20261012'],
                source_metadata_title=s['title'] + ' | ' + s['journal'],
                full_alias_or_graph_historical_clearance=False,
                SIs_not_yet_in_this_raw_universe=True,
                SI_required_for_any_reaction_must_be_acquired_in_separate_preregistered_raw_route=True))
            official_record = 'R78 sealed custody: preregistered lead metadata (precontract.json: pmcid/pmid/doi/title/enzyme) acquired at the canonical PMC article URL (query R78-CANON-01, SHA-bound); in-document title re-confirmation deferred to the A4/A5 read itself'
            results.append(dict(source_id=s['source_id'], identity_status='verified',
                identity_basis='documentary identity from preregistered custody: ' + official_record,
                official_aliases=aliases, unresolved_conflicts=[],
                evidence=[fq.pointer(A11), fq.pointer(A6R), fq.pointer(INTAKE), fq.pointer(PRECONTRACT)] + [dict(path=p0['path'], sha256=p0['sha256']) for p0 in s['raw_files']],
                publisher_literals_preserved=True, publisher_relation_not_legal_entity_equality=True))
        _ru = r / 'raw_source_universe.json'
        put(_ru, dict(task=T, scientific_content_read=False, final_structures_provided=False,
            source_candidates=sources, metadata_only_dispositions=[], source_count=1,
            shared_source_count_across_C_SS=0, independence_group_count_not_doubled=True,
            prior_read_uncertainty_retained=True,
            identifier_level_design_exposure=dict(intersecting_rows=2,
                rows=['governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl#L2548', 'governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl#L3209'],
                consequence='fresh lane closed by policy (prior_design_or_historical_exposure_still_excludes); content read proceeds as late prior design structural-evidence read'),
            unknown_prior_note='harness semantics: prior scientific content kept unknown+blocking; identifier-level design exposure documented; independent A11/A6 R81 reviews bound as precheck evidence; resolution at A6 admission'))
        _a3p = r / 'A3_source_results.json'
        put(_a3p, dict(task=T, sources=results))
        role = role_manifest('A3', family + '-E02',
            [r / 'raw_source_universe.json', INTAKE, PRECONTRACT, A11, A6R, RAW_PEA],
            [r / 'A3_source_results.json'], dict(processed=1, passed=1, rejected=0, pending=0),
            pointers=[fq.pointer(A11), fq.pointer(A6R)], read_holdout=False, read_model_outcome=False)
        role['scope'] = 'Documentary identity projection from R78 sealed custody (preregistered lead metadata + canonical PMC URL binding); no new scientific eligibility; fresh lane closed by identifier-level design exposure.'
        _rp = r / 'role_A3_manifest.json'
        put(_rp, role)
        ledger = B / 'epoch_ledger.jsonl'; data = (ROOT / ledger).read_bytes()
        epoch = B / 'epochs' / (family + '-E02') / ('epoch_state.v6.json')
        adapter = load(ADAPT / 'temporal_adapter_manifest.json')
        spec = dict(family=family, epoch_id=family + '-E02', batch_id=family + '-E02-R81-owner-originals-full-qualification',
            G4=fq.pointer(g4), epoch_state=fq.pointer(epoch),
            epoch_ledger_prefix=dict(path=str(ledger), prefix_bytes=len(data), prefix_sha256=sha(ledger)),
            scope_manifest=fq.pointer(B / f'{family}/E02/scope_manifest.json'),
            scope_bank=fq.pointer(B / f'{family}/E02/scope_bank.json'),
            raw_source_universe=fq.pointer(r / 'raw_source_universe.json'),
            A3_source_results=fq.pointer(r / 'A3_source_results.json'),
            A3_role=fq.pointer(r / 'role_A3_manifest.json'),
            prior_exposure_snapshot=fq.pointer(B / f'governance/prior_exposure_inventory_v4/prior_exposure_snapshot_{family}.json'),
            late_prior_design_files=[adapter['prior_exposure']],
            prior_current_evaluation_ledger=adapter['current_evaluation'],
            current_exposure_temporal_adapter=fq.pointer(ADAPT / 'temporal_adapter_manifest.json'),
            future_G7_requirement=fq.pointer(REQ), policy=fq.pointer(POLICY),
            unknown_prior_intake_policy=fq.pointer(UNKNOWN),
            independent_intake_review=fq.pointer(A11),
            independent_exposure_projection_review=fq.pointer(A6R),
            evaluation_events_directory=str(r / 'evaluation_read_events'))
        cp_path = r / 'full_qualification_contract.json'
        if not (ROOT / cp_path).exists():
            fq.freeze_full_qualification_contract(cp_path, spec)
        cp = fq.pointer(cp_path)
        v = fq.validate_full_qualification_contract(cp)
        assert v['source_candidates'] == 1 and v['admitted'] == 0
        contracts[family] = cp
        put(r / 'pre_G5_contract_validation.json', dict(task=T, at=now(), family=family, source_candidates=1,
            A3_identity_passed=1, prior_unknown=1, science_admitted=0, HTTP=0, MCTS=0,
            trapero2012_identifier_level_design_exposure_rows=2,
            fresh_lane_status='closed_by_prior_design_exposure (policy: prior_design_or_historical_exposure_still_excludes)',
            content_read_lane='late_prior_design structural-evidence read, only after this G5 preregistration'))
    r = base('SS'); g4 = B / 'SS/E02/stages/G4_SCOPE_FREEZE.json'; g5 = stage('SS')
    paths = [r / x for x in ('full_qualification_contract.json', 'raw_source_universe.json', 'A3_source_results.json',
              'role_A3_manifest.json', 'pre_G5_contract_validation.json')] + [RAW_PEA] + \
            [Path(__file__).relative_to(ROOT), A11, A6R, INTAKE, ADAPT / 'prior_exposure_rows.jsonl', ADAPT / 'current_exposure_rows.jsonl', ADAPT / 'temporal_adapter_manifest.json', UNKNOWN]
    if not (ROOT / g5).exists():
        freeze_stage_manifest(ROOT / g5.parent, 'G5_FRESH_HOLDOUT_ACQUIRE', paths, g4,
            expected_previous_sha=sha(g4), family='SS', epoch_id='SS-E02')
    verify_stage_chain(g5, sha(g5))
    ledger = B / 'epoch_ledger.jsonl'
    row = dict(task=T, epoch_id='SS-E02', family='SS', stage='G5_FRESH_HOLDOUT_ACQUIRE', status='active',
        event_type='R81_owner_originals_preregistered_before_content_read', at=now(),
        stage_manifest_path=str(g5), stage_manifest_sha256=sha(g5), qualification_contract=contracts['SS'],
        source_count=1, prior_read_unknown=1, source_science_read=False, fresh_admitted=0,
        fresh_lane_closed_by_prior_design_exposure=True,
        approval_type='agent_delegated', human_reviewed=False)
    write(T, str(ledger), (ROOT / ledger).read_text() + json.dumps(row, sort_keys=True) + '\n')
    event(T, 'R81_G5_frozen', sources=1, content_read=False)
    print(json.dumps(dict(G5=sha(g5), science_reads=0, fresh_admitted=0)))

def sha_file_rel(rel):
    import hashlib
    h = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    return h

def pointer_of(rel):
    return dict(path=str(rel), sha256=sha(rel))

if __name__ == '__main__':
    main()
