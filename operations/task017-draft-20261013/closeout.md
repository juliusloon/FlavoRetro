# TASK-017 合同编制交付记录

- 日期：2026-10-13；编制交付：Completed；正式TASK-017：Proposed，执行未批准。
- 批准溯源：agent_delegated，human_reviewed=false。所有者批准阶段分工与合同编制；完整指令和边界见scope_decision.json。
- 当前TASK-016按已交付模板、搜索接入及有限开发效果结项。该Completed不证明C/SS独立迁移成功；P7保持Partial/stopped，历史曝光、epoch与科学指标不变。
- 新合同：docs/tasks/TASK-017-independent-c-ss-transfer-benchmark.md。将C/SS独立面板、真实标签、来源/角色隔离、正式前置、冻结比较、真实MCTS、固定分母及结果边界集中为一次有界评价。
- 主要比较E=v6对A=generic；次要比较对B=合格v3。与旧P7/P9基线差异已明确，历史结果不混并。
- 有效正/零/负结果均可完成评价；缺面板、缺准入、未运行或关键无效结果不算Completed，正迁移能力另记effect_pass。
- 阶段长期决定见docs/adr/ADR-006-method-delivery-and-independent-evaluation.md；STATE、ARCHITECTURE、两份Roadmap及索引已同步，旧TASK/REPORT不回写。
- 验证：743个保护文件SHA未漂移；36个新增/变更局部链接有效；10项未来执行验收保持未勾选；源码、release、配置及既有交付保护保持。
- 本次科学读取、下载、标签生产、模板构建、代码实现、模型/MCTS运行均为0；无P7恢复、epoch重开、正式结果或REPORT-017生成，无Git提交/推送。
- operate记录命令共14次（含最终核验）。起始一次本地命令语法错误、随后一次核验对嵌套审计目录Git忽略状态的错误假设均已纠正，均未写入计划内容；失败日志保留。
- 本地审计目录未被现有Git规则忽略；只含治理记录/文档副本/哈希，不含新原始科学记录、结构或gold，也未暂存提交。未为此改动受保护的.gitignore。
- 本记录、verification与delivery_manifest是合同编制审计，不是正式评测REPORT。
- 后续须明确批准TASK-017执行，再按G0核对依赖及可达性；不从“写Task17”推导实验许可。正式门或独立面板不满足时按合同停止，不默认追加恢复。
