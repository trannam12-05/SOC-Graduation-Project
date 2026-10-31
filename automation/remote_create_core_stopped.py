"""Chay tren EVE bang SSH: chi tao image moi va lab/node moi GIU TAT.

Full copy doc base, resize ban moi, qemu-img check/compare; EVE Lab/Node native
classes tao file lab va 8 interface. Khong goi start/stop/wipe/fixpermissions.
"""
import glob
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid
import xml.etree.ElementTree as ET

BASE=Path('/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs/virtioa.qcow2')
TARGET=Path('/opt/unetlab/addons/qemu/linux-ubuntu-24.04-soc-core-l2')
LAB=Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl')
QEMU='/opt/qemu-2.12.0/bin/qemu-img'
EXPECTED='04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def execute(args,input=None):
    p=subprocess.run(args,input=input,text=True,capture_output=True,timeout=120)
    if p.returncode:raise RuntimeError('Failed '+repr(args)+': '+p.stdout+p.stderr)
    return {'args':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}

assert not TARGET.exists() and not LAB.exists(), 'Destination exists; refusing overwrite'
assert shutil.disk_usage(BASE.parent).free>3*1024**3
assert digest(BASE)==EXPECTED
protected={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in glob.glob('/opt/unetlab/labs/**/*.unl',recursive=True)+['/opt/unetlab/html/templates/intel/linux.yml','/opt/unetlab/html/templates/amd/linux.yml']}
TARGET.mkdir(mode=0o755)
disk=TARGET/'virtioa.qcow2'
with BASE.open('rb') as source,disk.open('xb') as dest: shutil.copyfileobj(source,dest,8388608)
os.chmod(disk,0o644)
assert digest(disk)==EXPECTED
audit=[execute([QEMU,'check','--output=json',str(disk)])]
audit.append(execute([QEMU,'resize','-f','qcow2',str(disk),'8G']))
audit.append(execute([QEMU,'check','--output=json',str(disk)]))
audit.append(execute([QEMU,'compare','-f','qcow2','-F','qcow2',str(BASE),str(disk)]))
info=json.loads(execute([QEMU,'info','--output=json',str(disk)])['stdout'])
assert info['virtual-size']==8589934592 and 'backing-filename' not in info
assert digest(BASE)==EXPECTED
node_uuid=str(uuid.uuid4())
reserved_ids={int(x.get('id')) for p in glob.glob('/opt/unetlab/labs/**/*.unl',recursive=True) for x in ET.parse(p).getroot().findall('.//node')}
core_id=next(i for i in range(1,128) if i not in reserved_ids)
firstmac='02:53:'+':'.join('%02x'%x for x in os.urandom(3))+':00'
params={'type':'qemu','template':'linux','name':'SOC-Core-L2','image':TARGET.name,'console':'vnc','cpu':1,'cpulimit':1,'ram':2048,'ethernet':8,'uuid':node_uuid,'firstmac':firstmac,'qemu_arch':'x86_64','qemu_version':'2.12.0','qemu_nic':'virtio-net-pci','qemu_options':'-machine type=pc,accel=kvm -vga std -usbdevice tablet -boot order=cd -cpu host','delay':0,'icon':'Server-2D-Linux-S.svg','config':'0','left':480,'top':320}
php='''<?php
chdir('/opt/unetlab/html');
require_once('/opt/unetlab/html/includes/init.php');
$f=__LAB__;
if (file_exists($f)) throw new Exception('Refuse existing lab');
$lab=new Lab($f,0);
$rc=$lab->edit(array('author'=>'SOC Project','description'=>'SOC Core L2 stage 1 - keep stopped, 8 unconnected NICs','version'=>'1'));
if ($rc!==0) throw new Exception('Lab edit failed '.$rc);
$p=json_decode(__PARAMS__,true);
$rc=$lab->addNode($p);
if ($rc!==0) throw new Exception('Node creation failed '.$rc);
$coreId=__CORE_ID__;
// EVE console ports depend on tenant/node ID, not lab UUID. Reserve an ID
// unused by existing labs, changing only this brand-new, never-booted lab.
if ($coreId!==1) {
    $doc=new DOMDocument(); $doc->load($f);
    $doc->getElementsByTagName('node')->item(0)->setAttribute('id',(string)$coreId);
    $doc->save($f); $lab=new Lab($f,0);
}
$n=$lab->getNodes()[$coreId]; $interfaces=array();
foreach($n->getEthernets() as $id=>$eth) $interfaces[]=array('id'=>$id,'eve_name'=>$eth->getName(),'network_id'=>$eth->getNetworkId(),'mac'=>incMac($n->getFirstMac(),$id));
echo json_encode(array('lab_id'=>$lab->getId(),'node_id'=>$coreId,'uuid'=>$n->getUuid(),'status'=>$n->getStatus(),'interfaces'=>$interfaces));
?>'''
php=php.replace('__LAB__',json.dumps(str(LAB))).replace('__PARAMS__',"'"+json.dumps(params).replace("'","\\'")+"'").replace('__CORE_ID__',str(core_id))
result=execute(['php'],php)
created=json.loads(result['stdout'])
assert created['status']==0 and len(created['interfaces'])==8
assert all(not x['network_id'] for x in created['interfaces'])
assert len({x['mac'] for x in created['interfaces']})==8
os.chmod(LAB,0o664)
try:
    import pwd
    uid=pwd.getpwnam('www-data').pw_uid
    os.chown(LAB,uid,uid)
except KeyError: pass
r=ET.parse(LAB).getroot()
assert len(r.findall('.//node'))==1 and not r.findall('.//network')
assert not r.findall('.//interface')
unchanged={p:digest(Path(p))==h for p,h in protected.items()}
assert all(unchanged.values())
created.update({'lab_path':str(LAB),'node_params':params,'disk_info':info,'disk_sha256':digest(disk),'base_sha256_before_after':EXPECTED,'image_audit':audit,'protected_unchanged':unchanged,'seed':'not yet created','core_booted':False,'network_objects':0,'links':0})
state=Path('/opt/unetlab/soc-core-preparation-20261031/core-created-stopped.json')
state.parent.mkdir(mode=0o700,exist_ok=True)
with state.open('x') as f:json.dump(created,f,indent=2)
print(json.dumps(created))
