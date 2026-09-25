# TASK-011：糖苷连接拓扑审计接入 Web 界面（有效性判断可视化）

## 合同元数据

- 任务 ID：TASK-011
- 状态：Approved（已批准）
- 基线分支：main
- 基线提交：115cf67（feat: TASK-010 web 工作台完整化、布局修复与独立收口）
- 人工负责人：项目所有者（ljx）
- 执行者：Kimi（Kimi Work 会话，经 ssh cano 在远程执行验证）
- 修改预算：`flavoretro/web.py`、`web/` 三个前端文件、`tests/test_web.py`、`scripts/browser_check.py`、`docs/`（tasks/reports 两目录 README、docs/README.md、WORKBENCH_ROADMAP.md）、根级 `STATE.md`；不动 `flavoretro/` 其余模块（含 `topology.py`）、`configs/`、`data/`、`outputs/`、`metadata/`、旧项目目录
- 批准：项目所有者（ljx）人工批准（2026-09-25，本会话回复"同意。开始执行"）。所有者已于同日早前收回 agent 代行批准权（原话："delegate 权利已经被我收回，从此之后所有 task 起草后必须经我人工确认才可执行"），本批准为人工批准，非 agent_delegated

## 目标

把已有的糖苷连接拓扑审计（`flavoretro/topology.py` 的 `audit()`）以只读方式接入 Web 工作台界面：目标分子与路线末端原料的糖苷位点家族候选标注（aryl_O / sugar_sugar_O / aryl_C 等标签原样呈现并附中文释义）、结构图候选键按家族着色高亮、随每处标注同屏出现的边界文案、与文献教学层的工程关联链接。只呈现，不改搜索语义。完成判定：验收标准全部通过，单元测试与浏览器验收在 cano 通过。

## 背景

- 拓扑审计自 TASK-006 起仅存在于结构诊断层：`python -m flavoretro.topology` CLI 与 `outputs/validation/topology-v1.json`（首版 55 次回放失败，有意保留）/ `topology-v2.json`（修复后 156 分子、132 检出、192 位点、0 回放失败）；未进搜索、未进界面（REPORT-006；STATE.md 已知缺口第 2 条）。
- WORKBENCH_ROADMAP P1（有效性判断可视化，低风险，建议优先）即本任务对应阶段；其准入原本允许 agent_delegated 批准，但所有者已于 2026-09-25 收回代行授权，故本任务走人工批准。
- `audit(smiles)` 为纯计算：输入任意 SMILES 返回糖环候选数与位点列表（family、bond_index、anomeric_candidate、other_atom、sugar_ring_size、graph_roundtrip）及 claim 原文 "topology candidates; no independent labels or reaction feasibility"；不写文件、不触碰搜索。
- 搜索响应的树节点与末端叶子均携带 SMILES（前端 treeView/leafCard 已使用），前端可按 SMILES 调新端点完成标注，无需改动搜索。
- 已在 cano 验证可行性：本机 RDKit 的 rdMolDraw2D DrawMolecule 按位置传参（highlightAtoms、highlightBonds、highlightAtomColors、highlightBondColors）可对候选键着色高亮。
- 文献教学层 15 张文献卡中多条 title/key_step 涉及 O-/C-糖基化文本（如 P003/P004 的 C-glycosylation、P010 的 4'-/7-O glycosylation、P014 的分支糖链转化），可做关键词工程关联；关联本身不是化学判断。

## 范围

### 允许项

- `flavoretro/web.py`：新增 `GET /api/topology?smiles=`（SearchRequest 校验 → `topology.audit()` → 返回位点列表、claim 原文字段与 boundary 字段 "labelled graph synthons, not reagents"）；`/api/molecule` 新增可选参数 `topology=1`（对同一规范化 SMILES 运行 audit 并按家族着色高亮候选键；不带该参数时行为逐字节不变）。
- `web/index.html`、`web/app.js`、`web/style.css`：探索页目标分子侧栏新增拓扑标注区块；末端原料卡追加拓扑标注；家族中文标签映射；文献关联 chips（点击切换到文献教学页并滚动定位对应卡片，卡片新增锚点 id）。
- `tests/test_web.py`：新增拓扑端点与高亮绘图测试（沿用 ephemeral 端口真实服务器写法）。
- `scripts/browser_check.py`：新增拓扑块与边界文案断言（仅选择子与断言适配，不动既有流程）。
- `docs/tasks/README.md`、`docs/reports/README.md`、`docs/README.md`、`docs/WORKBENCH_ROADMAP.md`、根级 `STATE.md` 的一致性更新；新增 `docs/reports/REPORT-011-topology-web.md`。
- 全部写入与命令经 `scripts/operate.py TASK-011` 在 cano 服务器执行记录（`/Volumes/cano` 挂载仅用于访问，不作为运行环境）；写入暂存用 `operations/.staging-task011/`（沿用 TASK-009/010 先例，非交付物）。

### 禁止项

