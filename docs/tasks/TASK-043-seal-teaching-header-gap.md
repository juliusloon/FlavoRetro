# TASK-043 修复文献教学固定栏顶部缝隙

日期：2026-10-24。状态：Approved。审批：agent_delegated；human_reviewed=false。依据：用户明确要求修复教学标题/导航bar与顶部header之间空隙造成的滚动内容泄露；本会话AGENTS.md授予自主审批权。

理解与理由：已在用户给定LAN主机复现，文献教学滚动容器的padding-top使sticky标题栏始终低于header底部桌面20px、手机16px。滚动正文在缝隙中可命中显示。

范围：仅将文献教学页顶部内边距设为0，沿用原sticky背景和定位，包内CSS同步；不改变其他边距、原导航排列和路由状态，不恢复已移除面包屑，不改HTML/JS、正文/资产/数据/API/搜索。

验收：1440/1920桌面、768平板及390/320手机的教学首屏与滚动后，标题导航栏顶边贴header底边；不出现暴露正文的缝隙。三分区与工具切换、来源定位、浏览器返回/前进及刷新正常，导航可达无横溢。CSS镜像、既有package及diff通过；浏览器只GET、真实新MCTS0、控制台异常0。

停止条件：只做上述CSS修复；不重启服务、不安装依赖、不提交/推送，保留既有改动。沿用前端测试技能，Browser plugin not available，使用已有Playwright；访问用户指定http://10.70.160.64:8767/。临时脚本/截图在/tmp/flavoretro-task043；本地基线及验收摘要在outputs/task043，均不入Git。

完成记录：2026-10-24，Completed；五视口93项浏览器、3项package、12项静态检查通过，实测顶部缝隙均0，异常/非GET/新MCTS0。见[REPORT-043](../reports/REPORT-043-seal-teaching-header-gap.md)，原批准保留。
