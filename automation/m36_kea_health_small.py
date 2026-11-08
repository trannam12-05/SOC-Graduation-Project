import pathlib
import subprocess

def run(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=25)
    return {'rc': p.returncode, 'stdout': p.stdout[-2500:], 'stderr': p.stderr[-800:]}

config = pathlib.Path('/usr/local/etc/kea/kea-dhcp4.conf').read_text(errors='replace')
identity = [line.strip() for line in config.splitlines()
            if 'this-server-name' in line or 'http:\\/\\/10.255.255.' in line]
sock = run(['/usr/bin/sockstat', '-4', '-l'])
listeners = [line for line in sock['stdout'].splitlines()
             if ':67 ' in line or ':8000 ' in line or ':8001 ' in line]
d = {
    'hostname': run(['/bin/hostname'])['stdout'].strip(),
    'kea_status': run(['/usr/local/sbin/configctl', 'kea', 'status']),
    'identity': identity,
    'listeners': listeners,
}
