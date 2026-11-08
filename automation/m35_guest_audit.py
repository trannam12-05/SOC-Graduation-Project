import pathlib,subprocess,json,hashlib,shutil,os,xml.etree.ElementTree as E
os.umask(0o077)
conf=pathlib.Path('/conf/config.xml');raw=conf.read_bytes();root=E.fromstring(raw)
backup=pathlib.Path('/root/soc-m35-20261105');backup.mkdir(mode=0o700,exist_ok=True)
dest=backup/'config.before.xml'
if dest.exists():
    assert dest.read_bytes()==raw,'Existing M3.5 backup differs from current config; stop'
else:
    dest.write_bytes(raw);dest.chmod(0o600)
assert hashlib.sha256(dest.read_bytes()).hexdigest()==hashlib.sha256(raw).hexdigest()
def text(node,name):
    x=node.find(name) if node is not None else None
    return (x.text or '') if x is not None else None
interfaces={}
it=root.find('interfaces')
if it is not None:
    for x in it:
        interfaces[x.tag]={'if':text(x,'if'),'descr':text(x,'descr'),'ipaddr':text(x,'ipaddr'),'subnet':text(x,'subnet'),'enable':x.find('enable') is not None}
dhcpd={}
dh=root.find('dhcpd')
if dh is not None:
    for x in dh:
        rng=x.find('range')
        dhcpd[x.tag]={'enable':x.find('enable') is not None,'from':text(rng,'from'),'to':text(rng,'to'),'gateway':text(x,'gateway'),'dnsserver':[z.text for z in x.findall('dnsserver') if z.text]}
rules=[]
filt=root.find('filter')
if filt is not None:
    for r in filt.findall('rule'):
        src=r.find('source');dst=r.find('destination')
        rules.append({'uuid':r.get('uuid'),'type':text(r,'type'),'interface':text(r,'interface'),'protocol':text(r,'protocol'),'descr':text(r,'descr'),'source_network':text(src,'network'),'source_address':text(src,'address'),'destination_network':text(dst,'network'),'destination_address':text(dst,'address'),'destination_port':text(dst,'port'),'disabled':r.find('disabled') is not None})
models={}
opn=root.find('OPNsense')
if opn is not None:
    for child in opn:
        low=child.tag.lower()
        if any(k in low for k in ['kea','dnsmasq','dhcp','unbound']):models[child.tag]={'attributes':dict(child.attrib),'children':[x.tag for x in child][:80]}
def run(cmd):
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
    return {'rc':p.returncode,'stdout':p.stdout[-8000:],'stderr':p.stderr[-2000:]}
d={'hostname':subprocess.run(['hostname'],capture_output=True,text=True).stdout.strip(),'version':run(['/usr/local/sbin/opnsense-version']),'config_sha256':hashlib.sha256(raw).hexdigest(),'backup_path':str(dest),'backup_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'backup_mode':oct(dest.stat().st_mode & 0o777),'interfaces':interfaces,'dhcpd':dhcpd,'opnsense_models':models,'rules':rules,'ifconfig_carp':run(['/sbin/ifconfig','-g','carp']),'ifconfig_pfsync':run(['/sbin/ifconfig','pfsync0']),'processes':run(['/bin/ps','auxww']),'config_root_tags':[x.tag for x in root]}
