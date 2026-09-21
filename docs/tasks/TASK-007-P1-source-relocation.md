# TASK-007 补充：来源路径追溯修复
Cano agent_delegated 批准。最终审计发现 508 条 note source 文件名已由 YY-MM-DD 空格迁移为 YYMMDD-；旧原始 source 不改，新增映射与独立 v2。
复制历史 docs/literature 九份实际笔记；保存来源清单 v1 与资源构建器 v1；v2 记录文件定位、原反应 token 是否找到；两次重放一致后切换活动数据指针，旧 v1 保留。
理由：用户要求逐项核实来源；不能把能定位的实际文件永久标缺失，也不能只靠名称声称反应原文核验。
