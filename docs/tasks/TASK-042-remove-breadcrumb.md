# TASK-042 移除新增面包屑导航栏

日期：2026-10-24。状态：Approved。审批：agent_delegated；human_reviewed=false。依据：用户明确要求去掉新增crumble（面包屑）栏，并保留其他变动；本会话AGENTS.md授予自主审批权。

范围与理由：删除TASK041新增的当前位置/上级面包屑DOM、对应渲染和样式，使顶栏下直接显示内容；保留页面标题、真实导航链接、URL/history、刷新/状态恢复、来源跳转及读取错误提示。同步包内镜像与当前说明。

验收：1440×1000和390×844中面包屑与空白占位均消失；子页切换、返回/前进、刷新及保存运行读取正常，页面标题和主/教学导航保持；错误提示仍显示。相关语法/镜像/diff与已有package检查通过；浏览器仅GET、新MCTS 0、控制台异常0。

停止条件：仅做所需移除，不修改其他布局、内容/科学数据、搜索/API语义，不重启服务、不新增依赖、不提交/推送。保留既有未提交改动。沿用前端测试技能；Browser plugin not available，使用既有Playwright。临时脚本/截图放/tmp/flavoretro-task042，本地基线/验收摘要按项目要求放outputs/task042，均不入Git。

完成记录：2026-10-24，Completed。29项浏览器、3项既有package及12项静态检查通过，异常/非GET/新MCTS0。见[REPORT-042](../reports/REPORT-042-remove-breadcrumb.md)，原批准内容保留。
