# FlavoRetro Web 工作台界面设计规范（规划稿）

- 状态：SPECIFY 阶段交付物，待所有者人工批准后进入 EXECUTE（2026-09-25 起 TASK 须人工确认）
- 范围：`web/index.html`、`web/style.css`、`web/app.js`（打包副本 `flavoretro/assets/web/` 同步更新）
- 原则：**只改呈现，不改语义**。现有措辞纪律（候选不代表可执行、未知保持未知、边界文案同屏）全部保留，视觉升级不得弱化任何免责声明的视觉权重。
- 基线：移动优先、WCAG 2.2 AA、8px 基线网格、纯原生技术栈（不引入构建步骤，CSS 自定义属性即可满足 token 化）。

---

## 1. 现状功能实现分析

### 1.1 已实现能力（TASK-010/011/012 验收通过）

| 页面 | 功能 | 实现效果评估 |
|---|---|---|
| 路线探索 | MCTS 实时搜索、分子结构预览、糖苷拓扑标注、评分构成、末端原料证据卡、逐步反应卡、教学解释模式、JSON 导出 | 信息架构完整；桌面双栏贴边独立滚动是亮点；搜索长任务只有文本提示，无进度反馈 |
| 资源与证据 | 类型/关键词/QC/收率/来源五维筛选、分页、原始 JSON 查看 | 功能完整；筛选器在窄屏挤压；表格未做窄屏优化 |
| 文献教学 | 边界声明横幅、15 文献卡 + 1 课程、27 教学条目、拓扑关联跳转 | 内容分层清晰；卡片密度高、缺少视觉节奏 |
| 项目状态 | 统计块、基线状态、历史运行、12-cell 开发对照、预算配置卡 | 信息全面；stats 数字块视觉冲击弱；pre 块在小屏溢出风险 |

### 1.2 问题清单（按严重度分级）

**P0 · 阻断级（移动端基本可用性）**
1. **桌面优先写法**：基础样式是 360px 双栏网格，靠 `@media(max-width:900px)` 向下退化。与移动优先原则相反，且 900px 单断点无法覆盖平板横竖屏差异。
2. **触控目标不足**：复选框（`.check input` 约 16px）、`#preview` 按钮（padding 6px×12px，高约 30px）、表格内"查看"按钮均小于 WCAG 2.2 建议的 44×44px 最小触控区域。
3. **iOS 双重滚动隐患**：`body{overflow:hidden}` + `main` 内部滚动在桌面成立，移动端切换为 `overflow:auto` 后，探索页侧栏/结果区的滚动链在 iOS Safari 易出现橡皮筋冲突。

**P1 · 合规级（WCAG 2.2 AA 对比度不达标，实测值）**

| 元素 | 配色 | 实测对比度 | 要求 | 判定 |
|---|---|---|---|---|
| `.eyebrow`（11px 粗体小字） | #548370 on #f3f5f1 | 3.94:1 | ≥4.5:1 | 不达标 |
| `.note` / `.intro p`（12–15px） | #65776e on #f3f5f1 | 4.33:1 | ≥4.5:1 | 不达标 |
| `.empty` 空态文字 | #7c8d80 on #f3f5f1 | 3.20:1 | ≥4.5:1 | 不达标 |
| `footer` | #789078 on #f3f5f1 | 3.16:1 | ≥4.5:1 | 不达标 |

（其余 14 组关键配色实测均通过，含主按钮 6.58:1、hazard 红 6.66:1、导航 8.77:1。）

**P1 · 语义与结构**
4. **Tab 导航无语义**：四个页签是普通 `button`，缺少 `role="tablist"/tab/tabpanel`、`aria-selected`、`aria-controls` 与方向键导航；屏幕阅读器无法识别当前页签。
5. **无跳转链接（skip link）**：键盘用户每页都需 Tab 穿过整个导航。
6. **表格 `th` 缺 `scope`**；搜索失败提示仅用 `#message` 文本（`role="status"` 是 polite 级别，错误应为 `role="alert"`）。

**P2 · 体验级**
7. **配色无 token**：全部硬编码十六进制，同一语义多处散值（绿灰出现了 #557157/#507353/#5c6f60/#65776e/#697a6c/#789078/#7c8d80 七种近似但互不相等的"弱化绿"），无法统一维护，也无法支持深色模式。
8. **字体刻度散点**：11/11.5/12/12.5/13/14/15/16/17/18/23/30/38/60px 共 14 档，无比例体系；`font-weight:550` 非标准值可移植性差；中文字体栈未显式声明。
9. **零微交互**：按钮无 hover/active 反馈；长任务（MCTS 数秒到数分钟）无骨架屏或进度指示，仅一句静态文本。
10. **窄屏细节**：`.fields` 在移动端 `flex-basis:40%` 挤压下拉框；`td:first-child{max-width:300px}` 在 360px 屏过宽；stats 2 列在 320px 屏偏挤。

