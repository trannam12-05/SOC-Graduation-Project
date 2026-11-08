import datetime as dt,json,time
from topology_remote import remote,ROOT

time.sleep(25)
CODE=r'''
import json,pathlib,telnetlib,time,xml.etree.ElementTree as E
r=E.parse('/opt/unetlab/labs/SOC-M2-Core-L2.unl').getroot();ports={n.get('name'):32768+int(n.get('id')) for n in r.findall('.//node')}
cases=[
 ('Employee','ping 192.168.40.1 -c 3 -w 1000','employee_carp_gateway'),
 ('Guest','ping 192.168.50.1 -c 3 -w 1000','guest_carp_gateway'),
 ('Management','ping 192.168.99.1 -c 3 -w 1000','management_carp_gateway'),
 ('Employee','ping opnsense.internal -c 1 -w 1000','employee_dns'),
 ('Guest','ping opnsense.internal -c 1 -w 1000','guest_dns'),
 ('Employee','ping 192.168.30.10 -P 6 -p 8000 -c 3 -w 1000','employee_to_dc_tcp8000_allow'),
 ('Guest','ping 192.168.30.10 -P 6 -p 8000 -c 3 -w 1000','guest_to_dc_tcp8000_deny')]
rows=[]
for node,cmd,name in cases:
 with telnetlib.Telnet('127.0.0.1',ports[node],timeout=6) as t:
  t.write(b'\r\n');time.sleep(.6);t.read_very_eager();t.write(b'show ip\r\n');time.sleep(1);t.read_very_eager();t.write(cmd.encode()+b'\r\n');data=b'';start=time.monotonic();last=start
  while time.monotonic()-start<14:
   time.sleep(.25);part=t.read_very_eager()
   if part:data+=part;last=time.monotonic()
   if cmd.encode() in data and b'>' in data and time.monotonic()-last>.6:break
  rows.append({'case':name,'node':node,'command':cmd,'output':data.decode(errors='replace'),'duration_s':round(time.monotonic()-start,2)})
print(json.dumps(rows))
'''
rows=json.loads(remote(CODE,timeout=150))
def ok(case,out):
 low=out.lower()
 if case.endswith('_dns'):return 'opnsense.internal resolved to ' in low
 if case.endswith('_deny'):return 'timeout' in low or '0/' in low or 'unreachable' in low
 return ('bytes from' in low or 'connect ' in low or 'connected' in low or 'open' in low) and not ('0/' in low and '3/' not in low)
for r in rows:r['passed']=ok(r['case'],r['output'])
d={'collected_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),
   'scope':'Actual VPCS traffic through Core L2 and OPNsense Primary CARP MASTER','cases':rows,
   'status':'PASS' if all(r['passed'] for r in rows) else 'REVIEW'}
out=ROOT/'docs/evidence/M3/M3.5-network-services-20261105';(out/'m35-live-tests.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
