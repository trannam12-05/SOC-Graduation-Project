import pathlib,subprocess,json,hashlib,xml.etree.ElementTree as e
r=e.parse('/conf/config.xml').getroot()
files={}
for p in ['/usr/local/etc/rc.bootup','/usr/local/etc/inc/plugins.inc.d/pf.inc','/usr/local/etc/inc/interfaces.inc','/usr/local/etc/inc/plugins.inc']:
 lines=pathlib.Path(p).read_text().splitlines();hits=[]
 for i,line in enumerate(lines):
  if 'pfsync' in line or ('plugins_configure' in line and 'rc.bootup' in p):hits.append({'line':i+1,'context':lines[max(0,i-2):i+4]})
 files[p]=hits
def run(a):
 q=subprocess.run(a,capture_output=True,text=True,timeout=15);return dict(rc=q.returncode,stdout=q.stdout,stderr=q.stderr)
d={'source':files,'configured_sync':{k:r.findtext('hasync/'+k) for k in ['pfsyncinterface','pfsyncpeerip','pfsyncversion']},'runtime':run(['ifconfig','pfsync0']),'start_hooks':[p.name for p in pathlib.Path('/usr/local/etc/rc.syshook.d/start').iterdir()],'physmem':run(['sysctl','hw.physmem']),'config_sha256':hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest()}
