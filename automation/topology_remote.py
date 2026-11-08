"""Transport SSH réutilisable; clés et passphrase restent hors du repository."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SSH = ['ssh.exe', '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
       '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=10',
       '-i', str(Path.home()/'.ssh/eve-ng-root-ed25519'), 'root@192.168.220.143']

def remote(code, timeout=90):
    result = subprocess.run(SSH+['python3', '-'], input=code, text=True,
                            encoding='utf-8', capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout

if __name__ == '__main__':
    import sys
    print(remote(Path(sys.argv[1]).read_text(encoding='utf-8')))
