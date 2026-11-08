"""Backup mới và audit HA chỉ đọc; chỉ xuất ciphertext và trường công khai."""
import base64,hashlib,json,os,pathlib,secrets,subprocess,sys,zlib
import xml.etree.ElementTree as E
ROLE='__ROLE__'
PUBLIC_DER='__PUBLIC_DER__'
assert ROLE in ['Primary','Secondary'] and os.geteuid()==0
os.umask(0o077)
raw=pathlib.Path('/conf/config.xml').read_bytes();tree=E.fromstring(raw)
expected='10.255.255.1' if ROLE=='Primary' else '10.255.255.2'
assert tree.findtext('interfaces/opt6/ipaddr')==expected,'Unexpected firewall identity; stop'
work=pathlib.Path('/root/soc-m3-group1-'+ROLE.lower()+'-20261103');work.mkdir(mode=0o700,exist_ok=False)
backup=work/'config.xml'
with backup.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
backup.chmod(0o600)
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=20)
 return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def fields(n,names):
 return {k:n.findtext(k) for k in names.split() if n is not None and n.find(k) is not None}
interfaces=[{'assignment':n.tag,**fields(n,'if enable descr ipaddr subnet ipaddrv6 subnetv6')} for n in tree.findall('interfaces/*')]
vips=[]
for path in ['virtualip/vip','OPNsense/Interfaces/Vips/vip','OPNsense/Interfaces/Vip/vip']:
 for n in tree.findall(path):vips.append({'source':path,**fields(n,'mode interface subnet subnet_bits address prefix vhid advbase advskew descr')})
audit={'role':ROLE,'backup_path_guest':str(backup),'backup_bytes':len(raw),'backup_mode':oct(backup.stat().st_mode&0o777),'backup_directory_mode':oct(work.stat().st_mode&0o777),
 'config_sha256_before':hashlib.sha256(raw).hexdigest(),'backup_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),
 'interfaces':interfaces,'vlans':[fields(n,'if tag vlanif descr') for n in tree.findall('vlans/vlan')],
 'VIPs_public':vips,'sync_public':fields(tree.find('hasync'),'pfsyncinterface pfsyncpeerip pfsyncenabled synchronizetoip synchronizefilter synchronizetoip2 disablepreempt'),
 'version':run(['/usr/local/sbin/opnsense-version']),'runtime_ifconfig':run(['ifconfig','-a']),
 'carp_sysctl':run(['sysctl','net.inet.carp.allow','net.inet.carp.demotion','net.inet.carp.preempt']),
 'root_mount':run(['mount']),
 'scope':'Read-only HA audit and new backup; no config save/reload/probe/failover'}
audit['config_sha256_after']=hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest()
audit['config_unchanged']=audit['config_sha256_before']==audit['config_sha256_after']==audit['backup_sha256']
(work/'public-audit.json').write_text(json.dumps(audit))
# Bí mật chỉ trong guest root-only; transport chỉ dùng public key.
key=work/'transport-pass.key';key.write_text(secrets.token_hex(32))
pub=work/'transport-public.der';pub.write_bytes(base64.b64decode(PUBLIC_DER,validate=True))
compressed=work/'config.compressed';compressed.write_bytes(zlib.compress(raw,9))
encrypted=work/'config.enc';wrapped=work/'transport-pass.enc'
for cmd in [ ['openssl','enc','-aes-256-cbc','-salt','-pbkdf2','-iter','100000','-pass','file:'+str(key),'-in',str(compressed),'-out',str(encrypted)],
 ['openssl','pkeyutl','-encrypt','-pubin','-keyform','DER','-inkey',str(pub),'-in',str(key),'-out',str(wrapped),'-pkeyopt','rsa_padding_mode:oaep','-pkeyopt','rsa_oaep_md:sha256'] ]:
 p=subprocess.run(cmd,capture_output=True,timeout=25)
 assert p.returncode==0,'Backup encryption failed; do not export plaintext'
bundle={'session':'soc-m3-group1-20261103','audit':audit,'ciphertext_b64':base64.b64encode(encrypted.read_bytes()).decode(),'wrapped_passphrase_b64':base64.b64encode(wrapped.read_bytes()).decode(),
 'ciphertext_sha256':hashlib.sha256(encrypted.read_bytes()).hexdigest()}
(work/'encrypted-public-bundle.json').write_text(json.dumps(bundle))
transfer=base64.b64encode(zlib.compress(json.dumps(bundle,separators=(',',':')).encode(),9)).decode()
(work/'transfer.b64').write_text(transfer)
print('M3_BACKUP_READY',ROLE,'sha256',audit['backup_sha256'],'unchanged',audit['config_unchanged'],'VIP_count',len(vips),'transfer_chars',len(transfer),flush=True)
