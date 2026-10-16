# -*- coding: utf-8 -*-
"""TASK-015-P5 阶段 D2：供应商带日期核查汇编。

核查方式：公开供应商目录/聚合页的 Web 检索（2026-09-29，美国区结果），
未登录任何商业账号、未绕过任何付费墙或权限。内部片段（无外部商品身份）
如实记 not_commodity/skipped，不伪造"已核查"。

输入（只读）：outputs/evidence/task015-p5-vendor/identity_packets.jsonl
输出：outputs/evidence/task015-p5-vendor/{vendor_checks.jsonl, manifest.json 更新}
检索结果为人工记录数据（本文件内联），构建确定性。
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VDIR = ROOT / "outputs/evidence/task015-p5-vendor"
RETRIEVED = "2026-09-29"

S = "https://www.sigmaaldrich.com"
T = "https://www.tcichemicals.com"

# name -> dict(check=..., vendors=[...], cas_note=..., flags=[...])
CHECKS = {
    "methyl_iodide": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich/Merck（多纯度等级）", "TCI", "Fisher Scientific（分销）", "Reagents.com"],
        notes="高毒烷化剂，购买需机构账号与合规审查；公开目录确认为常规在售试剂"),
    "acetic_anhydride": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich ACS ≥99.7% (CAS 108-24-7)", "Fisher Scientific", "VWR", "IBIS Scientific", "Alliance Chemical"],
        notes="列管前体，购买需机构账号；公开目录确认为常规在售试剂"),
    "benzyl_bromide": dict(status="commercial_listing_found", vendors=[
        "Fisher（Sigma-Aldrich/TCI 品牌）", "Reagents.com 99%（MFCD00000172）", "TCI B0578"],
        notes="催泪剂，常需机构账号"),
    "TBSCl": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich B1522 ≥99%", "TCI B1144 >98%", "Acros/Alfa Aesar/Oakwood/Fluorochem（文献常引）"], notes=""),
    "benzaldehyde": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich 418099 ReagentPlus ≥99%", "TCI B2379 >99% (GC)", "Fisher/Spectrum/Alfa Aesar"], notes=""),
    "anisole": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich anhydrous 99.7% 及 801452（100 mL ≈ $43.50）", "TCI A0492 >99.0% (GC)", "Spectrum/Santa Cruz/Loba"], notes=""),
    "acetophenone": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich 多等级（含 TraceCERT 分析标样）", "TCI A0267（2024 价目在售）", "Fisher"], notes=""),
    "phenyl_acetate": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich 108723 99%（100 g ≈ $39.67–52.90）", "TCI P0301"],
        cas_note="苯基乙酸酯正确 CAS 为 122-79-2；检索中 122-88-3 为 4-氯苯氧乙酸（不同化合物）"),
    "vanillin": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich for synthesis（25 kg ≈ $3,050；小包装在售）", "TCI H0264"],
        notes="InChIKey MWOOGOJBHIARFG 与库存记录一致（检索页交叉印证）"),
    "isovanillin": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich ≥97%", "TCI >98.0%", "Alfa Aesar/Thermo", "Santa Cruz", "Combi-Blocks/Oakwood"],
        cas_note="异香兰素正确 CAS 为 621-59-0；121-34-6 为香草酸（不同化合物）"),
    "2,4,6-trihydroxyacetophenone": dict(status="commercial_listing_found", vendors=[
        "Merck/Sigma 841389（单水合物，for synthesis）", "TCI T1888 >98.0% (GC)（单水合物）",
        "ChemicalBook 聚合 344 家（约 $5–10/g）"],
        notes="市售通常为单水合物，购前需确认水合物形态"),
    "2,4-dihydroxy-6-methoxyacetophenone": dict(status="specialty_thin_market", vendors=[
        "ChemUniverse（CAS 3602-54-8 条目）"],
        cas_note="正确 CAS 为 3602-54-8；90-24-4 是 2'-羟基-4',6'-二甲氧基苯乙酮（xanthoxylin，不同化合物）",
        flags=["identity_ambiguity_owner_check", "stock_no_cid"]),
    "glucose": dict(status="commercial_listing_found", vendors=[
        "TCI G0048 >98.0% (GC)", "Sigma-Aldrich G8270 等多等级", "Fisher D16-10 ACS", "Cayman 23733"], notes=""),
    "rhamnose": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich 83655 单水合物 ≥99%", "TCI R0054 单水合物 99%"],
        notes="库存 InChIKey 为 α-L-吡喃鼠李糖形式，供货为单水合物固体"),
    "neohesperidose": dict(status="specialty_found", vendors=[
        "Chengdu Biopurify", "BOC Sciences", "NeoBiotech", "Biovalley (FR)"],
        cas_note="CAS 17074-02-1；检索页给 PubChem CID 441426（库存缺 CID 证据）",
        flags=["stock_no_cid"]),
    "rutinose": dict(status="specialty_found_mg_scale", vendors=[
        "ChemImpex（10 mg ≈ $140，在售）", "Greyhound（植物化学标样商）"],
        notes="游离芸香糖为稀有标样，仅 mg 级；CAS 检索有混淆条目（90-52-8 为喹啉类，非 rutinose）",
        flags=["stock_no_cid"]),
    "hesperetin": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich W431300 ≥95%（≈$389）", "Sigma-Aldrich H4125 分析标样（≈$195）",
        "MedChemExpress", "Extrasynthese 1115S（±）", "Otto Chemie 97%"],
        notes="供应商页立体形态表述不一（± 与单一对映体并存）；检索页出现 CID 72281 与库存 CID 3593 并存，须核对立体形式",
        flags=["stereo_form_owner_check"]),
    "hesperetin_chalcone": dict(status="specialty_found", vendors=[
        "Biosynth（Suzhou）", "Apin Chemicals (UK)", "Pharmaffiliates（标样/定制）", "Conier"],
        cas_note="CAS 29287-30-7；目录聚合页在售"),
    "naringenin_chalcone": dict(status="commercial_listing_found", vendors=[
        "Cayman 33806 ≥98%", "TargetMol（1 mg $39 / 10 mg $128，现货）", "ChemFaces CFN90606",
        "Sigma PHL83877 phyproof（≈$448）", "MedChemExpress（经 Fisher ≈$225–265/10 mg）"],
        cas_note="柚皮素查耳酮正确 CAS 为 73692-50-9（2',4,4',6'-四羟基）；25515-43-9 与 961-29-5 为异甘草素类（不同化合物）"),
    "naringenin": dict(status="commercial_listing_found", vendors=[
        "TCI N0072（外消旋 67604-48-2）", "Sigma-Aldrich N5893/W530001；S(-) 型 480-41-1", "Santa Cruz ≥98%"],
        flags=["identity_gap_stock_no_cid", "stereo_form_owner_check"],
        notes="库存记录缺 PubChem 身份证据（CID=None）；市售区分外消旋与 S(-) 型，须先定库存立体形式"),
    "quercetin": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich Q4951 ≥95% (HPLC)", "TCI Q0112（5 g $57 / 25 g $170，当日发货）"], notes=""),
    "eriodictyol": dict(status="commercial_listing_found", vendors=[
        "Sigma-Aldrich (±)-Eriodictyol ≥95% (HPLC)（≈$204，CAS 4049-38-1）", "Selleck", "BLD Pharm（暂缺货）"],
        notes="市售以外消旋 4049-38-1 为主；单一对映体 4049-39-6 少见"),
    "hydrated_alpha_L_rhamnopyranose": dict(status="covered_by_parent_sugar", vendors=[
        "同 L-鼠李糖供货（Sigma 83655 / TCI R0054）"],
        notes="CID 439710 即 α-L-吡喃鼠李糖（半缩醛形式）；无独立商品名"),
    "dehydrated_rhamnopyranose_quercitrin_fragment": dict(status="covered_by_parent_sugar", vendors=[
        "同 L-鼠李糖供货（Sigma 83655 / TCI R0054）"],
        notes="CID 13455857 实为甲基脱氧己糖（C6H12O4），即 quercitrin 的鼠李糖部分；内部命名，无独立商品"),
    "sugar_gap_rhamnosyl_hexose_disaccharide_OFZYAYMKZL": dict(status="not_commodity_internal_fragment",
        vendors=[], notes="CID 91577512 实为乙酰化双糖片段（C14H24O10）；内部构建块，无商业供货预期"),
    "sugar_gap_rhamnosyl_hexose_disaccharide_UZIKLNYKVU": dict(status="not_commodity_internal_fragment",
        vendors=[], notes="CID 53985910 实为甲基化双糖片段（C12H22O9）；内部构建块，无商业供货预期"),
}

SKIP_INTERNAL = dict(status="not_commodity_internal_fragment", vendors=[],
                     notes="内部桥接/保护片段（无 CID、无外部身份证据）；不对应可购商品，供应核查不适用")

# 其余 sugar_gap_*（无 CID）与 protected_rhamnose_leaf_*
for nm in ["sugar_gap_rhamnosyl_hexose_disaccharide_ASGYRTWPIY",
           "sugar_gap_rhamnosyl_hexose_disaccharide_BSESJCOUYF",
           "sugar_gap_rhamnosyl_hexose_disaccharide_COAOCSAWRK",
           "sugar_gap_rhamnosyl_hexose_disaccharide_HMSBGGCYEH",
           "sugar_gap_rhamnosyl_hexose_disaccharide_MZLKGISSOY",
           "sugar_gap_rhamnosyl_hexose_disaccharide_NDAQNSFGSP",
           "sugar_gap_rhamnosyl_hexose_disaccharide_RAFSHHVKLA",
           "sugar_gap_rhamnosyl_hexose_disaccharide_NTQPAWBRYI",
           "sugar_gap_rhamnosyl_hexose_disaccharide_SJFVSFLVJA",
           "sugar_gap_rhamnosyl_hexose_disaccharide_SPCUBGINFC",
           "sugar_gap_rhamnosyl_hexose_disaccharide_TXZOTBUOBZ",
           "sugar_gap_rhamnosyl_hexose_disaccharide_UDYLCPHGMF",
           "sugar_gap_rhamnosyl_hexose_disaccharide_UNBOZMFZFL",
           "sugar_gap_rhamnosyl_hexose_disaccharide_VOAJQPZXTF",
           "sugar_gap_rhamnosyl_hexose_disaccharide_VQFCRWDUJQ",
           "protected_rhamnose_leaf_DXIYMRQWRZEOPK",
           "protected_rhamnose_leaf_FHJJHGKLMNWFAW",
           "protected_rhamnose_leaf_HLFFSCAGHKVLRS",
           "protected_rhamnose_leaf_PHJALNHKEFXHLQ",
           "protected_rhamnose_leaf_VWVYQJLOYLHJRF",
           "protected_rhamnose_leaf_WTGKXNNEXLYQBU",
           "protected_rhamnose_leaf_WUBVDUVHASUWBA",
           "protected_rhamnose_leaf_ZGEPWFMCYFOGJI"]:
    CHECKS[nm] = SKIP_INTERNAL


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    packets = [json.loads(l) for l in (VDIR / "identity_packets.jsonl").read_text(encoding="utf-8").splitlines()]
    stocks = [p for p in packets if p["kind"] == "stock"]
    assert len(stocks) == 49, f"expected 49 stocks, got {len(stocks)}"
    rows = []
    missing = []
    for s in stocks:
        name = s.get("name")
        chk = CHECKS.get(name)
        if chk is None:
            missing.append(name)
            continue
        rows.append({
            "stock_ref": s.get("ref"), "name": name,
            "stock_cid": (s.get("identity_evidence") or {}).get("source_id"),
            "inchikey": s.get("inchikey"),
            "check_status": chk["status"],
            "vendors": chk.get("vendors", []),
            "cas_note": chk.get("cas_note", ""),
            "flags": chk.get("flags", []),
            "notes": chk.get("notes", ""),
            "method": "public catalog web search, US results; no login, no paywall bypass",
            "retrieved_at": RETRIEVED,
        })
    if missing:
        raise SystemExit("uncovered stocks: " + "; ".join(missing))

    (VDIR / "vendor_checks.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")

    tally = {}
    for r in rows:
        tally[r["check_status"]] = tally.get(r["check_status"], 0) + 1
    summary = {
        "task": "TASK-015-P5-D2", "retrieved_at": RETRIEVED,
        "stocks_total": len(rows), "status_tally": tally,
        "boundary": "documentary evidence only; does not set current_vendor_evidence=approved; "
                    "no login or paywall bypass; prices as seen in public pages, not quotes",
    }
    (VDIR / "vendor_checks_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    mf_path = VDIR / "manifest.json"
    mf = json.loads(mf_path.read_text(encoding="utf-8"))
    mf["outputs_sha256"] = {f.name: sha(f) for f in sorted(VDIR.iterdir()) if f.is_file() and f.name != "manifest.json"}
    mf["d2_status_tally"] = tally
    mf["boundary"] = (mf.get("boundary", "") + "; D2 adds dated public-catalog vendor checks (2026-09-29)").strip("; ")
    mf_path.write_text(json.dumps(mf, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
