"""Cấu hình tối thiểu DC/DMZ mới và thử HTTP cục bộ; chưa nghiệm thu liên VLAN."""
from pathlib import Path
import sys,json,subprocess,urllib.request,time
role=sys.argv[1];assert role in ['Data-Center','DMZ']
vid=30 if role=='Data-Center' else 60;port=8000 if vid==30 else 80
out=Path('/var/lib/soc');out.mkdir(exist_ok=True)
result={'role':role,'scope':'Local OS/IP/service only; routed client path still requires separate test'}
try:
 root=Path('/var/www/soc-lab');root.mkdir(parents=True,exist_ok=True)
 (root/'index.html').write_text('<!doctype html><html lang="vi"><meta charset="utf-8"><title>SOC '+role+'</title><h1>SOC '+role+'</h1><p>Dich vu Web toi thieu trong mo hinh EVE-NG.</p></html>')
 unit='''[Unit]
Description=SOC minimal ROLE HTTP lab service
After=network-online.target
Wants=network-online.target
[Service]
User=www-data
ExecStart=/usr/bin/python3 -m http.server PORT --bind 192.168.VID.10 --directory /var/www/soc-lab
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true
Restart=on-failure
[Install]
WantedBy=multi-user.target
'''.replace('ROLE',role).replace('PORT',str(port)).replace('VID',str(vid))
 Path('/etc/systemd/system/soc-lab-http.service').write_text(unit)
 subprocess.run(['systemctl','daemon-reload'],check=True)
 subprocess.run(['systemctl','enable','--now','soc-lab-http.service'],check=True,capture_output=True)
 time.sleep(2)
 with urllib.request.urlopen('http://192.168.%d.10:%d/'%(vid,port),timeout=5) as r:
  result['local_http_status']=r.status;result['local_http_bytes']=len(r.read())
 result['interfaces']=json.loads(subprocess.run(['ip','-j','address','show','lan0'],text=True,capture_output=True,check=True).stdout)
 result['state']='CONFIGURED_LOCAL_SERVICE_VERIFIED_NOT_END_TO_END'
 result['service_port']=port
except Exception as e:result.update({'state':'FAILED','error':str(e)})
result['boot_id']=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
(out/'result.json').write_text(json.dumps(result,indent=2))
for terminal in ['/dev/ttyS0','/dev/tty1']:
 try:
  with open(terminal,'w') as f:f.write('SOC_BOOTSTRAP_RESULT '+json.dumps(result)+'\n')
 except OSError:pass
