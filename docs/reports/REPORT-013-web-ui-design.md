# REPORT-013：Web 界面设计规范落地（移动优先、对比度与可访问性）

- 任务：docs/tasks/TASK-013-web-ui-design.md（所有者 2026-09-26“批准，执行”，human_direct）
- 执行日期：2026-09-26
- 执行者：Cano
- 结论：**完成**。验收标准全部勾选（见 TASK-013 文件）；合同覆盖的 S1—S3 已落地并通过全部工程验收。
- 范围纪律：仅改呈现层（web/ 三文件与打包副本、验收脚本）；未改任何 API、后端、搜索语义、数据与既有文案；既有文本节点零变更（证据见下文）；未执行 git 提交/推送（合同未授权），工作区改动待所有者决定。

## 实际修改

### web/style.css（全量重写）

- 设计 token 化：green/amber 50–900 双十级色阶、5 级中性灰绿、语义色、字体刻度（1.25 比例，基字号 15→16px）、间距/圆角变量，全部集中在 `:root`；7 种弱化绿散值收敛为 `--ink-2`/`--ink-3`/`--accent-text`；14 档字号收敛为 8 档；`font-weight:550` 废除。
- 对比度修正（实测值见 contrast 报告）：eyebrow #548370→#3F6B56（3.94→5.55）、note/intro #65776e→#4E5F56（4.33→6.18）、空态 #7c8d80→#5C6F60（3.20→4.91）、footer #789078→#5C6F60（3.16→4.91）。
- 移动优先重构：废弃 `body{overflow:hidden}` 与 900px max-width 覆盖；改为移动基础 + `min-width:768/992/1280` 渐进增强；≥992px 探索页双栏改为 sticky 侧栏（`--header-h` 由 app.js 实测写入），消除 iOS 滚动链隐患。
- 触控目标：页签/主按钮/预览/表格按钮/复选框行/表单控件 min-height ≥44px（主按钮 48px）；输入控件字号 16px 防 iOS 聚焦缩放。
- 微交互：按钮 hover 色深 + scale(1.02)、active scale(.97)（仅 transform/颜色，0.2s，`hover:hover` 且 `no-preference` 才启用）；骨架屏 opacity 呼吸；`prefers-reduced-motion: reduce` 全局 `animation/transition: none !important`。
- 焦点指示升级为双环（2px 墨色内环 + 4px 琥珀外环）：起草轮核查发现原 3px 琥珀单环在浅底实测仅约 2.2:1，不达 WCAG 2.4.11 的 3:1；双环在浅/深底均有 ≥3:1 的一侧（contrast 报告含两组证据对）。
- 装饰豁免两处（contrast 报告 `decorative_exemptions` 登记）：卡片/message 左侧 3px 强调条（2.24:1，组件由完整边框识别）、空态 60px 图形（纯装饰水印）。

### web/index.html（仅语义属性与角色，既有文本节点零变更）

- nav → `role="tablist"`；四页签 `role="tab"` + `aria-selected` + `aria-controls` + roving tabindex；四 section `role="tabpanel"` + `aria-labelledby`。
- 新增 skip link「跳到主要内容」（合同 S3 列明的新增控件，是唯一新增文本节点）；`<main id="main" tabindex="-1">`。
- 三个数据表 `th scope="col"`；三个 `.table-wrap` 加 `tabindex="0" role="region" aria-label`（可键盘滚动；aria-label 为新增无障碍属性标注，非可见文本）。
- 计划偏差点 1：设计稿 §3.1 的 badge 窄屏隐藏「· v0.1 ·」未实施——需要拆分文本节点，与合同“既有文本节点 diff 为零”冲突，已回退为原始单节点；窄屏 badge 随 header 自然折行。

### web/app.js（仅交互层）

- `activateTab()`：页签切换同步 `aria-selected`/tabindex/`hidden`；`nav` 上 ←/→/Home/End 键盘导航（focus 跟随）。
- 搜索提交：渲染 3 张骨架卡（`aria-hidden`）并置 `#routes[aria-busy=true]`，完成/失败清除；失败时 `#message` 改 `role="alert"`（样式联动 danger 配色），新搜索/历史读取恢复 `role="status"`。
- 新增 `--header-h` 实测写入（load/resize）。未改任何请求参数、API 调用与数据渲染逻辑。

### 验收脚本

- 新增 `scripts/contrast_check.py`：解析 style.css `:root`，复测 34 组配色对（正文 ≥4.5，装饰/大字号 ≥3），并守卫 `:root` 之外零硬编码 hex；输出 outputs/validation/contrast-*/report.json，失败退出码 1。
- 扩展 `scripts/browser_check.py`：保留全部既有断言（拓扑边界、真实双阶段搜索、参数、筛选、15 文献卡、27 教学条目、历史运行不触发新 MCTS、12-cell、429 门控、400/503 分支、JS 错误 0），新增：skip link 首焦点、tablist/tabpanel 语义、th scope、方向键切换、骨架屏与 aria-busy、触控目标 ≥44、role=alert、reduced-motion 无过渡、320/375/768/992/1280/390 六档视口四页横向溢出断言。

