"""Read-only audit for user-authorized normal node stop and EVE shutdown."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'docs/evidence/M2'
SSH=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143']
CODE=r'''
import os,glob,json,pathlib,subprocess,xml.etree.ElementTree as E
def run(args):
    p=subprocess.run(args,text=True,capture_output=True,timeout=20)
    return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
out={'labs':[],'vm_processes':[],'processes':[],'overlays':[]}
for p in pathlib.Path('/opt/unetlab/labs').rglob('*.unl'):
    r=E.parse(p).getroot()
    out['labs'].append({'path':str(p),'id':r.get('id'),'nodes':[dict(n.attrib) for n in r.findall('.//node')]})
for p in glob.glob('/proc/[0-9]*/cmdline'):
    try:
        base=pathlib.Path(p).parent
        a=[x.decode(errors='replace') for x in pathlib.Path(p).read_bytes().split(b'\0') if x]
        if not a:continue
        cmd=os.path.basename(a[0])
        out['processes'].append({'pid':base.name,'executable':cmd})
        if cmd in ['qemu-system-x86_64','qemu-system-i386','dynamips','iouyap','docker'] or cmd.startswith('i86bi'):
            row={'pid':base.name,'executable':cmd,'cwd':os.readlink(str(base/'cwd'))}
            if '-uuid' in a:row['uuid']=a[a.index('-uuid')+1]
            if '-name' in a:row['name']=a[a.index('-name')+1]
            out['vm_processes'].append(row)
    except (OSError,ValueError):pass
for p in pathlib.Path('/opt/unetlab/tmp').rglob('*.qcow2'):
    s=p.stat();out['overlays'].append({'path':str(p),'bytes':s.st_size,'inode':s.st_ino})
php="<?php chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');$out=[];foreach(['/opt/unetlab/labs/SOC-Ubuntu-Image-Test.unl','/opt/unetlab/labs/SOC-M2-Core-L2.unl'] as $path){$l=new Lab($path,0);foreach($l->getNodes() as $id=>$n){$out[]=array('lab'=>$path,'id'=>$id,'name'=>$n->getName(),'status'=>$n->getStatus(),'cpu'=>$n->getCpu(),'ram'=>$n->getRam(),'ethernet'=>$n->getEthernetCount());}}echo json_encode($out);?>"
p=subprocess.run(['php'],input=php,text=True,capture_output=True,check=True);out['node_status']=json.loads(p.stdout)
for key,cmd in [('jobs',['systemctl','list-jobs','--no-pager']),('sessions',['who']),('uptime',['uptime']),('memory',['free','-m']),('disk',['df','-Pk','/opt/unetlab']),('timers',['systemctl','list-timers','--all','--no-pager'])]:out[key]=run(cmd)
out['task_executables']=[p for p in out['processes'] if p['executable'] in ['apt','apt-get','dpkg','unattended-upgrade','qemu-img','rsync','scp','sftp-server','genisoimage','mkisofs','tar','gzip','wget','curl','dd','unl_wrapper']]
print(json.dumps(out))
'''
def main():
    label=sys.argv[1]
    result=subprocess.run(SSH+['python3','-'],input=CODE,text=True,encoding='utf-8',capture_output=True,timeout=60)
    if result.returncode:raise RuntimeError(result.stderr)
    data=json.loads(result.stdout)
    data['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    if label=='before':
        checks=[]
        for manifest in EV.glob('*SHA256SUMS*.txt'):
            for line in manifest.read_text(encoding='utf-8-sig').splitlines():
                if not line.strip():continue
                sha,name=line.split(None,1);name=name.strip().lstrip('*')
                candidates=[ROOT/name,EV/name,manifest.parent/name]
                found=next((p for p in candidates if p.is_file()),None)
                checks.append({'manifest':manifest.name,'path':name,'exists':found is not None,'match':found is not None and hashlib.sha256(found.read_bytes()).hexdigest()==sha})
        data['local_manifest_checks']=checks
        data['local_files']=[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size} for folder in ['docs/M2','docs/evidence/M2','network','opnsense'] for p in (ROOT/folder).rglob('*') if p.is_file()]
        data['word_packages']=[{'path':str(p.relative_to(ROOT)),'zip_valid':zipfile.is_zipfile(p)} for p in (ROOT/'docs/M2').glob('*.docx')]
    path=EV/('M2-safe-restart-'+label+'-20261031.json')
    with path.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:data[k] for k in ['collector_time','node_status','vm_processes','overlays','task_executables','jobs','sessions']},ensure_ascii=False))
    if label=='before':print(json.dumps({'manifest_entries':len(checks),'failed':[x for x in checks if not x['match']],'saved_files':len(data['local_files'])}))
if __name__=='__main__':main()
