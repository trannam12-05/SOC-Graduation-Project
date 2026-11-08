import pathlib,xml.etree.ElementTree as E,subprocess
r=E.fromstring(pathlib.Path('/conf/config.xml').read_bytes())
def walk(x,p=''):
 out=[]
 for c in x:
  q=p+'/'+c.tag
  out.append({'path':q,'value':(c.text or '')[:500],'attributes':dict(c.attrib)})
  out.extend(walk(c,q))
 return out
d={'legacy_dnsmasq':walk(r.find('dnsmasq'),'dnsmasq') if r.find('dnsmasq') is not None else [],
   'model_dnsmasq':walk(r.find('./OPNsense/dnsmasq'),'OPNsense/dnsmasq') if r.find('./OPNsense/dnsmasq') is not None else [],
   'rc_scripts':[p.name for p in pathlib.Path('/usr/local/etc/rc.d').glob('*dnsmasq*')]}
