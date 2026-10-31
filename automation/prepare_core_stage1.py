"""SOC M2: chuan bi tai nguyen rieng, khong start guest/khong cai package.

Metadata va .deb chi tai HTTPS tu Ubuntu chinh thuc. APT resolver tach source,
state/status/cache/Etc, chi dung Noble amd64 va file repository cuc bo.
Khong goi install that, khong dung Jammy status/sources/cache cua host.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import time
import urllib.parse
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'staging/soc-core-l2-20261031-stage1'
REMOTE='/opt/unetlab/soc-core-preparation-20261031'
IMAGE='/opt/unetlab/addons/qemu/linux-ubuntu-24.04-soc-core-l2'
LAB='/opt/unetlab/labs/SOC-M2-Core-L2.unl'
SSH=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143']
SCP=['scp.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519')]
SUITES=['noble','noble-updates','noble-security']

def now(): return dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''): h.update(part)
    return h.hexdigest()
def fresh_json(path,data):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n')
def remote(code,timeout=300):
    p=subprocess.run(SSH+['python3','-'],input=code,text=True,encoding='utf-8',capture_output=True,timeout=timeout)
    if p.returncode: raise RuntimeError('Remote failed: '+p.stdout+p.stderr)
    return p.stdout
def copy_to(source,destination):
    p=subprocess.run(SCP+[str(source),'root@192.168.220.143:'+destination],capture_output=True,text=True,timeout=300)
    if p.returncode: raise RuntimeError('SCP failed: '+p.stderr)
def download(url,dest,expected=None):
    dest=Path(dest); dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        if expected and sha(dest)!=expected: raise ValueError('Existing file hash mismatch '+str(dest))
        return
    for attempt in range(1,5):
        temporary=dest.with_name(dest.name+'.part-'+str(attempt))
        if temporary.exists(): continue
        print('DOWNLOAD '+url+' attempt='+str(attempt),flush=True)
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'SOC-M2-Offline-Preparation/1.0'})
            with urllib.request.urlopen(request,timeout=60) as response, temporary.open('xb') as out:
                while True:
                    data=response.read(1048576)
                    if not data: break
                    out.write(data)
            if expected and sha(temporary)!=expected: raise ValueError('Downloaded hash mismatch '+url)
            if dest.exists(): raise FileExistsError(str(dest))
            temporary.rename(dest)
            return
        except urllib.error.HTTPError:
            raise
        except (OSError, ConnectionError, TimeoutError) as error:
            if attempt==4: raise
            print('RETRY '+type(error).__name__+' '+dest.name,flush=True)
            time.sleep(2)
    raise RuntimeError('Download retry files already exist; inspect partial files '+str(dest))

def metadata():
    LOCAL.mkdir(parents=True,exist_ok=True)
    records=[]
    for suite in SUITES:
        base='https://security.ubuntu.com/ubuntu' if suite=='noble-security' else 'https://archive.ubuntu.com/ubuntu'
        release=LOCAL/'mirror/dists'/suite/'InRelease'
        download(base+'/dists/'+suite+'/InRelease',release)
        text=release.read_text(encoding='utf-8')
        assert '\nOrigin: Ubuntu\n' in text and '\nCodename: noble\n' in text
        assert '\nSuite: '+suite+'\n' in text
        section=text.split('\nSHA256:\n',1)[1].split('\nSHA512:',1)[0]
        hashes={m.group(3):(m.group(1),int(m.group(2))) for m in re.finditer(r'^\s+([0-9a-f]{64})\s+(\d+)\s+(.+)$',section,re.M)}
        for component in ['main','universe']:
            index=component+'/binary-amd64/Packages.xz'
            digest,size=hashes[index]
            dest=release.parent/index
            url=base+'/dists/'+suite+'/'+component+'/binary-amd64/by-hash/SHA256/'+digest
            download(url,dest,digest)
            assert dest.stat().st_size==size
            records.append({'suite':suite,'component':component,'url':url,'relative':dest.relative_to(LOCAL/'mirror').as_posix(),'sha256':digest,'size':size})
    fresh_json(LOCAL/'metadata-manifest.json',{'collected_at':now(),'signature_verification':'pending remote gpgv','indexes':records})
    archive=LOCAL/'metadata.tar'
    with tarfile.open(archive,'x') as t:
        for path in (LOCAL/'mirror').rglob('*'):
            if path.is_file(): t.add(path,arcname=path.relative_to(LOCAL/'mirror').as_posix(),recursive=False)
    print(json.dumps({'metadata_files':len(records),'tar':str(archive),'bytes':archive.stat().st_size}),flush=True)

def solver():
    print(remote("from pathlib import Path\np=Path("+repr(REMOTE)+")\np.mkdir(mode=0o700,exist_ok=True)\nassert not (p/'mirror').exists()\nprint('dedicated preparation directory ready')"),flush=True)
    copy_to(LOCAL/'metadata.tar',REMOTE+'/metadata.tar')
    code=REMOTE_SOLVER.replace('__REMOTE__',repr(REMOTE))
    output=remote(code,timeout=300)
    result=json.loads(output)
    fresh_json(LOCAL/'resolver-result.json',result)
    print(json.dumps({'package_count':result['package_count'],'signature_audit':result['signature_audit'],'ovs':[p for p in result['packages'] if p['Package']=='openvswitch-switch']}),flush=True)

REMOTE_SOLVER=r'''
import os, pathlib, tarfile, subprocess, json, hashlib, lzma, re, urllib.parse
root=pathlib.Path(__REMOTE__); mirror=root/'mirror'; mirror.mkdir()
with tarfile.open(root/'metadata.tar') as archive:
    for member in archive.getmembers():
        dest=(mirror/member.name).resolve()
        if not dest.is_relative_to(mirror.resolve()) or not member.isfile(): raise RuntimeError('Unsafe metadata archive')
        dest.parent.mkdir(parents=True,exist_ok=True)
        with archive.extractfile(member) as src, dest.open('xb') as dst: dst.write(src.read())
audit=[]
for suite in ['noble','noble-updates','noble-security']:
    release=mirror/'dists'/suite/'InRelease'
    result=subprocess.run(['gpgv','--status-fd','1','--keyring','/usr/share/keyrings/ubuntu-archive-keyring.gpg',str(release)],text=True,capture_output=True)
    audit.append({'suite':suite,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode or 'VALIDSIG ' not in result.stdout: raise RuntimeError('Repository signature not valid '+suite)
    section=release.read_text().split('\nSHA256:\n',1)[1].split('\nSHA512:',1)[0]
    hashes={m.group(3):m.group(1) for m in re.finditer(r'^\s+([0-9a-f]{64})\s+(\d+)\s+(.+)$',section,re.M)}
    for component in ['main','universe']:
        p=release.parent/component/'binary-amd64/Packages.xz'
        if hashlib.sha256(p.read_bytes()).hexdigest()!=hashes[component+'/binary-amd64/Packages.xz']: raise RuntimeError('Signed index hash mismatch')
apt=root/'apt-root'
for sub in ['etc','state/lists/partial','cache/archives/partial','log','empty-parts','trusted-empty']:
    (apt/sub).mkdir(parents=True,exist_ok=True)
(apt/'status').write_text('')
(apt/'etc/sources.list').write_text(''.join('deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg by-hash=no] file:'+str(mirror)+' '+s+' main universe\n' for s in ['noble','noble-updates','noble-security']))
config='\n'.join([
 'Dir::Etc "'+str(apt/'etc')+'";', 'Dir::Etc::main "-";', 'Dir::Etc::parts "'+str(apt/'empty-parts')+'";',
 'Dir::Etc::sourcelist "sources.list";', 'Dir::Etc::sourceparts "-";', 'Dir::Etc::trustedparts "'+str(apt/'trusted-empty')+'";',
 'Dir::State "'+str(apt/'state')+'";', 'Dir::State::status "'+str(apt/'status')+'";',
 'Dir::Cache "'+str(apt/'cache')+'";', 'Dir::Log "'+str(apt/'log')+'";',
 'APT::Architecture "amd64";', 'APT::Architectures { "amd64"; };', 'APT::Sandbox::User "root";',
 'Acquire::Languages "none";', 'Acquire::PDiffs "false";',
 'Acquire::IndexTargets::deb::DEP-11::DefaultEnabled "false";',
 'Acquire::IndexTargets::deb::DEP-11-icons-small::DefaultEnabled "false";',
 'Acquire::IndexTargets::deb::DEP-11-icons::DefaultEnabled "false";',
 'Debug::NoLocking "true";', 'APT::Install-Recommends "false";'])
(apt/'apt.conf').write_text(config+'\n')
env=dict(os.environ,APT_CONFIG=str(apt/'apt.conf'),LC_ALL='C')
def run(command,label):
    p=subprocess.run(command,env=env,text=True,capture_output=True,timeout=240)
    (root/(label+'.log')).write_text(p.stdout+p.stderr)
    if p.returncode: raise RuntimeError(label+' failed: '+p.stdout[-3500:]+p.stderr[-3500:])
    return p
update=run(['apt-get','update'],'apt-update-noble-isolated')
simulation=run(['apt-get','--simulate','--no-install-recommends','install','openvswitch-switch'],'apt-simulation-empty-status')
uris=run(['apt-get','--yes','--download-only','--print-uris','--no-install-recommends','install','openvswitch-switch'],'apt-print-uris')
needed={}
for line in uris.stdout.splitlines():
    m=re.match(r"^'([^']+)' (\S+) (\d+) (\S+)$",line)
    if m:
        relative=urllib.parse.unquote(m.group(1)).split('/mirror/',1)[1]
        needed[relative]={'apt_uri':m.group(1),'apt_archive_name':m.group(2),'apt_bytes':int(m.group(3))}
if not needed: raise RuntimeError('APT returned no package URIs')
records={}
for suite in ['noble','noble-updates','noble-security']:
    for component in ['main','universe']:
        path=mirror/'dists'/suite/component/'binary-amd64/Packages.xz'
        record={}; key=None
        def consume(record):
            name=record.get('Filename')
            if name not in needed: return
            if record.get('Architecture') not in ['amd64','all']: raise RuntimeError('Wrong architecture')
            if name in records:
                if records[name]['SHA256']!=record['SHA256']: raise RuntimeError('Conflicting signed metadata')
                records[name]['origins'].append({'suite':suite,'component':component})
            else:
                records[name]={k:record.get(k,'') for k in ['Package','Version','Architecture','Filename','Size','SHA256','Depends','Pre-Depends','Provides']}
                records[name]['origins']=[{'suite':suite,'component':component}]
        with lzma.open(path,'rt',encoding='utf-8',errors='strict') as stream:
            for line in stream:
                line=line.rstrip('\n')
                if not line:
                    consume(record);record={};key=None
                elif line.startswith(' ') and key:
                    record[key]+=' '+line.strip()
                elif ': ' in line:
                    key,value=line.split(': ',1);record[key]=value
            if record: consume(record)
if set(records)!=set(needed): raise RuntimeError('Missing signed package record')
result={'signature_audit':audit,'apt_config':config,'sources':(apt/'etc/sources.list').read_text(),'status_basis':'empty isolated status; no host Jammy package state','simulation':simulation.stdout,'package_count':len(records),'packages':sorted(records.values(),key=lambda r:r['Package'])}
(root/'resolver-result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
'''

def packages():
    result=json.loads((LOCAL/'resolver-result.json').read_text(encoding='utf-8'))
    def one(record):
        filename=record['Filename']; path=LOCAL/'mirror'/filename
        bases=['https://security.ubuntu.com/ubuntu','https://archive.ubuntu.com/ubuntu'] if all(o['suite']=='noble-security' for o in record['origins']) else ['https://archive.ubuntu.com/ubuntu','https://security.ubuntu.com/ubuntu']
        for i,base in enumerate(bases):
            try:
                url=base+'/'+filename; download(url,path,record['SHA256'])
                assert path.stat().st_size==int(record['Size'])
                return dict(record,download_url=url,downloaded_at=now(),verified_sha256=sha(path))
            except urllib.error.HTTPError:
                if i==len(bases)-1: raise
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(one,result['packages']))
    manifest={'collected_at':now(),'release':'Ubuntu 24.04 Noble','architecture':'amd64/all','root_package':'openvswitch-switch','signature_audit':result['signature_audit'],'status_basis':result['status_basis'],'guest_installation':'not attempted; Core never started','packages':records}
    fresh_json(LOCAL/'package-manifest.json',manifest)
    with (LOCAL/'SHA256SUMS').open('x',encoding='utf-8',newline='\n') as f:
        for p in sorted((LOCAL/'mirror').rglob('*')):
            if p.is_file(): f.write(sha(p)+'  '+p.relative_to(LOCAL).as_posix()+'\n')
    bundle=LOCAL/'ovs-noble-amd64-offline-20261031.tar'
    with tarfile.open(bundle,'x') as archive:
        for p in sorted((LOCAL/'mirror').rglob('*')):
            if p.is_file(): archive.add(p,arcname=p.relative_to(LOCAL).as_posix(),recursive=False)
        for name in ['package-manifest.json','metadata-manifest.json','SHA256SUMS']:
            archive.add(LOCAL/name,arcname=name,recursive=False)
    copy_to(bundle,REMOTE+'/'+bundle.name)
    verify="""import pathlib,hashlib,json,tarfile
