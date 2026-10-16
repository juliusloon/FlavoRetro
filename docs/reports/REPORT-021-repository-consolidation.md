# REPORT-021 仓库全面盘点与精简重构

日期：2026-10-16（Asia/Shanghai）。执行与验收裁定：Cano，agent_delegated、human_reviewed=false。

**治理整理完成，存在已声明的历史验证例外。** 已完成全仓分类、非活动产物归档、目录索引与 STATE/PROGRESS/ARCHITECTURE 重构；原始全量 compileall 通过标准未达成，两个被冻结历史脚本语法错误原字节保留。有效验收细化在 [TASK-021续作批准](../../outputs/restructure/repo-consolidation-20261015/continuation-approval.md) 与 [合同附录](../tasks/TASK-021-repository-consolidation.md)，不把失败写成通过。

## 授权与执行范围

承接所有者“全面完整分析整个仓库……整理精简……统一重构”及本轮 continue this work。原代理通过 /Volumes/cano 挂载和 SSH 执行；本轮直接使用服务器 /home/ljx/FlavoRetro。未使用 CondRxnBench 运行环境或旧仓库可写权限。所有续作命令/写入经 scripts/operate.py，flock 串行记录避免本轮并发日志编号冲突。

G2决定沿用：原始/冻结证据和被路径+SHA钉定脚本保留；冗余阅读入口通过分组索引和归档分离，不合并历史运行代码或抹除失败。原G1/G2文件不回写；重构前STATE/ARCHITECTURE/PROGRESS/导航全文保存至 before-continuation/。本轮没有Git暂存、提交、推送、发布、来源检索、下载、MCTS或科研矩阵。

## 实际改动与交付

| 用户要求 | 具体交付 | 结果与边界 |
| --- | --- | --- |
| 全仓分析与分类 | [整理总入口](../../outputs/restructure/repo-consolidation-20261015/README.md)、G1原盘点、file-disposition.jsonl | 续作24,880实质文件逐项SHA/处置；虚拟环境、.git、工具私有状态、旁车、可再生缓存等排除范围显式记录，不声称逐行审读第三方环境 |
| scripts/py精简可读化 | [scripts索引](../../scripts/README.md)、script-catalog.tsv | 523顶层Python脚本逐项用途/角色/SHA/语法状态；522有引用台账，task020工具按报告溯源KEEP；保护脚本不物理搬动 |
| outputs整合 | [outputs索引](../../outputs/README.md)、分层架构、任务台账README | 版本、活动视图、旧结果/superseded/失败与新归档分开查阅；冻结outputs原路径/字节保留 |
| operations归档 | [定位规则](../../operations/README.md)、archive-verification.json | 6,364份历史日志迁入operations/archive/command-logs/；事件账仅追加，编号复用按时间/命令/SHA解析 |
| 临时/生成物分离 | archived/temp-scripts、flavoretro-web-report、trae-html-share-packages | 4临时脚本、11网页文件、1分享包保留归档；用户RDF/PDF与被报告引用中间件原位保留 |
| 历史草稿分离 | [报告档案](archive/README.md)、draft-link-relocation.json | pre-v38草稿移出正式层；原字节另存本地档案；阅读副本只重定位25个链接，科学文字保持 |
| 缓存精简 | cache-cleanup.json | 上轮build/.pytest_cache已清；续作删除3处__pycache__共583文件/5,322,020B，生成语法缓存放仓库外临时目录并清除 |
| 当前状态/进度/架构统一 | [STATE](../../STATE.md)、[PROGRESS](../../PROGRESS.md)、[ARCHITECTURE](../../ARCHITECTURE.md)、docs三类索引 | 当前状态与历史流水分离；补齐全部现有任务/报告/ADR入口，纠正过时TASK017审核与FutureHealth职责 |

归档主要减少顶层混杂，不以移动宣称磁盘空间大幅释放。data、运行模块、配置、测试、原脚本、旧科学/曝光/epoch账均未改字节。原始/受限材料、outputs与temp不入Git。

## 归档数量与保全等级

| 类别 | 文件/字节 | 已验证 | 保留限制 |
| --- | --- | --- | --- |
| 历史命令日志 | 6,364 / 70,119,072B | 前6,356份总大小70,119,033B与原盘点相等；6,360份匹配最新历史write SHA；1份匹配历史并发write中的一项 | 3份缺write事件；不宣称最新事件全量一致 |
| temp脚本 | 4 / 38,543B | 原位置缺失、归档位置存在、原盘点大小一致 | 移动前SHA未记录，不能证明逐字节前后相等 |
| 网页报告 | 11 / 4,320,843B | 原盘点逐文件大小一致、归档路径存在 | 同上，现SHA是续作取证 |
| 分享zip | 1 / 1,442,665B | 原盘点大小一致、归档路径存在 | 同上 |
| pre-v38原草稿 | 1 / 156,126B | SHA `5a4fe464791be11c5daa40c986c45ea098017b21d86ec99bb2af3b9acd37d6fe` 与2026-10-12原write事件相同 | 阅读副本链接调整另有SHA，不冒充原件 |

