"""Loai tep tam khoi artifact phat hanh, giu nguyen ban v1 de doi chieu.

Chi cap nhat payload/seed cua Core moi dang tat; khong sua mat khau/instance-id,
khong stop/start/wipe, khong cham seed cua hai node cu.
"""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[1]
STAGE=ROOT/'staging/soc-core-l2-20261031-stage1'
SOURCE=STAGE/'ovs-noble-amd64-offline-20261031.tar'
TARGET=STAGE/'ovs-noble-amd64-offline-20261031-v2.tar'
SSH=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143']
SCP=['scp.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519')]

with tarfile.open(SOURCE) as original,tarfile.open(TARGET,'x') as output:
    removed=[]
    for member in original.getmembers():
        if '.part-' in member.name:
            assert member.size==0
            removed.append({'name':member.name,'bytes':member.size})
            continue
        with original.extractfile(member) as source:
            if member.name=='SHA256SUMS':
                data='\n'.join(line for line in source.read().decode().splitlines() if '.part-' not in line)+'\n'
                blob=data.encode();member.size=len(blob);output.addfile(member,io.BytesIO(blob))
            else:output.addfile(member,source)
digest=hashlib.sha256(TARGET.read_bytes()).hexdigest()
subprocess.run(SCP+[str(TARGET),'root@192.168.220.143:/opt/unetlab/soc-core-preparation-20261031/'+TARGET.name],check=True)
code=r'''
import glob,hashlib,json,os,pathlib,shutil,subprocess,tarfile
root=pathlib.Path('/opt/unetlab/soc-core-preparation-20261031')
state=json.loads((root/'core-created-stopped.json').read_text());seed=json.loads((root/'seed-ready.json').read_text())
for p in glob.glob('/proc/[0-9]*/cmdline'):
    try:assert state['uuid'].encode() not in pathlib.Path(p).read_bytes().split(bytes([0]))
    except (FileNotFoundError,PermissionError):pass
assert not pathlib.Path('/opt/unetlab/tmp/0/'+state['lab_id']).exists()
bundle=root/'ovs-noble-amd64-offline-20261031-v2.tar'
assert hashlib.sha256(bundle.read_bytes()).hexdigest()==__HASH__
with tarfile.open(bundle) as archive:
    assert not any('.part-' in p for p in archive.getnames())
    manifest=json.load(archive.extractfile('package-manifest.json'))
    for p in manifest['packages']:
        assert hashlib.sha256(archive.extractfile('mirror/'+p['Filename']).read()).hexdigest()==p['SHA256']
newseed=root/'secrets/seed-input-v2';newseed.mkdir(mode=0o700)
for name in ['user-data','meta-data','network-config']:
    with (root/'secrets/seed-input'/name).open('rb') as src,(newseed/name).open('xb') as dest:shutil.copyfileobj(src,dest)
    os.chmod(newseed/name,0o600)
os.link(bundle,newseed/bundle.name)
iso=pathlib.Path(seed['seed_path']);pending=iso.with_name('cdrom-stage1-v2.pending.iso')
assert not pending.exists()
subprocess.run(['genisoimage','-quiet','-volid','cidata','-joliet','-rock','-o',str(pending),str(newseed)],capture_output=True,check=True)
os.chmod(pending,0o600)
names=subprocess.run(['isoinfo','-R','-i',str(pending),'-f'],capture_output=True,text=True,check=True).stdout.splitlines()
assert {'/user-data','/meta-data','/network-config'}.issubset(names)
archived=root/'secrets/cdrom-stage1-v1.iso';assert not archived.exists()
os.link(iso,archived)
assert hashlib.sha256(archived.read_bytes()).hexdigest()==seed['seed_sha256']
os.replace(pending,iso)
seed.update({'seed_sha256':hashlib.sha256(iso.read_bytes()).hexdigest(),'seed_bytes':iso.stat().st_size,'files':names,'bundle_sha256':__HASH__,'payload_revision':'v2 - excluded one zero-byte transient download file; all70 debs unchanged','previous_seed_archived_root_only':str(archived)})
with (root/'seed-ready-v2.json').open('x') as out:json.dump(seed,out,indent=2)
bundle_state={'bundle':str(bundle),'sha256':__HASH__,'package_count':len(manifest['packages']),'bytes':bundle.stat().st_size,'revision':'v2','previous_bundle_retained':str(root/'ovs-noble-amd64-offline-20261031.tar')}
with (root/'bundle-ready-v2.json').open('x') as out:json.dump(bundle_state,out,indent=2)
print(json.dumps({'seed':seed,'bundle':bundle_state}))
'''.replace('__HASH__',repr(digest))
result=subprocess.run(SSH+['python3','-'],input=code,text=True,capture_output=True,timeout=60)
if result.returncode:raise RuntimeError(result.stdout+result.stderr)
report=json.loads(result.stdout)
report['excluded_files']=removed
with (STAGE/'payload-v2-finalization.json').open('x',encoding='utf-8') as target:json.dump(report,target,indent=2)
print(json.dumps(report))
