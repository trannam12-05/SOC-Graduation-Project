"""Một TCP/HTTP client thật qua access TAP sẵn có, không gán IP/interface host.

Chỉ một handshake và một HTTP request lab; giữ header mở trong lúc đọc state,
sau đó hoàn tất request khi nhận cờ finish-request. Không tự reconnect.
"""
import hashlib,json,os,pathlib,random,select,socket,struct,sys,time

os.umask(0o077)
OUT=pathlib.Path(sys.argv[1]);OUT.mkdir(mode=0o700,exist_ok=True)
SRC='192.168.40.100';DST='192.168.30.10';GATEWAY='192.168.40.1'
SPORT=44340;DPORT=8000;MAC=bytes.fromhex('02534f430434');TAP='vunl0_3_1'
sock=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3));sock.setsockopt(263,8,1);sock.bind((TAP,0));sock.setblocking(False)
start=time.monotonic();log=(OUT/'client-events.jsonl').open('x',buffering=1)
pcap=(OUT/'client.pcap').open('xb');pcap.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1))
phase='before';isn=random.randrange(10000000,1000000000);snd_next=isn;snd_una=isn;rcv_next=None
gw_mac=None;server_isn=None;pending=[];response=b'';steps=[];syn_count=0;retransmits=0;tcp_packets=0;ip_id=100
state='INITIAL';last_step=0;finish_sent=False;server_fin=False;failure=None

def phase_now():
    p=OUT/'phase'
    return p.read_text().strip() if p.exists() else 'before'
def event(kind,**kw):
    row=dict(event=kind,elapsed=round(time.monotonic()-start,6),host_wall_clock_untrusted=time.time(),phase=phase_now(),**kw)
    log.write(json.dumps(row,separators=(',',':'))+'\n')
def record(frame):
    now=time.time();pcap.write(struct.pack('<IIII',int(now),int(now%1*1e6),len(frame),len(frame)));pcap.write(frame);pcap.flush()
