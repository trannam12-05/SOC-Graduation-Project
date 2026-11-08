"""Cài riêng Wazuh manager offline; không gọi là bộ SOC đầy đủ hoặc pipeline live."""
from pathlib import Path
import subprocess,json,hashlib,os,re,time,traceback
OUT=Path('/var/lib/soc');OUT.mkdir(exist_ok=True)
result={'role':'Wazuh-SOC','deployment':'MANAGER_ONLY','state':'INSTALLING','indexer_dashboard':'NOT_INSTALLED','network_pipeline':'NOT_VERIFIED'}
def run(args,timeout=240):
 p=subprocess.run(args,text=True,capture_output=True,timeout=timeout,env={**os.environ,'DEBIAN_FRONTEND':'noninteractive'})
 with (OUT/'manager-bootstrap.log').open('a') as f:f.write('$ '+' '.join(args)+'\n'+p.stdout+p.stderr+'\nexit='+str(p.returncode)+'\n')
 if p.returncode:raise RuntimeError('Command failed: '+args[0])
 return p.stdout
try:
 seed=Path('/mnt/soc-seed');seed.mkdir(exist_ok=True)
 if not os.path.ismount(seed):run(['mount','-o','ro','LABEL=cidata',str(seed)])
 pkg=next(seed.glob('wazuh-manager*.deb'))
 h=hashlib.sha256()
 with pkg.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 assert h.hexdigest()=='8b6f615f84c93a51c6023e7e542b9519945684434b117396ae61517bcdcba5f8'
 run(['dpkg','-i',str(pkg)],timeout=480)
 conf=Path('/var/ossec/etc/ossec.conf');backup=OUT/'ossec.conf.before';backup.write_bytes(conf.read_bytes());backup.chmod(0o600)
 text=conf.read_text()
 # Node chưa có đường indexer/Internet trong thiết kế vật lý được xác nhận.
 for name in ['vulnerability-detection','indexer']:
  pattern=r'(<'+name+r'>)(.*?)(</'+name+r'>)'
  def disable(m):return m.group(1)+re.sub(r'<enabled>\s*yes\s*</enabled>','<enabled>no</enabled>',m.group(2))+m.group(3)
  text=re.sub(pattern,disable,text,flags=re.S)
 location='/var/log/soc-suricata-replay.json'
 Path(location).touch()
 block='<localfile><log_format>json</log_format><location>'+location+'</location></localfile>\n'
 where=text.rfind('</ossec_config>');assert where>=0
 text=text[:where]+block+text[where:];conf.write_text(text)
 rules='''<group name="local,soc,suricata,">
 <rule id="100101" level="8">
  <decoded_as>json</decoded_as>
  <field name="event_type">^alert$</field>
  <field name="alert.signature_id">^1000001$</field>
  <description>SOC benign Suricata marker: controlled replay</description>
 </rule>
</group>
'''
 Path('/var/ossec/etc/rules/soc_suricata_replay.xml').write_text(rules)
 run(['systemctl','daemon-reload']);run(['systemctl','enable','--now','wazuh-manager']);time.sleep(10)
 result['service']=run(['systemctl','is-active','wazuh-manager']).strip()
 result['package_version']=run(['dpkg-query','-W','wazuh-manager']).strip()
 replay=seed/'suricata-real-alert-replay.jsonl'
 if replay.exists():
  line=replay.read_text().strip();event=json.loads(line)
  assert event['event_type']=='alert' and event['alert']['signature_id']==1000001
  test=subprocess.run(['/var/ossec/bin/wazuh-logtest'],input=line+'\n',text=True,capture_output=True,timeout=30)
  (OUT/'logtest.txt').write_text(test.stdout+test.stderr)
  result['real_suricata_replay_sha256']=hashlib.sha256((line+'\n').encode()).hexdigest()
  result['logtest_rule_100101_matched']=bool(re.search(r"id:\s*'100101'",test.stdout+test.stderr))
  with Path(location).open('a') as f:f.write(line+'\n')
  time.sleep(12)
  alerts=Path('/var/ossec/logs/alerts/alerts.json')
  matched=[]
  if alerts.exists():
   for row in alerts.read_text(errors='replace').splitlines():
    try:d=json.loads(row)
    except json.JSONDecodeError:continue
    if str(d.get('rule',{}).get('id'))=='100101':matched.append(d)
  result['manager_replay_alert_count']=len(matched)
  (OUT/'suricata-replay-alerts.json').write_text(json.dumps(matched,indent=2))
 result['state']='CONFIGURED_MANAGER_ONLY'
 result['boot_id']=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
except Exception as error:
 result['state']='FAILED';result['error']=str(error)
 with (OUT/'manager-bootstrap.log').open('a') as f:f.write(traceback.format_exc())
finally:
 (OUT/'result.json').write_text(json.dumps(result,indent=2))
 message='SOC_BOOTSTRAP_RESULT '+json.dumps(result)+'\n'
 for terminal in ['/dev/ttyS0','/dev/tty1']:
  try:
   with open(terminal,'w') as f:f.write(message)
  except OSError:pass
