import hashlib,json,os,pathlib,subprocess
os.umask(0o077)
php=r'''<?php
require_once('/usr/local/etc/inc/config.inc');
$backup='/root/soc-m35-20261105/config.before-dnsmasq-ipv4-migration.xml';
if(!file_exists($backup)){if(!copy('/conf/config.xml',$backup))throw new Exception('Backup failed');chmod($backup,0600);}
$mdl=new \OPNsense\Dnsmasq\Dnsmasq();$deleted=[];
foreach($mdl->dhcp_ranges->iterateItems() as $id=>$r){
 if(strpos((string)$r->start_addr,':')===false){$deleted[]=['uuid'=>$id,'start'=>(string)$r->start_addr,'end'=>(string)$r->end_addr,'interface'=>(string)$r->interface];$mdl->dhcp_ranges->del($id);}
}
$errors=[];foreach($mdl->performValidation() as $e)$errors[]=['field'=>$e->getField(),'message'=>$e->getMessage()];
if($errors){echo json_encode(['status'=>'VALIDATION_FAILED','errors'=>$errors]);exit(2);}
$mdl->serializeToConfig();\OPNsense\Core\Config::getInstance()->save();
echo json_encode(['status'=>'SAVED','backup'=>$backup,'migrated_ipv4_ranges'=>$deleted]);
?>'''
p=pathlib.Path('/var/tmp/soc-m35-migrate-dnsmasq-ipv4.php');p.write_text(php);p.chmod(0o600)
def run(a,timeout=60):
 q=subprocess.run(a,capture_output=True,text=True,timeout=timeout)
 return {'command':' '.join(a),'rc':q.returncode,'stdout':q.stdout[-7000:],'stderr':q.stderr[-3000:]}
steps=[run(['/usr/local/bin/php','-l',str(p)])]
if steps[-1]['rc']==0:steps.append(run(['/usr/local/bin/php',str(p)]))
if steps[-1]['rc']==0:steps.append(run(['/usr/local/sbin/configctl','template','reload','OPNsense/Dnsmasq']))
if steps[-1]['rc']==0:steps.append(run(['/usr/local/sbin/configctl','dnsmasq','restart']))
if steps[-1]['rc']==0:steps.append(run(['/usr/local/sbin/configctl','kea','restart']))
steps.append(run(['/usr/bin/sockstat','-4','-l']))
d={'status':'DONE' if len(steps)>=6 and all(x['rc']==0 for x in steps[:5]) else 'FAILED',
   'config_sha256':hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest(),
   'steps':steps[:5],'listeners':steps[-1]['stdout']}
