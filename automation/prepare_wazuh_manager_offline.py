"""Chuẩn bị Wazuh manager offline từ metadata ký chính thức; không cài host."""
import json,hashlib,datetime as dt
from pathlib import Path
import prepare_core_stage1 as old
from topology_remote import remote,ROOT

LOCAL=ROOT/'staging/topology-first/wazuh-offline'
DEST='/opt/unetlab/soc-wazuh-preparation-20261102'
def main():
 remote("from pathlib import Path\np=Path("+repr(DEST)+");p.mkdir(mode=0o700,exist_ok=True)\nprint('Dedicated offline preparation directory ready')")
 for name in ['GPG-KEY-WAZUH','InRelease','Packages']:old.copy_to(LOCAL/name,DEST+'/'+name)
 code=r'''
import pathlib,subprocess,json,hashlib,re
p=pathlib.Path('__DEST__');ring=p/'wazuh.gpg'
if not ring.exists():
 subprocess.run(['gpg','--batch','--dearmor','--output',str(ring),str(p/'GPG-KEY-WAZUH')],check=True,capture_output=True)
check=subprocess.run(['gpgv','--status-fd','1','--keyring',str(ring),str(p/'InRelease')],text=True,capture_output=True)
assert check.returncode==0 and 'VALIDSIG ' in check.stdout,'Wazuh metadata signature failed'
text=(p/'InRelease').read_text();section=text.split('SHA256:',1)[1].split('SHA512:',1)[0]
rows={m.group(3):m.group(1) for m in re.finditer(r'^\s+([0-9a-f]{64})\s+(\d+)\s+(.+)$',section,re.M)}
assert hashlib.sha256((p/'Packages').read_bytes()).hexdigest()==rows['main/binary-amd64/Packages']
print(json.dumps({'gpgv_returncode':check.returncode,'signature_status':check.stdout,'package_index_sha256_verified':True}))
'''.replace('__DEST__',DEST)
 verified=json.loads(remote(code))
 records=json.loads((LOCAL/'manager-candidates.json').read_text())
 record=records[0]
 assert record['Version']=='4.14.9-1' and record['Architecture']=='amd64'
 target=LOCAL/Path(record['Filename']).name
 old.download('https://packages.wazuh.com/4.x/apt/'+record['Filename'],target,record['SHA256'])
 assert old.sha(target)==record['SHA256']
 old.copy_to(target,DEST+'/'+target.name)
 receipt={'collected_at':old.now(),'package':'wazuh-manager','version':record['Version'],'architecture':'amd64','bytes':target.stat().st_size,'sha256':record['SHA256'],'signature_verification':verified,'remote_package':DEST+'/'+target.name,'scope':'Manager package prepared; not a complete indexer/dashboard deployment, not installed yet'}
 output=ROOT/'docs/evidence/M5/resume-20261102';output.mkdir(parents=True,exist_ok=True)
 (output/'wazuh-manager-offline-prepared.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(receipt))
if __name__=='__main__':main()
