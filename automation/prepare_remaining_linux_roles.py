"""Seed mới chỉ cho node chưa từng boot: DC, DMZ và Wazuh manager-only."""
import json,base64,datetime as dt
from topology_remote import remote,ROOT
alert=ROOT/'docs/evidence/M4/resume-20261102/suricata-real-alert-replay.jsonl'
event=json.loads(alert.read_text());assert event['alert']['signature_id']==1000001 and event['pkt_src']=='wire/pcap'
payload={'role_code':base64.b64encode((ROOT/'automation/linux_role_bootstrap.py').read_bytes()).decode(),
 'manager_code':base64.b64encode((ROOT/'automation/wazuh_manager_bootstrap.py').read_bytes()).decode(),
 'alert':base64.b64encode(alert.read_bytes()).decode()}
CODE=r'''
import pathlib,json,xml.etree.ElementTree as E,base64,shutil,subprocess,uuid,hashlib,os
data=json.loads(base64.b64decode('__PAYLOAD__'));r=E.parse('/opt/unetlab/labs/SOC-M2-Core-L2.unl').getroot()
base=pathlib.Path('/root/soc-linux-seeds-20261102');work=pathlib.Path('/root/soc-service-seeds-20261102');assert not work.exists();work.mkdir(mode=0o700)
rows=[]
for n in r.findall('.//node'):
 name=n.get('name')
 if name not in ['Data-Center','DMZ','Wazuh-SOC']:continue
 runtime=pathlib.Path('/opt/unetlab/tmp/0')/r.get('id')/n.get('id')
 assert not (runtime/'virtioa.qcow2').exists(),'Node already booted: inspect instead of replacing seed'
 old=base/name;seed=work/name;seed.mkdir(mode=0o700)
 conf=json.loads((old/'user-data').read_text().split('\n',1)[1]);net=json.loads((old/'network-config').read_text())
 conf['runcmd']=[x for x in conf['runcmd'] if x[0]!='python3']
 script='wazuh_manager_bootstrap.py' if name=='Wazuh-SOC' else 'linux_role_bootstrap.py'
 conf['write_files'].append({'path':'/opt/soc/'+script,'encoding':'b64','content':data['manager_code' if name=='Wazuh-SOC' else 'role_code'],'permissions':'0700'})
 conf['runcmd'].append(['python3','/opt/soc/'+script]+([] if name=='Wazuh-SOC' else [name]))
 if name=='Wazuh-SOC':
  package=pathlib.Path('/opt/unetlab/soc-wazuh-preparation-20261102/wazuh-manager_4.14.9-1_amd64.deb')
  os.link(package,seed/package.name);(seed/'suricata-real-alert-replay.jsonl').write_bytes(base64.b64decode(data['alert']))
 else:
  vid=30 if name=='Data-Center' else 60
  for iface in net['ethernets'].values():iface['addresses']=['192.168.%d.10/24'%vid];iface['routes']=[{'to':'0.0.0.0/0','via':'192.168.%d.2'%vid}]
 for file,content in [('user-data','#cloud-config\n'+json.dumps(conf)),('network-config',json.dumps(net)),('meta-data',json.dumps({'instance-id':'iid-'+name.lower()+'-service-'+str(uuid.uuid4()),'local-hostname':name.lower()}))]:
  (seed/file).write_text(content);(seed/file).chmod(0o600)
 image=pathlib.Path('/opt/unetlab/addons/qemu')/n.get('image');iso=image/'cdrom.iso'
 shutil.copy2(iso,seed/'previous-seed.iso')
 new=image/'cdrom.soc-new.iso';assert not new.exists()
 # Không đưa bản ISO cũ vào seed mới; giữ backup cạnh thư mục seed.
 backup=work/(name+'-previous-seed.iso');(seed/'previous-seed.iso').rename(backup)
 subprocess.run(['genisoimage','-quiet','-volid','cidata','-joliet','-rock','-o',str(new),str(seed)],capture_output=True,check=True)
 new.chmod(0o600);os.replace(new,iso)
 h=hashlib.sha256()
 with iso.open('rb') as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
 rows.append({'node':name,'seed_sha256':h.hexdigest(),'seed_bytes':iso.stat().st_size,'previous_seed_backup':str(backup),'network':net,'state':'PREPARED_NOT_BOOTED'})
print(json.dumps(rows))
'''
if __name__=='__main__':
 rows=json.loads(remote(CODE.replace('__PAYLOAD__',base64.b64encode(json.dumps(payload).encode()).decode()),timeout=180))
 p=ROOT/'docs/evidence/M5/resume-20261102/service-seed-preparation.json';p.write_text(json.dumps({'collected_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'nodes':rows},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'prepared':[r['node'] for r in rows]}))
