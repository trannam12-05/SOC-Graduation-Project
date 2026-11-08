"""Dựng phần topology đã có đặc tả; giữ node tắt, không sửa cấu hình guest."""
import base64, json, datetime as dt
from pathlib import Path
from topology_remote import remote, ROOT

PLAN=json.loads((ROOT/'configs/topology-first-plan.json').read_text(encoding='utf-8'))
EV=ROOT/'docs/evidence/M2/topology-first-20261102'
CODE=r'''
import base64,json,pathlib,subprocess,hashlib,shutil,datetime,os,xml.etree.ElementTree as E,uuid
plan=json.loads(base64.b64decode('__PLAN__'))
lab=pathlib.Path(plan['lab']); initial=lab.read_bytes()
assert hashlib.sha256(initial).hexdigest()==plan['expected_before_sha256'],'Lab changed; re-audit required'
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  args=p.read_bytes().split(b'\0')
  assert not (args and b'qemu-system-' in args[0]),'A QEMU is running; no mutation'
 except FileNotFoundError:pass
root=E.fromstring(initial); oldnodes={n.get('name'):n for n in root.findall('.//node')}
assert set(oldnodes)=={'SOC-Core-L2','OPNsense-Primary','OPNsense-Secondary'}
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=pathlib.Path('/root/soc-topology-first-backup-'+stamp);backup.mkdir(mode=0o700)
shutil.copy2(lab,backup/'lab-before.unl')
disk_manifest=[]
tmp=pathlib.Path('/opt/unetlab/tmp/0')/root.get('id')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert shutil.disk_usage(lab).free>8*1024**3
for name,n in oldnodes.items():
 for p in (tmp/n.get('id')).glob('*.qcow2'):
  target=backup/(name+'-'+p.name);shutil.copy2(p,target)
  s=sha(p);assert sha(target)==s
  disk_manifest.append({'node':name,'source':str(p),'backup':str(target),'sha256':s,'bytes':p.stat().st_size})
(backup/'manifest.json').write_text(json.dumps(disk_manifest,indent=2))
qemu='/opt/qemu-2.12.0/bin/qemu-img'
base=pathlib.Path('/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs/virtioa.qcow2')
base_before=sha(base)
positions={'OPNsense-Primary':(350,190),'OPNsense-Secondary':(770,190),'SOC-Core-L2':(560,365),
 'Data-Center':(125,610),'Employee':(330,610),'Guest':(535,610),'DMZ':(740,610),'Management':(945,610),
 'Suricata-NIDS':(1120,365),'Wazuh-SOC':(1120,550)}
newparams=[]
for row in plan['nodes']:
 name=row['name']
 if name in oldnodes:continue
 left,top=positions[name]
 if name in ['Employee','Guest','Management']:
  p={'type':'vpcs','template':'vpcs','name':name,'console':'telnet','ethernet':1,'ram':64,'icon':'PC-2D-Gen-White-S.svg','left':left,'top':top,'config':'0','delay':0}
 else:
  directory=pathlib.Path('/opt/unetlab/addons/qemu/linux-soc-'+name.lower())
  assert not directory.exists(),'Refuse image overwrite'
  directory.mkdir(mode=0o755)
  subprocess.run([qemu,'create','-f','qcow2','-F','qcow2','-b',str(base),str(directory/'virtioa.qcow2'),'40G' if name=='Wazuh-SOC' else '12G'],check=True,capture_output=True)
  os.chmod(directory/'virtioa.qcow2',0o644)
  p={'type':'qemu','template':'linux','name':name,'image':directory.name,'console':'vnc','cpu':2 if name=='Wazuh-SOC' else 1,'cpulimit':1,
   'ram':4096 if name=='Wazuh-SOC' else 1024,'ethernet':row['nic_count'],'uuid':str(uuid.uuid4()),
   'firstmac':'02:54:'+':'.join('%02x'%v for v in os.urandom(3))+':00',
   'qemu_arch':'x86_64','qemu_version':'2.12.0','qemu_nic':'virtio-net-pci',
   'qemu_options':'-machine type=pc,accel=kvm -vga std -usbdevice tablet -boot order=c -cpu host',
   'delay':0,'icon':'Server-2D-Linux-S.svg','config':'0','left':left,'top':top}
 newparams.append(p)
payload={'nodes':newparams,'positions':positions,'lab':str(lab)}
php=r"""<?php
chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');
$p=json_decode(base64_decode('__PAYLOAD__'),true);$l=new Lab($p['lab'],0);
function ok($rc){if($rc!==0)throw new Exception('EVE operation failed: '.$rc);}
foreach($p['nodes'] as $n)ok($l->addNode($n));
foreach($l->getNodes() as $id=>$n){$pos=$p['positions'][$n->getName()];$v=array('id'=>$id,'left'=>$pos[0],'top'=>$pos[1]);if(in_array($n->getName(),array('OPNsense-Primary','OPNsense-Secondary')))$v['ethernet']=4;ok($l->editNode($v));}
$out=array();foreach($l->getNodes() as $id=>$n)$out[]=array('id'=>$id,'name'=>$n->getName(),'status'=>$n->getStatus(),'ethernet'=>$n->getEthernetCount());
echo json_encode($out);?>"""
php=php.replace('__PAYLOAD__',base64.b64encode(json.dumps(payload).encode()).decode())
p=subprocess.run(['php'],input=php,text=True,capture_output=True);assert p.returncode==0,p.stderr
created=json.loads(p.stdout);assert len(created)==10 and all(n['status']==0 for n in created)
# Sau đủ node mới dựng link; ba segment cũ giữ nguyên ID và cả hai đầu.
nodesroot=E.parse(lab).getroot()
(backup/'lab-nodes-created.unl').write_bytes(lab.read_bytes())
netdefs=[('WAN-ISP-1',290,65,1),('WAN-ISP-2',820,65,1),('VLAN30-Data-Center',125,520,0),('VLAN40-Employee',330,520,0),
 ('VLAN50-Guest',535,520,0),('VLAN60-DMZ',740,520,0),('VLAN99-Management',945,520,1),('SPAN-Capture',1000,365,0)]
php2=r"""<?php chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');
$p=json_decode(base64_decode('__PAYLOAD__'),true);$l=new Lab($p['lab'],0);
function ok($rc){if($rc!==0)throw new Exception('EVE link operation failed '.$rc);}
foreach($p['nets'] as $v)ok($l->addNetwork(array('name'=>$v[0],'left'=>$v[1],'top'=>$v[2],'visibility'=>$v[3],'type'=>'bridge','icon'=>'lan.png')));
$nets=array();foreach($l->getNetworks() as $id=>$n)$nets[$n->getName()]=$id;
$ns=array();foreach($l->getNodes() as $id=>$n)$ns[$n->getName()]=$id;
foreach($p['connections'] as $name=>$ports){$v=array();foreach($ports as $port=>$net)$v[$port]=(string)$nets[$net];ok($l->connectNode($ns[$name],$v));}
echo json_encode(array('nodes'=>$ns,'networks'=>$nets));?>"""
connections={
 'OPNsense-Primary':{'1':'WAN-ISP-1','3':'WAN-ISP-2'},'OPNsense-Secondary':{'1':'WAN-ISP-1','3':'WAN-ISP-2'},
 'SOC-Core-L2':{'0':'VLAN30-Data-Center','1':'VLAN40-Employee','2':'VLAN50-Guest','3':'VLAN60-DMZ','4':'VLAN99-Management','7':'SPAN-Capture'},
 'Data-Center':{'0':'VLAN30-Data-Center'},'Employee':{'0':'VLAN40-Employee'},'Guest':{'0':'VLAN50-Guest'},'DMZ':{'0':'VLAN60-DMZ'},
 'Management':{'0':'VLAN99-Management'},'Suricata-NIDS':{'0':'SPAN-Capture','1':'VLAN99-Management'}}
payload2={'lab':str(lab),'nets':netdefs,'connections':connections}
php2=php2.replace('__PAYLOAD__',base64.b64encode(json.dumps(payload2).encode()).decode())
p=subprocess.run(['php'],input=php2,text=True,capture_output=True);assert p.returncode==0,p.stderr
linkresult=json.loads(p.stdout)
after=E.parse(lab).getroot();newnodes={n.get('name'):n for n in after.findall('.//node')}
for name,old in oldnodes.items():
 new=newnodes[name]
 for k,v in old.attrib.items():
  if k not in ['left','top','ethernet']:assert new.get(k)==v,(name,k)
 for interface in old.findall('interface'):
  newif=next(i for i in new.findall('interface') if i.get('id')==interface.get('id'))
  assert newif.attrib==interface.attrib,'Existing link changed'
assert sha(base)==base_before
for d in disk_manifest:assert sha(pathlib.Path(d['source']))==d['sha256'],'Existing runtime disk changed'
os.chmod(lab,0o664)
(backup/'lab-after.unl').write_bytes(lab.read_bytes())
result={'backup_directory':str(backup),'backup_disks':disk_manifest,'nodes_after_creation':created,'link_result':linkresult,
 'lab_sha256_before':hashlib.sha256(initial).hexdigest(),'lab_sha256_after':sha(lab),'protected_existing_disks_unchanged':True,
 'protected_existing_attributes_and_links_unchanged':True,'base_image_unchanged':True,'nodes_started':0,
 'unresolved':plan['unresolved'],'completed_at_remote_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(backup/'build-receipt.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');o=p.parse_args()
    if not o.execute:raise SystemExit('Prepared; --execute required to change EVE')
    result=json.loads(remote(CODE.replace('__PLAN__',base64.b64encode(json.dumps(PLAN).encode()).decode()),timeout=300))
    result['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    (EV/'build-receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True))