---

## 2. 设计基础

### 2.1 色彩系统（保留品牌基因，token 化，全部通过 AA 验证）

现有"墨绿 + 翡翠绿 + 琥珀金"与天然产物主题契合，**色相不变**，仅补齐色阶、修正对比度、统一散值。

**品牌绿（primary，围绕现 #246857 建阶）**

| Token | 色值 | 用途 |
|---|---|---|
| `--green-50` | #EDF4EF | 成功/中性浅底（替代现 #eef2ea/#edf2e9 等散值） |
| `--green-100` | #D7E8DE | 悬停浅底 |
| `--green-200` | #B3D3C2 | 边框强调 |
| `--green-300` | #86B8A0 | 装饰、图表 |
| `--green-400` | #5A9C80 | 图表次级 |
| `--green-500` | #35846A | 链接悬停（on white 4.51:1，仅用于 ≥14px 粗体或图标） |
| `--green-600` | #246857 | **主色**：按钮、链接（on white 6.58:1 ✓） |
| `--green-700` | #1D5446 | 按钮悬停 |
| `--green-800` | #173F35 | 深底上文字 |
| `--green-900` | #142C28 | 顶栏底色（保留现状） |

**琥珀金（accent，围绕现 #DBA849 建阶）**

| Token | 色值 | 用途 |
|---|---|---|
| `--amber-50` | #FDF8EC | 教学/提示浅底（保留现 #fbf6ea 区域） |
| `--amber-100` | #F7EDD7 | tag 浅底 |
| `--amber-200` | #EEE0BD | tag 边框 |
| `--amber-400` | #DBA849 | 焦点描边、强调图形（不作文字色） |
| `--amber-700` | #85601C | 琥珀底上的文字（on #F7EDD7 4.9:1 ✓） |
| `--amber-900` | #4A3510 | 深琥珀文字 |

**中性灰绿（neutral，收敛 7 种散值为 5 级）**

| Token | 色值 | 用途 | on #F3F5F1 对比度 |
|---|---|---|---|
| `--bg` | #F3F5F1 | 页面底（保留） | — |
| `--surface` | #FFFFFF | 卡片 | — |
| `--field` | #FAFCF8 | 输入框底（保留） | — |
| `--border` | #DAE3D9 | 卡片边框（保留） | — |
| `--border-strong` | #C9D7CC | 输入框边框（保留） | — |
| `--ink` | #172C28 | 正文（保留，13.41:1 ✓） | 13.41:1 |
| `--ink-2` | #4E5F56 | **次级文字**（替代 #65776e/#557157） | 6.18:1 ✓ |
| `--ink-3` | #5C6F60 | **弱化文字下限**（替代 #789078/#7c8d80，footer/空态/辅助说明） | 4.91:1 ✓ |
| `--accent-text` | #3F6B56 | eyebrow/小标签绿（替代 #548370） | 5.55:1 ✓ |

**语义色（沿用现有合格色，正式命名）**

| 语义 | 文字 | 底色 | 对比度 | 用途 |
|---|---|---|---|---|
| danger | #8F2D2D | #FBE3E3 | 6.66:1 ✓ | hazard 标记、错误 |
| warning | #85601C | #FBF6EA | 6.25:1 ✓ | 教学提示、待复核 |
| info | #2D4A8F | #E8EEFB | 7.26:1 ✓ | 拓扑标注 |
| success | #246857 | #EDF4EF | 6.58:1 ✓ | 闭合、已核查 |

**墨绿底上的文字**（顶栏）：主文字 #EEF7ED（保留）；次级 #B8CCC3（8.77:1 ✓ 保留）；琥珀强调 #E3B45C（7.71:1 ✓，替代 #DBA849 用于深底）。

### 2.2 字体系统

**字族**（两族，不加网络字体，保持零依赖）：

```css
--font-sans: system-ui, -apple-system, "PingFang SC", "Hiragino Sans GB",
             "Microsoft YaHei", "Noto Sans SC", sans-serif;
--font-mono: ui-monospace, "SF Mono", "Cascadia Mono", Consolas, monospace;
```

**刻度**（1.25 比例，8 档收敛现有 14 档；基字号 15→16 提升小屏可读性）：

