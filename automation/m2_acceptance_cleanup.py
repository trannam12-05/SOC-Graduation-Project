"""Sau tắt mềm DC: kiểm hash topology, phục hồi NIC thử từ backup, giữ Core/Primary."""
import datetime,json
from topology_remote import ROOT,remote
OUT=ROOT/'docs/evidence/M2/final-acceptance-20261103'
receipt=json.loads((OUT/'prepare-receipt.json').read_text(encoding='utf-8'))
CODE=r'''
import pathlib,os,time,json,hashlib,xml.etree.ElementTree as E
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl')
def running():
 rows=[]
 for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
  try:
   a=[v.decode(errors='replace') for v in p.read_bytes().split(b'\0') if v]
   if a and 'qemu-system-' in os.path.basename(a[0]):rows.append({'name':a[a.index('-name')+1],'uuid':a[a.index('-uuid')+1],'ram_mib':int(a[a.index('-m')+1])})
  except (OSError,ValueError):pass
 return rows
for attempt in range(20):
 if not any(x['name']=='Data-Center' for x in running()):break
 time.sleep(1)
assert not any(x['name']=='Data-Center' for x in running()),'DC still running; no topology restoration'
assert hashlib.sha256(lab.read_bytes()).hexdigest()==__AFTER__,'Lab changed during tests; do not overwrite'
backup=pathlib.Path('/root/soc-m2-final-20261103-backup/lab-before.unl');raw=backup.read_bytes()
assert hashlib.sha256(raw).hexdigest()==__BEFORE__
mode=lab.stat().st_mode & 0o777;uid=lab.stat().st_uid;gid=lab.stat().st_gid
temp=lab.with_name(lab.name+'.m2-restore');assert not temp.exists()
with temp.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
os.chmod(temp,mode);os.chown(temp,uid,gid);os.replace(temp,lab)
assert lab.read_bytes()==raw
mem=dict((s.split(':')[0],int(s.split()[1])) for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if len(s.split())>1 and s.split()[1].isdigit())
print(json.dumps({'DC_stopped_verified':True,'temporary_client_NIC_removed':True,'lab_restored_byte_exact':True,'lab_sha256':hashlib.sha256(raw).hexdigest(),'running':running(),'eve_memory':mem,'scope':'Restore only temporary topology addition; no firewall/Core/HA/NAT/DHCP change'}))
'''.replace('__AFTER__',repr(receipt['lab_sha256_after'])).replace('__BEFORE__',repr(receipt['lab_sha256_before']))
d=json.loads(remote(CODE,timeout=35));d['collector_time']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
(OUT/'cleanup-receipt.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in d.items() if k!='eve_memory'}))
