# FlavoRetro 协作规范
按 PROJECT.md → STATE.md → ARCHITECTURE.md → 当前 TASK 阅读。
流程：UNDERSTAND → SPECIFY → APPROVE → EXECUTE → VERIFY → REPORT → UPDATE STATE。
每个 TASK 执行前明确范围、理由、验收、停止条件；每次写入/命令以 scripts/operate.py 记录。TASK/REPORT 保存历史，STATE 只保存当前状态，ADR 解释长期决定，Git 保存代码版本。
历史 /home/ljx/retro_synthesis 与 /home/ljx/CondRxnBench 只读；不要在旧目录运行可能写缓存的代码。不得依赖旧库可写权限。
本次用户授予 Cano 自主审批权，批准记录写 agent_delegated，禁止伪装 human_reviewed。后续无新授权时须先取得 TASK 批准。
禁止将候选、数据库身份、图回放、工程测试、供应证据、独立化学验证混为一谈。
中文报告；最小充分变更；数据保留并标记；零不作为缺失。禁止把原始或受限数据加入 Git。
