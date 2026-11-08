"""Đọc lại tệp minh chứng công khai đã tạo; không chạy lại collector hoặc sửa xác thực."""
from pathlib import Path
import base64, datetime, hashlib, json, struct, subprocess, sys, time, zlib
root = Path('D:/SOC')
sys.path.insert(0, str(root/'automation'))
from topology_console_job import TopologyConsoleJob
from decode_m2_console_transport import ALPHABET, decode
out = Path(__file__).resolve().parent
job = TopologyConsoleJob(out/'readonly-console', 'primary-2b2-readonly', 'OPNsense-Primary')
target = '/var/tmp/soc-2b2-public-rules.b64'

def observe(label):
    time.sleep(3)
    p = subprocess.run([sys.executable, str(root/'automation/capture_m3_primary_readonly.py'), '--output-dir',str(out/'readonly-console'),'--label',label], capture_output=True, text=True, encoding='utf-8', timeout=30)
    if p.returncode:
        raise RuntimeError('READ_ONLY_ACCESS_ERROR_STOP: '+p.stderr)
    return Path(json.loads(p.stdout)['image'])

# Header was already decoded successfully before the stale first-page image.
header = sorted((out/'readonly-console').glob('job7-*.png'))[-1]
length, expected = struct.unpack('>I32s',base64.b64decode(decode(header,48),validate=True))
data = decode(out/'readonly-page-observe-20261103T164519+0700.png',1440)
print('First page recovered from later unmodified screenshot', flush=True)
for offset in range(1440,length,1440):
    code='import pathlib; s=pathlib.Path('+repr(target)+').read_text()['+str(offset)+':'+str(offset+1440)+']; print(chr(27)+"[2J"+chr(27)+"[H"+'+repr(ALPHABET)+'+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))'
    screen=job.command('python3 -c '+job.quote(code))
    # Đợi khung console mới; chỉ chụp lại, không gửi lại lệnh nếu ảnh cũ.
    screen=observe('public-page-'+str(offset))
    data+=decode(screen,min(1440,length-offset))
    print('Decoded page',offset,'of',length,flush=True)
assert hashlib.sha256(data.encode()).digest()==expected,'Payload SHA mismatch; reject result'
d=json.loads(zlib.decompress(base64.b64decode(data,validate=True)))
d['collector_time']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
d['transport']='Exact glyph and complete SHA256 verified; first stale image retained; later real screenshot used without editing'
(out/'firewall-current-public.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'saved':str(out/'firewall-current-public.json'),'legacy':len(d['legacy_rules']),'modern':len(d['modern_rules']),'config_unchanged':d['config_unchanged']}),flush=True)
