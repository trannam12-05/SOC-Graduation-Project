import pathlib,subprocess,json,xml.etree.ElementTree as E
root=E.parse('/conf/config.xml').getroot();opn=root.find('OPNsense')
def leaves(x,prefix='',depth=0):
    if x is None or depth>7:return []
    path=(prefix+'/'+x.tag).strip('/');children=list(x)
    if not children:
        value=(x.text or '').strip()
        return [{'path':path,'value':value[:200],'attributes':dict(x.attrib)}]
    out=[]
    for c in children:out.extend(leaves(c,path,depth+1))
    return out
models={}
for x in (list(opn) if opn is not None else []):
    if x.tag.lower() in ['kea','firewall','filter','dnsmasq','aliases']:
        models[x.tag]=leaves(x)[:300]
legacy_filter=[]
f=root.find('filter')
if f is not None:
    for child in f:
        legacy_filter.append({'tag':child.tag,'attributes':dict(child.attrib),'children':[(c.tag,(c.text or '').strip(),dict(c.attrib)) for c in child]})
def run(cmd):
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
    return {'rc':p.returncode,'stdout':p.stdout[-10000:],'stderr':p.stderr[-1000:]}
d={'opnsense_child_tags':[x.tag for x in opn] if opn is not None else [],'model_leaves':models,'legacy_filter':legacy_filter,'pf_rules':run(['/sbin/pfctl','-sr']),'action_files':[p.name for p in pathlib.Path('/usr/local/opnsense/service/conf/actions.d').glob('*') if any(k in p.name.lower() for k in ['kea','dhcp','filter','firewall','unbound','dnsmasq'])]}
