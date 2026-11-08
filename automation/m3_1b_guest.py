"""M3-1B: kiểm tra xung đột, snapshot trước sửa, chỉ áp pfsync native; chưa tạo VIP."""
import base64,hashlib,hmac,json,os,pathlib,re,subprocess,sys,zlib
import xml.etree.ElementTree as E
ROLE=sys.argv[1];MODE=sys.argv[2]
assert ROLE in ['Primary','Secondary'] and MODE in ['audit','apply'] and os.geteuid()==0
os.umask(0o077)
WORK=pathlib.Path('/root/soc-m3-1b-'+ROLE.lower()+'-20261103')
def run(a):
 p=subprocess.run(a,text=True,capture_output=True,timeout=25)
 return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def config():return pathlib.Path('/conf/config.xml').read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
raw=config();root=E.fromstring(raw);local='10.255.255.1' if ROLE=='Primary' else '10.255.255.2';peer='10.255.255.2' if ROLE=='Primary' else '10.255.255.1'
assert root.findtext('interfaces/opt6/if')=='vtnet2' and root.findtext('interfaces/opt6/ipaddr')==local and root.findtext('interfaces/opt6/subnet')=='30'
targets=[f'192.168.{v}.1' for v in [30,40,50,60,99]]
conflicts=[];vhids=[]
def walk(n,path):
 path=path+'/'+n.tag
 if n.text:
  found=[t for t in targets if re.search(r'(?<![\d.])'+re.escape(t)+r'(?![\d.])',n.text)]
  if found:conflicts.append({'path':path,'VIPs':found})
  if n.tag.lower()=='vhid' and n.text.strip() not in ['','0']:vhids.append({'path':path,'value':n.text.strip()})
 for c in n:walk(c,path)
walk(root,'')
if conflicts or vhids:
 print('CONFLICT_STOP',ROLE,json.dumps({'VIP_references':conflicts,'VHIDs':vhids}));raise SystemExit(3)
def protect():
 tree=E.fromstring(config())
 return {name:sha(E.tostring(tree.find(name))) if tree.find(name) is not None else None for name in ['interfaces','filter','nat','dhcpd','dhcpdv6','hasync','virtualip','OPNsense']}
def output(d):
 d['config_sha256_after']=sha(config());d['config_unchanged']=d['config_sha256_before']==d['config_sha256_after']
 text=json.dumps(d,separators=(',',':'));(WORK/(MODE+'.json')).write_text(text)
 b=base64.b64encode(zlib.compress(text.encode(),9)).decode();(WORK/'reply.b64').write_text(b)
 print('M3_1B_READY',ROLE,MODE,len(b),sha(b.encode()),'config_unchanged',d['config_unchanged'],flush=True)
