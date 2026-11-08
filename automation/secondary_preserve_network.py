"""Chạy trong Secondary Live: chuyển riêng mạng đã xác nhận sang ổ đã cài.

Không format, không thay đĩa, không lấy cấu hình Primary. Giữ nguyên system,
người dùng/mật khẩu, chứng thư, NAT, DHCP và các rule không thuộc HA SYNC.
Mặc định chỉ kiểm tra. Trước --apply phải mount đúng vtbd0p3 đọc/ghi.
"""
from pathlib import Path
import argparse,copy,hashlib,json,os,shutil,subprocess,xml.etree.ElementTree as E

LIVE=Path('/conf/config.xml')
INSTALLED=Path('/tmp/soc-installed/conf/config.xml')
BACKUP=Path('/tmp/soc-installed/root/soc-ha-backup-20261102-1522')

def semantic(e):
 if e is None:return None
 return [e.tag,sorted(e.attrib.items()),(e.text or '').strip(),[semantic(c) for c in e]]
def digest(e):return hashlib.sha256(json.dumps(semantic(e),sort_keys=True).encode()).hexdigest()
def ensure(root,path):
 for name in path.split('/'):
  child=root.find(name)
  if child is None:child=E.SubElement(root,name)
  root=child
 return root
def replace(root,path,node):
 bits=path.split('/');parent=ensure(root,'/'.join(bits[:-1])) if len(bits)>1 else root
 old=parent.find(bits[-1])
 if old is not None:parent.remove(old)
 parent.append(copy.deepcopy(node))
def public_interfaces(root):
 return {n.tag:{k:n.findtext(k) for k in ['if','ipaddr','subnet']} for n in root.findall('interfaces/*')}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args()
 mount=subprocess.run(['mount'],text=True,capture_output=True,check=True).stdout
 assert '/dev/vtbd0p3 on /tmp/soc-installed ' in mount,'Wrong/missing installed mount'
 source=E.parse(LIVE).getroot();tree=E.parse(INSTALLED);target=tree.getroot()
 assert source.findtext('interfaces/opt6/if')=='vtnet2'
 assert source.findtext('interfaces/opt6/ipaddr')=='10.255.255.2','Not the inspected Secondary'
 protected=['system','cert','ca','ipsec','openvpn','nat','dhcpd','hasync','virtualip']
 before={name:digest(target.find(name)) for name in protected}
 old_rules=[digest(n) for n in target.findall('OPNsense/Firewall/Filter/rules/rule') if not n.findtext('description','').startswith('SOC HA SYNC ')]
 report={'mode':'APPLY' if args.apply else 'CHECK_ONLY','interfaces_before':public_interfaces(target),'interfaces_live':public_interfaces(source)}
 for path in ['interfaces','vlans','OPNsense/Interfaces/Vlan']:
  node=source.find(path)
  if node is not None:replace(target,path,node)
 # Chỉ thêm các rule HA theo peer của Secondary; không thay các rule khác.
 rules=ensure(target,'OPNsense/Firewall/Filter/rules')
 newrules=[]
 for rule in source.findall('OPNsense/Firewall/Filter/rules/rule'):
  desc=rule.findtext('description','')
  if not desc.startswith('SOC HA SYNC '):continue
  assert rule.findtext('interface')=='opt6' and rule.findtext('source_net')=='10.255.255.1/32'
  assert rule.findtext('destination_net')=='10.255.255.2/32' and rule.findtext('nosync')=='1'
  found=next((x for x in rules.findall('rule') if x.findtext('description')==desc),None)
  if found is not None:
   assert digest(found)==digest(rule),'Different existing disk HA rule'
  else:rules.append(copy.deepcopy(rule));newrules.append(desc)
 after={name:digest(target.find(name)) for name in protected}
 assert after==before,'Protected section changed in planned tree'
 assert old_rules==[digest(n) for n in target.findall('OPNsense/Firewall/Filter/rules/rule') if not n.findtext('description','').startswith('SOC HA SYNC ')]
 report.update({'protected_sections_unchanged':True,'existing_non_HA_rules_unchanged':True,'new_HA_rules':newrules,'interfaces_after':public_interfaces(target)})
 if args.apply:
  assert ', read-only' not in next(line for line in mount.splitlines() if ' on /tmp/soc-installed ' in line),'Mounted read-only'
  backup=BACKUP/'installed-config-before-network.xml'
  assert not backup.exists(),'Backup already exists: inspect current outcome, do not reapply blindly'
  with INSTALLED.open('rb') as src,backup.open('xb') as dst:shutil.copyfileobj(src,dst)
  backup.chmod(0o600)
  info=INSTALLED.stat();temporary=INSTALLED.with_name('config.xml.soc-network-new')
  assert not temporary.exists()
  with temporary.open('xb') as f:
   tree.write(f,encoding='utf-8',xml_declaration=True);f.flush();os.fsync(f.fileno())
  os.chmod(temporary,info.st_mode & 0o777);os.chown(temporary,info.st_uid,info.st_gid)
  check=E.parse(temporary).getroot()
  assert {n:digest(check.find(n)) for n in protected}==before
  os.replace(temporary,INSTALLED)
  report.update({'backup':str(backup),'config_sha256_after':hashlib.sha256(INSTALLED.read_bytes()).hexdigest(),'state':'NETWORK_MIGRATED_NOT_BOOT_VERIFIED'})
  (BACKUP/'network-migration-public.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report))
