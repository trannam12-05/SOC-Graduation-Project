"""Cancel observed unfinished root shell input with Ctrl+C; never reset a VM."""
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from capture_m2_core_console import REMOTE


def main():
    injection='''    for modifier in [0xffe1,0xffe2,0xffe3,0xffe4,0xffe9,0xffea]:
        sock.sendall(struct.pack('>BBHI',4,0,0,modifier))
        time.sleep(0.05)
    sock.sendall(struct.pack('>BBHI',4,1,0,0xffe3))
    time.sleep(0.1)
    sock.sendall(struct.pack('>BBHI',4,1,0,ord('c')))
    time.sleep(0.1)
    sock.sendall(struct.pack('>BBHI',4,0,0,ord('c')))
    sock.sendall(struct.pack('>BBHI',4,0,0,0xffe3))
    time.sleep(1)
    facts['control_sent']='Ctrl+C at confirmed unfinished shell input; controller stopped first'
    if check or custom_command:
'''
    code=REMOTE.replace('__CHECK__','None').replace('__CUSTOM_COMMAND__','None').replace('    if check or custom_command:\n',injection)
    cmd=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10',
         '-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143','python3','-']
    r=subprocess.run(cmd,input=code,capture_output=True,text=True,encoding='utf-8',timeout=30)
    assert r.returncode==0,r.stderr
    data=json.loads(r.stdout);now=dt.datetime.now(dt.timezone(dt.timedelta(hours=7)))
    png=base64.b64decode(data['capture'].pop('png_base64'));data['collector_time']=now.isoformat()
    data['capture']['sha256']=hashlib.sha256(png).hexdigest()
    out=Path('docs/evidence/M2/live-tests-20261101')/('console-line-cancel-'+now.strftime('%H%M%S'))
    with out.with_suffix('.png').open('xb') as f:f.write(png)
    with out.with_suffix('.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
    print(out.with_suffix('.png'))


if __name__=='__main__':main()
