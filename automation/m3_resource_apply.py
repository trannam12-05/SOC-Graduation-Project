"""Chỉ sửa ba thuộc tính RAM sau khi xác minh guest đã tắt; giữ nguyên XML khác."""
import json
from m3_resource_optimization import save
from topology_remote import remote
CODE=r'''
import pathlib,xml.etree.ElementTree as E,os,re,json,hashlib,subprocess
p=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');before=p.read_bytes();root=E.fromstring(before)
targets={'SOC-Core-L2':1024,'OPNsense-Primary':2048,'OPNsense-Secondary':2048}
uuids={n.get('uuid') for n in root.findall('.//node') if n.get('name') in targets}
for c in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  args=c.read_bytes().decode(errors='replace').split('\0')
  assert not (uuids.intersection(args) and 'qemu-system-' in args[0]),'Node still running; refuse mutation'
 except OSError:pass
def replace(m):
 s=m.group(0);node=E.fromstring(s[:-1]+b'/>' if not s.endswith(b'/>') else s)
 if node.get('name') in targets:
  s,count=re.subn(rb'\bram="[0-9]+"',b'ram="'+str(targets[node.get('name')]).encode()+b'"',s)
  assert count==1
 return s
# Chỉ thay giá trị RAM trong start tag, không serialize lại topology.
after=re.sub(rb'<node\b[^>]*?(?=/?>)/?>',replace,before)
new=E.fromstring(after)
for old,n in zip(root.findall('.//node'),new.findall('.//node')):
 expected=dict(old.attrib)
 if old.get('name') in targets:expected['ram']=str(targets[old.get('name')])
 assert n.attrib==expected
 assert E.tostring(old).replace(('ram="'+old.get('ram','')+'"').encode(),b'ram="RESOURCE"')==E.tostring(n).replace(('ram="'+n.get('ram','')+'"').encode(),b'ram="RESOURCE"')
assert len(root.findall('.//node'))==len(new.findall('.//node'))
assert before!=after
p.write_bytes(after)
print(json.dumps({'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest(),'changes':targets,'only_ram_changed':True,'nodes_off_verified':True}))
'''
if __name__=='__main__':print(json.dumps(save('resource-change',json.loads(remote(CODE)))))
