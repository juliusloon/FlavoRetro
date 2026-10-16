"""R82: Trapero 2012 (PMC3425182) late-prior-design structural-evidence read.

Source is identifier-level design-exposed (2 historical_design rows), so the
fresh-qualification lane is closed by policy; this batch executes the dual-reader
content read AFTER the R81 G5 preregistration freeze, for the SS scope-design
question: does the body provide structural evidence for sophoroside 1->2 linkage
(NMR / methylation / authentic standard)?
"""
import json, os, re, hashlib
import html as htmllib
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now
from scripts.task016_p7_orchestrate import role_manifest, verify_stage_chain
from scripts.task016_p7_r47_A4 import parse as parse_a4
from scripts import task016_p7_full_qualification_harness_v4 as fq

T = 'TASK-016-P7'; B = Path('outputs/task016-p7/v1')
R81 = B / 'SS/E02/fresh/SS-E02-R81-owner-originals-full-qualification-v1'
CONTRACT = fq.pointer(R81 / 'full_qualification_contract.json')
G5 = fq.pointer(B / 'SS/E02/stages/batches/SS-E02-R81-owner-originals-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json')
R = B / 'SS/E02/fresh/SS-E02-R82-trapero-structural-evidence-read-v1'
RAW = dict(path='data/raw/task016-p7/SS/E02/SS-E02-R78-trapero2012-raw-custody-v1/R78-368f3ba8993540008fe51d793455e803.bin',
           sha256='d41422e74fc01299bd7b8581fbc9cd7786e629b1f2cac46f8710a35222812e90')
SID = 'SS-E02-R81-S01'
TOKENS = ['article:PMC3425182', 'doi:10.1104/pp.112.198069', 'pmcid:PMC3425182', 'pmid:22649274']
CTX = re.compile(r'sophoros|diglucoside|triglucoside|2["\u2032\u2033\']{1,2}\s*-?\s*O|1\s*(?:\u2192|->)\s*2|1,2[- ]linked|NMR|methylat|authentic (?:standard|sample)|FAB|LC[- ]?MS|MS/MS|mass spectromet|product identif|structural (?:assignment|determination|elucidation)|co[- ]?chromatog|UGT707B1|kaempferol|quercetin|glucosyltransferase|UDP[- ]glucose', re.I)

def parse_a5(data):
    """Independent second parser: stdlib regex block extraction (no lxml)."""
    text = data.decode('utf-8')
    m = re.search(r'(?is)<article[\s>].*?</article>', text)
    body = m.group(0) if m else text
    body = re.sub(r'(?is)<(script|style|head)[^>]*>.*?</\1>', ' ', body)
    sections = [mm.group(1) for mm in re.finditer(r'(?is)<section[^>]*\bid="([^"]*)"', body)]
    pat = re.compile(r'(?is)<(p|h1|h2|h3|h4|tr|figcaption)([^>]*)>(.*?)</\1\s*>')
    blocks = []
    for mm in pat.finditer(body):
        tag, attrs, inner = mm.group(1).lower(), mm.group(2), mm.group(3)
        before = body[:mm.start()]
        sec = [s for s in re.finditer(r'(?is)<section[^>]*\bid="([^"]*)"[^>]*>', before)]
        section_path = [s.group(1) for s in sec[-6:]]
        idm = re.search(r'(?i)\bid="([^"]*)"', attrs)
        txt = re.sub(r'(?s)<[^>]+>', ' ', inner)
        txt = ' '.join(htmllib.unescape(txt).split())
        if not txt:
            continue
        blocks.append(dict(tag=tag, index=len(blocks) + 1, section_path=section_path,
                           element_id=idm.group(1) if idm else None, text=txt))
    return blocks

def contexts(blocks):
    out = []
    for blk in blocks:
        if CTX.search(blk['text']):
            out.append(dict(index=blk['index'], tag=blk['tag'], section_path=blk['section_path'],
                            text=blk['text'][:2000], text_SHA=hashlib.sha256(blk['text'].encode()).hexdigest()))
    return out

