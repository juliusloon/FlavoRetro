"""A4 independent stdlib OOXML extraction; never reads A5 outputs."""
import zipfile,posixpath
from xml.etree import ElementTree as ET
from scripts.operate import ROOT
from scripts.task016_p7_r56_read_receipts import pre_read,complete
NS="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
def main():
 c,raw,start=pre_read("A4")
 with zipfile.ZipFile(ROOT/raw) as z:
  assert sum(x.file_size for x in z.infolist())<32*1024**2
  def xml(name):
   data=z.read(name);assert len(data)<8*1024**2 and b"<!DOCTYPE" not in data.upper()
   return ET.fromstring(data)
  ss=[]
  if "xl/sharedStrings.xml" in z.namelist():
   for item in xml("xl/sharedStrings.xml").findall("{"+NS+"}si"):
    ss.append("".join(t.text or "" for t in item.iter("{"+NS+"}t")))
  rels={r.attrib["Id"]:r.attrib["Target"] for r in xml("xl/_rels/workbook.xml.rels")}
  wb=xml("xl/workbook.xml");out=[]
  for s in wb.find("{"+NS+"}sheets"):
   target=rels[s.attrib["{"+REL+"}id"]]
   name=target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/"+target)
   assert name.startswith("xl/") and ".." not in name.split("/")
   root=xml(name);cells=[]
   for cell in root.iter("{"+NS+"}c"):
    v=cell.find("{"+NS+"}v");f=cell.find("{"+NS+"}f");inline=cell.find("{"+NS+"}is")
    rawv=None if v is None else v.text
    val=rawv
    if cell.attrib.get("t")=="s":val=ss[int(rawv)] if rawv is not None else None
    if cell.attrib.get("t")=="inlineStr":val="".join(t.text or "" for t in inline.iter("{"+NS+"}t")) if inline is not None else None
    cells.append(dict(reference=cell.attrib["r"],cell_type=cell.attrib.get("t"),style=cell.attrib.get("s"),raw_value=rawv,resolved_value=val,formula=None if f is None else f.text))
   dimension=root.find("{"+NS+"}dimension")
   merges=[x.attrib["ref"] for x in root.iter("{"+NS+"}mergeCell")]
   out.append(dict(name=s.attrib["name"],state=s.attrib.get("state"),sheet_path=name,dimension=None if dimension is None else dimension.attrib.get("ref"),merged_cells=merges,cells=cells))
 complete("A4",start,out,"stdlib zipfile + xml.etree.ElementTree")
if __name__=="__main__":main()
