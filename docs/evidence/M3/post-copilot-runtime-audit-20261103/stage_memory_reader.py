import sys,subprocess,json,hashlib,concurrent.futures
from pathlib import Path
out=Path(__file__).parent
payload=(out/'guest_readonly_payload.py').read_text(encoding='utf-8-sig').encode()
hexdata=payload.hex()
def call(role,cmd,label):
 f=out/(role.lower()+'-'+label+'-command.txt');f.write_text(cmd,encoding='ascii')
 r=subprocess.run([sys.executable,str(out/'readonly_console_collect.py'),'--node',role,'--label',role.lower()+'-'+label,'--command-file',str(f),'--stdin-mode'],capture_output=True,text=True,encoding='utf-8',timeout=250)
 if r.returncode: raise RuntimeError(r.stderr[-1000:])
 info=json.loads(r.stdout); print(role,label,info['image'],flush=True);return info

def stage(role):
 for off in range(0,len(hexdata),400):
  c=('h=' if off==0 else 'h+=')+repr(hexdata[off:off+400]);call(role,c,'memory-chunk-'+str(off))
 call(role,'assert __import__("hashlib").sha256(bytes.fromhex(h)).hexdigest()=='+repr(hashlib.sha256(payload).hexdigest())+';exec(bytes.fromhex(h))','snapshot-ready')
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  list(pool.map(stage,['Primary','Secondary']))
