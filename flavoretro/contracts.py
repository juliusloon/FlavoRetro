import json
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from rdkit import Chem
from .workspace import config


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    smiles: str = Field(min_length=1, max_length=3000)
    mode: Literal["quick", "balanced", "strict"] = "balanced"
    engine: Literal["optimized", "native"] = "optimized"
    seed: int = Field(default=0, ge=0, le=2**32 - 1)
    candidate_stock: bool = False
    top_k: int = Field(default=5, ge=1, le=25)
    seconds: float | None = Field(default=None, ge=0.1, le=360, allow_inf_nan=False)
    iterations: int | None = Field(default=None, ge=1, le=1800)
    depth: int | None = Field(default=None, ge=1, le=10)
    branching: int | None = Field(default=None, ge=1, le=24)
    nodes: int | None = Field(default=None, ge=1, le=25000)

    @field_validator("smiles")
    @classmethod
    def valid_smiles(cls, value):
        mol = Chem.MolFromSmiles(value)
        if (
            mol is None
            or not mol.GetNumAtoms()
            or mol.GetNumAtoms() > 250
            or any(a.GetAtomicNum() == 0 for a in mol.GetAtoms())
        ):
            raise ValueError(
                "Invalid or unsupported molecule; max 250 atoms, no wildcard"
            )
        return Chem.MolToSmiles(mol, isomericSmiles=True)

    def phases(self):
        settings = config("search.json")
        phases = settings["profiles"][self.mode]
        for phase in phases:
            for field in ("seconds", "iterations", "depth", "branching", "nodes"):
                value = getattr(self, field)
                if value is not None:
                    phase[field] = value
        return phases