### 打包副本

- `flavoretro/assets/web/` 三文件已同步，`diff -r web flavoretro/assets/web` 为空。

## 验证证据

| 核查 | 结果 | 证据 |
| --- | --- | --- |
| 单元测试（cano，.venv-foundation） | 51 项全部通过、无跳过（含 2 个独立实时 MCTS、节点上限、来源保全、拓扑、教学端点），零回归 | operations/command-0187.log |
| contrast_check 本地 | 初跑 1 处失败（green-300 强调条 2.24:1<3.0，登记装饰豁免后修正检查表）；复跑 34 组全过、`:root` 之外零硬编码 hex | command-0182.log（失败证据保留）、command-0183.log；outputs/validation/contrast-cd2e7f75/ |
| contrast_check cano | 34 组全过、零漂移、2 项装饰豁免登记 | command-0186.log；outputs/validation/contrast-ca9a2615/ |
| index.html 文本节点核对 | 初跑标出 badge 拆分节点（已回退，见偏差）；复跑 PASS：109 个既有节点全部保留、零丢失，新增仅合同 S3 列明的 skip link | command-0184.log（失败证据保留）、command-0185.log |
| browser_check（cano，Chromium） | 既有断言全部不回归 + 新增 S2/S3 断言全过；JS 错误 0；6 档视口 24 项横向溢出全 false；触控目标全部 ≥44×44 | command-0189.log；outputs/validation/browser-7ff005c5/（report.json、各视口截图、export.json） |
| 打包副本一致 | `diff -r web flavoretro/assets/web` 为空 | 本报告；events.jsonl 对应写入记录 |
| git diff --check | 无空白错误 | command-0188.log |

浏览器验收关键值（browser-7ff005c5/report.json）：`live_search/two_phases/all_search_parameters` true；`resource_version` v3；27 教学条目、15 文献卡；历史读取前后运行总数不变（未触发新 MCTS）；12-cell 开发对照 development-71d874235766475b8810777da5767b38 完成、0 失败；并发门控 429、非法输入 400、引擎失败 fixture 503 分支均通过；`formal_run_ready` 仍 false。新增断言：skip link 首焦点、tablist/tabpanel 语义、`th` 无 scope 缺失、方向键循环切换并 focus 跟随、骨架屏 + `aria-busy` 出现/清除、失败提示 `role="alert"`、reduced-motion 下 `transitionDuration=0s`。触控目标实测：页签 100×44、submit 352×48、preview 82×44、复选框行 352×44、SMILES 352×124、表格查看按钮 66×44。

### 键盘走查记录

键盘覆盖以自动化断言固化于 browser_check.py（每次验收可重复执行）：首 Tab 聚焦 skip link；页签支持 ←/→/Home/End 并同步 aria-selected 与焦点；搜索→结果→导出→切页→历史运行读取的完整流程由既有断言覆盖。

## 界面通过验收不等于

工程验收通过不代表候选路线可执行、不代表化学有效性；`release_ready`/`formal_run_ready` 仍为 false（browser 报告已核）。所有免责声明与边界文案逐字未动、对比度按正文标准复测通过。

## 偏差与未做事项

- badge 窄屏「· v0.1 ·」裁剪未实施：实现需拆分既有文本节点，与合同“文本节点 diff 为零”冲突，已回退为原始单节点（command-0184/0185 记录全过程）；窄屏 badge 随 header 自然折行。
- 焦点指示从设计稿的 3px 琥珀单环改为双环（2px 墨色内环 + 4px 琥珀外环）：起草后实测单环在浅底仅约 2.2:1，不达 WCAG 2.4.11 的 3:1；双环在浅/深底均有 ≥3:1 的一侧。
- 两处装饰豁免（卡片/message 左侧强调条 2.24:1、空态 60px 图形）已登记于 contrast 报告 `decorative_exemptions`，非弱化任何文字信息。
- 本任务不含 git 提交/推送授权，未提交；macOS 挂载产生的 `._*` AppleDouble 文件与 mode 位噪音不纳入任何提交。
- 深色模式（设计稿 T4）、P2—P5 阶段不属于本合同，未动工。

## 执行记录摘要

- 全部写入经 scripts/operate.py TASK-013 记录（web/ 三文件、flavoretro/assets/web/ 三文件、scripts/contrast_check.py、scripts/browser_check.py、本报告与治理文档）。
- 命令日志：command-0182—0189（含两次保留的失败中间态：contrast 初跑、文本节点初跑）。
- 下一步由所有者决定：工作区改动是否提交推送；设计稿 T4 深色模式与 P2—P5 另行立 TASK 审核。
