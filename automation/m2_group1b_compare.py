"""Đối chiếu snapshot runtime đã thu; không gửi lệnh hoặc tạo lưu lượng."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
from m2_mirror_guest_prepared import check

root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
assert out.parent == root / 'docs/evidence/M2' and out.name.startswith('group1b-')
s = json.loads((out / 'runtime.json').read_text())
manifest = json.loads((out / 'backup-manifest.json').read_text())
for row in manifest['files']:
    assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['sha256']
old_path = root / 'docs/evidence/M2/live-tests-20261101/final-collection/guest-public-replies/postboot-readonly-console__export-5-verified-reply.json'
old = json.loads(json.loads(old_path.read_text())['stdout'])['state']


def mirrors(state):
    ports = {p['_uuid']: p['name'] for p in state['ports']}
    def names(value):
        return sorted(ports[x] for x in (value if isinstance(value, list) else [value]))
    return sorted([{'name': m['name'], 'select_all': m['select_all'],
                    'source_ports': names(m['select_src_port']), 'destination_ports': names(m['select_dst_port']),
                    'vlans': sorted(m['select_vlan']), 'output_ports': names(m['output_port']),
                    'output_vlan': m.get('output_vlan', [])} for m in state['mirrors']], key=lambda x: x['name'])


failures = []
try:
    check(s, mirror=True)
except AssertionError as e:
    failures.append('Strict historical Core guards: ' + (str(e) or 'mismatch; inspect saved runtime'))
if mirrors(s) != mirrors(old):
    failures.append('Mirror differs from historical verified configuration; do not change')
if any(p['lacp'] not in ([], 'off') for p in s['ports']):
    failures.append('Unexpected LACP configuration; do not change')
if s['noip_service'] != 'active' or s['noip_service_enabled'] != 'enabled':
    failures.append('No-IP persistence service differs; outside VLAN-only correction scope')
result = {'collector_time': dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),
          'status': 'MATCH_CONFIRMED_CONFIGURATION' if not failures else 'STOP_UNEXPLAINED_DIFFERENCE',
          'failures': failures, 'configuration_changes': [], 'traffic_tested': False,
          'lacp': 'NOT_APPLICABLE_NO_CONFIGURATION', 'historical_mirror': mirrors(old),
          'current_mirror': mirrors(s), 'boot_id': s['boot_id'],
          'scope': 'Runtime configuration comparison only; no new functional traffic acceptance'}
with (out / 'comparison.json').open('x', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps(result, ensure_ascii=True, indent=2))
