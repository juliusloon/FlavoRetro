# TASK-013：Web 界面设计规范落地（移动优先、对比度与可访问性）

## 合同元数据

- 任务 ID：TASK-013
- 状态：Done（完成；S1—S3 全部落地并通过验收）
- 起草日期：2026-09-26
- 基线分支：main
- 本地基线提交：5f3240f（TASK-011）；远端 main 核查值 f272c36，落后本地两个提交，TASK-012 G5 同步收口进行中
- 人工负责人：项目所有者 ljx
- 拟执行者：Cano
- 修改预算：仅“范围与修改预算”表所列；预算外改动先修订合同再审批
- 批准：所有者 ljx 于 2026-09-26 明确回复“批准，执行”，批准本合同 S1—S3 全部范围。记录为 human_direct 工程授权，非 agent_delegated。
- 设计依据：`docs/WEB_UI_DESIGN.md`（2026-09-26 经 operate.py 记录入仓，task=web-ui-design-spec；含完整色值 token 表、字体刻度、断点规则、逐页布局方案、微交互参数与无障碍清单）

## 目标

将 WEB_UI_DESIGN.md 的 T1—T3 落地到四页工作台：全部文字配色达到 WCAG 2.2 AA、布局从桌面优先翻转为移动优先 min-width 断点、页签与表格语义化并支持键盘操作、补齐按钮微交互与搜索加载骨架屏。完成判定为“验收标准”全部勾选；任一未勾选则结论为 Partial/Blocked，禁止写“界面优化完成”。

本任务是呈现层工程，不改变任何搜索语义、证据等级与文案内容；“界面通过验收”不代表候选路线可执行、不代表化学有效性。

## 起草前核查：已确认事实（2026-09-26 审计，非本任务未来成果）

1. 配色实测（WCAG 对比度计算，`operations` 本轮记录）：`.eyebrow` 3.94:1、`.note`/`.intro p` 4.33:1、`.empty` 3.20:1、`footer` 3.16:1（均 on #f3f5f1，正文级需 ≥4.5:1，不达标）；主按钮 6.58:1、hazard 6.66:1、导航 8.77:1 等其余 14 组通过。修正候选色 #4E5F56/#5C6F60/#3F6B56 已实测分别为 6.18/4.91/5.55:1。
2. 布局结构事实：`body{overflow:hidden}` + `main` 内部滚动；`.workspace` 基础样式为 `grid-template-columns:360px minmax(0,1fr)` 桌面双栏，仅靠 `@media(max-width:900px)` 单断点退化——桌面优先写法，无 768/992/1280 渐进增强。
3. 可访问性缺口：四个页签为普通 `button`，无 `role=tablist/tab/tabpanel`、`aria-selected` 与方向键导航；无 skip link；表格 `th` 无 `scope`；搜索失败提示复用 `role="status"`（polite）而非 `role="alert"`；复选框、`#preview`、表格“查看”按钮触控区域实测小于 44×44px。
4. 样式治理缺口：无 CSS 变量，同类弱化绿存在 #557157/#507353/#5c6f60/#65776e/#697a6c/#789078/#7c8d80 七种互不相等散值；字号 11—60px 共 14 档无比例体系；`font-weight:550` 非标准值；按钮除 disabled 外无 hover/active 态；搜索长任务仅静态文本提示。
5. `web/` 与 `flavoretro/assets/web/` 三个文件逐字节一致（diff 验证），后者为打包副本，改动必须双处同步。
6. 现有验收基线：`scripts/browser_check.py` 覆盖 1440×1000 桌面与 390×844 移动两档、四页横向溢出断言、真实双阶段搜索、拓扑/教学/文献/历史运行/12-cell 开发对照断言与 JS 错误收集；单元测试 TASK-012 验收基线 51 项（G1—G4 已通过，G5 收口ing，执行时以最新 STATE 为准）。

## 范围与修改预算

### 允许项（获批后）

