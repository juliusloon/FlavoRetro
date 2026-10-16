# REPORT-016-P4：P3 准入纠偏与 C/糖间迁移验收补全

## 结论

整体 **Partial**。工程纠偏与准入纠偏两轴 Completed；C 迁移与糖间迁移两轴 Partial，
**A/B/E 矩阵一次都没有执行**，全部迁移指标为 `null`（不是 0）。

| 轴 | 状态 | 依据 |
| --- | --- | --- |
| correction_engineering | **Completed** | 独立终验 0 失败项 |
| corrected_reaction_admission | **Completed** | C=8 / SS=16 / 总 24，全部达到 8/8/16 地板 |
| C_transfer | **Partial** | 面板 1 目标（C12 + P4R-C01 + P4R-C04 = 3，仍 < 6），A/B/E 未执行 |
| sugar_sugar_transfer | **Partial** | 面板 5 目标 < 6，A/B/E 未执行 |

批准：`human_direct`，所有者 2026-10-07「批准 TASK-016-P4 开始执行」；阶段决定 `agent_delegated`。
合同 SHA-256 `10f1b995d350ccea7a2511014a676844a5a05a6d8384be6e8d16973e39e1fb86`。
产物命名空间 `outputs/task016-p4/v1`，原始件 `data/raw/task016-p4/`，均本地不入 Git。

## 1. P3 原 34 条经重审后的四级状态

判据 T1–T5 写死在 `scripts/task016_p4_audit.py` 的 `A` 表，每条都记录 failed_tests
与证据定位，可独立重算。

| | P3 声称 | P4 纠偏 |
| --- | --- | --- |
| C_formation | 12 | **8** structure_complete / 4 deferred |
| sugar_sugar_formation | 22 | **16** structure_complete / 6 deferred |
| 合计 | 34 | **24** / 10 deferred / 0 provisional_inferred / 0 rejected |
| 覆盖 | — | **34/34** |

降级 10 条及原因：

- **P3R-C01、C02**：2-羟基黄烷酮 C-葡萄糖苷中间体在 PMC9563126 只做 MS、在 PMC6036675
  只算 m/z，PMC7060329 的 NMR 是脱水终产物 vitexin/isovitexin/orientin/isoorientin。
  P3 build 脚本把 identification 写成 “source NMR-assigned 2-hydroxyflavanone
  C-glycoside”，等于把终产物证据转嫁给未赋值中间体。降为 deferred。
- **P3R-C07**：vitexin 只有 LC-MS 与一句酶产物陈述，无标准品/NMR，达不到 T1。
- **P3R-C08**：中间体 3 只有 m/z 595 = 2 + 146，且 C2 构型未定。
- **P3R-SS17—SS21**：α-L 端基构型仅由产物类名（rutinoside/linarin）与 UDP-β-L-rhamnose
  供体规格推定，原文无 NMR；P3 自己的抽取也记 `identity_complete=false`。
- **P3R-SS23**：咖啡酰酯位置需图/SI 核验，P3 明确未做。

升级 1 条：**P3R-C12**。P3 记 deferred，理由「区域化学靠看图」，但 P3 自己已收的 SI 文本里
就有显式 **8-bromo 前体**与产物 92 的立体全名 `(2S,3S,4R,5R,6R)`，区域化学由前体固定，
不依赖看图。审计的单步是 91+45n→92（三-O-苄基保护产物）。论文对脱保护产物 93 的命名
自相矛盾，**未采用**。

## 2. 三个 P3 范围的保留/降级/撤出

计数键冻结为 `canonical_acceptor_signature`。

| 范围 | P3 支持数 | distinct canonical acceptor | 判定 |
| --- | --- | --- | --- |
| `C_hydroxyflavanone_C3` | 3 | **0**（C01/C02 降级后无中间体证据） | **撤出** |
| `rhamnoside_glucoside_O2` | 2 | **2** | **保留**，唯一进入 v5 |
| `rhamnoside_glucoside_O6` | 2（两篇来源） | **1** | **撤出** |

SS 1→6 的两个支持 `reaction_id` 同为 `P3R-SS03`，acceptor、target 完全相同，
所以 distinct canonical acceptor = 1 < 硬门 2。**两个出处不能把同一 canonical
acceptor 计成两个受体。**

## 3. 纠正后面板的可计算留出

暴露分级 E0/E1/E2 替代二元判断（一刀切「审查过=已暴露」会毁掉面板，
「审查过=干净」会泄漏）。另加一条硬规则：**任何被用作模板 build support 的反应
强制归入 build**，因为其精确结构/位点/供体范围已用于设计模板。

| | 目标 | 闭包组 | 硬门 | 结果 |
| --- | --- | --- | --- | --- |
| C_formation | **3**（P3R-C12、P4R-C01、P4R-C04） | 3 | ≥6 / ≥2 | **FAIL**（缺 3 目标） |
| sugar_sugar_formation | **5**（SS04、SS05、SS06、SS12、SS22） | 3 | ≥6 / ≥2 | **FAIL**（缺 1 目标） |

`deferred` 计入分母 = 0。全局 6 目标，未达 12–18 窗口。

## 4. G3 定向补源结果

