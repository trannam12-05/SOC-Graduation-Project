"""Chạy sau khi đã xác nhận console Core có shell và sudo -n.

Sao lưu mới, không ghi đè. Xuất OVSDB về thư mục private-backups trong M2,
đối chiếu checksum; các dữ liệu console trung gian được Git bỏ qua.
"""
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
from m2_console_job import ConsoleJob

root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
assert out.parent == root / 'docs/evidence/M2' and out.name.startswith('group1b-')
adapter = ConsoleJob(out / 'console-transfer-group1b', 'group1b-20261102-212014', shell_ready=True)
adapter.stage({'guest.py': (root / 'automation/m2_group1b_backup_guest.py').read_bytes()})
reply = adapter.run('backup', '/root/m2-group1b-20261102-212014')
data = json.loads(reply['stdout'])
target = out / 'private-backups'
target.mkdir(exist_ok=False)
rows = []
for name, item in data.pop('files').items():
    assert Path(name).name == name
    content = base64.b64decode(item['base64'], validate=True)
    assert len(content) == item['bytes'] and hashlib.sha256(content).hexdigest() == item['sha256']
    with (target / name).open('xb') as f:
        f.write(content)
    rows.append({'name': name, 'path': str(target / name), 'bytes': len(content), 'sha256': item['sha256']})
data['files'] = rows
data['collector_time'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
data['transport'] = 'Exact console glyph decoding; whole reply and each file SHA-256 verified'
with (out / 'backup-manifest.json').open('x', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
with (out / 'runtime.json').open('xb') as f:
    f.write((target / 'runtime.json').read_bytes())
print(json.dumps({'backup': str(target), 'manifest': str(out / 'backup-manifest.json'), 'files': len(rows), 'schema': data['schema']}), flush=True)
