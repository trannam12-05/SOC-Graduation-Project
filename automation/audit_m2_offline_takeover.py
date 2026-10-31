"""Đối chiếu bundle hiện có; chỉ đọc nguồn, tạo bằng chứng mới trên Windows."""
import datetime as dt
import hashlib
import json
import lzma
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'staging/soc-core-l2-20261031-stage1'
EV = ROOT / 'docs/evidence/M2'

def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()

def records(text):
    for block in text.split('\n\n'):
        row = {}
        for line in block.splitlines():
            if line and not line[0].isspace() and ': ' in line:
                key, value = line.split(': ', 1)
                row[key] = value
        if 'Package' in row:
            yield row

def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=7)))
    stem = 'M2-ovs-takeover-' + now.strftime('%Y%m%dT%H%M%S%z')
    manifest = json.loads((BUNDLE/'package-manifest.json').read_text(encoding='utf-8'))
    metadata = json.loads((BUNDLE/'metadata-manifest.json').read_text(encoding='utf-8'))
    targets = {(p['Package'], p['Version'], p['Architecture']): p for p in manifest['packages']}
    found = {k: [] for k in targets}
    indexes = []
    for item in metadata['indexes']:
        path = BUNDLE/'mirror'/item['relative']
        actual = digest(path)
        indexes.append({'path': item['relative'], 'sha256': actual, 'matches': actual == item['sha256']})
        for row in records(lzma.decompress(path.read_bytes()).decode()):
            key = (row['Package'], row['Version'], row['Architecture'])
            if key in found:
                ref = targets[key]
                found[key].append({'suite': item['suite'], 'component': item['component'],
                                   'matches': all(row.get(k, '') == ref.get(k, '') for k in ['Filename','Size','SHA256','Depends','Pre-Depends']),
                                   'depends': row.get('Depends', ''), 'pre_depends': row.get('Pre-Depends', '')})
    packages = []
    for key, item in targets.items():
        path = BUNDLE/'mirror'/item['Filename']
        actual = digest(path)
        packages.append({'package': key[0], 'version': key[1], 'architecture': key[2],
                         'filename': item['Filename'], 'sha256': actual,
                         'matches_sha256': actual == item['SHA256'],
                         'matches_size': path.stat().st_size == int(item['Size']),
                         'index_matches': found[key]})
    command = ['ssh.exe','-vv','-o','BatchMode=yes','-o','IdentitiesOnly=yes',
               '-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10',
               '-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143','true']
    result = subprocess.run(command, capture_output=True, text=True, timeout=25)
    ssh_log = EV/(stem+'-ssh.log')
    ssh_log.write_text('Collector time: '+now.isoformat()+'\nCommand: '+' '.join(command)+'\nExit: '+str(result.returncode)+'\n'+result.stdout+result.stderr, encoding='utf-8')
    report = {'collected_at': now.isoformat(), 'time_basis': 'Windows collector, UTC+07:00; EVE clock not used',
              'scope': 'Windows local mirror verification only; no guest commands executed',
              'package_count': len(packages), 'deb_file_count': len(list((BUNDLE/'mirror/pool').rglob('*.deb'))),
              'indexes': indexes, 'packages': packages,
              'all_passed': all(p['matches_sha256'] and p['matches_size'] and p['index_matches'] and all(i['matches'] for i in p['index_matches']) for p in packages) and all(i['matches'] for i in indexes),
              'signature_validation': 'Historical gpgv evidence only; signatures not reverified in this Windows audit',
              'guest_dependency_resolution': 'Not executed: SSH authentication blocked; old empty-status validation is not guest compatibility',
              'ssh_exit_code': result.returncode, 'ssh_log': ssh_log.name,
              'important_finding': 'OVS 3.3.9-0ubuntu0.24.04.1 is in noble-updates/main, absent from noble-only source'}
    output = EV/(stem+'-audit.json')
    with output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps({'audit': str(output), 'ssh_log': str(ssh_log), 'all_passed': report['all_passed'], 'packages': len(packages), 'ssh_exit': result.returncode}))

if __name__ == '__main__':
    main()
