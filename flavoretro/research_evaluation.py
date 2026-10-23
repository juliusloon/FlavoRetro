"""Private, immutable development ablation binding; no public search option."""
import json
from pathlib import Path
from .workspace import root,AssetError
from .resources import sha


def validate(binding,request):
    if set(binding)!={'protocol','protocol_sha256','cell_id','arm'}:raise AssetError('invalid evaluation binding')
    path=(root()/binding['protocol']).resolve()
    if not path.is_relative_to((root()/'outputs/task027').resolve()) or not path.is_file() or sha(path)!=binding['protocol_sha256']:raise AssetError('evaluation protocol drift')
    protocol=json.loads(path.read_text())
    if protocol.get('kind')!='task027_frozen_ablation_v1' or protocol.get('approval')!='agent_delegated' or protocol.get('human_reviewed') is not False:raise AssetError('unapproved evaluation protocol')
    for relative,expected in protocol['assets'].items():
        asset=(root()/relative).resolve()
        if not asset.is_relative_to(root().resolve()) or not asset.is_file() or sha(asset)!=expected:raise AssetError('frozen evaluation asset drift: '+relative)
    rows=[row for row in protocol['cells'] if row['cell_id']==binding['cell_id']]
    if len(rows)!=1 or rows[0]['arm']!=binding['arm'] or rows[0]['request']!=request.payload():raise AssetError('evaluation cell mismatch')
    return rows[0]
