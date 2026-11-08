import hashlib,json,os,pathlib,subprocess,xml.etree.ElementTree as E
os.umask(0o077)
raw=pathlib.Path('/conf/config.xml').read_bytes();root=E.fromstring(raw)
local=root.findtext('interfaces/opt6/ipaddr');role='Primary' if local=='10.255.255.1' else ('Secondary' if local=='10.255.255.2' else 'UNKNOWN')
backup=pathlib.Path('/root/soc-m36-20261106');backup.mkdir(mode=0o700,exist_ok=True);dest=backup/'config.before.xml'
if dest.exists():assert dest.read_bytes()==raw,'Existing M3.6 backup differs; stop'
else:dest.write_bytes(raw);dest.chmod(0o600)
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=30)
 return {'rc':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-2000:]}
def subtree_hash(path):
 n=root.find(path);return hashlib.sha256(E.tostring(n)).hexdigest() if n is not None else None
hasync=root.find('hasync')
public_hasync={k:(hasync.findtext(k) if hasync is not None else None) for k in ['pfsyncinterface','pfsyncpeerip','pfsyncversion','synchronizetoip','syncitems','disablepreempt']}
kea=root.find('./OPNsense/Kea/dhcp4')
kea_public=[]
if kea is not None:
 for s in kea.findall('./subnets/subnet4'):
  kea_public.append({'subnet':s.findtext('subnet'),'pools':s.findtext('pools'),'routers':s.findtext('./option_data/routers'),'dns':s.findtext('./option_data/domain_name_servers'),'description':s.findtext('description')})
rules=[]
fw=root.find('./OPNsense/Firewall/Filter/rules')
if fw is not None:
 for r in fw.findall('rule'):
  desc=r.findtext('description') or ''
  if desc.startswith('SOC M35') or desc.startswith('SOC HA'):
   rules.append({'description':desc,'enabled':r.findtext('enabled'),'interface':r.findtext('interface'),'protocol':r.findtext('protocol'),'source':r.findtext('source_net'),'destination':r.findtext('destination_net'),'port':r.findtext('destination_port')})
d={'role':role,'hostname':run(['/bin/hostname']),'version':run(['/usr/local/sbin/opnsense-version']),
   'config_sha256':hashlib.sha256(raw).hexdigest(),'backup':str(dest),'backup_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'backup_mode':oct(dest.stat().st_mode&0o777),
   'public_hasync':public_hasync,'kea':kea_public,'rules':rules,
   'hashes':{x:subtree_hash(x) for x in ['interfaces','virtualip','hasync','OPNsense/Kea','OPNsense/Firewall']},
   'carp':run(['/sbin/ifconfig','-a']),'pfsync':run(['/sbin/ifconfig','pfsync0']),
   'kea_status':run(['/usr/local/sbin/configctl','kea','status']),'pf_rules':run(['/sbin/pfctl','-sr']),
   'sync_ping':run(['/sbin/ping','-c','2','-S',local,'10.255.255.2' if role=='Primary' else '10.255.255.1'])}