if MODE=='audit':
 WORK.mkdir(mode=0o700,exist_ok=False)
 with (WORK/'config.before.xml').open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 protected=protect();(WORK/'protected-before.json').write_text(json.dumps(protected))
 key=WORK/'carp-recipient-private.key'
 p=subprocess.run(['openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:2048','-out',str(key)],capture_output=True,timeout=25);assert p.returncode==0
 p=subprocess.run(['openssl','pkey','-in',str(key),'-pubout','-outform','DER','-out',str(WORK/'carp-recipient-public.der')],capture_output=True,timeout=25);assert p.returncode==0
 source=pathlib.Path('/usr/local/etc/inc/interfaces.inc').read_text()
 start=source.index('function interfaces_pfsync_configure(');end=source.index('\nfunction ',start+10)
 fn=source[start:end]
 actions=pathlib.Path('/usr/local/opnsense/service/conf/actions.d/actions_interface.conf').read_text()
 action=actions[actions.index('[pfsync.configure]'):].split('\n[',1)[0]
 callsites=[]
 for directory in ['/usr/local/etc/inc','/usr/local/etc/rc.bootup','/usr/local/opnsense/service/conf/actions.d']:
  base=pathlib.Path(directory);paths=[base] if base.is_file() else list(base.rglob('*.inc'))+list(base.rglob('*.conf'))
  for p in paths:
   if not p.is_file():continue
   try:lines=p.read_text(errors='replace').splitlines()
   except OSError:continue
   for i,line in enumerate(lines):
    if 'interfaces_pfsync_configure' in line or ('pfsync' in line and 'plugin' in str(p)):
     callsites.append({'file':str(p),'line':i+1,'context':lines[max(0,i-2):i+3]})
 arp=run(['arp','-an']);arp_conf=[l for l in arp['stdout'].splitlines() if any('('+t+')' in l for t in targets)]
 d={'role':ROLE,'mode':MODE,'config_sha256_before':sha(raw),'backup_sha256':sha((WORK/'config.before.xml').read_bytes()),'backup_guest':str(WORK/'config.before.xml'),'backup_bytes':len(raw),
 'VIP_references':conflicts,'VHIDs':vhids,'ARP_VIP_conflicts':arp_conf,'source_function':fn,'source_file_sha256':sha(source.encode()),'native_action':action,'source_callsites':callsites,
 'sync':{'assignment':'opt6','device':'vtnet2','local':local,'peer':peer,'configured_device':root.findtext('hasync/pfsyncinterface'),'configured_peer':root.findtext('hasync/pfsyncpeerip')},
 'runtime_before':run(['ifconfig','pfsync0']),'runtime_all':run(['ifconfig','-a']),'source_public_key_der_b64':base64.b64encode((WORK/'carp-recipient-public.der').read_bytes()).decode(),'protected_before':protected}
 output(d)
elif MODE=='apply':
 audit=json.loads((WORK/'audit.json').read_text());assert sha(raw)==audit['backup_sha256']
 assert root.findtext('hasync/pfsyncinterface')=='opt6' and root.findtext('hasync/pfsyncpeerip')==peer
 # Guard nguyên nhân/cách áp đúng mã cài; không sửa XML hoặc gọi configure interface khác.
 assert '/usr/local/sbin/pluginctl -c pfsync' in audit['native_action']
 assert "$config['hasync']['pfsyncinterface']" in audit['source_function'] and "'up'" in audit['source_function']
 cipher=WORK/'carp-shared-secret.enc';cipher.write_bytes(base64.b64decode(sys.argv[3],validate=True))
 secretpath=WORK/'carp-shared.secret';assert not secretpath.exists()
 p=subprocess.run(['openssl','pkeyutl','-decrypt','-inkey',str(WORK/'carp-recipient-private.key'),'-in',str(cipher),'-out',str(secretpath),'-pkeyopt','rsa_padding_mode:oaep','-pkeyopt','rsa_oaep_md:sha256'],capture_output=True,timeout=20)
 assert p.returncode==0,'Private secret decryption failed'
 secret=secretpath.read_bytes();assert len(secret)==19 and re.fullmatch(b'[A-Za-z0-9]{19}',secret)
 secretpath.chmod(0o600)
 applied=run(['/usr/local/sbin/configctl','interface','pfsync.configure'])
 after=run(['ifconfig','pfsync0'])
 assert protect()==audit['protected_before'],'Protected config changed unexpectedly'
 d={'role':ROLE,'mode':MODE,'config_sha256_before':sha(raw),'native_apply':applied,'runtime_after':after,'protected_sections_unchanged':True,'secret_path':str(secretpath),'secret_mode':oct(secretpath.stat().st_mode&0o777),'secret_attestation':hmac.new(secret,bytes.fromhex(sys.argv[4]),hashlib.sha256).hexdigest(),'CARP_VIPs_created':0}
 d['runtime_ready']=applied['rc']==0 and 'UP' in after['stdout'].splitlines()[0] and 'syncdev: vtnet2' in after['stdout'] and ('syncpeer: '+peer) in after['stdout']
 output(d)
