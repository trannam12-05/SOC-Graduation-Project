import hashlib, json, os, pathlib, subprocess

os.umask(0o077)
php=r'''<?php
require_once('/usr/local/etc/inc/config.inc');
$backup='/root/soc-m35-20261105/config.before-firewall.xml';
if(!file_exists($backup)){if(!copy('/conf/config.xml',$backup))throw new Exception('Backup failed');chmod($backup,0600);}
$mdl=new \OPNsense\Firewall\Filter();$existing=[];
foreach($mdl->rules->rule->iterateItems() as $r)$existing[(string)$r->description]=$r;
$spec=[
 ['opt2','udp','192.168.40.0/24','192.168.40.1/32','53','SOC M35 EMPLOYEE DNS UDP'],
 ['opt2','tcp','192.168.40.0/24','192.168.40.1/32','53','SOC M35 EMPLOYEE DNS TCP'],
 ['opt2','icmp','192.168.40.0/24','192.168.40.1/32','','SOC M35 EMPLOYEE CARP PING'],
 ['opt2','tcp','192.168.40.0/24','192.168.30.10/32','8000','SOC M35 EMPLOYEE TO DC HTTP8000'],
 ['opt3','udp','192.168.50.0/24','192.168.50.1/32','53','SOC M35 GUEST DNS UDP'],
 ['opt3','tcp','192.168.50.0/24','192.168.50.1/32','53','SOC M35 GUEST DNS TCP'],
 ['opt3','icmp','192.168.50.0/24','192.168.50.1/32','','SOC M35 GUEST CARP PING'],
 ['opt5','icmp','192.168.99.100/32','192.168.99.1/32','','SOC M35 MANAGEMENT CARP PING']
];$added=[];
foreach($spec as $i=>$x){[$iface,$proto,$src,$dst,$port,$desc]=$x;
 $f=['enabled'=>'1','action'=>'pass','quick'=>'1','interface'=>$iface,'direction'=>'in','ipprotocol'=>'inet',
     'protocol'=>$proto,'source_net'=>$src,'destination_net'=>$dst,'log'=>'1','sequence'=>(string)(300+$i),'description'=>$desc];
 if($port!=='')$f['destination_port']=$port;
 if(isset($existing[$desc])){foreach($f as $k=>$v)if((string)$existing[$desc]->{$k}!==$v)throw new Exception('Existing rule differs: '.$desc);continue;}
 $r=$mdl->rules->rule->Add();$r->setNodes($f);$added[]=$f;
}
$errors=[];foreach($mdl->performValidation() as $e)$errors[]=['field'=>$e->getField(),'message'=>$e->getMessage()];
if($errors){echo json_encode(['status'=>'VALIDATION_FAILED','errors'=>$errors]);exit(2);}
$mdl->serializeToConfig();\OPNsense\Core\Config::getInstance()->save();
echo json_encode(['status'=>'SAVED','backup'=>$backup,'added'=>$added]);
?>'''
p=pathlib.Path('/var/tmp/soc-m35-apply-firewall.php');p.write_text(php);p.chmod(0o600)
def run(args,timeout=60):
 q=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 return {'command':' '.join(args),'rc':q.returncode,'stdout':q.stdout[-8000:],'stderr':q.stderr[-3000:]}
steps=[run(['/usr/local/bin/php','-l',str(p)])]
if steps[-1]['rc']==0:steps.append(run(['/usr/local/bin/php',str(p)]))
if steps[-1]['rc']==0:steps.append(run(['/usr/local/sbin/configctl','filter','reload']))
steps.append(run(['/sbin/pfctl','-sr']))
d={'status':'DONE' if len(steps)>=4 and all(x['rc']==0 for x in steps[:3]) else 'FAILED',
   'config_sha256':hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest(),
   'steps':steps[:3],
   'runtime_rules':[x for x in steps[-1]['stdout'].splitlines() if 'SOC M35' in x or '192.168.40.1' in x or '192.168.50.1' in x or '192.168.99.1' in x]}
