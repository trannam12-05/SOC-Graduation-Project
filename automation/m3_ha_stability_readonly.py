import pathlib,subprocess,time,datetime,json,re,xml.etree.ElementTree as E
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=12)
 return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
root=E.fromstring(pathlib.Path('/conf/config.xml').read_bytes())
d={'started_utc':stamp(),'hostname':root.findtext('system/hostname'),'wan_config':{k:root.findtext('interfaces/wan/'+k) for k in ['if','enable','ipaddr','subnet','gateway']},'boot':run(['/sbin/sysctl','kern.boottime']),'uptime':run(['/usr/bin/uptime'])}
logs=[]
for folder in ['/var/log/system','/var/log/routing']:
 for p in sorted(pathlib.Path(folder).glob('*.log'))[-3:]:
  lines=p.read_text(errors='replace').splitlines()[-8000:]
  hits=[s for s in lines if re.search(r'carp|pfsync|demot|bootup|shutdown|reboot',s,re.I) and not re.search(r'password|authorization|token|secret',s,re.I)]
  logs.append({'path':str(p),'matching_lines':hits[-45:]})
d['logs']=logs
d['kernel_events']=[s for s in run(['/sbin/dmesg'])['stdout'].splitlines() if re.search(r'carp|pfsync|demot',s,re.I)][-35:]
d['wan_runtime']=run(['/sbin/ifconfig',root.findtext('interfaces/wan/if') or 'vtnet1'])
d['default_route']=run(['/sbin/route','-n','get','-inet','default'])
d['nat']=run(['/sbin/pfctl','-sn'])
d['samples']=[]
for i in range(7):
 if i:time.sleep(10)
 info=run(['/sbin/ifconfig','-a'])
 d['samples'].append({'utc':stamp(),'carp':[s.strip() for s in info['stdout'].splitlines() if 'carp:' in s],'pfsync':run(['/sbin/ifconfig','pfsync0']),'carp_sysctl':run(['/sbin/sysctl','net.inet.carp.demotion','net.inet.carp.allow'])})
d['finished_utc']=stamp()