def main():
    g5 = verify_stage_chain(ROOT / G5['path'], G5['sha256'])
    assert g5['stage'] == 'G5_FRESH_HOLDOUT_ACQUIRE' and g5['epoch_id'] == 'SS-E02'
    spec = fq.load(CONTRACT)
    assert spec['source_candidate_ids'] == [SID], spec['source_candidate_ids']
    # --- 1. execution-proof probe: the fq fresh lane must refuse this source ---
    probe = None
    try:
        fq.open_for_first_scientific_read(CONTRACT, G5, SID, 'A4', 'R82-fresh-lane-probe')
        probe = dict(fresh_lane='NOT_BLOCKED_UNEXPECTED', note='probe unexpectedly passed; closure rests on policy + A6 qualification gates instead')
    except Exception as exc:
        probe = dict(fresh_lane='closed_by_harness', error_type=type(exc).__name__, error=str(exc)[:500],
                     interpretation='policy prior_design_or_historical_exposure_still_excludes; requires exclusion or explicit recovery contract; structural-evidence read proceeds in the late-prior-design lane only')
    put(R / 'A0_fresh_lane_closure_probe.json', dict(task=T, at=now(), probe=probe,
        policy='governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json#prior_design_or_historical_exposure_still_excludes',
        exposure_rows_intersecting=['governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl#L2548', 'governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl#L3209'],
        G5_preregistration=G5, contract=CONTRACT, approval_type='agent_delegated', human_reviewed=False))
    # --- 2. dual isolated readers on the sealed custody HTML ---
    data = (ROOT / RAW['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == RAW['sha256'], 'CUSTODY_DRIFT'
    outs = {}
    for role, parser_name, fn in (('A4', 'stdlib HTMLParser (r47_A4.Reader)', parse_a4),
                                  ('A5', 'stdlib regex block extraction (R82-local)', parse_a5)):
        rid = 'R82-' + role + '-' + str(os.getpid())
        dest = R / role
        common = dict(task=T, approval_type='agent_delegated', human_reviewed=False, family='SS',
            epoch_id='SS-E02', batch_id='SS-E02-R82-trapero-structural-evidence-read',
            reader_role=role, reader_id=rid, source_id=SID,
            official_aliases=['doi:10.1104/pp.112.198069', 'pmid:22649274', 'article:PMC3425182'],
            closure_tokens=TOKENS, raw_files=[RAW], G5=G5,
            development_exposed=True, prior_design=True, exposure_type='historical_design',
            future_fresh_eligible=False, current_epoch_fresh_eligible=False,
            read_other_extractor_output=False, read_model_outcome=False,
            scientific_read_lane='late_prior_design structural-evidence read after R81 G5 preregistration')
        started = dict(common, event_type='scientific_read_started', timestamp=now(), scientific_content_read=False)
        put(dest / 'scientific_read_started.json', started)
        blocks = []
        for blk in fn(data):
            txt = ' '.join(blk['text'].split()) if 'text' in blk else blk.get('text', '')
            blk = dict(blk); blk['text'] = txt
            blk['text_SHA'] = hashlib.sha256(txt.encode()).hexdigest()
            blk['source_file'] = RAW['path']; blk['source_SHA'] = RAW['sha256']
            blocks.append(blk)
        assert blocks, 'no text blocks extracted'
        ctx = contexts(blocks)
        out = dest / 'original_article_text_blocks.json'
        put(out, dict(task=T, agent_role=role, source_id=SID, parser=parser_name, blocks=blocks,
            literal_linkage_evidence_contexts=ctx,
            all_article_text_blocks_processed=True, source_images_not_downloaded_or_transcribed=True,
            independent_graph_transcription=False, chemical_reaction_enumeration_complete=False,
            read_other_extractor_output=False, scope_modified=False, fresh_admitted=0))
        ended = dict(common, event_type='scientific_read_completed', timestamp=now(),
            scientific_content_read=True, output_pointer=dict(path=str(out), sha256=sha(out)),
            stored_text_blocks=len(blocks), linkage_evidence_context_blocks=len(ctx))
        put(dest / 'scientific_read_completed.json', ended)
        manifest = role_manifest(role, 'SS-E02', [CONTRACT['path'], G5['path'], Path(RAW['path']),
            Path(__file__).resolve().relative_to(ROOT)],
            [out, dest / 'scientific_read_started.json', dest / 'scientific_read_completed.json'],
            dict(processed=1, passed=0, rejected=0, pending=1), pointers=[RAW, G5],
            read_holdout=True, read_model_outcome=False)
        manifest.update(reader_id=rid, read_other_extractor_output=False,
            count_unit='one design-exposed source structural-evidence text extraction; no fresh qualification granted')
        put(dest / 'role_manifest.json', manifest)
        outs[role] = dict(blocks=len(blocks), contexts=len(ctx), output=str(out), sha256=sha(out))
        event(T, 'R82_design_lane_read_completed', role=role, blocks=len(blocks), contexts=len(ctx))
    # --- 3. permanent exposure rows (R68 row schema) ---
    rows = []
    for role in ('A4', 'A5'):
        base = R / role
        started = json.loads((ROOT / base / 'scientific_read_started.json').read_text())
        ended = json.loads((ROOT / base / 'scientific_read_completed.json').read_text())
        for row in (started, ended):
            keep = {k: row[k] for k in ('task', 'approval_type', 'human_reviewed', 'family', 'epoch_id',
                'batch_id', 'reader_role', 'reader_id', 'source_id', 'official_aliases', 'closure_tokens',
                'raw_files', 'G5', 'development_exposed', 'prior_design', 'exposure_type',
                'future_fresh_eligible', 'current_epoch_fresh_eligible', 'read_other_extractor_output',
                'read_model_outcome', 'event_type', 'timestamp', 'scientific_content_read')}
            rows.append(keep)
    write(T, str(R / 'scientific_exposure_reads.jsonl'), ''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows))
    put(R / 'A0_batch_summary.json', dict(task=T, at=now(), batch='SS-E02-R82-trapero-structural-evidence-read',
        source_id=SID, custody=RAW, G5_preregistration=G5, contract=CONTRACT,
        fresh_lane_probe=probe, readers=outs, exposure_rows=len(rows),
        core_question='does the body provide structural evidence for sophoroside 1->2 linkage (NMR/methylation/authentic standard)',
        disposition='A6 determination draft follows in a separate immutable record; nothing here grants fresh eligibility',
        approval_type='agent_delegated', human_reviewed=False))
    print(json.dumps(dict(probe=probe['fresh_lane'], a4_blocks=outs['A4']['blocks'], a4_ctx=outs['A4']['contexts'],
        a5_blocks=outs['A5']['blocks'], a5_ctx=outs['A5']['contexts']), ensure_ascii=False))

if __name__ == '__main__':
    main()
