"""Truyền lệnh hex chữ thường, thu JSON qua console/font và SHA-256 thực."""
import base64,datetime as dt,hashlib,json,struct,subprocess,sys,zlib
from pathlib import Path
from decode_m2_console_transport import ALPHABET,decode
from topology_remote import ROOT
OUT=ROOT/'docs/evidence/M3/todo-completion-20261103'
def command(node,label,text=None):
 args=[sys.executable,str(ROOT/'automation/m3_resource_console.py'),node,label,'--output-dir',str(OUT)]
 if text is not None:
  p=OUT/(label+'.txt')
  with p.open('x',encoding='ascii') as f:f.write(text)
  args+=['--command-file',str(p)]
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',timeout=260)
 if r.returncode:raise RuntimeError(r.stderr)
 return Path(json.loads(r.stdout)['image'])
def pycmd(code):return "python3 -c 'import zlib;exec(zlib.decompress(bytes.fromhex(\""+zlib.compress(code.encode(),9).hex()+"\")))'"
def run(node,label,source):
 if label.endswith('-carp-apply'):
  assert json.loads((OUT/'M3.1-acceptance.json').read_text(encoding='utf-8'))['status']=='DONE/PASS','M3.1 acceptance required'
 path='/var/tmp/soc-m3-todo-'+label+'.b64'
 wrapper=source+"\nimport base64,zlib,json,pathlib,hashlib\nb=base64.b64encode(zlib.compress(json.dumps(d,separators=(',',':')).encode(),9));pathlib.Path("+repr(path)+").write_bytes(b);print('public_result_ready',len(b),hashlib.sha256(b).hexdigest())\n"
 command(node,label+'-execute',pycmd(wrapper))
 code="import pathlib,base64,struct,hashlib;b=pathlib.Path("+repr(path)+").read_bytes();print(chr(27)+'[2J'+chr(27)+'[H'+"+repr(ALPHABET)+"+chr(10)+base64.b64encode(struct.pack('>I32s',len(b),hashlib.sha256(b).digest())).decode())"
 pic=command(node,label+'-header',pycmd(code));head=decode(pic,48);length,digest=struct.unpack('>I32s',base64.b64decode(head,validate=True));assert 0<length<120000
 data=''
 for off in range(0,length,1440):
  code="import pathlib;s=pathlib.Path("+repr(path)+").read_text()["+str(off)+":"+str(off+1440)+"];print(chr(27)+'[2J'+chr(27)+'[H'+"+repr(ALPHABET)+"+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))"
  pic=command(node,label+'-page-'+str(off),pycmd(code));data+=decode(pic,min(1440,length-off))
 assert hashlib.sha256(data.encode()).digest()==digest
 d=json.loads(zlib.decompress(base64.b64decode(data,validate=True)));d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
 with (OUT/(label+'.json')).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
 return d
if __name__=='__main__':
 node,label,file=sys.argv[1:];d=run(node,label,Path(file).read_text(encoding='utf-8'));print(json.dumps(d,ensure_ascii=False))