p=pathlib.Path(__PATH__)
h=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(1048576),b''): h.update(b)
assert h.hexdigest()==__HASH__
with tarfile.open(p) as t: m=json.load(t.extractfile('package-manifest.json'))
marker=p.parent/'bundle-ready.json'
with marker.open('x') as out: json.dump({'bundle':str(p),'sha256':h.hexdigest(),'package_count':len(m['packages'])},out)
print(json.dumps({'bundle':str(p),'sha256':h.hexdigest(),'package_count':len(m['packages'])}))
""".replace('__PATH__',repr(REMOTE+'/'+bundle.name)).replace('__HASH__',repr(sha(bundle)))
    print(remote(verify),flush=True)
    print(json.dumps({'windows_bundle':str(bundle),'bytes':bundle.stat().st_size,'sha256':sha(bundle),'package_count':len(records),'ovs':[r for r in records if r['Package']=='openvswitch-switch']}),flush=True)

def image_node():
    script=(ROOT/'automation/remote_create_core_stopped.py').read_text(encoding='utf-8')
    output=remote(script,timeout=180)
    LOCAL.mkdir(parents=True,exist_ok=True)
    fresh_json(LOCAL/'core-created-stopped.json',json.loads(output))
    print(output,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['metadata','solver','packages','image-node'])
    args=parser.parse_args()
    {'metadata':metadata,'solver':solver,'packages':packages,'image-node':image_node}[args.phase]()
