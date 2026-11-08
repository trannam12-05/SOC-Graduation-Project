import pathlib,xml.etree.ElementTree as E,subprocess,hashlib
r=E.fromstring(pathlib.Path('/conf/config.xml').read_bytes())
def canonical(n):
 return {'tag':n.tag,'attrs':dict(sorted(n.attrib.items())),'text':(n.text or '').strip(),'children':[canonical(c) for c in n]}
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=25)
 return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
rules=[canonical(n) for n in r.findall('./OPNsense/Firewall/Filter/rules/rule') if (n.findtext('description') or '').startswith('SOC M35')]
pools=[canonical(n) for n in r.findall('./OPNsense/Kea/dhcp4/subnets/subnet4')]
d={'role':r.findtext('system/hostname'),'syncitems':r.findtext('hasync/syncitems'),'rules':rules,'pools':pools,'runtime':{k:run(a) for k,a in {'interfaces':['/sbin/ifconfig','-a'],'pfsync':['/sbin/ifconfig','pfsync0'],'filter':['/sbin/pfctl','-sr'],'nat':['/sbin/pfctl','-sn'],'routes':['/sbin/route','-n','get','default'],'kea':['/usr/local/sbin/configctl','kea','status']}.items()}}
