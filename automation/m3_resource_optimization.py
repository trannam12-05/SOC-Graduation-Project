"""Checkpoint và kiểm kê tài nguyên; không xuất bí mật cấu hình guest."""
import json, datetime as dt, sys
from pathlib import Path
from topology_remote import remote, ROOT
OUT=ROOT/'docs/evidence/M3/resource-optimization-20261103'
def save(name,data):
    data['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    p=OUT/(name+'.json')
    with p.open('x',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
    return data
CODE=r'''
import pathlib,json,os,subprocess,xml.etree.ElementTree as E,hashlib,datetime,shutil
p=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');r=E.parse(p).getroot()
stamp=datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
b=pathlib.Path('/root/soc-resource-checkpoint-'+stamp);b.mkdir(mode=0o700)
shutil.copy2(p,b/p.name)
running=[]
for c in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[x.decode(errors='replace') for x in c.read_bytes().split(b'\0') if x]
  if a and 'qemu-system-' in os.path.basename(a[0]):
   running.append({'pid':int(c.parent.name),'name':a[a.index('-name')+1],'ram':a[a.index('-m')+1],'smp':a[a.index('-smp')+1]})
 except (OSError,ValueError):pass
commands={}
for name,cmd in [('free',['free','-m']),('vmstat',['vmstat','1','3']),('uptime',['uptime']),('oom',['journalctl','-k','-b','--no-pager','--grep','Out of memory|Killed process|oom-kill'])]:
 x=subprocess.run(cmd,capture_output=True,text=True,timeout=15);commands[name]={'rc':x.returncode,'stdout':x.stdout,'stderr':x.stderr}
print(json.dumps({'checkpoint':str(b),'lab_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nodes':[dict(n.attrib,interfaces=[dict(i.attrib) for i in n.findall('interface')]) for n in r.findall('.//node')],'running':running,'commands':commands,'meminfo':pathlib.Path('/proc/meminfo').read_text(),'cpu_count':os.cpu_count()}))
'''
if __name__=='__main__':
 d=save(sys.argv[1],json.loads(remote(CODE)))
 print(json.dumps({'checkpoint':d['checkpoint'],'running':d['running'],'commands':d['commands']},ensure_ascii=False))
