"""Thử qua console endpoint thật; lưu toàn bộ output, không suy từ exit process."""
import argparse,json,datetime as dt
from topology_remote import remote,ROOT
CODE=r'''
import telnetlib,time,json
cases=__CASES__
rows=[]
for node,port,command in cases:
 with telnetlib.Telnet('127.0.0.1',port,timeout=5) as t:
  time.sleep(0.4);pre=t.read_very_eager();t.write(b'\r\n');time.sleep(0.3);pre+=t.read_very_eager()
  t.write(command.encode()+b'\r\n');data=b'';start=time.monotonic();last=start
  while time.monotonic()-start<12:
   time.sleep(0.2);part=t.read_very_eager()
   if part:data+=part;last=time.monotonic()
   if b'>' in data and time.monotonic()-last>0.6:break
  rows.append({'node':node,'command':command,'output':data.decode(errors='replace'),'duration_s':round(time.monotonic()-start,2)})
print(json.dumps(rows))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['inventory','gateway','dc-http','guest-deny']);a=p.parse_args()
 cases={'inventory':[['Employee',32773,'show ip'],['Employee',32773,'set ?'],['Guest',32774,'show ip']],
        'gateway':[['Employee',32773,'ping 192.168.40.2 -c 3 -w 1000']],
        'dc-http':[['Employee',32773,'ping 192.168.30.10 -P 6 -p 8000 -c 3 -w 1000']],
        'guest-deny':[['Guest',32774,'ping 192.168.30.10 -P 6 -p 8000 -c 3 -w 1000']]}[a.phase]
 rows=json.loads(remote(CODE.replace('__CASES__',repr(cases)),timeout=90))
 d={'collected_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'scope':'Actual VPCS output; assess responses, not process exit','cases':rows}
 out=ROOT/'docs/evidence/M4/resume-20261102';out.mkdir(exist_ok=True)
 (out/('vpcs-'+a.phase+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(d))
