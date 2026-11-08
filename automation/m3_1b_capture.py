"""Thu thụ động protocol240 khi áp native pfsync; không phát probe hoặc tạo phiên thử."""
import argparse,base64,datetime,json
from topology_remote import ROOT,remote
p=argparse.ArgumentParser();p.add_argument('action',choices=['start','stop']);a=p.parse_args()
OUT=ROOT/'docs/evidence/M3/group1b-prerequisites-20261103'
WORKER=r'''
import socket,struct,time,pathlib,json,hashlib,signal
b=pathlib.Path('/root/soc-m3-1b-pfsync-capture-20261103')
running=True
def stop(s,f):
 global running
 running=False
signal.signal(signal.SIGTERM,stop)
s=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3));s.bind(('vunl0_2_2',0));s.settimeout(0.5)
rows=[];started=time.monotonic();p=b/'pfsync.pcap'
with p.open('xb') as f:
 f.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1))
 while running and time.monotonic()-started<600:
  try:data=s.recv(65535)
  except socket.timeout:continue
  if len(data)<34 or data[12:14]!=b'\x08\x00' or data[23]!=240:continue
  src=socket.inet_ntoa(data[26:30]);dst=socket.inet_ntoa(data[30:34])
  if {src,dst}!={'10.255.255.1','10.255.255.2'}:continue
  t=time.time();f.write(struct.pack('<IIII',int(t),int(t%1*1000000),len(data),len(data)));f.write(data)
  rows.append({'elapsed_seconds':round(time.monotonic()-started,3),'source':src,'destination':dst,'protocol':240,'bytes':len(data)})
s.close();p.chmod(0o600)
d={'scope':'Passive protocol240 capture, no state-retention or failover acceptance','interface':'vunl0_2_2','packets':rows,'both_directions':{r['source'] for r in rows}=={'10.255.255.1','10.255.255.2'},'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(b/'result.json').write_text(json.dumps(d))
'''
if a.action=='start':
 code="import pathlib,subprocess,json;b=pathlib.Path('/root/soc-m3-1b-pfsync-capture-20261103');b.mkdir(mode=0o700,exist_ok=False);p=subprocess.Popen(['python3','-c',"+repr(WORKER)+"],stdout=subprocess.DEVNULL,stderr=(b/'capture.stderr').open('w'),start_new_session=True);(b/'pid').write_text(str(p.pid));print(json.dumps({'started':True,'pid':p.pid,'interface':'vunl0_2_2'}))"
else:
 code=r'''
import pathlib,os,signal,time,json,base64
b=pathlib.Path('/root/soc-m3-1b-pfsync-capture-20261103');pid=int((b/'pid').read_text());p=pathlib.Path('/proc')/str(pid)/'cmdline'
if p.exists():
 assert b'soc-m3-1b-pfsync-capture' in p.read_bytes();os.kill(pid,signal.SIGTERM)
for i in range(15):
 if (b/'result.json').exists():break
 time.sleep(0.5)
d=json.loads((b/'result.json').read_text());d['pcap_b64']=base64.b64encode((b/'pfsync.pcap').read_bytes()).decode();print(json.dumps(d))
'''
d=json.loads(remote(code,timeout=25));d['collector_time']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
if a.action=='stop':(OUT/'pfsync.pcap').write_bytes(base64.b64decode(d.pop('pcap_b64'),validate=True))
(OUT/('pfsync-capture-'+a.action+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
