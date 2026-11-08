"""Cập nhật bốn nhãn topology đã lỗi thời theo minh chứng runtime; không boot node."""
from pathlib import Path
import datetime as dt
import json
from topology_remote import ROOT, remote

EV = ROOT / 'docs/evidence/M1/label-correction-20261105'
EV.mkdir(parents=True, exist_ok=True)
expected_hash = json.loads((ROOT / 'docs/evidence/M1/wazuh-link-20261105/connection-result.json').read_text(encoding='utf-8'))['after_sha256']
code = r'''
from pathlib import Path
import base64,datetime,hashlib,json,os,shutil,subprocess,xml.etree.ElementTree as E
lab=Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');before=lab.read_bytes()
assert hashlib.sha256(before).hexdigest()=='__HASH__','Topology changed after verified Wazuh link; stop'
running=[]
for f in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=f.read_bytes().split(b'\0')
  if a and (b'qemu-system-' in a[0] or os.path.basename(a[0])==b'vpcs'):running.append(f.parent.name)
 except OSError:pass
assert not running,'Node process running; stop before label edit'
root=E.fromstring(before);texts={int(t.get('id')):t for t in root.findall('.//textobject')}
assert texts[4].get('name')=='DC-zone' and texts[7].get('name')=='DMZ-zone'
assert texts[10].get('name')=='Suricata-state' and texts[11].get('name')=='Wazuh-state'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup=Path('/root/soc-m1-label-correction-'+stamp);backup.mkdir(mode=0o700)
shutil.copy2(lab,backup/'lab-before.unl');os.chmod(backup/'lab-before.unl',0o600)
rows={
 4:('DC-zone',96,498,'DATA CENTER · VLAN 30<br>Ubuntu · HTTP 8000 đã kiểm chứng','#176642'),
 7:('DMZ-zone',685,690,'DMZ · VLAN 60<br>Ubuntu · HTTP 80 đã kiểm chứng','#176642'),
 10:('Suricata-state',1055,440,'Suricata 7.0.3 đã cài<br>capture: NIC0 · quản trị: NIC1','#6d39a0'),
 11:('Wazuh-state',1065,620,'Wazuh Manager 4.14.9 đã cài<br>NIC0 · VLAN 99 Management','#176642')
}
payload=[]
for ident,(name,x,y,text,color) in rows.items():
 html=f'<div id="customText{20261102000+ident}" class="customShape customText context-menu" data-path="" style="display:inline;position:absolute;left:{x}px;top:{y}px;cursor:move;z-index:1001;"><p align="center" style="vertical-align:top;color:{color};background-color:#ffffff;font-size:13px;font-weight:bold;">{text}</p></div>'
 payload.append({'id':ident,'name':name,'data':html})
php=r"""<?php
chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');
$l=new Lab('/opt/unetlab/labs/SOC-M2-Core-L2.unl',0);$rows=json_decode(base64_decode('__ROWS__'),true);
foreach($rows as $row){$rc=$l->editTextObject($row);if($rc!==0)throw new Exception('editTextObject failed '.$row['id'].' rc '.$rc);}
echo json_encode(array('updated_ids'=>array_map(function($x){return $x['id'];},$rows),'count'=>count($l->getTextObjects())));
?>""".replace('__ROWS__',base64.b64encode(json.dumps(payload,ensure_ascii=False).encode()).decode())
p=subprocess.run(['php'],input=php,text=True,capture_output=True);assert p.returncode==0,p.stderr
operation=json.loads(p.stdout);after=lab.read_bytes();a=E.fromstring(after)
assert len(a.findall('.//node'))==10 and len(a.findall('.//network'))==11
assert not any(Path('/proc').glob('[0-9]*/cmdline')) is False
def normalized_without_targets(x):
 x=E.fromstring(E.tostring(x))
 for t in x.findall('.//textobject'):
  if int(t.get('id')) in rows:
   d=t.find('data');d.text='EXPECTED_UPDATED_DATA'
 return E.tostring(x)
assert normalized_without_targets(root)==normalized_without_targets(a),'Unexpected topology change outside four label data fields'
actual={int(t.get('id')):t.find('data').text for t in a.findall('.//textobject') if int(t.get('id')) in rows}
for ident,row in rows.items():
 raw=actual[ident]
 try:decoded=base64.b64decode(raw,validate=True).decode()
 except Exception:decoded=raw
 assert row[3] in decoded,(ident,decoded)
shutil.copy2(lab,backup/'lab-after.unl');os.chmod(backup/'lab-after.unl',0o600)
result={'operation':operation,'backup_directory':str(backup),'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest(),'updated_ids':sorted(rows),'only_four_label_data_fields_changed':True,'node_count':10,'network_count':11,'power_operations':False,'guest_configuration_changed':False}
(backup/'result.json').write_text(json.dumps(result,indent=2));os.chmod(backup/'result.json',0o600)
print(json.dumps(result))
'''.replace('__HASH__', expected_hash)

result = json.loads(remote(code))
result['collector_time'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
(EV / 'label-update-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
