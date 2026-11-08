import pathlib,subprocess,json,re,hashlib,xml.etree.ElementTree as e
def run(a):
 q=subprocess.run(a,capture_output=True,text=True,timeout=15);return dict(rc=q.returncode,stdout=q.stdout,stderr=q.stderr)
r=e.parse('/conf/config.xml').getroot();local=r.findtext('interfaces/opt6/ipaddr');primary=local=='10.255.255.1';role='primary' if primary else 'secondary';expected='MASTER' if primary else 'BACKUP';rows=[]
for i,vlan in enumerate([30,40,50,60,99]):
 nodes=[n for n in r.findall('virtualip/vip') if n.findtext('subnet')=='192.168.%d.1'%vlan];assert len(nodes)==1
 n=nodes[0];fields={k:n.findtext(k) for k in ['mode','interface','subnet','subnet_bits','vhid','advbase','advskew']};runtime=run(['ifconfig','vtnet0_vlan'+str(vlan)])
 ok=fields==dict(mode='carp',interface='opt'+str(i+1),subnet='192.168.%d.1'%vlan,subnet_bits='24',vhid=str(vlan),advbase='1',advskew='0' if primary else '100') and ('carp: '+expected+' vhid '+str(vlan)+' ') in runtime['stdout'] and ('inet 192.168.%d.1 netmask 0xffffff00'%vlan) in runtime['stdout']
 rows.append(dict(vlan=vlan,persistent=fields,runtime=runtime,expected_state=expected,pass_verified=ok))
pf=run(['pfctl','-sr']);d={'role':role,'rows':rows,'all_five_pass':all(x['pass_verified'] for x in rows),'pfsync':run(['ifconfig','pfsync0']),'demotion':run(['sysctl','net.inet.carp.demotion']),'carp_filter_rules':[l for l in pf['stdout'].splitlines() if 'carp' in l.lower()],'config_sha256':hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest(),'vip_count':len(r.findall('virtualip/vip')),'failover_tested':False}
