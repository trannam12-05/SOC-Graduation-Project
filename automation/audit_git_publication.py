"""Rà soát nội dung dự kiến commit và mọi blob trong Git, không in giá trị bí mật.

Đọc thêm XML/metadata/ảnh nhúng của DOCX và metadata PNG. OCR được thực hiện riêng
bằng Windows OCR; công cụ không kết luận ảnh an toàn nếu chưa có kết quả OCR/review.
"""
import argparse
import base64
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import subprocess
import zipfile
import zlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'staging/github-backup'
PATTERNS={
 'private_key':rb'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----|openssh-key-v1\x00|-----BEGIN PGP [P]RIVATE KEY BLOCK-----',
 'github_token':rb'\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{35,})\b',
 'aws_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'slack_token':rb'\bxox[baprs]-[A-Za-z0-9-]{20,}',
 'google_api_key':rb'\bAIza[A-Za-z0-9_-]{30,}',
 'bearer_literal':rb'(?i)authorization\s*[:=]\s*["\x27]?bearer\s+[A-Za-z0-9_.-]{20,}',
 'crypt_password_hash':rb'\$(?:6|5|1|y|2[aby])\$[A-Za-z0-9./=,\-]{5,}\$[A-Za-z0-9./]{20,}',
 'jwt':rb'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{16,}\b',
 'credential_url':rb'(?i)https?://[^\s/"\x27:]+:[^\s/@"\x27]{4,}@',
 'quoted_credential':rb'(?i)(?:password|passwd|passphrase|api[_-]?key|access[_-]?token|client[_-]?secret)\s*["\x27]?\s*[:=]\s*["\x27]([^"\x27\r\n]{1,})["\x27]',
}
PLACEHOLDER=re.compile(rb'(?i)^(?:redacted|<[^>]*>|\[[^\]]*\]|none|null|false|true|dummy|example|changeme|your[_ -].*|\*+)$')
REVIEWED_REDACTION_NOTICE='8843152ca9fe0d24609ff6cc60abacfec08bef3ef2b5a27d0856af92eae30035'

def git(args,input=None):
    r=subprocess.run(['git',*args],cwd=ROOT,input=input,capture_output=True)
    if r.returncode:raise RuntimeError('Git failed: '+' '.join(args))
    return r.stdout

def candidates():
    return sorted(set(p.decode('utf-8') for p in git(['ls-files','--cached','--others','--exclude-standard','-z']).split(b'\0') if p))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--known-values-stdin',action='store_true');parser.add_argument('--label',default='worktree')
    parser.add_argument('--ocr-results',type=Path)
    o=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    known=[]
    if o.known_values_stdin:
        import sys
        known=[str(v).encode() for v in json.load(sys.stdin) if v]
    findings=[];images={};manifest=[];scanned=set()
    def scan(label,data):
        digest=hashlib.sha256(data).hexdigest()
        # Không bỏ qua label khác khi ghi finding, nhưng tránh giải nén trùng.
        for rule,pattern in PATTERNS.items():
            for match in re.finditer(pattern,data):
                if rule=='quoted_credential':
                    value=match.group(1).strip()
                    if PLACEHOLDER.fullmatch(value):continue
                    if hashlib.sha256(value).hexdigest()==REVIEWED_REDACTION_NOTICE:continue
                findings.append({'path':label,'rule':rule,'line':data[:match.start()].count(b'\n')+1})
        for value in known:
            if value in data:findings.append({'path':label,'rule':'known_sensitive_value','line':data[:data.index(value)].count(b'\n')+1})
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            images.setdefault(digest,{'references':[],'data':data})['references'].append(label)
            pos=8
            while pos+12<=len(data):
                n=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];payload=data[pos+8:pos+8+n]
                if kind in [b'tEXt',b'iTXt']:scan(label+'::PNG-metadata',payload)
                if kind==b'zTXt':
                    try:scan(label+'::PNG-zTXt',zlib.decompress(payload.split(b'\0',1)[1][1:]))
                    except (ValueError,zlib.error):pass
                pos+=n+12
        if data.startswith(b'PK\x03\x04') and digest not in scanned:
            scanned.add(digest)
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    for name in archive.namelist():
                        member=archive.read(name)
                        if len(member)>20*1024*1024:raise RuntimeError('Archive member too large for audit')
                        scan(label+'::'+name,member)
            except zipfile.BadZipFile:findings.append({'path':label,'rule':'unreadable_archive','line':0})
        if b'\0' not in data and len(data)<3_000_000:
            # Những payload base64 dài trong JSON cũng phải được rà, không chỉ phần hiển thị.
            for token in set(re.findall(rb'[A-Za-z0-9+/]{120,}={0,2}',data)):
                try:
                    decoded=base64.b64decode(token,validate=True)
                    if decoded!=data and (b'\n' in decoded or decoded.startswith((b'{',b'['))):
                        for value in known:
                            if value in decoded:findings.append({'path':label,'rule':'known_value_in_base64','line':0})
                        for rule,pattern in PATTERNS.items():
                            if rule!='quoted_credential' and re.search(pattern,decoded):findings.append({'path':label,'rule':rule+'_in_base64','line':0})
                except (ValueError,base64.binascii.Error):pass
    paths=candidates()
    for name in paths:
        path=ROOT/name
        if not path.is_file():continue
        data=path.read_bytes();scan(name,data)
        manifest.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    commits=git(['rev-list','--all']).decode().splitlines()
    objects=git(['cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype) %(objectsize)']).decode().splitlines()
    blobs=[line.split()[0] for line in objects if line.split()[1]=='blob']
    for oid in blobs:scan('git-blob:'+oid,git(['cat-file','blob',oid]))
    image_dir=OUT/'ocr-images';image_dir.mkdir(exist_ok=True)
    image_inventory=[]
    for digest,entry in images.items():
        target=image_dir/(digest+'.png');target.write_bytes(entry['data'])
        image_inventory.append({'sha256':digest,'file':str(target),'references':entry['references']})
    ocr_summary={'provided':False}
    if o.ocr_results:
        ocr=json.loads(o.ocr_results.read_text(encoding='utf-8-sig'))
        for result in ocr:
            if not result.get('error'):scan('image-ocr:'+result['sha256'],result['text'].encode('utf-8'))
        ocr_summary={'provided':True,'images':len(ocr),'errors':sum(bool(r.get('error')) for r in ocr),
                     'all_current_images_covered':all(d in {r['sha256'] for r in ocr if not r.get('error')} for d in images)}
    summary={'candidate_files':len(manifest),'total_bytes':sum(p['bytes'] for p in manifest),
       'extensions':dict(Counter(Path(p['path']).suffix for p in manifest)),
       'history_commit_count':len(commits),'all_object_blob_count':len(blobs),
       'scanned_docx_and_embedded_content':True,'unique_images_pending_ocr':len(images),
       'findings':findings,'no_secret_values_in_findings':True}
    summary['ocr']=ocr_summary
    (OUT/(o.label+'-scan.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'candidate-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'ocr-inventory.json').write_text(json.dumps(image_inventory,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':main()
