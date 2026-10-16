"""A5 independent lxml OOXML extraction; never reads A4 outputs."""
import io,zipfile,pathlib
from lxml import etree
from scripts.operate import ROOT
from scripts.task016_p7_r56_read_receipts import pre_read,complete
N={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships","p":"http://schemas.openxmlformats.org/package/2006/relationships"}
def main():
 c,raw,start=pre_read("A5")
 data=(ROOT/raw).read_bytes()
 archive=zipfile.ZipFile(io.BytesIO(data));assert sum(x.file_size for x in archive.infolist())<32*1024**2
 parser=etree.XMLParser(resolve_entities=False,no_network=True,load_dtd=False)
 def doc(p):
  blob=archive.read(p);assert len(blob)<8*1024**2 and b"<!DOCTYPE" not in blob.upper()
  return etree.fromstring(blob,parser)
 shared=[]
 if "xl/sharedStrings.xml" in archive.namelist():
  shared=["".join(node.xpath("./s:t/text() | ./s:r/s:t/text()",namespaces=N)) for node in doc("xl/sharedStrings.xml").xpath("./s:si",namespaces=N)]
 relationships={node.get("Id"):node.get("Target") for node in doc("xl/_rels/workbook.xml.rels").xpath("./p:Relationship",namespaces=N)}
 out=[]
 for sheet in doc("xl/workbook.xml").xpath("./s:sheets/s:sheet",namespaces=N):
  target=relationships[sheet.get("{"+N["r"]+"}id")]
  if target.startswith("/"):path=target[1:]
  else:
   parts=[]
   for part in ("xl/"+target).split("/"):
    if part in ("","."):continue
    if part=="..":parts.pop()
    else:parts.append(part)
   path="/".join(parts)
  assert path.startswith("xl/") and ".." not in path.split("/")
  node=doc(path);cells=[]
  for cell in node.xpath(".//s:sheetData/s:row/s:c",namespaces=N):
   values=cell.xpath("./s:v/text()",namespaces=N);value=values[0] if values else None
   result=value;kind=cell.get("t")
   if kind=="s":result=shared[int(value)] if value is not None else None
   elif kind=="inlineStr":result="".join(cell.xpath("./s:is/s:t/text() | ./s:is/s:r/s:t/text()",namespaces=N)) if cell.find("s:is",N) is not None else None
   formula=cell.xpath("./s:f/text()",namespaces=N)
   cells.append(dict(reference=cell.get("r"),cell_type=kind,style=cell.get("s"),raw_value=value,resolved_value=result,formula=formula[0] if formula else None))
  dims=node.xpath("./s:dimension/@ref",namespaces=N)
  out.append(dict(name=sheet.get("name"),state=sheet.get("state"),sheet_path=path,dimension=dims[0] if dims else None,merged_cells=node.xpath("./s:mergeCells/s:mergeCell/@ref",namespaces=N),cells=cells))
 complete("A5",start,out,"lxml XPath + independent in-memory ZIP cell decoding")
if __name__=="__main__":main()
