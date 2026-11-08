"""Chỉ kiểm tra readiness trong Employee mới; không kết nối Internet."""
import pathlib,subprocess,json,ssl,time,datetime,shutil
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=10)
 return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
for attempt in range(30):
 addr=run(['ip','-j','-4','addr','show','employee0']);routes=run(['ip','-j','-4','route','show','default'])
 if '192.168.40.' in addr['stdout'] and '192.168.40.1' in routes['stdout']:break
 time.sleep(2)
paths=ssl.get_default_verify_paths()
d={'hostname':run(['hostname'])['stdout'].strip(),'guest_utc_unverified':datetime.datetime.now(datetime.timezone.utc).isoformat(),'addresses':json.loads(addr['stdout'] or '[]'),'default_routes':json.loads(routes['stdout'] or '[]'),'python_ssl':ssl.OPENSSL_VERSION,'ca_file':paths.cafile,'ca_exists':bool(paths.cafile and pathlib.Path(paths.cafile).is_file()),'curl':run(['curl','--version']) if shutil.which('curl') else None,'ipv4_forward':pathlib.Path('/proc/sys/net/ipv4/ip_forward').read_text().strip(),'scope':'Local IP/route and HTTPS client only; no external requests'}
ips=[x['local'] for n in d['addresses'] for x in n.get('addr_info',[]) if x.get('family')=='inet']
d['ready']=bool(any(s.startswith('192.168.40.') for s in ips) and any(s.get('gateway')=='192.168.40.1' for s in d['default_routes']) and d['ca_exists'] and d['ipv4_forward']=='0')
p=pathlib.Path('/var/lib/soc');p.mkdir(exist_ok=True)
(p/'employee-readiness.json').write_text(json.dumps(d,indent=2))
summary='\n'.join(['EMPLOYEE LINUX READINESS','hostname: '+d['hostname'],'IPv4: '+', '.join(ips),'gateway: '+', '.join(x.get('gateway','') for x in d['default_routes']),'Python TLS: '+d['python_ssl'],'CA bundle: '+str(d['ca_exists']),'curl available: '+str(bool(d['curl'] and d['curl']['rc']==0)),'IPv4 forwarding: '+d['ipv4_forward'],'Ready: '+str(d['ready']),'No HTTPS request sent; WAN unchanged'])+'\n'
(p/'employee-readiness.txt').write_text(summary)
for device in ['/dev/ttyS0','/dev/tty1']:
 try:
  with open(device,'w') as f:f.write(summary+'SOC_EMPLOYEE_READINESS '+json.dumps(d)+'\n' if device.endswith('S0') else summary)
 except OSError:pass
