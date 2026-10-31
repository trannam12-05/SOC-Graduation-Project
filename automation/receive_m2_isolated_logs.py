"""Thu log public từ console thật; chỉ xuất tệp sau khi hash khớp guest.

Không thu bản OVSDB backup raw, private key hoặc dữ liệu xác thực.
"""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import zlib
from decode_m2_console_transport import decode

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'docs/evidence/M2/isolated-bridge-20261101'
STAGE=ROOT/'staging/m2-isolated-20261101'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--length',type=int,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--start',type=int,required=True)
    parser.add_argument('--stop',type=int,required=True)
    parser.add_argument('--reuse',action='store_true')
    o=parser.parse_args()
    dest=EV/'console-transfer';dest.mkdir(exist_ok=True)
    for number in range(o.start,o.stop):
        offset=number*1440;size=min(1440,o.length-offset)
        assert size>0
        cmd=f's=b[{offset}:{offset+1440}]; print("\\033[2J\\033[H"+a+"\\n"+"\\n".join(s[i:i+80] for i in range(0,len(s),80)))'
        command=STAGE/f'log-page-{number:02d}.txt';command.write_text(cmd,encoding='utf-8')
        existing=sorted(dest.glob(f'log-page-{number:02d}-*.png'))
        if o.reuse and existing:path=existing[-1]
        else:
            r=subprocess.run([sys.executable,str(ROOT/'automation/capture_m2_core_console.py'),
                 '--output-dir',str(dest),'--label',f'log-page-{number:02d}',
                 '--command-file',str(command)],capture_output=True,text=True,encoding='utf-8',timeout=55)
            assert r.returncode==0,r.stderr
            path=Path(json.loads(r.stdout)['image'])
        content=decode(path,size)
        assert len(content)==size
        (dest/f'page-{number:02d}.b64').write_text(content,encoding='ascii')
        print(f'Page {number}: {size} characters, exact glyph match',flush=True)
    count=math.ceil(o.length/1440)
    if o.stop==count:
        blob=''.join((dest/f'page-{i:02d}.b64').read_text() for i in range(count)).encode()
        assert len(blob)==o.length and hashlib.sha256(blob).hexdigest()==o.sha256,'Hash mismatch; no extraction'
        files=json.loads(zlib.decompress(base64.b64decode(blob)))
        out=EV/'guest';out.mkdir(exist_ok=False)
        for name,content in files.items():
            assert Path(name).name==name and not name.endswith(('.ovsdb','.before','.backup-validated'))
            (out/name).write_bytes(content.encode('utf-8'))
        captures=[json.loads(p.read_text()) for p in dest.glob('log-page-*.json')]
        metadata={'bytes':len(blob),'sha256':o.sha256,'verified_against_guest_console':True,
          'collector_start':min(p['collector_time_start'] for p in captures),
          'collector_end':max(p['collector_time_end'] for p in captures),'files':list(files)}
        (out/'transfer-integrity.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
        print('Logs extracted; complete SHA256 matches guest',flush=True)

if __name__=='__main__':main()
