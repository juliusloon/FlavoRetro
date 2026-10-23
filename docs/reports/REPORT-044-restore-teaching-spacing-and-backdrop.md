# REPORT-044 恢复教学标题高度并补齐顶部背景

2026-10-24。Completed；审批agent_delegated，human_reviewed=false。[事前合同](../tasks/TASK-044-restore-teaching-spacing-and-backdrop.md)。本背景修复的独立证据目录为outputs/task044/backdrop/，按合同路径、时间及SHA与其他同号记录区分。

## 修正

用户指出TASK043通过删除教学页顶部间距挡住泄露，却使标题栏相对其他页面上移。现撤销padding-top:0，恢复原桌面20px、手机16px顶部间距。在sticky标题栏增加同色不透明::before背景，向上延伸24px，超出滚动容器的部分被裁切。背景覆盖原标题栏与主header之间区域，不占布局空间；pointer-events:none避免阻拦操作。

只修改web/style.css与包内CSS镜像；标题栏、标题文字和导航的top/left/width/height均与TASK043前参考样式一致，也与历史/资源/研究范围页面的标题栏起点和顶部内边距一致。正文布局、导航、面包屑移除、搜索/数据均保持。既有工具small样式及来源定位默认25修订保留，不作为本背景任务改动。

## 环境与验证

Browser plugin not available，使用已有Playwright Chromium和Pillow读取截图像素。用户LAN地址http://10.70.160.64:8767/；1440×1000、1920×1080、768×1024、390×844、320×844。

目标流程：在隔离参考页面加载TASK043前的CSS→比较当前标题/导航几何→比较其他三页的顶部起点→来源库首屏和多段滚动的整段背景像素→三分区与来源定位→刷新、返回/前进。

| 检查 | 结果 |
| --- | --- |
| 身份/非空/错误遮罩 | 对应URL/标题和实际内容正常，无错误遮罩 |
| 原高度与跨页面统一 | 五档标题栏/文字/导航几何恢复参考原样；教学与历史/资源/研究范围的顶部间距和标题栏起点一致 |
| 背景覆盖 | 桌面20px、手机16px间距保留；45个位置/状态的整段顶部截图（含左右边缘）像素全部为背景色，无正文露出 |
| 点击/布局 | 背景不拦截操作，header及导航可达，无横溢；面包屑未恢复 |
| 导航与定位 | 三分区、来源无遮挡、刷新及返回/前进通过；对当前保留的来源定位修订另做6项补验 |
| 控制台/搜索 | 浏览器异常/错误/警告0，非GET0，新增真实MCTS0 |
| 工程 | 188项主浏览器＋6项来源补验＝194项；3项既有package和14项CSS最小变更/镜像/HTML/服务字节/diff检查通过 |

只读工程审查复核了sticky层叠、父容器裁切、两侧背景及pointer-events，背景效果以截图像素而非命中测试判定。临时QA脚本/截图在/tmp/flavoretro-task044；独立摘要及前后CSS在outputs/task044/backdrop/。操作均经operate记录。主要命令为`.venv/bin/python -B /tmp/flavoretro-task044/qa.py`、只读来源补验、`.venv-foundation/bin/python -B -m unittest tests.test_package`、`git diff --check`及LAN实际CSS字节核对。首次静态核验改用本任务基线区分既有/其他工作变更，未将这些变更回退。

未安装、重启服务、提交或推送。仅验证Chromium和模拟手机视口，未测试其他浏览器及真实触屏设备。当前界面替代TASK043的零间距实现；其原报告作为历史保留。

## 截图

![桌面：原顶部高度保留并补齐背景](/tmp/flavoretro-task044/1440-restored-spacing.png)
![手机：保留16px间距且不透出正文](/tmp/flavoretro-task044/390-restored-spacing.png)
