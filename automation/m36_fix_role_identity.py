import hashlib
import pathlib
import subprocess

php = r'''<?php
require_once('/usr/local/etc/inc/config.inc');
require_once('/usr/local/etc/inc/util.inc');
$ip = $config['interfaces']['opt6']['ipaddr'] ?? '';
if ($ip === '10.255.255.1') {
    $hostname = 'OPNsense-Primary';
} elseif ($ip === '10.255.255.2') {
    $hostname = 'OPNsense-Secondary';
} else {
    throw new Exception('Unknown HA role');
}
$config['system']['hostname'] = $hostname;
write_config('SOC M3.6: persist role-specific hostname for Kea HA identity');
echo json_encode(['ip' => $ip, 'hostname' => $hostname]);
?>'''
path = pathlib.Path('/var/tmp/soc-m36-fix-role.php')
path.write_text(php)
path.chmod(0o600)
result = subprocess.run(['/usr/local/bin/php', str(path)], capture_output=True,
                        text=True, timeout=30)
d = {
    'status': 'DONE' if result.returncode == 0 else 'FAILED',
    'rc': result.returncode,
    'stdout': result.stdout,
    'stderr': result.stderr[-1000:],
    'config_sha256': hashlib.sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest(),
}
