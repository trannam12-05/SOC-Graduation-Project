"""Nối duy nhất Wazuh e0 vào Management theo quyền ngày 05/11; không boot/IP."""
from pathlib import Path
import datetime as dt
import json
from topology_remote import ROOT, remote

EV = ROOT / 'docs/evidence/M1/wazuh-link-20261105'
before = json.loads((EV / 'inventory-before.json').read_text())
code = r'''
from pathlib import Path
import os,json,hashlib,shutil,datetime,subprocess,xml.etree.ElementTree as E
p=Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');original=p.read_bytes()
assert hashlib.sha256(original).hexdigest()=='__HASH__','Topology changed; stop'
def running():
 out=[]
 for f in Path('/proc').glob('[0-9]*/cmdline'):
  try:
   args=f.read_bytes().split(b'\0')
   if args and (b'qemu-system-' in args[0] or os.path.basename(args[0])==b'vpcs'):out.append(int(f.parent.name))
  except OSError:pass
 return out
assert not running(),'Running nodes; stop'
r=E.fromstring(original);ns={n.get('name'):n for n in r.findall('.//node')}
assert r.get('id')=='f39cfc8c-5eaf-461e-bb0c-60b5fde848b7'
assert len(ns)==10 and ns['Wazuh-SOC'].get('id')=='10'
assert not ns['Wazuh-SOC'].findall('interface')
net=next(n for n in r.findall('.//network') if n.get('name')=='VLAN99-Management')
assert net.get('id')=='10' and net.get('type')=='bridge'
for name,port in [('SOC-Core-L2','4'),('Management','0'),('Suricata-NIDS','1')]:
 assert next(i for i in ns[name].findall('interface') if i.get('id')==port).get('network_id')=='10'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=Path('/root/soc-m1-wazuh-link-'+stamp);backup.mkdir(mode=0o700)
shutil.copy2(p,backup/'lab-before.unl');os.chmod(backup/'lab-before.unl',0o600)
assert (backup/'lab-before.unl').read_bytes()==original
assert p.read_bytes()==original and not running()
php=r"""<?php
chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');
$l=new Lab('/opt/unetlab/labs/SOC-M2-Core-L2.unl',0);
$n=$l->getNodes()[10];if($n->getName()!=='Wazuh-SOC'||$n->getStatus()!==0)throw new Exception('Wrong node or running');
$rc=$l->connectNode(10,array('0'=>'10'));if($rc!==0)throw new Exception('connectNode failed '.$rc);
echo json_encode(array('operation'=>'connectNode','node_id'=>10,'port'=>0,'network_id'=>10,'return_code'=>$rc));
?>"""
proc=subprocess.run(['php'],input=php,text=True,capture_output=True)
assert proc.returncode==0,proc.stderr
operation=json.loads(proc.stdout)
after=p.read_bytes();a=E.fromstring(after);ans={n.get('name'):n for n in a.findall('.//node')}
w=ans['Wazuh-SOC'];interfaces=w.findall('interface')
assert len(interfaces)==1 and interfaces[0].get('id')=='0' and interfaces[0].get('network_id')=='10'
newinterface=dict(interfaces[0].attrib);w.remove(interfaces[0])
def canonical(e):return (e.tag,sorted(e.attrib.items()),(e.text or '').strip(),[canonical(c) for c in e])
assert canonical(r)==canonical(a),'Unexpected semantic changes; inspect backup before proceeding'
assert not running(),'Unexpected node state'
shutil.copy2(p,backup/'lab-after.unl');os.chmod(backup/'lab-after.unl',0o600)
result={'operation':operation,'backup_directory':str(backup),'before_sha256':hashlib.sha256(original).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest(),'added_interface':newinterface,'only_expected_semantic_change':True,'node_count':len(ans),'network_count':len(a.findall('.//network')),'running_node_processes':running(),'guest_configuration_changed':False,'power_operations':False,'raw_backup_local_downloaded':False}
(backup/'result.json').write_text(json.dumps(result,indent=2));os.chmod(backup/'result.json',0o600)
print(json.dumps(result))
'''.replace('__HASH__', before['sha256'])
if __name__ == '__main__':
    result = json.loads(remote(code))
    result['collector_time'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    (EV / 'connection-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
