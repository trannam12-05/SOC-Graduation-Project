"""Một HTTPS HEAD duy nhất đến đích đã duyệt, không redirect/proxy/retry."""
import pathlib,subprocess,json,os,ssl,time,hashlib,zlib,struct,base64,sys,datetime
result=pathlib.Path('/var/tmp/soc-m3-https-result.json')
if '--show' not in sys.argv:
 assert not result.exists(),'HTTPS already attempted; do not repeat'
 ip=json.loads(subprocess.run(['ip','-j','-4','addr','show','employee0'],capture_output=True,text=True,check=True).stdout)
 assert any(x.get('local')=='192.168.40.110' for n in ip for x in n.get('addr_info',[])),'Employee source changed'
 sentinel='/var/tmp/soc-m3-https-attempted';fd=os.open(sentinel,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
 fmt=json.dumps({k:'%{'+k+'}' for k in ['local_ip','local_port','remote_ip','remote_port','http_code','ssl_verify_result','time_total']})
 command=['curl','--ipv4','--interface','employee0','--noproxy','*','--proto','=https','--silent','--show-error','--head','--output','/var/tmp/soc-m3-https-headers.txt','--connect-timeout','5','--max-time','12','--retry','0','--write-out',fmt,'https://1.1.1.1/']
 p=subprocess.run(command,capture_output=True,text=True,timeout=16)
 try:metrics=json.loads(p.stdout)
 except Exception:metrics={'parse_error':p.stdout[:200]}
 d={'guest_utc_unverified':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'rc':p.returncode,'metrics':metrics,'stderr':p.stderr[:500],'requests_attempted':1,'redirects_followed':False,'scope':'Employee Linux NAT Internet only; no HA failover or previous PASS retests'}
 d['status']='PASS' if p.returncode==0 and metrics.get('local_ip')=='192.168.40.110' and metrics.get('remote_ip')=='1.1.1.1' and metrics.get('remote_port')=='443' and metrics.get('ssl_verify_result')=='0' and int(metrics.get('http_code','0'))>=100 else 'FAILED'
 result.write_text(json.dumps(d,indent=2))
 summary='\n'.join(['M3 HTTPS ONCE: '+d['status'],'source: '+str(metrics.get('local_ip')),'destination: '+str(metrics.get('remote_ip'))+':'+str(metrics.get('remote_port')),'HTTP status: '+str(metrics.get('http_code')),'TLS verify: '+str(metrics.get('ssl_verify_result')),'curl rc: '+str(p.returncode),'requests: 1; no redirect/proxy/retry'])+'\n'
 pathlib.Path('/var/tmp/soc-m3-https-summary.txt').write_text(summary)
d=json.loads(result.read_text());b=zlib.compress(json.dumps(d,separators=(',',':')).encode(),9);assert len(b)<=924
packet=(struct.pack('>I32s',len(b),hashlib.sha256(b).digest())+b).ljust(960,b'\0');s=base64.b64encode(packet).decode()
print('\x1b[2J\x1b[H'+'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='+'\n'+'\n'.join(s[i:i+80] for i in range(0,len(s),80)))
