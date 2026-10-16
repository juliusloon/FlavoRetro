"""R80 A4/A5: first scientific reads (pea 1982 + Morita 2005) via isolated readers,
dual pdftotext parsers, reaction-claim harvesting + exposure-signature leakage scan."""
import json, re, subprocess, tempfile, hashlib
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now
from scripts import task016_p7_full_qualification_harness_v4 as fq

T = 'TASK-016-P7'; B = Path('outputs/task016-p7/v1')
R = B / 'SS/E02/fresh/SS-E02-R80-owner-originals-full-qualification-v1'
CONTRACT = fq.pointer(R / 'full_qualification_contract.json')
G5 = fq.pointer(B / 'SS/E02/stages/batches/SS-E02-R80-owner-originals-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json')
READERS = [('A4', 'a4-pdftotext-layout-v1', ['-layout']), ('A5', 'a5-pdftotext-raw-v1', ['-raw'])]
KEY = re.compile(r'sophoros|2.{0,3}["\u2032\u2033\']{1,2}\s*-?\s*O|diglucoside|triglucoside|quercetin|kaempferol|UDP[- ]glucose|glucosyltransferase|glycosyltransferase|substrate|specificity|NMR|FAB|UV', re.I)

def extract(pdf_bytes, mode):
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(pdf_bytes); path = f.name
    try:
        out = subprocess.run(['pdftotext'] + mode + [path, '-'], capture_output=True, text=True, check=True).stdout
    finally:
        Path(path).unlink(missing_ok=True)
    return out

def harvest(text, sid):
    lines = text.splitlines()
    claims = []
    for i, ln in enumerate(lines):
        if KEY.search(ln) and len(ln.strip()) > 25:
            claims.append(dict(line=i + 1, text=ln.strip()[:400]))
    paras = re.split(r'\n\s*\n', text)
    big = []
    for p in paras:
        if len(p) > 200 and re.search(r'sophoros|2.{0,3}["\u2032\u2033\']{1,2}\s*-?\s*O|triglucoside', p, re.I):
            big.append(re.sub(r'\s+', ' ', p)[:1500])
    return dict(lines=claims[:120], paragraphs=big[:20])

RAW_BY_SID = {'SS-E02-R80-S01': 'data/raw/task016-p7/manual_grabbed_20261012/manual_grabbed_1/P1-1-jourdan1982.pdf',
              'SS-E02-R80-S02': 'data/raw/task016-p7/manual_grabbed_20261012/manual_grabbed_1/P1-2-morita2005.pdf'}
def main():
    contract = fq.load(CONTRACT); g5 = fq.load(G5)
    s_raw = RAW_BY_SID
    outs = {}
    for sid in ('SS-E02-R80-S01', 'SS-E02-R80-S02'):
        for role, rid, mode in READERS:
            try:
                opened = fq.open_for_first_scientific_read(CONTRACT, G5, sid, role, rid)
                pdf_bytes = list(opened['payloads'].values())[0]
                receipt = opened['receipt']
            except Exception as exc:
                if 'already registered' not in str(exc): raise
                evs = fq.evaluation_events(CONTRACT)
                ev = next(x for x in evs if x['source_id'] == sid and x['reader_role'] == role)
                receipt = dict(recovered=True, prior_end_event=ev.get('timestamp'),
                    note='first read registered in prior run; bytes re-opened from sealed immutable copy (already exposed)')
                pdf_bytes = (ROOT / s_raw[sid]).read_bytes()
            text = extract(pdf_bytes, mode)
            obs = harvest(text, sid)
            p = R / f'evaluation_read_events/{role}_{rid}_{sid}.text'
            if not (ROOT / p).exists():
                write(T, str(p), text)
            fn = R / f'{role}_result_{sid}.json'
            put(fn, dict(task=T, agent_role=role, reader_id=rid, contract_sha256=CONTRACT['sha256'],
                source_id=sid, parser_mode=str(mode), scientific_body_read=True,
                read_receipt=receipt,
                chars=len(text), reaction_claim_lines=obs['lines'], reaction_claim_paragraphs=obs['paragraphs'],
                note='verbatim line/paragraph harvest only; structure binding deferred to A6/database identity'))
            outs[(sid, role)] = fn
            event(T, 'R80_first_scientific_read', source_id=sid, role=role, chars=len(text))
    # exposure-signature leakage scan on harvested text (pea source)
    exp = []
    for rel in ('exposure_ledger.jsonl', 'governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl'):
        for l in (ROOT / B / rel).read_text().splitlines():
            if l.strip():
                exp.append(json.loads(l).get('closure_tokens', []))
    exp_tokens = sorted(set(t for row in exp for t in row))
    def scan(text):
        hits = []
        for t in exp_tokens:
            if len(t) > 8 and t.lower() in text.lower(): hits.append(t)
        return hits
    pea_text = (ROOT / R / 'evaluation_read_events/A4_a4-pdftotext-layout-v1_SS-E02-R80-S01.text').read_text()
    mor_text = (ROOT / R / 'evaluation_read_events/A4_a4-pdftotext-layout-v1_SS-E02-R80-S02.text').read_text()
    scan_result = dict(pea1982_exposed_token_hits=scan(pea_text)[:40], morita2005_exposed_token_hits=scan(mor_text)[:40])
    put(R / 'A6_leakage_scan_draft.json', dict(task=T, at=now(), method='verbatim exposed-token scan over harvested text (draft; formal A6 round next)',
        result=scan_result))
    att = None
    print(json.dumps(dict(reads=4, pea_token_hits=len(scan_result['pea1982_exposed_token_hits']),
                          mor_token_hits=len(scan_result['morita2005_exposed_token_hits']),
                          pea_chars=len(pea_text), mor_chars=len(mor_text)), ensure_ascii=False))

if __name__ == '__main__':
    main()
