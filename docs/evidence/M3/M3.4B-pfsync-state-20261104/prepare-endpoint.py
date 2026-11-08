import sys,json
from pathlib import Path
sys.path.insert(0,'automation')
import m3_todo_console as c
c.OUT=Path(__file__).parent
assert json.loads((c.OUT/'before-acceptance.json').read_text())['status']=='PASS'
original=c.pycmd
c.pycmd=lambda source:'sudo -n '+original(source)
source="""import pathlib,subprocess,json,os,hashlib
os.umask(0o077);p=pathlib.Path('/root/soc-m34b-20261104');p.mkdir(mode=0o700,exist_ok=True)
def routes():return json.loads(subprocess.check_output(['ip','-j','route'],text=True))
before=routes();assert not any(r.get('dst') in ['192.168.40.100','192.168.40.100/32'] for r in before)
b=p/'routes.before.json';assert not b.exists();b.write_text(json.dumps(before));b.chmod(0o600)
q=subprocess.run(['ip','route','add','192.168.40.100/32','via','192.168.30.1','dev','lan0'],text=True,capture_output=True);assert q.returncode==0,q.stderr
after=routes();assert [r for r in before if r['dst']=='default']==[r for r in after if r['dst']=='default']
d={'routes_before':before,'routes_after':after,'default_route_unchanged':True,'backup':str(b),'backup_mode':oct(b.stat().st_mode&0o777),'backup_sha256':hashlib.sha256(b.read_bytes()).hexdigest(),'route_get':json.loads(subprocess.check_output(['ip','-j','route','get','192.168.40.100'],text=True)),'scope':'One test host route via existing CARP VIP; no IP/default route/netplan/topology changes'}
"""
d=c.run('Data-Center','endpoint-test-route',source)
print(json.dumps(d,ensure_ascii=True))
