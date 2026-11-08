"""Thu minh chứng qua console đã xác thực; không thay cấu hình hoặc xác thực."""
from pathlib import Path
import base64, datetime, hashlib, json, struct, sys, zlib

ROOT = Path('D:/SOC')
sys.path.insert(0, str(ROOT / 'automation'))
from topology_console_job import TopologyConsoleJob
from decode_m2_console_transport import ALPHABET, decode

out = Path(__file__).resolve().parent
job = TopologyConsoleJob(out / 'readonly-console', 'primary-2b2-readonly', 'OPNsense-Primary')
source = (out / 'collect-rules-readonly.py').read_bytes()
blob = base64.b64encode(zlib.compress(source, 9)).decode()
temp = '/var/tmp/soc-2b2-reader.b64'
try:
    for offset in range(0, len(blob), 500):
        part = blob[offset:offset+500]
        code = 'import pathlib; pathlib.Path(' + repr(temp) + ').open(' + repr('w' if offset == 0 else 'a') + ').write(' + repr(part) + '); print("READER_CHUNK_OK",' + str(offset) + ')'
        job.command('python3 -c ' + job.quote(code))
        print('Reader chunk sent', offset, flush=True)
    code = 'import pathlib,base64,zlib,hashlib; b=pathlib.Path(' + repr(temp) + ').read_text(); assert hashlib.sha256(b.encode()).hexdigest()==' + repr(hashlib.sha256(blob.encode()).hexdigest()) + '; exec(zlib.decompress(base64.b64decode(b)))'
    job.command('python3 -c ' + job.quote(code))
    print('Read-only collector executed', flush=True)
    target = '/var/tmp/soc-2b2-public-rules.b64'
    code = 'import pathlib,hashlib,base64,struct; b=pathlib.Path(' + repr(target) + ').read_bytes(); print(chr(27)+"[2J"+chr(27)+"[H"+' + repr(ALPHABET) + '+chr(10)+base64.b64encode(struct.pack(">I32s",len(b),hashlib.sha256(b).digest())).decode())'
    screen = job.command('python3 -c ' + job.quote(code))
    length, expected = struct.unpack('>I32s', base64.b64decode(decode(screen, 48), validate=True))
    assert 0 < length < 250000
    data = ''
    for offset in range(0, length, 1440):
        code = 'import pathlib; s=pathlib.Path(' + repr(target) + ').read_text()[' + str(offset) + ':' + str(offset+1440) + ']; print(chr(27)+"[2J"+chr(27)+"[H"+' + repr(ALPHABET) + '+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))'
        data += decode(job.command('python3 -c ' + job.quote(code)), min(1440, length-offset))
        print('Verified glyph page', offset, 'of', length, flush=True)
    assert hashlib.sha256(data.encode()).digest() == expected
    result = json.loads(zlib.decompress(base64.b64decode(data, validate=True)))
    result['collector_time'] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
    result['transport'] = 'Exact glyph decoding and complete payload SHA256 verified; public fields only'
    (out / 'firewall-current-public.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'saved': str(out/'firewall-current-public.json'), 'legacy': len(result['legacy_rules']), 'modern': len(result['modern_rules']), 'config_unchanged': result['config_unchanged']}), flush=True)
except Exception as e:
    (out/'readonly-collection-error.json').write_text(json.dumps({'error': str(e), 'action': 'STOP_NO_AUTH_CHANGE', 'collector_time': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()}, indent=2), encoding='utf-8')
    raise
