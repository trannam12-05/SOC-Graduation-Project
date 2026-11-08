import sys,json
from pathlib import Path
sys.path.insert(0,'automation')
import m3_todo_console as c
c.OUT=Path(__file__).parent
role,operation,label=sys.argv[1:4]
base="import runpy,json,pathlib;ns=runpy.run_path('/root/soc-m34b-20261104/native.py');"
if operation=='stage':
 src=(c.OUT/'native.py').read_text(encoding='utf-8');compile(src,'native','exec')
 source="import pathlib,os,hashlib;os.umask(0o077);p=pathlib.Path('/root/soc-m34b-20261104/native.py');assert not p.exists();p.write_text("+repr(src)+");p.chmod(0o700);d={'staged':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}"
elif operation=='capture':source=base+"d=ns['capture']()"
elif operation=='arm':source="""import pathlib,subprocess,sys,os,time,json
os.umask(0o077);p=pathlib.Path('/root/soc-m34b-20261104');assert not (p/'watcher-ready.json').exists();f=(p/'watcher.log').open('x');q=subprocess.Popen([sys.executable,str(p/'native.py'),'watch'],stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
for _ in range(50):
 if (p/'watcher-ready.json').exists():break
 assert q.poll() is None,'Watcher exited'
 time.sleep(0.1)
d=json.loads((p/'watcher-ready.json').read_text())
"""
elif operation=='after':source="import json,pathlib;d=json.loads(pathlib.Path('/root/soc-m34b-20261104/secondary-after-immediate.json').read_text())"
else:raise RuntimeError('Unsupported native operation')
d=c.run('OPNsense-'+role,role.lower()+'-'+label,source)
print(json.dumps({'role':role,'operation':operation,'blocks':d.get('blocks'),'carp_all':d.get('carp_all'),'trigger_delay':d.get('trigger_to_state_capture_seconds'),'pid':d.get('pid'),'staged':d.get('staged')},ensure_ascii=True))
