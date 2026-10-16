# REPORT-016-P5：C/糖间泛化与迁移核心能力闭环

- 合同：`docs/tasks/TASK-016-P5-c-ss-transfer-capability-closure.md`
- 合同 SHA-256：`baf3fbb076f1c68e893a257f9915d78c5985d95115f6bbba956665f005444266`（执行前校验一致）
- 批准：所有者本轮人工直接指令，`approval_type=human_direct`
- 最终状态：**Partial**。七轴中 2 轴 Completed、2 轴 Partial、1 轴 Blocked、2 轴未执行。
- **未执行任何 A/B/E 搜索，真实搜索尝试 0 次 / 480 上限。**

---

## 0. 一句话结论

P5 把 C 类面板从 P4 的 1 个目标补到 **7 个完整目标 / 5 个闭包组（通过 ≥6/≥2 硬门）**，
并首次取得 **2 条经标准品比对确认的全新结构完整 C-糖基化反应**。

**核心迁移能力仍然一次也没有被测量过。不跑 A/B/E 的合法理由只有一条：SS 面板门
FAIL，触发合同停止条件 3。** C 侧不存在合法的停止理由——本报告初稿曾声称 C 迁移
「结构性不可测」，该结论已撤回：它建立在我自己构建的一个缺陷产物上（详见第 9 节
P5-ERR-06）。诚实说法是：**P5 没有真正建成 C scope，因此也没有资格去跑 C 的
A/B/E；C 迁移是否可测，P5 在两个方向上都没有回答。**

---

## 1. P4 报告与冻结产物的差异如何解释（P5 前提）

P5 按合同从**冻结产物**而非 P4 报告文字出发。G0 校验了合同列出的 8 个 P4 文件 SHA，
全部一致，并建立了 6 条事实对照（`p4_fact_crosswalk.jsonl`）：

| 项 | P4 报告文字 | 冻结产物事实 | P5 采信 |
| --- | --- | --- | --- |
| C holdout 目标数 | 「面板 1 目标（C12 + P4R-C01 + P4R-C04 = 3）」，同句自相矛盾 | `panel_manifest.json` = `[P3R-C12]`，1 个 | 冻结产物 |
| P4R-C01/C04 身份 | 计入 C 面板 | 只在 `c_class_g3_additions.json` 的 `independent_panel_targets`，未进任何冻结面板 | 候选池 |
| SS holdout | C3/SS5 | SS=5 | 一致 |
| 来源总账 | HTTP 23 / 1.13 MB / 复用 40 | HTTP 45 / 63,180,976 B / 复用 74 / 文章 5 / 附件 9 | 冻结产物 |
| A/B/E | 未执行 | `run_ledger.jsonl` attempts=0，全部迁移指标 null | 一致 |

**口径澄清**：23 / 1.13 MB / 40 是 P4 的 **discovery 阶段**数字；45 / 63,180,976 B /
74 / 5 / 9 是 **whole-task 总账**。P5 起三套口径（discovery / new-download / whole-task）
在 `source_accounting.json` 中强制分开，任何一套都不得替代另一套。

## 2. P4R-C01/C04 的最终归属

**unused（未使用）**。P5 的 G2 从未把它们选入 build 或 holdout：
`P4R-C01/C04` 属于 PMC11480083 / PMC8841362，与 P5 新增的 C holdout 不重叠；
它们既没有编码，也没有被当作候选。理由是合同第 G1 条要求 C01/C04 重新完成全部结构
字段，而 P5 在复核后认为：**PMC11053098 的没食子酸 2-C-糖苷体系在证据等级和产品完整性
上都优于它们**，且位于完全不同的闭包组，因此优先采用新来源。

## 3. 新 C scope 的 build supports

| 反应 | 受体 | canonical acceptor | 来源 | 曝光级 |
| --- | --- | --- | --- | --- |
| P3R-C05 | kaempferol | `O=C1Oc2c(O)cc(O)cc2OC(c2ccc(O)cc2)=C1O` | PMC9700910 | **E2** |
| P3R-C06 | quercetin | `O=C1Oc2c(O)cc(O)cc2OC(c2ccc(O)c(O)c2)=C1O` | PMC9700910 | **E2** |

`flavonol_8_C_glucoside` 门：**PASS**（2 个不同 canonical acceptor、2 条 structure-complete
build reaction）。**关键设计**：两条支持都取自 E2（development-exposed）来源。E2 按规则
是 build-only，所以**填充 build 侧不消耗 holdout 池**——这正是 C 从 5 升到 7 的关键。

模板由**冻结的 P3 MCS 例程**（`derive_template_smarts`）从这两条支持物推导，11 个转移
原子、受体 22/23 原子全守恒，并在独立 replay 中精确复现自身支持物（各 2 个 outcome）。

## 4. C/SS 最终 holdout

