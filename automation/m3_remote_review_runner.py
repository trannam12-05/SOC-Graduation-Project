import base64,json,io,contextlib,tempfile,pathlib,zlib,struct,hashlib,datetime
bundle=json.loads(base64.b64decode(BUNDLE))
cap=bundle['capture'].split("REMOTE = r'''",1)[1].split("'''",1)[0]
cap=cap.replace("key = ord(char)","key = ord(shifted.get(char, char.lower() if char.isupper() else char))")
decoder={ '__name__':'decoder'};exec(bundle['decoder'],decoder)
images=[]
def capture(node,command,label):
 code=cap.replace("n.get('name') == 'SOC-Core-L2'","n.get('name') == "+repr(node)).replace('__CHECK__','None').replace('__CUSTOM_COMMAND__',repr(command))
 if label.endswith('-execute'):code=code.replace('time.sleep(3)', 'time.sleep('+str(bundle.get('execute_wait',3))+')')
 out=io.StringIO()
 with contextlib.redirect_stdout(out):exec(code,{})
 f=json.loads(out.getvalue());images.append({'label':label,'facts':f})
 return f
def pycmd(s):return "python3 -c 'import zlib;exec(zlib.decompress(bytes.fromhex(\""+zlib.compress(s.encode(),9).hex()+"\")))'"
def decode(f,size):
 with tempfile.TemporaryDirectory() as tmp:
  p=pathlib.Path(tmp)/'screen.png';p.write_bytes(base64.b64decode(f['capture']['png_base64']));return decoder['decode'](p,size)
results={}
for node in bundle['nodes']:
 capture(node,bundle.get('status_command'),node+('-status' if bundle.get('status_command') else '-before'))
 # The caller inspects the initial screenshot before sending commands.
 if bundle.get('capture_only'):continue
 path='/var/tmp/soc-m3-readonly-review.b64'
 s=bundle['payload']+"\nimport json,zlib,base64,pathlib\npathlib.Path("+repr(path)+").write_bytes(base64.b64encode(zlib.compress(json.dumps(d).encode(),9)))"
 capture(node,pycmd(s),node+'-execute')
 alphabet=decoder['ALPHABET']
 prefix="import pathlib,base64,struct,hashlib;b=pathlib.Path("+repr(path)+").read_bytes();print(chr(27)+'[2J'+chr(27)+'[H'+"+repr(alphabet)+"+chr(10)+"
 f=capture(node,pycmd(prefix+"base64.b64encode(struct.pack('>I32s',len(b),hashlib.sha256(b).digest())).decode())"),node+'-header')
 length,digest=struct.unpack('>I32s',base64.b64decode(decode(f,48)));assert 0<length<50000
 data=''
 for offset in range(0,length,1440):
  s="import pathlib;s=pathlib.Path("+repr(path)+").read_text()["+str(offset)+":"+str(offset+1440)+"];print(chr(27)+'[2J'+chr(27)+'[H'+"+repr(alphabet)+"+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))"
  f=capture(node,pycmd(s),node+'-page-'+str(offset));data+=decode(f,min(1440,length-offset))
 assert hashlib.sha256(data.encode()).digest()==digest
 results[node]=json.loads(zlib.decompress(base64.b64decode(data)))
print(json.dumps({'results':results,'images':images}))
