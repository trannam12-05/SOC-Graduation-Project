"""Sao lưu Secondary đã tắt mềm, giữ ISO, chỉ đổi boot order sang ổ cứng."""
import json,datetime as dt
from topology_remote import remote,ROOT
CODE=r'''
import pathlib,subprocess,json,hashlib,shutil,xml.etree.ElementTree as E,os
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');before=E.parse(lab).getroot()
secondary=next(n for n in before.findall('.//node') if n.get('name')=='OPNsense-Secondary')
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[s.decode(errors='replace') for s in p.read_bytes().split(b'\0') if s]
  if a and 'qemu-system-' in a[0]:assert secondary.get('uuid') not in a,'WAIT_SECONDARY_GRACEFUL_POWER_OFF'
 except FileNotFoundError:pass
source=pathlib.Path('/opt/unetlab/tmp/0')/before.get('id')/secondary.get('id')/'virtioa.qcow2'
backup=pathlib.Path('/root/soc-secondary-installed-backup-20261102-resume');assert not backup.exists(),'Backup exists: inspect outcome instead of overwriting'
assert shutil.disk_usage(source).free>source.stat().st_size+1024**3
backup.mkdir(mode=0o700);shutil.copy2(lab,backup/'lab-before.unl')
target=backup/'virtioa.qcow2';h=hashlib.sha256()
with source.open('rb') as src,target.open('xb') as dst:
 for data in iter(lambda:src.read(8*1024*1024),b''):h.update(data);dst.write(data)
shutil.copystat(source,target);target.chmod(0o600)
def digest(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):d.update(b)
 return d.hexdigest()
assert digest(target)==h.hexdigest()
info=subprocess.run(['/opt/qemu-2.12.0/bin/qemu-img','info','--output=json',str(source)],text=True,capture_output=True,check=True)
php="""<?php chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');$l=new Lab('/opt/unetlab/labs/SOC-M2-Core-L2.unl',0);$n=$l->getNodes()[2];if($n->getStatus()!==0)throw new Exception('Secondary running');$old=$n->getQemu_options();$new=str_replace('order=dc','order=c',$old);if($old===$new)throw new Exception('Unexpected boot options');$rc=$l->editNode(array('id'=>2,'qemu_options'=>$new,'ro_qemu_options'=>$old));if($rc!==0)throw new Exception('Boot option failed');echo json_encode(array('before'=>$old,'after'=>$new));?>"""
p=subprocess.run(['php'],input=php,text=True,capture_output=True);assert p.returncode==0,p.stderr
boot=json.loads(p.stdout);after=E.parse(lab).getroot()
for old in before.findall('.//node'):
 new=next(n for n in after.findall('.//node') if n.get('id')==old.get('id'))
 for k,v in old.attrib.items():
  if old.get('id')=='2' and k=='qemu_options':continue
  assert new.get(k)==v,'Protected node attribute changed'
 assert [i.attrib for i in old.findall('interface')]==[i.attrib for i in new.findall('interface')]
result={'source':str(source),'backup':str(target),'bytes':target.stat().st_size,'sha256_source_and_backup':h.hexdigest(),'secondary_stopped_at_backup':True,'image_info':json.loads(info.stdout),'boot':boot,'other_nodes_and_links_unchanged':True,'ISO':'Preserved unchanged; boot order selects disk only'}
(backup/'backup-public.json').write_text(json.dumps(result,indent=2))
for f in [source,target]:
 with f.open('rb') as stream:os.posix_fadvise(stream.fileno(),0,0,os.POSIX_FADV_DONTNEED)
p=subprocess.run(['/opt/unetlab/wrappers/unl_wrapper','-a','start','-T','0','-F',str(lab),'-D','2'],text=True,capture_output=True,timeout=30)
assert p.returncode==0,p.stderr
result['start_requested']=True
print(json.dumps(result))
'''
if __name__=='__main__':
 result=json.loads(remote(CODE,timeout=600));result['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
 out=ROOT/'docs/evidence/M3/resume-20261102/secondary-installed-disk-backup.json'
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result))
