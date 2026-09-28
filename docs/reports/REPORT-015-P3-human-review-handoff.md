# REPORT-015-P3：60 卡人工复核包交付（阶段 1）

对应 [TASK-015-P3](../tasks/TASK-015-P3-human-review-handoff.md)。所有者选择方案 A 后，Cano 已完成可独立打开的本地审核交接包；本报告仅覆盖阶段 1。实际所有者审核文件尚未回传，后续缺口裁决及 gold 冻结尚未执行，TASK 状态为 AwaitingUserReview。

## 交付

本地入口：`outputs/review/task015-p3/handoff-v2/index.html`，使用说明同目录 `README.md`，可表格查看的逐卡缺口表 `gap_register.tsv`。页面包含全部 60 个固定 ID、原反应结构、TASK-015-P1 代理结论/证据/缺项和 P2 新 RDF 的严格结构、反应号、仅文献线索三种连接；30 条糖苷重点被标记，13 条争议/否决/来源异常列为 P0，另 25 条为 P1、22 条为 P2。优先级仅影响审核顺序，不决定科学标签。

每卡由实际审核者选择「同意代理判断 / 更正 / 暂存疑 / 排除」，分别勾选亲自核对过的结构分类、一手原文实例、条件/收率；勾选原文/收率必须提供具体定位/说明。更正、存疑、排除必须给出理由。浏览器本地保存草稿，可导入、导出带固定 ID、源 SHA、版本、逐卡审核者/时间和修改历史的 JSON。导出统一为 `human_submission_pending_validation`，不写入 `human_reviewed` 或 gold。空白包中的人审字段均为空。

`gap_register.tsv` 按卡号列出代理需要补的材料、用户问题及新 RDF 连接；其中的空白人工列便于表格查漏，但正式交接应使用页面导出的 JSON。页面和载荷含受限数据库衍生材料，保存在 Git 忽略的 `outputs/`；代码、合同和报告不含原始 RDF。不改 TASK-014 冻结样本、P1 代理审核、P2 接收、v3、active 或 MCTS。

## 验证

首版 v1 的自动初次渲染会把页面滚动到卡片，视觉复核发现页首说明不在初屏。保留 v1 作为失败记录，修正后交付 v2；v2 首屏滚动为 0，桌面和手机截图保存在本地验证目录。


生成器 `scripts/build_task015_p3_handoff.py` 校验 TASK-014 原 60 卡空白人审、P1 代理审核 60 ID、P2 交叉表 60 ID 同序，并冻结三份输入的 SHA-256。独立浏览器检查 `scripts/check_task015_p3_handoff.py` 在托管环境通过：60 ID/源及输出哈希、0/60 初始人审、P0/P1 筛选、结构 SVG、保存与刷新恢复、JSON 导出/导入、错源哈希拒绝、1440/390/320 像素无横向溢出、JS 错误 0。合成填写只在 `outputs/validation/task015-p3-handoff-v2/` 中标记 `BROWSER TEST ONLY`，不代表所有者审核。

## 下一阶段门槛

等待所有者按 README 审核并提供导出的 JSON 路径。收到后 Cano 将校验 60 ID/哈希/实际审核者/逐卡字段，依据更正与缺口做来源/结构复核，给每个标签轴明确 verified / uncertain / excluded；合法无法取得的证据保留未核实，不用题名或数据库身份填补。最后交所有者确认闭环，再冻结**开发** gold 的证据合格子集。60 条均为 `development_exposed`，即便完整人审也不会变成未见盲测；正式 benchmark、生产准入及公开发布仍属其他任务。
