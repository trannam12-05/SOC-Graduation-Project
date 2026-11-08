"""Capture đúng flow test trên hai trunk; không sửa packet hoặc mạng."""
import hashlib,json,os,pathlib,select,socket,struct,sys,time
os.umask(0o077);out=pathlib.Path(sys.argv[1]);sockets=[];files={};counts={};start=time.monotonic();done_at=None
events=(out/'wire.jsonl').open('x',buffering=1)
for tap in ['vunl0_3_5','vunl0_3_6']:
    s=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3));s.setsockopt(263,8,1);s.bind((tap,0));s.setblocking(False);sockets.append(s)
    f=(out/(tap+'-flow.pcap')).open('xb');f.write(struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1));files[tap]=f;counts[tap]=0
while time.monotonic()-start<900:
    if (out/'client-result.json').exists():
        if done_at is None:done_at=time.monotonic()
        if time.monotonic()-done_at>8:break
    ready,_,_=select.select(sockets,[],[],0.3)
    for s in ready:
        b,aux,_,address=s.recvmsg(65535,1024);tap=s.getsockname()[0];offset=14;vlan=None
        if len(b)<54:continue
        kind=b[12:14]
        if kind==b'\x81\x00':vlan=struct.unpack('!H',b[14:16])[0]&4095;kind=b[16:18];offset=18
        for level,typ,data in aux:
            if level==263 and typ==8 and len(data)>=20:
                st=struct.unpack('I',data[:4])[0]
                if st&16:vlan=struct.unpack('H',data[16:18])[0]&4095
        if kind!=b'\x08\x00' or b[offset+9]!=6:continue
        src=socket.inet_ntoa(b[offset+12:offset+16]);dst=socket.inet_ntoa(b[offset+16:offset+20]);t=offset+(b[offset]&15)*4
        if len(b)<t+20:continue
        sp,dp,seq,ack,bits,win,cs,urg=struct.unpack('!HHIIHHHH',b[t:t+20])
        if not ((src,dst,sp,dp)==('192.168.40.100','192.168.30.10',44341,8000) or (src,dst,sp,dp)==('192.168.30.10','192.168.40.100',8000,44341)):continue
        now=time.time();f=files[tap];f.write(struct.pack('<IIII',int(now),int(now%1*1e6),len(b),len(b)));f.write(b);f.flush();counts[tap]+=1
        row=dict(elapsed=round(time.monotonic()-start,6),host_clock_untrusted=now,tap=tap,vlan=vlan,source=src,destination=dst,source_port=sp,destination_port=dp,seq=seq,ack=ack,flags=bits&511,payload_bytes=struct.unpack('!H',b[offset+2:offset+4])[0]-(t-offset)-(bits>>12)*4,ttl=b[offset+8],source_mac=b[6:12].hex(':'),destination_mac=b[:6].hex(':'),phase=(out/'phase').read_text().strip())
        events.write(json.dumps(row,separators=(',',':'))+'\n')
events.close()
for s in sockets:s.close()
for f in files.values():f.close()
d={'counts':counts,'elapsed_s':round(time.monotonic()-start,3),'pcaps':{tap:{'private_path':str(out/(tap+'-flow.pcap')),'sha256':hashlib.sha256((out/(tap+'-flow.pcap')).read_bytes()).hexdigest()} for tap in files}}
(out/'wire-result.json').write_text(json.dumps(d,indent=2))
