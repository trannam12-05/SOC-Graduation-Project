"""Cấu hình endpoint VPCS đúng vùng M1; dùng IP .100 và gateway Primary .2.

Gateway .2 dành cho kiểm thử một firewall, không gọi là CARP VIP đang chạy.
Chỉ dùng console VPCS native, không thay mạng host hoặc Core.
"""
import json,datetime as dt
from topology_remote import remote,ROOT
CODE=r'''
import pathlib,json,subprocess,xml.etree.ElementTree as E,time,socket,telnetlib,shutil,datetime
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');root=E.parse(lab).getroot()
php="""<?php chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');$l=new Lab('/opt/unetlab/labs/SOC-M2-Core-L2.unl',0);$o=[];foreach($l->getNodes() as $id=>$n)$o[$n->getName()]=$n->getStatus();echo json_encode($o);?>"""
p=subprocess.run(['php'],input=php,text=True,capture_output=True,check=True);status=json.loads(p.stdout)
results=[]
for name,vid in [('Employee',40),('Guest',50),('Management',99)]:
 n=next(n for n in root.findall('.//node') if n.get('name')==name);assert n.get('type')=='vpcs'
 if status[name]==0:
  p=subprocess.run(['/opt/unetlab/wrappers/unl_wrapper','-a','start','-T','0','-F',str(lab),'-D',n.get('id')],capture_output=True,text=True,timeout=20);assert p.returncode==0,p.stderr
 time.sleep(0.5)
 logs=[]
 with telnetlib.Telnet('127.0.0.1',32768+int(n.get('id')),timeout=5) as c:
  c.write(b'\n');initial=c.read_until(b'>',timeout=3).decode(errors='replace');logs.append({'command':'connect','output':initial})
  assert name.lower() in initial.lower() or 'vpcs' in initial.lower(),'Unexpected console'
  for command in ['set pcname '+name,'ip 192.168.%d.100/24 192.168.%d.2'%(vid,vid),'save','show ip','ping ?']:
   c.write(command.encode()+b'\n');time.sleep(0.25)
   output=c.read_until(b'>',timeout=3).decode(errors='replace');logs.append({'command':command,'output':output})
 show=next(x['output'] for x in logs if x['command']=='show ip')
 assert '192.168.%d.100'%vid in show and '192.168.%d.2'%vid in show,'IP not confirmed in actual show output'
 startup=pathlib.Path('/opt/unetlab/tmp/0')/root.get('id')/n.get('id')/'startup.vpc'
 results.append({'node':name,'id':n.get('id'),'vlan':vid,'ip':'192.168.%d.100/24'%vid,'gateway':'192.168.%d.2'%vid,'state':'CONFIGURED_NOT_END_TO_END_VERIFIED','console_log':logs,'startup_config':startup.read_text() if startup.exists() else None})
print(json.dumps(results))
'''
if __name__=='__main__':
 rows=json.loads(remote(CODE,timeout=120));out=ROOT/'docs/evidence/M2/resume-20261102';out.mkdir(exist_ok=True)
 d={'collected_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'scope':'Actual VPCS console configuration; no CARP or end-to-end acceptance yet','endpoints':rows}
 (out/'vpcs-configured.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'configured':[r['node'] for r in rows],'evidence':str(out/'vpcs-configured.json')}))
