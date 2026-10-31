"""Đóng gói script và manifest; truyền qua console, không dùng mạng guest/QCOW2."""
import base64
import hashlib
import json
from pathlib import Path
import zlib

root = Path(__file__).resolve().parents[1]
stage = root/'staging/m2-ovs-takeover'
stage.mkdir(exist_ok=True)
audit = json.loads(sorted((root/'docs/evidence/M2').glob('M2-ovs-takeover-*-audit.json'))[-1].read_text())
assert audit['all_passed']
expected = {'indexes': [{'path': p['path'], 'sha256': p['sha256']} for p in audit['indexes']],
            'packages': [{'path': p['filename'], 'sha256': p['sha256'], 'Package': p['package'],
                          'Version': p['version'], 'Architecture': p['architecture']} for p in audit['packages']]}
script = (root/'automation/install_m2_ovs_offline_guest.py').read_text(encoding='utf-8')
files = {'install.py': script, 'm2-ovs-expected.json': json.dumps(expected)}
blob = base64.b64encode(zlib.compress(json.dumps(files).encode(),9)).decode()
destination = '/tmp/m2-ovs-takeover-2349'
commands = ['mkdir '+destination]
for start in range(0,len(blob),1200):
    commands.append("printf %s '"+blob[start:start+1200]+"' >> "+destination+'/payload.b64')
commands.append("python3 -c 'import base64,zlib,json,pathlib; p=pathlib.Path(\""+destination+"\"); d=json.loads(zlib.decompress(base64.b64decode((p/\"payload.b64\").read_bytes()))); [(p/k).write_text(v) for k,v in d.items()]'; sha256sum "+destination+'/install.py')
for i, command in enumerate(commands):
    (stage/f'command-{i:02d}.txt').write_text(command,encoding='utf-8')
(stage/'m2-ovs-expected.json').write_text(json.dumps(expected,indent=2),encoding='utf-8')
print(json.dumps({'commands':len(commands),'destination':destination,'script_sha256':hashlib.sha256(script.encode()).hexdigest()}))
