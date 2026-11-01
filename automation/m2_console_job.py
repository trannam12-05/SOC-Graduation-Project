"""Prepared console adapter. Only invoked by a future explicitly enabled run.

Uses EVE SSH + existing RFB screenshots, not guest networking. Requires a verified
idle shell and sudo -n access. Never accepts credentials. Exact glyph decoding
and SHA-256 are mandatory; an unreadable console blocks instead of guessing.
"""
import base64
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
import zlib
from decode_m2_console_transport import ALPHABET, decode

ROOT = Path(__file__).resolve().parents[1]


class ConsoleJob:
    def __init__(self, directory, session, shell_ready=False):
        if not shell_ready:
            raise RuntimeError('WAIT_CONSOLE: verify login, idle shell and sudo access first')
        if not session or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in session):
            raise ValueError('Unsafe console session name')
        self.directory = Path(directory)
        self.directory.mkdir(parents=True,exist_ok=True)
        self.session = session
        existing=[int(p.stem.split('-')[-1]) for p in self.directory.glob('command-*.txt')]
        self.counter = max(existing,default=0)
        self.remote = '/tmp/m2-bundle-'+session

    def command(self, text):
        self.counter += 1
        path = self.directory/('command-'+str(self.counter).zfill(4)+'.txt')
        path.write_text(text,encoding='utf-8')
        r = subprocess.run([sys.executable,str(ROOT/'automation/capture_m2_core_console.py'),
                            '--output-dir',str(self.directory),'--label','job'+str(self.counter),
                            '--command-file',str(path)],capture_output=True,text=True,encoding='utf-8',timeout=60)
        if r.returncode:
            raise RuntimeError('Console transport failed; inspect saved screenshots, do not retry mutation blindly')
        return Path(json.loads(r.stdout)['image'])

    def stage(self, files):
        payload = json.dumps({name:base64.b64encode(data).decode() for name,data in files.items()}).encode()
        self.payload_sha=hashlib.sha256(payload).hexdigest()
        blob = base64.b64encode(zlib.compress(payload,9)).decode()
        self.command('mkdir '+self.remote)
        for offset in range(0,len(blob),600):
            self.command("printf %s '"+blob[offset:offset+600]+"' >> "+self.remote+'/payload.b64')
        code = ('import base64,zlib,json,pathlib,hashlib; p=pathlib.Path('+repr(self.remote)+'); '
                'raw=zlib.decompress(base64.b64decode((p/"payload.b64").read_bytes())); '
                'assert hashlib.sha256(raw).hexdigest()=='+repr(hashlib.sha256(payload).hexdigest())+'; '
                'd=json.loads(raw); assert all(pathlib.Path(k).name==k for k in d); '
                '[(p/k).write_bytes(base64.b64decode(v)) for k,v in d.items()]; '
                '(p/"stage.ok").write_text('+repr(self.payload_sha)+')')
        self.command('python3 -c '+self.quote(code))

    @staticmethod
    def quote(text):
        return "'"+text.replace("'","'\"'\"'")+"'"

    def run(self, action, work):
        # Launcher has no privileged file reader. Only the root script's stdout
        # and its small public reply cross the console; binary DB stays in guest.
        name = action+'-'+str(self.counter)
        target = self.remote+'/'+name
        args = ['sudo','-n','python3',self.remote+'/guest.py',action,'--work',work]
        launcher = ('import subprocess,json,pathlib,base64,zlib,hashlib,struct; '
                    'assert pathlib.Path('+repr(self.remote+'/stage.ok')+').read_text()=='+repr(self.payload_sha)+'; '
                    'r=subprocess.run('+repr(args)+',capture_output=True,timeout=150); '
                    'd={"rc":r.returncode,"stdout":r.stdout.decode(errors="replace"),'
                    '"stderr":r.stderr.decode(errors="replace")}; '
                    'b=base64.b64encode(zlib.compress(json.dumps(d).encode())).decode(); '
                    'p=pathlib.Path('+repr(target)+'); p.with_suffix(".b64").write_text(b); '
                    'p.with_suffix(".head").write_text(base64.b64encode(struct.pack(">I32si",len(b),hashlib.sha256(b.encode()).digest(),r.returncode)).decode())')
        # Start in background so a slow guest action is not killed by the RFB tool timeout.
        self.command('python3 -c '+self.quote(launcher)+' > '+target+'.launcher.log 2>&1 &')
        header = None
        for attempt in range(25):
            code = 'import pathlib; p=pathlib.Path('+repr(target+'.head')+'); print(chr(27)+"[2J"+chr(27)+"[H"+'+repr(ALPHABET)+'+chr(10)+(p.read_text() if p.exists() else ""))'
            image = self.command('python3 -c '+self.quote(code))
            try:
                raw = base64.b64decode(decode(image,56),validate=True)
                length,digest,rc = struct.unpack('>I32si',raw)
                if not 0 < length < 250000:
                    raise ValueError('Reply length invalid')
                header = (length,digest,rc)
                break
            except (ValueError,AssertionError,struct.error):
                time.sleep(1)
        if header is None:
            raise RuntimeError('Guest job result unavailable; inspect console and launcher log before retry')
        length,digest,rc = header
        data = ''
        for offset in range(0,length,1440):
            count = min(1440,length-offset)
            code = ('import pathlib; s=pathlib.Path('+repr(target+'.b64')+').read_text()['+str(offset)+':'+str(offset+1440)+']; '
                    'print(chr(27)+"[2J"+chr(27)+"[H"+'+repr(ALPHABET)+'+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))')
            data += decode(self.command('python3 -c '+self.quote(code)),count)
        if hashlib.sha256(data.encode()).digest() != digest:
            raise RuntimeError('Console SHA-256 mismatch; reply rejected')
        reply = json.loads(zlib.decompress(base64.b64decode(data)))
        if reply['rc'] != rc:
            raise RuntimeError('Console return-code mismatch')
        path = self.directory/(name+'-verified-reply.json')
        path.write_text(json.dumps(reply,indent=2)+'\n',encoding='utf-8')
        if rc:
            raise RuntimeError('Guest action failed; inspect '+str(path)+' (sudo -n failure requires local authentication, never sudoers changes)')
        return reply
