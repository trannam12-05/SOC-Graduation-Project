import subprocess,json
def run(args):
    q=subprocess.run(args,text=True,capture_output=True,timeout=15);return dict(rc=q.returncode,out=q.stdout,err=q.stderr)
d={'services':run(['systemctl','is-active','openvswitch-switch','ovsdb-server','ovs-vswitchd']),'ports':run(['ovs-vsctl','--format=json','--columns=name,tag,trunks,vlan_mode','list','Port']),'bridge':run(['ovs-vsctl','list-br']),'flow':run(['ovs-ofctl','dump-flows','br-core-l2']),'addresses':run(['ip','-j','address']),'ipv4_forwarding':run(['sysctl','-n','net.ipv4.ip_forward']),'ipv6_forwarding':run(['sysctl','-n','net.ipv6.conf.all.forwarding']),'hostname':run(['hostname'])}
