"""Bật đúng một node trong nhóm nhỏ, kiểm tài nguyên và lưu receipt thực tế."""
import json,datetime as dt,argparse
from topology_remote import remote,ROOT
import subprocess
p=argparse.ArgumentParser();p.add_argument('node',choices=['Suricata-NIDS','Data-Center','DMZ','Wazuh-SOC','SOC-Core-L2','OPNsense-Primary']);a=p.parse_args()
win=subprocess.run(['powershell.exe','-NoProfile','-Command','$o=Get-CimInstance Win32_OperatingSystem; @{available_kib=[long]$o.FreePhysicalMemory;commit_available_kib=[long]$o.FreeVirtualMemory}|ConvertTo-Json'],capture_output=True,text=True,check=True)
windows=json.loads(win.stdout)
assert windows['commit_available_kib']>2*1024*1024,'Windows commit reserve below 2 GiB'
code=r'''
import pathlib,subprocess,json,xml.etree.ElementTree as E,os
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');r=E.parse(lab).getroot()
node=next(n for n in r.findall('.//node') if n.get('name')==__NODE__)
running=[]
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[s.decode(errors='replace') for s in p.read_bytes().split(b'\0') if s]
  if a and 'qemu-system-' in os.path.basename(a[0]):running.append({'name':a[a.index('-name')+1],'ram_mib':int(a[a.index('-m')+1])})
 except (FileNotFoundError,ValueError):pass
assert not any(x['name']==node.get('name') for x in running),'Already running; refusing duplicate start'
total=sum(x['ram_mib'] for x in running)+int(node.get('ram'))
names={x['name'] for x in running}|{node.get('name')}
limit=6144 if names.issubset({'OPNsense-Primary','OPNsense-Secondary'}) or names.issubset({'OPNsense-Primary','SOC-Core-L2','Suricata-NIDS'}) or names.issubset({'Wazuh-SOC','Data-Center','DMZ'}) else 5120
assert total<=limit,'Group exceeds RAM budget'
mem=dict((l.split(':')[0],int(l.split()[1])) for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if len(l.split())>1 and l.split()[1].isdigit())
assert mem['MemAvailable']>int(node.get('ram'))*1024+1024*1024,'Insufficient EVE reserve'
p=subprocess.run(['/opt/unetlab/wrappers/unl_wrapper','-a','start','-T','0','-F',str(lab),'-D',node.get('id')],text=True,capture_output=True,timeout=30)
assert p.returncode==0,p.stderr
print(json.dumps({'node':node.get('name'),'id':node.get('id'),'group_nominal_MiB':total,'already_running':running,'eve_meminfo':mem,'wrapper_returncode':p.returncode,'scope':'Start requested, boot not yet verified'}))
'''.replace('__NODE__',repr(a.node))
result=json.loads(remote(code));result['windows']=windows;result['collected_at']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
out=ROOT/'docs/evidence/M2/topology-first-20261102';file=out/('start-'+a.node+'-'+dt.datetime.now().strftime('%H%M%S')+'.json');file.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'node':a.node,'group_nominal_MiB':result['group_nominal_MiB'],'receipt':str(file)}))
