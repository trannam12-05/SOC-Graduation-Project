import pathlib,os,hashlib,datetime,subprocess,xml.etree.ElementTree as E
os.umask(0o077)
raw=pathlib.Path('/conf/config.xml').read_bytes();r=E.fromstring(raw)
folder=pathlib.Path('/root/soc-m3-nat-prechange-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
folder.mkdir(mode=0o700);p=folder/'config.before.xml';p.write_bytes(raw);p.chmod(0o600)
assert p.read_bytes()==raw
def run(a):
 x=subprocess.run(a,capture_output=True,text=True,timeout=15);return {'rc':x.returncode,'stdout':x.stdout,'stderr':x.stderr}
d={'role':r.findtext('system/hostname'),'backup':str(p),'backup_mode':oct(p.stat().st_mode&0o777),'config_sha256':hashlib.sha256(raw).hexdigest(),'backup_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'wan':run(['/sbin/ifconfig','vtnet1']),'default_route':run(['/sbin/route','-n','get','-inet','default']),'scope':'Backup only; no configuration, link, service or HA changes'}
