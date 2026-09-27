# TASK-014 外部来源接入调查

核查日期：2026-09-27。范围是官方公开资料调查；本轮没有批量下载、商业账号登录、API 授权测试或 MCP 安装。表中的“可作为入口”是后续工程选择，不是黄酮覆盖率、内容正确性或本机构权限已经得到验证。

| 来源 | 官方核查结果 | 对本项目的角色 | 仍需核查 |
| --- | --- | --- | --- |
| ORD | 官方 ord-data 发布 Parquet，反应为序列化 Protobuf；schema 含 inputs/outcomes/provenance；数据许可 CC-BY-SA-4.0，代码许可独立 | 优先做可下载子集的离线结构筛选接入试验 | 冻结 dataset/commit/下载哈希、目标化学覆盖和条件/出处缺失情况；可能与 USPTO 模型训练重叠；衍生数据发布前另核许可 |
| Reaxys | 产品页明确 API/MCP/flat file 为单独许可；支持中心列出数据交付方式 | 机构获授权后的补充来源 | 网页订阅不自动证明数据许可；本机构权限、具体接口、配额和导出范围均未验证 |
| CAS SciFinder | 官方开发文档描述授权 Client ID、sfn-search scope 和交互式 PKCE；文档年代较早 | 现有合法本地导出用于试点；未来官方授权接口或人工困难案例复核 | 文档是否仍适用、本机构授权及反应导出能力须向机构/CAS 确认，不能按旧 PDF 假定当前可用 |
| EPO OPS | 官方介绍程序化访问专利数据的 web services | 找专利元数据/全文，再做实验实例抽取 | 不是现成反应库；覆盖、认证、配额、全文/图式可提取性及家族身份须在接入任务中验证 |
| Europe PMC | 已定位官方 REST 文档地址，本轮工具未成功取得正文 | 后续开放论文/全文检索候选入口 | 本轮未验证功能，不能据链接声称全文或 SI 均可获取 |
| PubChem | 只读 PUG REST 实际读取 CID 10680（flavone）和 6537099（aurone）成功，两个母核查询均命中返回结构；文档网页本轮仅返回 JS 提示 | 名称、结构及身份辅助；不作为反应事实主库 | 仅验证两个化合物属性读取，批量限额及其他接口未核；化合物身份确认不能证明反应成立 |

官方来源：[ORD 数据仓库](https://github.com/open-reaction-database/ord-data)、[ORD schema](https://docs.open-reaction-database.org/en/latest/schema.html)、[Reaxys 产品](https://www.elsevier.com/products/reaxys)、[Reaxys 数据支持](https://www.elsevier.support/dataasaservice/answer/overview-of-reaxys-data)、[CAS 官方开发文档](https://scifinder-n.cas.org/static/api/SFN_API_Developer_Documentation.pdf)、[EPO OPS](https://www.epo.org/en/searching-for-patents/data/web-services/ops)、[Europe PMC 文档入口](https://europepmc.org/RestfulWebService)、[PubChem PUG REST](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest)。

建议：本地试点先建立统一记录合同；后续新增独立数据接入任务，以 ORD 的一个冻结子集检验读取/结构/出处/去重，不直接下载全库。商业接入取决于真实授权。论文/专利发现工具的记录只能进入 discovery candidate，经实例抽取与来源核验后才能成为反应证据。

统一接入最小字段：provider/dataset/version、provider_record_id、retrieved_at、raw_sha256、license/access_scope、source DOI/patent/instance、原始及规范化结构、条件/收率的归属与缺失、标准化变换清单、审核状态及 training_overlap_status。保留相同反应的多个出处和条件，不合并证据强度。接口存在、下载成功和 parser 成功均不等于独立化学审核。
