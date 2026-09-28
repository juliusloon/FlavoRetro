# TASK-015-P1：可直接用于 SciFinder 的检索词

2026-09-27。根据 ORD 全量筛选及 60 条代理审核确定优先级；本轮未登录 SciFinder。下面每行作为一个独立检索起点，不假定不同机构版本的布尔语法相同。先看具体反应，不以题名命中数量为目标。

## 先补 C-糖苷真实构键

| 优先级 | 直接复制的英文词 | 需要的实例 |
|---|---|---|
| P1 | `flavone C-glycosylation` | 反应前没有相应芳基-C-糖键、反应后形成该键的具体步骤 |
| P1 | `vitexin isovitexin synthesis` | 分开核查8-C与6-C、区域异构体及每个产物的收率 |
| P1 | `orientin isoorientin synthesis` | 木犀草素类8-C/6-C糖苷构键，补不同苷元 |
| P1 | `flavone O-to-C glycoside rearrangement` | O→C重排那一步，连同其前后中间体；不要只导出最终成环 |
| P1 | `OsCGT 2-hydroxynaringenin C-glycosylation` | 糖供体、2-羟基黄烷酮受体、酶促C构键与后续脱水分别定位 |
| P2 | `flavone 6,8-di-C-glycosylation` | 双C糖苷，区分逐次构键与整条发酵路线 |

## 再补 O-糖苷位点及糖种

| 优先级 | 直接复制的英文词 | 要区分什么 |
|---|---|---|
| P2 | `flavonol 3-O glycosylation` | 3-O构键、异头构型、供体和保护顺序 |
| P2 | `flavone 7-O glycosylation` | 7-O构键与其他酚位点竞争 |
| P2 | `kaempferol 5-O glycosylation glycosyl ortho-alkynylbenzoate` | 当前卡26/31的5-O实例；葡萄糖与半乳糖不能混同 |
| P2 | `flavonol 3-O ribofuranoside glycosylation` | 五元核糖供体，区别常见葡萄吡喃糖 |
| P3 | `naringin prunin selective hydrolysis alpha-L-rhamnosidase` | 糖-糖键选择性水解，和苷元脱糖分别登记；当前已有公开专利实例，无需重复抓同一条 |
| P3 | `hesperetin 7-O-glucoside beta-glucosidase hydrolysis` | 单糖底物，不能用hesperidin双糖实验替代 |

已有本地 744 条领域糖苷候选、其中 227 条有芳基C拓扑，不要求重搜全量。首轮优先前5行，遇到本地同论文/专利的同实例保留来源重合，不充作新增独立样本。每方向先找3–5个反应物/产物/实例号明确的例子即可；这是工作量建议，不是充分覆盖证明。

## 现有卡片的精准核查词

| 卡号 | 可复制的精确定位 | 核对目标 |
|---|---|---|
| 5 | `10.1080/00397911.2024.2445860`；`chrysin 4-bromobutyl`；反应号 `31-614-CAS-43975190` | 4-溴丁醇、活化步骤或反应物表示是否有误 |
| 12 | `10.1016/j.tet.2013.10.002`；`apigenin benzylic dendrimers` | 产物黄酮C2=C3是否被错画成单键 |
| 46 | `CN113831314A`；底物 `31712-49-9`；反应号 `31-614-CAS-31342232` | 单糖/双糖、S/R橙皮素是否正确配对 |
| 54 | `2243238-14-2`；反应号 `31-479-CAS-23349279`；`hesperidin diosmin aluminum chloride complex` | 铝络合中间体原结构，不要自动删Al补成diosmin |
| 28/29/50/56 | `10.1002/jlac.199519950362`；`vitexin isovitexin Fries rearrangement` | 前体O糖基化、O→C重排、两异构支路及最终成环的分步对应 |
| 26/31 | `10.1039/C5OB02313K` | 山柰酚5-O糖基化、糖C4构型与精确实例 |
| 35/57/59 | `10.1021/jo1014189` | 24g而非24b的条件；糖供体三步累计50%；苷元前体路线 |
| 48 | `10.22159/ajpcr.2020.v13i1.35684`；`hesperdin thiadiazole` | 已补得DOI；核对78%与C=N构型即可，无须重新寻找论文身份 |

当前7条需裁决包括27整体发酵、50双异构支路、51仅产物：这些有些需要拆记录/补底物，有些需要具体原图，不是继续增加主题关键词就能解决。卡53已撤稿，不把重新导出同文当恢复可信证据的办法。

## 交给 Cano 的最小材料

按账号允许方式导出相关反应的原始 RDF/RDfile，保留 reference、CAS Reaction Number、结构、条件、收率和实验步骤；若格式不支持，保留原导出并附文本定位。不用手工抄 SMILES，也不用再逐条替我填60卡。

存入 `/home/ljx/FlavoRetro/data/inbox/scifinder/task015-user/`，另附检索词、日期、DOI/专利号、例号/化合物号及对应卡号。按本轮偏好，不要求下载正文或SI。Cano负责后续解析、哈希、去重与逐条来源绑定；本轮结果已在独立审核层保存，原始数据及活动v3没有被覆盖。商业数据库原始导出只留本地。
