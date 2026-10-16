"""Rebuild frozen P2/P3 core payloads from the same raw source snapshots."""
import json,shutil
from pathlib import Path
from scripts.task016_p1_sources import ROOT,OUT as ORIGINAL,save
from scripts.operate import write,event
from flavoretro.resources import sha

def replay():
    target=ROOT/'outputs/task016-p1/replay-v1';assert not target.exists();target.mkdir(parents=True)
    inputs=['rhea_knowledge_records.jsonl','identity_manifest.json','identity_additional_manifest.json','identity_epimedium_manifest.json','article_acquisition_manifest.json','article_acquisition_addendum.json','assay_annotations.json']
    for name in inputs:shutil.copy2(ORIGINAL/name,target/name)
    import scripts.task016_p1_sources as sources
    sources.OUT=target
    # Execute the configuration-driven annotator without mutating the frozen originals.
    source=(ROOT/'scripts/task016_p1_curate.py').read_text()
    exec(compile(source,str(ROOT/'scripts/task016_p1_curate.py'),'exec'),dict(__file__=str(ROOT/'scripts/task016_p1_curate.py'),__name__='__main__'))
    import scripts.task016_p1_freeze as freezer
    freezer.OUT=target;freezer.freeze()
    import scripts.task016_p1_build as builder
    builder.OUT=target
    import scripts.operate as operations
    original_write=operations.write
    def redirected(task,path,content):
        if path.startswith('configs/') or path.startswith('flavoretro/assets/configs/'):
            path=str((target/'configuration-copy'/path).relative_to(ROOT))
        return original_write(task,path,content)
    operations.write=redirected
    try:builder.build()
    finally:operations.write=original_write
    names=['provisional_instances.jsonl','assay_record_dispositions.jsonl','instances.jsonl','build_views.jsonl','runtime_instances.jsonl','holdout_views.jsonl','reference_precursors.jsonl','dedup_links.jsonl','reaction_groups.jsonl','counting_contract.json','development_split_manifest.json','evaluation_reference_manifest.json','templates.jsonl','template_validation.jsonl','template_groups.jsonl','applicability_contract.json','representation_rules.json','fusion_contract.json','review_binding.json','template_source_manifest.json']
    checks=[dict(path=n,original_sha256=sha(ORIGINAL/n),replayed_sha256=sha(target/n),equal=sha(ORIGINAL/n)==sha(target/n)) for n in names]
    write('TASK-016-P1','outputs/task016-p1/v1/replay.json',json.dumps(dict(passed=all(r['equal'] for r in checks),checks=checks,files=len(checks),scope='same-source deterministic source annotations, closure split and build-only templates; no MCTS cache or independent chemistry claim'),indent=2)+'\n')
    event('TASK-016-P1','core_replay_completed',files=len(checks),passed=all(r['equal'] for r in checks))
    print('byte-identical core files',sum(r['equal'] for r in checks),'/',len(checks));print([r['path'] for r in checks if not r['equal']])
if __name__=='__main__':replay()
