import pathlib,subprocess,hashlib,os,xml.etree.ElementTree as e
os.umask(0o077)
p=pathlib.Path('/conf/config.xml');raw=p.read_bytes();r=e.fromstring(raw)
local=r.findtext('interfaces/opt6/ipaddr');peer={'10.255.255.1':'10.255.255.2','10.255.255.2':'10.255.255.1'}[local]
assert r.findtext('hasync/pfsyncinterface')=='opt6' and r.findtext('hasync/pfsyncpeerip')==peer and r.findtext('interfaces/opt6/if')=='vtnet2'
w=pathlib.Path('/root/soc-m3-todo-pfsync-20261103');w.mkdir(mode=0o700)
(w/'config.before.xml').write_bytes(raw)
h=pathlib.Path('/usr/local/etc/rc.syshook.d/start/96-soc-pfsync');assert not h.exists()
hook='''#!/bin/sh
# SOC M3: ap pfsync native sau khi network khoi dong; khong sua core/config.xml.
umask 077
{
 /bin/date -u
 /sbin/sysctl -n kern.boottime
 /usr/local/sbin/pluginctl -c pfsync
 result=$?
 /sbin/ifconfig pfsync0
 echo "native_rc=$result"
} > /var/log/soc-pfsync-start.log 2>&1
exit "$result"
'''
h.write_text(hook);h.chmod(0o700)
assert subprocess.run(['/bin/sh','-n',str(h)],capture_output=True).returncode==0
q=subprocess.run([str(h)],capture_output=True,text=True,timeout=25)
runtime=subprocess.run(['ifconfig','pfsync0'],capture_output=True,text=True,timeout=10)
assert p.read_bytes()==raw
d={'local':local,'peer':peer,'backup':str(w/'config.before.xml'),'config_sha256_before':hashlib.sha256(raw).hexdigest(),'config_unchanged':p.read_bytes()==raw,'hook_path':str(h),'hook_sha256':hashlib.sha256(h.read_bytes()).hexdigest(),'hook_mode':oct(h.stat().st_mode&0o777),'native_rc':q.returncode,'runtime':runtime.stdout,'ready':q.returncode==0 and 'UP' in runtime.stdout.splitlines()[0] and 'syncdev: vtnet2' in runtime.stdout and ('syncpeer: '+peer) in runtime.stdout,'boot_log':pathlib.Path('/var/log/soc-pfsync-start.log').read_text(),'boottime':subprocess.check_output(['sysctl','-n','kern.boottime'],text=True)}
