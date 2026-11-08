import pathlib,subprocess,json,xml.etree.ElementTree as E
root=E.parse('/conf/config.xml').getroot()
def tree(x,depth=0):
    if x is None:return None
    if depth>6:return {'tag':x.tag,'truncated':True}
    text=(x.text or '').strip()
    return {'tag':x.tag,'attributes':dict(x.attrib),'text':text if len(text)<300 else text[:300]+'...','children':[tree(c,depth+1) for c in x]}
opn=root.find('OPNsense')
selected=[]
for x in (list(opn) if opn is not None else []):
    if x.tag.lower() in ['kea','firewall','filter','dnsmasq','unboundplus','interfaces','aliases']:
        selected.append(tree(x))
def run(cmd):
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
    return {'rc':p.returncode,'stdout':p.stdout[-30000:],'stderr':p.stderr[-3000:]}
d={'opnsense_child_tags':[x.tag for x in opn] if opn is not None else [],'selected_models':selected,'legacy_filter':tree(root.find('filter')),'legacy_dnsmasq':tree(root.find('dnsmasq')),'pf_rules':run(['/sbin/pfctl','-sr']),'pf_nat':run(['/sbin/pfctl','-sn']),'kea_actions':run(['/usr/local/sbin/configctl','configd','actions','list'])}
