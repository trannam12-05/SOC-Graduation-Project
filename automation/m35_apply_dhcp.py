import hashlib, json, os, pathlib, subprocess, textwrap

os.umask(0o077)
php = r'''<?php
require_once('/usr/local/etc/inc/config.inc');
$backup='/root/soc-m35-20261105/config.before-dhcp.xml';
if (!file_exists($backup)) {
    if (!copy('/conf/config.xml',$backup)) throw new Exception('Backup failed');
    chmod($backup,0600);
}
$mdl=new \OPNsense\Kea\KeaDhcpv4();
$mdl->general->enabled='1';
$mdl->general->interfaces='lan,opt2,opt3';
$mdl->general->fwrules='1';
$wanted=[
 ['subnet'=>'192.168.1.0/24','pools'=>'192.168.1.100 - 192.168.1.199',
  'option_data_autocollect'=>'0','option_data.domain_name_servers'=>'192.168.1.1',
  'option_data.routers'=>'192.168.1.1','option_data.domain_name'=>'internal','description'=>'Migrated existing LAN IPv4 DHCP'],
 ['subnet'=>'192.168.40.0/24','pools'=>'192.168.40.110 - 192.168.40.199',
  'option_data_autocollect'=>'0','option_data.domain_name_servers'=>'192.168.40.1',
  'option_data.routers'=>'192.168.40.1','option_data.domain_name'=>'soc.local','description'=>'SOC VLAN40 Employee'],
 ['subnet'=>'192.168.50.0/24','pools'=>'192.168.50.110 - 192.168.50.199',
  'option_data_autocollect'=>'0','option_data.domain_name_servers'=>'192.168.50.1',
  'option_data.routers'=>'192.168.50.1','option_data.domain_name'=>'soc.local','description'=>'SOC VLAN50 Guest']
];
$by=[];
foreach($mdl->subnets->subnet4->iterateItems() as $id=>$s) $by[(string)$s->subnet]=$s;
foreach($wanted as $row){
  $s=$by[$row['subnet']]??$mdl->subnets->subnet4->Add();
  foreach($row as $key=>$value){
    if(strpos($key,'.')!==false){[$a,$b]=explode('.',$key,2);$s->{$a}->{$b}=$value;}
    else $s->{$key}=$value;
  }
}
$errors=[];foreach($mdl->performValidation() as $e)$errors[]=['field'=>$e->getField(),'message'=>$e->getMessage()];
if($errors){echo json_encode(['status'=>'VALIDATION_FAILED','errors'=>$errors]);exit(2);}
$mdl->serializeToConfig();
\OPNsense\Core\Config::getInstance()->save();
echo json_encode(['status'=>'SAVED','backup'=>$backup,'subnets'=>$wanted]);
?>'''
path = pathlib.Path('/var/tmp/soc-m35-apply-dhcp.php')
path.write_text(php)
path.chmod(0o600)

def run(args, timeout=45):
    p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    return {'command':' '.join(args),'rc':p.returncode,'stdout':p.stdout[-5000:],'stderr':p.stderr[-3000:]}

steps=[]
steps.append(run(['/usr/local/bin/php','-l',str(path)]))
if steps[-1]['rc'] != 0: raise SystemExit(json.dumps({'status':'PHP_LINT_FAILED','steps':steps}))
steps.append(run(['/usr/local/bin/php',str(path)]))
if steps[-1]['rc'] != 0: raise SystemExit(json.dumps({'status':'APPLY_FAILED','steps':steps}))
steps.append(run(['/usr/local/sbin/configctl','template','reload','OPNsense/Kea']))
steps.append(run(['/usr/local/sbin/configctl','kea','restart']))
steps.append(run(['/usr/local/sbin/configctl','kea','status']))
steps.append(run(['/bin/ps','auxww']))
conf=pathlib.Path('/conf/config.xml').read_bytes()
d={'status':'DONE' if all(x['rc']==0 for x in steps[:5]) else 'PARTIAL',
   'config_sha256':hashlib.sha256(conf).hexdigest(),'steps':steps[:5],
   'kea_process_lines':[line for line in steps[5]['stdout'].splitlines() if 'kea-dhcp4' in line]}
