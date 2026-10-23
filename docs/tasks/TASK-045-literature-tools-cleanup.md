# TASK-045 精简文献核查工具区与统一分页

日期：2026-10-24。状态：Approved。审批：agent_delegated；human_reviewed=false。依据：用户明确要求删除文献教学工具区重复标题/说明、四个工具选项第三行、案例页指定全库提示，并将下面选择栏与搜索历史统一；本会话AGENTS.md授予自主审批权。

范围与理由：删除tools-title及相邻指定说明、四项small第三行；案例页隐藏已删除的context提示且不留占位，其他工具既有范围说明保留。修复示例筛选按钮原来对tools-title的聚焦引用。下方选择栏按分页理解，四工具改为仅保留顶部分页，文献/案例/新增证据复用历史的默认25条、10/25/50/100选项，六步练习保留1/2/3/6选项与默认1步。保留现有筛选/来源/URL/返回刷新/全量导出。web三文件及包内镜像同步。

验收：1440桌面、768平板、390及320手机中指定文字及第三行移除、案例无提示占位；所有工具顶部分页可用且无底部分页；文献/案例/证据25默认和10/25/50/100选项与历史一致，分页/筛选空态及越界回收正确；六步内容和导出全量保留；示例显式筛选聚焦、工具键盘导航、来源跳转和返回/前进/刷新可用；无页面横溢，浏览器异常/非GET/新增MCTS0；相关package/Node语法/镜像/diff通过。

停止条件：仅做上述呈现与分页改动；不修改后端/科学内容、数据或搜索语义，不重启服务、不安装依赖、不提交/推送；保留已有改动及另一聊天的TASK044顶部间距/背景遮挡调整。Browser plugin not available，使用现有Playwright，访问用户LAN地址http://10.70.160.64:8767/。临时脚本和截图在/tmp/flavoretro-task044；按用户项目规范保存TASK/REPORT及outputs/task044本地基线/验收，不入Git原始或受限数据。

编号续作说明：原批准文件为TASK-044-literature-tools-cleanup.md；执行过程中另一聊天建立TASK-044-restore-teaching-spacing-and-backdrop.md并覆盖outputs/task044基线。为隔离记录，自本条起文献工具精简改用TASK045及outputs/task045。原批准历史保留；利用operations/command-2274.log的完整原始diff反向恢复本任务原基线并核对最初SHA，不覆盖另一任务的CSS或证据。原117项验收属修改顶部间距前的状态，最终对当前共存版本重验。补修openLiteratureAnchor仍引用旧默认分页数导致来源跳转size参数丢失的问题，同步包内镜像。

完成记录：2026-10-24，Completed。118项四视口浏览器、3项已有package、17项静态及Node/diff检查通过，异常/非GET/新增MCTS0；保留并行顶部背景修改。见[REPORT045](../reports/REPORT-045-literature-tools-cleanup.md)。
