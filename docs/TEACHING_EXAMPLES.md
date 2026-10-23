# 常见反应类型示例图

四张图使用现有来源实例的结构，以RDKit重新绘制；图示方向为从产物回到已报道前体。SVG没有复制原论文图片，来源许可和所有结构表示信息保存在web/teaching-examples.json及包内镜像。本轮仅本机提供，不新增搜索模板、课程准入或Git发布。

| 类型 | 示例 | 来源与定位 |
| --- | --- | --- |
| o | 芹菜素 7-O-葡萄糖苷的逆合成 | [10.3390/ijms242317118](https://doi.org/10.3390/ijms242317118) · body//p[8]；Figure 4A,B；Section 2.1 |
| c | 根皮素 C-葡萄糖苷的逆合成 | [10.1038/s41467-020-18990-9](https://doi.org/10.1038/s41467-020-18990-9) · body//p[4]；body//p[11]；Supplementary Figure 4；Compound 17a |
| chain | 芹菜苷的糖间连接拆分 | [10.3390/ijms242317118](https://doi.org/10.3390/ijms242317118) · body//p[9]；Figure 4A,C；Section 2.2 |
| scaffold | 黄烷酮 C 环的逆合成开环 | [10.26554/sti.2025.10.4.1169-1178](https://doi.org/10.26554/sti.2025.10.4.1169-1178) · Tables1,3;Fig3;§2.3.4 pp1173–1174 |

页面默认展示正向方程式、逆合成结构图、三步具体解释、结构身份、来源标题/DOI/定位及核对说明，并提供“查看完整结构大图”。图中标明逆合成方向和目标连接，酶/副产物省略、未指定立体与条件冲突保存在详情；不把逆合成箭头解释为实验反应可逆。完整UDP供体保留。

生成与验证记录位于outputs/task025/chemist/：build_examples.py、validation.json、cross-process-validation.json与REPORT.md；原始材料和本地证据不入Git。当前四例源许可分别按来源记录保留CC BY/CC-BY4.0，不将来源材料重新许可为项目代码。

TASK-033将全部反应原理独立为同级区域，27条按具体实例或明确标注的通式解释；资料不足保留待补齐。上方类型只切换示例，文献筛选须显式操作；工具区说明全库/通用/独立检索范围。原四张SVG及teaching-examples.json保持原字节，详见[REPORT-033](reports/REPORT-033-literature-teaching-hierarchy.md)。


## TASK-048 Git同步范围

用户现已明确授权规范化后Git同步；四张原创RDKit SVG与teaching-examples.json作为前端教学资产纳入本次代码审核，逐例source.license均登记为CC BY或CC-BY4.0，原来源/许可字段保留。此前“仅本机提供、不新增Git发布”是TASK025当时执行边界；当前同步不包含论文原件、data/raw或outputs载荷，不改变科学/课程准入。
