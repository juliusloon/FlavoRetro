# TASK-044 恢复教学标题高度并补齐顶部背景

日期：2026-10-24。状态：Approved。审批：agent_delegated；human_reviewed=false。依据：用户明确纠正TASK043：应与其他页面保持原高度，补齐背景而非删除顶部间距；本会话自主审批授权继续有效。

范围与理由：撤销TASK043的教学padding-top:0，恢复原桌面20px/手机16px页面间距；在sticky教学标题栏上方延伸同色不透明背景，覆盖滚动内容。只改CSS及包内镜像；原标题/导航尺寸位置、正文布局、面包屑移除状态和路由逻辑保持。

验收：1440/1920、768、390/320五档视口，与历史/资源/研究范围的页面顶部内边距和标题栏起点一致；教学标题栏与TASK042（修复前）几何一致。首屏及滚动时原间距区域的截图像素均为页面背景，无正文透出；覆盖区不阻拦操作。三分区、来源定位、返回/前进、刷新可用，无横溢或控制台异常。CSS镜像、最小修改、既有package及diff通过，浏览器仅GET，新增MCTS0。

停止条件：只恢复原间距并补背景，不改变HTML/JS、标题/导航内部padding和排版、其他页面样式、科学内容/数据、API或搜索；不安装、不重启、不提交/推送，保留旧改动。沿用前端测试技能；Browser plugin not available，使用已有Playwright及用户LAN主机http://10.70.160.64:8767/。临时脚本/截图放/tmp/flavoretro-task044；本地基线/摘要按项目要求放outputs/task044，均不入Git。

完成记录：2026-10-24，Completed。五档194项浏览器（188主流程＋6当前来源补验）、3项package及14项静态检查通过。原桌面20px/手机16px顶部间距和原几何恢复，整段截图像素无泄露，异常/非GET/新MCTS0。见[REPORT-044](../reports/REPORT-044-restore-teaching-spacing-and-backdrop.md)；独立证据在outputs/task044/backdrop/。原批准内容保留。
