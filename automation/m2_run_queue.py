"""Sequential M2 controller, PREPARED ONLY. Default creates a plan, no SSH/VM calls.

Future execution requires --execute --resources-ready. A clock reaching 10:00 is
never authorization. First run stops at one manual console login/sudo step;
resume then handles guest transfer, baseline, frame tests, mirror and collection.
Reboot has a separate checkpoint because sudo/login expires across boots.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from m2_console_job import ConsoleJob, ConsoleTransportError

ROOT=Path(__file__).resolve().parents[1]
STAGES=['resources','start-core','baseline','backup','vlan-trunk','mirror','mirror-traffic','persist','reboot','postboot-baseline','postboot-traffic','collect']
REMOTE=r'''
import glob,json,pathlib,subprocess,xml.etree.ElementTree as E
p=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');r=E.parse(p).getroot();n=r.findall('.//node')
assert len(n)==1 and n[0].get('name')=='SOC-Core-L2' and n[0].get('id')=='3'
assert n[0].get('uuid')=='2b295168-b72e-4de7-b364-37298252dd9f'
assert n[0].get('ram')=='2048' and not r.findall('.//network') and not n[0].findall('interface')
q=[]
for f in glob.glob('/proc/[0-9]*/cmdline'):
 try:
  a=pathlib.Path(f).read_bytes().split(b'\0')
  if a and b'qemu-system' in a[0]:q.append({'pid':f.split('/')[2],'args':[v.decode() for v in a if v]})
 except (FileNotFoundError,PermissionError,ProcessLookupError):pass
mem={s.split(':')[0]:int(s.split()[1]) for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if s.split()[1].isdigit()}
print(json.dumps({'node':n[0].attrib,'qemu':q,'mem_available_kib':mem['MemAvailable'],'swap_used_kib':mem['SwapTotal']-mem['SwapFree']}))
'''


def now():return dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()


def ssh(code,timeout=60):
    args=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes',
          '-o','ConnectTimeout=10','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143','python3','-']
    r=subprocess.run(args,input=code,capture_output=True,text=True,encoding='utf-8',timeout=timeout)
    if r.returncode:raise RuntimeError('EVE action failed: '+r.stderr)
    return json.loads(r.stdout)


def require_resources(windows,eve):
    core=[p for p in eve['qemu'] if eve['node']['uuid'] in p['args']]
    if len(core)!=len(eve['qemu']) or len(core)>1:
        raise RuntimeError('Unexpected VM on EVE; no start or stop performed')
    reserve=1024*1024 if core else 3*1024*1024
    if windows['available_kib']<reserve or windows['virtual_available_kib']<reserve:
        raise RuntimeError('Insufficient Windows memory/commit headroom; leave existing VMs untouched')
    if eve['mem_available_kib']<(1024*1024 if core else 3*1024*1024) or eve['swap_used_kib']>256*1024:
        raise RuntimeError('Insufficient EVE headroom or active swap pressure')
    return bool(core)


class Queue:
    def __init__(self,path):
        self.path=path
        self.file=path/'queue.json'
        if self.file.exists():self.data=json.loads(self.file.read_text(encoding='utf-8'))
        else:
            self.data={'created_at':now(),'session':path.name,'mode':'PREPARED','stages':{k:{'status':'NOT_RUN'} for k in STAGES},'network_functional_acceptance':False}
            path.mkdir(parents=True,exist_ok=False)
        self.write()

    def write(self):
        self.data['updated_at']=now()
        self.file.write_text(json.dumps(self.data,indent=2)+'\n',encoding='utf-8')
        with (self.path/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['stage','status','time_UTC+0700','evidence','scope'])
            for key,val in self.data['stages'].items():w.writerow([key,val['status'],val.get('time',''),val.get('evidence',''),'stage status, not overall M2 acceptance'])

    def mark(self,key,status,evidence='',detail=''):
        self.data['stages'][key]={'status':status,'time':now(),'evidence':evidence,'detail':detail}
        self.write()
        with (self.path/'events.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps({'stage':key,**self.data['stages'][key]})+'\n')

    def done(self,key):return self.data['stages'][key]['status']=='DONE'


def parse_public(reply):
    return json.loads(reply['stdout'])


def frame_test(q,stage,mirror):
    q.data['active_stage']=stage;q.write()
    dest='/root/m2-frame-'+q.data['session']+'-'+stage
    code=(ROOT/'automation/m2_tap_frame_test.py').read_text(encoding='utf-8')
    # No shell interpolation; sys.argv is a literal Python list.
    program='import sys\nsys.argv='+repr(['frame.py','--guest-ready','--output',dest]+(['--mirror'] if mirror else []))+'\n'+code
    # Print progress goes to stderr; final JSON alone goes to SSH stdout.
    wrapper='import contextlib,io,json,pathlib\nb=io.StringIO()\nwith contextlib.redirect_stdout(b):\n exec('+repr(program)+',{"__name__":"__main__"})\nprint(pathlib.Path('+repr(dest+'/result.json')+').read_text())'
    result=ssh(wrapper,timeout=60)
    if not result.get('completed') or not result.get('all_cases_passed'):
        raise RuntimeError('Incomplete/failed frame test; inspect EVE capture directory '+dest)
    file=q.path/(stage+'.json');file.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    # PCAP remains root-only on EVE, synthetic traffic only; raw captures ignored by Git.
    q.mark(stage,'DONE',str(file),'Real frame result required; PCAP on EVE at '+dest)


def execute(q,args):
    if not args.resources_ready:raise RuntimeError('Execution requires the user to confirm resources are ready, not merely 10:00')
    if q.data.get('rollback'):
        raise RuntimeError('This run was rolled back; retain all logs and create a new run after reviewing restored baseline')
    if q.done('collect'):
        print('Run already collected; no repeated VM or network checks')
        return
    q.data['mode']='EXECUTION_REQUESTED';q.write()
    r=subprocess.run(['powershell.exe','-NoProfile','-Command',
        '$o=Get-CimInstance Win32_OperatingSystem; @{available_kib=[long]$o.FreePhysicalMemory;virtual_available_kib=[long]$o.FreeVirtualMemory}|ConvertTo-Json'],capture_output=True,text=True,check=True)
    windows=json.loads(r.stdout);eve=ssh(REMOTE)
    running=require_resources(windows,eve)
    if q.data.get('error'):
        q.data.setdefault('historical_errors',[]).append(q.data.pop('error'))
    p=q.path/('resource-'+dt.datetime.now().strftime('%H%M%S')+'.json')
    p.write_text(json.dumps({'collector_time':now(),'windows':windows,'eve':eve},indent=2)+'\n')
    q.mark('resources','DONE',str(p))
    if not running:
        start=REMOTE+'\nassert not q\nx=subprocess.run(["/opt/unetlab/wrappers/unl_wrapper","-a","start","-T","0","-F","/opt/unetlab/labs/SOC-M2-Core-L2.unl","-D","3"],capture_output=True,text=True)\nassert x.returncode==0,x.stderr\n'
        ssh(start)
        q.mark('start-core','REQUESTED',str(p),'Wrapper accepted start for Core ID3; boot not yet verified')
        q.mark('baseline','WAIT_CONSOLE',detail='Wait boot; inspect actual screen, log in and sudo -v locally, then resume with --console-shell-ready. Never send credentials to the script.')
        return
    q.mark('start-core','DONE',str(p),'Existing Core already running; no duplicate start')
    if not args.console_shell_ready:
        q.mark('baseline','WAIT_CONSOLE',detail='Verified idle guest shell + sudo -n access required once per boot')
        return
    work='/root/m2-traffic-'+q.data['session']
    session=q.data.get('bundle_session',q.data['session']+'-'+str(int(time.time())))
    adapter=ConsoleJob(q.path/'console-transfer',session,shell_ready=True)
    files={'guest.py':(ROOT/'automation/m2_mirror_guest_prepared.py').read_bytes(),
           'soc-core-l2-noip.service':(ROOT/'configs/M2/soc-core-l2-noip.service').read_bytes(),
           'soc-core-l2-noip.sh':(ROOT/'configs/M2/soc-core-l2-noip.sh').read_bytes()}
    if not q.data.get('bundle_session') or not adapter.reuse(files):
        if q.data.get('bundle_session'):
            adapter=ConsoleJob(q.path/'console-transfer',q.data['session']+'-'+str(int(time.time())),shell_ready=True)
        adapter.stage(files)
    q.data['bundle_session']=adapter.session;q.write()
    mutated=q.done('mirror')
    try:
        if not q.done('baseline'):
            q.data['active_stage']='baseline';q.write()
            reply=parse_public(adapter.run('baseline',work+'-baseline-'+str(int(time.time()))))
            q.data['initial_boot_id']=reply['state']['boot_id'];q.mark('baseline','DONE')
        if not q.done('backup'):
            q.data['active_stage']='backup';q.write()
            reply=parse_public(adapter.run('backup',work))
            q.data['backup']=reply['backup'];q.mark('backup','DONE',detail='OVSDB raw kept root-only in '+work)
        if not q.done('vlan-trunk'):frame_test(q,'vlan-trunk',False)
        if not q.done('mirror'):
            q.data['active_stage']='mirror';q.write()
            mutated=True
            adapter.run('mirror',work);q.mark('mirror','DONE')
        if not q.done('mirror-traffic'):frame_test(q,'mirror-traffic',True)
        if not q.done('persist'):
            q.data['active_stage']='persist';q.write()
            adapter.run('persist',work);q.mark('persist','DONE')
        if q.data['stages']['reboot']['status']=='REQUESTED':
            reply=parse_public(adapter.run('verify',work))
            if reply['state']['boot_id']==q.data['initial_boot_id']:
                q.mark('reboot','REQUESTED',detail='Still same boot ID: reboot not verified, inspect actual console; no repeated reboot request')
                return
            q.mark('reboot','DONE',detail='Changed boot_id verified after console reauthentication')
        if not q.done('reboot'):
            if not args.reboot_ready:
                q.mark('reboot','WAIT_REBOOT_CHECKPOINT',detail='Save logs and ensure no other guest task is running; resume --reboot-ready after checking actual console')
                return
            require_resources(windows,ssh(REMOTE))
            # Graceful guest reboot, never EVE/Windows reboot or node reset.
            adapter.command('sudo -n systemd-run --unit=soc-m2-controlled-reboot --on-active=5s /usr/bin/systemctl reboot')
            q.mark('reboot','REQUESTED',detail='Not yet verified; reboot is NOT DONE until boot_id changes')
            return
        reply=parse_public(adapter.run('verify',work))
        if reply['state']['boot_id']==q.data['initial_boot_id']:
            raise RuntimeError('Boot ID did not change; persistence not verified')
        q.mark('postboot-baseline','DONE')
        if not q.done('postboot-traffic'):frame_test(q,'postboot-traffic',True)
        q.data['network_functional_acceptance']=True
        q.data['network_functional_acceptance_scope']='Controlled M2 Ethernet frame suites and reboot; not routing/HA/IDS/performance'
        q.mark('collect','DONE',str(q.path),'Verified public JSON/screenshots local; raw DB/PCAP remain EVE/guest; no complete SOC/HA acceptance')
    except ConsoleTransportError:
        q.data['transport_interrupted']=True
        q.data['transport_note']='Inspect actual shell and guest process state; do not start rollback while outcome/console is unknown'
        q.write()
        raise
    except Exception:
        active=q.data.get('active_stage')
        if active:q.mark(active,'FAILED_OR_BLOCKED',detail='See queue error and saved guest/host output; not a networking PASS')
        if mutated:
            try:
                adapter.run('rollback',work)
                q.data['rollback']='CONFIGURATION_RESTORED'
                for key in ['mirror','mirror-traffic','persist','reboot','postboot-baseline','postboot-traffic','collect']:
                    q.data['stages'][key]={'status':'INVALIDATED_BY_ROLLBACK'}
            except Exception:
                q.data['rollback']='UNVERIFIED_MANUAL_CONSOLE_REQUIRED'
        q.write()
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--resources-ready',action='store_true')
    parser.add_argument('--console-shell-ready',action='store_true')
    parser.add_argument('--reboot-ready',action='store_true')
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    if not __debug__:raise RuntimeError('Python -O disables required checks')
    if not re_safe_name(args.run_dir.name):raise ValueError('Run name must contain ASCII letters, digits and hyphens only')
    q=Queue(args.run_dir)
    if args.execute:
        try:execute(q,args)
        except Exception as exc:
            q.data['error']={'type':type(exc).__name__,'message':str(exc),'at':now()};q.write()
            raise
    else:
        print('PREPARED ONLY: no SSH, no VM, no frame generation. Queue: '+str(q.file))


def re_safe_name(name):
    return bool(name) and all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in name)


if __name__=='__main__':main()
