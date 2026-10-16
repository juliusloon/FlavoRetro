"""Bounded root A6 comparison; raw values remain in both fixed packs."""
import json,re
from pathlib import Path
from collections import Counter
from scripts.task016_p7_orchestrate import ROOT,TASK,sha_file,now
from scripts.task016_p7_c_e02_http import immutable_json
B=ROOT/"outputs/task016-p7/v1/C/E02/fresh/C-E02-R7"
O=B/"A6_source_reconciliation_v1"
def js(p): return json.loads(p.read_text())
def jl(p): return [json.loads(s) for s in p.read_text().splitlines()]
def n(v): return re.sub(r"\s+","",str(v)).replace("−","-").casefold() if v is not None else None
def main():
    inputs=[Path(__file__)]
    def load(rel,lines=False):
        p=B/rel;inputs.append(p);return jl(p) if lines else js(p)
    a4=load("A4_raw_extraction_v1/A4_literal_NMR_and_membrane_cells.jsonl",True)
    out4=load("A4_raw_extraction_v1/A4_literal_outcome_table_rows.jsonl",True)
    comparisons=[]
    def add(kind,key,x,y,proj4,proj5):
        comparisons.append(dict(kind=kind,key=list(key),A4=x,A5=y,A4_comparison_projection=proj4,A5_comparison_projection=proj5,equal=proj4==proj5))
    nm5=load("A5_raw_extraction_v1/PMC13273386_TableS1_NMR_raw21rows.json")["rows"]
    d4={(n(x["row"]),x["column"]):x for x in a4 if x["source_id"]=="PMC13273386"}
    assert len(d4)==42 and len(nm5)==21
    for r in nm5:
        for col,k in [("13C ppm","delta_C_literal"),("1H ppm(JHz)","delta_H_J_multiplicity_literal")]:
            x=d4[(n(r["position"]),col)];add("NMR",(r["position"],col),x,r,n(x["raw_literal"]),n(r[k]))
    f5=load("A5_raw_extraction_v1/PMC7904931_SI_fluorescence234cells.json")
    d4={(x["table"].replace("SI_Table",""),n(x["row"]),n(x["lipid_system"]),x["column"]):x for x in a4 if x["source_id"]=="PMC7904931" and x["table"].startswith("SI_")}
    d5={(x["table"],n(x["compound_literal"]),n(x["system"]),{"tau_weighted_ns":"tau_mean_ns"}.get(x["parameter"],x["parameter"])):x for x in f5["cells"]}
    assert len(d4)==len(d5)==234 and set(d4)==set(d5)
    for key,x in d4.items():
        y=d5[key];add("SI_fluorescence",key,x,y,[x["value"],x["error"],n(x.get("significance_literal")) or ""],[float(y["value_literal"]),float(y["SD_literal"]),n(y.get("significance_literal")) or ""])
    tm5=load("A5_raw_extraction_v1/PMC7904931_main_Table1_XML_cells.json")["tables"][0]["rows"]
    headers=[x["literal"] for x in tm5[0]["cells"]]
    d4={(n(x["row"]),n(x["column"])):x for x in a4 if x["source_id"]=="PMC7904931" and x["table"]=="main_Table1"}
    assert len(d4)==21
    for r in tm5[1:]:
        cells=r["cells"]
        for j in range(1,4):
            key=(n(cells[0]["literal"]),n(headers[j]));x=d4[key];y=cells[j]
            add("main_membrane",key,x,y,n(x["raw_literal"]),n(y["literal"]))
    r5=load("A5_raw_extraction_v1/PMC13273386_printed_ratio_labels13.json")["rows"]
    def key4(x):
        f=x["fields"];return (x["table"].replace("_ratio",""),float(f["time_min_raw"] if "time_min_raw" in f else f["time_h_raw"]),f.get("donor1:acceptor2"))
    d4={key4(x):x for x in out4 if x["table"] in ("Fig2d_ratio","Fig2e_ratio")}
    assert len(d4)==len(r5)==13
    for y in r5:
        key=(y["panel"],float(y["time"] if "time" in y else y["time_h"]),y.get("donor1_to_phloretin2_molar_ratio"))
        x=d4[key];add("printed_ratio",key,x,y,x["outcome_value"],y["ratio_3ox2a_over2ox2a"])
    op5=load("A5_raw_extraction_v1/PMC11663222_Fig2_optimization_raw16rows.json")["rows"]
    d4={(x["table"],int(x["row"])):x for x in out4 if x["table"] in ("Fig2A","Fig2B")}
    assert len(d4)==len(op5)==16
    for y in op5:
        key=("Fig"+y["panel"],y["entry"]);x=d4[key]
        add("chemical_optimization_yield",key,x,y,n(x["outcome_raw_literal"]),n(y["yield_literal"]))
    y5=load("A5_raw_extraction_v1/PMC11663222_visible_Fig3to7_yields43.json")["rows"]
    d4={(x["table"].split("_")[0],x["row"]):x for x in out4 if x["table"].startswith(tuple("Fig"+str(i)+"_" for i in range(3,8))) and x["source_id"]=="PMC11663222"}
    assert len(d4)==len(y5)==43
    for y in y5:
        key=(y["figure"],y["product_label"]);x=d4[key];add("chemical_scope_yield_label",key,x,y,x["outcome_value"],y["yield_percent"])
    s5=load("A5_raw_extraction_v1/PMC7904931_Scheme1_multistep_yields9.json")["rows"]
    s4={x["row"]:x for x in out4 if x["table"]=="Scheme1_yields"}
    smap={("a","single"):"a_8to9",("b","both isomers global"):"b_10plus11",("b","isolated10"):"b_10isolated",("c","single"):"c_benzylation",("d","single"):"d_hydrolysis",("e","single"):"e_oxidation",("f","both E/Z global"):"f_14plus15",("f","isolatedE15"):"f_15E",("g","single"):"g_6"}
    assert len(s4)==len(s5)==9
    for y in s5:
        key=(y["step"],y["basis"]);x=s4[smap[key]];add("chemical_scheme_yield_label",key,x,y,x["outcome_value"],float(y["yield_percent_literal"]))
    counts=Counter(x["kind"] for x in comparisons);diff=[x for x in comparisons if not x["equal"]]
    assert len(comparisons)==378
    text=ROOT/f5["raw_pdf"];inputs.append(text)
    header_lines=[dict(line=i+1,literal=s) for i,s in enumerate(text.read_text().splitlines()) if ("τ1 (ns)" in s or "mean ± standard deviation" in s)]
    payload=dict(task=TASK,agent_role="A6 root bounded literal reconciliation",created_at=now(),comparisons=comparisons,counts_by_kind=dict(counts),compared_records=len(comparisons),equal_records=len(comparisons)-len(diff),differences=diff,
       input_file_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in inputs},
       projections=dict(whitespace_and_unicode_minus="comparison only; original literals retained",SI_last_column={"source_header":"<τ> (ns)","A4":"tau_mean_ns","A5":"tau_weighted_ns","source_header_lines":header_lines,"reason":"same sixth source column, explicit alignment; original labels retained, no kinetic interpretation inferred"},scheme_steps=[dict(step=k[0],basis=k[1],A4_row=v) for k,v in smap.items()]),
       denominators=dict(NMR_cells=42,NMR_carbon_reported=21,NMR_proton_reported=11,NMR_proton_blank=10,membrane_main_mean_uncertainty_pair_cells=21,fluorescence_SI_mean_SD_pair_cells=234,SI_mean_and_SD_are_not_independent_measurements=True,printed_ratio_labels=13,main_optimization_yield_labels=16,visible_chemical_scope_yield_labels=43,scheme_yield_labels=9,reaction_count_inferred=False),
       zeros_and_absence=dict(main_Fig2_numeric_zero=sum(y["yield_percent"]==0 for y in op5),SI_optimization_independent_zero=sum(x["outcome_value"]==0 for x in out4 if x["table"] in ("SIp5_temperature","SIp5_time","SIp4_initial")),main_SI_duplicate_rows=[x for x in out4 if x.get("duplicate_of")],non_numeric_upper_bound=[y for y in op5 if y["yield_literal"]=="<50"],NMR_blanks_not_zero=True),
       material_scope_qualification=False,fresh_admitted=0,new_HTTP=0,new_MCTS=0,human_reviewed=False)
    p=O/"378_literal_comparisons_v1.json";immutable_json(p,payload)
    print(json.dumps(dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p),counts=dict(counts),equal=len(comparisons)-len(diff),differences=[dict(kind=x["kind"],key=x["key"],A4=x["A4_comparison_projection"],A5=x["A5_comparison_projection"]) for x in diff]),ensure_ascii=False))
if __name__=="__main__":main()