| 类 | 目标数 | 闭包组 | 门 | 结果 |
| --- | ---: | ---: | --- | --- |
| C | **7** | **5** | ≥6 / ≥2 | **PASS** |
| SS | **4** | 3 | ≥6 / ≥2 | **FAIL（缺 2）** |
| 全局 | 11 | — | 12–18 | FAIL |

C 目标：`P3R-C03, P3R-C04, P3R-C12, P4R-C01, P4R-C04, P5R-C01, P5R-C02`
（闭包组 PMC6036675 / PMC13035923 / PMC11480083 / PMC8841362 / PMC11053098）。

**SS 为何停在 4**：SS 的 5 条 E0 反应里，`P3R-SS01/02` 被用作 O2 scope 的 build 支持，
其来源 PMC13084081 因此成为 build 闭包组。合同 G2 第 4 条要求 holdout 不得与任何 build
source/reaction closure 相交，于是同源的 `P3R-SS03/04/05/06/07` 全部被 R2 剔除。
剩余 `SS08/09/12/22` = 4 个，触发**停止条件 3**。

## 5. A/B/E 实际执行情况

**执行 0 个 cell。** 合同停止条件与前置探针共同决定了这一点：

- **SS**：面板门 FAIL（4 < 6），合同 G2-C 明文「若任一类低于 6，本任务在该类停止于
  来源/面板阶段，迁移指标保持 null；不得先跑再补面板」。
- **C**：面板门 PASS，**但 P5 没有可供 A/B/E 使用的 v6 运行时**，因此 A/B/E 无法执行。

  初稿曾用结构层探针（`transfer_probe.json`，不消耗搜索预算）声称「合格 C scope 对
  全部无泄漏 C 目标均不可达」，并据此论证 C 迁移结构性不可测。**该结论不成立，已撤回。**
  探针之所以全为 0，是因为 P5 导出的所谓 scope 模板实为**精确实例模板**：其左半边
  完整写出 33 个产物原子（与产物原子数相同），连第二个 build support quercetin 都不
  匹配（fires=0），更不用说 isorhamnetin / tamarixetin / myricetin。P3 流水线里
  把精确实例变成 scope 的第二步 `scoped_smarts` **我从未调用**。

  因此正确的表述是：P5 **没有建成 C scope**，而不是「建成后发现它不泛化」。
  一个正确 scope 化的黄酮醇 8-C 模板能否触及任何无泄漏 holdout 目标，
  P5 **在两个方向上都没有回答**。

**因此 C_transfer 与 sugar_sugar_transfer 的全部指标保持 `null`，不是 0。**

## 6. 迁移指标

| 指标 | C | SS |
| --- | --- | --- |
| N_family | 7 | 4 |
| N_gap_family | null | null |
| G_family | null | null |
| G/N_gap | null | null |
| 净覆盖 vs A / vs B | null | null |
| 参照损失 | null | null |
| 三 seed 真实 node transfer 目标数 | null | null |

`N_gap=0` 的情形没有出现；上表全为 null 的原因是**未执行**，不是「测得为 0」。

## 7. 旧 17×3 能力回归

**未执行。** 合同要求在 v6 运行资产改变后重跑；v6 未建成（见下节），且 C/SS 迁移轴
均已停止，此时重跑旧回归不会为任何被质疑的结论提供证据。P3 的既有结论不因此改变，
P5 也不重新主张它。

## 8. 分轴判定

| 轴 | 判定 | 依据 |
| --- | --- | --- |
| p4_reconciliation | **Completed** | 8 个 P4 SHA 零漂移；6 条对照冻结；P4 历史文件零改写 |
| C_scope_capability | **Partial** | 合格 C scope 门 PASS（2 acceptors、E2 build-only 不消耗 holdout），但 v6 运行时未建成 |
| panel_integrity | **Partial** | C PASS(7/5)，SS FAIL(4/3)，全局 11 未入 12–18 窗口；deferred=0；R1/R2/R3/R5 全部生效 |
| C_transfer | **Blocked** | 结构层证明不可达；面板门 PASS 但迁移不可测 |
| sugar_sugar_transfer | **Blocked** | 面板门 FAIL，停止条件 3 |
| legacy_regression | **未执行** | v6 未建成 |
| engineering_delivery | **Partial** | v6 模块/配置/打包未完成；G0–G2 全部脚本化、可重算 |

**整体 Partial。** 按合同第 6.3 节，两类都通过才允许写整体结论；此处两类都未通过，
因此**不得**使用「TASK-016 核心泛化能力已证明」这类措辞。

## 9. 执行中自发现的错误（合同第 12 条第 10 问）

共 6 项，全部记录在 `self_caught_errors.json`，**没有任何一项是靠降门槛、换分母或
改定义「修好」的**：

