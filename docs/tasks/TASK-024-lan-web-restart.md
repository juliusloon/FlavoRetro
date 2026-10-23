# TASK-024：局域网Web重新挂起

- 日期：2026-10-22（Asia/Shanghai）。状态：Approved。
- 批准：agent_delegated；human_reviewed=false。
- 授权：用户明确要求重新挂起Web，并通过--host使同一局域网其他设备可访问。
- 范围与理由：核验本任务审阅服务所有权后，将127.0.0.1:8767的FlavoRetro重启为0.0.0.0:8767，以独立后台会话保留；登记PID、日志和局域网地址。不修改应用代码、历史数据、其他服务或防火墙。
- 验收：目标进程存活，ss显示IPv4全接口监听；本机loopback及两个实际物理网卡IPv4的页面与health均返回200；报告局域网URL。其他设备端到端访问仍须以实际设备结果为准。
- 停止：进程身份不符则不终止；端口被其他进程占用则停止并记录；启动失败保留日志并恢复可用服务。不执行MCTS搜索、不stage/commit/push。
- 记录：全部命令通过scripts/operate.py，文本用operate.write，本地证据outputs/task024，完成后更新REPORT、STATE、PROGRESS与索引。