3份无write事件日志为command-1217/1220/1222.log。command-3737.log在2026-10-10两个相隔19微秒的write事件中分别登记当前内容和空文件SHA；当前文件匹配前一项，标记history_event_race_ambiguous，不判作本轮损坏，也不修写历史事件。移动首次命令返回1，随后SSH迁移返回0，失败过程保留。

原脚本引用清单524个名字中，__init__.py/custom_expansion.py不在当前scripts顶层；实际522/523。原G1 Markdown的temp=169与JSON明细168不符，按明细更正。原日志盘点6,356，迁移时新增8，因此实际归档6,364；不混用两个时点计数。

## 验证与验收

| 验收 | 事实 |
| --- | --- |
| 全仓分类/目录覆盖 | file-disposition.jsonl 24,880行；script-catalog.tsv 523正文脚本行；排除项目保留并显式登记 |
| 活动代码与路径 | 续作基线未发现脚本/模块/配置/测试字节变化或正文文件丢失；既有入口不改 |
| 冻结保护 | TASK017v2中scripts/flavoretro专项565正文文件SHA全部相等；40旧缺失AppleDouble旁车单列。此专项不是全TASK017919项检查；以前总体42缺旁车的历史结论未改 |
| 完整语法扫描 | CPython3.10.20检查585文件；flavoretro/、tests/通过；scripts/失败2份，原始全量compileall验收未达成 |
| 合同回归 | 直接执行 tests.test_contracts + tests.test_task017_formal，53/53通过，0skip，真实returncode=0；见test-verification.json及其日志SHA |
| 归档/导航 | 数量与已记录大小守恒；草稿25处新增断链已修；当前导航链接核验见final-verification.json |
| 续作完整性与Git | 24,880起点文件无丢失、无非授权字节变化；events既有前缀、Git HEAD和index不变；最终现场结果见final-verification.json |

两份历史语法失败分别是 scripts/task016_p7_progress_v9.py:65 和 task016_p7_ss_new_source_reconcile_v1.py:121；其SHA与TASK016-P9、TASK017v1/v2及教学调研保护基线一致。本轮保留，不运行/修复旧P7脚本。其余583文件语法通过，不能把此计数写成全585通过。检查包装命令在确认失败集合符合已批准例外后退出0，内部compileall scripts=false完整保存在syntax-verification.json。

本轮终验首轮因README链接指向尚未生成的final-verification.json而中断；先建立明确pending产物再完整重验，失败命令与日志保留。最终结果以该JSON的最终状态为准。

上一代理全量unittest discover仅有command_start、没有command_end，实际退出码未知；交接描述为超时，不能作为通过证据。本轮未重复可能触发真实本地MCTS的全量发现。53测试含合成门/结果fixture，不是新科学cell或独立化学验证。TASK017合同第288行两处原有材料相对链接错误保留冻结字节，当前docs导航提供正确入口。

## 当前项目位置与未处理事项

科研线保持research_candidate：活动v3与冻结审核视图承载3,059资源；糖苷扩展默认关闭。TASK016方法阶段结项，P7仍Partial/stopped，不恢复epoch；TASK017历史代理裁定完成、整体Partial，preparation_ready=true、research_run_ready=false、正式科学cell0、C/SS效果null、legacy formal/release=false。历史32卡全部development_exposed；25纳入/4领域排除/3证据不足不升级为fresh或gold，不再要求ljx逐卡重复审核。

教学代码位于FutureHealth，M0+P0交付状态沿用TASK020报告；后续治理仍在FlavoRetro登记。FutureHealth当前工作树本轮未重新检查。P1内容复制/教师审定、M1—M5不在范围。retro_synthesis/CondRxnBench/FutureHealth本轮均未触碰。

遗留为两个冻结历史脚本语法错误、3份日志缺事件、1份历史并发歧义、40项专项缺旁车、旧合同2处材料链接缺陷和原临时件移动前SHA缺证。均保留标记，不通过清理伪造完整性。Git仍有既有未提交交付；本地HEAD993b22f5，最近内容提交3361c07；本轮未查询远端，未同步。科研面板/协议与科学门、教学审定/发布和Git同步继续按各自合同单独取得授权。
