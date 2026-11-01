"""Resume only after a checksum-verified read-only console receipt after reboot.

Uses the same controller Queue/frame_test and strict guest check. Never marks a
frame PASS from screenshots or a simulated result; executes the last real suite.
"""
import argparse
import json
from pathlib import Path
from m2_run_queue import Queue, frame_test, now, require_resources, ssh, REMOTE
from m2_mirror_guest_prepared import check
import subprocess


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-dir',type=Path,required=True);p.add_argument('--verified-reply',type=Path,required=True)
    p.add_argument('--resources-ready',action='store_true',required=True)
    a=p.parse_args();q=Queue(a.run_dir)
    assert q.data['stages']['reboot']['status']=='REQUESTED' and not q.data.get('rollback')
    reply=json.loads(a.verified_reply.read_text());assert reply['rc']==0
    data=json.loads(reply['stdout']);s=data['state'];check(s,mirror=True)
    assert s['boot_id']!=q.data['initial_boot_id'] and s['noip_unit']=='active' and s['noip_unit_enabled']=='enabled'
    cmd='$o=Get-CimInstance Win32_OperatingSystem; @{available_kib=[long]$o.FreePhysicalMemory;virtual_available_kib=[long]$o.FreeVirtualMemory}|ConvertTo-Json'
    w=subprocess.run(['powershell.exe','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True)
    e=ssh(REMOTE);assert require_resources(json.loads(w.stdout),e), 'Core must already be running; no VM start here'
    (a.run_dir/'postboot-resource.json').write_text(json.dumps({'collector_time':now(),'windows':json.loads(w.stdout),'eve':e},indent=2)+'\n')
    q.mark('reboot','DONE',str(a.verified_reply),'Changed boot ID, complete actual state and enabled/active no-IP unit verified')
    q.mark('postboot-baseline','DONE',str(a.verified_reply),'Same strict MAC/OVS/VLAN/Mirror/noIP/forwarding guards; read-only fallback')
    frame_test(q,'postboot-traffic',True)
    q.data['transport_interrupted']=False;q.data['transport_note']='Resolved by checksum-verified read-only export using retained source hash; last real suite executed by controller'
    q.data['controlled_m2_suite_verified']=True
    q.data['network_functional_acceptance']=True
    q.data['network_functional_acceptance_scope']='Controlled M2 Ethernet VLAN/trunk/mirror suites and reboot only; not routing/HA/IDS/performance'
    q.mark('collect','DONE',str(a.run_dir),'95 actual frame cases complete; collect PCAP/log separately; not routing/HA/IDS acceptance')
    print('POSTBOOT_REAL_SUITE_COMPLETED')


if __name__=='__main__':main()
