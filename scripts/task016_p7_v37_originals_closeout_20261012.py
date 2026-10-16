"""v37 close-out: unified originals-request list, evidence archives, documents, snapshot."""
import hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path

from scripts.operate import ROOT, write

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "governance/R79-originals-request-v1"
EV = B / "discovery_evidence/session2_20261012"
REPORT = Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE = Path("STATE.md")
SNAP = B / "report_snapshots"
ARCH = SNAP / "progress-v37-inputs/prior_documents"
R79M = B / "discovery_r79_access_verification_20261012"

def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def pointer(p): return {"path": str(p), "sha256": sha(p)}

ENTRIES = [
 dict(priority="P1", family="SS", cite="Jourdan PS, Mansell RL (1982) Arch Biochem Biophys 213(2):434-443",
      doi="10.1016/0003-9861(82)90569-0", pmid="6462109", publisher="Elsevier", access="closed (R74 OpenAlex: is_oa=false)",
      why="SS 轴唯一机械 fresh 候选（豌豆三糖基转移酶分离表征，1979 豌豆文的延续；R11 元数据级提示、从未化学检视）；quercetin 3-O-糖苷 O2 延伸若在正文/表格中有结构级证据即为新 fresh 目标",
      caution="与已曝光 1979 豌豆文（manual #14）同一 Mansell 豌豆酶学体系：未来处理前须独立 A6 先裁决同实验队列闭包风险"),
 dict(priority="P1", family="SS", cite="Morita Y et al. (2005) Plant J 42(3):353-363",
      doi="10.1111/j.1365-313x.2005.02383.x", pmid="15842621", publisher="Wiley", access="bronze (OpenAlex is_oa=true) 但此前人机验证拦截——请代取 PDF",
      why="牵牛花 UDP-glucose:anthocyanidin 3-O-glucoside 2''-O-glucosyltransferase (IpA3G2″GlcT, AB192315)；其体外底物面板是否含黄酮醇 3-O-糖苷 O2 延伸=unknown（SS 子代理被 Wiley 反爬阻挡）"),
 dict(priority="P2", family="C8", cite="He JB et al. (2019) Angew Chem Int Ed — TcCGT1 原始表征",
      doi="10.1002/anie.201905505", pmid=None, publisher="Wiley", access="closed (R79 OpenAlex: is_oa=false)",
      why="TcCGT1 原始表征与结构；其底物面板可能含 chrysin 等其他黄酮的 8-C 数据→若开 C8 新 stratum epoch（合同 §9），是潜在 fresh 池的关键来源"),
 dict(priority="P2", family="C8", cite="江南大学 (2021) J Agric Food Chem — TcCGT1+蔗糖合酶 orientin/vitexin",
      doi="10.1021/acs.jafc.1c00602", pmid=None, publisher="ACS", access="closed (R79 OpenAlex: is_oa=false)",
      why="CN115975901A 背景自引的本体论文；TcCGT1 直接 8-C 催化 luteolin/apigenin 的量化生产数据；C8 epoch 的 build/fresh 候选来源"),
 dict(priority="P2", family="C8", cite="(2021) Bioorg Chem — one-pot enzymatic cascade orientin/vitexin",
      doi="10.1016/j.bioorg.2021.104926", pmid=None, publisher="Elsevier", access="bronze (OpenAlex is_oa=true) 但 ScienceDirect 人机验证拦截史——请代取 PDF",
      why="与 JAFC 2021 同族的独立定量数据；C8 epoch 的 build/fresh 候选来源"),
 dict(priority="P3", family="SS", cite="Kamsteeg et al. (1979) Phytochemistry 18:659",
      doi="10.1016/S0031-9422(00)84283-1", pmid=None, publisher="Elsevier", access="closed (R74: no legal OA)",
      why="Petunia 黄酮醇糖苷链延伸老文献（R10 引文网络定位；内容未核）"),
 dict(priority="P3", family="SS", cite="Kho et al. (1978) Z. Pflanzenphysiol 88:449",
      doi="10.1016/S0044-328X(78)80261-X", pmid=None, publisher="Elsevier", access="closed (R74: no legal OA)",
      why="同上链延伸老文献"),
 dict(priority="P3", family="SS", cite="Heinsbroek et al. (1979) Phytochemistry 18:935",
      doi="10.1016/S0031-9422(00)91452-3", pmid=None, publisher="Elsevier", access="closed (R74: no legal OA)",
      why="同上链延伸老文献"),
 dict(priority="P3", family="SS", cite="Sutter A, Grisebach H (1973) BBA 309:289",
      doi="10.1016/0005-2744(73)90027-2", pmid=None, publisher="Elsevier", access="closed (R74: no legal OA)",
      why="黄酮醇糖基转移酶可逆性/底物专一性时代文献"),
 dict(priority="P3", family="C6", cite="王源杰 (2018) 硕士学位论文《毛竹叶黄酮碳苷 C-糖基化途径及其 C-糖基转移酶的研究》中国林业科学研究院（导师郭雪峰）+ 期刊版：王源杰、郭雪峰、赵蕾《林业科学》2018 年 54 卷 12 期",
      doi=None, pmid=None, publisher="CNKI/掌桥科研", access="摘要公开；全文代理获取",
      why="四属之外第一个直接型黄酮 C6 天然纯化酶证据（毛竹叶天然 CGT：luteolin+UDP-葡萄糖→isoorientin 6-C 为主途径，Q-TOF 肽段匹配）；若其面板含 apigenin/chrysin 等其他黄酮的 C6 数据，是 C6 方向仅存的新来源可能"),
 dict(priority="P3-optional", family="C", cite="(2026) J Agric Food Chem — EkCGT1 (Euscaphis konishii)",
      doi="10.1021/acs.jafc.5c09887", pmid="41568575", publisher="ACS", access="closed (OpenAlex 经子代理；摘要级)",
      why="体外活性扎实但主底物为色酮 noreugenin；黄酮面板 unknown——若全文面板含黄酮即为边界外新证据"),
]

