"""Collect only actual synthetic M2 frame results/PCAPs and queue receipts.

No database/credentials/images, no mutation on EVE; collection may include a
failed/partial run. NOT_RUN stays NOT_RUN. PCAPs are local, ignored by Git.
"""
import argparse
import base64
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import struct

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args();args.run_dir=args.run_dir.resolve();args.output_dir=args.output_dir.resolve()
    queue=json.loads((args.run_dir/'queue.json').read_text())
    session=queue['session']
    assert all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in session)
    args.output_dir.mkdir(parents=True,exist_ok=False)
    code='''import pathlib,json,base64,hashlib
session=__SESSION__
files=[]
for stage in ['vlan-trunk','mirror-traffic','postboot-traffic']:
 d=pathlib.Path('/root')/('m2-frame-'+session+'-'+stage)
 if not d.is_dir():continue
 for p in d.iterdir():
  if p.name!='result.json' and p.suffix!='.pcap':continue
  assert p.is_file() and not p.is_symlink() and p.stat().st_size<2000000
  b=p.read_bytes();files.append({'stage':stage,'name':p.name,'sha256':hashlib.sha256(b).hexdigest(),'data':base64.b64encode(b).decode()})
print(json.dumps(files))
'''.replace('__SESSION__',repr(session))
    cmd=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10',
         '-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143','python3','-']
    r=subprocess.run(cmd,input=code,capture_output=True,text=True,encoding='utf-8',timeout=40)
    assert r.returncode==0,r.stderr
    now=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    inventory=[];cases=[];capture_summary=[]
    for entry in json.loads(r.stdout):
        data=base64.b64decode(entry['data']);assert hashlib.sha256(data).hexdigest()==entry['sha256']
        dest=args.output_dir/entry['stage']/entry['name'];dest.parent.mkdir(exist_ok=True)
        with dest.open('xb') as f:f.write(data)
        inventory.append({'name':entry['name'],'stage':entry['stage'],'collector_time':now,'path':str(dest.relative_to(ROOT)),
                          'sha256':entry['sha256'],'bytes':len(data),'report_position':'M2 live frame tests'})
        if dest.suffix=='.json':
            result=json.loads(data)
            for case in result['cases']:
                cases.append({'stage':entry['stage'],'case':case['case'],'status':case['status'],
                              'run_completed':result.get('completed',False),'ingress':case['ingress'],
                              'tx_vlan':case['tx_vlan'],'expected':json.dumps(case['expected']),
                              'observed':json.dumps(case['observed']),'mirror_frames':case['mirror_frames'],
                              'evidence':str(dest.relative_to(ROOT))})
        else:
            assert data[:4]==bytes.fromhex('d4c3b2a1') and struct.unpack('<I',data[20:24])[0]==1
            offset=24;packets=0;tags={};markers=set()
            while offset<len(data):
                _,_,captured,original=struct.unpack('<IIII',data[offset:offset+16]);offset+=16
                frame=data[offset:offset+captured];offset+=captured
                assert len(frame)==captured==original and b'SOC-M2-' in frame
                vlan=str(struct.unpack('!H',frame[14:16])[0]&4095) if frame[12:14]==b'\x81\x00' else 'untagged'
                tags[vlan]=tags.get(vlan,0)+1;packets+=1
            assert offset==len(data)
            capture_summary.append({'stage':entry['stage'],'file':entry['name'],'packets':packets,'vlan_counts':tags})
    shutil.copy2(args.run_dir/'queue.json',args.output_dir/'queue-receipt.json')
    if (args.run_dir/'events.jsonl').is_file():shutil.copy2(args.run_dir/'events.jsonl',args.output_dir/'events.jsonl')
    replies=args.output_dir/'guest-public-replies';replies.mkdir()
    for group in ['console-transfer','postboot-readonly-console','bootfix-console']:
        for source in (args.run_dir/group).glob('*-verified-reply.json'):
            shutil.copy2(source,replies/(group+'__'+source.name))
    (args.output_dir/'evidence-index.json').write_text(json.dumps(inventory,indent=2)+'\n')
    (args.output_dir/'pcap-summary.json').write_text(json.dumps(capture_summary,indent=2)+'\n')
    with (args.output_dir/'frame-cases.csv').open('x',encoding='utf-8-sig',newline='') as f:
        fields=['stage','case','status','run_completed','ingress','tx_vlan','expected','observed','mirror_frames','evidence']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cases)
    print(json.dumps({'actual_cases_collected':len(cases),'pass':sum(c['status']=='PASS' for c in cases),
                      'fail':sum(c['status']=='FAIL' for c in cases),'captures':len(capture_summary),'queue_complete':queue['stages']['collect']['status']=='DONE'}))


if __name__=='__main__':main()