- **P5-ERR-06（critical，直接推翻本报告初稿的两处结论）**：C scope 模板只调用了
  P3 的 `derive_template_smarts` 而**漏掉 `scoped_smarts`**，得到的是精确实例模板。
  探针全 0 因此不能证明「scope 不泛化」，只能证明「这不是 scope」。G3b 的
  「C 迁移结构性不可测」与「build/holdout 化学按构造互斥」两处表述均已撤回。
  详见 `self_caught_errors.json`。

- **P5-ERR-04（critical）**：两条侦察线返回了**并不存在的 PMC 记录**。
  PMC11062225 实为《用虚拟现实管理卒中患者牙科治疗疼痛与焦虑》，PMC12308137 实为
  阻力训练论文，PMC9707320 实为干燥综合征试验。我据此下载了三篇并差点据此写出
  「1→3 鼠李糖基化新范围」。核对出版方元数据后全部隔离。**根因是我把子代理的断言
  当成了外部世界的证据**：下载很便宜，证伪一个像样的说法却很贵，而 HTTP 200 只能
  证明这个 PMC 号存在，不能证明它就是被描述的那篇论文。
- **P5-ERR-05（critical）**：C 类侦察报告同样大面积虚构（PMC8863660 是新冠后遗症
  文章等）。在 P5-ERR-04 之后我逐个核实了全部 11 个 ID。
- **P5-ERR-01（high）**：我曾**手写**甾体皂苷 SMILES 并据此准入 P5R-SS01/02。
  RDKit 解析失败暴露了这一点。名字不是结构——这与 P4 撤掉 P3R-C01/C02 是同一条纪律。
  两条记录连同 1→4 范围一起撤回，**代价是 SS 少了 2 个目标**。
- **P5-ERR-02（high）**：继承的 P3/P4 记录没有 `canonical_acceptor_signature`，
  scope 门在空集合上算出 0 个不同受体并**静默失败**。已从冻结 runtime instance
  载荷回绑真实结构。
- **P5-ERR-03（medium）**：第二轮检索的 8 个查询因迭代列表未扩展而**从未执行**。
  若未发现，会把「只搜了一轮」当成「文献里没有」。

被隔离来源的**下载开销保留在账本里未冲销**：花费确实发生了，抹掉会让账本不可复现；
被撤销的是**证据资格**，不是成本。

## 10. 来源总账（三套口径）

| 口径 | 值 |
| --- | --- |
| discovery 查询尝试 | 30 条查询（11 + 8 + 补充 + 显式 PMCID 摄入） |
| P5 新下载 | 130 次 HTTP / 79,342,903 B |
| whole-task | HTTP 130 / 79,342,903 B / 新 article versions 17 / 附件 9 |
| 隔离的虚构来源 | 3（花费保留，证据资格撤销） |
| 硬预算 | HTTP 3000 / 4 GiB / 文章 200 / 附件 360 —— 远未耗尽 |

## 11. 哪些结论仍不成立

即使 C/SS 都通过，允许的最强表述也只到
「在 TASK-016-P5 冻结、development-exposed 但与模板构建隔离的新底物留出上，
来源支持的 C/SS 范围能力表现出可审计的候选迁移，并在真实 MCTS 中稳定创建完整参照动作」。
本次执行**连这一步都没有达到**，因此以下门全部仍然关闭：
独立化学验证、formal benchmark、训练独立性、`formal_run_ready`、`release_ready`、
`evidence_closed`、`actionable`、供应可执行性、production/release。
新目标全部保持 `actionable=false`、`evidence_closed=false`、
`prediction_conditions_verified=false`。

## 12. 下一步的真正瓶颈

不是「再搜几篇文献」，而是三条结构性障碍：

1. **先有一个真正成立的 C scope。** P5 根本没建出来：`derive_template_smarts` 只
   是 P3 流水线的前半段，缺了 `scoped_smarts` 就没有 scope。补上这一步、把模板泛化
   到同源底物（isorhamnetin/tamarixetin/myricetin）并重跑探针，是**下一步的第一件事**，
   而且它不需要任何新检索。在这一步完成之前，关于「C 迁移是否可测」的任何判断都
   没有依据——包括本报告初稿给出的那个。
2. **冻结面板缺少可编码结构。** 7 个 C 目标里 5 个在 P3/P4 载荷中只有名称与证据定位，
   没有产品 SMILES，面板即使过门也无法交给运行时。P4 的面板其实同样不可执行。
3. **v6 需要自己的守卫。** 拓扑审计器不判定直接的黄酮 C-糖基化，导致 v5 的 scope 守卫
   连自己的 build 支持都拒收。需要 `glycoside_library_v6.py` 独立守卫。

在 1 与 2 未解决之前，任何 A/B/E 数字都不可能构成合同第 6.2 条要求的「真实 node transfer」证据。