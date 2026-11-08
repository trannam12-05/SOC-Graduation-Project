"""Chạy trong guest Suricata mới qua cloud-init; cài offline và lưu kết quả thật."""
from pathlib import Path
import subprocess,json,hashlib,tarfile,glob,os,time,traceback

OUT=Path('/var/lib/soc');OUT.mkdir(exist_ok=True)
RESULT={'role':'Suricata-NIDS','state':'INSTALLING','checks':{}}
def run(args,timeout=180):
 p=subprocess.run(args,text=True,capture_output=True,timeout=timeout,env={**os.environ,'DEBIAN_FRONTEND':'noninteractive'})
 with (OUT/'bootstrap.log').open('a') as f:f.write('$ '+' '.join(args)+'\n'+p.stdout+p.stderr+'\nexit='+str(p.returncode)+'\n')
 if p.returncode:raise RuntimeError('Command failed: '+args[0]+' (exit '+str(p.returncode)+')')
 return p.stdout

def publish():
 (OUT/'result.json').write_text(json.dumps(RESULT,indent=2))
 message='SOC_BOOTSTRAP_RESULT '+json.dumps(RESULT)+'\n'
 for terminal in ['/dev/ttyS0','/dev/tty1']:
  try:
   with open(terminal,'w') as f:f.write(message)
  except OSError:pass

try:
 seed=Path('/mnt/soc-seed');seed.mkdir(exist_ok=True)
 if not os.path.ismount(seed):run(['mount','-o','ro','LABEL=cidata',str(seed)])
 bundle=seed/'suricata-offline.tar';destination=Path('/opt/soc-offline');destination.mkdir(exist_ok=True)
 with tarfile.open(bundle) as t:
  for member in t.getmembers():
   target=(destination/member.name).resolve()
   if not target.is_relative_to(destination) or not member.isfile():raise RuntimeError('Unsafe bundle member')
   target.parent.mkdir(parents=True,exist_ok=True)
   with t.extractfile(member) as src,target.open('wb') as dst:dst.write(src.read())
 manifest=json.loads((destination/'manifest.json').read_text())
 for p in manifest:
  if hashlib.sha256((destination/p['path']).read_bytes()).hexdigest()!=p['sha256']:raise RuntimeError('Package digest mismatch')
 RESULT['checks']['package_sha256']=len(manifest)
 # Ngăn package tự khởi động sensor trên interface mặc định sai.
 policy=Path('/usr/sbin/policy-rc.d');assert not policy.exists()
 policy.write_text('#!/bin/sh\nexit 101\n');policy.chmod(0o755)
 (OUT/'empty-lists/partial').mkdir(parents=True,exist_ok=True)
 try:run(['apt-get','-y','-o','Dir::Etc::sourcelist=/dev/null','-o','Dir::Etc::sourceparts=-','-o','Dir::State::lists=/var/lib/soc/empty-lists','--no-install-recommends','--no-remove','install',*sorted(glob.glob(str(destination/'pool/**/*.deb'),recursive=True))],timeout=480)
 finally:policy.unlink()
 Path('/etc/suricata/rules').mkdir(exist_ok=True)
 Path('/etc/suricata/rules/soc-lab.rules').write_bytes((seed/'soc-lab.rules').read_bytes())
 test=run(['/usr/bin/suricata','-T','-c','/etc/suricata/suricata.yaml','-S','/etc/suricata/rules/soc-lab.rules'])
 RESULT['checks']['suricata_configuration_test']='PASS'
 RESULT['suricata_version']=run(['/usr/bin/suricata','-V']).strip()
 run(['ip','link','set','capture0','up'])
 run(['systemctl','disable','suricata.service'])
 unit='''[Unit]
Description=SOC Suricata IDS on dedicated mirror capture port
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/suricata --pcap=capture0 --runmode=single -c /etc/suricata/suricata.yaml -S /etc/suricata/rules/soc-lab.rules -l /var/log/suricata
Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
'''
 Path('/etc/systemd/system/soc-suricata.service').write_text(unit)
 run(['systemctl','daemon-reload']);run(['systemctl','enable','--now','soc-suricata.service']);time.sleep(3)
 RESULT['checks']['service_active']=run(['systemctl','is-active','soc-suricata.service']).strip()
 interfaces=json.loads(run(['ip','-j','address','show']))
 RESULT['interfaces']=[{'name':i['ifname'],'mac':i.get('address'),'addresses':i.get('addr_info',[])} for i in interfaces if i['ifname']!='lo']
 assert all(not i['addresses'] for i in RESULT['interfaces']),'Unexpected IP on capture or unconfigured management'
 RESULT['checks']['capture_no_ip']='PASS'
 RESULT['state']='CONFIGURED_NOT_TRAFFIC_VERIFIED'
 RESULT['boot_id']=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
except Exception as e:
 RESULT['state']='FAILED';RESULT['error']=str(e)
 with (OUT/'bootstrap.log').open('a') as f:f.write(traceback.format_exc())
finally:publish()
