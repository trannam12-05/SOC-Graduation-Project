<?php
/* Đọc mật khẩu từ stdin riêng, không in hoặc lưu vào script/log.
 * Chỉ bật Primary→Secondary và phạm vi Aliases; không đồng bộ interface.
 */
require_once('/usr/local/etc/inc/config.inc');
$input=json_decode(stream_get_contents(STDIN),true);
if (empty($input['secret']) || ($config['interfaces']['opt6']['ipaddr']??'')!=='10.255.255.1') { exit(2); }
$before=simplexml_load_file('/conf/config.xml');$protected=[];
foreach(['interfaces','system','cert','ca','nat','dhcpd','virtualip'] as $key){$protected[$key]=hash('sha256',json_encode($before->{$key}));}
$dir='/root/soc-xmlrpc-backup-'.date('Ymd-His');mkdir($dir,0700);
copy('/conf/config.xml',$dir.'/config.xml');chmod($dir.'/config.xml',0600);
$mdl=new \OPNsense\Core\Hasync();
$mdl->synchronizetoip='10.255.255.2';$mdl->username='root';$mdl->password=$input['secret'];
$mdl->syncitems='aliases';$mdl->pfsyncversion='1400';
$errors=$mdl->performValidation();if(count($errors)){echo "MODEL_VALIDATION_FAILED\n";exit(3);}
$mdl->serializeToConfig();\OPNsense\Core\Config::getInstance()->save();
$current=simplexml_load_file('/conf/config.xml');
foreach($protected as $key=>$hash){if(hash('sha256',json_encode($current->{$key}))!==$hash){echo "PROTECTED_SECTION_CHANGED\n";exit(4);}}
echo json_encode(['configured'=>true,'peer'=>'10.255.255.2','direction'=>'Primary to Secondary only','scope'=>'aliases','pfsync_compatibility'=>'1400','backup'=>$dir])."\n";
