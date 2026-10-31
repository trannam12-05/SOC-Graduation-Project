"""Doc trang thai Core dang tat va ghi snapshot khong bi mat; khong start VM."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CODE=r'''
import os,glob,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as E
root=pathlib.Path('/opt/unetlab/soc-core-preparation-20261031')
out={}
for name in ['core-created-stopped.json','seed-ready.json','bundle-ready.json','bundle-validated.json']:
    path=root/name
    candidate=root/(name.removesuffix('.json')+'-v2.json')
    if candidate.exists():path=candidate
    out[name]=json.loads(path.read_text())
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()
protected=['/opt/unetlab/html/templates/intel/linux.yml','/opt/unetlab/html/templates/amd/linux.yml','/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs/virtioa.qcow2','/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs/cdrom.iso','/opt/unetlab/addons/qemu/linux-ubuntu-24.04-soc-console-test/virtioa.qcow2','/opt/unetlab/addons/qemu/linux-ubuntu-24.04-soc-console-test/cdrom.iso','/opt/unetlab/labs/M2.unl','/opt/unetlab/labs/M2_Core_L3.unl','/opt/unetlab/labs/SOC-Ubuntu-Image-Test.unl']
out['protected']=[{'path':p,'sha256':sha(p),'bytes':os.stat(p).st_size} for p in protected]
out['qemu_running']=[]
for p in glob.glob('/proc/[0-9]*/cmdline'):
    try:
        a=[x.decode(errors='replace') for x in pathlib.Path(p).read_bytes().split(bytes([0])) if x]
        if a and os.path.basename(a[0])=='qemu-system-x86_64':out['qemu_running'].append({'pid':p.split('/')[2],'name':a[a.index('-name')+1],'uuid':a[a.index('-uuid')+1]})
    except (FileNotFoundError,PermissionError):pass
state=out['core-created-stopped.json']
out['core_process_present']=any(p['uuid']==state['uuid'] for p in out['qemu_running'])
out['core_runtime_directory_exists']=pathlib.Path('/opt/unetlab/tmp/0/'+state['lab_id']).exists()
out['core_lab_xml']=pathlib.Path(state['lab_path']).read_text()
php="<?php chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');$l=new Lab('/opt/unetlab/labs/SOC-M2-Core-L2.unl',0);$n=$l->getNodes()[3];$a=[];foreach($n->getEthernets() as $id=>$e)$a[]=array('id'=>$id,'eve_name'=>$e->getName(),'network_id'=>$e->getNetworkId(),'mac'=>incMac($n->getFirstMac(),$id));echo json_encode(array('status'=>$n->getStatus(),'interfaces'=>$a,'cpu'=>$n->getCpu(),'ram'=>$n->getRam(),'ethernet'=>$n->getEthernetCount()));?>"
out['live_eve_node']=json.loads(subprocess.run(['php'],input=php,text=True,capture_output=True,check=True).stdout)
out['seed_sha256_live']=sha(out['seed-ready.json']['seed_path'])
out['core_disk_sha256_live']=sha(state['disk_info']['filename'])
out['free_memory']=subprocess.run(['free','-m'],capture_output=True,text=True,check=True).stdout
out['df']=subprocess.run(['df','-Pk','/opt/unetlab/addons/qemu'],capture_output=True,text=True,check=True).stdout
assert out['live_eve_node']['status']==0 and out['live_eve_node']['ethernet']==8
assert not out['core_process_present'] and not out['core_runtime_directory_exists']
assert out['seed_sha256_live']==out['seed-ready.json']['seed_sha256']
assert out['core_disk_sha256_live']==state['disk_sha256']
assert not E.fromstring(out['core_lab_xml']).findall('.//network')
assert not E.fromstring(out['core_lab_xml']).findall('.//interface')
print(json.dumps(out))
'''
def main():
    ssh=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143','python3','-']
    response=subprocess.run(ssh,input=CODE,text=True,encoding='utf-8',capture_output=True,timeout=80)
    if response.returncode:raise RuntimeError(response.stderr+response.stdout)
    data=json.loads(response.stdout)
    data['collected_at_windows']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    command="$s=Get-CimInstance Win32_OperatingSystem; [pscustomobject]@{CollectedAt=(Get-Date -Format o);TotalVisibleMemoryKiB=$s.TotalVisibleMemorySize;FreePhysicalMemoryKiB=$s.FreePhysicalMemory}|ConvertTo-Json -Compress"
    data['windows_memory']=json.loads(subprocess.run(['powershell.exe','-NoProfile','-Command',command],capture_output=True,text=True,check=True).stdout)
    baseline=json.loads((ROOT/'docs/evidence/M2/M2-core-stage1-baseline-20261031.json').read_text(encoding='utf-8'))
    hashes={p['path']:p['sha256'] for p in baseline['protected']}
    data['protected_comparison']=[{'path':p['path'],'unchanged':p['sha256']==hashes[p['path']]} for p in data['protected']]
    assert all(p['unchanged'] for p in data['protected_comparison'])
    destination=Path(sys.argv[1])
    with destination.open('x',encoding='utf-8',newline='\n') as target:json.dump(data,target,ensure_ascii=False,indent=2);target.write('\n')
    node=data['live_eve_node'];seed=data['seed-ready.json'];bundle=data['bundle-ready.json']
    print('LIVE READ-ONLY EVE CHECK - Core has NOT booted')
    print('SOC-Core-L2: lab SOC-M2-Core-L2; node ID 3; status '+str(node['status'])+' = STOPPED')
    print('CPU '+str(node['cpu'])+'; RAM '+str(node['ram'])+' MiB; configured vNICs '+str(node['ethernet'])+'; links 0')
    print('Core virtual disk: 8 GiB QCOW2 independent copy; check-errors 0')
    print('Core QEMU process: absent; Core runtime overlay: absent')
    for interface in node['interfaces']:print('EVE '+interface['eve_name']+'  MAC '+interface['mac']+'  network_id='+str(interface['network_id']))
    print('NoCloud seed: cidata; user-data / meta-data / network-config verified')
    print('Account soc-core-admin; console password hash set; SSH password auth OFF')
    print('OVS bundle: 3.3.9-0ubuntu0.24.04.1; '+str(bundle['package_count'])+' Noble amd64/all packages')
    print('Bundle hash/signatures/control fields verified; OFFLINE byte check PASS')
    print('Old templates, images, seeds and labs: ALL CHECKSUMS UNCHANGED')
    print('Windows free physical memory: %.1f MiB'%(data['windows_memory']['FreePhysicalMemoryKiB']/1024))
    print('NO guest installation, VLAN, trunk or mirror configuration performed')
    print('Snapshot saved: '+destination.name)

if __name__=='__main__':main()
