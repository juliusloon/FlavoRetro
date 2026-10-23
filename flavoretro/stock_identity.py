"""Canonical full-structure stock identity; preserve selected queries and all criteria."""
from rdkit import Chem
from aizynthfinder.chem import Molecule
from aizynthfinder.context.stock import Stock

class CanonicalStock(Stock):
    @classmethod
    def adopt(cls, original):
        instance=cls()
        # Transfer this fresh finder's existing query objects/configuration;
        # their inventory bytes, selection and stopping criteria are unchanged.
        instance.__dict__.update(original.__dict__)
        instance.identity_profile=dict(method="canonical_smiles_full_inchikey_v1",queries=0,internal_key_differences=0)
        return instance

    def _canonical(self,mol):
        # Molecule(smiles) in this pinned upstream version does not assign
        # doublebond geometry. Parse normally before constructing the proxy.
        rd_mol=Chem.MolFromSmiles(mol.smiles)
        if rd_mol is None:raise ValueError("invalid stock-query structure")
        proxy=Molecule(rd_mol=rd_mol,sanitize=True)
        self.identity_profile["queries"]+=1
        self.identity_profile["internal_key_differences"]+=int(proxy.inchi_key!=mol.inchi_key)
        return proxy

    def __contains__(self,mol):
        return super().__contains__(self._canonical(mol))

    def exclude(self,mol):
        return super().exclude(self._canonical(mol))

    def availability_list(self,mol):
        return super().availability_list(self._canonical(mol))

    def amount(self,mol):
        return super().amount(self._canonical(mol))

    def price(self,mol):
        return super().price(self._canonical(mol))

def install(finder):
    if finder.stock is not finder.config.stock:raise ValueError("stock ownership mismatch")
    stock=CanonicalStock.adopt(finder.stock)
    finder.stock=finder.config.stock=stock
    return stock
