"""CARP secret: tạo một lần, DPAPI CurrentUser; chỉ truyền ciphertext tới từng firewall."""
from pathlib import Path
import base64,datetime,hashlib,hmac,json,secrets,string,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/evidence/M3/group1b-prerequisites-20261103'
PRIVATE=OUT/'private-backups'
SSL=r'C:\Program Files\Git\usr\bin\openssl.exe'
def dpapi(data,decrypt=False):
 op='Unprotect' if decrypt else 'Protect'
 code='Add-Type -AssemblyName System.Security; $b=[Convert]::FromBase64String([Console]::In.ReadToEnd()); [Convert]::ToBase64String([Security.Cryptography.ProtectedData]::'+op+'($b,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser))'
 p=subprocess.run(['powershell.exe','-NoProfile','-Command',code],input=base64.b64encode(data),capture_output=True)
 assert p.returncode==0,'DPAPI failed; no plaintext output'
 return base64.b64decode(p.stdout.strip(),validate=True)
def initialize():
 PRIVATE.mkdir(exist_ok=False)
 owner=subprocess.run(['whoami'],capture_output=True,text=True,check=True).stdout.strip()
 subprocess.run(['icacls.exe',str(PRIVATE),'/inheritance:r','/grant:r',owner+':(OI)(CI)F'],capture_output=True,check=True)
 manifests=[]
 for role in ['Primary','Secondary']:
  d=json.loads((OUT/(role.lower()+'-audit.json')).read_text(encoding='utf-8'))
  assert d['config_unchanged'] and not d['VIP_references'] and not d['VHIDs'] and not d['ARP_VIP_conflicts']
  assert d['sync']['configured_device']=='opt6' and d['sync']['configured_peer']==d['sync']['peer']
  source=ROOT/'docs/evidence/M3/group1-carp-readiness-20261103/private-backups'/(role+'-config.xml')
  raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==d['backup_sha256']==d['config_sha256_before']
  dest=PRIVATE/(role+'-before.xml');dest.write_bytes(raw)
  assert subprocess.run(['git','check-ignore','--',str(dest.relative_to(ROOT))],cwd=ROOT,capture_output=True).returncode==0
  manifests.append({'role':role,'snapshot_guest':d['backup_guest'],'local_backup':str(dest.relative_to(ROOT)),'sha256':d['backup_sha256'],'bytes':len(raw),'method':'Fresh snapshot on guest; local bytes copied from prior verified backup after exact SHA256 comparison to fresh snapshot; no redundant secret transfer'})
 value=''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(19)).encode()
 (PRIVATE/'carp-shared-secret.dpapi').write_bytes(dpapi(value))
 assert dpapi((PRIVATE/'carp-shared-secret.dpapi').read_bytes(),True)==value
 assert subprocess.run(['git','check-ignore','--',str((PRIVATE/'carp-shared-secret.dpapi').relative_to(ROOT))],cwd=ROOT,capture_output=True).returncode==0
 now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
 (OUT/'backup-before-manifest.json').write_text(json.dumps({'collected_at':now,'backups':manifests,'private_directory_owner_only':True,'CARP_secret_created_once_DPAPI_CurrentUser':True,'CARP_secret_disclosed':False},ensure_ascii=False,indent=2),encoding='utf-8')
 (OUT/'SHA256SUMS-before.txt').write_text(''.join(x['sha256']+'  private-backups/'+x['role']+'-before.xml\n' for x in manifests),encoding='ascii')
 print(json.dumps({'backup_count':2,'fresh_guest_and_local_hashes_match':True,'DPAPI_secret_prepared':True,'secret_printed':False}))
def prepare_cipher(role):
 value=dpapi((PRIVATE/'carp-shared-secret.dpapi').read_bytes(),True)
 d=json.loads((OUT/(role.lower()+'-audit.json')).read_text(encoding='utf-8'))
 pub=OUT/(role.lower()+'-carp-recipient-public.der');pub.write_bytes(base64.b64decode(d['source_public_key_der_b64'],validate=True))
 p=subprocess.run([SSL,'pkeyutl','-encrypt','-pubin','-keyform','DER','-inkey',str(pub),'-pkeyopt','rsa_padding_mode:oaep','-pkeyopt','rsa_oaep_md:sha256'],input=value,capture_output=True)
 assert p.returncode==0,'Recipient encryption failed'
 challenge=secrets.token_bytes(32)
 return base64.b64encode(p.stdout).decode(),challenge.hex(),hmac.new(value,challenge,hashlib.sha256).hexdigest()
if __name__=='__main__':initialize()
