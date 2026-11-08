"""Đọc PCAP đã thu, ghép SYN trước/sau SNAT; không phát gói."""
import pathlib,struct,socket,json,hashlib,sys
work=pathlib.Path(sys.argv[1])
def packets(path):
 data=path.read_bytes();endian='<' if data[:4] in [b'\xd4\xc3\xb2\xa1',b'\x4d\x3c\xb2\xa1'] else '>'
 assert data[:4] in [b'\xd4\xc3\xb2\xa1',b'\xa1\xb2\xc3\xd4',b'\x4d\x3c\xb2\xa1',b'\xa1\xb2\x3c\x4d']
 assert struct.unpack(endian+'I',data[20:24])[0]==1,'Expected Ethernet capture'
 out=[];pos=24
 while pos+16<=len(data):
  sec,usec,size,original=struct.unpack(endian+'IIII',data[pos:pos+16]);pos+=16;frame=data[pos:pos+size];pos+=size
  if len(frame)<34:continue
  offset=14;proto=frame[12:14]
  if proto==b'\x81\x00':proto=frame[16:18];offset=18
  if proto!=b'\x08\x00':continue
  ip=frame[offset:];ihl=(ip[0]&15)*4
  if ip[9]!=6 or len(ip)<ihl+20:continue
  tcp=ip[ihl:];sport,dport,seq,ack=struct.unpack('>HHII',tcp[:12])
  out.append({'sec':sec,'fraction':usec,'source':socket.inet_ntoa(ip[12:16]),'destination':socket.inet_ntoa(ip[16:20]),'source_port':sport,'destination_port':dport,'seq':seq,'ack':ack,'flags':tcp[13]})
 return out
employee=packets(work/'employee.pcap');wan=packets(work/'wan.pcap');state=json.loads((work/'state.json').read_text());expected=state['history'][-1]['guards']['OPNsense-Primary']['wan'][0][0]
syn=lambda x:x['flags']&2 and not x['flags']&16 and x['destination']=='1.1.1.1' and x['destination_port']==443
pairs=[{'before':a,'after':b} for a in employee if syn(a) and a['source']=='192.168.40.110' for b in wan if syn(b) and b['source']==expected and a['seq']==b['seq']]
result={'nat_translation_proved':bool(pairs),'expected_wan_ip_from_dhcp_guard':expected,'matched_syn_pairs':pairs,'employee_packets':len(employee),'wan_packets':len(wan),'sha256':{name:hashlib.sha256((work/name).read_bytes()).hexdigest() for name in ['employee.pcap','wan.pcap']},'scope':'Passive capture of exactly the one approved HTTPS attempt; no extra traffic or failover test'}
(work/'nat-pcap-analysis.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
