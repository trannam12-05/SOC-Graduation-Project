import pathlib,subprocess,time
def run(a,timeout=120):
 p=subprocess.run(a,capture_output=True,text=True,timeout=timeout);return {'command':' '.join(a),'rc':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-4000:]}
before=pathlib.Path('/conf/config.xml').stat().st_mtime
steps=[run(['/usr/local/sbin/configctl','system','ha_reconfigure_backup'],180)]
time.sleep(8)
steps.append(run(['/usr/local/sbin/configctl','kea','status']))
steps.append(run(['/usr/local/sbin/configctl','system','ha','services_cached']))
d={'status':'DONE' if steps[0]['rc']==0 else 'FAILED','config_mtime_before':before,'steps':steps}
