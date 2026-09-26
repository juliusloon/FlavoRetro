"""Runtime workspace is separate from installed, read-only application resources."""
import json
import os
import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent

class AssetError(ValueError):
    """Missing, stale or corrupt local assets; never silently fall back."""

def root():
    explicit = os.environ.get("FLAVORETRO_WORKSPACE")
    if explicit:
        return Path(explicit).expanduser().resolve()
    checkout = PACKAGE.parent
    return checkout if (checkout / "PROJECT.md").is_file() else Path.home() / ".local/share/flavoretro"

def configure(path):
    if path:
        os.environ["FLAVORETRO_WORKSPACE"] = str(Path(path).expanduser().resolve())
    return root()

def config_path(name):
    if name not in {"search.json", "teaching_guidance.json", "literature_teaching_layer.json"}:
        raise ValueError("unknown application configuration")
    override = root() / "configs" / name
    return override if override.is_file() else PACKAGE / "assets/configs" / name

def config(name):
    return json.loads(config_path(name).read_text())

def active_data():
    from .resources import sha
    pointer = root() / "metadata/active.json"
    if not pointer.is_file():
        raise AssetError("missing_assets: configure FLAVORETRO_WORKSPACE and restore sources; see environment/README.md")
    state = json.loads(pointer.read_text())
    version = state.get("version", "")
    if state.get("schema_version") != 1 or not re.fullmatch(r"[A-Za-z0-9_-]+", version):
        raise AssetError("invalid active resource pointer")
    folder = root() / "data/derived" / version
    try:
        manifest_path = folder / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        checks = [(manifest_path, state["manifest_sha256"]),
                  (folder / "records.json", manifest["records_sha256"]),
                  (root() / "metadata/sources.json", manifest["sources_sha256"])]
        if any(sha(p) != expected for p, expected in checks):
            raise AssetError("resource_integrity_failed: version/source hash mismatch; restore or rebuild a new immutable version")
    except (FileNotFoundError, KeyError) as exc:
        raise AssetError("missing_assets: restore the active resource version and its sources") from exc
    return folder, manifest, state
