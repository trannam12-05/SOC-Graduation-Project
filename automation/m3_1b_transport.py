"""Truyền helper công khai và nhận JSON qua glyph/hash; không in secret."""
from pathlib import Path
import argparse,base64,hashlib,json,struct,subprocess,sys,time,zlib
from topology_remote import ROOT
from decode_m2_console_transport import ALPHABET,decode
p=argparse.ArgumentParser();p.add_argument('role',choices=['Primary','Secondary']);p.add_argument('mode',choices=['audit','apply','repair']);p.add_argument('--stage',action='store_true');a=p.parse_args()
OUT=ROOT/'docs/evidence/M3/group1b-prerequisites-20261103'
folder=OUT/('console-'+a.role.lower()+'-'+a.mode);folder.mkdir(exist_ok=True)
def q(t):return "'"+t.replace("'","'\"'\"'")+"'"
def command(t,label):
 f=folder/(label+'.txt');f.write_text(t,encoding='utf-8')
 r=subprocess.run([sys.executable,str(ROOT/'automation/m3_group1_console.py'),'--node','OPNsense-'+a.role,'--output-dir',str(folder),'--label',label,'--command-file',str(f)],capture_output=True,text=True,encoding='utf-8',timeout=65)
 if r.returncode:raise RuntimeError('Console failed; inspect saved image before further actions')
 return Path(json.loads(r.stdout)['image'])
source=(ROOT/'automation/m3_1b_guest.py').read_bytes();blob=base64.b64encode(zlib.compress(source,9)).decode();target='/var/tmp/soc-m3-1b-reader.b64'
if a.stage:
 for off in range(0,len(blob),450):
  c='import pathlib;pathlib.Path('+repr(target)+').open('+repr('w' if off==0 else 'a')+').write('+repr(blob[off:off+450])+');print("CHUNK",'+str(off)+')'
  command('python3 -c '+q(c),'stage-'+str(off));print(a.role,'staged',off,'of',len(blob),flush=True)
args=['reader',a.role,a.mode]
if a.mode=='apply':
 sys.path.insert(0,str(ROOT/'automation'))
 from m3_1b_secret import prepare_cipher
 cipher,challenge,expected=prepare_cipher(a.role)
 args.extend([cipher,challenge])
argfile=None
if a.mode=='apply':
 argfile='/var/tmp/soc-m3-1b-'+a.role.lower()+'-apply.json'
 c='import pathlib;pathlib.Path('+repr(argfile)+').write_text('+repr(json.dumps(args))+');print("CIPHER_ARGS_STAGED")'
 command('python3 -c '+q(c),'cipher-args')
