"""Đọc guard WAN/HA và xuất một frame có SHA-256; không sửa cấu hình."""
import pathlib,subprocess,re,json,hashlib,zlib,struct,base64,xml.etree.ElementTree as E
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=6);return p.stdout
r=E.fromstring(pathlib.Path('/conf/config.xml').read_bytes())
allif=run(['/sbin/ifconfig','-a']);wan=run(['/sbin/ifconfig','vtnet1']);sync=run(['/sbin/ifconfig','pfsync0'])
route=run(['/sbin/route','-n','get','-inet','default'])
role='Primary' if r.findtext('interfaces/opt6/ipaddr')=='10.255.255.1' else 'Secondary'
ips=re.findall(r'^\s*inet (\S+) netmask (\S+)',wan,re.M)
gateway=re.search(r'gateway:\s*(\S+)',route)
demotion=run(['/sbin/sysctl','-n','net.inet.carp.demotion']).strip()
d={'role':role,'wan':ips,'gateway':gateway.group(1) if gateway else None,'carp':re.findall(r'carp: (\S+) vhid (\d+)',allif),'syncok':bool(re.search(r'syncok: 1\b',sync)),'demotion':demotion,'protected':{p:hashlib.sha256(E.tostring(r.find(p))).hexdigest() for p in ['interfaces','virtualip','hasync']},'hook':hashlib.sha256(pathlib.Path('/usr/local/etc/rc.syshook.d/start/96-soc-pfsync').read_bytes()).hexdigest()}
b=zlib.compress(json.dumps(d,separators=(',',':')).encode(),9);assert len(b)<=924
packet=(struct.pack('>I32s',len(b),hashlib.sha256(b).digest())+b).ljust(960,b'\0')
s=base64.b64encode(packet).decode();print('\x1b[2J\x1b[H'+'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='+'\n'+'\n'.join(s[i:i+80] for i in range(0,len(s),80)))
