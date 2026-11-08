"""Chỉ xuất các JSON công khai của verifier; không xuất raw serial/config."""
import datetime as dt
import json
from pathlib import Path
from topology_remote import remote, ROOT

code = r'''
import json,pathlib
p=pathlib.Path('/opt/unetlab/tmp/0/f39cfc8c-5eaf-461e-bb0c-60b5fde848b7/10/serial.log')
rows=[]
if p.exists():
 for line in p.read_text(errors='replace').splitlines():
  if not line.startswith('SOC_VERIFY_RESULT '):continue
  try:
   d=json.loads(line[len('SOC_VERIFY_RESULT '):])
   if d.get('mode') in ['audit','synthetic','real'] and d.get('session','').startswith('soc-'):rows.append(d)
  except ValueError:pass
print(json.dumps(rows))
'''
rows = json.loads(remote(code))
out = ROOT / 'docs/evidence/M5/continuation-20261102'
for row in rows:
    path = out / (row['session'] + '.json')
    if path.exists():
        continue
    row['collector_time'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    row['time_basis'] = 'Windows collector UTC+07:00; guest timestamps untrusted'
    with path.open('x', encoding='utf-8') as f:
        json.dump(row, f, ensure_ascii=False, indent=2)
print(json.dumps([{'session': r['session'], 'mode': r['mode'], 'result': r['result'], 'error': r.get('error'), 'service': r.get('service',{}).get('stdout'), 'existing_alerts':r.get('rule_100101_existing'), 'new_alerts':len(r.get('new_matching_alerts',[]))} for r in rows]))