| 目录及职责 | 允许文件（新增均为计划） | 用途与拟改动 |
| --- | --- | --- |
| web：工作台前端 | style.css、index.html、app.js | style.css 按设计稿重构（token 变量、移动优先断点、组件态）；index.html 仅加语义属性/角色/结构调整（tablist、skip link、th scope），文本节点零变更；app.js 仅加页签 aria/方向键、骨架屏渲染、错误提示 role=alert，不改请求参数与渲染数据逻辑 |
| flavoretro/assets/web：包内静态副本 | 同名三个文件 | 与 web/ 同步，保持逐字节一致 |
| scripts：验收工具 | browser_check.py；计划新增 contrast_check.py | browser_check 扩展 320/375/768/992/1280 视口、键盘操作与触控目标断言；contrast_check 对设计文档 §2.1 全表复测 ≥4.5:1 |
| tests：单元测试 | 现有测试；如确需，新增针对语义属性的 DOM 断言 | 防回归；不得为通过断言改动既有测试语义 |
| docs 与根级治理 | 本 TASK；计划 docs/reports/REPORT-013-web-ui-design.md；STATE.md；WEB_UI_DESIGN.md 仅在执行发现偏差时追加说明 | 事实与进度记录；历史 TASK/REPORT 不静默改写 |
| outputs/operations | 各阶段验收目录、截图、操作日志 | 保留成功与失败证据 |

### 禁止项与非目标

- 不改 `flavoretro/*.py` 后端、任何 API、`configs/`、`data/`、搜索语义与评分逻辑。
- 不改任何界面文案文字（含免责声明、边界文案、措辞纪律）；index.html 文本节点 diff 必须为零。布局必需的结构性调整（如包裹容器）逐处在 REPORT 列出。
- 不引入任何框架、构建工具、网络字体或外部 CSS/JS 依赖；保持纯原生三文件部署。
- 不做深色模式（设计稿 T4，另行评估立项）；不做 P2 糖苷接入搜索、P4 图形编辑器/可缩放路线树、分子结构编辑器。
- 不把拓扑标注、文献关联等候选信息视觉升格：边界文案对比度按正文标准（≥4.5:1），禁止用弱化色降级免责声明。
- 不把原始或受限数据加入 Git；不 force push、不删除远端分支。挂载视图产生的 mode 位变化与 `._*` 元数据文件属挂载产物，不纳入任何提交。

## 执行顺序与阶段门槛

获批后可按 S1→S3 连续执行；阶段成功不能互相替代，触发停止条件即停。

### S1：设计 token、字体与对比度（纯 style.css）

- CSS 自定义属性落地：green/amber 50—900 双十级色阶、5 级中性灰绿、4 组语义色、字体刻度（1.25 比例 8 档，基字号 15→16px）、间距/圆角 token；收敛 7 种弱化绿散值与 14 档字号。
- 修正 4 组不达标配色为已验证色值；免责声明与边界文案按正文标准处理。
- 门槛：contrast_check 对设计文档 §2.1 全表通过；1440×1000 四页截图与基线并查，无版式破坏。

### S2：移动优先布局重构

- 断点翻转为移动基础 + `@media(min-width:768px/992px/1280px)` 渐进增强；废弃 900px max-width 覆盖。
- 以 `position:sticky` 侧栏替代 `body{overflow:hidden}` 方案，消除 iOS 滚动链隐患；页签窄屏横滑；触控目标全部 ≥44×44px；筛选器/stats/profile-grid/leaf-grid 窄屏规则按设计稿 §3。
- 门槛：320/375/768/992/1280 五档四页无横向溢出；既有 browser_check 全部断言不回归。

### S3：语义、键盘与微交互

- 页签 `role=tablist/tab/tabpanel`、`aria-selected/aria-controls`、←/→ 方向键循环；skip link；表格 `th scope`；搜索失败改 `role="alert"`；搜索进行中结果区骨架屏（`aria-busy`，仅 opacity 呼吸）。
- 按钮 hover/active 态（仅 transform/opacity，0.2—0.3s）；`prefers-reduced-motion` 全局关闭动画。
- 门槛：键盘全程走查记录（搜索→导出→切页→历史读取）；contrast_check 与五档溢出复测仍通过；JS 错误 0。

## 验收标准

