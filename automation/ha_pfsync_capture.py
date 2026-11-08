"""Thu hữu hạn gói protocol 240 giữa hai peer SYNC; PCAP giữ riêng trên EVE."""
import json,datetime as dt
from topology_remote import remote,ROOT
CODE=r'''
import socket,struct,time,pathlib,json,hashlib
directory=pathlib.Path('/root/soc-ha-pfsync-capture-20261102-'+str(int(time.time())))
directory.mkdir(mode=0o700);path=directory/'pfsync.pcap'
rows=[];s=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3));s.bind(('vunl0_2_2',0));s.settimeout(1)
start=time.monotonic()
with path.open('xb') as out:
 out.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1))
 while time.monotonic()-start<35:
  try:data=s.recv(65535)
  except socket.timeout:continue
  if len(data)<34 or data[12:14]!=b'\x08\x00' or data[23]!=240:continue
  src=socket.inet_ntoa(data[26:30]);dst=socket.inet_ntoa(data[30:34])
  if {src,dst}!={'10.255.255.1','10.255.255.2'}:continue
  now=time.time();out.write(struct.pack('<IIII',int(now),int(now%1*1000000),len(data),len(data)));out.write(data)
  rows.append({'elapsed_s':round(time.monotonic()-start,3),'source':src,'destination':dst,'protocol':240,'bytes':len(data)})
s.close();path.chmod(0o600)
result={'scope':'Real protocol-240 packets only; not proof of CARP failover or complete state-table replication','capture_interface':'vunl0_2_2','pcap_path':str(path),'pcap_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'packets':rows,'packet_count':len(rows),'both_directions':{r['source'] for r in rows}=={'10.255.255.1','10.255.255.2'}}
(directory/'public.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''
if __name__=='__main__':
 d=json.loads(remote(CODE,timeout=55));d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
 p=ROOT/'docs/evidence/M3/resume-20261102/pfsync-packets.json';p.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps(d))
