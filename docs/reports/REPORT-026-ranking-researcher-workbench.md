# REPORT-026：MCTS 路线精细排序与研究者界面

日期2026-10-23（Asia/Shanghai）；状态Completed；批准agent_delegated，human_reviewed=false。对应[TASK-026](../tasks/TASK-026-ranking-researcher-workbench.md)及[首跑自检纠偏](../tasks/TASK-026-P1-duplicate-leaf-ranking-correction.md)。用户要求五项均已执行：细化原MCTS评分、去除开发展示、降序排序、横向路线、芦丁实跑/自检/建立新TASK。计算完成不意味着化学项目已完成。

## 交付

| 用户需求 | 当前结果 |
| --- | --- |
| 原MCTS基础上优化rank | research-priority-v2连续研究优先级同时参与optimized真实回传和最终排序；原UCT/PUCT、过滤、精确库存身份与节点硬限保留。native搜索回传保持原行为。先完整提取全部实际前沿、结构去重、评分，再选top_k；不再先截25条。全部候选的全精度分数、组成和排名保存在candidate_ranking。 |
| 去除233.9s及开发raw展示 | 全站删除墙钟/搜索耗时、树节点统计、内部类、代码指纹、manifest、原始JSON与工程评测/安装/CI/冻结批次面板。资源/文献/教学/反应详情按明确科学字段展示结构、条件、收率、位置、冲突与来源链接；研究范围页只呈现适用范围和资源覆盖。底层原件和导出保留。 |
| 降序排列 | 新运行服务返回降序；网页也按当前优先级排序。历史只重排当时已保存路线，独立research_ranking展示投影保留原result/manifest及导出。 |
| 路径横排 | 目标→中间体→末端从左向右；多前体垂直分支；每步依据位于箭头，全部步骤编号唯一连续。桌面/手机在图内横滑，页面无横向溢出；键盘路线目录Home/End通过。 |
| 芦丁与后续TASK | 2次受控真实HTTP请求：首跑发现评分设计偏差，批准补充后纠偏并第二次验证；原首跑未覆写。最终自检和TASK-027已交付，TASK-027为Proposed、尚未执行。 |

评分使用唯一末端结构的库存覆盖35%、前体简化25%、模型先验25%、路线简洁15%，已知危险/未指定立体额外扣分。候选闭合60–100分，未闭合低于60；不是成功概率。未知危险不被认证安全，真实0和缺失概率分开记录；同分保持真实并列，不作随机抖动。细节见[ADR-010](../adr/ADR-010-continuous-research-ranking.md)。

## 芦丁实跑及自检

最终记录`20261022T174437-5016438cb8164927a1f954fe9cd4c484`，当地日期2026-10-23；UTC run ID从20261022开始是时间表示差异。请求为网页示例芦丁精确结构、optimized通用模型、seed0、默认balanced两阶段、显式审核候选库存、top_k25；糖苷/文献/黄烷酮扩展均未开启，未扩大库存或隐藏开启ZINC。完整请求和绑定见outputs/task026/rutin-request.json及outputs/runs/20261022T174437-5016438cb8164927a1f954fe9cd4c484/。

| 核查项目 | 最终实测 |
| --- | --- |
| 实际MCTS及回传 | 两阶段均search_repaired.SearchTree；连续回传分别100/800次；没有缓存或BFS替代 |
| 前沿与候选 | 3545条实际前沿，结构去重后2929条全部排序，展示25条 |
| 评分区分度 | 同一最终候选集合的旧整数成本26档；当前全精度2260个不同值，四位小数2225个；仍有552组真实并列 |
| 展示分数与步数 | 15.1635–25.5484；3–8步 |
| 候选闭合 | 全部2929条中0；展示25条中0 |
| 来源支持 | 展示路线共126次步骤出现（跨路线有重复），当前审核库来源实例支持0；不能解释为全球文献中不存在这些反应 |
| 思路重复 | 前25有5组不同根前体组合，重数[12, 2, 8, 1, 2]；51个不同结构反应签名。结构组合数不是机理/合成思路数 |
| 末端与结构 | 所选叶25个唯一完整键，逐叶库存匹配与结构解析均通过；22个不同未解决结构；未指定叶立体中心0，但未独立验证已指定立体是否正确 |
| 身份与原件 | 实际代码SHA/请求/结果与保存manifest一致；历史导出逐字段等于原result，原文件SHA不变 |

首跑v1执行正常，2977候选/2288种分数，但重复乙酸酐末端会提高库存覆盖，违反设计意图。已保存原结果、原代码及自检并标记execution_ok / ranking_invariance_failed；v2按规范化完整立体结构去重计算覆盖/负担，真实图和投料重数不删除，重复投料仍计路线代价。新增变形测试证明同一未解决结构及同一唯一库存集合下，重复库存不提高覆盖，延长路线降低分数。第二次搜索轨迹不同，不能把候选数减少或本例排序变化称为独立算法/化学提升。

