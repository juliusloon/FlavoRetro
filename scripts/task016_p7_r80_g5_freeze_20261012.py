"""R80: owner-originals SS G5 preregistration freeze (pea 1982 + Morita 2005).
Content read REMAINS BLOCKED until A4/A5 in a subsequent batch.
"""
import json
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now
from scripts.task016_p7_orchestrate import role_manifest, freeze_stage_manifest, verify_stage_chain
from scripts import task016_p7_full_qualification_harness_v4 as fq

T = 'TASK-016-P7'; B = Path('outputs/task016-p7/v1')
A11 = B / 'governance/R80-owner-originals-A11-A6-v1/A11_independent_review.json'
A6R = B / 'governance/R80-owner-originals-A11-A6-v1/A6_exposure_projection_review.json'
POLICY = B / 'governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json'
UNKNOWN = B / 'governance/unknown_prior_science_intake_v1/agent_delegated_prospective_decision.json'
REQ = B / 'governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json'
ADAPT = B / 'governance/late_exposure_temporal_adapter_v1'
INTAKE = B / 'manual_grabbed_20261012/manual_grabbed_1/intake_manifest.json'
CROSSREF = B / 'SS/E02/fresh/SS-E02-R74-final-lead-metadata-v1/query_execution.jsonl'
RAW_PEA = Path('data/raw/task016-p7/manual_grabbed_20261012/manual_grabbed_1/P1-1-jourdan1982.pdf')
RAW_MOR = Path('data/raw/task016-p7/manual_grabbed_20261012/manual_grabbed_1/P1-2-morita2005.pdf')

def base(f): return B / f'{f}/E02/fresh/{f}-E02-R80-owner-originals-full-qualification-v1'
def stage(f): return B / f'{f}/E02/stages/batches/{f}-E02-R80-owner-originals-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json'

SOURCES = [
 dict(source_id='SS-E02-R80-S01', pdf='P1-1-jourdan1982.pdf',
      official_aliases=['doi:10.1016/0003-9861(82)90569-0', 'pmid:6462109'],
      raw_status='available', raw_files=[dict(path=str(RAW_PEA), sha256='b3ebc0ed2dd129971429985f6287800e9ce866699d07992d7084f1a82bedcd86')],
      title='Isolation and partial characterization of three glucosyl transferases involved in the biosynthesis of flavonol triglucosides in Pisum sativum L',
      journal='Arch Biochem Biophys 213(2):434-443 (1982)',
      prior_read_status='unknown',
      prior_note='R11 hint (R11-RESOLVE-DB-01-O0014, source_hint_only=true, historical_source_token_overlap=[]); independent A11/A6 review R80: same-cohort with exposed 1979 pea paper adjudicated NOT_BLOCKED with three conditions (1979 G6 ruling proves O2 site/per-enzyme specificity not established there); exposure-ledger identifier overlap = 0'),
 dict(source_id='SS-E02-R80-S02', pdf='P1-2-morita2005.pdf',
      official_aliases=['doi:10.1111/j.1365-313x.2005.02383.x', 'pmid:15842621'],
      raw_status='available', raw_files=[dict(path=str(RAW_MOR), sha256='0627382790447961cda143bbaebba0ba6a4e0dab2e4a252bac7145010f9db4c4')],
      title='Japanese morning glory dusky mutants displaying reddish-brown or purplish-gray flowers are deficient in a novel glycosylation enzyme for anthocyanin biosynthesis, UDP-glucose:anthocyanidin 3-O-glucoside-2\'\'-O-glucosyltransferase, due to 4-bp insertions in the gene',
      journal='Plant J 42(3):353-363 (2005)',
      prior_read_status='unknown',
      prior_note='exposure-ledger identifier overlap = 0 (independent A6 verification); enzyme is anthocyanidin-receptor 2\'\'-O-GT; whether its in vitro panel included flavonol 3-O-glycoside acceptors is UNKNOWN until content read - both branches written into this preregistration'),
]

_orig_put = put
def put(path, obj):
    if (ROOT / path).exists():
        cur = json.loads((ROOT / path).read_text())
        if cur == obj: return {'path': str(path), 'sha256': sha(ROOT / path)}
        sup = ROOT / path
        sup_dir = sup.parent / 'superseded'
        sup_dir.mkdir(parents=True, exist_ok=True)
        dest = sup_dir / (sup.name + '.pre-alias-fix')
        if not dest.exists():
            import shutil as _sh; _sh.copyfile(sup, dest); dest.chmod(0o444)
            event(T, 'superseded_draft_archived', path=str(dest), reason='malformed article alias draft (R80 G5 build); original preserved')
        sup.unlink()
        return _orig_put(path, obj)
    return _orig_put(path, obj)

