"""Frozen positional 7-O methyl-transfer candidates; no enzyme activity claim."""
import json
from pathlib import Path
from rdkit import Chem
from aizynthfinder.chem import SmilesBasedRetroReaction
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from aizynthfinder.utils.exceptions import RejectionException
from .workspace import root, AssetError
from .resources import sha
from .literature_policy import canonical

PATTERN = '[O,o:1]1~[C,c:2](-[c:11]2:[c:12]:[c:13]:[c:14]:[c:15]:[c:16]:2)~[C,c:3]~[C,c:4](=[O:10])~[c:41]2:[c:5]:[c:6]:[c:7](-[O:70]-[CH3:71]):[c:8]:[c:81]:2~1'
QUERY = Chem.MolFromSmarts(PATTERN)


def acceptor(target):
    mol = Chem.MolFromSmiles(target)
    if mol is None or len(Chem.GetMolFrags(mol)) != 1:
        return None
    if any(a.GetAtomicNum() not in (6, 8) or a.GetFormalCharge() or a.GetIsotope() or a.GetNumRadicalElectrons() for a in mol.GetAtoms()):
        return None
    matches = mol.GetSubstructMatches(QUERY)
    if len(matches) != 1:
        return None
    ids = {a.GetAtomMapNum(): matches[0][a.GetIdx()] for a in QUERY.GetAtoms()}
    core = set(matches[0])
    # The three build substrates share free 5-OH and B-ring 4'-OH.
    for position in (5, 14):
        if not any(n.GetAtomicNum() == 8 and n.GetTotalNumHs() == 1 and n.GetDegree() == 1 for n in mol.GetAtomWithIdx(ids[position]).GetNeighbors()):
            return None
    c2, c3 = (mol.GetAtomWithIdx(ids[p]) for p in (2, 3))
    if not c2.GetIsAromatic() and (c2.GetTotalNumHs() != 1 or c3.GetTotalNumHs() != 2):
        return None
    # Reject glycosides, extra rings, carbon chains and bridging substituents.
    for atom in mol.GetAtoms():
        if atom.GetIdx() in core:
            continue
        neighbors = list(atom.GetNeighbors())
        if atom.GetAtomicNum() == 8:
            anchors = [n for n in neighbors if n.GetIdx() in core]
            if len(anchors) != 1 or anchors[0].GetAtomicNum() != 6 or not anchors[0].GetIsAromatic():
                return None
            if atom.IsInRing() or atom.GetDegree() not in (1, 2):
                return None
            if atom.GetDegree() == 2 and not any(n.GetAtomicNum() == 6 and n.GetDegree() == 1 and n.GetTotalNumHs() == 3 for n in neighbors):
                return None
        elif not (atom.GetDegree() == 1 and atom.GetTotalNumHs() == 3 and neighbors[0].GetAtomicNum() == 8 and not atom.IsInRing()):
            return None
    edited = Chem.RWMol(mol)
    edited.RemoveAtom(ids[71])
    product = edited.GetMol()
    Chem.SanitizeMol(product)
    return canonical(Chem.MolToSmiles(product,isomericSmiles=True))


class Registry:
    def __init__(self,binding):
        path=(root()/binding['manifest']).resolve()
        if not path.is_relative_to(root().resolve()) or sha(path)!=binding['manifest_sha256']:
            raise AssetError('methyl scope manifest drift')
        manifest=json.loads(path.read_text())
        if manifest.get('kind')!='positional_methyl_scope_v1' or manifest.get('policy')!={'prior':0.15,'weight':1.0,'generic_protection':3,'max_actions_per_molecule':1}:raise AssetError('methyl method identity drift')
        for rel,digest in manifest['assets'].items():
            asset=(root()/rel).resolve()
            if not asset.is_relative_to(root().resolve()) or sha(asset)!=digest:raise AssetError('methyl source drift: '+rel)
        self.manifest=manifest;self.binding=binding
        self.donor=manifest['donor']
        self.build_targets=set(manifest['build_targets'])

    def precursors(self,target):
        parent=acceptor(target)
        return '.'.join(sorted([parent,self.donor])) if parent else None

    def evidence(self,reaction):
        expected=self.precursors(reaction.mol.smiles)
        actual='.'.join(sorted(canonical(m.smiles) for m in reaction.reactants[reaction.index]))
        if not expected or actual!=expected or reaction.metadata.get('methyl_binding')!=self.binding:
            raise RejectionException('outside frozen positional methyl rule')
        return {'binding':self.binding,'template_id':'task022-7-O-methyl-scope-v1','support_role':'rule_build_examples_not_target_activity_evidence','transfer_status':'build_reconstruction' if canonical(reaction.mol.smiles) in self.build_targets else 'unvalidated_source_scope_candidate','source_support':self.manifest['support_ids'],'source_dois':self.manifest['source_dois'],'build_graph_seen':canonical(reaction.mol.smiles) in self.build_targets,'graph_scope_candidate':True,'enzyme_activity_verified':False,'conditions_prediction_verified':False,'independent_chemical_validation':False,'human_reviewed':False,'evidence_closed':False,'actionable':False}


class MethylExpansion(ExpansionStrategy):
    def __init__(self,key,config,methyl_binding,**kwargs):
        super().__init__(key,config,**kwargs);self.registry=Registry(methyl_binding)
        self.profiling={'lookups':0,'generated_actions':0}
    def get_actions(self,molecules,cache_molecules=None):
        actions=[];priors=[]
        for mol in molecules:
            self.profiling['lookups']+=1
            precursors=self.registry.precursors(mol.smiles)
            if not precursors:continue
            metadata={'policy_name':self.key,'template_id':'task022-7-O-methyl-scope-v1','template_code':'task022-7-O-methyl-scope-v1','methyl_binding':self.registry.binding}
            action=SmilesBasedRetroReaction(mol,reactants_str=precursors,metadata=metadata)
            if not action.reactants:continue
            action.metadata['methyl_scope_evidence']=self.registry.evidence(action)
            actions.append(action);priors.append(0.15);self.profiling['generated_actions']+=1
        return actions,priors


class MethylAwareFilter(QuickKerasFilter):
    def __init__(self,key,config,methyl_binding,**kwargs):
        super().__init__(key,config,**kwargs);self.registry=Registry(methyl_binding)
    def apply(self,reaction):
        if reaction.metadata.get('policy_name')=='methyl_scope':
            reaction.metadata['methyl_scope_evidence']=self.registry.evidence(reaction)
            reaction.metadata['filter_path']='known hazards + positional source-supported graph guard; enzyme unverified'
            return
        super().apply(reaction)
