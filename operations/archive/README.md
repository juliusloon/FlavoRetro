# operations/archive：一次性脚本归档

这里的脚本已完成其历史使命，**不是活动工具**：它们硬编码 `/home/ljx/retro_synthesis` 路径，只可在本机核对历史时使用。保留是为了溯源与可复核，修改活动代码勿参考此处实现。

| 文件 | 原位置 | 使命 | 关联 |
|---|---|---|---|
| `admit-task-002.py` | `scripts/admit.py` | 从历史项目只读复制 114 个文件并生成 `metadata/sources.json` | TASK-002 / REPORT-002 |
| `history_guard-task-001.py` | `scripts/history_guard.py` | 历史目录完整性基线快照与对比（`before`/`after` 两次运行） | TASK-001 / TASK-006 / TASK-007 |
| `resources-v1.py` | `flavoretro/resources.py` v1 | 资源构建器首版；被 v2（来源定位修复）替代后归档 | TASK-007-P1 |

用法示例（仅本机）：

```bash
.venv/bin/python -B operations/archive/history_guard-task-001.py before   # 建立基线（已执行过，勿重复）
.venv/bin/python -B operations/archive/history_guard-task-001.py          # 对比基线，退出码非 0 表示漂移
```
