"""Thu JSON public do guest ghi vào serial; không xuất toàn bộ serial hay config riêng."""
import json,datetime as dt
from topology_remote import remote,ROOT
CODE=r'''
import pathlib,json
base=pathlib.Path('/opt/unetlab/tmp/0/f39cfc8c-5eaf-461e-bb0c-60b5fde848b7')
rows=[]
for id,name in [('4','Data-Center'),('7','DMZ'),('10','Wazuh-SOC')]:
 p=base/id/'serial.log';valid=[]
 if p.exists():
  for line in p.read_text(errors='replace').splitlines():
   if 'SOC_BOOTSTRAP_RESULT ' not in line:continue
   try:d=json.loads(line.split('SOC_BOOTSTRAP_RESULT ',1)[1])
   except json.JSONDecodeError:continue
   if d.get('role')==name:valid.append(d)
 rows.append({'node':name,'serial_path':str(p),'result':valid[-1] if valid else None})
print(json.dumps(rows))
'''
if __name__=='__main__':
 rows=json.loads(remote(CODE));out=ROOT/'docs/evidence/M5/resume-20261102'
 for row in rows:
  if row['result'] is None:continue
  p=out/(row['node'].lower()+'-bootstrap-public.json');d={**row,'collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'time_basis':'Windows collector UTC+07:00; guest event times untrusted'}
  if p.exists() and json.loads(p.read_text())['result']!=d['result']:raise RuntimeError('Existing result differs; preserve both with a new evidence label')
  if not p.exists():p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps([{'node':r['node'],'state':r['result'].get('state') if r['result'] else 'NO_RESULT_YET','details':r['result']} for r in rows]))
