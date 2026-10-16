"""TASK-016-P7 owner-supplied originals intake (manual_grabbed_1, 11 papers).
Immutable custody + first-page identity triage only. NO scientific content read.
Fresh-candidate designation: P1-1 (pea 1982) and P1-2 (Morita 2005) may proceed to
a future SS G5 preregistration; C8-cluster content reads are DEFERRED to C-E03
design/freeze sequencing (reading now would burn the prospective fresh pool).
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, shutil, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from operate import write, event

TASK = 'TASK-016-P7'
REL = Path('outputs/task016-p7/v1/manual_grabbed_20261012/manual_grabbed_1')
DEST = Path('data/raw/task016-p7/manual_grabbed_20261012/manual_grabbed_1')
SOURCE = Path('temp/manual_grabbed_1')

RECORDS = [
 dict(file='P1-1-jourdan1982.pdf', doi='10.1016/0003-9861(82)90569-0', pmid='6462109',
      title_tokens=['Isolation', 'glucosyl transferases', 'flavonol triglucosides', 'Pisum sativum'],
      year='1982', journal_tokens=['Arch', 'Biochem', 'Biophys'], role='SS_fresh_candidate',
      prior_status='R11 metadata-only discovery hint (R11-RESOLVE-DB-01-O0014); never chemically examined; exposure ledger 0 rows; same-cohort closure risk with exposed 1979 pea paper must be adjudicated by A6'),
 dict(file='P1-2-morita2005.pdf', doi='10.1111/j.1365-313x.2005.02383.x', pmid='15842621',
      title_tokens=['Japanese morning glory', '2', 'glucosyltransferase', 'anthocyanin'],
      year='2005', journal_tokens=['Plant J'], role='SS_fresh_candidate',
      prior_status='no P7 metadata-store hit beyond R76 lead; exposure ledger 0 rows'),
 dict(file='P2-1-he2019.pdf', doi='10.1002/anie.201905505', pmid=None,
      title_tokens=['Promiscuous', 'Glycosyltransferase', 'Trollius chinensis'],
      year='2019', journal_tokens=['Angew'], role='C8_design_deferred',
      prior_status='exposure ledger 0 rows; C8-cluster content read DEFERRED to C-E03 design/freeze sequencing (early read would burn the prospective fresh pool)'),
 dict(file='P2-2-liu2021.pdf', doi='10.1021/acs.jafc.1c00602', pmid=None,
      title_tokens=['Orientin', 'Vitexin', 'Sucrose Synthase', 'Luteolin'],
      year='2021', journal_tokens=['Agric', 'Food', 'Chem'], role='C8_design_deferred',
      prior_status='exposure ledger 0 rows; C8-cluster content read DEFERRED (same reason)'),
 dict(file='P2-3-qiu2021.pdf', doi='10.1016/j.bioorg.2021.104926', pmid=None,
      title_tokens=['Orientin', 'vitexin', 'cascade', 'sucrose synthase'],
      year='2021', journal_tokens=['Bioorg', 'Chem'], role='C8_design_deferred',
      prior_status='exposure ledger 0 rows; C8-cluster content read DEFERRED (same reason)'),
 dict(file='P3-1-kamsteeg1979.pdf', doi='10.1016/S0031-9422(00)84283-1', pmid=None,
      title_tokens=['RHAMNOSE', 'ANTHOCYANIDIN', 'PROPERTIES'], year='1979',
      journal_tokens=['Phytochemistry'], role='SS_boundary_reference',
      prior_status='actual title (front page): UDP-L-rhamnose:anthocyanidin 3-O-glucoside 6\"-O-rhamnosyltransferase, Petunia; 6\"-O-Rha is OUTSIDE the frozen SS-E02 O2-glucosylation scope - boundary/reference only'),
 dict(file='P3-2-kho1978.pdf', doi='10.1016/S0044-328X(78)80261-X', pmid=None,
      title_tokens=['flavonol', 'glycosyltransferase'], year='1978',
      journal_tokens=['Pflanzenphysiol'], role='SS_historical_low_priority',
      prior_status='not in exposure ledger; content unknown'),
 dict(file='P3-3-heinsbroek1979.pdf', doi='10.1016/S0031-9422(00)91452-3', pmid=None,
      title_tokens=['flavonol', 'glucosyltransferase'], year='1979',
      journal_tokens=['Phytochemistry'], role='SS_historical_low_priority',
      prior_status='C-E01-era metadata dispositions only'),
 dict(file='P3-4-sutter1973.pdf', doi='10.1016/0005-2744(73)90027-2', pmid=None,
      title_tokens=['glucosyltransferase', 'flavonol'], year='1973',
      journal_tokens=['Biochim', 'Biophys', 'Acta'], role='SS_historical_low_priority',
      prior_status='SS-side metadata hint only'),
 dict(file='P3-opt-jf5c09887.pdf', doi='10.1021/acs.jafc.5c09887', pmid='41568575',
      title_tokens=['Glycosyltransferase', 'Euscaphis'], year='2026',
      journal_tokens=['Agric', 'Food', 'Chem'], role='C_boundary_optional',
      prior_status='chromone substrate per abstract; flavonol panel unknown'),
 dict(file='王源杰（2018）硕士学位论文-毛竹叶黄酮碳苷C-糖基化途径及C-糖基转移酶的分析_王源杰.pdf', doi=None, pmid=None,
      title_tokens=['毛竹', 'C', '糖基转移酶'], year='2018', journal_tokens=['林业', '科学研究院'],
      role='C6_design_deferred',
      prior_status='thesis full text; natural bamboo CGT direct luteolin C6; C6 fresh pool depends on its substrate panel'),
]

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''): h.update(chunk)
    return h.hexdigest()

def now(): return datetime.now(timezone.utc).isoformat()

def main():
    if (ROOT / REL / 'intake_manifest.json').exists(): raise RuntimeError('manual_grabbed_1 intake manifest already exists')
    # state-aware resume: prior partial run copied some files before an identity abort; reuse SHA-verified copies
    rows = []
    for rec in RECORDS:
        src = ROOT / SOURCE / rec['file']
        if not src.is_file(): raise FileNotFoundError(rec['file'])
        if src.open('rb').read(5) != b'%PDF-': raise RuntimeError('NOT_PDF ' + rec['file'])
        h = sha(src)
        dest = ROOT / DEST / rec['file']
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            if sha(dest) != h: raise RuntimeError('EXISTING_COPY_DRIFT ' + rec['file'])
        else:
            shutil.copyfile(src, dest)
            if sha(dest) != h: raise RuntimeError('COPY_CHECKSUM_ERROR ' + rec['file'])
            dest.chmod(0o444)
        info = subprocess.run(['pdfinfo', str(dest)], capture_output=True, text=True, check=True)
        pages = int(re.search(r'^Pages:\s*(\d+)', info.stdout, re.M).group(1))
        text = subprocess.run(['pdftotext', '-f', '1', '-l', '2', '-layout', str(dest), '-'],
                              capture_output=True, text=True, check=True).stdout
        if not text or len(text) < 300: raise RuntimeError('NO_SUBSTANTIVE_FIRST_PAGE ' + rec['file'])
        flat = re.sub(r'\s+', ' ', text)
        year_ok = rec['year'] in flat
        title_hits = sum(1 for t in rec['title_tokens'] if t.lower() in flat.lower())
        journal_ok = any(t.lower() in flat.lower() for t in rec['journal_tokens'])
        doi_in_page = rec['doi'].lower() in flat.lower() if rec['doi'] else False
        checks = sum([year_ok, title_hits >= 2, journal_ok])
        if rec['role'].startswith('SS_fresh') and checks < 2:
            raise RuntimeError('IDENTITY_WEAK_FRESH_CANDIDATE ' + rec['file'] + ' flat=' + flat[:200])
        rows.append(dict(file=rec['file'], sha256=h, bytes=dest.stat().st_size, pages=pages,
            expected_doi=rec['doi'], expected_pmid=rec['pmid'], expected_year=rec['year'],
            identity={'year_ok': year_ok, 'title_token_hits': title_hits, 'journal_ok': journal_ok,
                      'doi_literal_in_front': doi_in_page},
            identity_status='provisionally_verified_front_matter_only' if checks >= 2 else 'weak_front_matter_recorded',
            role=rec['role'], prior_status=rec['prior_status'],
            scientific_content_read=False, chemical_extracted=False,
            official_meta_check='deferred_to_A3_round'))
    manifest = dict(task=TASK, at=now(), batch='manual_grabbed_1', source=str(SOURCE),
        approval_type='agent_delegated', human_reviewed=False, count=len(rows),
        destination=str(DEST),
        intake_discipline=dict(first_two_pages_identity_only=True, scientific_content_read=False,
            chemical_extracted=False, HTTP=0, MCTS=0,
            fresh_sequencing=dict(SS_candidates='G5 preregistration REQUIRED before any content read',
                                  C8_cluster='content reads DEFERRED to C-E03 design/freeze sequencing; early read would burn the prospective fresh pool',
                                  C6_thesis='content read deferred pending C6 direction decision'),
            no_paywall_bypass=True, owner_supplied_permission_not_redistribution_clearance=True),
        files=rows)
    write(TASK, str(REL / 'intake_manifest.json'), json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    write(TASK, str(REL / 'intake_receipt.json'), json.dumps(dict(task=TASK, at=now(),
        files=[dict(file=r['file'], sha256=r['sha256'], bytes=r['bytes'], pages=r['pages']) for r in rows],
        all_identity_provisionally_verified=all(r['identity_status'].startswith('provisionally') for r in rows)), ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    event(TASK, 'manual_intake_1_completed', count=len(rows), bytes=sum(r['bytes'] for r in rows))
    print(json.dumps(dict(count=len(rows), dest=str(DEST),
        identities=[dict(f=r['file'][:28], ok=r['identity_status'][:14], doi_hit=r['identity']['doi_literal_in_front']) for r in rows]), ensure_ascii=False))

if __name__ == '__main__':
    main()
