"""Sao lưu OVS đang chạy; chỉ đọc cấu hình, không sửa mạng hoặc thử frame.

OVSDB lấy qua ovsdb-client backup để có snapshot nhất quán. Payload được
truyền qua console có SHA-256; không sao chép đĩa guest đang chạy.
"""
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys

assert os.geteuid() == 0
source = Path('/root/m2-isolated-20261101T0035/guest.py')
assert hashlib.sha256(source.read_bytes()).hexdigest() == '263c27f2b85f742fd15e8f9eef0c44831e52ae1bbf4a18234e7b7387985c9123'
work = Path(sys.argv[-1])
assert work.parent == Path('/root') and work.name.startswith('m2-group1b-')
os.umask(0o077)
work.mkdir(mode=0o700)
spec = importlib.util.spec_from_file_location('retained', source)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
g.WORK = work
with contextlib.redirect_stdout(io.StringIO()):
    assert g.run(['hostname']).strip() == 'soc-core-l2'
    backup = work / 'ovsdb.snapshot'
    with backup.open('xb') as f:
        p = subprocess.run(['ovsdb-client', 'backup', 'unix:/var/run/openvswitch/db.sock', 'Open_vSwitch'], stdout=f, stderr=subprocess.PIPE, timeout=20)
    assert p.returncode == 0, p.stderr.decode()
    dbname = g.run(['ovsdb-tool', 'db-name', str(backup)]).strip()
    schema = g.run(['ovsdb-tool', 'db-version', str(backup)]).strip()
    assert dbname == 'Open_vSwitch'
    assert schema == g.run(['ovsdb-client', 'get-schema-version', 'unix:/var/run/openvswitch/db.sock', 'Open_vSwitch']).strip()
    g.run(['ovsdb-tool', 'compact', str(backup), str(work / 'ovsdb.validation-copy')])
    state = g.state('runtime')
    state['ports'] = g.table('Port', '_uuid,name,vlan_mode,tag,trunks,interfaces,lacp,bond_mode')
    state['mirrors'] = g.table('Mirror', '_uuid,name,select_all,select_src_port,select_dst_port,select_vlan,output_port,output_vlan')
    state['boot_id'] = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    state['noip_service'] = g.run(['systemctl', 'is-active', 'soc-core-l2-noip'], check=False).strip()
    state['noip_service_enabled'] = g.run(['systemctl', 'is-enabled', 'soc-core-l2-noip'], check=False).strip()
    units = g.run(['systemctl', 'cat', 'openvswitch-switch', 'ovsdb-server', 'ovs-vswitchd', 'soc-core-l2-noip'], check=False)
(work / 'runtime.json').write_text(json.dumps(state, indent=2))
(work / 'ovs-show.txt').write_text(state['show'])
(work / 'systemd-units.txt').write_text(units)
files = {}
for name in ['ovsdb.snapshot', 'runtime.json', 'ovs-show.txt', 'systemd-units.txt', 'commands.jsonl']:
    data = (work / name).read_bytes()
    files[name] = {'base64': base64.b64encode(data).decode(), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
print(json.dumps({'guest_backup_directory': str(work), 'database_name': dbname, 'schema': schema, 'files': files, 'config_changes': [], 'traffic_tested': False}))