独立预算实际用量很轻：HTTP 23/2000、字节 1.13 MB/2 GiB、文章 1/100、附件 0/180、
复用既有原始件 40 个。

- 已采集材料里的干净 C 来源已用尽（PMC11577821、PMC12310836 全 MS-only）。
- 两轮检索（11 + 9 条查询）后新获得 8 个来源；其中真正含酶促 C 成键且干净的 3 个：
  **PMC11480083**（Nat Commun，酰基间苯二酚/大科丙酮，产物克级分离、1H/13C NMR + 标准品，
  2ad 即 nothofagin）、**PMC8841362**（maclurin + UDP-Glc → 1a/2a/2aa）、**PMC8196924**。
- 裁定为结构完整的新 C 反应 **2 个**：P4R-C01（PMC11480083）、P4R-C04（PMC8841362），
  各属独立闭包组。另 8 个新来源反应降级/未准入（含 P4R-C06 又一次出现
  「从脱水终产物反推中间体」的同类缺陷）。
- P4R-C03 与旧 phloretin 路线同反应闭包，P4R-C02 是 O-糖基化产物，二者**不计独立面板目标**。

检索过程中发现并修复了一个真实缺陷：标题规则未归一化内联标记，
`<i>C</i>-glycosyltransferase` 匹配不上，导致 3 个真正的 C-糖基化酶论文被静默拒绝。
修复后选择数从 6 升到 13。**这次修复没有引用任何 A/B/E 成绩，纯属实现 bug 修复，
不影响任何科学门槛。**

## 5. A/B/E 执行情况

**执行 0 个 cell，搜索尝试 0 次。** 面板硬门是 G6 前置条件，两类都 FAIL 触发合同
停止条件第 6 条，因此在任何搜索前停止。P4 独立账本
`outputs/task016-p4/v1/run_ledger.jsonl` 如实记录「未尝试」，480 硬上限未动用，
未借用任何旧任务预算。

| 指标 | C | SS |
| --- | --- | --- |
| N_family | 3 | 5 |
| N_gap_family | **null** | **null** |
| G_family | **null** | **null** |
| G/N_gap | **null** | **null** |
| 真实三 seed 节点迁移数 | **null** | **null** |

## 6. 旧能力是否退化

本轮**未执行**旧 17 目标 × 3 seed 的 E 回归。v5 只把 1 个合格范围并入 v3 基线，
v3/v4 模板数逐项核对为 54/57 未变，151 项本地测试全通过（含 10 项新增 v5 合同测试），
v5 默认关闭、缺资产/哈希漂移失败封闭。旧能力未被本轮证伪，也未被重新主张为 P4 证据。

## 7. 被 supersede 的 P3 陈述

| P3 陈述 | P4 当前事实 | 为何保留 P3 历史 |
| --- | --- | --- |
| 34 个新反应「全部具备完整单步身份」 | 24 个结构完整、10 个降级 | P3/v1 是历史证据现场，本身也是 P4 的输入 |
| C 羟基黄烷酮 C3 范围已验收 | 撤出，C01/C02 中间体无完整结构证据 | P3 报告保留，不追改 |
| SS 1→6 有 2 个来源支持 | 1 个 distinct canonical acceptor | 同上 |
| 名义面板 C1/SS2 | C3/SS5（且 C 目标 3 含新增来源） | P3 已自标 2 条 deferred |
| A/B/E 迁移未执行 | 仍未执行（面板更小） | — |

## 8. 仍未关闭的科学门

C 与 SS 的迁移硬门（候选迁移 G≥3 且 G/N_gap≥50%、真实三 seed 节点创建、
净覆盖为正）**全部未关闭**。训练重叠仍 unknown，独立化学验证未发生，
formal benchmark 未执行，`formal_run_ready=false`、`release_ready=false`、
0 production、0 human_reviewed。证据闭环未完成。

## 9. 本轮发现的一个自身错误（据实记录）

首版 G4 面板把 **P3R-SS01/SS02/SS03** 放进留出，而这三条正是 P3/v5 用于构建模板的
support，等于用同一批数据既设计模板又测迁移。新增的 v5 合同测试
`test_runtime_holds_no_holdout_instance` 把它抓了出来。已补上
「build support 强制归入 build」规则并重新冻结面板，错误版面板完整保留在
`outputs/task016-p4/v1/superseded/` 作为证据。后果是 SS 从 8 目标降到 5 目标，
由 PASS 变 FAIL —— 这也说明首版面板原本是错的，不是因为收紧门槛。

## 工程事实

- 保护基线 3,165 文件；P3 合同 SHA 全部一致，P3 delivery manifest 逐字节可复现。
- 本地 151 项测试全过；v5 默认关闭、缺资产失败封闭、配置外部与包内副本逐字节一致。
- 新增文件：`flavoretro/glycoside_library_v5.py`、`configs/glycoside-library-v5.json`
  及包内副本、`scripts/task016_p4_{g0,audit,scopes,sources,new_sources,panel,build,runs,verify}.py`、
  `tests/test_task016_p4_library.py`；`contracts.py`/`worker.py`/`cli.py`/`workspace.py`
  各增 v5 接线。未执行 Git 同步。