| Token | 大小/行高 | 用途 |
|---|---|---|
| `--text-xs` | 12px/1.5 | 辅助说明、tag、元信息 |
| `--text-sm` | 14px/1.55 | 次要正文、表格 |
| `--text-base` | 16px/1.65 | 正文、表单控件（≥16px 可避免 iOS 聚焦自动缩放） |
| `--text-lg` | 18px/1.5 | h2、卡片标题 |
| `--text-xl` | 20px/1.4 | 区块标题 |
| `--text-2xl` | 25px/1.3 | h1（移动端） |
| `--text-3xl` | 31px/1.25 | h1（平板） |
| `--text-4xl` | 39px/1.2 | h1（桌面） |

字重只用 400/600 两档（600 用于标题与 label；废弃 550/700 散值）。h1 保留 `clamp()` 流式：`font-size: clamp(25px, 1.2rem + 2vw, 39px)`。SMILES/代码继续用 `--font-mono` + `overflow-wrap:anywhere`。

### 2.3 间距与栅格

8px 基线：`--space-1:4px … --space-6:24px --space-8:32px --space-12:48px --space-16:64px`；页面左右留白 `clamp(16px, 4vw, 48px)`；卡片 padding 桌面 24px → 移动 16px。圆角三级：控件 8px、卡片 12px、徽章全圆角。

### 2.4 断点（移动优先，min-width 渐进增强）

| 断点 | 宽度 | 行为 |
|---|---|---|
| base | 0–767px | 单列文档流；页签横向滚动条；表单全宽；stats 2 列；筛选器纵向堆叠 |
| `--bp-md` | 768px | 筛选器两列；文献卡双列网格；stats 4 列 |
| `--bp-lg` | 992px | **探索页恢复双栏工作台**（侧栏 `clamp(320px,28vw,400px)` + 结果区独立滚动）；顶栏单行 |
| `--bp-xl` | 1280px | 非探索页最大内容宽 1200px 居中；leaf-grid 增至 3–4 列 |

旧 900px 断点废弃；CSS 结构从"桌面基础 + max-width 覆盖"翻转为"移动基础 + min-width 增强"，可删除约 40% 的覆盖规则。

---

## 3. 移动优先布局方案（逐页面）

### 3.1 顶栏与导航（四页共用）

- **base（≤767px）**：第一行 brand + badge（badge 可折行隐藏"· v0.1 ·"段）；第二行页签栏 `overflow-x:auto` 横滑，四个页签 `white-space:nowrap`，当前页下划线 + 底色双通道标识（不仅靠颜色）。页签触控高度 ≥44px。
- **≥992px**：恢复单行（brand 左、nav 中右、badge 尾）。
- 页签语义化：`nav[role=tablist]`、`button[role=tab][aria-selected][aria-controls]`、各 `section[role=tabpanel][aria-labelledby]`；支持 ←/→ 方向键循环切换（JS 约 15 行）。
- 新增跳转链接：`<a href="#main" class="skip-link">` 聚焦时可见。

### 3.2 路线探索页

- **base**：单列文档流——intro → 目标分子表单卡 → 结果区。表单卡内：示例选择 → SMILES（`rows=3`，`font-size:16px` 防 iOS 缩放）→ 预览图（`height:auto; max-height:200px`）→ 拓扑块 → 预算/种子（`grid-template-columns:1fr 1fr`，320px 屏降为 1 列）→ 复选项（label 整行可点，触控区 ≥44px）→ 实验参数 `<details>` → 主按钮（高 48px 全宽）。
- **≥992px**：恢复现有双栏贴边独立滚动，侧栏 `position:sticky` 方案替代 `body overflow:hidden`（消除 iOS 滚动链问题：body 永不 hidden，侧栏 `position:sticky; top:header高; max-height:calc(100vh - header)` 自滚动）。
- **搜索进行态**：结果区显示骨架屏（3 张路线卡轮廓，`aria-busy="true"`），`#message` 保留文本；按钮进入"搜索中…"禁用态。骨架屏 shimmer 动画仅 `opacity` 呼吸（0.5↔1，1.2s），`prefers-reduced-motion` 下静止。
- **路线卡**：评分构成折行优化（`.formula` 独占行）；leaf-grid `repeat(auto-fill,minmax(min(230px,100%),1fr))` 防 320px 溢出。

### 3.3 资源与证据页

- **base**：五个筛选器纵向堆叠全宽；≥768px 两列；≥992px 一行。
- **表格**：`.table-wrap` 保留横滑，增加 `position:sticky; left:0` 冻结首列（记录名）；`td:first-child{max-width:min(300px,60vw)}`；`<th scope="col">` 补齐。
- "查看"按钮触控高 ≥44px（视觉尺寸可用 padding 8px 16px + 上下透明点击扩展）。

### 3.4 文献教学页

