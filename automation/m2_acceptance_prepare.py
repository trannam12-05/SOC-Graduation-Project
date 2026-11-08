"""Chuẩn bị M2 được duyệt: backup topology, thêm NIC client cô lập, boot tối thiểu."""
from pathlib import Path
import datetime, json, subprocess
from topology_remote import remote, ROOT
OUT=ROOT/'docs/evidence/M2/final-acceptance-20261103'
OUT.mkdir(parents=True,exist_ok=True)
win=subprocess.run(['powershell.exe','-NoProfile','-Command','$o=Get-CimInstance Win32_OperatingSystem; @{available_kib=[long]$o.FreePhysicalMemory;commit_available_kib=[long]$o.FreeVirtualMemory}|ConvertTo-Json'],capture_output=True,text=True,check=True)
w=json.loads(win.stdout)
assert w['commit_available_kib']>2*1024*1024,'Windows commit reserve below 2 GiB'
CODE=r'''
import pathlib,json,subprocess,xml.etree.ElementTree as E,os,hashlib,shutil,base64
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');raw=lab.read_bytes();r=E.fromstring(raw)
ns={n.get('name'):n for n in r.findall('.//node')}
def running():
 rows=[]
 for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
  try:
   a=[s.decode(errors='replace') for s in p.read_bytes().split(b'\0') if s]
   if a and 'qemu-system-' in os.path.basename(a[0]):rows.append({'name':a[a.index('-name')+1],'uuid':a[a.index('-uuid')+1],'ram_mib':int(a[a.index('-m')+1])})
   elif a and os.path.basename(a[0])=='vpcs':raise RuntimeError('VPCS is running; cannot ensure unique client IP')
  except (OSError,ValueError):pass
 return rows
before=running();assert {x['name'] for x in before}.issubset({'OPNsense-Primary','SOC-Core-L2','Data-Center'})
dc=ns['Data-Center'];assert not any(x['uuid']==dc.get('uuid') for x in before),'DC must be stopped before NIC change'
mem=dict((s.split(':')[0],int(s.split()[1])) for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if len(s.split())>1 and s.split()[1].isdigit())
required=sum(int(ns[x].get('ram')) for x in ['OPNsense-Primary','SOC-Core-L2','Data-Center'])
new=sum(int(ns[x].get('ram')) for x in ['OPNsense-Primary','SOC-Core-L2','Data-Center'] if x not in {n['name'] for n in before})
assert required*1024<=mem['MemTotal']-1024*1024,'Nominal guest allocation exceeds physical RAM reserve'
assert mem['MemAvailable']>new*1024+1024*1024,'EVE live memory reserve insufficient'
assert mem['SwapTotal']==mem['SwapFree'],'Swap already in use; stop for review'
assert dc.get('ethernet')=='1'
net40=next(i.get('network_id') for i in ns['Employee'].findall('interface') if i.get('id')=='0')
net30=next(i.get('network_id') for i in dc.findall('interface') if i.get('id')=='0')
assert net40!=net30
backup=pathlib.Path('/root/soc-m2-final-20261103-backup');backup.mkdir(mode=0o700,exist_ok=False)
(backup/'lab-before.unl').write_bytes(raw);os.chmod(backup/'lab-before.unl',0o600)
php="""<?php chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');$l=new Lab('/opt/unetlab/labs/SOC-M2-Core-L2.unl',0);$rc=$l->editNode(array('id'=>__ID__,'ethernet'=>2));if($rc!==0)throw new Exception('editNode failed');$rc=$l->connectNode(__ID__,array('1'=>'__NET__'));if($rc!==0)throw new Exception('connectNode failed');echo json_encode(array('nic_added'=>1));?>""".replace('__ID__',dc.get('id')).replace('__NET__',net40)
p=subprocess.run(['php'],input=php,text=True,capture_output=True,check=True);change=json.loads(p.stdout)
after=E.parse(lab).getroot();newns={n.get('name'):n for n in after.findall('.//node')}
for name,n in ns.items():
 m=newns[name]
 if name!='Data-Center':assert E.tostring(n)==E.tostring(m),'Protected node changed: '+name
 else:
  assert m.get('ethernet')=='2'
  for k,v in n.attrib.items():
   if k!='ethernet':assert m.get(k)==v
  for i in n.findall('interface'):assert next(z for z in m.findall('interface') if z.get('id')==i.get('id')).attrib==i.attrib
assert next(i.get('network_id') for i in newns['Data-Center'].findall('interface') if i.get('id')=='1')==net40
oldnets=[dict(x.attrib) for x in r.findall('.//network')]
newnets=[dict(x.attrib) for x in after.findall('.//network')]
# EVE connectNode tự bật hiển thị segment được nối; chỉ khác cờ trình bày visibility.
assert [{k:v for k,v in x.items() if k!='visibility'} for x in oldnets]==[{k:v for k,v in x.items() if k!='visibility'} for x in newnets]
change['network_visual_changes']=[{'id':a['id'],'visibility_before':a.get('visibility'),'visibility_after':b.get('visibility')} for a,b in zip(oldnets,newnets) if a!=b]
starts=[]
for name in ['OPNsense-Primary','SOC-Core-L2','Data-Center']:
 if name in {x['name'] for x in running()}:continue
 m=dict((s.split(':')[0],int(s.split()[1])) for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if len(s.split())>1 and s.split()[1].isdigit())
 assert m['MemAvailable']>int(ns[name].get('ram'))*1024+1024*1024,'RAM guard before '+name
 p=subprocess.run(['/opt/unetlab/wrappers/unl_wrapper','-a','start','-T','0','-F',str(lab),'-D',ns[name].get('id')],capture_output=True,text=True,timeout=30)
 starts.append({'node':name,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'mem_available_kib_before':m['MemAvailable']})
 assert p.returncode==0,'Start failed: '+name
print(json.dumps({'backup':str(backup/'lab-before.unl'),'lab_sha256_before':hashlib.sha256(raw).hexdigest(),'lab_sha256_after':hashlib.sha256(lab.read_bytes()).hexdigest(),'change':change,'client_method':'Linux netns inside DC, NIC1 on existing VLAN40 segment; VPCS off','network30':net30,'network40':net40,'nominal_ram_mib':required,'starts':starts,'running':running(),'meminfo_before':mem,'lab_after_base64':base64.b64encode(lab.read_bytes()).decode()}))
'''
import sys
if '--resume' in sys.argv:
 # NIC đã được thêm nhưng kiểm tra nhánh XML networks sai đường dẫn đã chặn trước start.
 # Đọc lại backup để đối chiếu, không chạy lại editNode/connectNode.
 CODE=CODE.replace('raw=lab.read_bytes();r=E.fromstring(raw)',"raw=pathlib.Path('/root/soc-m2-final-20261103-backup/lab-before.unl').read_bytes();r=E.fromstring(raw)")
 a=CODE.index("backup=pathlib.Path('/root/soc-m2-final-20261103-backup')")
 b=CODE.index('after=E.parse(lab).getroot()',a)
 CODE=CODE[:a]+"backup=pathlib.Path('/root/soc-m2-final-20261103-backup');change={'nic_added':1,'resume_validation_only':True}\n"+CODE[b:]
try:
 d=json.loads(remote(CODE,timeout=100));import base64
 (OUT/'lab-client-topology.unl').write_bytes(base64.b64decode(d.pop('lab_after_base64')))
 d['windows_before']=w;d['collector_time']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
 (OUT/'prepare-receipt.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
 print(json.dumps(d))
except Exception as e:
 (OUT/'prepare-error.json').write_text(json.dumps({'error':str(e),'action':'Inspect state before further changes'}),encoding='utf-8');raise
