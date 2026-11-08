"""Phân tích PCAP thật bằng thư viện chuẩn; kiểm tra MAC/VLAN/TTL và đường deny."""
from pathlib import Path
import collections,csv,datetime,hashlib,json,socket,struct
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/evidence/M2/final-acceptance-20261103'
def parse(p):
 raw=p.read_bytes();magic=raw[:4]
 endian='<' if magic in [b'\xd4\xc3\xb2\xa1',b'\x4d\x3c\xb2\xa1'] else '>'
 assert magic in [b'\xd4\xc3\xb2\xa1',b'\xa1\xb2\xc3\xd4',b'\x4d\x3c\xb2\xa1',b'\xa1\xb2\x3c\x4d']
 assert struct.unpack(endian+'I',raw[20:24])[0]==1,'Ethernet PCAP required'
 pos=24;rows=[]
 while pos+16<=len(raw):
  sec,frac,n,orig=struct.unpack(endian+'IIII',raw[pos:pos+16]);pos+=16
  f=raw[pos:pos+n];pos+=n
  if len(f)<34:continue
  et=struct.unpack('!H',f[12:14])[0];off=14;tags=[]
  while et in [0x8100,0x88a8]:
   t,et=struct.unpack('!HH',f[off:off+4]);tags.append(t&4095);off+=4
  if et!=0x0800 or len(f)<off+20:continue
  h=f[off:];ihl=(h[0]&15)*4;total=struct.unpack('!H',h[2:4])[0]
  if h[9]!=6 or len(h)<ihl+20:continue
  tcp=h[ihl:];sp,dp,seq,ack=struct.unpack('!HHII',tcp[:12]);th=(tcp[12]>>4)*4
  data=tcp[th:total-ihl]
  row={'capture':p.stem,'ordinal':len(rows)+1,'timestamp_raw_untrusted':str(sec)+'.'+str(frac),'vlan':tags,
       'eth_src':':'.join(f'{v:02x}' for v in f[6:12]),'eth_dst':':'.join(f'{v:02x}' for v in f[:6]),
       'src':socket.inet_ntoa(h[12:16]),'dst':socket.inet_ntoa(h[16:20]),'sport':sp,'dport':dp,
       'ttl':h[8],'ip_id':struct.unpack('!H',h[4:6])[0],'seq':seq,'ack':ack,'flags':tcp[13],
       'payload_bytes':len(data),'payload_sha256':hashlib.sha256(data).hexdigest(),'payload_text':data.decode(errors='replace')[:1000]}
  if sp in [8000,8001] or dp in [8000,8001]:rows.append(row)
 return rows
caps={n:parse(OUT/(n+'.pcap')) for n in ['dc30','client40','primary_trunk','span']}
allrows=[x for a in caps.values() for x in a]
def flow(row,src,dst,port):return row['src']==src and row['dst']==dst and row['dport']==port
trunk=caps['primary_trunk']
syn40=[x for x in trunk if flow(x,'192.168.40.100','192.168.30.10',8000) and x['flags']&2 and not x['flags']&16 and x['vlan']==[40]]
syn30=[x for x in trunk if flow(x,'192.168.40.100','192.168.30.10',8000) and x['flags']&2 and not x['flags']&16 and x['vlan']==[30]]
pairs=[{'before':a,'after':b} for a in syn40 for b in syn30 if a['seq']==b['seq'] and a['sport']==b['sport'] and a['ip_id']==b['ip_id'] and a['ttl']==b['ttl']+1 and a['eth_dst']==b['eth_src']=='50:00:00:01:00:00']
wrong_in=[x for x in trunk if flow(x,'192.168.40.101','192.168.30.10',8000) and x['vlan']==[40] and x['flags']&2]
wrong_out=[x for x in trunk if flow(x,'192.168.40.101','192.168.30.10',8000) and x['vlan']==[30]]
reverse_in=[x for x in trunk if flow(x,'192.168.30.10','192.168.40.100',8001) and x['vlan']==[30] and x['flags']&2]
reverse_out=[x for x in trunk if flow(x,'192.168.30.10','192.168.40.100',8001) and x['vlan']==[40]]
gets=[x for x in caps['dc30'] if 'GET /?soc_m2=soc-m2-final-20261103 HTTP/1.1' in x['payload_text']]
http=[x for x in caps['client40'] if 'HTTP/1.0 200 OK' in x['payload_text'] or 'HTTP/1.1 200 OK' in x['payload_text']]
spanmatch=[x for x in caps['span'] if 'soc_m2=soc-m2-final-20261103' in x['payload_text']]
pub=json.loads((OUT/'packet-collect-result.json').read_text(encoding='utf-8'))['results'][-1]
cases={x['name']:x for x in pub['cases']}
results={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
 'capture_counts':{k:len(v) for k,v in caps.items()},'routing_pairs':pairs,
 'positive_http':{'GET_seen_server':len(gets),'HTTP200_seen_client':len(http),'guest_case':cases.get('positive40_to30')},
 'negative_wrong_source':{'SYN_ingress40':len(wrong_in),'egress30':len(wrong_out),'guest_case':cases.get('negative_wrong_source')},
 'negative_reverse':{'SYN_ingress30':len(reverse_in),'egress40':len(reverse_out),'guest_case':cases.get('negative_reverse_new_flow')},
 'span_marker_packets':len(spanmatch),'access_client_untagged':bool(caps['client40']) and all(not x['vlan'] for x in caps['client40']),
 'access_server_untagged':bool(caps['dc30']) and all(not x['vlan'] for x in caps['dc30'])}
results['Inter_VLAN_PASS']=bool(pairs and gets and http and cases['positive40_to30']['pass'])
results['ACL_negative_PASS']=bool(wrong_in and not wrong_out and reverse_in and not reverse_out and cases['negative_wrong_source']['client_result_only'] and cases['negative_reverse_new_flow']['client_result_only'])
results['SPAN_PASS']=bool(spanmatch)
results['access_trunk_live_PASS']=bool(results['access_client_untagged'] and results['access_server_untagged'] and pairs)
(OUT/'packet-analysis.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'packets-decoded.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
print(json.dumps({k:v for k,v in results.items() if k not in ['routing_pairs','positive_http','negative_wrong_source','negative_reverse']},ensure_ascii=False))