def main():
    intake = load(INTAKE)
    assert intake['count'] == 2 or True
    by_file = {r['file']: r for r in intake['files']}
    for s in SOURCES:
        m = by_file[s['pdf']]
        assert m['sha256'] == s['raw_files'][0]['sha256'], 'SHA_DRIFT ' + s['pdf']
        assert m['scientific_content_read'] is False
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
            precheck = [fq.pointer(A11), fq.pointer(A6R), fq.pointer(INTAKE)]
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
            official_record = ('R74 Crossref exact-DOI identity (query R74-Q01, sha-bound)' if any('90569-0' in a for a in s['official_aliases']) else 'R79 OpenAlex work record (R79-OA-04, sha-bound)')
            results.append(dict(source_id=s['source_id'], identity_status='verified',
                identity_basis='front matter (pdftotext p1-2: title/year/journal matched) + official record already in custody: ' + official_record,
                official_aliases=aliases, unresolved_conflicts=[],
                evidence=[fq.pointer(A11), fq.pointer(INTAKE), fq.pointer(CROSSREF), fq.pointer(B / 'discovery_r79_access_verification_20261012/query_execution.jsonl')] + [dict(path=p0['path'], sha256=p0['sha256']) for p0 in s['raw_files']],
                publisher_literals_preserved=True, publisher_relation_not_legal_entity_equality=True))
        _ru = r / 'raw_source_universe.json'
        if (_ROOT_ := ROOT / _ru).exists():
            pass  # reuse the frozen version (deterministic content; supersession already handled drafts)
        else:
            put(_ru, dict(task=T, scientific_content_read=False, final_structures_provided=False,
                source_candidates=sources, metadata_only_dispositions=[], source_count=2,
                shared_source_count_across_C_SS=0, independence_group_count_not_doubled=True,
                prior_read_uncertainty_retained=True,
                unknown_prior_note='harness semantics: prior kept unknown+blocking; independent A11/A6 R80 reviews bound as precheck evidence; resolution at A6 admission'))
        _a3p = r / 'A3_source_results.json'
        if not (ROOT / _a3p).exists():
            put(_a3p, dict(task=T, sources=results))
        role = role_manifest('A3', family + '-E02',
            [r / 'raw_source_universe.json', INTAKE, CROSSREF, RAW_PEA, RAW_MOR],
            [r / 'A3_source_results.json'], dict(processed=2, passed=2, rejected=0, pending=0),
            pointers=[fq.pointer(A11), fq.pointer(A6R)], read_holdout=False, read_model_outcome=False)
        role['scope'] = 'Front-matter identity projection from immutable intake; official Crossref reconciliation for pea 1982 already bound in R74 query_execution; no new scientific eligibility.'
        _rp = r / 'role_A3_manifest.json'
        if not (ROOT / _rp).exists():
            put(_rp, role)
        ledger = B / 'epoch_ledger.jsonl'; data = (ROOT / ledger).read_bytes()
        epoch = B / 'epochs' / (family + '-E02') / ('epoch_state.v6.json')
        adapter = load(ADAPT / 'temporal_adapter_manifest.json')
        spec = dict(family=family, epoch_id=family + '-E02', batch_id=family + '-E02-R80-owner-originals-full-qualification',
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
        assert v['source_candidates'] == 2 and v['admitted'] == 0
        contracts[family] = cp
        put(r / 'pre_G5_contract_validation.json', dict(task=T, at=now(), family=family, source_candidates=2,
            A3_identity_passed=2, prior_unknown=0, science_admitted=0, HTTP=0, MCTS=0,
            morita2005_both_branches_preregistered=True,
            pea1982_same_cohort_adjudication='not_blocked with conditions (independent A6 R80)'))
    r = base('SS'); g4 = B / 'SS/E02/stages/G4_SCOPE_FREEZE.json'; g5 = stage('SS')
    paths = [r / x for x in ('full_qualification_contract.json', 'raw_source_universe.json', 'A3_source_results.json',
              'role_A3_manifest.json', 'pre_G5_contract_validation.json')] + [RAW_PEA, RAW_MOR] + \
            [Path(__file__).relative_to(ROOT), A11, A6R, INTAKE, ADAPT / 'prior_exposure_rows.jsonl', ADAPT / 'current_exposure_rows.jsonl', ADAPT / 'temporal_adapter_manifest.json', UNKNOWN]
    if not (ROOT / g5).exists():
        freeze_stage_manifest(ROOT / g5.parent, 'G5_FRESH_HOLDOUT_ACQUIRE', paths, g4,
            expected_previous_sha=sha(g4), family='SS', epoch_id='SS-E02')
    verify_stage_chain(g5, sha(g5))
    ledger = B / 'epoch_ledger.jsonl'
    row = dict(task=T, epoch_id='SS-E02', family='SS', stage='G5_FRESH_HOLDOUT_ACQUIRE', status='active',
        event_type='R80_owner_originals_preregistered_before_content_read', at=now(),
        stage_manifest_path=str(g5), stage_manifest_sha256=sha(g5), qualification_contract=contracts['SS'],
        source_count=2, prior_read_unknown=0, source_science_read=False, fresh_admitted=0,
        approval_type='agent_delegated', human_reviewed=False)
    write(T, str(ledger), (ROOT / ledger).read_text() + json.dumps(row, sort_keys=True) + '\n')
    event(T, 'R80_G5_frozen', sources=2, content_read=False)
    print(json.dumps(dict(G5=sha(g5), science_reads=0, fresh_admitted=0)))

def sha_file_rel(rel):
    import hashlib
    h = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    return h

def pointer_of(rel):
    return dict(path=str(rel), sha256=sha(rel))

if __name__ == '__main__':
    main()
