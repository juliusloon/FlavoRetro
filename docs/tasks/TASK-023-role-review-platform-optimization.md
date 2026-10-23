# TASK-023：三角色试用评审与平台优化

- 日期：2026-10-22（Asia/Shanghai）
- 状态：Approved / In Progress
- 批准：agent_delegated；human_reviewed=false。
- 授权依据：本轮用户明确要求设计有机合成化学家、高校有机化学教师、Web交互设计师三个子agent，使用本平台给出意见并优化；AGENTS授予本轮Cano自主审批权。

## 范围与理由
三个角色独立操作本机FlavoRetro，基于实际界面和数据提出有复现路径的意见；主代理统一筛选、实施最小充分的界面/教学衔接优化。保留既有未提交改动、搜索语义、历史冻结文件与所有科学门。角色输出只属agent_delegated模拟专家评审，不代表真实化学家/教师认证。

## 验收
1. 三份角色定义、任务场景、实际试用证据、问题优先级及建议；共享代码由主代理修改。
2. 实施各角色交集及优先问题，教学化学说明须能回到已有证据；缺失/零/冲突/候选标记保留。
3. 两份web资源逐字节同步；必要针对性测试与桌面/手机浏览器交互通过，记录console/pageerror和search POST数。
4. REPORT、STATE、PROGRESS与导航更新，记录未采纳建议及局限；不stage/commit/push/部署。

## 执行与边界
读取现有保存run和来源/教学材料，主代理启动本机测试server；本TASK真实MCTS预算为0（避免改变搜索/计费历史），不恢复TASK022句柄。Browser plugin not available，使用已有Playwright；各agent独占outputs/task023/<role>/。所有命令经scripts/operate.py，写入用operate.write/登记SHA；截图/QA产物依AGENTS本地留证不入Git。先保留活动web源码、当前文档和相关配置前像，后执行修改。三个agent不修改共享代码、不启动服务器、不运行大范围/科研测试。

## 停止条件
发现来源与结构不匹配则保留并停止该内容扩写；历史SHA漂移不回写追认；端口/运行环境不可用则记录后修复独立问题；同类三次无进展换策略。无证据不编造机理、收率、教师认证或化学可行性。
