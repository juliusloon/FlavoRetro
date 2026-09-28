# 领域筛选与评测协议

本目录属于 TASK-014/015 的定义、覆盖实测与接管层，全部为中文原创规范，原始/受限数据载荷保存在本地 outputs/triage/。任务完成不等于独立化学确认。

| 文件 | 职责 |
| --- | --- |
| [DOMAIN_TRIAGE_V1.md](DOMAIN_TRIAGE_V1.md) | 黄酮总分类、糖苷重点、guide 身份、标准化/去重和优先级规则；工程冻结、化学待校准 |
| [ANNOTATION_EVALUATION_V1.md](ANNOTATION_EVALUATION_V1.md) | 人工字段、60 条校准审核设计、独立标签与盲测隔离、三个评测层次和正式门槛 |
| [SOURCE_ACCESS_SURVEY.md](SOURCE_ACCESS_SURVEY.md) | 官方公开资料的接入调查，区分已核查资料与未验证机构权限 |
| [ORD_COVERAGE_V1.md](ORD_COVERAGE_V1.md) | TASK-015 当前镜像 53 源全量核验、严格候选/糖苷/重合、工程复核与局限 |
| [SCIFINDER_TARGETED_IMPORT_V1.md](SCIFINDER_TARGETED_IMPORT_V1.md) | 60 卡使用、4 条首批材料、用户导出/原件接收和科学审核分工 |

执行入口：从仓库根目录运行以下命令，输出目录必须不存在；需要活动 v3 本地资产与 .venv-foundation。

```bash
python -B scripts/operate.py TASK-014 .venv-foundation/bin/python -B scripts/triage_reactions.py --output outputs/triage/new-run
```

模块 flavoretro/triage.py 只做离线筛选，不调用 MCTS。configs/domain_triage.json 与包内 assets/configs/domain_triage.json 是逐字节相同的 v1 规则；不加入 runtime 的配置 allowlist，也不影响 CLI/API 搜索参数。

输入：508 条笔记候选与 2,301 条 SciFinder 导出。输出：guide/pilot 全量 JSONL、两策略队列、精确去重、防泄漏分组、未填写的审核 JSONL/TSV、机器统计、规则与 manifest，以及 audit.ipynb 独立核查笔记本。详细文件职责见运行目录 README.md。首次开发构建 task014-v1 原样保留，最终活动交付使用 task014-final，task014-replay 为独立重放核查。

审核：复制 review.tsv 到新的版本化审核目录后填写。它是开发校准包，机器建议可见；用于独立 gold/盲标的包必须另按协议生成并隐藏建议。本轮不执行人工化学审核、不创建盲测集。下一任务由所有者决定，不自动开始。

TASK-015 覆盖、60 卡代理审核及九个用户 SciFinder RDF 接收已完成，分别见 REPORT-015、REPORT-015-P1、REPORT-015-P2。结果是开发候选与来源线索；实际独立人审/标签接管须另立版本，不能编辑 TASK-014 冻结 review。原始载荷不上 Git、科学标签不自动晋级。

[SCIFINDER_SEARCH_TASK015_P1.md](SCIFINDER_SEARCH_TASK015_P1.md)：60条代理审核后的精准查询词、实例缺口与材料接收格式；更新此前要求用户初筛60卡的工作分工。
