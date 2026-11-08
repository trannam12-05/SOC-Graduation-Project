import pathlib
import subprocess

def run(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return {'rc': result.returncode, 'stdout': result.stdout[-8000:],
            'stderr': result.stderr[-2000:]}

config = pathlib.Path('/usr/local/etc/kea/kea-dhcp4.conf')
text = config.read_text() if config.exists() else ''
safe_lines = [line for line in text.splitlines() if any(term in line for term in (
    'this-server-name', 'name', 'role', 'url', 'mode', 'heartbeat-delay',
    'max-response-delay', 'max-unacked-clients'))]
logs = []
for path in sorted(pathlib.Path('/var/log/kea').glob('*.log')):
    content = path.read_text(errors='replace').splitlines()
    relevant = [line for line in content if any(term in line.lower() for term in
                ('error', 'fail', 'high availability', 'ha service', 'hook'))]
    logs.extend(relevant[-40:])
d = {
    'hostname': run(['/bin/hostname']),
    'kea_status': run(['/usr/local/sbin/configctl', 'kea', 'status']),
    'safe_ha_config_lines': safe_lines[-100:],
    'kea_relevant_log_lines': logs[-100:],
    'listeners': run(['/usr/bin/sockstat', '-4', '-l']),
}
