# 当前状态（2026-10-24）

**TASK-029授权范围已完成**（agent_delegated，human_reviewed=false）。异槲皮苷真实MCTS→Pei2019文献开发入口→FlavoGlycoLab来源接收/保存与返查已跑通；Zhang2015为备选水解，Niu2024为并行工程菌探索。[报告](docs/reports/REPORT-029-isoquercitrin-lab-handoff.md)、[完成记录](docs/tasks/TASK-029-completion-20261023.md)、[协议决定](docs/adr/ADR-012-source-bound-lab-handoff.md)。项目仍research_candidate，供体与实验验证未闭合。

## 当前搜索与研究界面

- [TASK-047](docs/reports/REPORT-047-frontend-project-and-component-system.md)已将前端规范为源码项目：主壳/9个页面片段、页面控制器、core/shared、路由/构建清单及公共FlavoUI组件分别维护，原地址/返回/刷新/状态与无面包屑保持。公共标题/控件/面板/分页/分栏实际迁移，独立`/#/components`可操作；[开发入口](web/README.md)提供build/check/watch/routes/create-page和规范，源产物检查接入CI配置。164项浏览器、29项工程、35项静态及34组对比度通过；非预期错误/非GET/新MCTS0，故障注入503单列。后端/科学正文及32/18/54/27内容保持，无重启/安装/提交；agent_delegated，human_reviewed=false。

- [TASK-046](docs/reports/REPORT-046-literature-workspace.md)已将文献案例/论文/新增证据统一为紧凑列表与常驻详情，桌面约34:66独立滚动、手机上下；关联来源原地阅读，筛选/页码/选中/返回刷新保持。六步可直达，原笔记、自检及全量导出保留。五视口266项＋专项23项浏览器、3项package、15项静态及Node/diff通过；非预期错误/非GET/新MCTS0，故障注入两条500单列。原32/18/54内容与外层标题背景保持，agent_delegated，human_reviewed=false；旧页面刷新生效。

- [TASK-044背景修复](docs/reports/REPORT-044-restore-teaching-spacing-and-backdrop.md)已撤销TASK043去顶部间距的实现，恢复教学页桌面20px/手机16px间距与原标题导航位置，并向上延伸同色不透明背景遮住滚动正文。五档与原几何及历史/资源/研究范围起点一致，顶部整段像素无泄露；194项浏览器、3项package及14项静态通过，异常/非GET/新MCTS0。仅两份CSS为本背景任务代码修改，其他工作改动保留；证据outputs/task044/backdrop/。agent_delegated，human_reviewed=false。

- [TASK-045](docs/reports/REPORT-045-literature-tools-cleanup.md)已精简文献核查工具区：删除指定重复标题/说明、四选项第三行及案例全库提示，不留占位。四工具仅顶部分页，文献/案例/证据默认25及10/25/50/100，与历史同款；六步专用条数和全量导出保持。来源跳转/示例聚焦及页码状态通过；当前共存版本四视口118项浏览器、3项package、17项静态及Node/diff通过，异常/非GET/新MCTS0。保留并行TASK044顶部间距/背景修改。agent_delegated，human_reviewed=false；旧页面刷新生效。

- [TASK-042](docs/reports/REPORT-042-remove-breadcrumb.md)已按用户要求移除TASK041新增面包屑栏及空白占位，其余子页URL、返回/前进、刷新/状态恢复、标题和导航链接保持。桌面/手机29项浏览器、3项package及12项静态核验通过；异常/非GET/新增MCTS0。服务无需重启，旧页面刷新生效。agent_delegated，human_reviewed=false。

- [TASK-041](docs/reports/REPORT-041-addressable-subpages.md)已将五个主入口、教学分区/工具、示例/原理、资源详情和保存运行/路线建为独立地址子页；返回/前进、刷新和新标签直达可用；面包屑上级栏已按TASK042移除。筛选/分页/A/B/来源定位在URL，草稿/显式预算在会话，滚动随历史恢复，兼容旧?run。三视口117项浏览器、18项既有工程及23项静态/内容/服务核验通过，异常/非GET/新MCTS0。三份前端及镜像同步，服务未重启，旧页面需刷新一次；科学数据与搜索语义保持。agent_delegated，human_reviewed=false；设计见ADR-013。

- [TASK-040](docs/reports/REPORT-040-teaching-heading-navigation.md)教学三个导航按钮当前位于标题/说明右侧并右对齐；窄屏换行，默认/点击/键盘与来源跳转保持。五视口54项浏览器、3项相关镜像/diff通过，0异常/0非GET/0新MCTS。

- [TASK-039](docs/reports/REPORT-039-single-principle-layout.md)原理区现为标题“选择要了解的反应原理”与相邻菜单，删除原标题/指定说明及上下分页；27项固定单条，以独立key保留选择。复用常见类型左讲解/右图式双面板、手机堆叠，原正文/来源/资产保留；四视口172项浏览器、3项package测试、9项静态通过，异常/非GET/新搜索0（agent_delegated，human_reviewed=false）。

