import pathlib,subprocess,xml.etree.ElementTree as E,re
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=15)
 return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def tree(n):
 return None if n is None else {'tag':n.tag,'attrs':dict(n.attrib),'text':(n.text or '').strip(),'children':[tree(x) for x in n]}
r=E.fromstring(pathlib.Path('/conf/config.xml').read_bytes())
h=pathlib.Path('/usr/local/etc/rc.syshook.d/start/96-soc-pfsync')
d={'hostname':r.findtext('system/hostname'),'hook':h.read_text() if h.exists() else None,'hasync':{k:r.findtext('hasync/'+k) for k in ['pfsyncinterface','pfsyncpeerip','pfsyncversion','disablepreempt']},'sync_interface':tree(r.find('interfaces/opt6')),'nat_outbound':tree(r.find('nat/outbound')),'gateways':tree(r.find('gateways')),'wan_config':tree(r.find('interfaces/wan')),'pfsync_stats':run(['/usr/bin/netstat','-s','-p','pfsync'])}
d['sync_filter']=[s for s in run(['/sbin/pfctl','-sr'])['stdout'].splitlines() if 'vtnet2' in s or 'pfsync' in s]
d['log_events']=[]
for p in pathlib.Path('/var/log/system').glob('*20261106*.log'):
 lines=p.read_text(errors='replace').splitlines()
 d['log_events'] += [s for s in lines if re.search('pfsync|demoted|bulk',s,re.I) and not re.search('password|token|secret|authorization',s,re.I)][-25:]
for p in [pathlib.Path('/var/log/soc-pfsync-start.log'),pathlib.Path('/var/log/soc-pfsync.log')]:
 if p.exists():d[p.name]=p.read_text(errors='replace')[-1800:]
