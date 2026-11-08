"""Gửi helper qua console đã xác minh; nguồn có hash, không chứa xác thực."""
import argparse,base64,hashlib,json,subprocess,sys,zlib
from pathlib import Path
from topology_console_job import TopologyConsoleJob
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--node',required=True);p.add_argument('--session',required=True);p.add_argument('--sudo',action='store_true');a=p.parse_args()
out=ROOT/'docs/evidence/M2/final-acceptance-20261103'/('console-'+a.session)
j=TopologyConsoleJob(out,a.session,a.node)
data=base64.b64encode(zlib.compress(Path(a.source).read_bytes(),9)).decode()
target='/var/tmp/'+a.session+'.b64'
for offset in range(0,len(data),500):
 c='import pathlib;pathlib.Path('+repr(target)+').open('+repr('w' if offset==0 else 'a')+').write('+repr(data[offset:offset+500])+');print("CHUNK_OK",'+str(offset)+')'
 j.command('python3 -c '+j.quote(c));print('staged',offset,'of',len(data),flush=True)
c='import pathlib,zlib,base64,hashlib; b=pathlib.Path('+repr(target)+').read_text();assert hashlib.sha256(b.encode()).hexdigest()=='+repr(hashlib.sha256(data.encode()).hexdigest())+';exec(zlib.decompress(base64.b64decode(b)))'
j.command(('sudo -n ' if a.sudo else '')+'python3 -c '+j.quote(c));print('EXECUTED',a.session,flush=True)