def csum(b):
    if len(b)%2:b+=b'\0'
    s=sum(struct.unpack('!%dH'%(len(b)//2),b))
    while s>>16:s=(s&65535)+(s>>16)
    return (~s)&65535
def summary():
    return dict(state=state,flow=dict(source=SRC,source_port=SPORT,destination=DST,destination_port=DPORT),gateway=GATEWAY,gateway_mac=gw_mac.hex(':') if gw_mac else None,client_isn=isn,server_isn=server_isn,syn_transmissions=syn_count,retransmissions=retransmits,never_reconnects=True,phase=phase_now(),snd_una=snd_una,snd_next=snd_next,rcv_next=rcv_next,steps=steps,response_bytes=len(response),http_status_line=response.split(b'\r\n')[0].decode(errors='replace') if response else None,elapsed=round(time.monotonic()-start,3),failure=failure)
def save_live():
    temp=OUT/'live.pending';temp.write_text(json.dumps(summary(),indent=2));os.replace(temp,OUT/'live.json')
def emit(flags,payload=b'',seq=None,retry=False):
    global snd_next,syn_count,ip_id,tcp_packets
    seq=snd_next if seq is None else seq;ack=rcv_next or 0
    header=struct.pack('!HHIIHHHH',SPORT,DPORT,seq,ack,(5<<12)|flags,32768,0,0)
    pseudo=socket.inet_aton(SRC)+socket.inet_aton(DST)+struct.pack('!BBH',0,6,len(header)+len(payload))
    checksum=csum(pseudo+header+payload);header=header[:16]+struct.pack('!H',checksum)+header[18:]
    assert csum(pseudo+header+payload)==0
    ip=struct.pack('!BBHHHBBH4s4s',0x45,0,20+len(header)+len(payload),ip_id,0x4000,64,6,0,socket.inet_aton(SRC),socket.inet_aton(DST));ip_id=(ip_id+1)%65536
    ip=ip[:10]+struct.pack('!H',csum(ip))+ip[12:]
    frame=gw_mac+MAC+b'\x08\x00'+ip+header+payload;sock.send(frame);record(frame);tcp_packets+=1
    event('tcp_send',seq=seq,ack=ack,flags=flags,bytes=len(payload),retry=retry,payload_sha256=hashlib.sha256(payload).hexdigest() if payload else None)
    if flags&2:syn_count+=1
    if not retry and (payload or flags&3):
        end=seq+len(payload)+(1 if flags&2 else 0)+(1 if flags&1 else 0)
        pending.append(dict(seq=seq,end=end,flags=flags,payload=payload,last=time.monotonic(),attempts=1));snd_next=end
    return seq+len(payload)
def arp_request(target):
    payload=struct.pack('!HHBBH',1,0x0800,6,4,1)+MAC+b'\0'*4+b'\0'*6+socket.inet_aton(target)
    frame=b'\xff'*6+MAC+b'\x08\x06'+payload;sock.send(frame);record(frame)
def receive(timeout):
    if not select.select([sock],[],[],timeout)[0]:return
    global gw_mac,rcv_next,server_isn,state,snd_una,response,server_fin,tcp_packets
    frame,ancillary,msgflags,address=sock.recvmsg(65535,1024)
    offload=any(level==263 and kind==8 and len(data)>=4 and struct.unpack('I',data[:4])[0]&8 for level,kind,data in ancillary)
    if len(frame)>=42 and frame[12:14]==b'\x08\x06':
        op=struct.unpack('!H',frame[20:22])[0];sip=socket.inet_ntoa(frame[28:32]);tip=socket.inet_ntoa(frame[38:42])
        if op==2 and sip==GATEWAY:
            gw_mac=frame[22:28];event('gateway_arp',mac=gw_mac.hex(':'));record(frame)
        if op==2 and sip==SRC and frame[22:28]!=MAC:raise RuntimeError('Source IP already answers ARP; do not claim this address')
        if op==1 and tip==SRC and state!='PROBING':
            answer=frame[22:28]+MAC+b'\x08\x06'+struct.pack('!HHBBH',1,0x0800,6,4,2)+MAC+socket.inet_aton(SRC)+frame[22:28]+frame[28:32]
            sock.send(answer);record(frame);record(answer);event('client_arp_reply',target=sip)
        return
    if len(frame)<54 or frame[12:14]!=b'\x08\x00' or frame[23]!=6:return
    ihl=(frame[14]&15)*4
    if socket.inet_ntoa(frame[26:30])!=DST or socket.inet_ntoa(frame[30:34])!=SRC:return
    offset=14+ihl;sp,dp,seq,ack,bits,win,checksum,urg=struct.unpack('!HHIIHHHH',frame[offset:offset+20])
    if sp!=DPORT or dp!=SPORT:return
    plen=struct.unpack('!H',frame[16:18])[0]-ihl;tcp=frame[offset:offset+plen]
    pseudo=socket.inet_aton(DST)+socket.inet_aton(SRC)+struct.pack('!BBH',0,6,len(tcp))
    if csum(pseudo+tcp)!=0 and not offload:raise RuntimeError('Invalid TCP checksum received without offload metadata')
    flags=bits&511;data=tcp[(bits>>12)*4:];record(frame);tcp_packets+=1
    event('tcp_receive',seq=seq,ack=ack,flags=flags,bytes=len(data),ttl=frame[22],checksum_offload_pending=offload)
    if flags&4:raise RuntimeError('TCP reset received; original connection did not survive')
    if flags&2:
        if not flags&16 or ack!=isn+1:raise RuntimeError('Unexpected SYNACK')
        if server_isn is None:server_isn=seq;rcv_next=seq+1
        elif server_isn!=seq:raise RuntimeError('Server ISN changed')
        if state=='SYN_SENT':state='ESTABLISHED';event('established',server_isn=server_isn)
        emit(16)
    if flags&16:
        if ack>snd_next:raise RuntimeError('ACK beyond sent data')
        snd_una=max(snd_una,ack)
        pending[:]=[p for p in pending if p['end']>snd_una]
        for item in steps:
            if item['end']<=snd_una and not item.get('acked'):
                item.update(acked=True,ack_elapsed=round(time.monotonic()-start,6),ack_phase=phase_now());event('step_acked',step=item['step'],end=item['end'])
    if data:
        if seq==rcv_next:response+=data;rcv_next+=len(data)
        elif seq<rcv_next:
            extra=data[max(0,rcv_next-seq):]
            if extra:response+=extra;rcv_next+=len(extra)
        else:event('out_of_order',expected=rcv_next,received=seq)
        emit(16)
    if flags&1:
        if seq+len(data)==rcv_next:rcv_next+=1;server_fin=True
        emit(16)

try:
    state='PROBING';event('source_conflict_probe',source=SRC)
    for attempt in range(2):
        arp_request(SRC);until=time.monotonic()+1
        while time.monotonic()<until:receive(0.1)
    state='ARP_GATEWAY'
    for attempt in range(5):
        arp_request(GATEWAY);until=time.monotonic()+1
        while time.monotonic()<until:receive(0.1)
        if gw_mac:break
    assert gw_mac==bytes.fromhex('00005e000128'),'Missing expected VLAN40 CARP virtual MAC'
    state='SYN_SENT';emit(2)
    while time.monotonic()-start<900:
        receive(0.1);now=time.monotonic()
        if state=='ESTABLISHED' and not steps:
            payload=b'GET /?soc_m34=state-failover HTTP/1.0\r\nHost: 192.168.30.10\r\nX-SOC-M34: single-benign-request\r\n'
            end=emit(24,payload);steps.append(dict(step='request-headers',phase=phase_now(),end=end,acked=False));last_step=now
        if state=='ESTABLISHED' and steps and not pending and not finish_sent:
            if (OUT/'finish-request').exists():
                end=emit(24,b'\r\n');steps.append(dict(step='request-complete',phase=phase_now(),end=end,acked=False));finish_sent=True
            elif now-last_step>=10:
                assert len(steps)<80,'Header count guard; never overload server'
                n=len(steps);payload=('X-SOC-Step-%d: benign\r\n'%n).encode();end=emit(24,payload)
                steps.append(dict(step=n,phase=phase_now(),end=end,acked=False));last_step=now
        for item in list(pending):
            if now-item['last']>=2:
                assert item['attempts']<16,'Unacknowledged TCP data timed out; no reconnect'
                emit(item['flags'],item['payload'],item['seq'],True);item['last']=now;item['attempts']+=1;retransmits+=1
        save_live()
        if server_fin:
            if not response.startswith(b'HTTP/1.0 200 '):raise RuntimeError('Expected HTTP 200 from existing DC service')
            assert b'SOC Data-Center' in response,'Unexpected HTTP body'
            state='COMPLETED';event('http_completed',bytes=len(response),response_sha256=hashlib.sha256(response).hexdigest())
            emit(17);deadline=time.monotonic()+3
            while time.monotonic()<deadline and pending:receive(0.1)
            break
    else:raise RuntimeError('Client deadline exceeded; never reconnect')
except Exception as exc:
    failure=type(exc).__name__+': '+str(exc);state='FAILED';event('failed',reason=failure)
finally:
    save_live();pcap.close();log.close();sock.close()
    result=summary();result['pcap_private_path']=str(OUT/'client.pcap');result['pcap_sha256']=hashlib.sha256((OUT/'client.pcap').read_bytes()).hexdigest();result['response_sha256']=hashlib.sha256(response).hexdigest()
    (OUT/'client-result.json').write_text(json.dumps(result,indent=2))