argv=('__import__("json").loads(pathlib.Path('+repr(argfile)+').read_text())') if argfile else repr(args)
c='import pathlib,sys,zlib,base64,hashlib;b=pathlib.Path('+repr(target)+').read_text();assert hashlib.sha256(b.encode()).hexdigest()=='+repr(hashlib.sha256(blob.encode()).hexdigest())+';sys.argv='+argv+';exec(zlib.decompress(base64.b64decode(b)))'
if a.mode=='repair':
 fix='''import pathlib,json,hashlib,subprocess,base64,zlib
w=pathlib.Path('/root/soc-m3-1b-ROLE-20261103');p=pathlib.Path('/conf/config.xml');h=lambda b:hashlib.sha256(b).hexdigest();before=p.read_bytes();audit=json.loads((w/'audit.json').read_text());assert h(before)==audit['backup_sha256'];secret=w/'carp-shared.secret';hs=h(secret.read_bytes())
assert '/usr/local/sbin/pluginctl -c pfsync' in audit['native_action']
r=subprocess.run(['/usr/local/sbin/pluginctl','-c','pfsync'],capture_output=True,text=True,timeout=25);s=subprocess.run(['ifconfig','pfsync0'],capture_output=True,text=True,timeout=15);after=p.read_bytes();assert before==after and hs==h(secret.read_bytes())
peer=audit['sync']['peer'];ready=r.returncode==0 and 'UP' in s.stdout.splitlines()[0] and 'syncdev: vtnet2' in s.stdout and ('syncpeer: '+peer) in s.stdout
d={'role':'ROLECASE','mode':'repair','native_command':'/usr/local/sbin/pluginctl -c pfsync','native_apply':{'rc':r.returncode,'stdout':r.stdout,'stderr':r.stderr},'runtime_after':{'rc':s.returncode,'stdout':s.stdout,'stderr':s.stderr},'runtime_ready':ready,'config_unchanged':True,'config_sha256_before':h(before),'config_sha256_after':h(after),'secret_file_unchanged':True,'secret_mode':oct(secret.stat().st_mode&0o777),'CARP_VIPs_created':0}
(w/'repair.json').write_text(json.dumps(d));(w/'reply.b64').write_text(base64.b64encode(zlib.compress(json.dumps(d).encode(),9)).decode());print('PFSYNC_RUNTIME_READY',ready);print(s.stdout);print('CONFIG_UNCHANGED',h(after))
'''.replace('ROLECASE',a.role).replace('ROLE',a.role.lower())
 encoded=base64.b64encode(zlib.compress(fix.encode(),9)).decode()
 # Dùng tệp lệnh ngắn đã có checksum nguồn; payload lớn chia nhỏ để tránh thiếu ký tự console.
 stage='/var/tmp/soc-m3-1b-native-repair.b64'
 for off in range(0,len(encoded),450):
  chunk=encoded[off:off+450]
  code='import pathlib;pathlib.Path('+repr(stage)+').open('+repr('w' if off==0 else 'a')+').write('+repr(chunk)+');print("REPAIR_CHUNK",'+str(off)+')'
  command('python3 -c '+q(code),'repair-chunk-'+str(off))
 c='import pathlib,hashlib,zlib,base64;b=pathlib.Path('+repr(stage)+').read_bytes();assert hashlib.sha256(b).hexdigest()=='+repr(hashlib.sha256(encoded.encode()).hexdigest())+';exec(zlib.decompress(base64.b64decode(b)))'
command('python3 -c '+q(c),'execute-'+a.mode);print(a.role,a.mode,'invoked',flush=True)
reply='/root/soc-m3-1b-'+a.role.lower()+'-20261103/reply.b64'
def page(c,label,count):
 screen=command('python3 -c '+q(c),label)
 time.sleep(2)
 r=subprocess.run([sys.executable,str(ROOT/'automation/m3_group1_console.py'),'--node','OPNsense-'+a.role,'--output-dir',str(folder),'--label',label+'-stable'],capture_output=True,text=True,encoding='utf-8',timeout=30)
 if r.returncode:raise RuntimeError('Read-only screenshot failed')
 return decode(Path(json.loads(r.stdout)['image']),count)
c='import pathlib,struct,hashlib,base64;b=pathlib.Path('+repr(reply)+').read_bytes();print(chr(27)+"[2J"+chr(27)+"[H"+'+repr(ALPHABET)+'+chr(10)+base64.b64encode(struct.pack(">I32s",len(b),hashlib.sha256(b).digest())).decode())'
n,digest=struct.unpack('>I32s',base64.b64decode(page(c,'header',48),validate=True));assert 0<n<250000
data=''
for off in range(0,n,1440):
 c='import pathlib;s=pathlib.Path('+repr(reply)+').read_text()['+str(off)+':'+str(off+1440)+'];print(chr(27)+"[2J"+chr(27)+"[H"+'+repr(ALPHABET)+'+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))'
 data+=page(c,'page-'+str(off),min(1440,n-off));print(a.role,'received',off,'of',n,flush=True)
assert hashlib.sha256(data.encode()).digest()==digest
d=json.loads(zlib.decompress(base64.b64decode(data,validate=True)))
if a.mode=='apply':
 assert d.pop('secret_attestation')==expected,'Secret equality check failed'
 d['same_shared_secret_verified']=True
import datetime
d['collector_time']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
(OUT/(a.role.lower()+'-'+a.mode+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'role':a.role,'mode':a.mode,'config_unchanged':d['config_unchanged'],'runtime_ready':d.get('runtime_ready'),'VIP_reference_count':len(d.get('VIP_references',[]))},ensure_ascii=False),flush=True)
