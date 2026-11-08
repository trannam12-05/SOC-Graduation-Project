import hashlib,os,pathlib,subprocess,xml.etree.ElementTree as E
os.umask(0o077);raw=pathlib.Path('/conf/config.xml').read_bytes();root=E.fromstring(raw)
local=root.findtext('interfaces/opt6/ipaddr');role='Primary' if local=='10.255.255.1' else 'Secondary';peer='10.255.255.2' if role=='Primary' else '10.255.255.1'
backup=pathlib.Path('/root/soc-m36-20261106');backup.mkdir(mode=0o700,exist_ok=True);dest=backup/'config.before.xml'
if not dest.exists():dest.write_bytes(raw);dest.chmod(0o600)
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=25);return {'rc':p.returncode,'stdout':p.stdout[-5000:],'stderr':p.stderr[-1000:]}
ifc=run(['/sbin/ifconfig','-a'])['stdout']
carp=[x.strip() for x in ifc.splitlines() if 'carp:' in x or ('inet 192.168.' in x and 'vhid ' in x)]
hasync=root.find('hasync');public={k:(hasync.findtext(k) if hasync is not None else None) for k in ['pfsyncinterface','pfsyncpeerip','pfsyncversion','synchronizetoip','syncitems','disablepreempt']}
kea=root.find('./OPNsense/Kea/dhcp4');subnets=[]
if kea is not None:
 for s in kea.findall('./subnets/subnet4'):subnets.append({'subnet':s.findtext('subnet'),'pools':s.findtext('pools'),'routers':s.findtext('./option_data/routers'),'dns':s.findtext('./option_data/domain_name_servers')})
rules=[];fw=root.find('./OPNsense/Firewall/Filter/rules')
if fw is not None:
 for r in fw.findall('rule'):
  desc=r.findtext('description') or ''
  if desc.startswith('SOC M35'):rules.append(desc)
d={'role':role,'config_sha256':hashlib.sha256(raw).hexdigest(),'backup':str(dest),'backup_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'current_matches_prechange_backup':dest.read_bytes()==raw,'backup_mode':oct(dest.stat().st_mode&0o777),
   'public_hasync':public,'kea_enabled':kea.findtext('./general/enabled') if kea is not None else None,'kea_interfaces':kea.findtext('./general/interfaces') if kea is not None else None,'kea_subnets':subnets,'m35_rules':rules,
   'carp':carp,'pfsync':run(['/sbin/ifconfig','pfsync0']),'kea_status':run(['/usr/local/sbin/configctl','kea','status']),'sync_ping':run(['/sbin/ping','-c','2','-S',local,peer])}
