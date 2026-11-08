"""Gắn nhãn vùng và trạng thái trên lab thật; không thay link/guest."""
import base64,json,datetime as dt
from topology_remote import remote,ROOT

labels=[
 ('Internet-WAN',420,0,'INTERNET / WAN — upstream chưa xác định','#263b53'),
 ('Firewall',460,135,'FIREWALL / HA — chưa kiểm thử','#a53036'),
 ('Core',445,315,'CORE L2 — cấu hình M2 giữ nguyên','#205a9b'),
 ('DC-zone',65,690,'DATA CENTER · VLAN 30<br>Ubuntu · HTTP 8000 đã kiểm chứng','#176642'),
 ('Employee-zone',280,690,'EMPLOYEE · VLAN 40<br>VPCS · chưa cấu hình','#97630d'),
 ('Guest-zone',485,690,'GUEST · VLAN 50<br>VPCS · chưa cấu hình','#6d39a0'),
 ('DMZ-zone',685,690,'DMZ · VLAN 60<br>Ubuntu · HTTP 80 đã kiểm chứng','#176642'),
 ('MGMT-zone',890,690,'MANAGEMENT · VLAN 99<br>VPCS · chưa cấu hình','#176642'),
 ('SOC-zone',1080,290,'SOC / GIÁM SÁT','#6d39a0'),
 ('Suricata-state',1055,440,'Suricata 7.0.3 đã cài<br>capture: NIC0 · quản trị: NIC1','#6d39a0'),
 ('Wazuh-state',1065,620,'Wazuh Manager 4.14.9 đã cài<br>NIC0 · VLAN 99 Management','#176642'),
 ('Automation-note',1030,745,'Automation: thành phần logic M1<br>Chưa có đặc tả máy riêng; chưa tạo node','#526176'),
 ('Scope-note',180,785,'WAN1/WAN2 là bridge cô lập · không nối mạng Windows/VMware<br>Topology từng phần đã dựng; chưa xác minh E2E / HA / SOC','#526176'),
]
payload=[]
for idx,(name,x,y,text,color) in enumerate(labels,1):
 html=f'<div id="customText{20261102000+idx}" class="customShape customText context-menu" data-path="" style="display:inline;position:absolute;left:{x}px;top:{y}px;cursor:move;z-index:1001;"><p align="center" style="vertical-align:top;color:{color};background-color:#ffffff;font-size:13px;font-weight:bold;">{text}</p></div>'
 payload.append({'name':name,'type':'text','data':html})
code=r'''
import base64,json,pathlib,subprocess,shutil
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl')
backup=sorted(pathlib.Path('/root').glob('soc-topology-first-backup-*'))[-1]
if not (backup/'lab-before-labels.unl').exists():shutil.copy2(lab,backup/'lab-before-labels.unl')
php="""<?php chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');$l=new Lab('/opt/unetlab/labs/SOC-M2-Core-L2.unl',0);$existing=array();foreach($l->getTextObjects() as $t)$existing[$t->getName()]=$t->getData();$rows=json_decode(base64_decode('__LABELS__'),true);foreach($rows as $row){if(isset($existing[$row['name']])){if($existing[$row['name']]!==$row['data'])throw new Exception('Different existing label');continue;}$rc=$l->addTextObject($row);if($rc->status!==0)throw new Exception('Label failed '.$rc->status);}echo json_encode(array('labels'=>count($l->getTextObjects())));?>"""
p=subprocess.run(['php'],input=php,text=True,capture_output=True);assert p.returncode==0,p.stderr
print(p.stdout)
'''.replace('__LABELS__',base64.b64encode(json.dumps(payload).encode()).decode())
if __name__=='__main__':
 result=json.loads(remote(code));result['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
 (ROOT/'docs/evidence/M2/topology-first-20261102/labels-receipt.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(result)
