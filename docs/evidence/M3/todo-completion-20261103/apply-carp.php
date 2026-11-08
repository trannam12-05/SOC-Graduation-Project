<?php
/* M3: them nam VIP native; secret chi doc trong guest. */
require_once('/usr/local/etc/inc/config.inc');
require_once('/usr/local/etc/inc/interfaces.inc');
$local=$config['interfaces']['opt6']['ipaddr']??'';
if (!in_array($local,['10.255.255.1','10.255.255.2'])) {throw new Exception('Unknown role');}
$primary=$local==='10.255.255.1'; $role=$primary?'primary':'secondary'; $skew=$primary?'0':'100';
$dir='/root/soc-m3-todo-carp-20261103';
if (file_exists($dir)) {throw new Exception('Checkpoint exists; inspect before retry');}
if (!mkdir($dir,0700) || !copy('/conf/config.xml',$dir.'/config.before.xml')) {throw new Exception('Backup failed');}
chmod($dir.'/config.before.xml',0600);
function protected_sections() {
 $x=simplexml_load_file('/conf/config.xml');$out=[];
 foreach ($x->children() as $key=>$value) {if (!in_array($key,['virtualip','revision'])) {$out[$key]=hash('sha256',json_encode($value));}}
 return $out;
}
$before=protected_sections();
$password=file_get_contents('/root/soc-m3-1b-'.$role.'-20261103/carp-shared.secret');
if (!preg_match('/^[A-Za-z0-9]{19}$/D',$password)) {throw new Exception('Invalid protected secret');}
$mdl=new \OPNsense\Interfaces\Vip(); $existing=[];
foreach ($mdl->vip->iterateItems() as $id=>$v) {$existing[(string)$v->subnet]=$v;}
if (count($existing)!==0 && count($existing)!==5) {throw new Exception('Unexpected VIP count');}
$rows=[];$added=0;
foreach ([30,40,50,60,99] as $i=>$vlan) {
 $assignment='opt'.($i+1);$address='192.168.'.$vlan.'.1';
 if (($config['interfaces'][$assignment]['if']??'')!=='vtnet0_vlan'.$vlan || ($config['interfaces'][$assignment]['ipaddr']??'')!=='192.168.'.$vlan.'.'.($primary?'2':'3')) {throw new Exception('Interface guard');}
 $fields=['interface'=>$assignment,'mode'=>'carp','subnet'=>$address,'subnet_bits'=>'24','vhid'=>(string)$vlan,'advbase'=>'1','advskew'=>$skew,'password'=>$password,'noexpand'=>'0','nobind'=>'0','nosync'=>'0','descr'=>'SOC CARP VLAN'.$vlan];
 if (isset($existing[$address])) {
  $vip=$existing[$address];foreach ($fields as $k=>$value) {if ($k!=='descr' && (string)$vip->{$k}!==$value) {throw new Exception('Existing VIP differs: '.$k);}}
 } else {if (count($existing)) {throw new Exception('Unexpected existing VIP address');} $vip=$mdl->vip->Add();$vip->setNodes($fields);$added++;}
 unset($fields['password']);$rows[]=$fields;
}
$errors=[];foreach ($mdl->performValidation() as $err) {$errors[]=['field'=>$err->getField(),'message'=>$err->getMessage()];}
if ($errors) {echo json_encode(['status'=>'VALIDATION_FAILED','errors'=>$errors]);exit(2);}
if ($added) {$mdl->serializeToConfig();\OPNsense\Core\Config::getInstance()->save();}
if (protected_sections()!==$before) {throw new Exception('Protected section changed; inspect checkpoint');}
echo json_encode(['status'=>'SAVED','role'=>$role,'added'=>$added,'backup'=>$dir.'/config.before.xml','config_sha256_after'=>hash_file('sha256','/conf/config.xml'),'protected_sections_unchanged'=>true,'rows'=>$rows]);