- [TASK-038](docs/reports/REPORT-038-example-left-context.md)四类示例的出处、读图核对与筛选按钮当前独立排在左侧讲解卡片下方，卡片外直接排版；右图顶部对齐，指定筛选提示已删除。三视口80项浏览器、8项静态核验通过，原科学/来源文字保留，0异常/0非GET/0新MCTS。

- [TASK-037](docs/reports/REPORT-037-teaching-example-panels.md)常见反应类型当前为标题右侧四按钮、左讲解/右方程式与结构图约1:2双面板；手机堆叠。指定说明与重复身份块已删除，原出处/边界及四例科学内容保留；四视口150项浏览器、8项静态核验通过，0异常/0非GET/0新MCTS。

- [TASK-036](docs/reports/REPORT-036-literature-section-tabs.md)已完成教学顶部“常见反应类型 / 全部反应原理 / 文献核查与练习”导航，每次只显示一个区域，默认入口首项，具体地址按TASK041恢复；内部筛选/原理/练习状态及来源跨区跳转可用。三视口116项浏览器、6项完整镜像/语法/diff通过，0非GET/0新MCTS/0异常。

- [TASK-035](docs/reports/REPORT-035-history-side-panels.md)历史页当前为左历史/右对照约65:35双栏，各自滚动；窄于1100px改上下。指定对照标题/说明已删除，A/B选择、真实历史打开与JSON导出保持；四档69项浏览器、3项package测试及镜像/diff通过，错误/警告/新搜索0（agent_delegated，human_reviewed=false）。

- [TASK-033](docs/reports/REPORT-033-literature-teaching-hierarchy.md)教学升级完成（agent_delegated，human_reviewed=false）：教学三类内容保留，当前按TASK036互斥切换；四例直接显示结构图、正向方程式、逐例解释与出处；27原理独立选择并区分实例/通式/证据不足，四工具用途/范围可见，示例与筛选仅显式联动。218项三视口浏览器、10项既有测试、34组颜色与语法/镜像检查通过，错误/警告/新搜索0；原32/18/54资料与科学边界保留。

- TASK-034高级设置默认值已交付（agent_delegated，human_reviewed=false）：数字框显示预算默认值，平衡两阶段分列默认提示；切换/自定义/清空/恢复及历史请求可用，只提交显式编辑预算项，原两阶段默认语义保持。四档91项检查、9次拦截提交通过，错误/警告0、真实搜索0。[报告](docs/reports/REPORT-034-advanced-defaults.md)。
- [TASK-032](docs/reports/REPORT-032-history-and-pagination.md)的资源页同款表格与分页保留，历史当前左右布局见TASK035；历史/资源各仅保留顶部完整分页，默认25条，历史新增每页数与页码跳转。43项浏览器、2项既有接口及11项相关静态检查通过，0新MCTS/0浏览器POST；并行页面/参数修改独立验收。

- TASK-031界面整理完成（agent_delegated，human_reviewed=false）：反应原理固定加载、删除勾选框；随机种子/候选库存范围移入高级设置；左侧参数独立滚动、搜索按钮固定面板底部，手机可滚至结果区。六档视口148项浏览器检查通过、错误/警告0，3次提交仅本地拦截、实际搜索0；库存与后端语义保持。[报告](docs/reports/REPORT-031-panel-controls.md)。
- 当前research-priority-v4：唯一末端库存覆盖28%、结构简化20%、模型先验20%、路线简洁12%、精确来源支持20%；已知危险、未指定碳立体与有限O-乙酰保护调整另扣。杂原子立体标记分开保留，不补构型，不当作缺失糖异头碳；旧总标记/legacy_cost保持原口径。评分不是成功概率。
- all_generated_prefixes_v1保留所有实际创建的非根MCTS路径，包括有后续子节点的未闭合前缀；没有从参考树拼反应。真实frontier_count与extracted_node_count分记；全部候选去重/排序后按结构组优先展示，图仍降序横排、手机局部横滑。原UCT/PUCT、节点硬限及精确库存身份保留；native搜索回传不变。
- 默认通用optimized仍search_repaired.SearchTree，显式糖苷/文献路径仍search.SearchTree。当前精确文献库15条=TASK027原13条+Pei2019糖基转移核心/Zhang2015水解；另有1条Niu2024工程菌开发上下文，非可执行动作；需显式开启文献反应，非新泛化scope。候选库存新增0，仍17键。
- 网页芦丁示例提供“加入来源记录”按钮，明确末步仅作者摘要；不自动开库存。未知原料有后续子目标；源条件、收率、来源冲突与范围分别显示，开发JSON/耗时/配置/哈希不渲染，原始导出保留。既有资源分页、32论文/18案例/54反应与六步导出保留，教师/生产不升级。

## 实测效果与未解决事项

