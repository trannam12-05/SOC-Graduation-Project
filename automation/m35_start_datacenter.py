import datetime as dt,json,subprocess
from topology_remote import remote,ROOT

code=r'''
import json,os,pathlib,subprocess,xml.etree.ElementTree as E,time
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');r=E.parse(lab).getroot();node=next(n for n in r.findall('.//node') if n.get('name')=='Data-Center')
running=[]
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[s.decode(errors='replace') for s in p.read_bytes().split(b'\0') if s]
  if a and 'qemu-system-' in os.path.basename(a[0]):running.append({'name':a[a.index('-name')+1],'ram_mib':int(a[a.index('-m')+1])})
 except (FileNotFoundError,ValueError):pass
mem=dict((x.split(':')[0],int(x.split()[1])) for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if len(x.split())>1 and x.split()[1].isdigit())
started=False
if not any(x['name']=='Data-Center' for x in running):
 total=sum(x['ram_mib'] for x in running)+int(node.get('ram'));assert total<=7168,total;assert mem['MemAvailable']>int(node.get('ram'))*1024+768*1024
 p=subprocess.run(['/opt/unetlab/wrappers/unl_wrapper','-a','start','-T','0','-F',str(lab),'-D',node.get('id')],capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr;started=True
print(json.dumps({'started':started,'node_id':node.get('id'),'ram_mib':int(node.get('ram')),'running_before':running,'meminfo_before':mem}))
'''
d=json.loads(remote(code,timeout=60));d['collected_at']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
out=ROOT/'docs/evidence/M3/M3.5-network-services-20261105';(out/'m35-start-datacenter.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(d))