- `flavoretro/` 中 `topology.py`、`search.py`、`worker.py`、`policies.py`、`resources.py`、`contracts.py`、`service.py`、`evaluation.py`、`cli.py` 的任何改动。
- `configs/`、`data/`、`outputs/`、`metadata/` 的任何改动；不新跑全量审计，不改 `topology-v1.json`/`topology-v2.json`。
- 把拓扑候选接入 MCTS 扩展或评分（属 P2，须先冻结定义与评测协议并另行人工批准）。
- 界面措辞升格：拓扑候选不得表述为已验证断裂位点、试剂或反应可行性结论；"labelled graph synthons, not reagents" 边界文案与 claim 原文须随每处标注同屏出现。
- 文献关联不得表述为化学验证或人工核对结论；不修改文献/教学配置文件。
- 对 `/home/ljx/retro_synthesis` 与 `/home/ljx/CondRxnBench` 的任何写入；不在旧目录运行可能写缓存的代码。
- 推送远程、创建 GitHub 仓库、替换 git 身份。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| flavoretro（共享 API 逻辑） | web.py | 新增 /api/topology 端点；/api/molecule 可选 topology 高亮参数；其余逐行不动 |
| web（浏览器工作台） | index.html、app.js、style.css | 目标分子拓扑区块、末端原料拓扑标注、家族中文标签映射、边界文案同屏、文献关联 chips 与卡片锚点 |
| tests（测试合同） | test_web.py | 新增拓扑端点结构/边界字段/非法输入/高亮 SVG 四项测试 |
| scripts（活动工具） | browser_check.py | 新增拓扑块与边界文案断言 |
| docs/tasks、docs/reports（合同与报告） | TASK-011-topology-web.md、REPORT-011-topology-web.md、两目录 README | 本合同、事后报告与目录表登记 |
| docs（文档导航） | README.md、WORKBENCH_ROADMAP.md | 导航表新增行；P1 阶段状态收口 |
| 根级 | STATE.md | 状态更新至本任务完成后事实 |

## 非目标

- 不改变搜索、评分、资源准入的任何语义；不把拓扑审计接入搜索逻辑。
- 不对拓扑检测做独立真值、precision/recall 或化学有效性声称（沿用 REPORT-006 边界）。
- 不扩展 audit 检测范围（仍限 5/6 元含氧糖环候选）。
- 不做证据晋级、不处理名称冲突、不处理 TASK-007-P1（所有者搁置）。
- 不做 D3 可缩放路线树、JSME 结构编辑器等交互组件（P4 范围）。

## 必须执行的操作

1. 本合同经 operate.py 登记；获所有者人工批准后状态转 Approved（批准记录为人工确认，禁止写 agent_delegated）。
2. `flavoretro/web.py` 新增端点与可选高亮参数；扩充 `tests/test_web.py`。
3. `web/` 三文件实现拓扑标注、结构图键高亮联查、边界文案与文献关联。
4. 适配 `scripts/browser_check.py`。
5. 在 cano 远程依次验证：单元测试全套、启动服务 curl 全部端点（含新端点正/反例）、browser_check、一次真实搜索人工核对拓扑标注渲染截图。
6. 写 REPORT-011，更新 STATE.md、WORKBENCH_ROADMAP（P1 收口）与 docs 导航，Git 提交。

## 验收标准

- [ ] `/api/topology` 对含糖苷 SMILES 返回 200 与 sites（含 family、bond_index、sugar_ring_size、graph_roundtrip）、claim 原文与 boundary 字段（"labelled graph synthons, not reagents"）；普通醚阴性（sites 为空）；非法 SMILES 返回 400 invalid_request。
- [ ] `/api/molecule?...&topology=1` 返回 200 SVG 且候选键按家族着色；不带参数时行为与现状一致。
- [ ] 探索页目标分子区块与每条末端原料卡显示糖苷位点家族候选标注（中文释义 + 原始 family 串 + 糖环大小）；未检出时明确显示"未检出糖苷连接候选"而非沉默。
- [ ] 每处拓扑标注同屏含边界文案（含 "labelled graph synthons, not reagents" 原文与 claim 原文）。
- [ ] 拓扑标注含文献关联 chips，点击切换到文献教学页并定位对应卡片；关联处注明为工程关键词关联。
- [ ] 界面无升格措辞；evidence_closed:false、actionable:false 等既有事实行保持原样。
- [ ] `.venv/bin/python -B -m unittest discover -s tests` 在 cano 通过（含新增测试）。
- [ ] `scripts/browser_check.py` 在 cano 通过（含拓扑块断言）。
- [ ] 所有写入在 `operations/events.jsonl` 可查（含前后 SHA-256）。

## 验证

```bash
# 以下均经 scripts/operate.py TASK-011 包装记录，在 cano 远程 ~/FlavoRetro 执行
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B -m flavoretro.web --host 127.0.0.1 --port 8766 &
curl -sf "http://127.0.0.1:8766/api/topology?smiles=Oc1ccc(OC2OC(CO)C(O)C(O)C2O)cc1" | .venv/bin/python -m json.tool | head -40
curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8766/api/topology?smiles=INVALID"   # 期望 400
curl -sf "http://127.0.0.1:8766/api/molecule?smiles=Oc1ccc(OC2OC(CO)C(O)C(O)C2O)cc1&topology=1" -o /tmp/topo.svg && head -c 120 /tmp/topo.svg
.venv/bin/python -B scripts/browser_check.py
```

## 停止条件

- 呈现所需信息超出 `topology.audit()` 现有输出，需要改 `topology.py` 语义或字段：停止并报告，由所有者另批任务。
- 文献关联需要修改 `configs/` 或新增配置才能成立：停止并报告（本任务只做只读关联）。
- `browser_check.py` 需改动超出选择子与断言适配（如流程假设变化）：停止并报告，由所有者另批任务。
- 单元测试失败且与本次改动无关：记录并报告，不借机修无关代码。
- cano 远程环境故障导致无法验证：已完成部分如实记录，任务按 Partial 报告。

## 必须提交的报告

完成、部分完成或失败时，生成 `docs/reports/REPORT-011-topology-web.md` 并更新 `STATE.md`。
