"""Phát đúng hai frame ICMP lab và thu bản đến TAP sensor; không cấu hình lại OVS."""
import json,datetime as dt
from topology_remote import remote,ROOT
CODE=r'''
import socket,struct,time,select,pathlib,json,hashlib,xml.etree.ElementTree as E
r=E.parse('/opt/unetlab/labs/SOC-M2-Core-L2.unl').getroot();nodes={n.get('name'):n for n in r.findall('.//node')}
assert nodes['SOC-Core-L2'].get('uuid')=='2b295168-b72e-4de7-b364-37298252dd9f'
assert next(i for i in nodes['SOC-Core-L2'].findall('interface') if i.get('id')=='7').get('network_id')==next(i for i in nodes['Suricata-NIDS'].findall('interface') if i.get('id')=='0').get('network_id')
def csum(data):
 if len(data)%2:data+=b'\0'
 total=sum(struct.unpack('!%dH'%(len(data)//2),data))
 while total>>16:total=(total&65535)+(total>>16)
 return (~total)&65535
def frame(marker,seq):
 icmp=struct.pack('!BBHHH',8,0,0,0x534f,seq)+marker;icmp=icmp[:2]+struct.pack('!H',csum(icmp))+icmp[4:]
 ip=struct.pack('!BBHHHBBH4s4s',0x45,0,20+len(icmp),0x534f,0,64,1,0,socket.inet_aton('192.168.30.101'),socket.inet_aton('192.168.30.102'));ip=ip[:10]+struct.pack('!H',csum(ip))+ip[12:]
 return bytes.fromhex('02534f43123402534f4300000800')+ip+icmp
cases=[('positive',b'SOC-M4-TEST-20261101-RESUME-20261102',1),('negative',b'SOC-M4-NONMATCH-RESUME-20261102',2)]
capture=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3));capture.bind(('vunl0_9_0',0));capture.setblocking(False)
source=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3));source.bind(('vunl0_3_0',0))
out=pathlib.Path('/root/soc-live-mirror-'+str(int(time.time())));out.mkdir(mode=0o700)
observed=[]
with (out/'sensor-input.pcap').open('xb') as f:
 f.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1))
 for name,marker,seq in cases:
  data=frame(marker,seq);sent=source.send(data);end=time.monotonic()+3
  while time.monotonic()<end:
   if not select.select([capture],[],[],0.3)[0]:continue
   packet=capture.recv(65535)
   if marker not in packet:continue
   now=time.time();f.write(struct.pack('<IIII',int(now),int(now%1*1000000),len(packet),len(packet)));f.write(packet)
   vlan=struct.unpack('!H',packet[14:16])[0]&4095 if packet[12:14]==b'\x81\x00' else None
   observed.append({'case':name,'marker':marker.decode(),'bytes_sent':sent,'bytes_received_at_sensor_tap':len(packet),'vlan':vlan})
source.close();capture.close();p=out/'sensor-input.pcap';p.chmod(0o600)
result={'scope':'Host-generated benign ICMP frames injected into real Core guest TAP, mirrored to real sensor TAP; not VPCS ping or gateway routing','source':'vunl0_3_0 / Core ens3 access30','capture':'vunl0_9_0 / sensor capture NIC','observed':observed,'both_frames_reached_sensor':{x['case'] for x in observed}=={'positive','negative'},'pcap_path':str(p),'pcap_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(out/'public.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''
if __name__=='__main__':
 d=json.loads(remote(CODE,timeout=30));d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
 p=ROOT/'docs/evidence/M4/resume-20261102/live-mirror-frames.json';p.write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps(d))
