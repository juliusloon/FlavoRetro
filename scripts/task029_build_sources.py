"""Build a new local source registry from already-held, SHA-verified papers."""
import copy, json, shutil, sys
from pathlib import Path
from scripts.operate import write, digest, event
from flavoretro.literature_policy import canonical

TASK = 'TASK-029'
if Path('outputs/task029/literature/v3/manifest.json').exists():
    raise SystemExit('Immutable v3 already exists; inspect the archive or approve a new version instead of overwriting it.')
lab = Path(sys.argv[1]).resolve()
base = json.loads(Path('outputs/task027/literature/v2/manifest.json').read_text())
rows = json.loads(Path(base['records']).read_text())
content = json.loads((lab/'frontend/student/content/demo-content.json').read_text())
sources = {s['source_id']: s for s in content['sources']}
assets = dict(base['assets'])
for sid, source in sources.items():
    original = lab/source['source_path']
    assert digest(original) == source['source_sha256'], sid
    rel = 'outputs/task029/sources/'+sid+'.pdf'
    p=Path(rel); p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(original,p)
    assets[rel] = digest(p)
    event(TASK, 'local_primary_copy', source=str(original), path=rel, sha256=digest(p), redistribution=False)
iso = copy.deepcopy(next(r for r in rows if r['reaction_id']=='T027:isoquercitrin:glucosylation'))
rutin = copy.deepcopy(next(r for r in rows if r['reaction_id']=='T027:rutin:rhamnosylation')['products'][0])

def source(sid, title):
    s=sources[sid]
    return dict(doi=s['doi'], title=title, url='https://doi.org/'+s['doi'], locator=s['source_locator'],
                evidence_scope='primary_full_text', local_path='outputs/task029/sources/'+sid+'.pdf',
                sha256=s['source_sha256'], license='local_existing_copy_no_new_redistribution')
pei = copy.deepcopy(iso)
pei.update(reaction_id='T029:Pei2019:UGT78D2', source=source('Pei2019', 'Synergistic Catalysis of Glycosyltransferase and Sucrose Synthase to Produce Isoquercitrin Through Glycosylation of Quercetin'),
 catalyst='AtUGT78D2；论文耦联 GmSUS 再生 UDP-葡萄糖（本动作仅重现糖基转移核心）',
 conditions=dict(context='Table 1 的 UDP-葡萄糖组与 Experimental 双酶标准反应须分开；不将标准条件移作单酶组条件', standard_coupled_assay='1.25 mM 槲皮素、200 mM 蔗糖、0.25 mM UDP、50 mM 磷酸盐 pH7.5、10% DMSO、70 mU/mL AtUGT78D2、120 mU/mL GmSUS；100 μL、35°C、30 min'),
 yield_value=None, yield_unit=None, yield_status='not_isolated_yield', yield_reported_text='搜索动作不复制产率；Table 1 供体/酶组合与16 h补料结果分开查阅',
 review_cautions=['本动作保留活化供体 UDP-葡萄糖；GmSUS 的蔗糖/UDP再生进入实验室作为开发方案，搜索未闭合其供体供给。','E. coli 为酶表达宿主，实际是纯酶体外体系。','文献报告、MCTS候选与学生实验观测分别登记；仍待教师审定。'],
 admission_task=TASK, approval='agent_delegated', lab_case=dict(route_id='R1', source_id='Pei2019', role='main_development'))
pei['reactants'][0]['name']='quercetin'
rows.append(pei)
zhang=copy.deepcopy(iso)
zhang.update(reaction_id='T029:Zhang2015:rutin_hydrolysis', category='source_bound_selective_hydrolysis',
 reactants=[rutin,dict(name='water', smiles='O', inferred=False, identity_source=dict(provider='explicit molecular formula',identifier='H2O',source='Zhang2015 hydrolysis methods'), identity_basis='explicit_water_in_hydrolysis',independently_verified=False)],
 source=source('Zhang2015','Biotransformation of rutin to isoquercitrin using recombinant α-l-rhamnosidase from Bifidobacterium breve'),
 catalyst='Bifidobacterium breve 来源重组 α-L-鼠李糖苷酶；E. coli 为表达宿主',
 conditions=dict(buffer='sodium phosphate pH6.5',temperature_c=55,rutin_mM=20,enzyme_U_per_ml=1.2, DMSO='方法与 Fig.4–5 为5%；结果段0.5%，冲突保留，不自行裁定'),
 yield_value=None,yield_unit=None,yield_status='not_isolated_yield',yield_reported_text='原文60/240 min过程结果不当作当前候选预测值；非分离收率',
 review_cautions=['正向为选择性水解芦丁的末端鼠李糖苷键，保留3-O葡萄糖；不是从槲皮素加糖。','只登记主产物回溯，鼠李糖副产物不作为目标；未声明完整质量衡算已验证。','溶剂比例与动力学数值有原文冲突，实验条件不可无条件照搬。'],
 admission_task=TASK,approval='agent_delegated',lab_case=dict(route_id='R2',source_id='Zhang2015',role='alternative_synthesis'))
zhang['precursors']='.'.join(sorted(canonical(p['smiles']) for p in zhang['reactants']))
rows.append(zhang)
contexts=[dict(target=iso['target'],lab_case=dict(route_id='R3',source_id='Niu2024',role='parallel_development'),
 source=source('Niu2024','Combinatorial metabolic engineering of Bacillus subtilis enables the efficient biosynthesis of isoquercitrin from quercetin'),
 title='工程菌供体供给与降解控制', description='外加槲皮素经 UGT78D2 工程枯草芽孢杆菌转化；比较胞内 UDP-葡萄糖供给、底物降解及产物水解改造。',
 evidence_role='same_product_whole_cell_development', mcts_action=False, human_reviewed=False, independent_chemical_validation=False,
 cautions=['工程菌改造不是独立的单步分子逆合成动作。','不属于从葡萄糖出发的从头合成；不把菌株改造效果线性相加。'])]
folder='outputs/task029/literature/v3'
write(TASK,folder+'/records.json',json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
write(TASK,folder+'/contexts.json',json.dumps(contexts,ensure_ascii=False,indent=2)+'\n')
assets[folder+'/contexts.json']=digest(folder+'/contexts.json')
manifest={**base,'version':'task029-lab-exact-source-v3','records':folder+'/records.json','records_sha256':digest(folder+'/records.json'),'assets':assets,'development_contexts':folder+'/contexts.json','admission_task':TASK}
write(TASK,folder+'/manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for cfg in ['configs/runtime-candidates.json','flavoretro/assets/configs/runtime-candidates.json']:
 value=json.loads(Path(cfg).read_text());value['literature']={'manifest':folder+'/manifest.json','manifest_sha256':digest(folder+'/manifest.json')}
 write(TASK,cfg,json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(records=len(rows),contexts=len(contexts),new_ids=[pei['reaction_id'],zhang['reaction_id']],manifest_sha256=digest(folder+'/manifest.json'))))
