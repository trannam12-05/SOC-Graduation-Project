import json
import pathlib
import subprocess

code = r'''<?php
require_once('/usr/local/etc/inc/plugins.inc');
echo json_encode(plugins_xmlrpc_sync(), JSON_PRETTY_PRINT);
?>'''
path = pathlib.Path('/var/tmp/soc-m36-sync-map.php')
path.write_text(code)
path.chmod(0o600)
result = subprocess.run(['/usr/local/bin/php', str(path)], capture_output=True,
                        text=True, timeout=30)
d = {
    'rc': result.returncode,
    'mapping': json.loads(result.stdout) if result.returncode == 0 else None,
    'stderr': result.stderr[-1000:],
}
