"""Tạo seed riêng cho Linux node mới; không sửa seed/image Core/Primary."""
import base64,json,datetime as dt
from topology_remote import remote,ROOT

payload={
 'bootstrap':base64.b64encode((ROOT/'automation/sensor_bootstrap.py').read_bytes()).decode(),
 'rules':base64.b64encode((ROOT/'suricata/soc-lab.rules').read_bytes()).decode(),
}
CODE=r'''
import json,pathlib,subprocess,xml.etree.ElementTree as E,base64,uuid,os,hashlib
payload=json.loads(base64.b64decode('__PAYLOAD__'))
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');r=E.parse(lab).getroot()
root=pathlib.Path('/root/soc-linux-seeds-20261102');root.mkdir(mode=0o700,exist_ok=True)
public=pathlib.Path('/root/.ssh/authorized_keys').read_text().splitlines()
public=[line for line in public if line.startswith('ssh-ed25519 ')]
assert len(public)==1
results=[]
for n in r.findall('.//node'):
 name=n.get('name')
 if name not in ['Data-Center','DMZ','Suricata-NIDS','Wazuh-SOC']:continue
 seed=root/name;assert not seed.exists(),'Refuse overwrite seed';seed.mkdir(mode=0o700)
 config={'hostname':name.lower(),'preserve_hostname':False,'disable_root':True,'ssh_pwauth':False,
 'users':[{'name':'soc-admin','shell':'/bin/bash','groups':['adm','sudo'],'lock_passwd':True,'sudo':['ALL=(ALL) NOPASSWD:ALL'],'ssh_authorized_keys':public}],
 'package_update':False,'package_upgrade':False,
 'write_files':[{'path':'/etc/systemd/system/getty@tty1.service.d/soc-console.conf','content':'[Service]\nExecStart=\nExecStart=-/sbin/agetty --autologin soc-admin --noclear %I $TERM\n'}],
 'runcmd':[['systemctl','daemon-reload'],['systemctl','restart','getty@tty1.service']]}
 if name=='Suricata-NIDS':
  config['write_files'].append({'path':'/opt/soc/sensor_bootstrap.py','encoding':'b64','content':payload['bootstrap'],'permissions':'0700'})
  config['runcmd'].append(['python3','/opt/soc/sensor_bootstrap.py'])
  os.link('/opt/unetlab/soc-suricata-preparation-20261102/suricata-offline.tar',seed/'suricata-offline.tar')
  (seed/'soc-lab.rules').write_bytes(base64.b64decode(payload['rules']))
 else:
  # OS seulement: l'application métier DC/DMZ et Wazuh attend leur spécification.
  command="import json,pathlib,platform;d={'state':'OS_BOOTED_SERVICE_NOT_INSTALLED','role':"+repr(name)+",'os':platform.platform(),'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()};pathlib.Path('/var/lib/soc').mkdir(exist_ok=True);pathlib.Path('/var/lib/soc/result.json').write_text(json.dumps(d));print('SOC_BOOTSTRAP_RESULT '+json.dumps(d),file=open('/dev/ttyS0','w'))"
  config['runcmd'].append(['python3','-c',command])
 network={'version':2,'ethernets':{}}
 for idx in range(int(n.get('ethernet'))):
  value=int(n.get('firstmac').replace(':',''),16)+idx
  mac=':'.join(f'{value:012x}'[j:j+2] for j in range(0,12,2))
  iface=('capture0' if idx==0 else 'mgmt0') if name=='Suricata-NIDS' else 'lan0'
  network['ethernets'][iface]={'match':{'macaddress':mac},'set-name':iface,'dhcp4':False,'dhcp6':False,'accept-ra':False,'link-local':[],'optional':True}
 (seed/'user-data').write_text('#cloud-config\n'+json.dumps(config))
 (seed/'network-config').write_text(json.dumps(network))
 (seed/'meta-data').write_text(json.dumps({'instance-id':'iid-'+name.lower()+'-'+str(uuid.uuid4()),'local-hostname':name.lower()}))
 image=pathlib.Path('/opt/unetlab/addons/qemu')/n.get('image');iso=image/'cdrom.iso';assert not iso.exists()
 subprocess.run(['genisoimage','-quiet','-volid','cidata','-joliet','-rock','-o',str(iso),str(seed)],check=True,capture_output=True)
 os.chmod(iso,0o600)
 results.append({'node':name,'seed_path':str(iso),'sha256':hashlib.sha256(iso.read_bytes()).hexdigest(),'bytes':iso.stat().st_size,'network':network,'state':'SEED_PREPARED_NOT_BOOTED','console':'soc-admin autologin on isolated EVE console; SSH key only, password locked'})
print(json.dumps(results))
'''
if __name__=='__main__':
 rows=json.loads(remote(CODE.replace('__PAYLOAD__',base64.b64encode(json.dumps(payload).encode()).decode()),timeout=120))
 out=ROOT/'docs/evidence/M4/topology-first-20261102'
 (out/'linux-seed-preparation.json').write_text(json.dumps({'collected_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'nodes':rows},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'seeds':len(rows),'state':'PREPARED_NOT_BOOTED'}))