SELF_OBTAINED = [
 "Shi CQ 2026 (Synth Syst Biotechnol 13:350, PMC12993211, CC-BY) — TcCGT1 工程版：已 R77 密封保管（未读内容）",
 "Trapero A 2012 (Plant Physiol 159:1335, PMC3425182) — Crocus UGT707B1：已 R78 密封保管（canonical PMC HTML；未读内容）",
 "EfCGT1 2025 (PBJ, PMC12310836) — 芡实 C-GT：已 R79 密封保管（未读内容）",
 "免费专利：CN113186214A（TcCGT1+GmSUS，apigenin→vitexin / luteolin→orientin 定量数据，子代理已读至实施例参数）、CN121065126A（三叶青 ThCGT，体外验证 apigenin C-8→vitexin，本轮主控已读）、CN111808902B、EP4095145A1、WO2021065749A1 族、CN111041056B/CN111019919B、CN115975901A、CN114657160B、JP7531507B2、JP7405836B2、CN112961870B/CN112813084B/CN117187207A/CN120330153A（后四者定位未深取）",
 "Kerscher & Franz 1987 (ZNC, OA PDF) — 荞麦 2-羟基黄烷酮路线的否定性边界证据",
 "R76 三条新路线 + 本轮四份研究员报告（已归档 evidence）",
]

