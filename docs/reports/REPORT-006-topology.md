# REPORT-006
结构诊断独立于搜索 policy。首版 192 位点中 55 次立体图往返失败；定位邻居顺序/手性标签相对语义，修复后 192/192 图一致。原失败文件 topology-v1.json 保留。新增带绝对立体回归；不能解释为反应预测成功。

```json
{
  "code_sha256": "44dd9cbe05f5722b5c3ff3c1bd626fc53f5f5b904506b328bce383a3fbbbf3ec",
  "detected": 132,
  "input_sha256": "e09c2906cf900514f357a58abeae3b040cb4547b189b3c25c724e48c624fe141",
  "molecules": 156,
  "roundtrip_failures": 0,
  "scope": "development structural diagnostic; not precision/recall or MCTS improvement",
  "sites": 192
}
```
