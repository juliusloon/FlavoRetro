"""Validate actual mapped actions and the v3 scope source evidence without MCTS."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from aizynthfinder.chem import TreeMolecule
from flavoretro.glycoside_library import LibraryRetroReaction
from flavoretro.glycoside_library_v3 import load_registry
from flavoretro.reviewed_resources import canonical_side
from scripts.operate import write,event
OUT=Path('outputs/task016-p2/v2')
r=load_registry();checks=[]
for t in r.templates:
    for iid in t['support_instances']:
        source=r.instances[iid];parent=TreeMolecule(parent=None,smiles=source['target']);reaction=LibraryRetroReaction(parent,smarts=t['smarts'],use_rdchiral=False,metadata=dict(policy_name='glycoside',template_id=t['template_id'],library_template=t,domain_binding=r.binding,required_context=t['required_context']))
        expected=canonical_side(source['reference_precursors']);actual=[canonical_side([m.smiles for m in outcome]) for outcome in reaction.reactants]
        check=dict(template_id=t['template_id'],instance_id=iid,passed=expected in actual,outcome_count=len(actual),actual_mcts_runs=0)
        for index in range(len(reaction.reactants)):r.evidence(reaction.copy(index=index))
        checks.append(check)
result=dict(passed=all(c['passed'] for c in checks),checks=checks,template_count=len(r.templates),source_replays=len(checks),actual_mcts_runs=0,claim='mapped reaction actions and structural source replay, not independent chemistry')
write('TASK-016-P2',str(OUT/'build_action_validation.json'),json.dumps(result,ensure_ascii=False,indent=2)+'\n')
assert result['passed'],[c for c in checks if not c['passed']]
event('TASK-016-P2','G3_actual_actions_passed',source_replays=len(checks),actual_mcts_runs=0)
print('Mapped support replays',len(checks),'passed')
