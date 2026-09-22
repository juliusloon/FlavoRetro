# ADR-004：教学与文献层迁入 configs/ 及 Web 四页信息架构

- 状态：accepted
- 日期：2026-09-22
- 负责人：Kimi（agent_delegated，TASK-010）

## 背景

- 旧项目 web 端有完整路线解读、教学解释模式（`config/product/teaching_guidance.json`，27 个反应家族条目）与文献教学层（`config/product/literature_teaching_layer.json`，15 张文献卡 + 反应课程），但新项目 web 端仅有骨架，且文献教学层在旧前端从未被渲染（旧后端有接口、前端未调用）。
- 新项目搜索响应已携带路线解读所需字段（cost 分项、closure、evidence_basis、structure_check、hazard、metadata.classification/template/policy_probability），教学文案可按 classification 在前端联查，无需改动搜索逻辑。
- 项目须独立于旧 `retro_synthesis` 存在：教学配置不入仓则工作台内容长期依赖旧目录。

## 决定

1. 两份教学配置文件从旧项目 `config/product/` **只复制不移动**入 `configs/`，SHA-256 登记入治理日志；作为项目原创内容纳入本项目许可框架（所有者 2026-09-21 许可决定覆盖项目原创文档与配置）。
2. `flavoretro/web.py` 新增两个只读 GET 端点（`/api/teaching`、`/api/literature-teaching`）原样透传配置；教学块在前端按 `metadata.classification` 联查、default 条目兜底。
3. Web 信息架构定为四页：路线探索（含路线解读与教学解释开关）、资源与证据、文献教学、项目状态。布局契约：顶栏固定；探索页双栏贴边且各自独立滚动。
4. 本阶段不移植 D3 树视图、JSME 编辑器、冻结快照、国际化字典与 PubChem 联查；列入 `docs/WORKBENCH_ROADMAP.md` 评估。
5. 界面措辞沿用候选语义：surrogate/partial、非实验验证等事实原样呈现，禁止升格（延续 ADR-002）。

## 备选方案

- **搜索响应内嵌 teaching（旧项目做法）**：每次搜索附带 31.6 KB 教学全文。放弃理由：新前端可一次拉取独立端点缓存复用，搜索响应保持瘦小；且不改 worker 符合 TASK-010 禁止项。
- **整体搬运旧前端（2400 行 app.js）**：放弃理由：旧前端绑定旧响应 schema（schema_version 2.0、verification、literature_overlap 等新后端没有的字段），整体搬运等于重写一半；在新三页架构上扩充更可控。
- **改 worker 让 classification 对齐教学家族键**：放弃理由：属于搜索语义改动，需独立 TASK 与冻结评测定义（见 WORKBENCH_ROADMAP P2/P3）。

## 影响与风险

- 教学条目命名家族键与现行模板数值 classification 之间存在映射缺口，前端 default 回退已正确标注；若未来更换模板库或接入家族策略（P2），须复审本映射。
- 两个端点无版本协商；配置扩充需同步前端字段假设（前端对缺字段跳过，兼容风险低）。
- 文献教学层含机器抽取内容，claim 政策横幅与逐卡 claim_status 为强制呈现，不得在未来 UI 改版中移除。

## 复审条件

- 黄酮苷有效性判断接入搜索（P2）或模板库更换时，复审教学联查键与端点契约。
- 文献教学层扩充（新增课程/文献卡）或引入版本化时，复审透传端点是否需要版本参数。
- 若引入 D3/JSME 等 vendor 依赖，复审许可登记（LICENSES/）与静态资源 allowlist。
