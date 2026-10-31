"""Đọc các trang base64 từ console thật, xác minh SHA256 rồi mới xuất log."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zlib
from decode_m2_console_transport import decode

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT/'staging/m2-ovs-takeover'
DEST = ROOT/'docs/evidence/M2/console-transfer-20261101'
EXPECTED = 'd064b8dbdecf43a2ed2927ac3d924c6e66c0d88c7f7c3627532bd55d700ca9f2'
LENGTH = 26780

def main():
    start = int(sys.argv[1])
    stop = int(sys.argv[2])
    DEST.mkdir(exist_ok=True)
    for number in range(start,stop):
        offset = number*1440
        cmd = f's=b[{offset}:{offset+1440}]; print("\\033[2J\\033[H"+a+"\\n"+"\\n".join(s[i:i+80] for i in range(0,len(s),80)))'
        command = STAGE/f'page-{number:02d}.txt'
        command.write_text(cmd,encoding='utf-8')
        expected_length = min(1440,LENGTH-offset)
        existing = sorted(DEST.glob(f'log-page-{number:02d}-*.png'))
        if len(sys.argv)>3 and sys.argv[3]=='--reuse' and existing:
            captured = {'image':str(existing[-1])}
        else:
            result = subprocess.run([sys.executable,str(ROOT/'automation/capture_m2_core_console.py'),
                                     '--output-dir',str(DEST),'--label',f'log-page-{number:02d}',
                                     '--command-file',str(command)],capture_output=True,text=True,timeout=55)
            if result.returncode:
                raise RuntimeError(result.stderr)
            captured = json.loads(result.stdout)
        text = decode(Path(captured['image']),expected_length)
        if len(text) != expected_length:
            raise RuntimeError(f'Page {number}: {len(text)} bytes, expected {expected_length}')
        (DEST/f'page-{number:02d}.b64').write_text(text)
        print(f'Page {number}: {len(text)} base64 characters recovered exactly',flush=True)
    if stop == 19:
        blob = ''.join((DEST/f'page-{i:02d}.b64').read_text() for i in range(19)).encode()
        assert len(blob) == LENGTH and hashlib.sha256(blob).hexdigest() == EXPECTED, 'Hash khác guest; không xuất log'
        packed = json.loads(zlib.decompress(base64.b64decode(blob)))
        out = ROOT/'docs/evidence/M2/ovs-offline-guest-20261101'
        out.mkdir(exist_ok=False)
        for name,value in packed.items():
            assert Path(name).name == name
            (out/name).write_bytes(base64.b64decode(value))
        captures = [json.loads(p.read_text()) for p in DEST.glob('log-page-*.json')]
        (out/'transfer-integrity.json').write_text(json.dumps({'base64_length':len(blob),'sha256':EXPECTED,
                    'collector_time_start':min(p['collector_time_start'] for p in captures),
                    'collector_time_end':max(p['collector_time_end'] for p in captures),
                    'verified_against_guest_console':True,'files':list(packed)},indent=2))
        print('Guest logs recovered; SHA256 matches guest console: '+EXPECTED)

if __name__ == '__main__':
    main()
