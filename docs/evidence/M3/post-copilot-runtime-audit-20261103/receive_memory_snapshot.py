import sys,json,struct,base64,zlib,hashlib,concurrent.futures
from pathlib import Path
out=Path(__file__).parent
sys.path.insert(0,str(out));sys.path.insert(0,str(out.resolve().parents[3]/'automation'))
from stage_memory_reader import call
from decode_m2_console_transport import decode
clear='chr(27)+"[2"+chr(74)+chr(27)+"["+chr(72)'
def receive(role):
 info=call(role,'print('+clear+'+alphabet+chr(10)+base64.b64encode(struct.pack(">i32s",len(b),hashlib.sha256(b.encode()).digest())).decode())','snapshot-header')
 header=decode(Path(info['image']),48);length,digest=struct.unpack('>i32s',base64.b64decode(header,validate=True));assert 0<length<50000
 data=''
 for off in range(0,length,1440):
  cmd='s=b['+str(off)+':'+str(off+1440)+'];print('+clear+'+alphabet+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))'
  info=call(role,cmd,'snapshot-page-'+str(off));data+=decode(Path(info['image']),min(1440,length-off))
 assert hashlib.sha256(data.encode()).digest()==digest,'Transport checksum mismatch; do not accept'
 d=json.loads(zlib.decompress(base64.b64decode(data,validate=True)))
 assert d['role']==role.lower(),'Guest identity mismatch'
 d['transport']={'method':'exact console glyph decode with SHA256; no OCR guesses','encoded_sha256':digest.hex(),'encoded_chars':length}
 (out/(role.lower()+'-snapshot.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print(role,'SNAPSHOT_VERIFIED',d['config_sha256'],d['backup_equal'],flush=True)
 call(role,'raise systemexit' if False else 'exitcode=0;raise __import__("builtins").__dict__[bytes.fromhex("53797374656d45786974").decode()](exitcode)','reader-exit')
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(receive,['Primary','Secondary']))
