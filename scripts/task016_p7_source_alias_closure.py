"""Additive explicit PMID source alias checks; legacy frozen closure semantics retained."""
import re
from scripts.task016_p7_orchestrate import ContractError,require_fields
from scripts.task016_p7_closure_harness import closure_tokens as legacy_closure_tokens
from scripts.task016_p7_closure_harness import assert_fresh as legacy_assert_fresh
from scripts.task016_p7_closure_harness import assert_zero_leakage as legacy_assert_zero_leakage

def explicit_pmid_tokens(record):
    tokens=set()
    def add(value):
        if value is None:return
        if isinstance(value,bool) or not isinstance(value,(str,int)):raise ContractError("explicit PMID type invalid")
        value=str(value).strip()
        match=re.fullmatch(r"(?:(?:PMID|MED):\s*)?([1-9][0-9]*)",value,re.I)
        if not match:raise ContractError("explicit PMID identifier malformed")
        tokens.add("pmid:"+match.group(1))
    def walk(value):
        if isinstance(value,dict):
            for key,child in value.items():
                if key in {"pmid","source_pmid"}:add(child)
                elif key in {"source_tokens","closure_tokens"} and isinstance(child,list):
                    for t in child:
                        if isinstance(t,str) and t.lower().startswith("pmid:"):add(t)
                else:walk(child)
            if value.get("source")=="MED" and value.get("source_id") is not None:add(value["source_id"])
        elif isinstance(value,list):
            for child in value:walk(child)
    walk(record);return tokens

def closure_tokens(record):
    return legacy_closure_tokens(record)|explicit_pmid_tokens(record)

def assert_fresh(record,exposures):
    exposures=list(exposures)
    legacy_assert_fresh(record,exposures)
    tokens=closure_tokens(record)
    for row in exposures:
        require_fields(row,("development_exposed","exposure_type","closure_tokens"))
        if row["development_exposed"]:
            overlap=tokens.intersection(closure_tokens(row))
            if overlap:raise ContractError("historical/design source alias intersects holdout: "+str(sorted(overlap)))
    return True

def assert_zero_leakage(build,holdout,exposures=(),runtime_instances=()):
    build=list(build);holdout=list(holdout);exposures=list(exposures);runtime_instances=list(runtime_instances)
    result=legacy_assert_zero_leakage(build,holdout,exposures,runtime_instances)
    build_tokens=set().union(*(closure_tokens(r) for r in build)) if build else set()
    for row in holdout:
        overlap=build_tokens.intersection(closure_tokens(row))
        if overlap:raise ContractError("build/holdout source alias leakage: "+str(sorted(overlap)))
        assert_fresh(row,exposures)
    return result
