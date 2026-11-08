"""Đọc lại đúng vùng alert sau replay; giữ kết quả kiểm tra 100101 ban đầu.

Không append, không sửa rule. Bản dẫn xuất đối chiếu rule Suricata tích hợp.
"""
import json
from pathlib import Path

p = Path('/root/soc-real-fc29ab1fc31a/public-result.json')
r = json.loads(p.read_text())
f = open('/var/ossec/logs/alerts/alerts.json', 'rb')
f.seek(r['alerts_offset_before'])
found = []
for line in f:
    try:
        a = json.loads(line)
        if a.get('location') == '/var/log/soc-suricata-replay.json' and json.loads(a.get('full_log', '{}')) == r['input_event'] and str(a.get('rule', {}).get('id')) == '86601':
            found.append(a)
    except (ValueError, TypeError):
        pass
r['session'] = 'soc-real-native-fc29ab1fc31a'
r['original_verification'] = str(p)
r['original_result'] = r['result']
r['new_matching_alerts'] = found
r['result'] = 'PASS_REAL_REPLAY_NATIVE_RULE' if found else 'NOT_VERIFIED'
r['native_rule'] = '86601'
q = p.parent / 'native-rule-result.json'
with q.open('x') as f:
    json.dump(r, f, indent=2)
with open('/dev/ttyS0', 'w') as f:
    f.write('SOC_VERIFY_RESULT ' + json.dumps(r) + '\n')
print(r['result'], len(found))
