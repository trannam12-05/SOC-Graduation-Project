"""Thu duy nhất public-audit.json đã có; không chạy lại backup hoặc sửa XML."""
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib
from topology_console_job import TopologyConsoleJob
from decode_m2_console_transport import ALPHABET, decode

out = Path(sys.argv[1]).resolve()
job = TopologyConsoleJob(out / 'console-transfer-primary-read', 'primary-group2a-public', 'OPNsense-Primary')
path = '/root/soc-group2a-20261102-215617/public-audit.json'
target = '/var/tmp/soc-group2a-public.b64'
code = ('import pathlib,zlib,base64,hashlib,struct; '
        'b=base64.b64encode(zlib.compress(pathlib.Path(' + json.dumps(path) + ').read_bytes())).decode(); '
        'pathlib.Path(' + json.dumps(target) + ').write_text(b); '
        'print(chr(27)+"[2J"+chr(27)+"[H"+' + json.dumps(ALPHABET) + '+chr(10)+'
        'base64.b64encode(struct.pack(">I32s",len(b),hashlib.sha256(b.encode()).digest())).decode())')
p = job.command('python3 -c ' + job.quote(code))
length, expected = struct.unpack('>I32s', base64.b64decode(decode(p, 48), validate=True))
assert 0 < length < 250000
data = ''
for offset in range(0, length, 1440):
    code = ('import pathlib; s=pathlib.Path(' + json.dumps(target) + ').read_text()[' + str(offset) + ':' + str(offset + 1440) + ']; '
            'print(chr(27)+"[2J"+chr(27)+"[H"+' + json.dumps(ALPHABET) + '+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))')
    p = job.command('python3 -c ' + job.quote(code))
    data += decode(p, min(1440, length - offset))
assert hashlib.sha256(data.encode()).digest() == expected
r = json.loads(zlib.decompress(base64.b64decode(data, validate=True)))
r['collector_time'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
r['time_basis'] = 'Windows collector UTC+07:00; guest timestamps untrusted'
r['transport'] = 'Public JSON only; exact glyph decoding and SHA-256 verified'
with (out / 'primary-audit-before.json').open('x', encoding='utf-8') as f:
    json.dump(r, f, ensure_ascii=False, indent=2)
print(json.dumps({'backup_path': r['backup_path'], 'backup_sha256': r['backup_sha256'], 'public_reply_pages': (length + 1439) // 1440, 'output': str(out / 'primary-audit-before.json')}))
