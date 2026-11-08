"""Boot một node theo ngân sách có reserve 1536 MiB; không sửa cấu hình."""
import sys,json
from topology_remote import remote
from m3_resource_optimization import save
name=sys.argv[1]
code=r'''
import pathlib,json,os,subprocess,xml.etree.ElementTree as E
name=__NAME__;p='/opt/unetlab/labs/SOC-M2-Core-L2.unl';r=E.parse(p).getroot();n=next(n for n in r.findall('.//node') if n.get('name')==name)
running=[]
for c in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[x.decode(errors='replace') for x in c.read_bytes().split(b'\0') if x]
  if a and 'qemu-system-' in os.path.basename(a[0]):running.append({'name':a[a.index('-name')+1],'ram':int(a[a.index('-m')+1])})
 except (OSError,ValueError):pass
assert name not in {x['name'] for x in running}
m={s.split(':')[0]:int(s.split()[1]) for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if len(s.split())>1 and s.split()[1].isdigit()}
total=sum(x['ram'] for x in running)+int(n.get('ram'))
assert total*1024+1536*1024<m['MemTotal']
assert m['MemAvailable']>(int(n.get('ram'))+1024)*1024
x=subprocess.run(['/opt/unetlab/wrappers/unl_wrapper','-a','start','-T','0','-F',p,'-D',n.get('id')],capture_output=True,text=True,timeout=45)
assert x.returncode==0,x.stderr
print(json.dumps({'node':name,'allocated_total_mib':total,'reserve_policy_mib':1536,'stdout':x.stdout,'stderr':x.stderr,'rc':x.returncode,'boot_verified':False}))
'''.replace('__NAME__',repr(name))
print(json.dumps(save('start-'+name,json.loads(remote(code,timeout=60)))))