- [x] 获所有者人工批准（human_direct）：2026-09-26“批准，执行”，范围为 S1—S3 全部。
- [x] style.css 文字配色全部经 token 变量引用；设计文档 §2.1 对照表逐组复测 ≥4.5:1（装饰/大字号 ≥3:1），证据存 outputs/validation/contrast-*。（34 组全过，`:root` 之外零硬编码 hex，2 项装饰豁免登记）
- [x] 断点为 min-width 写法；320/375/768/992/1280 五档四页无横向溢出，截图存档。（实际按合同工具扩展为含 390 的六档，24 项全 false）
- [x] 页签 tablist 语义 + 方向键 + skip link + th scope + 错误 role=alert 全部落地；键盘走查记录存档。（自动化断言固化于 browser_check.py）
- [x] 页签、复选框行、表格按钮、主按钮触控区域 ≥44×44px（验收脚本断言）。（实测 tab 100×44 / submit 352×48 / preview 82×44 / 复选框行 352×44 / rows-view 66×44）
- [x] 骨架屏与微交互仅 transform/opacity；prefers-reduced-motion 下无动画。（transitionDuration=0s 断言通过）
- [x] `diff -r web flavoretro/assets/web` 为空；index.html 文本节点 diff 为零。（109 既有节点零丢失，唯一新增为合同 S3 列明的 skip link）
- [x] 现有单元测试全部通过（数量不低于 TASK-012 基线 51 项）；browser_check 扩展断言通过且既有断言（拓扑边界文案、27 教学条目、15 文献卡、12-cell、历史运行不触发新 MCTS 等）全部不回归；JS 错误 0。（51 项 10.15s 通过；browser-7ff005c5 全绿）
- [x] REPORT-013 与 STATE 更新一致；偏差、失败截图与日志保留。（command-0182/0184 两次失败中间态已保留）

## 验证计划

本段为获批后的计划，实际执行以 REPORT-013 记录的 argv 为准；每条命令均以 `scripts/operate.py TASK-013` 包装，在 cano 项目环境执行。

```bash
python -B -m unittest discover -s tests -v
python -B scripts/contrast_check.py        # 设计文档 §2.1 全表复测
python -B scripts/browser_check.py         # 扩展后：5 档视口/键盘/触控目标 + 既有全部断言
diff -r web flavoretro/assets/web
git diff --check
# index.html 文本节点零变更核对（词级 diff，剔除空白与属性）
```

## 停止条件

- 未获所有者人工批准：只可补充审核材料，不得执行 S1—S3。
- 实现要求改后端/API/搜索语义/数据/文案内容，或必须引入外部依赖：停止，修订合同再审批。
- 现有单元测试或既有浏览器断言出现与本任务无关的失败：记录根因，不借机扩大修改。
- TASK-012 G5 未收口期间：本任务不执行 git 提交/推送，避免与 G5 交付交错；执行时机由所有者明确。
- 任一免责声明/边界文案对比度复测不达标，或视觉调整降低其可读性：停止并回退该处。
- 远端出现未经本 TASK 纳入的更新、身份/权限不符：停止一切同步操作（本任务默认不含同步）。

## 必须提交的报告

完成、部分完成或失败时，都必须生成 `docs/reports/REPORT-013-web-ui-design.md`，记录每阶段实际修改、验证证据、偏差与失败截图，并更新 `STATE.md`。

本任务即使完成，也不自动进入 T4 深色模式、P2—P5 阶段或任何证据晋级；下一阶段另行立 TASK，交所有者审核。

## 批准后执行记录

2026-09-26：所有者回复"批准，执行"，合同 S1—S3 获批，开始执行；上文 Proposed/待批准措辞为冻结历史。TASK-012 G5 已于同日收口（fab9659 已同步 origin/main）；本合同不含 git 提交/推送授权，工作区改动在验收后交所有者决定提交。

2026-09-26 执行完成：S1—S3 全部落地并验收——51 项单元测试通过（command-0187）、contrast 34 组全过且 `:root` 外零 hex（command-0183/0186，outputs/validation/contrast-cd2e7f75、contrast-ca9a2615）、浏览器全量验收通过（command-0189，outputs/validation/browser-7ff005c5：24 项视口溢出全 false、JS 0、12-cell 0 失败、既有断言零回归）、文本节点零变更（command-0185）。两处起草后修正：焦点指示改双环（原 3px 琥珀单环浅底实测约 2.2:1 不达 WCAG 2.4.11）、badge 窄屏裁剪因违反文本节点零变更验收回退（command-0184 失败态保留）。REPORT-013 已生成，STATE 已更新。未执行 git 提交/推送（合同未授权）。
