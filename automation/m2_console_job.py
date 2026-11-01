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


class ConsoleTransportError(RuntimeError):
    """Guest command outcome is unknown: inspect before any configuration rollback."""


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
        self.remote = '/var/tmp/m2-bundle-'+session

    def command(self, text):
        self.counter += 1
        path = self.directory/('command-'+str(self.counter).zfill(4)+'.txt')
        path.write_text(text,encoding='utf-8')
        r = subprocess.run([sys.executable,str(ROOT/'automation/capture_m2_core_console.py'),
                            '--output-dir',str(self.directory),'--label','job'+str(self.counter),
                            '--command-file',str(path)],capture_output=True,text=True,encoding='utf-8',timeout=60)
        if r.returncode:
            raise ConsoleTransportError('Console transport failed; inspect saved screenshots, do not retry mutation blindly')
        return Path(json.loads(r.stdout)['image'])

    def stage(self, files):
        # All bundle members are UTF-8 source text. Compress their text directly;
        # base64-wrapping every member first needlessly doubles console typing.
        payload = json.dumps({name:data.decode('utf-8') for name,data in files.items()}).encode()
        self.payload_sha=hashlib.sha256(payload).hexdigest()
        blob = base64.b64encode(zlib.compress(payload,9)).decode()
        self.command('mkdir '+self.remote)
        count=0
        for offset in range(0,len(blob),600):
            chunk=blob[offset:offset+600];target=self.remote+'/part-'+format(count,'02d')+'.b64';count+=1
            expected=hashlib.sha256(chunk.encode()).hexdigest()
            for attempt in range(3):
                command="printf %s '"+chunk+"' > "+target+"; printf '\\033[2J\\033[H"+ALPHABET+"\\n'; sha256sum "+target
                image=self.command(command)
                try:actual=decode(image,64)
                except (ValueError,AssertionError) as exc:
                    raise ConsoleTransportError('Chunk hash screen unreadable; cancel unfinished input before retry') from exc
                if actual==expected:break
            else:raise ConsoleTransportError('Console chunk checksum mismatch after three bounded attempts')
        code = ('import base64,zlib,json,pathlib,hashlib; p=pathlib.Path('+json.dumps(self.remote)+'); '
                'b=b"".join((p/("part-%02d.b64"%i)).read_bytes() for i in range('+str(count)+')); '
                'raw=zlib.decompress(base64.b64decode(b)); '
                'assert hashlib.sha256(raw).hexdigest()=='+json.dumps(self.payload_sha)+'; '
                'd=json.loads(raw); assert all(pathlib.Path(k).name==k for k in d); '
                '[(p/k).write_bytes(v.encode("utf-8")) for k,v in d.items()]; '
                '(p/"stage.ok").write_text('+json.dumps(self.payload_sha)+'); '
                'print(chr(27)+"[2J"+chr(27)+"[H"+'+json.dumps(ALPHABET)+'+chr(10)+hashlib.sha256(raw).hexdigest())')
        image=self.command('python3 -c '+self.quote(code))
        try:actual=decode(image,64)
        except (ValueError,AssertionError) as exc:raise ConsoleTransportError('Bundle unpack acknowledgment unreadable; no guest job started') from exc
        if actual!=self.payload_sha:raise ConsoleTransportError('Whole bundle acknowledgment checksum mismatch')

    def reuse(self, files):
        """Read-only cache probe; accept only exact source hashes on guest."""
        payload=json.dumps({name:data.decode('utf-8') for name,data in files.items()}).encode()
        self.payload_sha=hashlib.sha256(payload).hexdigest()
        expected={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}
        token=base64.b64encode(bytes.fromhex(self.payload_sha)).decode()
        code=('import pathlib,hashlib; p=pathlib.Path('+json.dumps(self.remote)+'); h='+json.dumps(expected)+'; '
              'ok=(p/"stage.ok").is_file() and (p/"stage.ok").read_text()=='+json.dumps(self.payload_sha)+' and '
              'all((p/k).is_file() and hashlib.sha256((p/k).read_bytes()).hexdigest()==v for k,v in h.items()); '
              'print(chr(27)+"[2J"+chr(27)+"[H"+'+json.dumps(ALPHABET)+'+chr(10)+('+json.dumps(token)+' if ok else "A"*44))')
        image=self.command('python3 -c '+self.quote(code))
        return decode(image,44)==token

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
                    'assert pathlib.Path('+json.dumps(self.remote+'/stage.ok')+').read_text()=='+json.dumps(self.payload_sha)+'; '
                    'r=subprocess.run('+json.dumps(args)+',capture_output=True,timeout=150); '
                    'd={"rc":r.returncode,"stdout":r.stdout.decode(errors="replace"),'
                    '"stderr":r.stderr.decode(errors="replace")}; '
                    'b=base64.b64encode(zlib.compress(json.dumps(d).encode())).decode(); '
                    'p=pathlib.Path('+json.dumps(target)+'); p.with_suffix(".b64").write_text(b); '
                    'p.with_suffix(".head").write_text(base64.b64encode(struct.pack(">I32si",len(b),hashlib.sha256(b.encode()).digest(),r.returncode)).decode())')
        # Start in background so a slow guest action is not killed by the RFB tool timeout.
        self.command('python3 -c '+self.quote(launcher)+' > '+target+'.launcher.log 2>&1 &')
        header = None
        for attempt in range(5):
            code = 'import pathlib; p=pathlib.Path('+json.dumps(target+'.head')+'); print(chr(27)+"[2J"+chr(27)+"[H"+'+json.dumps(ALPHABET)+'+chr(10)+(p.read_text() if p.exists() else ""))'
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
            raise ConsoleTransportError('Guest job result unavailable; inspect console and launcher log before retry')
        length,digest,rc = header
        data = ''
        for offset in range(0,length,1440):
            count = min(1440,length-offset)
            code = ('import pathlib; s=pathlib.Path('+json.dumps(target+'.b64')+').read_text()['+str(offset)+':'+str(offset+1440)+']; '
                    'print(chr(27)+"[2J"+chr(27)+"[H"+'+json.dumps(ALPHABET)+'+chr(10)+chr(10).join(s[i:i+80] for i in range(0,len(s),80)))')
            try:data += decode(self.command('python3 -c '+self.quote(code)),count)
            except (ValueError,AssertionError) as exc:raise ConsoleTransportError('Reply page glyph mismatch; no automatic configuration retry') from exc
        if hashlib.sha256(data.encode()).digest() != digest:
            raise ConsoleTransportError('Console SHA-256 mismatch; reply rejected')
        reply = json.loads(zlib.decompress(base64.b64decode(data)))
        if reply['rc'] != rc:
            raise RuntimeError('Console return-code mismatch')
        path = self.directory/(name+'-verified-reply.json')
        path.write_text(json.dumps(reply,indent=2)+'\n',encoding='utf-8')
        if rc:
            raise RuntimeError('Guest action failed; inspect '+str(path)+' (sudo -n failure requires local authentication, never sudoers changes)')
        return reply
