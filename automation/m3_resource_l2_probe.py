"""ARP probe IP nguồn 0.0.0.0 qua access port hiện hữu; không cấu hình mạng."""
import json
from topology_remote import remote
from m3_resource_optimization import save
CODE=r'''
import socket,struct,time,json,select,pathlib,xml.etree.ElementTree as E
r=E.parse('/opt/unetlab/labs/SOC-M2-Core-L2.unl').getroot()
n=next(n for n in r.findall('.//node') if n.get('name')=='SOC-Core-L2')
assert n.get('uuid')=='2b295168-b72e-4de7-b364-37298252dd9f'
assert [i.get('network_id') for i in n.findall('interface')][:5]==['6','7','8','9','10']
src=bytes.fromhex('02534f430103');rows=[]
for idx,vlan in enumerate([30,40,50,60,99]):
 tap='vunl0_3_'+str(idx);s=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3));s.bind((tap,0));s.setblocking(False)
 targets=['192.168.%d.%d'%(vlan,last) for last in [2,3,1]];seen=[]
 for attempt in range(2):
  for target in targets:
   arp=struct.pack('!HHBBH',1,0x0800,6,4,1)+src+b'\0'*4+b'\0'*6+socket.inet_aton(target)
   s.send(b'\xff'*6+src+b'\x08\x06'+arp)
  end=time.monotonic()+2
  while time.monotonic()<end:
   if not select.select([s],[],[],0.2)[0]:continue
   d=s.recv(65535)
   if len(d)>=42 and d[12:14]==b'\x08\x06' and d[20:22]==b'\0\2':
    ip=socket.inet_ntoa(d[28:32])
    if ip in targets:seen.append({'ip':ip,'mac':d[22:28].hex(':')})
 s.close()
 rows.append({'vlan':vlan,'tap':tap,'probes_per_target':2,'responses':seen,'primary_seen':targets[0] in {x['ip'] for x in seen},'secondary_seen':targets[1] in {x['ip'] for x in seen},'vip_conflict_seen':targets[2] in {x['ip'] for x in seen}})
print(json.dumps({'scope':'ARP observations through existing Core access ports; no guest configuration read; no response is not a guarantee of unused VIP','rows':rows,'configuration_changed':False}))
'''
if __name__=='__main__':print(json.dumps(save('l2-arp-observation',json.loads(remote(CODE,timeout=40)))))
