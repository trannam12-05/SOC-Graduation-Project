import pathlib,subprocess,hashlib,xml.etree.ElementTree as E,re,os,shutil
os.umask(0o077)
def cmd(a):
 try:
  q=subprocess.run(a.split(),capture_output=True,text=True,timeout=10);return dict(rc=q.returncode,out=q.stdout)
 except subprocess.TimeoutExpired:return dict(rc=124,out='command timeout')
p=pathlib.Path('/conf/config.xml');raw=p.read_bytes();r=E.fromstring(raw);local=r.findtext('interfaces/opt6/ipaddr');primary=local=='10.255.255.1';peer='10.255.255.2' if primary else '10.255.255.1';role='primary' if primary else 'secondary';rows=[]
b=pathlib.Path('/root/soc-m34-20261104');b.mkdir(mode=0o700,exist_ok=True);backup=b/'config.before.xml'
if not backup.exists():shutil.copy2(p,backup);backup.chmod(0o600)
for v in [30,40,50,60,99]:
 s=cmd('ifconfig vtnet0_vlan'+str(v));t=s['out'];n=next(n for n in r.findall('virtualip/vip') if n.findtext('subnet')=='192.168.%d.1'%v)
 fields={k:n.findtext(k) for k in ['mode','interface','subnet','subnet_bits','vhid','advbase','advskew']}
 rows.append(dict(vlan=v,state=re.findall(r'carp: (\w+)',t),physical_ip_ok=('inet 192.168.%d.%d netmask 0xffffff00'%(v,2 if primary else 3)) in t,vip_ok=('inet 192.168.%d.1 netmask 0xffffff00'%v) in t,up='UP' in t.splitlines()[0],active='status: active' in t,persistent=fields,carp=[l.strip() for l in t.splitlines() if 'carp:' in l]))
boot=cmd('sysctl -n kern.boottime');log=pathlib.Path('/var/log/soc-pfsync-start.log').read_text()
d=dict(role=role,rows=rows,pfsync=cmd('ifconfig pfsync0'),demotion=cmd('sysctl -n net.inet.carp.demotion'),sync=cmd('ifconfig vtnet2'),ping=cmd('ping -c 2 '+peer),boottime=boot,hook_this_boot=boot['out'].strip() in log,hook_native_rc0='native_rc=0' in log,config_sha256=hashlib.sha256(raw).hexdigest(),backup_path=str(backup),backup_sha256=hashlib.sha256(backup.read_bytes()).hexdigest(),config_unchanged=raw==p.read_bytes())

q=cmd("pfctl -sr");d["flow_policy"]=[l for l in q["out"].splitlines() if "192.168.40.100" in l or "8000" in l]
