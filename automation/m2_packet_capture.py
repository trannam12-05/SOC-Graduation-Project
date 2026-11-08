"""PCAP giới hạn HTTP lab trên TAP endpoint, trunk Primary và cổng SPAN."""
import argparse,datetime,json
from topology_remote import remote,ROOT
p=argparse.ArgumentParser();p.add_argument('action',choices=['start','stop','collect-result']);a=p.parse_args()
out=ROOT/'docs/evidence/M2/final-acceptance-20261103';out.mkdir(parents=True,exist_ok=True)
START=r'''
import pathlib,subprocess,json,os,shutil
assert shutil.which('tcpdump'),'tcpdump not available; do not install automatically'
base=pathlib.Path('/root/soc-m2-final-pcaps-20261103');base.mkdir(mode=0o700,exist_ok=False)
links=json.loads(subprocess.run(['ip','-j','link','show'],capture_output=True,text=True,check=True).stdout)
names={i['ifname'] for i in links};devices={'dc30':'vunl0_4_0','client40':'vunl0_4_1','primary_trunk':'vunl0_1_0','span':'vunl0_3_7'}
assert set(devices.values()).issubset(names)
rows=[]
for label,iface in devices.items():
 log=(base/(label+'.stderr')).open('w')
 cmd=['tcpdump','-nn','-U','-s','0','-i',iface,'-w',str(base/(label+'.pcap')),'tcp port 8000 or tcp port 8001 or (vlan and (tcp port 8000 or tcp port 8001))']
 proc=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=log,start_new_session=True);log.close();rows.append({'label':label,'interface':iface,'pid':proc.pid,'cmd':cmd})
(base/'capture-processes.json').write_text(json.dumps(rows))
print(json.dumps({'base':str(base),'captures':rows,'links':[i for i in links if i['ifname'] in devices.values()]}))
'''
STOP=r'''
import pathlib,json,signal,os,time,base64
b=pathlib.Path('/root/soc-m2-final-pcaps-20261103');rows=json.loads((b/'capture-processes.json').read_text())
for r in rows:
 p=pathlib.Path('/proc')/str(r['pid'])/'cmdline'
 if p.exists():
  args=p.read_bytes().split(b'\0');assert args[0].endswith(b'tcpdump') and str(b).encode() in b' '.join(args)
  os.kill(r['pid'],signal.SIGINT)
time.sleep(1)
print(json.dumps({'captures':[{'label':r['label'],'bytes':(b/(r['label']+'.pcap')).stat().st_size,'pcap_b64':base64.b64encode((b/(r['label']+'.pcap')).read_bytes()).decode(),'stderr':(b/(r['label']+'.stderr')).read_text()} for r in rows]}))
'''
COLLECT=r'''
import pathlib,json
p=pathlib.Path('/opt/unetlab/tmp/0/f39cfc8c-5eaf-461e-bb0c-60b5fde848b7/4/serial.log')
rows=[]
for l in p.read_text(errors='replace').splitlines():
 if l.startswith('SOC_M2_RESULT '):
  try:
   d=json.loads(l[len('SOC_M2_RESULT '):])
   if d.get('session')=='soc-m2-final-20261103':rows.append(d)
  except ValueError:pass
print(json.dumps({'results':rows}))
'''
code={'start':START,'stop':STOP,'collect-result':COLLECT}[a.action]
d=json.loads(remote(code,timeout=30));d['collector_time']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
if a.action=='stop':
 import base64
 for c in d['captures']:(out/(c['label']+'.pcap')).write_bytes(base64.b64decode(c.pop('pcap_b64')))
(out/('packet-'+a.action+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
