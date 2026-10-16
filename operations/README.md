# operations/ 目录职责

- events.jsonl：追加式操作事件账，入 Git；旧行不改写。事件含 time/task/action/argv 或 path/前后 SHA。
- command-*.log：新命令输出仍写顶层；本轮归档的 6,364 份历史日志在 archive/command-logs/，文件名不变、本地保留、不入 Git。
- archive/：旧构建器/一次性脚本与历史命令日志，不作为活动 runtime。
- *-baseline.json / *-validation.json / *-exception.json、task016-p2…p8-original/、task016-p2-code-history/、history-before.json、usage-snapshot.json：历史基线/代码原件/核验，保留原位。
- task016-p9-draft-20261013/、task017-draft-20261013/：ADR-006/007 引用的草案决定。
- .staging-task011/、.staging-task012/：既有本地暂存，保留不提交。

## 日志定位

归档映射为旧 operations/command-NNNN.log → operations/archive/command-logs/command-NNNN.log。operate.py 使用当前顶层日志数量生成编号；归档后编号已复用，因此只凭文件名不能确定历史事件。按事件 time/task/argv 查出 write.after SHA，再在原位和归档候选中匹配哈希；不要覆盖或重编号历史文件。

已核实 6,360 份归档日志匹配归档前最新 write SHA；command-3737.log 匹配历史两个并发 write 中的一项（history_event_race_ambiguous），不能宣称最新账一致。command-1217/1220/1222.log 没有可用历史 write 事件，保留并标记未验证。

本轮续作使用 flock /tmp/flavoretro-task021-operate.lock 串行调用 operate.py，避免本轮代理同时分配同名日志；不修改被钉定的operate.py。命令不得用未启用 pipefail 的 tail 管道掩盖失败。只有 command_start、没有 command_end 的旧全量unittest尝试不作为通过证据；真实退出码未知。

记录与归档核验见 [TASK-021台账](../outputs/restructure/repo-consolidation-20261015/README.md)。所有项目命令/写入经 scripts/operate.py；不全局替换共享文件，不因重组重置科学预算。
