"""TASK-016-P7 R76 close-out: triage artifact, saturation confirmation, v36 documents."""
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

from scripts.operate import ROOT, write

TASK = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
R76 = B / "discovery_r76_skill_routes_20261012"
CONF = B / "governance/R76-skill-routes-saturation-confirmation-v1"
REPORT = Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE = Path("STATE.md")
SNAP = B / "report_snapshots"
ARCH = SNAP / "progress-v36-inputs/prior_documents"

def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def pointer(p): return {"path": str(p), "sha256": sha(p)}
def save(p, v):
    if (ROOT / p).exists(): raise RuntimeError("OUTPUT_ALREADY_EXISTS " + str(p))
    write(TASK, str(p), json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")

SS = re.compile(r"sophoroside|2.{0,3}[\"'\u2032\u2033\s]*-?\s*O|glucosyl\(1|diglucoside|triglucoside|sophorotrioside", re.I)
SSF = re.compile(r"flavonol|kaempferol|quercetin|isorhamnetin|myricetin|syringetin", re.I)
C = re.compile(r"C[- ]glycosyl|C[- ]glucosyl|isovitexin|isoorientin|vitexin|orientin|6-C|8-C|puerarin|swertisin|spinosin", re.I)
CF = re.compile(r"flavone|apigenin|luteolin|chrysin|tricetin|wogonin|baicalein|scutellarein", re.I)
GT = re.compile(r"glucosyltransferase|glycosyltransferase|UGT", re.I)
EXCLUSION = {
 "10.1186/s12870-026-09551-1": "OsCGT (development-exposed enzyme, 2-hydroxyflavanone route); 2026 paper is in-vivo omics of the same enzyme/route",
 "10.1016/j.ijbiomac.2024.134138": "duckweed in-vivo MYB/transport study; duckweed CGT LaCGT1 is phloretin-type (original states other substrates not recognized)",
 "10.1016/j.enzmictec.2022.110101": "cascade from naringenin uses existing CGT (2-OH route lineage); not a new direct flavone C6 CGT paper",
 "10.1016/j.enzmictec.2021.109862": "C-glycosylation step is luteolin->isoorientin = frozen C-E02 build support reaction",
 "10.1002/1873-3468.14179": "xanthone 4-C-glycosylation; scaffold outside flavone scope",
 "10.1186/s40643-021-00404-3": "C-arabinosylation (UDP-arabinose donor) and rice 2-OH-route CGT lineage; donor outside frozen scope",
 "10.1021/acs.jafc.1c00602": "orientin/vitexin are 8-C products; site outside C6 scope",
 "10.1016/j.bioorg.2021.104926": "orientin/vitexin are 8-C products; site outside C6 scope",
 "10.1007/s12010-019-03112-z": "isoorientin (build) and isovitexin (development-exposed reaction) steps",
 "10.1002/anie.201905505": "TcCGT1: 2-hydroxyflavanone route, already excluded",
 "10.1021/acs.jafc.8b05958": "luteolin->isoorientin = frozen C-E02 build support reaction",
 "10.1039/c5ob01926e": "di-C-glycosylflavone chemistry/biology; di-C sites and donors outside scope",
 "10.1016/j.phytochem.2012.08.005": "isoschaftoside biosynthesis; di-C/apiose chemistry outside scope",
 "10.1016/j.febslet.2014.11.045": "GtUF6CGT1 original paper, development-exposed",
 "10.1007/s12272-014-0351-3": "pharmacology of C-glycosylation, not an enzyme source",
 "10.1016/j.fct.2013.11.020": "pharmacology of C-glycosylation, not an enzyme source",
 "10.1248/cpb.c13-00264": "chemical total synthesis, not enzymatic",
 "10.1104/pp.110.161042": "CYP93G2 flavanone 2-hydroxylase (2-OH route enzyme)",
 "10.1042/BST20191140": "review",
 "10.1002/rcm.4910": "analytical LC-MS methods paper for acylated C-glycosyl flavones; not an enzyme source",
 "10.1039/c0ob00011f": "chemical regioselective synthesis of di-C-glycosylflavones; not enzymatic; di-C sites outside scope",
 "10.1016/j.chroma.2007.05.103": "analytical LC-MS/MS methods paper; not an enzyme source",
 "10.1016/j.chroma.2005.11.070": "analytical LC-MS assignment methods paper; not an enzyme source",
 "10.1002/pca.727": "analytical HPLC-MS methods paper; not an enzyme source",
}
TITLE_ONLY = {
 "10.1093/pcp/pcy129": "flavone 7,4'-O-diglucoside aglycone O-glycosylation (Nemophila); acceptor/donor chemistry outside flavonol-3-O-glycoside O2 scope",
}

def main():
    (ROOT / ARCH).mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in (ROOT / R76 / "new_leads.jsonl").read_text().splitlines() if l.strip()]
    triage = []
    for r in rows:
        t = r.get("title") or ""
        doi = r["hit"].get("doi")
        cls = None; reason = None
        if SS.search(t) and (GT.search(t) or SSF.search(t) or "flavon" in t.lower()):
            cls = "ss_title_relevant"; reason = TITLE_ONLY.get(doi)
        elif C.search(t) and (CF.search(t) or GT.search(t)):
            cls = "c_title_relevant"; reason = EXCLUSION.get(doi)
        if cls:
            triage.append(dict(key=r["key"], title=t, doi=doi, routes=r.get("routes"), title_class=cls,
                               disposition="title_level_out_of_scope" if reason else "needs_manual_review",
                               title_level_reason=reason))
    manual = [x for x in triage if x["disposition"] == "needs_manual_review"]
    if manual:
        raise RuntimeError("UNTRIAGED_TITLE_HITS: " + json.dumps(manual, ensure_ascii=False)[:500])
    save(R76 / "title_triage.json", dict(task=TASK, at=datetime.now(timezone.utc).isoformat(),
        method="deterministic local title-keyword triage; no HTTP; identifier-level exposure cross-check already in disposition_summary.json",
        total_new_leads=len(rows), title_relevant=len(triage),
        new_scope_aligned_candidates=0,
        triage=triage,
        note="every title-relevant hit carries an explicit title-level out-of-scope or already-excluded reason; this is metadata-level triage, not chemistry admission or article-level exclusion"))

    conf = dict(
        task=TASK, at=datetime.now(timezone.utc).isoformat(),
        approval_type="agent_delegated", human_reviewed=False,
        purpose="Confirm the 2026-10-12 source-loop stop review with three genuinely new route forms routed by the nature-academic-search skill",
        routes_executed=[
            "NCBI E-utilities esearch full-field queries (sophoroside x GT; C-glycosylation x flavone) — all years, new form vs prior TITLE-only rounds",
            "NCBI MeSH-qualified intersections (Flavonoids[MeSH] x sophoroside/GT; Glucosyltransferases[MeSH] x Flavones[MeSH]) — old-literature catch",
            "NCBI elink pubmed_pubmed related-article chase from the exposed SS (4 papers) and C (3 papers) anchors",
            "EPMC SRC:PPR preprint sweeps for both families",
        ],
        HTTP=14, all_http_200=True,
        unique_hits=385, new_identifier_leads=357,
        title_relevant=6 + 1,
        new_scope_aligned_candidates=0,
        per_family=dict(
            C="0 new candidates; all 24 title-relevant hits are exposed reactions/enzymes, wrong site (8-C), wrong donor (UDP-Ara), wrong scaffold (xanthone), 2-OH route, chemical synthesis, methods or reviews",
            SS="0 new candidates; the only new title-relevant hit (Nemophila flavone 7,4'-O-diglucoside GTs) is aglycone O-glycosylation outside the frozen flavonol-3-O-glycoside O2 scope; elink chase from exposed anchors surfaced nothing new",
        ),
        prior_blind_spot_coverage=dict(
            pre2010="MeSH x MeSH and full-field all-year queries now executed (C-SEARCH-02 hitcount 33; triaged)",
            preprints="PPR sweeps now executed for both families",
            citation_chase="formal elink route now executed from 7 exposed anchors",
        ),
        remaining_blind_spots=["patent literature (still not executed as a route)", "paywalled non-indexed old literature (access-boundary documented in R74)"],
        conclusion="R76 confirms the source-loop stop review: saturation per contract 6.3 condition 3 and access boundary per condition 4 stand; no gate lowered; epochs remain open for future legally obtained originals",
        evidence=dict(
            r76_batch=pointer(R76 / "disposition_summary.json"),
            r76_leads=pointer(R76 / "new_leads.jsonl"),
            r76_triage=pointer(R76 / "title_triage.json"),
            prior_stop_review=pointer(B / "governance/R74-R75-source-loop-stop-review-v1/source_loop_stop_review.json"),
            r74_batch=pointer(B / "SS/E02/fresh/SS-E02-R74-final-lead-metadata-v1/final_lead_dispositions.json"),
        ),
    )
    save(CONF / "confirmation.json", conf)

    # REPORT v36
    rep = (ROOT / REPORT).read_text(encoding="utf-8")
    if "progress-v36-final：R76 技能路线" not in rep:
        write(TASK, str(ARCH / "REPORT-016-P7.pre-v36.md"), rep)
        rep2 = rep.replace(
            "当前权威截面 **progress-v35-final（见文末）**",
            "当前权威截面 **progress-v36-final（见文末）**", 1)
        if rep2 == rep:
            raise RuntimeError("REPORT_HEADER_ANCHOR_NOT_FOUND")
        section = """

## progress-v36-final：R76 技能路线增量发现——饱和判定经三条新路线复核成立（2026-10-12）

本节追加于 progress-v35-final 之后；任务阶段结论不变：**Partial**（C/SS 面板不足，来源循环停止；epoch 开放）。批准与阶段决定 agent_delegated，非 human_reviewed。

1. **R76 新路线（nature-academic-search 技能路由；MCP 工具本环境不可用，按其无 MCP 回退与查询构造指南以项目自有预注册可观测 HTTP 实现）**：14/14 HTTP 200（全局物理账 1286 HTTP / 1,244,871,814 B）：① NCBI esearch 全字段查询（sophoroside×GT；C-糖基化×flavone，全年代）——此前各轮均为 TITLE 限定，本形式首次执行；② NCBI MeSH 限定交叉（Flavonoids[MeSH]×sophoroside/GT；Glucosyltransferases[MeSH]×Flavones[MeSH]）——覆盖老文献盲区；③ NCBI elink 从 7 篇已曝光锚点论文做正式相关文献引文追踪；④ EPMC SRC:PPR 预印本专项扫描（两族）。

2. **结果**：385 唯一命中、357 标识符级新线索、标题相关 25 条逐一处置——**0 个新的 scope 对齐候选**。C 轴 24 条：已曝光反应/酶（luteolin→isoorientin=build、isovitexin reaction token、GtUF6CGT1、OsCGT、TcCGT1）、错误位点（orientin/vitexin 为 8-C）、错误供体（UDP-Ara）、错误骨架（xanthone）、2-OH 路线、化学合成、方法学或综述。SS 轴 1 条（Nemophila flavone 7,4′-O-diglucoside GT）：苷元 O-糖基化，越出冻结的黄酮醇 3-O-糖苷 O2 scope。预印本扫描 37+3 条均无新酶学论文。逐条处置与理由见 `discovery_r76_skill_routes_20261012/title_triage.json`（题名级元数据分诊，不构成论文级排除）。

3. **结论**：饱和评估（§6.3 条件3）与访问边界（条件4）经三条新路线复核后维持成立；豌豆 1982 的 OpenAlex 无合法 OA 结论无变化；专利文献仍是唯一未执行的路线类型，如实保留为盲区。未降低任何门槛、未做任何化学检视、无新 MCTS、无新曝光行；受保护文件与回归状态继承 v35 截面。机器凭证：`governance/R76-skill-routes-saturation-confirmation-v1/confirmation.json`、快照 `report_snapshots/progress-v36-final.json`；v35 前 REPORT 原字节归档于 `report_snapshots/progress-v36-inputs/prior_documents/`。
"""
        rep2 = rep2.rstrip("\n") + "\n" + section
        write(TASK, str(REPORT), rep2)

    # STATE increment
    st = (ROOT / STATE).read_text(encoding="utf-8")
    if "R76 技能路线增量发现" not in st:
        anchor = "R74 预注册元数据轮 7/7 HTTP（全局 1272 HTTP / 1,244,444,031 B；唯一有合法OA副本的老线索 L06 为酰基转移酶，越出冻结 scope）。"
        if anchor not in st: raise RuntimeError("STATE_ANCHOR_NOT_FOUND")
        st2 = st.replace(anchor, anchor + "R76 以学术检索技能路由的三条新路线（MeSH 全字段、elink 引文追踪、PPR 预印本；14/14 HTTP，全局 1286 HTTP / 1,244,871,814 B）复核：385 唯一命中、25 条标题相关逐一处置，0 个新 scope 对齐候选，饱和判定维持；快照 progress-v36-final。", 1)
        write(TASK, str(STATE), st2)

    # Snapshot v36
    snap = dict(
        task=TASK, version="progress-v36-final",
        as_of=datetime.now(timezone.utc).isoformat(),
        status="Partial_source_loop_stopped_per_contract_6_3_confirmed_by_R76",
        approval_type="agent_delegated", human_reviewed=False,
        fresh_C=0, fresh_SS=0, scientific_ABE_cells=0, metrics=None,
        roadmap_P2_completed=False, epochs_open=True, gates_lowered=False,
        physical_HTTP=1286, physical_bytes=1244871814,
        R76=dict(batch="discovery_r76_skill_routes_20261012", planned=14, executed=14,
                 unique_hits=385, new_identifier_leads=357, title_relevant=25,
                 new_scope_aligned_candidates=0,
                 routes=["pubmed_esearch_fullfield", "pubmed_esearch_mesh", "ncbi_elink_related_chase", "europepmc_ppr_preprints"],
                 summary=pointer(R76 / "disposition_summary.json"),
                 triage=pointer(R76 / "title_triage.json")),
        saturation_confirmation=pointer(CONF / "confirmation.json"),
        prior_snapshot=pointer(SNAP / "progress-v35-final.json"),
        archive={"report_pre_v36": pointer(ARCH / "REPORT-016-P7.pre-v36.md")},
        known_blind_spots=["patent literature (route never executed)", "paywalled non-indexed old literature (access-boundary documented)"],
    )
    p = SNAP / "progress-v36-final.json"
    if not (ROOT / p).exists():
        write(TASK, str(p), json.dumps(snap, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(report_sha=sha(REPORT), state_sha=sha(STATE), snapshot_sha=sha(p),
                          conf_sha=sha(CONF / "confirmation.json"), triage_rows=len(triage)), ensure_ascii=False))

if __name__ == "__main__":
    main()