## 距离项目目标的差距

本轮解决了“无法细分/排序候选”和网站研究信息过载；芦丁仍只能提供未完成计算假设，不能给出可执行合成方案。高分路线中出现多步保护/脱保护及糖基溴供体等未解决末端，第一名仍为5步未闭合路线：槲皮素/乙酸酐可命中候选库存，但剩余糖供体需要继续规划。并未验证其保护方案、制备条件、区域/异头选择性或当前供应；不能把结构解析成功、无未指定立体或数值高分当成这些证据。

差距可明确为三个未通过的实用门：有效思路多样性和保护基逻辑未验证；关键糖供体子路线尚未闭合；步骤与条件尚无本次来源链支持。当前无法给出有依据的“完成百分比”，也不能从单个已曝光目标推断泛化。下一阶段应优先解决化学覆盖与路线有效性，再做独立参考下的排序校准。

已建立[TASK-027：芦丁有效路线、糖供体闭合与评分校准](../tasks/TASK-027-rutin-actionable-route-quality.md)，分P0逐步诊断、P1一手来源/供体准入、P2保护基与近重复路线约束、P3三臂开发对照。参考路线必须保留真实活化/保护/立体，缺失不补0；现有TASK017独立科研门不降低。仅建立合同，不启动后续预算。

## 验证与证据

环境：Linux / 现有Python3.10 / Playwright1.63 Chromium；Browser plugin not available，采用已有Playwright。访问http://127.0.0.1:8767/，桌面1440×1000及手机390×844。测试流程为历史→芦丁结果→目录切换/步骤展开/横滑→资源分页和详情→文献/六步/反应来源→研究范围→A/B与原始导出。

| 检查 | 结果 |
| --- | --- |
| 页面身份、非空、无框架错误遮罩 | 通过 |
| 控制台warning/error及pageerror | 最终检查0 |
| 截图与交互 | 桌面/手机截图已目视；局部横滑、面板切换、分页、学习与来源可用 |
| 研究字段清理 | 资源与全部32文献/18案例/54反应展开扫描，无开发哈希、内部路径、原始JSON与审批布尔字段；科学条件保留可读中文标签 |
| 历史与导出 | 最终芦丁与旧20261021保存运行的原始JSON导出一致、SHA不变；当前排序投影正确；全6步学习导出保留 |
| 回归 | 57项相关测试通过；含11项新排序行为/真实节点回传/历史只读测试、原搜索/精确库存/运行时/Web/包镜像测试 |
| 工程 | 6个活动Python模块/测试AST、Node语法、前端3镜像及diff检查通过；最终运行Python指纹等于当前文件 |
| 真实请求 | 2次均终态，预算已用尽；浏览器验证POST0；无待恢复搜索，不启动旧TASK账 |

主要命令均经scripts/operate.py TASK-026：`python -m unittest tests.test_ranking tests.test_search_repaired tests.test_search tests.test_stock_identity tests.test_task022_runtime tests.test_web tests.test_web_foundation tests.test_pipeline_presentation tests.test_package`（实际使用.venv-foundation/bin/python -B）、node --check、浏览器与audit_rutin_v2。首次浏览器脚本在手机保留详情状态时等待隐藏记录按钮失败，修正先点击资源记录；一次Playwright参数签名错误和一次误用系统Python均保留失败日志并修正环境/调用，不追认失败为通过。治理脚本两次参数/恢复校验错误也留日志；web.py漏存前像已从精确变更逆推并匹配原操作before SHA恢复。

证据位于outputs/task026/：before/及pre-v2/原件，rutin-http-result[-v2].json、rutin-self-review[-v2].json、rutin-quality-gaps.json、duplicate-leaf-correction-offline.json、browser-preflight.json、browser-final[-v2].json、browser-export-compatibility.json、final-verification.json和service-v2.json。截图在仓库外/tmp/flavoretro-task026/rutin-desktop-v2.png与rutin-mobile-v2.png。原始/受限数据、outputs/temp均不入Git；没有stage/commit/push。

当前后台PID3460415监听0.0.0.0:8767，局域网http://10.70.160.64:8767/及http://10.70.194.126:8767/；本机loopback与两个物理地址主页/health均200，其他设备端到端未实测。首次采用shell代理环境访问第二网卡超时，原检查保留；显式直连本机接口后6项主页/health均200。原进程实际PID3441296与旧STATE记载不同，重启前核对具体cmdline及无活动worker，再依次接续至当前PID；FlavoGlycoLab8766及旧项目未修改。

尚未测试其他浏览器、真实触摸设备或独立实验化学；评分权重及结构负担是透明开发启发式，仍待TASK027校准。可选安装Browser插件以在应用内继续进行页面与控制台复验。
