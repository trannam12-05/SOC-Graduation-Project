"""Kiểm tra Manager hoặc append đúng một sự kiện; không cài/restart dịch vụ.

Chạy trong guest với root: audit | synthetic | real. Chỉ chạy hai chế độ
ghi sau khi audit xác nhận dịch vụ và localfile. Backup root-only trước append.
Kết quả công khai ra serial; cấu hình đầy đủ chỉ lưu root-only trong guest.
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

mode = sys.argv[1]
assert mode in ('audit', 'synthetic', 'real')
os.umask(0o077)
sid = 'soc-' + mode + '-' + uuid.uuid4().hex[:12]
out = Path('/root') / sid
out.mkdir(mode=0o700)
replay = Path('/var/log/soc-suricata-replay.json')
alerts = Path('/var/ossec/logs/alerts/alerts.json')


def run(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=20)
    return {'rc': p.returncode, 'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def matches_event(alert, event):
    if 'full_log' in alert:
        return json.loads(alert['full_log']) == event
    # Rule Suricata tích hợp không ghi full_log: đối chiếu dữ liệu giải mã.
    data = alert.get('data', {})
    keys = ('timestamp', 'event_type', 'in_iface', 'src_ip', 'dest_ip', 'proto', 'vlan')
    return (all(data.get(k) == event.get(k) for k in keys)
            and str(data.get('alert', {}).get('signature_id')) == str(event['alert']['signature_id'])
            and data.get('alert', {}).get('signature') == event['alert']['signature'])


r = {'session': sid, 'mode': mode, 'guest_time_untrusted': dt.datetime.now(dt.timezone.utc).isoformat(),
     'backup_directory': str(out), 'live_end_to_end': 'NOT_VERIFIED'}
try:
    r['service'] = run(['systemctl', 'is-active', 'wazuh-manager'])
    r['systemd'] = run(['systemctl', 'show', 'wazuh-manager', '-p', 'TimeoutStartUSec', '-p', 'DropInPaths', '-p', 'ActiveState', '-p', 'SubState'])
    r['enabled'] = run(['systemctl', 'is-enabled', 'wazuh-manager'])
    r['components'] = run(['/var/ossec/bin/wazuh-control', 'status'])
    r['version'] = run(['dpkg-query', '-W', 'wazuh-manager'])
    r['boot_id'] = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    conf = Path('/var/ossec/etc/ossec.conf')
    shutil.copy2(conf, out / 'ossec.conf.backup')
    root = ET.fromstring('<soc>' + conf.read_text() + '</soc>')
    r['replay_localfile'] = [dict((c.tag, c.text) for c in n) for n in root.iter('localfile') if n.findtext('location') == str(replay)]
    r['rules'] = []
    for p in Path('/var/ossec/etc/rules').glob('*.xml'):
        if '100101' in p.read_text():
            shutil.copy2(p, out / p.name)
            r['rules'].append({'name': p.name, 'sha256': digest(p.read_bytes()), 'text': p.read_text()})
    r['override_files'] = []
    for p in Path('/etc/systemd/system/wazuh-manager.service.d').glob('*.conf'):
        shutil.copy2(p, out / p.name)
        r['override_files'].append({'name': p.name, 'timeout_lines': [s for s in p.read_text().splitlines() if s.strip().startswith('TimeoutStartSec=')], 'sha256': digest(p.read_bytes())})
    assert replay.is_file() and not replay.is_symlink(), 'Replay absent or symlink'
    st = replay.stat()
    r['replay_before'] = {'bytes': st.st_size, 'lines': len(replay.read_bytes().splitlines()), 'mode': oct(st.st_mode & 0o777), 'uid': st.st_uid, 'gid': st.st_gid, 'sha256': digest(replay.read_bytes())}
    r['logcollector_process'] = run(['ps', '-C', 'wazuh-logcollector', '-o', 'pid,euser,egroup,comm'])
    log = Path('/var/ossec/logs/ossec.log').read_text(errors='replace').splitlines()
    r['collector_messages'] = [s for s in log if str(replay) in s][-8:]
    r['component_error_counts_last_500'] = {name: sum(name in s and ('ERROR' in s or 'WARNING' in s) for s in log[-500:]) for name in ('wazuh-logcollector', 'wazuh-analysisd')}
    r['rule_100101_existing'] = 0
    if alerts.exists():
        for line in alerts.read_text(errors='replace').splitlines():
            try:
                if str(json.loads(line).get('rule', {}).get('id')) == '100101':
                    r['rule_100101_existing'] += 1
            except ValueError:
                pass
    if mode != 'audit':
        assert r['service']['stdout'] == 'active', 'Manager not active'
        assert any(n.get('log_format') == 'json' for n in r['replay_localfile']), 'Missing JSON localfile'
        assert 'wazuh-logcollector is running' in r['components']['stdout'], 'Collector not running'
        if mode == 'synthetic':
            event = {'event_type': 'alert', 'alert': {'signature_id': 1000001, 'signature': 'SOC SYNTHETIC collector test'}, 'soc_test_id': sid, 'soc_test_kind': 'synthetic'}
            raw = (json.dumps(event, separators=(',', ':')) + '\n').encode()
        else:
            source = Path('/mnt/soc-seed/suricata-real-alert-replay.jsonl')
            assert source.is_file(), 'Seed source missing; do not invent real event'
            raw = source.read_bytes()
            assert len(raw.splitlines()) == 1 and raw.endswith(b'\n')
            event = json.loads(raw)
            assert event['alert']['signature_id'] == 1000001 and event['vlan'] == [30]
            # Hash nguồn Windows được truyền làm tham số; không tự tin cậy seed.
            assert digest(raw) == sys.argv[2], 'Real event source hash mismatch'
        shutil.copy2(replay, out / 'replay.before')
        (out / 'event.jsonl').write_bytes(raw)
        r['input_sha256'] = digest(raw)
        r['input_event'] = event
        test = subprocess.run(['/var/ossec/bin/wazuh-logtest'], input=raw.decode(), text=True, capture_output=True, timeout=20)
        r['logtest'] = {'rc': test.returncode, 'stdout': test.stdout, 'stderr': test.stderr}
        # Alert Suricata đầy đủ khớp rule tích hợp 86601 trong ruleset đã quan sát.
        r['expected_rule_id'] = '86601' if mode == 'real' else '100101'
        offset = alerts.stat().st_size if alerts.exists() else 0
        r['alerts_offset_before'] = offset
        with replay.open('ab') as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        found = []
        for _ in range(30):
            time.sleep(1)
            if not alerts.exists():
                continue
            assert alerts.stat().st_size >= offset, 'Alert file rotated; recheck manually'
            with alerts.open('rb') as f:
                f.seek(offset)
                rows = f.read().splitlines()
            for line in rows:
                try:
                    a = json.loads(line)
                    if str(a.get('rule', {}).get('id')) == r['expected_rule_id'] and a.get('location') == str(replay) and matches_event(a, event):
                        found.append(a)
                except (ValueError, TypeError):
                    pass
            if found:
                break
        r['new_matching_alerts'] = found
        r['result'] = ('PASS_REAL_REPLAY_NATIVE_RULE' if mode == 'real' else 'PASS_SYNTHETIC_COLLECTION') if found else 'NOT_VERIFIED_NO_NEW_MATCH'
    else:
        r['result'] = 'AUDIT_COLLECTED'
except Exception as e:
    r['result'] = 'ERROR'
    r['error'] = str(e)
(out / 'public-result.json').write_text(json.dumps(r, indent=2))
message = 'SOC_VERIFY_RESULT ' + json.dumps(r) + '\n'
print(message, flush=True)
with open('/dev/ttyS0', 'w') as f:
    f.write(message)
