import json,shutil,stat
from pathlib import Path
from operate import ROOT,digest,event,write
SRC=Path('/home/ljx/retro_synthesis'); selected={}
def add(rel,role):
    p=SRC/rel
    if p.is_file() and not p.name.startswith('._'): selected[rel]=role
for rel in ['docs/reports/260920-pre_refactor_project_retrospective.md','outputs/retrospective/2026-09-20/inventory.json','outputs/retrospective/2026-09-20/test_contract_catalog.md','outputs/retrospective/2026-09-20/proposal_first_git_version.md','outputs/retrospective/2026-09-20/early_template_search_summary.md']:
    add(rel,'historical_reference')
for rel in ['templates/literature_curated/flavonoid_literature_reactions.json','templates/production/production_template_registry.json','templates/stock_layers/production_stock_registry.json','templates/stock_layers/stock_layers_metadata.csv','outputs/publication/2026-09-10/library_v3/molecule_library.csv','outputs/publication/2026-09-10/library_v3/summary.json','outputs/validation/stock-identity-review-20260912/stock_identity_review.json','config/product/literature_registry.json','config/product/target_panel.json']:
    add(rel,'candidate_data')
for folder in ['import_raw','files','outputs/publication/2026-09-10/scifinder_import','maintenance/metadata/source_manifests','maintenance/metadata/dataset_cards']:
    for p in (SRC/folder).rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts: add(str(p.relative_to(SRC)),'source_evidence')
for rel in ['data/uspto_model.onnx','data/uspto_templates.csv.gz','data/uspto_filter_model.onnx','data/uspto_ringbreaker_model.onnx','data/uspto_ringbreaker_templates.csv.gz']:
    add(rel,'external_model')
# Frozen API responses are admitted by content hash referenced in historical records.
refs=set()
for p in (SRC/'maintenance/metadata/source_manifests').glob('*.json'):
    for token in p.read_text().replace('"', ' ').split():
        if len(token)==64 and all(c in '0123456789abcdef' for c in token): refs.add(token)
base=json.loads((ROOT/'operations/history-before.json').read_text())
for rel,item in base.items():
    if item.get('sha256') in refs and rel.endswith('.json'): add(rel,'frozen_source_response')
manifest=[]
for rel,role in sorted(selected.items()):
    src=SRC/rel; dest=ROOT/'data/raw/legacy'/rel
    if dest.exists(): raise RuntimeError('refuse overwrite '+str(dest))
    before=digest(src); dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dest); dest.chmod(0o444)
    assert before==digest(dest)==digest(src)
    row={'source_path':rel,'path':str(dest.relative_to(ROOT)),'sha256':before,'size':dest.stat().st_size,'role':role,'license_status':'source_inherited_not_cleared_for_redistribution','review_status':'historical_claims_only_not_revalidated','redistribute':False}
    manifest.append(row); event('TASK-002','copy_verified',**row)
write('TASK-002','metadata/sources.json',json.dumps({'schema_version':1,'source_root':str(SRC),'files':manifest},indent=2,ensure_ascii=False)+'\n')
inv=json.loads((SRC/'outputs/retrospective/2026-09-20/inventory.json').read_text())
checks=[]
for item in inv['source_manifest']+inv['python_source_catalog']:
    p=SRC/item['path']; checks.append({'path':item['path'],'matches':p.is_file() and digest(p)==item['sha256']})
write('TASK-002','outputs/validation/historical-inventory-check.json',json.dumps(checks,indent=2))
print(json.dumps({'copied_files':len(manifest),'bytes':sum(r['size'] for r in manifest),'historical_inventory_checks':len(checks),'drift':[r for r in checks if not r['matches']]}))
