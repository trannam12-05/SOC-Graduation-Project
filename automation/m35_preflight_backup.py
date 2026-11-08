"""M3.5: kiểm kê và sao lưu topology trước khi boot/cấu hình."""
from pathlib import Path
import datetime as dt
import json
from topology_remote import ROOT, remote

OUT = ROOT / 'docs/evidence/M3/M3.5-network-services-20261105'
OUT.mkdir(parents=True, exist_ok=True)
code = r'''
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,xml.etree.ElementTree as E
lab=Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');raw=lab.read_bytes();root=E.fromstring(raw)
running=[]
for f in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[x.decode(errors='replace') for x in f.read_bytes().split(b'\0') if x]
  if a and ('qemu-system-' in os.path.basename(a[0]) or os.path.basename(a[0])=='vpcs'):running.append({'pid':f.parent.name,'name':a[a.index('-name')+1] if '-name' in a else a[0]})
 except (OSError,ValueError):pass
allowed={'SOC-Core-L2','OPNsense-Primary','OPNsense-Secondary'}
assert {x['name'] for x in running}.issubset(allowed),'Unexpected running node outside Core/HA pair'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup=Path('/root/soc-m35-preflight-'+stamp);backup.mkdir(mode=0o700)
shutil.copy2(lab,backup/'lab-before.unl');os.chmod(backup/'lab-before.unl',0o600)
assert (backup/'lab-before.unl').read_bytes()==raw
mem={x.split(':')[0]:int(x.split()[1]) for x in Path('/proc/meminfo').read_text().splitlines() if len(x.split())>1 and x.split()[1].isdigit()}
disks=[];tmp=Path('/opt/unetlab/tmp/0')/root.get('id')
for n in root.findall('.//node'):
 d=tmp/n.get('id')
 for p in d.glob('*.qcow2'):
  disks.append({'node':n.get('name'),'path':str(p),'bytes':p.stat().st_size,'format':subprocess.run(['/opt/qemu-2.12.0/bin/qemu-img','info','--output=json',str(p)],capture_output=True,text=True).stdout})
result={'lab':str(lab),'lab_id':root.get('id'),'lab_sha256':hashlib.sha256(raw).hexdigest(),'backup_directory':str(backup),'backup_sha256':hashlib.sha256((backup/'lab-before.unl').read_bytes()).hexdigest(),'nodes':[{**dict(n.attrib),'interfaces':[dict(i.attrib) for i in n.findall('interface')]} for n in root.findall('.//node')],'networks':[dict(n.attrib) for n in root.findall('.//network')],'running':running,'meminfo_kib':mem,'disk_metadata':disks,'scope':'Lab XML backup and read-only disk metadata with existing Core/HA pair running; guest config backup follows'}
(backup/'preflight.json').write_text(json.dumps(result,indent=2));os.chmod(backup/'preflight.json',0o600)
print(json.dumps(result))
'''
d=json.loads(remote(code,timeout=90));d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
(OUT/'preflight-and-host-backup.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'backup':d['backup_directory'],'lab_sha256':d['lab_sha256'],'eve_available_MiB':d['meminfo_kib']['MemAvailable']//1024,'nodes':len(d['nodes'])},ensure_ascii=False))
