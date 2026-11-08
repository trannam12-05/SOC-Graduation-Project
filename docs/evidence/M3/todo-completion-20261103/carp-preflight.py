import pathlib,subprocess,xml.etree.ElementTree as e
r=e.parse('/conf/config.xml').getroot();local=r.findtext('interfaces/opt6/ipaddr');role='primary' if local=='10.255.255.1' else 'secondary'
secret=pathlib.Path('/root/soc-m3-1b-'+role+'-20261103/carp-shared.secret')
assert secret.is_file() and secret.stat().st_mode&0o077==0 and len(secret.read_bytes())==19
model=pathlib.Path('/usr/local/opnsense/mvc/app/models/OPNsense/Interfaces/Vip.xml');actions=pathlib.Path('/usr/local/opnsense/service/conf/actions.d/actions_interface.conf').read_text();start=actions.index('[vip.configure]')
ips={n.tag:{k:n.findtext(k) for k in ['if','ipaddr','subnet']} for n in r.findall('interfaces/*')}
pf=subprocess.run(['pfctl','-sr'],capture_output=True,text=True,timeout=15)
d={'role':role,'secret_present_root_only_19_bytes':True,'model':model.read_text(),'vip_native_action':actions[start:].split('\n[',1)[0],'interfaces':ips,'vip_count':len(r.findall('.//vip')),'carp_filter_rules':[l for l in pf.stdout.splitlines() if 'carp' in l.lower()],'carp_sysctl':subprocess.check_output(['sysctl','net.inet.carp.allow','net.inet.carp.preempt','net.inet.carp.demotion'],text=True)}
