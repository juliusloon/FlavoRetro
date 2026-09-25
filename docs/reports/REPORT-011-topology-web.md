# REPORT-011：糖苷连接拓扑审计接入 Web 界面（有效性判断可视化）

## 对应任务

- 任务 ID：TASK-011
- 任务文件：[../tasks/TASK-011-topology-web.md](../tasks/TASK-011-topology-web.md)
- 状态：Completed（完成）
- 基线：main @ 115cf67（feat: TASK-010 web 工作台完整化、布局修复与独立收口）
- 批准：项目所有者（ljx）人工批准（2026-09-25，会话回复"同意。开始执行"）；所有者已于同日前收回 agent 代行批准权，本批准为人工批准，非 agent_delegated
- 执行时段：2026-09-25 15:03—15:27 UTC（合同登记至验收完成；文档落盘另计）
- 结果提交：见末节 Git 提交

## 改动文件

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| docs/tasks（事前合同） | TASK-011-topology-web.md | 新增：本任务合同；两次写入对应 Proposed（ca70b08d…）→ 所有者人工批准后 Approved（30b5a05d…） |
| flavoretro（共享 API 逻辑） | web.py | 改动（28946946… → aeb5fb8f…）：新增 `GET /api/topology?smiles=`（SearchRequest 校验后实时运行 `topology.audit()`，返回 sites、claim 原文与 boundary 字段 "labelled graph synthons, not reagents"）；`/api/molecule` 新增可选参数 `topology=1`（候选键按家族着色高亮，位置传参调用 DrawMolecule）；不带参数时行为不变；其余逐行未动 |
| web（浏览器工作台） | index.html | 改动（68808ad0… → 3ecd8bc5…）：探索页侧栏新增 `#topology` 拓扑区块容器 |
| web（浏览器工作台） | app.js | 改动（eedf3f38… → ee5009c2…）：拓扑标注渲染（家族中文释义 + 原始 family 串 + 糖环大小 + 键序号）、边界文案同屏、文献工程关联 chips（点击切文献页并滚动定位）、侧栏拓扑区块与过期渲染防护、末端原料卡异步拓扑标注、文献卡/课程卡锚点 id；fetchLiterature 抽取复用 |
| web（浏览器工作台） | style.css | 改动（27b687ce… → cc615e8a…）：拓扑块、边界文案、文献关联 chips 与叶子注记样式 |
| tests（测试合同） | test_web.py | 改动（8fbbf407… → 5ec34bcd…）：新增 4 项拓扑测试（位点与边界字段、普通醚阴性、非法输入 400、高亮 SVG） |
| scripts（活动工具） | browser_check.py | 改动（9df22b65… → 99918155…）：新增拓扑块、边界文案、键高亮、文献关联断言；既有流程逐行未动 |
| docs/reports（事后报告） | REPORT-011-topology-web.md | 新增：本报告 |
| docs（文档导航与路线图） | README.md、WORKBENCH_ROADMAP.md | 导航表新增 TASK-011/REPORT-011 行；P1 标记完成、现状更新；准入规则补记 2026-09-25 代行授权收回 |
| docs/tasks、docs/reports（目录规则） | 两目录 README.md | 文件职责表补登 TASK-010/TASK-011 与 REPORT-009/010/011 行（TASK-010、REPORT-009/010 行为此前漏登，本次一并补齐） |
| 根级 | STATE.md | 更新至本任务完成后事实：P1 完成、已知缺口改写、人工批准流恢复 |

生成但不进入 Git 的文件：`outputs/validation/browser-dc951e12/`（本次 browser_check 截图与 report.json）、`outputs/validation/topology-web-check/`（橙皮苷真实搜索渲染核对的截图与 check.json）、`operations/.staging-task011/`（写入暂存，沿用 TASK-009/010 先例，非交付物）。

## 实际改动

1. **拓扑端点**：`/api/topology` 对任意合法 SMILES 实时运行 `topology.audit()`（纯计算，不写文件），响应携带 sites（family、bond_index、anomeric_candidate、other_atom、sugar_ring_size、graph_roundtrip）、claim 原文 "topology candidates; no independent labels or reaction feasibility" 与 boundary 字段 "labelled graph synthons, not reagents"；非法 SMILES 经 SearchRequest 校验返回 400 invalid_request；普通醚返回空 sites 的 checked 结果。
2. **结构图键高亮**：`/api/molecule?...&topology=1` 对同一规范化 SMILES 审计并按家族着色高亮候选键（aryl_O 蓝、sugar_sugar_O 绿、aryl_C 紫、other_O 橙、N 红、磷酸对照灰）；diff 证实高亮版仅多出候选键着色路径（如 bond-4 fill #1972E5），不带参数时输出与改动前一致。
3. **探索页标注**：目标分子侧栏新增"糖苷连接拓扑"区块（预览/搜索时刷新，过期渲染丢弃）；每条末端原料卡异步追加拓扑标注；未检出位点明确显示"未检出糖苷连接候选"，不沉默；检出位点的叶子结构图同步切换为高亮版。
4. **边界文案同屏**：每处拓扑标注块携带"拓扑候选是带标记的图合成子，不是试剂（labelled graph synthons, not reagents）；topology candidates; no independent labels or reaction feasibility。"。
5. **文献工程关联**：按家族关键词在 `/api/literature-teaching` 的文献卡与课程中匹配（如 aryl_C → C-glycosyl），标注块内呈现为可点击 chips，点击切换文献教学页并滚动至对应卡片（卡片新增锚点 id）；关联处注明"工程关键词匹配，非化学验证"。
6. **未触碰项**：`topology.py`、搜索与评分、`configs/`、`data/`、`outputs/` 既有文件均未改动；搜索语义不变。

