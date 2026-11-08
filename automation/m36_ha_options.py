import pathlib,subprocess
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=30);return {'rc':p.returncode,'stdout':p.stdout[-15000:],'stderr':p.stderr[-2000:]}
d={'options':run(['/usr/local/sbin/configctl','system','ha','options']),
   'model_files':[str(p) for p in pathlib.Path('/usr/local/opnsense/mvc/app/models').rglob('*HAsync*')],
   'actions':pathlib.Path('/usr/local/opnsense/service/conf/actions.d/actions_system.conf').read_text()[-12000:] if pathlib.Path('/usr/local/opnsense/service/conf/actions.d/actions_system.conf').exists() else ''}