- 原v3冻结开发18/18正常（3目标×2技术seed×A/B/C），68资产封存。A/B六配对候选集合完全一致；参考首步前5 A0/6→B4/6，C4/6；实际根参考5/6、5/6、6/6。前5结构组中位数4.5/5/5，O-乙酰保护调整中位数2/0/0；全部闭合0。已曝光目标/共享来源及技术seed不作为独立化学样本，不声称提速。
- P4三次前缀纠偏与P5三次碳/杂原子分轴验证另存，不覆盖原18cell，也不把原v3矩阵说成当前v4校准。当前三例参考首步均第一，前5各5结构组；紫云英苷465/异槲皮苷430/芦丁420候选，全部闭合0。
- 最终芦丁HTTP记录`20261023T103139-14f4c67bbe53476c825fa42cebb56d8c`：159真实前沿、420实际非根路径/去重候选、展示25，首条20.4748分；实际为芦丁→异槲皮苷＋UDP-β-L-鼠李糖的一步未闭合前缀。来源支持1/1步但仅原作者摘要，完整实验条件/分离收率未知。末端两种未解决原料，碳立体缺失0、P等杂原子标记2；未指定0不证明已指定立体正确。
- 来源库有异槲皮苷→槲皮素＋UDP-Glc动作，且独立异槲皮苷查询中优先显示；不能声称芦丁单次MCTS已自动生成完整两步方案。模型保护糖/糖基卤化物路线尚无逐步一手支持。所查UDP-Rha美国目录缺货/询价，其他供应未核实；UDP-Glc盐型资料不替代中性母体身份。
- [TASK-028](docs/tasks/TASK-028-rutin-subgoal-and-donor-closure.md)为Proposed、未执行，聚焦跨层子目标选择、完整原文条件、活化糖供体制备/再生与精确供应、新版本冻结评价。需要新TASK批准；本轮24/24真实请求均正常终态，预算用尽，无待恢复搜索。

## 验证、服务与工作区

- 当前72相关测试通过；最终31项Playwright Chromium桌面1440×1000/手机390×844交互检查通过，警告/异常0、浏览器POST0；原始结果导出一致、六步导出全量。最终28项离线/资产/接口核验通过；8活动Python/测试AST、Node语法、前端/配置镜像及diff检查通过。其他浏览器、真实触摸或独立湿实验未验证。
- 当前Retro PID3750432监听0.0.0.0:8767；[本次异槲皮苷结果](http://10.70.160.64:8767/?run=20261023T104955-9ca6aa531fd741338c95fcec2447eda9)。Lab PID3750202监听0.0.0.0:8766；用户本次授权的跨项目来源接收已完成。两端LAN health 200；其它设备未实测。服务登记outputs/task029/services.json；没有活动MCTS。
- TASK027的原结果/冻结开发证据保留且不回写；本次基线、来源v3、真实运行副本、交接包与Lab校验收据、最终浏览器46项及变更审计统一在outputs/task029。原始MCTS归档仍按manifest校验。
- Git未stage/commit/push，旧未提交改动保留；原始/受限数据、outputs/temp不入Git。旧retro_synthesis/CondRxnBench不执行、不依赖其可写。全部操作以operate记录。

## 不变的资源与科学边界

metadata/active.json仍指data/derived/v3，3059候选/123来源；records为事实源、SQLite只读派生。审核视图task015-06-v1仍17允许键/4错配禁用，9原文/6原报收率不等于供应认证。库存按正常解析后的完整InChIKey核E/Z/手性/目标排除，内容未扩大。

既有intake v5仍54条/17来源、45来源绑定结构候选/9问题、runtime_admitted0；20收率未报告不补零，FV6原报51%与计算38.37%冲突/MOM实际保护投料保留。新三条精确来源动作是独立显式注册表，不把这54条或教学课程整体放行。

TASK022历史21配对、130 DFF开发回归及效率门失败保持当时身份；不是当前v4验收，原总账1449/3600=1440完成+9失败，不重置或恢复。TASK016 P7仍Partial/stopped；TASK017仍Partial、preparation_ready=true、research_run_ready=false、正式科研0cell，独立panel/标签/forward/实验、供应、教师与生产门未升级。旧两个被冻结P7脚本语法错误不因当前活动模块AST通过而改为通过。

## 当前异槲皮苷开发链

- 实际运行20261023T104955-9ca6aa531fd741338c95fcec2447eda9：1,922候选、25展示、0闭合；Zhang第1（20.0525），Pei第2（19.6246）。候选库存关闭，源动作不复制论文产率；GmSUS供体再生作为Lab开发内容，未声明搜索已闭合。
- 与Lab关联且实际生成的同图来源树保存在source_variants；交接包只有真实源树才可导出。Web明确展示三篇角色并提供进入/导出；Lab只附计算来源，既有学习/方案/观测状态独立。校验和不是签名或独立复算。
- 最终Retro76测试、Lab78项Python（3显式跳过）/70Node、跨站46检查通过；public工作台977/数据页65通过。三篇原件与Lab教学内容未改。
- 论文来自本任务核对后准入目录，本轮证明精确来源重现与联动，不证明对未登记论文的盲发现。后续[Retro TASK030提案](docs/tasks/proposals/TASK-030-isoquercitrin-donor-regeneration-and-discovery.md)与Lab TASK036提案待批准，均未执行。芦丁TASK028仍独立待办。
