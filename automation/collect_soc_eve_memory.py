"""Chỉ đọc RAM EVE và QEMU; không gửi thao tác vòng đời node."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys

code = r'''
import glob,json,os,pathlib,subprocess
out={'meminfo':pathlib.Path('/proc/meminfo').read_text(),'qemu':[]}
for p in glob.glob('/proc/[0-9]*/cmdline'):
    try:
        a=[x.decode(errors='replace') for x in pathlib.Path(p).read_bytes().split(b'\0') if x]
        if not a or os.path.basename(a[0])!='qemu-system-x86_64':continue
        base=pathlib.Path(p).parent
        row={'pid':base.name,'name':a[a.index('-name')+1],'uuid':a[a.index('-uuid')+1], 'configured_ram':a[a.index('-m')+1]}
        row['memory_status']=[x for x in (base/'status').read_text().splitlines() if x.startswith(('VmRSS:','VmSwap:','VmSize:','RssAnon:','RssFile:','RssShmem:'))]
        try:row['smaps_rollup']=[x for x in (base/'smaps_rollup').read_text().splitlines() if x.startswith(('Rss:','Pss:','Private_Clean:','Private_Dirty:','Swap:'))]
        except OSError:row['smaps_rollup']=None
        out['qemu'].append(row)
    except (OSError,ValueError):continue
print(json.dumps(out))
'''
ssh=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=10','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143','python3','-']
result=subprocess.run(ssh,input=code,text=True,encoding='utf-8',capture_output=True,timeout=30,check=True)
data=json.loads(result.stdout)
data['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
with Path(sys.argv[1]).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps(data,ensure_ascii=False))
