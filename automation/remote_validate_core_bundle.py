"""Kiem tra byte/package offline trong staging rieng; khong cai package.

APT --download-only --no-download chi kiem tra closure/cache, status rong.
Khong goi dpkg --install/configure, khong thay host/guest package state.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import urllib.parse
import sys

ROOT=Path('/opt/unetlab/soc-core-preparation-20261031')
SUFFIX='-v2' if '--v2' in sys.argv else ''
marker=json.loads((ROOT/('bundle-ready'+SUFFIX+'.json')).read_text())
BUNDLE=Path(marker['bundle'])
APT=ROOT/'apt-root'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    return h.hexdigest()

before=sha('/var/lib/dpkg/status')
host_sources={str(p):sha(p) for p in Path('/etc/apt').rglob('*') if p.is_file()}
assert sha(BUNDLE)==marker['sha256']
with tarfile.open(BUNDLE) as archive:
    manifest=json.load(archive.extractfile('package-manifest.json'))
    for record in manifest['packages']:
        member='mirror/'+record['Filename']
        dest=ROOT/member
        assert dest.resolve().is_relative_to((ROOT/'mirror/pool').resolve())
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():
            with archive.extractfile(member) as src,dest.open('xb') as out:
                while True:
                    data=src.read(1048576)
                    if not data:break
                    out.write(data)
        assert sha(dest)==record['SHA256']
        control=subprocess.run(['dpkg-deb','--field',str(dest),'Package','Version','Architecture'],capture_output=True,text=True,check=True)
        fields=dict(line.split(': ',1) for line in control.stdout.splitlines())
        assert all(fields[k]==record[k] for k in ['Package','Version','Architecture'])
        assert fields['Architecture'] in ['amd64','all']
uri_rows={}
for line in (ROOT/'apt-print-uris.log').read_text().splitlines():
    match=re.match(r"^'([^']+)' (\S+) (\d+) (\S+)$",line)
    if match:
        relative=urllib.parse.unquote(match.group(1)).split('/mirror/',1)[1]
        uri_rows[relative]=match.group(2)
for record in manifest['packages']:
    source=ROOT/'mirror'/record['Filename']; dest=APT/'cache/archives'/uri_rows[record['Filename']]
    if not dest.exists():os.link(source,dest)
    assert sha(dest)==record['SHA256']
env=dict(os.environ,APT_CONFIG=str(APT/'apt.conf'),LC_ALL='C')
command=['apt-get','--yes','--download-only','--no-download','--no-install-recommends','install','openvswitch-switch']
result=subprocess.run(command,env=env,text=True,capture_output=True,timeout=120)
with (ROOT/('apt-offline-byte-check'+SUFFIX+'.log')).open('x') as target:target.write(result.stdout+result.stderr)
assert result.returncode==0,result.stdout+result.stderr
assert sha('/var/lib/dpkg/status')==before
assert all(sha(p)==h for p,h in host_sources.items())
assert (APT/'status').stat().st_size==0
report={'package_count':len(manifest['packages']),'all_sha256_verified':True,'all_deb_control_package_version_arch_verified':True,'architectures':sorted(set(p['Architecture'] for p in manifest['packages'])),'repository_suites':['noble','noble-updates','noble-security'],'signature_fingerprint':'F6ECB3762474EDA9D21B7022871920D1991BC93C','offline_byte_check_command':command,'offline_byte_check_rc':result.returncode,'offline_byte_check_output':result.stdout,'host_dpkg_status_sha256_before_after':before,'host_apt_configuration_unchanged':True,'isolated_apt_status_still_empty':True,'guest_runtime_compatibility':'Not tested; Core remains OFF. Verify target installed-state simulation/kernel module after approved boot. Do not install all dependency debs indiscriminately.'}
with (ROOT/('bundle-validated'+SUFFIX+'.json')).open('x') as target:json.dump(report,target,indent=2)
print(json.dumps(report))
