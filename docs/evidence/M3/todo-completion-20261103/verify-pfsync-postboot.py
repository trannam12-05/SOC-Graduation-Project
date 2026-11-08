import pathlib,subprocess,hashlib,xml.etree.ElementTree as e
def run(a):
 q=subprocess.run(a,capture_output=True,text=True,timeout=15);return dict(rc=q.returncode,stdout=q.stdout,stderr=q.stderr)
p=pathlib.Path('/conf/config.xml');raw=p.read_bytes();r=e.fromstring(raw)
local=r.findtext('interfaces/opt6/ipaddr');peer=r.findtext('hasync/pfsyncpeerip');runtime=run(['ifconfig','pfsync0']);boot=run(['sysctl','-n','kern.boottime'])
log=pathlib.Path('/var/log/soc-pfsync-start.log').read_text()
d={'local':local,'peer':peer,'runtime':runtime,'boottime':boot,'boot_hook_log':log,'hook_executed_this_boot':boot['stdout'].strip() in log,'config_unchanged':raw==pathlib.Path('/root/soc-m3-todo-pfsync-20261103/config.before.xml').read_bytes(),'config_sha256':hashlib.sha256(raw).hexdigest(),'demotion':run(['sysctl','net.inet.carp.demotion']),'sync_ping':run(['ping','-c','2',peer]),'pfsync_stats':run(['netstat','-s','-p','pfsync']),'all_interfaces':run(['ifconfig','-a'])}
d['ready']='UP' in runtime['stdout'].splitlines()[0] and 'syncdev: vtnet2' in runtime['stdout'] and ('syncpeer: '+peer) in runtime['stdout'] and 'syncok: 1' in runtime['stdout'] and d['hook_executed_this_boot'] and 'native_rc=0' in log
