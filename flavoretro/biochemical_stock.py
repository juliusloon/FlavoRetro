"""A declared biochemical candidate inventory, independent of source targets.

Salt fragments and protonation are standardized for structural candidate matching.
Stereochemistry is retained. A match is not current stock, purity, or supply proof.
"""
import json
from pathlib import Path
from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize
from aizynthfinder.context.stock.queries import StockQueryMixin
from .resources import sha
from .workspace import root, AssetError


def key(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None:raise ValueError('invalid biochemical stock structure')
    mol=rdMolStandardize.FragmentParent(mol)
    mol=rdMolStandardize.Uncharger().uncharge(mol)
    for atom in mol.GetAtoms():atom.SetAtomMapNum(0)
    return Chem.MolToInchiKey(mol)


class BiochemicalStock(StockQueryMixin):
    def __init__(self,biochemical_binding,**kwargs):
        path=(root()/biochemical_binding['manifest']).resolve()
        if not path.is_relative_to(root().resolve()) or not path.is_file() or sha(path)!=biochemical_binding['manifest_sha256']:
            raise AssetError('biochemical stock binding drift')
        manifest=json.loads(path.read_text())
        if manifest['kind']!='fixed_biochemical_candidates_v1' or manifest['normalization']!='RDKit FragmentParent then Uncharger, full stereo InChIKey' or manifest['current_supplier_verified'] is not False:
            raise AssetError('biochemical stock role drift')
        for rel,digest in manifest['assets'].items():
            asset=(root()/rel).resolve()
            if not asset.is_relative_to(root().resolve()) or not asset.is_file() or sha(asset)!=digest:
                raise AssetError('biochemical stock source drift: '+rel)
        records=json.loads((root()/manifest['records']).read_text())
        self.keys={key(r['smiles']) for r in records if r['candidate_admitted']}
        if len(self.keys)!=manifest['keys']:raise AssetError('biochemical key count drift')
        self.binding=biochemical_binding
    def __contains__(self,mol):return key(mol.smiles) in self.keys
    def __len__(self):return len(self.keys)
