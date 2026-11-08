"""Start three VPCS endpoints and configure DHCP/static addressing for M3.5."""
import datetime as dt, json
from topology_remote import remote, ROOT

CODE=r'''
import json,pathlib,subprocess,telnetlib,time,xml.etree.ElementTree as E
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');root=E.parse(lab).getroot()
php="""<?php chdir('/opt/unetlab/html');require_once('/opt/unetlab/html/includes/init.php');$l=new Lab('/opt/unetlab/labs/SOC-M2-Core-L2.unl',0);$o=[];foreach($l->getNodes() as $id=>$n)$o[$n->getName()]=$n->getStatus();echo json_encode($o);?>"""
status=json.loads(subprocess.run(['php'],input=php,text=True,capture_output=True,check=True).stdout)
rows=[]
for name in ['Employee','Guest','Management']:
 n=next(x for x in root.findall('.//node') if x.get('name')==name);assert n.get('type')=='vpcs'
 if status[name]==0:
  p=subprocess.run(['/opt/unetlab/wrappers/unl_wrapper','-a','start','-T','0','-F',str(lab),'-D',n.get('id')],capture_output=True,text=True,timeout=20);assert p.returncode==0,p.stderr
 time.sleep(1)
 commands=['set pcname '+name]
 if name in ['Employee','Guest']:commands+=['ip dhcp','save','show ip']
 else:commands+=['ip 192.168.99.100/24 192.168.99.1','save','show ip']
 logs=[]
 with telnetlib.Telnet('127.0.0.1',32768+int(n.get('id')),timeout=6) as c:
  time.sleep(1);c.write(b'\x03\r\n');time.sleep(1);logs.append({'command':'connect-and-cancel-startup-check','output':c.read_very_eager().decode(errors='replace')})
  for cmd in commands:
   c.write(cmd.encode()+b'\r\n');data=b'';start=time.monotonic();last=start
   limit=14 if cmd=='ip dhcp' else 5
   while time.monotonic()-start<limit:
    time.sleep(.25);part=c.read_very_eager()
    if part:data+=part;last=time.monotonic()
    if b'>' in data and time.monotonic()-last>.5:break
   logs.append({'command':cmd,'output':data.decode(errors='replace')})
 show=logs[-1]['output']
 if name=='Employee':assert any('192.168.40.'+str(i) in show for i in range(110,200)),name+' DHCP pool address not confirmed: '+show
 elif name=='Guest':assert any('192.168.50.'+str(i) in show for i in range(110,200)),name+' DHCP pool address not confirmed: '+show
 else:assert '192.168.99.100' in show,name+' static address not confirmed: '+show
 assert ('192.168.99.1' if name=='Management' else ('192.168.40.1' if name=='Employee' else '192.168.50.1')) in show,name+' VIP gateway not confirmed'
 rows.append({'node':name,'id':n.get('id'),'console_port':32768+int(n.get('id')),'logs':logs})
print(json.dumps(rows))
'''
rows=json.loads(remote(CODE,timeout=150))
out=ROOT/'docs/evidence/M3/M3.5-network-services-20261105';out.mkdir(parents=True,exist_ok=True)
d={'collected_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),
   'scope':'Actual VPCS console: Employee/Guest DHCP; Management static; CARP VIP .1 as gateway',
   'endpoints':rows}
(out/'m35-endpoints-configured.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'DONE','nodes':[x['node'] for x in rows],'evidence':str(out/'m35-endpoints-configured.json')}))