SECTION = """

## progress-v37-final：来源发现战役扩容——C8 新方向确立与统一代取清单（2026-10-12）

任务阶段：来源循环在所有者明确授权下**恢复扩容检索**（用户指示"进一步扩大搜索范围"，并约定由其代取无法直接获得的原件）。批准 agent_delegated，非 human_reviewed。本节汇总三个并行研究员子代理 + 主控验证的扩容战役结果，并交付统一代取清单。

1. **C8 方向确立（本轮最重要发现）**：合同 §9 本就允许建立 flavone C8 stratum scope epoch。此前该方向只有 TcCGT1（Angew 2019）一条线索；本轮确认为完整文献群：① Shi CQ 2026（Synth Syst Biotechnol 13:350，**PMC12993211 OA/CC-BY**，R77 已密封保管）——TcCGT1 工程版，apigenin→vitexin + "55×其他黄酮受体"；② **CN113186214A（免费专利，子代理已读至实施例）**——TcCGT1+GmSUS 偶联，apigenin→vitexin、luteolin→orientin 定量数据（2324/5524 mg/L，89-91% 转化率），无 2-羟基黄烷酮中间体；③ **CN121065126A（免费专利，本轮主控已读全文）**——三叶青 ThCGT（第五个属：葡萄科 Tetrastigma），体外重组酶验证 apigenin C-8→vitexin + 烟草瞬时/稳定系统重建；④ JAFC 2021 与 BioOrg 2021（付费，列入代取清单）。本地核验：**orientin（luteolin 8-C）0 曝光、vitexin 仅分子级 target、上述四篇论文 0 曝光令牌**——8-C 方向的 build 支持（luteolin+apigenin 两受体）与潜在 fresh 池同时存在。

2. **C6 方向**：四属之外发现**毛竹天然纯化 CGT**（王源杰 2018 硕士论文+《林业科学》2018,54(12)）：luteolin+UDP-葡萄糖→isoorientin（6-C）为主途径——但由于 luteolin→isoorientin 是 C-E02 build 反应、apigenin→isovitexin 已曝光，其 fresh 价值取决于论文面板中其他黄酮数据（需原件）。Kerscher & Franz 1987（OA PDF）给出荞麦谱系 2-OH 路线的否定性边界证据。

3. **SS 方向**：Trapero 2012（Crocus UGT707B1，Plant Physiol 159:1335，**PMC3425182**）——摘要级强证据（kaempferol/quercetin 3-O-sophorosides + 转基因拟南芥表型），**R78 已密封保管 canonical PMC HTML（未读内容）**；曝光账 0 行，R29 仅有图注级提及（metadata hint 已登记）。其 quercetin 3-O-糖苷 O2 反应若正文有结构级证据即为第一个 fresh SS 目标候选。Vogt & Taylor 1995（PMC157439）为 R10 评审已标注的 design-exposed。SS 专利线两轮查询阴性；UGT79B 家族全库扫描无新表征成员。

4. **R79 收尾批（7/7 HTTP，全局 1298 HTTP / 1,245,739,256 B）**：清单条目 OpenAlex OA 验证 + EfCGT1（芡实，PBJ 2025，PMC12310836，gold OA）密封保管——2023-2026 唯一待读的新 CGT 表征论文。

5. **统一代取清单**：`governance/R79-originals-request-v1/originals_request_list.md`（P1×2 / P2×3 / P3×6，含 DOI、出版商、访问状态证据、代取理由与注意项）；已自行取得项单列。全部研究员报告归档 `discovery_evidence/session2_20261012/`。

6. **后续资格流水线（待下一批执行，本节不做）**：Trapero 2012 → G5 预注册 → A4/A5 双独立抽取（HTML）→ A6 闭包（含 R29 图注提示与同队列裁决）→ 若 quercetin 反应合格即首个 fresh SS 目标；Shi 2026/EfCGT1 密封件同理。C8 方向的 epoch 决策（C-E03 scope 设计→G4 冻结→fresh 池评估）待所有者对代取原件到位后一并定夺。本轮无化学检视、无新 MCTS、无新曝光行（密封保管不读内容）；293/293 回归与保护文件 0 漂移状态继承。
"""