## 验证

| 命令或检查项 | 结果 |
| --- | --- |
| `.venv/bin/python -B -m unittest discover -s tests -v`（command-0045） | 32 项全部通过（28 项既有 + 4 项新增拓扑测试），OK |
| `/api/topology` 含糖苷正例 curl（command-0046） | 200：aryl_O_candidate、键 4、糖环 6 元、graph_roundtrip true；claim 与 boundary 字段原样在 |
| `/api/topology` 普通醚阴性 curl（command-0047） | 200：status checked、sites 空 |
| `/api/topology` 非法 SMILES（command-0048） | HTTP 400 |
| `/api/molecule?...&topology=1`（command-0049）与无参数对比 diff（command-0055） | 200 SVG；高亮版仅多一条候选键着色路径（bond-4，#1972E5），默认行为不变 |
| 既有端点回归 curl（command-0050） | /api/health、/api/status、/api/targets、/api/teaching、/api/literature-teaching、/api/records?kind=paper 全部 200 |
| `scripts/browser_check.py`（command-0051，产物 browser-dc951e12） | 通过：拓扑块断言（aryl_O_candidate + 两句边界原文）、键高亮 src 切换、文献关联 chips 4 枚、实时双阶段搜索、路线卡 >0、库存 49 条、文献卡 15 张、移动端无溢出、非法 SMILES 400、JS 零错误 |
| 橙皮苷真实搜索渲染核对（command-0053，产物 topology-web-check） | 侧栏 aryl_O_candidate + other_O_candidate 标注与高亮截图；quick 实时搜索完成；末端叶子 5 个拓扑块 + 7 条未检出注记；JS 零错误 |
| 橙皮苷 `/api/topology` 诊断查询（command-0054） | 与 `outputs/validation/topology-v1.json` 中同分子记录一致（aryl_O_candidate 键 15 + other_O_candidate 键 20） |

## 与任务合同的偏差

- 渲染核对脚本（一次性，非交付物）首跑 rc=1（command-0052）：脚本断言误按 topology-v1.json 中 neohesperidin 的 sugar_sugar_O_candidate 预期，而橙皮苷实际审计结果为 aryl_O_candidate + other_O_candidate（与 v1 中橙皮苷记录一致）。属脚本断言错误而非代码缺陷；修正断言后复跑通过（command-0053），界面与端点代码未因此改动。
- 8766 验证服务器的启动与关停、以及 SVG diff 与橙皮苷拓扑两次诊断 curl，最初直接经 ssh 执行（进程管理与只读诊断）；两条诊断 curl 已补记（command-0054、0055），服务器关停亦已记录（command-0056）。
- staging 目录的使用未在合同"允许项"逐字列明，沿用 TASK-009/010 先例（合同已允许"全部写入经 operate.py 执行记录"），暂存文件非交付物。

## 已发现但未修改的问题

- **文献关联选择性弱**：aryl_O 等家族的关键词在本文献语料（黄酮苷合成主题）中命中 15/16 条，区分度低；界面已注明为工程关键词匹配。属语料分布事实，不在本任务收窄。
- **橙皮苷糖间键为 other_O_candidate 而非 sugar_sugar_O_candidate**：与 topology-v1.json 同分子记录一致，属 `topology.audit()` 既有判定行为；本任务不改判定语义（合同禁止项），差异原因未做诊断。

## 遗留风险

- `/api/topology` 为逐请求实时计算，无服务端缓存（前端按 SMILES 有会话内缓存）；位点标注为结构候选，不构成断裂位点或可行性结论（边界文案已同屏）。
- 文献关键词关联依赖文献卡 title/key_step 文本，语料扩充后命中分布会变化；关联始终不构成化学验证。
- audit 检测范围仍限 5/6 元含氧糖环候选（REPORT-006 遗留风险不变）。
- 浏览器验收为工程验收，不构成人体可用性结论（report.json scope 已注明）。

## 仓库与 CI 状态

- 无 CI；验证依赖本地 unittest、端点 curl 与 browser_check（结果见上表）。
- 本任务全部写入与命令在 `operations/events.jsonl` 可查（TASK-011 前缀，含前后 SHA-256；命令输出存 operations/command-0045…0056.log，本机证据不入 Git）。
- Git 提交：见本节下方提交记录；`data/`、`outputs/`、`operations/.staging-task011/` 不入 Git。

## 建议的下一任务

- 按 [../WORKBENCH_ROADMAP.md](../WORKBENCH_ROADMAP.md) 推进：P3（教学条目与数值 classification 的映射补齐，低风险）；P2（黄酮苷有效性判断接入搜索）须先冻结定义与评测协议并人工批准，不因本次界面呈现自动开始。
- 工程向：`.venv` 独立环境重建验证（现依赖 retro Conda 环境的 system-site-packages，见 environment/README.md）。
