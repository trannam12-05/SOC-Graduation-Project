import pathlib
import subprocess

def run(args, timeout=90):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    return {'command': ' '.join(args), 'rc': result.returncode,
            'stdout': result.stdout[-5000:], 'stderr': result.stderr[-2000:]}

steps = [run(['/usr/local/sbin/configctl', 'template', 'reload', 'OPNsense/Kea'])]
if steps[-1]['rc'] == 0:
    steps.append(run(['/usr/local/sbin/configctl', 'filter', 'reload']))
if steps[-1]['rc'] == 0:
    steps.append(run(['/usr/local/sbin/configctl', 'dnsmasq', 'restart']))
if steps[-1]['rc'] == 0:
    steps.append(run(['/usr/local/sbin/configctl', 'kea', 'restart']))
steps.append(run(['/usr/local/sbin/configctl', 'kea', 'status']))

config = pathlib.Path('/usr/local/etc/kea/kea-dhcp4.conf')
safe = []
if config.exists():
    for line in config.read_text(errors='replace').splitlines():
        if any(term in line for term in ('this-server-name', '"name"', '"role"', '"url"')):
            safe.append(line.strip())
d = {
    'status': 'DONE' if all(step['rc'] == 0 for step in steps) else 'FAILED',
    'steps': steps,
    'safe_ha_config_lines': safe[-30:],
}