def main():
    (ROOT / ARCH).mkdir(parents=True, exist_ok=True)
    (ROOT / EV).mkdir(parents=True, exist_ok=True)
    # 1) archive agent reports
    for src, name in ((".zwork/runs/ca622eb6/1-研究员.md", "SS_axis_deep_agent_report.md"),
                      (".zwork/runs/ca622eb6/2-研究员.md", "old_era_patents_agent_report.md"),
                      (".zwork/runs/ca622eb6/3-研究员.md", "C_axis_gapfill_agent_report.md")):
        write(T, str(EV / name), (ROOT / src).read_text(encoding="utf-8"))
        write(T, str(EV / (name + ".provenance.json")), json.dumps(dict(
            task=T, copied_at=datetime.now(timezone.utc).isoformat(), source_path=str(src),
            source_sha256=sha(src), role="A1/A2 discovery researcher (web metadata only)", approval_type="agent_delegated",
            human_reviewed=False), ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    (ROOT / EV / "C_axis_first_attempt_timed_out.md").write_text(
        "C-axis deep agent (job uKNXs9UyqoMcfGZJIAeQKg) exceeded deadline and produced no report; its scope was covered by the old_era_patents agent (patents+theses) and the C_axis_gapfill retry agent; no identifiers were recovered from the failed run (terminal=failed, empty projection).") if not (ROOT / EV / "C_axis_first_attempt_timed_out.md").exists() else None
    # 2) unified list
    lst_md = ["# TASK-016-P7 统一代取原件清单（progress-v37，2026-10-12）", "",
        "以下为项目无法直接合法获得、请所有者代取的原件。已自行取得项单列于文末。拿到后请放入 `data/inbox/`（或告知路径），由项目走 G5 预注册→A3→A4/A5→A6 资格流水线。", ""]
    for e in ENTRIES:
        lst_md.append(f"## {e['priority']}｜{e['family']} 轴")
        lst_md.append(f"- **{e['cite']}**")
        if e.get("doi"): lst_md.append(f"- DOI: {e['doi']}")
        if e.get("pmid"): lst_md.append(f"- PMID: {e['pmid']}")
        lst_md.append(f"- 出版商/访问状态: {e['publisher']} — {e['access']}")
        lst_md.append(f"- 代取理由: {e['why']}")
        if e.get("caution"): lst_md.append(f"- 注意: {e['caution']}")
        lst_md.append("")
    lst_md.append("## 已自行取得（无需代取）")
    for s in SELF_OBTAINED: lst_md.append(f"- {s}")
    lst_md.append("")
    lst_md.append("## 处理纪律提醒")
    lst_md.append("- 全部原件到位后统一走预注册资格流水线（G5 先于任何内容阅读）；付费墙不可绕过，代取是唯一合法途径。")
    lst_md.append("- Trapero/Shi/EfCGT1 三个密封件已保管未读：内容阅读必须等到各自 G5 批次。")
    write(T, str(OUT / "originals_request_list.md"), "\n".join(lst_md) + "\n")
    save_json = dict(task=T, at=datetime.now(timezone.utc).isoformat(), approval_type="agent_delegated",
        human_reviewed=False, entries=ENTRIES, self_obtained=SELF_OBTAINED,
        evidence=dict(r79_verification=pointer(R79M / "access_verification_summary.json"),
                      r78_trapero=pointer(B / "SS/E02/fresh/SS-E02-R78-trapero2012-raw-custody-v1/raw_custody_summary.json"),
                      r77_shi2026=pointer(B / "C/E02/fresh/C-E02-R77-shi2026-TcCGT1-raw-custody-v1/raw_custody_summary.json"),
                      r74_noOA_batch=pointer(B / "SS/E02/fresh/SS-E02-R74-final-lead-metadata-v1/final_lead_dispositions.json"),
                      agent_reports=[pointer(EV / "SS_axis_deep_agent_report.md"), pointer(EV / "old_era_patents_agent_report.md"), pointer(EV / "C_axis_gapfill_agent_report.md")]))
    write(T, str(OUT / "originals_request_list.json"), json.dumps(save_json, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    # 3) REPORT v37
    rep = (ROOT / REPORT).read_text(encoding="utf-8")
    if "progress-v37-final：来源发现战役扩容" not in rep:
        write(T, str(ARCH / "REPORT-016-P7.pre-v37.md"), rep)
        rep2 = rep.replace("当前权威截面 **progress-v36-final（见文末）**", "当前权威截面 **progress-v37-final（见文末）**", 1)
        if rep2 == rep: raise RuntimeError("HEADER_ANCHOR_NOT_FOUND")
        rep2 = rep2.rstrip("\n") + "\n" + SECTION
        write(T, str(REPORT), rep2)
    # 4) STATE
    st = (ROOT / STATE).read_text(encoding="utf-8")
    if "统一代取清单" not in st:
        anchor = "R76 以学术检索技能路由的三条新路线（MeSH 全字段、elink 引文追踪、PPR 预印本；14/14 HTTP，全局 1286 HTTP / 1,244,871,814 B）复核：385 唯一命中、25 条标题相关逐一处置，0 个新 scope 对齐候选，饱和判定维持；快照 progress-v36-final。"
        if anchor not in st: raise RuntimeError("STATE_ANCHOR_NOT_FOUND")
        add = ("所有者授权恢复扩容检索后（progress-v37-final）：三个研究员子代理+专利/学位论文/向前引文路线发现 **C8 方向确立**（TcCGT1 簇 + 三叶青 ThCGT 第五属 + 毛竹天然 C6 酶 + Trapero 2012 Crocus UGT707B1），Shi 2026/Trapero 2012/EfCGT1 三件 OA 原件已密封保管未读；"
               "统一代取清单 `outputs/task016-p7/v1/governance/R79-originals-request-v1/originals_request_list.md`（P1×2/P2×3/P3×6）已交付所有者；全局 1298 HTTP / 1,245,739,256 B。")
        write(T, str(STATE), st.replace(anchor, anchor + add, 1))
    # 5) snapshot
    snap = dict(task=T, version="progress-v37-final", as_of=datetime.now(timezone.utc).isoformat(),
        status="Source_loop_resumed_owner_authorized_originals_list_delivered",
        approval_type="agent_delegated", human_reviewed=False,
        fresh_C=0, fresh_SS=0, scientific_ABE_cells=0, metrics=None, roadmap_P2_completed=False,
        physical_HTTP=1298, physical_bytes=1245739256,
        new_directions=dict(C8="established: TcCGT1 cluster + ThCGT 5th genus; orientin 0-exposure, vitexin target-only; epoch decision pending owner originals",
                            C6="bamboo natural CGT (thesis+journal) = only remaining new direct-C6 lead outside 4 genera",
                            SS="Trapero 2012 in custody (quercetin-O2 fresh candidate); pea 1982 owner-pursuing"),
        sealed_custody=[{"pmcid":"PMC12993211","round":"R77"},{"pmcid":"PMC3425182","round":"R78"},{"pmcid":"PMC12310836","round":"R79"}],
        originals_list=pointer(OUT / "originals_request_list.md"),
        originals_list_json=pointer(OUT / "originals_request_list.json"),
        r79_verification=pointer(R79M / "access_verification_summary.json"),
        agent_reports=[pointer(EV / "SS_axis_deep_agent_report.md"), pointer(EV / "old_era_patents_agent_report.md"), pointer(EV / "C_axis_gapfill_agent_report.md")],
        prior_snapshot=pointer(SNAP / "progress-v36-final.json"),
        archive={"report_pre_v37": pointer(ARCH / "REPORT-016-P7.pre-v37.md")})
    p = SNAP / "progress-v37-final.json"
    if not (ROOT / p).exists():
        write(T, str(p), json.dumps(snap, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(report_sha=sha(REPORT), state_sha=sha(STATE), list_sha=sha(OUT / "originals_request_list.md")), ensure_ascii=False))

if __name__ == "__main__":
    main()
