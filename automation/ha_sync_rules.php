<?php
/* Chỉ thêm ba rule SYNC theo peer; không thay interface, mật khẩu hoặc rule cũ.
 * Dùng model Firewall/Filter của đúng guest; mặc định chỉ kiểm tra, không lưu.
 */
require_once('/usr/local/etc/inc/config.inc');
$role = $argv[1] ?? '';
$apply = ($argv[2] ?? 'check') === 'apply';
if (!in_array($role, ['Primary', 'Secondary'])) { throw new Exception('Invalid role'); }
$local = $role === 'Primary' ? '10.255.255.1' : '10.255.255.2';
$peer = $role === 'Primary' ? '10.255.255.2' : '10.255.255.1';
if (($config['interfaces']['opt6']['if'] ?? '') !== 'vtnet2' ||
    ($config['interfaces']['opt6']['ipaddr'] ?? '') !== $local) {
    throw new Exception('SYNC interface/IP does not match inspected guest');
}
function protected_hashes() {
    $xml = simplexml_load_file('/conf/config.xml'); $out = [];
    foreach (['interfaces','system','cert','ca','ipsec','openvpn','nat','dhcpd','hasync','virtualip'] as $key) {
        $out[$key] = hash('sha256', json_encode($xml->{$key}));
    }
    return $out;
}
$before = protected_hashes();
$mdl = new \OPNsense\Firewall\Filter();
$added = []; $existing = [];
foreach ($mdl->rules->rule->iterateItems() as $id => $r) {
    $existing[(string)$r->description] = $r;
}
foreach (['icmp','pfsync','tcp'] as $index => $proto) {
    $name = 'SOC HA SYNC '.$proto;
    $fields = ['enabled'=>'1','action'=>'pass','quick'=>'1','interface'=>'opt6',
        'direction'=>'in','ipprotocol'=>'inet','protocol'=>$proto,
        'source_net'=>$peer.'/32','destination_net'=>$local.'/32',
        'log'=>'1','nosync'=>'1','sequence'=>(string)(10+$index),'description'=>$name];
    if ($proto === 'tcp') { $fields['destination_port'] = '443'; }
    if ($proto === 'pfsync') { $fields['statetype'] = 'none'; }
    if (isset($existing[$name])) {
        foreach ($fields as $key=>$value) {
            if ((string)$existing[$name]->{$key} !== $value) { throw new Exception('Different existing HA rule: '.$name); }
        }
        continue;
    }
    $r = $mdl->rules->rule->Add(); $r->setNodes($fields); $added[] = $fields;
}
$errors = [];
foreach ($mdl->performValidation() as $e) { $errors[] = ['field'=>$e->getField(),'message'=>$e->getMessage()]; }
if ($errors) { echo json_encode(['validation'=>'FAILED','errors'=>$errors]); exit(2); }
if ($apply && count($added)) {
    $dir = '/root/soc-ha-rules-backup-'.date('Ymd-His');
    if (!mkdir($dir,0700) || !copy('/conf/config.xml',$dir.'/config.xml')) { throw new Exception('Backup failed'); }
    chmod($dir.'/config.xml',0600);
    $mdl->serializeToConfig();
    \OPNsense\Core\Config::getInstance()->save();
    if (protected_hashes() !== $before) { throw new Exception('Protected section changed; inspect backup before proceeding'); }
    echo json_encode(['status'=>'SAVED','backup'=>$dir,'added'=>count($added),'protected_sections_unchanged'=>true])."\n";
} else {
    echo json_encode(['status'=>$apply?'ALREADY_PRESENT':'CHECK_ONLY','new_rule_count'=>count($added),'planned'=>$added])."\n";
}
