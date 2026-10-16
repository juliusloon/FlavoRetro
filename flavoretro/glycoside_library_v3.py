"""Opt-in v3 source-supported C/hexoside/rhamnoside scopes; activity stays unknown."""
from rdkit import Chem
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from . import glycoside_library as v2
from .workspace import root,config,AssetError
from .reviewed_resources import canonical_side
from .open_glycoside_library import structural_formation

def scope_center_allowed(t,target,products):
    acceptor,donor=products;scope=t['scope']
    if canonical_side([Chem.MolToSmiles(donor,isomericSmiles=True)])!=t['donor']:return False
    try:f=structural_formation(Chem.MolToSmiles(acceptor,isomericSmiles=True),t['donor'],Chem.MolToSmiles(target,isomericSmiles=True))
    except ValueError:return False
    if f['family']!=t['category']:return False
    # Local sugar chirality/connection is explicit in SMARTS. Full parent glycan guards
    # retain declared Glc/Gal/Rha stereo even where the C4 epimer query is relaxed.
    if not any(acceptor.HasSubstructMatch(Chem.MolFromSmarts(p),useChirality=True) for p in scope['parent_glycan_patterns']):return False
    if not any(acceptor.HasSubstructMatch(Chem.MolFromSmarts(p)) for p in scope['acceptor_cores']):return False
    if scope['center_class']=='phloretin_mono_C_second':
        from .topology import audit
        sites=[s for s in audit(Chem.MolToSmiles(acceptor,isomericSmiles=True))['sites'] if s['family']=='aryl_C_candidate']
        if len(sites)!=1:return False
        # Require only source-supported neutral phloroglucinol/dihydrochalcone context,
        # with finite remote phenol/methoxy decorations, no arbitrary side chains.
        core=Chem.MolFromSmarts(scope['acceptor_cores'][0]);matches=acceptor.GetSubstructMatches(core)
        parent_matches=[m for p in scope['parent_glycan_patterns'] for m in acceptor.GetSubstructMatches(Chem.MolFromSmarts(p),useChirality=True)]
        for match in matches:
            allowed=set(match)|set().union(*(set(m) for m in parent_matches))
            for a in acceptor.GetAtoms():
                if a.GetIdx() in allowed or a.GetAtomicNum()!=8 or a.GetFormalCharge()!=0:continue
                nn=list(a.GetNeighbors());aryl=[n for n in nn if n.GetIdx() in match and n.GetIsAromatic()]
                if len(aryl)!=1 or any(b.GetBondType()!=Chem.BondType.SINGLE for b in a.GetBonds()):continue
                if len(nn)==1 and a.GetTotalNumHs()==1:allowed.add(a.GetIdx())
                elif len(nn)==2:
                    other=next(n for n in nn if n.GetIdx()!=aryl[0].GetIdx())
                    if other.GetAtomicNum()==6 and other.GetDegree()==1 and other.GetTotalNumHs()==3:allowed.update([a.GetIdx(),other.GetIdx()])
            if len(allowed)==acceptor.GetNumAtoms():return True
        return False
    return True

class Registry(v2.Registry):
    def evidence(self,reaction):
        e=super().evidence(reaction)
        e['namespace']='task016_p2'
        e['inherited_template']=not e['template_id'].startswith('p2-scope:')
        return e

def load_registry(expected=None):
    s=config('glycoside-library-v3.json');r=Registry(root()/s['manifest'],s['manifest_sha256'])
    if r.binding['version']!='task016-p2-qualified-v3':raise AssetError('v3 strategy version drift')
    if expected is not None and r.binding!=expected:raise AssetError('v3 binding changed during run')
    return r
class GlycosideExpansion(v2.GlycosideExpansion):
    def __init__(self,key,config,domain_binding=None,**kwargs):
        ExpansionStrategy.__init__(self,key,config,**kwargs);self.registry=load_registry(domain_binding);self.profiling=dict(template_attempts=0,generation_seconds=0.,generated_actions=0)
class DomainAwareQuickFilter(v2.DomainAwareQuickFilter):
    def __init__(self,key,config,domain_binding=None,**kwargs):
        QuickKerasFilter.__init__(self,key,config,**kwargs);self.registry=load_registry(domain_binding)
    def apply(self,reaction):
        if reaction.metadata.get('policy_name')=='glycoside':
            e=self.registry.evidence(reaction);reaction.metadata['task016_evidence']=e;reaction.metadata['filter_path']='known_hazards + validated v3 scope guard; activity unverified';reaction.metadata.setdefault('review',{})['task016_p2']=e;return
        QuickKerasFilter.apply(self,reaction)
