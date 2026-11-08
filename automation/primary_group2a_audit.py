"""Backup root-only và xuất riêng cấu hình interface/VLAN công khai.

Chạy trong shell root Primary đã xác nhận. Không sửa XML, không apply hoặc
reload dịch vụ; không đọc/truyền nội dung chứng thư, mật khẩu hoặc API key.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as E

assert os.geteuid() == 0
work = Path(sys.argv[-1])
assert work.parent == Path('/root') and work.name.startswith('soc-group2a-')
os.umask(0o077)
work.mkdir(mode=0o700)
source = Path('/conf/config.xml')
raw = source.read_bytes()
tree = E.fromstring(raw)
assert tree.findtext('interfaces/lan/if') == 'vtnet0', 'Unexpected LAN parent; stop'
assert tree.findtext('interfaces/opt6/ipaddr') == '10.255.255.1', 'Not inspected Primary identity; stop'
backup = work / 'config.xml'
with backup.open('xb') as f:
    f.write(raw)
    f.flush()
    os.fsync(f.fileno())
backup.chmod(0o600)


def command(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=20)
    return {'rc': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}


interfaces = []
for n in tree.findall('interfaces/*'):
    interfaces.append({'assignment': n.tag, 'device': n.findtext('if'), 'description': n.findtext('descr'),
                       'ipaddr': n.findtext('ipaddr'), 'prefix': n.findtext('subnet'),
                       'enabled': n.find('enable') is not None})
vlans = []
for path in ['vlans/vlan', 'OPNsense/Interfaces/Vlan//vlan']:
    for n in tree.findall(path):
        vlans.append({'source_path': path, **{c.tag: c.text for c in n if c.tag in ['if', 'tag', 'vlanif', 'descr', 'proto', 'pcp']}})
devices = sorted({n['device'] for n in interfaces if n['device']})
runtime = {name: command(['ifconfig', name]) for name in devices}
mount = command(['mount'])
protected = ['system', 'cert', 'ca', 'nat', 'dhcpd', 'dhcpdv6', 'hasync', 'virtualip', 'gateways', 'staticroutes', 'filter', 'OPNsense']
hashes = {name: hashlib.sha256(E.tostring(tree.find(name))).hexdigest() if tree.find(name) is not None else None for name in protected}
current = source.read_bytes()
r = {'backup_path': str(backup), 'backup_sha256': hashlib.sha256(raw).hexdigest(), 'backup_bytes': len(raw),
     'backup_mode': oct(backup.stat().st_mode & 0o777), 'backup_directory_mode': oct(work.stat().st_mode & 0o777),
     'config_unchanged_during_audit': current == raw, 'protected_section_hashes': hashes,
     'interfaces': interfaces, 'vlan_definitions': vlans, 'runtime': runtime,
     'root_mount': [s for s in mount['stdout'].splitlines() if ' on / ' in s],
     'version': command(['opnsense-version']), 'ipv4_forwarding': command(['sysctl', '-n', 'net.inet.ip.forwarding']),
     'routes_ipv4': command(['netstat', '-rn', '-f', 'inet']), 'changes': [], 'traffic_tested': False}
(work / 'public-audit.json').write_text(json.dumps(r, indent=2))
print(json.dumps(r))
