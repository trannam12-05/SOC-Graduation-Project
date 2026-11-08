import hashlib,json,os,pathlib,subprocess
os.umask(0o077)
php=r'''<?php
require_once('/usr/local/etc/inc/config.inc');
if(($config['interfaces']['opt6']['ipaddr']??'')!=='10.255.255.1')throw new Exception('Not Primary');
$config['system']['hostname']='OPNsense-Primary';
$config['hasync']['syncitems']='aliases,rules,kea,dnsforwarder';
$ca=new \OPNsense\Kea\KeaCtrlAgent();$ca->general->enabled='1';$ca->general->http_host='127.0.0.1';$ca->general->http_port='8000';
$kea=new \OPNsense\Kea\KeaDhcpv4();$kea->ha->enabled='1';$kea->ha->this_server_name='';$kea->ha->max_unacked_clients='2';
$peers=[];foreach($kea->ha_peers->peer->iterateItems() as $id=>$p)$peers[(string)$p->name]=$p;
$wanted=[['name'=>'OPNsense-Primary','role'=>'primary','url'=>'http://10.255.255.1:8001/'],['name'=>'OPNsense-Secondary','role'=>'standby','url'=>'http://10.255.255.2:8001/']];
foreach($wanted as $f){$p=$peers[$f['name']]??$kea->ha_peers->peer->Add();$p->setNodes($f);}
$fw=new \OPNsense\Firewall\Filter();$desc='SOC HA KEA tcp8001';$found=null;foreach($fw->rules->rule->iterateItems() as $r)if((string)$r->description===$desc)$found=$r;
$fields=['enabled'=>'1','action'=>'pass','quick'=>'1','interface'=>'opt6','direction'=>'in','ipprotocol'=>'inet','protocol'=>'tcp','source_net'=>'10.255.255.2/32','destination_net'=>'10.255.255.1/32','destination_port'=>'8001','log'=>'1','nosync'=>'1','sequence'=>'13','description'=>$desc];
if($found){foreach($fields as $k=>$v)if((string)$found->{$k}!==$v)throw new Exception('Existing KEA rule differs');}else{$r=$fw->rules->rule->Add();$r->setNodes($fields);}
$errors=[];foreach([$ca,$kea,$fw] as $m)foreach($m->performValidation() as $e)$errors[]=['field'=>$e->getField(),'message'=>$e->getMessage()];
if($errors){echo json_encode(['status'=>'VALIDATION_FAILED','errors'=>$errors]);exit(2);}
$ca->serializeToConfig();$kea->serializeToConfig();$fw->serializeToConfig();
$config['system']['hostname']='OPNsense-Primary';
$config['hasync']['syncitems']='aliases,rules,kea,dnsforwarder';
\OPNsense\Core\Config::getInstance()->save();
echo json_encode(['status'=>'SAVED','hostname'=>'OPNsense-Primary','syncitems'=>$config['hasync']['syncitems'],'peers'=>$wanted,'ha_rule'=>$fields]);
?>'''
p=pathlib.Path('/var/tmp/soc-m36-primary-ha.php');p.write_text(php);p.chmod(0o600)
def run(a,timeout=70):
 q=subprocess.run(a,capture_output=True,text=True,timeout=timeout);return {'command':' '.join(a),'rc':q.returncode,'stdout':q.stdout[-7000:],'stderr':q.stderr[-3000:]}
steps=[run(['/usr/local/bin/php','-l',str(p)]),run(['/usr/local/bin/php',str(p)])]
if steps[-1]['rc']==0:steps.append(run(['/usr/local/sbin/configctl','template','reload','OPNsense/Kea']))
if steps[-1]['rc']==0:steps.append(run(['/usr/local/sbin/configctl','filter','reload']))
if steps[-1]['rc']==0:steps.append(run(['/bin/hostname','OPNsense-Primary.internal']))
if steps[-1]['rc']==0:steps.append(run(['/usr/local/sbin/configctl','kea','restart']))
d={'status':'DONE' if all(x['rc']==0 for x in steps) else 'FAILED','steps':steps,'config_sha256':hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest()}
