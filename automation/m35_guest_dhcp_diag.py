import json,pathlib,subprocess
def run(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=20)
 return {'rc':p.returncode,'stdout':p.stdout[-10000:],'stderr':p.stderr[-3000:]}
d={'kea_config':pathlib.Path('/usr/local/etc/kea/kea-dhcp4.conf').read_text() if pathlib.Path('/usr/local/etc/kea/kea-dhcp4.conf').exists() else None,
   'sockstat':run(['/usr/bin/sockstat','-4','-l']),
   'service':run(['/usr/local/sbin/configctl','kea','status']),
   'kea_log':run(['/usr/bin/tail','-n','80','/var/log/kea/kea-dhcp4.log']),
   'pf_dhcp':run(['/sbin/pfctl','-sr'])}
