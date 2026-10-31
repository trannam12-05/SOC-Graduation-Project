"""Chi chay tu terminal SSH co TTY; mat khau nhap getpass, khong qua chat/log.

Chi tao seed ISO moi cho Core dang tat; khong start guest hay cai package.
"""
import base64
import datetime as dt
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

ROOT=Path('/opt/unetlab/soc-core-preparation-20261031')
TARGET=Path('/opt/unetlab/addons/qemu/linux-ubuntu-24.04-soc-core-l2')
ISO=TARGET/'cdrom.iso'

def main():
    if not sys.stdin.isatty(): raise RuntimeError('Require an interactive terminal; never enter password through automation output')
    if ISO.exists(): raise FileExistsError('Core seed ISO exists; refuse replacement')
    state=json.loads((ROOT/'core-created-stopped.json').read_text())
    assert state['status']==0 and len(state['interfaces'])==8
    if (ROOT/'secrets').exists(): raise FileExistsError('Protected seed input exists; inspect completion state before retry')
    print('SOC Core L2 seed preparation. Core will remain OFF and unconnected.')
    print('Enter the NEW soc-core-admin console password below, not in chat.')
    while True:
        first=getpass.getpass('New console password (at least 12 characters): ')
        second=getpass.getpass('Repeat console password: ')
        if first==second and len(first)>=12: break
        print('Passwords must match and contain at least 12 characters. Try again.')
    result=subprocess.run(['openssl','passwd','-6','-stdin'],input=(first+'\n').encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    del first,second
    password_hash=result.stdout.decode().strip()
    if not re.fullmatch(r'\$6\$[^$]+\$[./0-9A-Za-z]+',password_hash): raise RuntimeError('Unexpected password hash format')
    secret=ROOT/'secrets'; secret.mkdir(mode=0o700)
    seed=secret/'seed-input'; seed.mkdir(mode=0o700)
    public=[]
    for line in Path('/root/.ssh/authorized_keys').read_text().splitlines():
        parts=line.strip().split()
        if len(parts)>1 and parts[0]=='ssh-ed25519':
            fingerprint='SHA256:'+base64.b64encode(hashlib.sha256(base64.b64decode(parts[1])).digest()).decode().rstrip('=')
            if fingerprint=='SHA256:NmKKtOy8jUJd/x2Zg9xzrdGLCRAHCFfdNejRnrJ+ne4': public.append((parts[0]+' '+parts[1],fingerprint))
    if len(public)!=1: raise RuntimeError('Expected management public key not found uniquely')
    instance='iid-soc-core-l2-'+str(uuid.uuid4())
    user_data='''#cloud-config
hostname: soc-core-l2
preserve_hostname: false
disable_root: true
ssh_pwauth: false
users:
  - name: soc-core-admin
    gecos: SOC Core Layer 2 administrator
    shell: /bin/bash
    groups: [adm, sudo]
    lock_passwd: false
    hashed_passwd: __HASH__
    ssh_authorized_keys:
      - __PUBLIC__
'''.replace('__HASH__',password_hash).replace('__PUBLIC__',public[0][0])
    del password_hash,result
    metadata='instance-id: '+instance+'\nlocal-hostname: soc-core-l2\n'
    network=['version: 2','ethernets:']
    for interface in state['interfaces']:
        network+=['  core-port-'+str(interface['id'])+':','    match:','      macaddress: '+interface['mac'],'    dhcp4: false','    dhcp6: false','    accept-ra: false','    optional: true','    link-local: []']
    for name,content in [('user-data',user_data),('meta-data',metadata),('network-config','\n'.join(network)+'\n')]:
        with (seed/name).open('x') as target:target.write(content)
        os.chmod(seed/name,0o600)
    del user_data
    with (ROOT/'password-configured.json').open('x') as target:
        json.dump({'account':'soc-core-admin','password_hash_configured':True,'plaintext_saved':False,'seed_ready':False,'instance_id':instance},target)
    print('Password accepted without logging. Waiting for the verified offline bundle...')
    marker=ROOT/'bundle-ready.json'
    deadline=time.monotonic()+1800
    while not marker.exists():
        if time.monotonic()>deadline: raise RuntimeError('Bundle not ready; protected seed inputs retained, Core remains OFF')
        time.sleep(2)
    bundle=json.loads(marker.read_text())
    path=Path(bundle['bundle'])
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1048576),b''):h.update(part)
    if h.hexdigest()!=bundle['sha256']:raise RuntimeError('Offline bundle hash mismatch; refuse seed')
    os.link(path,seed/path.name)
    # No old seed or template is touched. ISO is a new file, mode 0600 root.
    subprocess.run(['genisoimage','-quiet','-volid','cidata','-joliet','-rock','-o',str(ISO),str(seed)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    os.chmod(ISO,0o600)
    names=subprocess.run(['isoinfo','-R','-i',str(ISO),'-f'],check=True,capture_output=True,text=True).stdout.splitlines()
    if not {'/user-data','/meta-data','/network-config'}.issubset(set(names)):raise RuntimeError('Wrong NoCloud filenames')
    # Validate YAML structure via the already installed PHP YAML extension; no secret output.
    check='''<?php $u=yaml_parse_file($argv[1]); if (!is_array($u) || $u['ssh_pwauth']!==false || $u['users'][0]['name']!=='soc-core-admin' || $u['users'][0]['lock_passwd']!==false || !isset($u['users'][0]['hashed_passwd'])) exit(1); echo "YAML structure OK"; ?>'''
    # Fixed checker only prints a verdict; it never prints secret YAML fields.
    validation=subprocess.run(['php','-r',check.removeprefix('<?php ').removesuffix(' ?>'),str(seed/'user-data')],text=True,capture_output=True)
    if validation.returncode:raise RuntimeError('User-data YAML structure check failed; inspect securely')
    iso_hash=hashlib.sha256(ISO.read_bytes()).hexdigest()
    safe={'created_remote_utc_untrusted':dt.datetime.now(dt.timezone.utc).isoformat(),'account':'soc-core-admin','hostname':'soc-core-l2','instance_id':instance,'seed_path':str(ISO),'seed_sha256':iso_hash,'seed_bytes':ISO.stat().st_size,'mode':oct(ISO.stat().st_mode&0o777),'files':names,'ssh_pwauth':False,'root_login_disabled':True,'lock_passwd':False,'password_hash_configured':True,'plaintext_password_saved':False,'public_key_fingerprint':public[0][1],'network_config':'8 MAC matches, DHCP4/DHCP6/RA off, no addresses; no guest boot','bundle_sha256':bundle['sha256'],'package_count':bundle['package_count'],'yaml_check':'PHP YAML parse, not cloud-init runtime/schema','core_booted':False}
    with (ROOT/'seed-ready.json').open('x') as target:json.dump(safe,target,indent=2)
    print('SEED READY. User-data/meta-data/network-config verified; no secrets printed.')
    print('SOC-Core-L2 is still OFF, 1 CPU / 2048 MiB / 8 unconnected vNICs.')
    print('No OVS package has been installed into the guest. You may close this window.')

if __name__=='__main__':
    try: main()
    except Exception as error:
        print('PREPARATION STOPPED: '+type(error).__name__+'. No old node/image was changed.')
        print('Do not paste a password or hash into chat. Keep this window for review.')
        sys.exit(1)
