import json,pathlib,subprocess,hashlib
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=30)
 return {'rc':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-2000:]}
d={'hostname':run(['hostname']),'ovs_show':run(['ovs-vsctl','show']),'ovs_ports':run(['ovs-vsctl','list','port']),
   'flows':run(['ovs-ofctl','dump-flows','br-soc']),'addresses':run(['ip','-br','address']),
   'ipv4_forward':pathlib.Path('/proc/sys/net/ipv4/ip_forward').read_text().strip(),
   'ipv6_forward':pathlib.Path('/proc/sys/net/ipv6/conf/all/forwarding').read_text().strip(),
   'config_sha256':hashlib.sha256(pathlib.Path('/etc/netplan/99-soc-core-l2.yaml').read_bytes()).hexdigest() if pathlib.Path('/etc/netplan/99-soc-core-l2.yaml').exists() else None}
