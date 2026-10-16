"""R82 A6: structural-evidence determination for the sophoroside 1->2 linkage.

Verbatim quotes are extracted programmatically from the stored A4/A5 block
files (no manual transcription). Draft pending independent verification.
"""
import json, re
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now
from scripts.task016_p7_orchestrate import role_manifest

T = 'TASK-016-P7'; B = Path('outputs/task016-p7/v1')
R = B / 'SS/E02/fresh/SS-E02-R82-trapero-structural-evidence-read-v1'

def grab(blocks, pattern, group=0, flags=re.S):
    for blk in blocks:
        m = re.search(pattern, blk['text'], flags)
        if m:
            return dict(reader_block=blk['index'], tag=blk['tag'], section_path=blk.get('section_path'),
                        text_SHA=blk['text_SHA'], verbatim=m.group(group).strip())
    raise AssertionError('quote not found: ' + pattern[:60])

def main():
    a4 = json.loads((ROOT / R / 'A4/original_article_text_blocks.json').read_text())['blocks']
    a5 = json.loads((ROOT / R / 'A5/original_article_text_blocks.json').read_text())['blocks']
    quotes = {
      'hmbc_linkage_sentence_A4': grab(a4, r'Correlations observed between.*?moiety\.'),
      'aglycone_linkage_sentence_A4': grab(a4, r'In addition, the observed correlation between.*?aglycone moiety\.'),
      'compound_identification_sentence_A4': grab(a4, r'Therefore, compound 2 was identified as[^.]*\.'),
      'literature_concordance_sentence_A4': grab(a4, r'13C-NMR chemical shifts were in accordance with[^.]*\.'),
      'invitro_negative_sentence_A4': grab(a4, r'UGT707B1 eluted after[^.]*activity over any of the assayed substrates[^.]*\.'),
      'whole_cell_negative_sentence_A4': grab(a4, r'whole-cell biotransformation was carried out.*?unable to detect any activity\.'),
      'putative_activity_sentence_A4': grab(a4, r'putative flavonol 3-O-glucoside:2[^ ]*-O-glucosyltransferase activity'),
      'quercetin_sophoroside_ms_A4': grab(a4, r'Compound 1 has a m/z value corresponding to quercetin 3-O-sophoroside \(m/z [0-9.]+, Rt [0-9.]+ min\)'),
      'nmr_methods_sentence_A4': grab(a4, r'Structure elucidation was accomplished by NMR spectroscopy[^.]*\.'),
      'inner_glc_C2_table_row_A5': grab(a5, r'2\u2032\u2032\s+79\.53\s+3\.79'),
      'terminal_glc_anomeric_table_row_A5': grab(a5, r'Glc\u2032\u2032\u2032 moiety\s+1\u2032\u2032\u2032\s+102\.32\s+4\.77 \(7\.9\)'),
      'aglycone_C3_table_row_A5': grab(a5, r'3\s+133\.51'),
    }
    # dual-reader agreement on the in-vitro negative
    a5_invitro = [b for b in a5 if 'did not show appreciable activity' in b['text']]
    assert a5_invitro, 'A5 in-vitro negative missing'
    det = dict(task=T, at=now(), agent_role='A6', epoch_id='SS-E02',
        batch='SS-E02-R82-trapero-structural-evidence-read', source_id='SS-E02-R81-S01',
        approval_type='agent_delegated', human_reviewed=False, read_model_outcome=False,
        status='draft_pending_independent_verification',
        core_question='Does the Trapero 2012 body provide structural evidence for the sophoroside 1->2 linkage (NMR / methylation / authentic standard)?',
        verdict=dict(
            linkage_structural_evidence='PRESENT_DIRECT_2D_NMR_HMBC',
            linkage_evidence_basis=['1H-13C HMBC: terminal-Glc H1 (4.75 ppm) x inner-Glc C2 (79.53 ppm) and terminal-Glc C1 (102.32 ppm) x inner-Glc H2 (3.77 ppm) correlations establish beta-D-Glcp-(1->2)-beta-D-Glcp',
                                     'HMBC: Glc H1 (5.10 ppm) x aglycone C-3 (133.51 ppm) establishes the 3-O attachment',
                                     'two Glc units (12 sugar carbons), beta-configurations from anomeric coupling constants',
                                     '13C shifts concordant with literature (Markham et al., 1978)',
                                     'full 1H/13C assignment table (Table I) present in main text'],
            methylation_analysis='ABSENT (no permethylation/linkage-analysis channel anywhere in the retrieved text; only TMS external NMR reference and pathway wording)',
            authentic_standard_cochromatography='ABSENT (no co-injection with authentic sophoroside standard claimed; identification = NMR + HPLC-ESI-MS/MS + UV + literature values)',
            in_vitro_enzyme_activity='NOT_DEMONSTRATED (recombinant UGT707B1: no activity on any assayed substrate incl. kaempferol-3-glucoside; whole-cell biotransformation also negative; enzyme-level 2\"-O assignment rests on in vivo transgenic Arabidopsis metabolites + interspecies co-expression correlation)',
            nmr_product_origin='natural saffron tepal extract (HPLC-collected peak), NOT an UGT707B1 enzymatic product',
            structural_moiety_established=['kaempferol-3-O-beta-D-Glcp-(1->2)-beta-D-Glcp (compound 2, NMR-identified)',
                                            'quercetin 3-O-sophoroside (m/z 626.8, Rt 9.14 min, MS-level identification only)']),
        dual_reader_agreement=dict(
            a4_blocks=632, a5_blocks=207,
            hmbc_evidence_found_by_both=True, invitro_negative_found_by_both=True,
            numeric_shifts_consistent=['79.53 (inner Glc C-2)', '102.32 (terminal Glc C-1)', '133.51 (aglycone C-3)', '4.75-4.77 (terminal Glc H-1)']),
        design_corpus_implications=[
            'The 1->2 linkage semantics of the SS-E02 O2 scope now have a primary structural-evidence anchor inside project custody (design-corpus use only).',
            'Trapero 2012 is NOT a clean enzyme-level SS-O2 build support: no in vitro catalytic demonstration; product structure derives from natural-extract NMR.',
            'Fresh lane stays closed (execution-proven probe: closed_by_harness); SS fresh pool remains 0/0 pending new non-exposed sources.'],
        verbatim_quotes=quotes, errors=[])
    put(R / 'A6_structural_evidence_determination.json', det)
    manifest = role_manifest('A6', 'SS-E02',
        [R / 'A4/original_article_text_blocks.json', R / 'A5/original_article_text_blocks.json',
         B / 'SS/E02/fresh/SS-E02-R81-owner-originals-full-qualification-v1/full_qualification_contract.json',
         B / 'SS/E02/stages/batches/SS-E02-R81-owner-originals-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json',
         Path(__file__).resolve().relative_to(ROOT)],
        [R / 'A6_structural_evidence_determination.json'],
        dict(processed=1, passed=0, rejected=0, pending=1),
        pointers=[dict(path=str(R / 'A4/original_article_text_blocks.json'), sha256=sha(R / 'A4/original_article_text_blocks.json')),
                  dict(path=str(R / 'A5/original_article_text_blocks.json'), sha256=sha(R / 'A5/original_article_text_blocks.json'))],
        read_holdout=True, read_model_outcome=False)
    manifest.update(count_unit='one design-corpus structural-evidence determination; no fresh qualification granted')
    put(R / 'role_A6_manifest.json', manifest)
    event(T, 'R82_A6_determination_draft', verdict=str(det['verdict']['linkage_structural_evidence']))
    print(json.dumps(dict(quotes=len(quotes), verdict='PRESENT_DIRECT_2D_NMR_HMBC', methylation='ABSENT', standard='ABSENT', invitro='NOT_DEMONSTRATED')))

if __name__ == '__main__':
    main()
