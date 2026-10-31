"""Kiểm kê chỉ đọc phục vụ thiết kế cổng M2; không gọi API đăng nhập hoặc sửa node."""
import datetime as dt
import json
from pathlib import Path
import subprocess
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
import glob,hashlib,json,os,subprocess,xml.etree.ElementTree as ET
def command(args):
 p=subprocess.run(args,capture_output=True,text=True)
 return {'args':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
labs=[]
for path in sorted(glob.glob('/opt/unetlab/labs/**/*.unl',recursive=True)):
 r=ET.parse(path).getroot()
 labs.append({'path':path,'lab_id':r.get('id'),'sha256':hashlib.sha256(open(path,'rb').read()).hexdigest(),
  'nodes':[{'attributes':n.attrib,'interfaces':[i.attrib for i in n.findall('interface')]} for n in r.findall('.//node')],
  'networks':[n.attrib for n in r.findall('.//network')]})
processes=[]
for path in glob.glob('/proc/[0-9]*/cmdline'):
 try:
  args=[s.decode(errors='replace') for s in open(path,'rb').read().split(b'\0') if s]
  if args and os.path.basename(args[0])=='qemu-system-x86_64':
   pid=path.split('/')[2]
   processes.append({'pid':pid,'args':args,'cwd':os.readlink('/proc/'+pid+'/cwd'),
                     'status':open('/proc/'+pid+'/status').read()})
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
images=[]
for path in sorted(glob.glob('/opt/unetlab/addons/qemu/*')):
 if os.path.isdir(path):
  images.append({'directory':path,'files':[{'name':os.path.basename(p),'bytes':os.stat(p).st_size} for p in glob.glob(path+'/*') if os.path.isfile(p)]})
print(json.dumps({'labs':labs,'qemu_processes':processes,'qemu_image_inventory':images,
 'host_links':command(['ip','-j','link','show']), 'memory':command(['free','-m']),
 'meminfo':open('/proc/meminfo').read(),'cpu':command(['lscpu']),
 'load':open('/proc/loadavg').read(),'vmstat':command(['vmstat','1','3']),
 'disk':command(['df','-h','/','/opt/unetlab']),
 'clock_untrusted':command(['timedatectl','show','-p','Timezone','-p','NTPSynchronized']),
 'vpcs_binary':command(['stat','-c','%a %U %G %n','/opt/vpcsu/bin/vpcs'])}))
'''

def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=7)))
    output = ROOT/'docs/evidence/M2'/('port-design-'+now.strftime('%Y%m%dT%H%M%S%z'))
    output.mkdir(exist_ok=False)
    ssh = ['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes',
           '-o','ConnectTimeout=10','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143','python3','-']
    result = subprocess.run(ssh,input=REMOTE,capture_output=True,text=True,encoding='utf-8',timeout=55)
    if result.returncode:
        raise RuntimeError(result.stderr)
    facts = json.loads(result.stdout)
    facts['collector_time_start'] = now.isoformat()
    facts['collector_time_end'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    facts['scope'] = 'Read-only host inventory; no guest commands, lifecycle, network, image or configuration changes'
    (output/'eve-inventory.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
    windows_cmd = '$o=Get-CimInstance Win32_OperatingSystem; $c=Get-CimInstance Win32_ComputerSystem; [PSCustomObject]@{CollectedAt=(Get-Date).ToString("o"); FreePhysicalMemoryKiB=$o.FreePhysicalMemory; TotalVisibleMemoryKiB=$o.TotalVisibleMemorySize; LogicalProcessors=$c.NumberOfLogicalProcessors} | ConvertTo-Json'
    windows = subprocess.run(['powershell.exe','-NoProfile','-Command',windows_cmd],capture_output=True,text=True,timeout=25)
    assert windows.returncode == 0
    (output/'windows-memory.json').write_text(windows.stdout,encoding='utf-8')
    report = ROOT/'docs/M2/M2-report-ovs-offline-installed-20261101.docx'
    with zipfile.ZipFile(report) as z:
        document = ET.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    text='\n'.join(''.join(p.itertext()) for p in document.findall('.//w:p',ns))
    # itertext cũng gồm nội dung thẻ; file này là bản trích đọc, không thay bản gốc.
    (output/'prior-docx-extracted.txt').write_text(text,encoding='utf-8')
    print(json.dumps({'directory':str(output),'labs':[(l['path'],len(l['nodes']),len(l['networks'])) for l in facts['labs']],
        'running_qemu':[(p['pid'],p['args'][p['args'].index('-name')+1]) for p in facts['qemu_processes']],
        'images':[p['directory'] for p in facts['qemu_image_inventory']],
        'eve_memory':facts['memory']['stdout'],'windows_memory':windows.stdout},ensure_ascii=False))

if __name__=='__main__':main()
