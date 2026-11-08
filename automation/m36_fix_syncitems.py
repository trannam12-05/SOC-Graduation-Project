import hashlib
import pathlib
import subprocess

php = r'''<?php
require_once('/usr/local/etc/inc/config.inc');
require_once('/usr/local/etc/inc/util.inc');
if (($config['interfaces']['opt6']['ipaddr'] ?? '') !== '10.255.255.1') {
    throw new Exception('Not Primary');
}
$config['hasync']['syncitems'] = 'aliases,rules,kea,dnsforwarder';
write_config('SOC M3.6: enable scoped XMLRPC synchronization for rules, Kea and DNS');
echo json_encode(['syncitems' => $config['hasync']['syncitems']]);
?>'''
path = pathlib.Path('/var/tmp/soc-m36-fix-syncitems.php')
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