- **base**：banner → summary chips → 目录 `<details>` → 文献卡单列；≥768px 文献卡 `grid-template-columns:1fr 1fr`。
- `.kv-table th{width:auto; min-width:8em}` 替代固定 220px（窄屏挤压正文列）。
- 教学条目 `.teaching-entry` 增加 anchor id，支持拓扑 chips 跳转后 `:target` 高亮（琥珀左边框 2s 淡出）。

### 3.5 项目状态页

- stats：base 2 列 → ≥768px 4 列；`.stat b` 用 `--text-3xl`，数字与标签增加 8px 间距。
- 历史运行/开发对照表格同 3.3 的横滑 + 首列冻结；`pre` 块 `max-height:50vh` + 字号降至 `--text-xs`（12px）。
- profile-grid：base 1 列 → ≥768px 2 列 → ≥1200px 4 列（3 预算 + 1 全局）。

---

## 4. 组件状态与微交互规范

| 组件 | 状态 | 参数 |
|---|---|---|
| 主按钮 | hover | `background: var(--green-700); transform: scale(1.02)`，0.2s ease-out |
| | active | `transform: scale(0.97)` |
| | disabled | `opacity:.55`（保留），加 `aria-disabled` |
| | focus-visible | `outline:3px solid var(--amber-400); outline-offset:2px`（保留现有优秀方案） |
| 次级按钮 | hover | `border-color: var(--green-300); background:#fff` |
| 页签 | hover | 底色 green-50；active 下划线 3px green-600 + 文字 green-800 |
| 卡片 | hover（可点卡） | `transform: translateY(-2px)` + 边框加深；非可点卡不动 |
| 链接 | hover | underline + green-700 |
| 骨架屏 | loading | opacity 呼吸 0.5↔1，1.2s ease-in-out infinite |

**约束**：仅动画 `transform`/`opacity`；时长 0.2–0.3s（骨架屏除外）；`@media (prefers-reduced-motion: reduce)` 全局关闭动画与过渡；不用纯颜色传达状态——closure/hazard/拓扑 tag 均已含文字标签，保持。

---

## 5. 无障碍检查清单（WCAG 2.2 AA，验收用）

1. [ ] 全部正文/小字对比度 ≥4.5:1（按 §2.1 token 表逐组复测，重点：eyebrow、note、footer、empty）
2. [ ] 页签 `role=tablist/tab/tabpanel` + `aria-selected` + 方向键导航
3. [ ] skip link 首个可聚焦元素，聚焦可见
4. [ ] 全部可交互元素触控区 ≥44×44px（复选框 label、表格按钮、页签）
5. [ ] 表单错误用 `role="alert"`；进行中状态 `aria-busy` + 保留现有 `aria-live="polite"` 区域
6. [ ] 表格 `th scope`；`.table-wrap` 横滑区域 `tabindex="0"` + `aria-label`（键盘可滚动）
7. [ ] `prefers-reduced-motion` 下无动画；焦点顺序与视觉顺序一致
8. [ ] 输入框字号 ≥16px（防 iOS 自动缩放）；`<select>` 同上
9. [ ] 免责声明/边界文案对比度按正文标准（≥4.5:1），不得使用弱化色降级
10. [ ] 键盘全程可走通：搜索 → 结果 → 导出 → 切页签 → 历史运行读取

---

## 6. 实施路线（建议 TASK 拆分）

| 批次 | 内容 | 风险 | 验收 |
|---|---|---|---|
| T1 · token 与对比度 | CSS 变量落地；4 组不达标配色修正；字体刻度收敛 | 低（纯 CSS） | §5-1 复测全过；视觉回归截图比对 |
| T2 · 移动优先重构 | 断点翻转为 min-width；sticky 替代 body overflow:hidden；逐页窄屏优化 | 中（布局重写） | 320/375/768/992/1280 五档真机或模拟器验收；32+ 项单元测试不回归 |
| T3 · 导航语义与微交互 | tablist 语义、skip link、方向键、按钮状态、骨架屏 | 低 | §5-2/3/4/10 键盘走查 |
| T4 · 深色模式（可选，独立评估） | `prefers-color-scheme` 暗色 token 映射 | 中 | 暗色下对比度复测 |

每批次独立 TASK 合同（范围/验收/停止条件）→ 所有者人工批准 → operate.py 全程记录 → REPORT + STATE 更新。T2 完成后同步更新 `flavoretro/assets/web/` 打包副本并复跑浏览器验收。

---

## 7. 明确排除项（本次不做）

- 不引入任何框架/构建工具（保持纯原生三文件部署）。
- 不改任何 API、搜索语义、措辞文案与免责声明内容。
- 不做分子图形编辑器与可缩放路线树（WORKBENCH_ROADMAP 既定未就绪项）。
- 不把拓扑标注、文献关联等候选信息做视觉"升格"（如改色弱化边界文案）。
