"""Đối chiếu JSON đã thu; không kết nối guest hoặc thay cấu hình."""
import datetime as dt
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
data = json.loads((out / 'primary-audit-before.json').read_text())
observed = json.loads((root / 'configs/M3/deployment-observed-20261102.json').read_text())['primary']['vlans']
rows = []
failures = []
for tag in [30, 40, 50, 60, 99]:
    defs = [v for v in data['vlan_definitions'] if v.get('tag') == str(tag)]
    unique = {(v.get('if'), v.get('vlanif')) for v in defs}
    if len(unique) != 1:
        failures.append(f'VLAN {tag}: definition absent or ambiguous')
        continue
    parent, device = next(iter(unique))
    assignments = [i for i in data['interfaces'] if i['device'] == device]
    if len(assignments) != 1:
        failures.append(f'VLAN {tag}: missing/ambiguous assignment for {device}')
        continue
    n = assignments[0]
    runtime = data['runtime'][device]
    text = runtime['stdout']
    address = str(n['ipaddr']) + '/' + str(n['prefix'])
    checks = {'parent_vtnet0': parent == 'vtnet0', 'address_matches_observed': address == observed[str(tag)],
              'enabled': n['enabled'], 'runtime_read_ok': runtime['rc'] == 0,
              'runtime_up': bool(text.splitlines()) and 'UP' in text.splitlines()[0],
              'runtime_tag_parent': bool(re.search(r'vlan:\s*' + str(tag) + r'\b.*?parent interface:\s*vtnet0\b', text, re.S)),
              'runtime_ipv4_prefix': bool(re.search(r'\binet\s+' + re.escape(n['ipaddr']) + r'\s+netmask\s+0xffffff00\b', text))}
    rows.append({'vlan': tag, 'assignment': n['assignment'], 'device': device, 'parent': parent,
                 'address_before': address, 'address_after': address, 'action': 'KEEP_UNCHANGED', 'checks': checks})
    failures += [f'VLAN {tag}: {k}' for k, ok in checks.items() if not ok]
parent_text = data['runtime'].get('vtnet0', {}).get('stdout', '')
if not re.search(r'ether\s+50:00:00:01:00:00\b', parent_text):
    failures.append('Parent MAC differs from historically verified Primary mapping')
if not data['config_unchanged_during_audit']:
    failures.append('Configuration changed during audit; stop before editing')
if data['ipv4_forwarding']['stdout'] != '1':
    failures.append('IPv4 forwarding is not 1; requires review outside VLAN assignment check')
if len(rows) != 5:
    failures.append('Not all five VLANs could be verified')
result = {'collector_time': dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),
          'status': 'MATCH_EXISTING_VLAN_CONFIGURATION' if not failures else 'STOP_REVIEW_REQUIRED',
          'before_after': rows, 'failures': failures, 'configuration_changes': [], 'traffic_tested': False,
          'scope': 'Interface/parent/tag/address configuration only; no firewall or traffic acceptance',
          'address_reference': 'Previously observed deployed Primary addresses, not unconfirmed M1 VIP proposals'}
with (out / 'primary-comparison.json').open('x', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps(result, ensure_ascii=True, indent=2))
