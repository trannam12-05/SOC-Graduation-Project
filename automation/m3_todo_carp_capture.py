"""Bắt CARP thụ động trên trunk hiện hữu; chỉ xuất metadata, PCAP root-only."""
import json,sys,datetime as dt
from topology_remote import remote
from m3_todo_console import OUT
code=r'''
import socket,select,time,struct,pathlib,json,hashlib
directory=pathlib.Path('/root/soc-m3-carp-capture-'+str(time.time_ns()));directory.mkdir(mode=0o700)
sockets=[]
for name in ['vunl0_3_5','vunl0_3_6']:
 s=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3));s.bind((name,0));s.setblocking(False);sockets.append(s)
p=directory/'carp.pcap';f=p.open('xb');p.chmod(0o600);f.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1));rows=[];start=time.monotonic()
while time.monotonic()-start<20:
 ready,_,_=select.select(sockets,[],[],0.5)
 for s in ready:
  b=s.recv(65535);offset=14;vlan=None
  if len(b)<34:continue
  kind=b[12:14]
  if kind==b'\x81\x00':
   vlan=struct.unpack('!H',b[14:16])[0]&4095;kind=b[16:18];offset=18
  if kind!=b'\x08\x00' or len(b)<offset+20 or b[offset+9]!=112:continue
  c=offset+(b[offset]&15)*4
  if len(b)<c+8:continue
  now=time.time();f.write(struct.pack('<IIII',int(now),int(now%1*1000000),len(b),len(b)));f.write(b)
  rows.append(dict(tap=s.getsockname()[0],elapsed=round(time.monotonic()-start,3),vlan=vlan,source=socket.inet_ntoa(b[offset+12:offset+16]),destination=socket.inet_ntoa(b[offset+16:offset+20]),ttl=b[offset+8],vhid=b[c+1],advskew=b[c+2],advbase=b[c+5]))
f.close()
for s in sockets:s.close()
print(json.dumps({'scope':'Passive CARP metadata only; not failover testing','packets':rows,'pcap_private_path':str(p),'pcap_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'duration_s':20}))
'''
d=json.loads(remote(code,timeout=35));d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
with (OUT/(sys.argv[1]+'.json')).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
print(json.dumps({'packet_count':len(d['packets']),'evidence':sys.argv[1]}))
