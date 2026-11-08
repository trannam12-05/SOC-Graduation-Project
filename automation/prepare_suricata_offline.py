"""Tái dùng bộ resolver Noble đã ký; chỉ tải gói, không cài lên host EVE."""
from pathlib import Path
import json,hashlib,datetime as dt,concurrent.futures,urllib.request,urllib.error
import prepare_core_stage1 as old
from topology_remote import remote,ROOT

DEST='/opt/unetlab/soc-suricata-preparation-20261102'
LOCAL=ROOT/'staging/topology-first/suricata-offline'
LOCAL.mkdir(parents=True,exist_ok=True)

def solver():
 prep="""from pathlib import Path
import shutil
p=Path('__DEST__');p.mkdir(mode=0o700,exist_ok=True)
shutil.copy2('/opt/unetlab/soc-core-preparation-20261031/metadata.tar',p/'metadata.tar')
""".replace('__DEST__',DEST)
 code=old.REMOTE_SOLVER.replace('__REMOTE__',repr(DEST)).replace("'install','openvswitch-switch'", "'install','suricata','tcpdump'")
 data=json.loads(remote(prep+code,timeout=300))
 (LOCAL/'resolver-result.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
 print(json.dumps({'packages':data['package_count'],'suricata':[p for p in data['packages'] if p['Package']=='suricata']}))

def packages():
 data=json.loads((LOCAL/'resolver-result.json').read_text())
 def one(p):
  target=LOCAL/'mirror'/p['Filename'];target.parent.mkdir(parents=True,exist_ok=True)
  cached=ROOT/'staging/soc-core-l2-20261031-stage1/mirror'/p['Filename']
  if not target.exists() and cached.exists():
   import shutil
   shutil.copyfile(cached,target)
  if not target.exists():
   for host in ['https://archive.ubuntu.com/ubuntu/','https://security.ubuntu.com/ubuntu/']:
    try:
     old.download(host+p['Filename'],target,p['SHA256']);break
    except urllib.error.HTTPError as e:
     if host.endswith('security.ubuntu.com/ubuntu/'):raise
  assert hashlib.sha256(target.read_bytes()).hexdigest()==p['SHA256']
  return {'package':p['Package'],'version':p['Version'],'sha256':p['SHA256'],'path':p['Filename']}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:manifest=list(ex.map(one,data['packages']))
 (LOCAL/'manifest.json').write_text(json.dumps(manifest,indent=2))
 import tarfile
 archive=LOCAL/'suricata-offline.tar'
 with tarfile.open(archive,'w') as t:
  for p in (LOCAL/'mirror').rglob('*.deb'):t.add(p,arcname=p.relative_to(LOCAL/'mirror').as_posix())
  t.add(LOCAL/'manifest.json',arcname='manifest.json')
 old.copy_to(archive,DEST+'/suricata-offline.tar')
 receipt={'collected_at':old.now(),'package_count':len(manifest),'bundle_sha256':old.sha(archive),'bytes':archive.stat().st_size,'remote_bundle':DEST+'/suricata-offline.tar','origin':'Ubuntu Noble official signed metadata, SHA256 package checks; no installation on EVE host'}
 out=ROOT/'docs/evidence/M4/topology-first-20261102';out.mkdir(parents=True,exist_ok=True)
 (out/'offline-bundle.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(receipt))

if __name__=='__main__':
 import sys
 {'solver':solver,'packages':packages}[sys.argv[1]]()
