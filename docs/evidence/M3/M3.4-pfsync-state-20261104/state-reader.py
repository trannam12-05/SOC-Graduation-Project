"""Đọc duy nhất state của flow kiểm thử; không tạo/xóa state hay sửa rule."""
import subprocess,re,hashlib,pathlib
q=subprocess.run(['pfctl','-ss','-vv'],text=True,capture_output=True,timeout=15)
lines=q.stdout.splitlines();blocks=[]
for i,line in enumerate(lines):
    if '192.168.40.100:44340' in line and '192.168.30.10:8000' in line:
        block=[line]
        for nxt in lines[i+1:]:
            if nxt and not nxt[0].isspace():break
            block.append(nxt)
        text='\n'.join(block);m=re.search(r'id:\s*(\S+)\s+creatorid:\s*(\S+)',text)
        blocks.append(dict(text=text,id=m.group(1) if m else None,creatorid=m.group(2) if m else None,established='ESTABLISHED:ESTABLISHED' in text))
def cmd(args):
    x=subprocess.run(args,text=True,capture_output=True,timeout=15);return dict(rc=x.returncode,out=x.stdout)
d=dict(flow='192.168.40.100:44340 -> 192.168.30.10:8000',state_read_rc=q.returncode,blocks=blocks,pfsync=cmd(['ifconfig','pfsync0']),demotion=cmd(['sysctl','-n','net.inet.carp.demotion']),carp=cmd(['ifconfig','vtnet0_vlan40']),pfsync_stats=cmd(['netstat','-s','-p','pfsync']),config_sha256=hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest())
d['carp_all']=[]
for vlan in [30,40,50,60,99]:
    s=cmd(['ifconfig','vtnet0_vlan'+str(vlan)])['out']
    d['carp_all'].append(dict(vlan=vlan,state=re.findall(r'carp: (\w+)',s),vip_ok=('inet 192.168.%d.1 netmask 0xffffff00'%vlan) in s,carp=[l.strip() for l in s.splitlines() if 'carp:' in l]))
