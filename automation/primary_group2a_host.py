"""Chạy sau khi xác nhận shell root Primary; chỉ chuyển mã và JSON công khai.

Raw config.xml chỉ ở guest root-only, không đi qua ảnh console hoặc Git.
"""
import datetime as dt
import hashlib
import inspect
import json
from pathlib import Path
import sys
import textwrap
import types
import m2_console_job as transport
from topology_console_job import TopologyConsoleJob

root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
assert out.parent == root / 'docs/evidence/M2' and out.name.startswith('group2a-')
adapter = TopologyConsoleJob(out / 'console-transfer-primary', 'primary-group2a-20261102-215617', 'OPNsense-Primary')
files = {'guest.py': (root / 'automation/primary_group2a_audit.py').read_bytes()}
if '--reuse-stage' in sys.argv:
    # Launcher kiểm tra lại stage.ok trước khi chạy; không tin cậy file chưa hash.
    payload = json.dumps({name: raw.decode('utf-8') for name, raw in files.items()}).encode()
    adapter.payload_sha = hashlib.sha256(payload).hexdigest()
else:
    adapter.stage(files)
# Root console OPNsense dùng csh: chuyển riêng redirect launcher sang cú pháp csh.
original_command = adapter.command
def root_command(text):
    if text.endswith(' 2>&1 &'):
        prefix, tail = text.rsplit(' > ', 1)
        text = prefix + ' >& ' + tail[:-len(' 2>&1 &')] + ' &'
    return original_command(text)
adapter.command = root_command
# Tái dùng nguyên cơ chế hash/glyph; shell đã là root nên không gọi sudo.
source = textwrap.dedent(inspect.getsource(transport.ConsoleJob.run))
old = "args = ['sudo','-n','python3',"
assert source.count(old) == 1
namespace = {}
exec(source.replace(old, "args = ['python3',"), vars(transport), namespace)
adapter.run = types.MethodType(namespace['run'], adapter)
reply = adapter.run('audit', '/root/soc-group2a-20261102-215617')
data = json.loads(reply['stdout'])
data['collector_time'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
data['time_basis'] = 'Windows collector UTC+07:00; guest timestamps untrusted'
data['transport'] = 'Exact glyph decoding and whole reply SHA-256 verified; public data only'
with (out / 'primary-audit-before.json').open('x', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(json.dumps({'output': str(out / 'primary-audit-before.json'), 'backup_path_guest': data['backup_path'], 'backup_sha256': data['backup_sha256'], 'config_unchanged': data['config_unchanged_during_audit']}), flush=True)
