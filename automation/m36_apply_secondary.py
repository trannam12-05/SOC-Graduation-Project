import hashlib,json,os,pathlib,subprocess
os.umask(0o077)
php=r'''<?php
require_once('/usr/local/etc/inc/config.inc');
if(($config['interfaces']['opt6']['ipaddr']??'')!=='10.255.255.2')throw new Exception('Not Secondary');
$config['system']['hostname']='OPNsense-Secondary';
$mdl=new \OPNsense\Firewall\Filter();$desc='SOC HA KEA tcp8001';$found=null;
foreach($mdl->rules->rule->iterateItems() as $r)if((string)$r->description===$desc)$found=$r;
$fields=['enabled'=>'1','action'=>'pass','quick'=>'1','interface'=>'opt6','direction'=>'in','ipprotocol'=>'inet','protocol'=>'tcp','source_net'=>'10.255.255.1/32','destination_net'=>'10.255.255.2/32','destination_port'=>'8001','log'=>'1','nosync'=>'1','sequence'=>'13','description'=>$desc];
if($found){foreach($fields as $k=>$v)if((string)$found->{$k}!==$v)throw new Exception('Existing KEA rule differs');}
else{$r=$mdl->rules->rule->Add();$r->setNodes($fields);}
$errors=[];foreach($mdl->performValidation() as $e)$errors[]=['field'=>$e->getField(),'message'=>$e->getMessage()];
if($errors){echo json_encode(['status'=>'VALIDATION_FAILED','errors'=>$errors]);exit(2);}
$mdl->serializeToConfig();
$config['system']['hostname']='OPNsense-Secondary';
\OPNsense\Core\Config::getInstance()->save();
echo json_encode(['status'=>'SAVED','hostname'=>'OPNsense-Secondary','rule'=>$fields]);
?>'''
p=pathlib.Path('/var/tmp/soc-m36-secondary.php');p.write_text(php);p.chmod(0o600)
def run(a,timeout=60):
 q=subprocess.run(a,capture_output=True,text=True,timeout=timeout);return {'command':' '.join(a),'rc':q.returncode,'stdout':q.stdout[-5000:],'stderr':q.stderr[-2000:]}
steps=[run(['/usr/local/bin/php','-l',str(p)]),run(['/usr/local/bin/php',str(p)])]
if steps[-1]['rc']==0:steps.append(run(['/usr/local/sbin/configctl','filter','reload']))
if steps[-1]['rc']==0:steps.append(run(['/bin/hostname','OPNsense-Secondary.internal']))
d={'status':'DONE' if all(x['rc']==0 for x in steps) else 'FAILED','steps':steps,'config_sha256':hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest()}
