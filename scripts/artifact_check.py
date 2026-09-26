"""Check built application resources and exclude local/limited payloads."""
import json
import sys
import tarfile
import zipfile
from pathlib import Path

folder=Path(sys.argv[1])
wheel=next(folder.glob("*.whl"));sdist=next(folder.glob("*.tar.gz"))
with zipfile.ZipFile(wheel) as archive:
    names=archive.namelist()
    assert all(f"flavoretro/assets/{kind}/{name}" in names for kind,name in (("web","index.html"),("web","app.js"),("web","style.css"),("configs","search.json"),("configs","teaching_guidance.json"),("configs","literature_teaching_layer.json")))
    assert not any(n.startswith(("data/","outputs/","metadata/","environment/","operations/")) or n.endswith((".onnx",".rdf",".sqlite")) for n in names)
with tarfile.open(sdist) as archive:
    names=archive.getnames()
    assert not any(any(part in n.split("/")[1:] for part in ("data","outputs","metadata","operations",".venv",".venv-foundation")) or n.endswith((".onnx",".rdf",".sqlite")) for n in names)
print(json.dumps({"wheel":str(wheel),"sdist":str(sdist),"local_payloads_excluded":True,"application_resources_included":True}))
