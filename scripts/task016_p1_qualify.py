"""Version source qualification without repartitioning or fitting development targets."""
import copy,json,xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from aizynthfinder.chem import TreeMolecule
from scripts.task016_p1_sources import ROOT,OUT as ORIGINAL,rows,TASK
from scripts.operate import write,event
from flavoretro.resources import sha
from flavoretro.glycoside_library import apply_template,LibraryRetroReaction
from flavoretro.reviewed_resources import canonical_side

QUALIFIED=ROOT/'outputs/task016-p1/v2'
def save_at(directory,name,data,jsonl=False):
    text=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in data) if jsonl else json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    write(TASK,str((directory/name).relative_to(ROOT)),text)

def qualify(directory=QUALIFIED,activate=True):
    assert not (directory/'qualification_manifest.json').exists(),'qualified source payload already frozen'
    source=rows(ORIGINAL/'instances.jsonl')
    excluded=[r for r in source if r['provenance'].get('pmcid')=='PMC9149423' and r['sugar_type']=='galactose']
    assert len(excluded)==12 and len({r['covalent_signature'] for r in excluded})==6
    excluded_ids={r['instance_id'] for r in excluded};instances=[r for r in source if r['instance_id'] not in excluded_ids]
    build=[r for r in instances if r['template_role']=='development_build'];hold=[r for r in instances if r['template_role']=='development_holdout']
    for name,data in [('instances.jsonl',instances),('build_views.jsonl',build),('runtime_instances.jsonl',build),('holdout_views.jsonl',hold)]:save_at(directory,name,data,True)
    assert sha(directory/'holdout_views.jsonl')==sha(ORIGINAL/'holdout_views.jsonl'),'holdout bytes changed'
    unresolved=[dict(original_instance=r,disposition='retained_unresolved_product_identity',reason='Acquired source supports UDP-Gal glycosylation activity, but does not individually establish the full 3-O-beta-D product identity for all six acceptors. Paragraph40 explicitly assigns only pelargonidin3-OH; database names/3GT naming cannot fill other product/site/stereo evidence.',critical_uncertainty=['full product identity','individual regioassignment','individual stereochemical identification'],executable=False,human_reviewed=False) for r in excluded]
    save_at(directory,'unresolved_instances.jsonl',unresolved,True)
    disp=[dict(r,disposition='retained_unresolved_product_identity' if r['instance_id'] in excluded_ids else r['disposition']) for r in rows(ORIGINAL/'assay_record_dispositions.jsonl')]
    save_at(directory,'assay_record_dispositions.jsonl',disp,True)
    write(TASK,str((directory/'assay_annotations.json').relative_to(ROOT)),(ORIGINAL/'assay_annotations.json').read_text())
    save_at(directory,'reference_precursors.jsonl',[r for r in rows(ORIGINAL/'reference_precursors.jsonl') if r['instance_id'] not in excluded_ids],True)
    save_at(directory,'dedup_links.jsonl',[r for r in rows(ORIGINAL/'dedup_links.jsonl') if r['left'] not in excluded_ids and r['right'] not in excluded_ids],True)
    groups=[r for r in rows(ORIGINAL/'reaction_groups.jsonl') if not set(r['instance_ids'])<=excluded_ids];assert all(not set(r['instance_ids'])&excluded_ids for r in groups)
    save_at(directory,'reaction_groups.jsonl',groups,True)
    original_split=json.loads((ORIGINAL/'development_split_manifest.json').read_text());source_groups=[]
    for g in original_split['groups']:
        rr=[r for r in instances if r['source_group']==g['source_group']]
        if rr:source_groups.append(dict(g,instances=sorted(r['instance_id'] for r in rr),reactions=len({r['covalent_signature'] for r in rr}),targets=len({r['target'] for r in rr})))
    counts=dict(assay_annotations_universe=93,admitted_new_contexts=81,retained_unresolved_contexts=12,specific_instances=len(instances),inherited_instances=4,unique_covalent_groups=len(groups),new_covalent_groups=sum(not g['inherited'] for g in groups),new_acceptors=len({r['acceptor'] for r in instances if not r.get('inherited')}),new_sugars=sorted({r['sugar_type'] for r in instances if not r.get('inherited')}),new_publications=len({r['provenance']['pmcid'] for r in instances if not r.get('inherited')}),new_closed_source_groups=len({r['source_group'] for r in instances if not r.get('inherited')}),closure_groups=len(source_groups),build_contexts=len(build),build_reactions=len({r['covalent_signature'] for r in build}),holdout_reactions=len({r['covalent_signature'] for r in hold}),holdout_targets=len({r['target'] for r in hold}),new_categories=dict(Counter(g['category'] for g in groups if not g['inherited'])))
    save_at(directory,'counting_contract.json',dict(schema_version=2,counts=counts,definition='qualified primary-source formation; same covalent/stereo/acid-O dedup rule and source-closed roles; unresolved identity excluded from executable/new counts, retained in original93 annotation universe',physical_replicates=None,review_type='agent_delegated',human_reviewed=False))
    split=dict(original_split,version='task016-p1-source-qualified-v2',groups=source_groups,counts=counts,qualification_revision=dict(original_split_sha256=sha(ORIGINAL/'development_split_manifest.json'),partition_reselected=False,original_roles_preserved=True,removal_reason='primary-source identity evidence only, not model outcome',excluded_instance_ids=sorted(excluded_ids)),files_sha256={n:sha(directory/n) for n in original_split['files_sha256']})
    save_at(directory,'development_split_manifest.json',split)
    save_at(directory,'evaluation_reference_manifest.json',dict(schema_version=2,scope='offline evaluator only; holdout bytes/roles inherited unchanged; never loaded by runtime registry',files_sha256={n:sha(directory/n) for n in ['reference_precursors.jsonl','holdout_views.jsonl','development_split_manifest.json']},human_reviewed=False))
    templates=copy.deepcopy(rows(ORIGINAL/'templates.jsonl'));templates=[t for t in templates if not set(t['support_instances'])<=excluded_ids]
    assert all(not set(t['support_instances'])&excluded_ids for t in templates)
    assert len(templates)==51
    validations=[];lookup={r['instance_id']:r for r in build}
    old_validation={v['template_id']:v for v in rows(ORIGINAL/'template_validation.r3.jsonl')}
    action_checks=[]
    for t in templates:
        v=copy.deepcopy(old_validation[t['template_id']])
        for check in v['checks']:
            kind=check['kind'];support=lookup[t['support_instances'][0]]
            if kind=='support_replay':
                r=lookup[check['instance_id']];out=apply_template(t,r['target']);check['passed']=canonical_side(r['reference_precursors']) in [o['precursors'] for o in out];check['outcome_indices']=[o['outcome_index'] for o in out]
            elif kind=='wrong_context_or_donor':check['passed']=not apply_template(t,support['target'],check['context'])
            elif kind in ['wrong_anomeric_stereo','outside_flavonoid_core','outside_declared_OH_OMe_decorations']:check['passed']=not apply_template(t,check['target'])
            elif kind=='acid_representation_equivalence':check['passed']=canonical_side(support['reference_precursors']) in [o['precursors'] for o in apply_template(t,check['ionic_target'])]
            else:raise ValueError('unrecognized boundary '+kind)
        v['passed']=all(c['passed'] for c in v['checks']);assert v['passed'],v['template_id'];validations.append(v)
    for r in build:
        checks=[]
        for t in templates:
            if r['instance_id'] not in t['support_instances']:continue
            a=LibraryRetroReaction(TreeMolecule(parent=None,smiles=r['target']),smarts=t['smarts'],use_rdchiral=False,metadata={'library_template':t})
            matched=canonical_side(r['reference_precursors']) in [canonical_side([m.smiles for m in outcome]) for outcome in a.reactants];checks.append(dict(template_id=t['template_id'],passed=matched));assert matched,(r['instance_id'],t['template_id'])
        action_checks.append(dict(instance_id=r['instance_id'],passed=bool(checks) and all(c['passed'] for c in checks),checks=checks))
    save_at(directory,'templates.jsonl',templates,True);save_at(directory,'template_validation.jsonl',validations,True);save_at(directory,'build_action_validation.json',dict(passed=all(c['passed'] for c in action_checks),checks=action_checks,actual_mcts_runs=0))
    for name in ['applicability_contract.json','representation_rules.json','fusion_contract.json','review_binding.json']:
        d=json.loads((ORIGINAL/name).read_text())
        if name=='applicability_contract.json':d['split_sha256']=sha(directory/'development_split_manifest.json')
        save_at(directory,name,d)
    save_at(directory,'template_groups.jsonl',[dict(r,templates=[i for i in r['templates'] if i in {t['template_id'] for t in templates}]) for r in rows(ORIGINAL/'template_groups.jsonl')],True)
    prior=json.loads((ORIGINAL/'template_source_manifest.r3.json').read_text())
    manifest=dict(prior,version='task016-p1-open-v2-source-qualified-r4',files_sha256={n:sha(directory/n) for n in ['templates.jsonl','runtime_instances.jsonl','template_validation.jsonl','applicability_contract.json','representation_rules.json','fusion_contract.json']},dependency_revision=dict(previous_manifest_sha256=sha(ORIGINAL/'template_source_manifest.r3.json'),reason='remove insufficiently identified UDP-Gal anthocyanidin products only; scope SMARTS/supports, guards, representation, fusion unchanged'))
    save_at(directory,'template_source_manifest.json',manifest)
    qualification=dict(schema_version=1,approval_type='agent_delegated',original_instances_sha256=sha(ORIGINAL/'instances.jsonl'),original_split_sha256=sha(ORIGINAL/'development_split_manifest.json'),excluded_instance_ids=sorted(excluded_ids),excluded_unique_reactions=6,record_universe=93,dispositions=dict(Counter(r['disposition'] for r in disp)),role_changes=0,holdout_bytes_unchanged=True,scope_templates_unchanged=True,counts=counts,files_sha256={n:sha(directory/n) for n in ['instances.jsonl','unresolved_instances.jsonl','assay_record_dispositions.jsonl','reaction_groups.jsonl','development_split_manifest.json','templates.jsonl','template_validation.jsonl','template_source_manifest.json']},human_reviewed=False)
    save_at(directory,'qualification_manifest.json',qualification)
    if activate:
        config=dict(version=2,default_enabled=False,manifest='outputs/task016-p1/v2/template_source_manifest.json',manifest_sha256=sha(directory/'template_source_manifest.json'),status='development_candidate_scope_not_production')
        for path in ['configs/glycoside-library-v2.json','flavoretro/assets/configs/glycoside-library-v2.json']:write(TASK,path,json.dumps(config,indent=2)+'\n')
    event(TASK,'source_qualified_payload',path=str(directory.relative_to(ROOT)),counts=counts,templates=len(templates),activate=activate)
    print(json.dumps(counts,sort_keys=True));print('templates',len(templates),'support replay',sum(c['kind']=='support_replay' for v in validations for c in v['checks']),'actual action replay contexts',len(action_checks))
if __name__=='__main__':qualify()
