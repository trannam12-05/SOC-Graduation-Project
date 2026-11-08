"""Đưa reader không chứa secret vào console đã xác thực; xuất backup mã hóa."""
from pathlib import Path
import argparse,base64,hashlib,json,subprocess,sys,zlib
from topology_remote import ROOT,remote
OUT=ROOT/'docs/evidence/M3/group1-carp-readiness-20261103'
p=argparse.ArgumentParser();p.add_argument('role',choices=['Primary','Secondary']);p.add_argument('--collect-only',action='store_true');p.add_argument('--attempt',default='v2');a=p.parse_args()
directory=OUT/('console-backup-'+a.role.lower()+'-'+a.attempt);directory.mkdir(exist_ok=True)
def quote(t):return "'"+t.replace("'","'\"'\"'")+"'"
def command(text,label):
 file=directory/(label+'.txt');file.write_text(text,encoding='utf-8')
 proc=subprocess.run([sys.executable,str(ROOT/'automation/m3_group1_console.py'),'--node','OPNsense-'+a.role,'--output-dir',str(directory),'--label',label,'--command-file',str(file)],capture_output=True,text=True,encoding='utf-8',timeout=65)
 if proc.returncode:raise RuntimeError('Console action failed; inspect saved screen before further action: '+proc.stderr)
 return json.loads(proc.stdout)
if not a.collect_only:
 source=(ROOT/'automation/m3_group1_backup_guest.py').read_text(encoding='utf-8').replace('__ROLE__',a.role).replace('__PUBLIC_DER__',base64.b64encode((OUT/'transport-public.der').read_bytes()).decode())
 blob=base64.b64encode(zlib.compress(source.encode(),9)).decode();target='/var/tmp/soc-m3-group1-'+a.role.lower()+'-'+a.attempt+'.b64'
 for offset in range(0,len(blob),450):
  code='import pathlib;pathlib.Path('+repr(target)+').open('+repr('w' if offset==0 else 'a')+').write('+repr(blob[offset:offset+450])+');print("CHUNK",'+str(offset)+')'
  command('python3 -c '+quote(code),'chunk-'+str(offset));print(a.role,'staged',offset,'of',len(blob),flush=True)
 code='import pathlib,hashlib,zlib,base64;b=pathlib.Path('+repr(target)+').read_text();assert hashlib.sha256(b.encode()).hexdigest()=='+repr(hashlib.sha256(blob.encode()).hexdigest())+';exec(zlib.decompress(base64.b64decode(b)))'
 command('python3 -c '+quote(code),'backup-execute');print(a.role,'backup reader invoked',flush=True)
from decode_m2_console_transport import ALPHABET,decode
import struct,time
def public_page(code,label,count):
 info=command('python3 -c '+quote(code),label)
 # Chụp lại sau khi output ổn định; không gửi lại lệnh hoặc chỉnh ảnh.
 time.sleep(2)
 proc=subprocess.run([sys.executable,str(ROOT/'automation/m3_group1_console.py'),'--node','OPNsense-'+a.role,'--output-dir',str(directory),'--label',label+'-stable'],capture_output=True,text=True,encoding='utf-8',timeout=30)
 if proc.returncode:raise RuntimeError('Read-only recapture failed; stop')
 return decode(Path(json.loads(proc.stdout)['image']),count)
target='/root/soc-m3-group1-'+a.role.lower()+'-20261103/transfer.b64'
code='import pathlib,hashlib,base64,struct;b=pathlib.Path('+repr(target)+').read_bytes();print(chr(27)+"[2J"+chr(27)+"[H"+'+repr(ALPHABET)+'+chr(10)+base64.b64encode(struct.pack(">I32s",len(b),hashlib.sha256(b).digest())).decode())'
length,expected=struct.unpack('>I32s',base64.b64decode(public_page(code,'header',48),validate=True))
assert 0<length<250000
text=''
for offset in range(0,length,1440):
 code='import pathlib;s=pathlib.Path('+repr(target)+').read_text()['+str(offset)+':'+str(offset+1440)+'];print(chr(27)+"[2J"+chr(27)+"[H"+'+repr(ALPHABET)+'+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))'
 text+=public_page(code,'page-'+str(offset),min(1440,length-offset));print(a.role,'verified page',offset,'of',length,flush=True)
assert hashlib.sha256(text.encode()).digest()==expected
d=json.loads(zlib.decompress(base64.b64decode(text,validate=True)));audit=d['audit'];private=OUT/'private-backups'
cipher=private/(a.role+'-config.enc');wrapped=private/(a.role+'-transport-pass.enc');password=private/(a.role+'-transport-pass.key');compressed=private/(a.role+'-config.compressed');xml=private/(a.role+'-config.xml')
for f,b in [(cipher,base64.b64decode(d['ciphertext_b64'],validate=True)),(wrapped,base64.b64decode(d['wrapped_passphrase_b64'],validate=True))]:
 if f.exists():assert f.read_bytes()==b
 else:f.write_bytes(b)
assert hashlib.sha256(cipher.read_bytes()).hexdigest()==d['ciphertext_sha256']
for f in [cipher,wrapped,password,compressed,xml]:
 proc=subprocess.run(['git','check-ignore','--',str(f.relative_to(ROOT)).replace('\\','/')],cwd=ROOT,capture_output=True)
 assert proc.returncode==0,'Private backup must be Git ignored'
ssl=r'C:\Program Files\Git\usr\bin\openssl.exe'
for cmd in [[ssl,'pkeyutl','-decrypt','-inkey',str(private/'transport-private.key'),'-in',str(wrapped),'-out',str(password),'-pkeyopt','rsa_padding_mode:oaep','-pkeyopt','rsa_oaep_md:sha256'],
 [ssl,'enc','-d','-aes-256-cbc','-pbkdf2','-iter','100000','-pass','file:'+str(password),'-in',str(cipher),'-out',str(compressed)]]:
 proc=subprocess.run(cmd,capture_output=True);assert proc.returncode==0,'Private backup decryption failed; do not print secrets'
raw=zlib.decompress(compressed.read_bytes());assert hashlib.sha256(raw).hexdigest()==audit['backup_sha256'] and len(raw)==audit['backup_bytes']
if xml.exists():assert xml.read_bytes()==raw
else:xml.write_bytes(raw)
import datetime
audit['collector_time']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat();audit['backup_local']=str(xml.relative_to(ROOT)).replace('\\','/');audit['local_sha256']=hashlib.sha256(xml.read_bytes()).hexdigest();audit['local_decryption_and_hash_verified']=True
(OUT/(a.role.lower()+'-audit.json')).write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
(private/(a.role+'-config.xml.sha256')).write_text(audit['backup_sha256']+'  '+xml.name+'\n',encoding='ascii')
print(json.dumps({'role':a.role,'backup':str(xml),'sha256':audit['backup_sha256'],'bytes':len(raw),'config_unchanged':audit['config_unchanged'],'local_verified':True}),flush=True)
