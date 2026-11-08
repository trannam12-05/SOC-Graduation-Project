"""Phân tích PCAP nguyên bản của một session; không tạo traffic mới."""
import collections,hashlib,json,struct,datetime as dt
from pathlib import Path
P=Path(__file__).parent
r=json.loads((P/'artifacts/client-result.json').read_text())
b=(P/'artifacts/client.pcap').read_bytes();assert b[:4]==b'\xd4\xc3\xb2\xa1';offset=24;packets=[]
while offset<len(b):
    assert offset+16<=len(b),'Truncated PCAP record header'
    sec,usec,n,original=struct.unpack('<IIII',b[offset:offset+16]);offset+=16
    assert offset+n<=len(b),'Truncated PCAP frame'
    f=b[offset:offset+n];offset+=n
    if len(f)<54 or f[12:14]!=b'\x08\x00' or f[23]!=6:continue
    ihl=(f[14]&15)*4;t=14+ihl;sp,dp,seq,ack,bits,win,cs,urg=struct.unpack('!HHIIHHHH',f[t:t+20]);length=struct.unpack('!H',f[16:18])[0]
    src='.'.join(str(x) for x in f[26:30]);dst='.'.join(str(x) for x in f[30:34]);data=f[t+(bits>>12)*4:14+length]
    packets.append(dict(source=src,destination=dst,sport=sp,dport=dp,seq=seq,ack=ack,flags=bits&511,payload=data))
outbound=[p for p in packets if p['source']=='192.168.40.100' and p['sport']==44341]
incoming=[p for p in packets if p['source']=='192.168.30.10' and p['sport']==8000]
assert sum(bool(p['flags']&2) for p in outbound)==1
assert sum(p['payload'].startswith(b'GET ') for p in outbound)==1,'More than one HTTP request'
assert not any(p['flags']&4 for p in packets),'TCP RST observed'
segments=sorted((p['seq'],p['payload']) for p in incoming if p['payload']);expected=r['server_isn']+1;response=b''
for seq,data in segments:
    if seq>expected:raise RuntimeError('Gap in captured server response')
    extra=data[max(0,expected-seq):];response+=extra;expected+=len(extra)
assert len(response)==r['response_bytes'] and hashlib.sha256(response).hexdigest()==r['response_sha256']
assert response.startswith(b'HTTP/1.0 200 OK\r\n') and b'SOC Data-Center' in response
counts=collections.Counter((p['source'],p['sport'],p['seq'],hashlib.sha256(p['payload']).hexdigest()) for p in packets if p['payload'])
duplicates=sum(n-1 for n in counts.values() if n>1)
wire=[json.loads(l) for l in (P/'artifacts/wire.jsonl').read_text().splitlines()]
def pair(tap,phases,mac):
    rows=[p for p in wire if p['tap']==tap and p['phase'] in phases and p['source']=='192.168.40.100' and p['payload_bytes']>0]
    for a in rows:
        if a['vlan']!=40 or a['ttl']!=64:continue
        for b in rows:
            if b['vlan']==30 and b['ttl']==63 and b['source_mac']==mac and all(a[k]==b[k] for k in ['seq','ack','flags','payload_bytes']):return {'ingress':a,'egress':b}
    raise RuntimeError('Missing real routed packet pair')
d={'status':'PASS','collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'pcap_complete_no_truncated_records':True,'tcp_packets_at_client':len(packets),'client_syn_packets':1,'http_requests_observed':1,'tcp_rst_observed':0,'response_bytes':len(response),'response_sha256':hashlib.sha256(response).hexdigest(),'response_reassembled_from_pcap':True,'duplicate_tcp_payload_segments_observed_at_client':duplicates,'client_retry_counter':r['retransmissions'],'packet_loss':'Not measured; duplicate/retry observations do not establish zero loss','routed_before':pair('vunl0_3_5',{'before'},'50:00:00:01:00:00'),'routed_after':pair('vunl0_3_6',{'primary-off','secondary-master'},'50:00:00:02:00:00')}
(P/'packet-analysis.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in d.items() if not k.startswith('routed_')}))
