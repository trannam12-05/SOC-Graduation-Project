"""Historical attempted repair, retained for review; do not rerun this helper.

Two attempts were blocked by guards; the actual final recovery used the logged
runtime-backup/runtime-restored-up console commands. The SOURCE path below was
temporary and is not the current persistence mechanism. Use the controller and
the installed no-IP unit for normal operation.

Online OVSDB backup first. No bridge recreation, VLAN, old NIC, route assignment
or forwarding changes. Only runtime on existing internal br-core-l2. Work root-only.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

# Exact bundle transferred and verified in the first actual run.
SOURCE=Path('/tmp/m2-bundle-m2-live-20261101a-1793504538/guest.py')


def main():
    assert os.geteuid()==0 and __debug__
    work=Path(sys.argv[-1])
    assert work.parent==Path('/root') and work.name.startswith('m2-bootfix-') and not work.is_symlink()
    work.mkdir(mode=0o700,exist_ok=False)
    spec=importlib.util.spec_from_file_location('verified_m2_guest',SOURCE)
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);g.WORK=work
    before=g.state();g.save('before.json',before)
    temporary=copy.deepcopy(before)
    bridge=next(x for x in temporary['links'] if x['ifname']==g.BR)
    assert 'UP' not in bridge['flags'], 'Repair only the observed admin-DOWN condition'
    bridge['flags'].append('UP')
    g.check(temporary)  # All other guards must hold; no actual interface changed yet.
    old={k:Path('/proc/sys/net/ipv6/conf/br-core-l2/'+k).read_text().strip() for k in ['disable_ipv6','addr_gen_mode']}
    command=['ovsdb-client','backup',g.SOCKET,'Open_vSwitch']
    r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    assert r.returncode==0, 'Backup failed, no repair'
    backup=work/'ovsdb.before'
    with backup.open('xb') as f:f.write(r.stdout)
    os.chmod(backup,0o600)
    assert g.run(['ovsdb-tool','db-version',str(backup)]).decode().strip()=='8.5.1'
    g.run(['ovsdb-tool','compact',str(backup),str(work/'ovsdb.validated')])
    metadata={'path':str(backup),'sha256':hashlib.sha256(r.stdout).hexdigest(),'bytes':len(r.stdout),'schema':'8.5.1'}
    g.save('backup-metadata.json',metadata)
    rollback='#!/bin/sh\nset -eu\nip link set dev br-core-l2 down\n'
    rollback+='sysctl -w net.ipv6.conf.br-core-l2.disable_ipv6='+old['disable_ipv6']+'\n'
    rollback+='sysctl -w net.ipv6.conf.br-core-l2.addr_gen_mode='+old['addr_gen_mode']+'\n'
    (work/'rollback-runtime.sh').write_text(rollback);os.chmod(work/'rollback-runtime.sh',0o700)
    try:
        g.run(['ip','link','set','dev',g.BR,'addrgenmode','none'])
        g.run(['sysctl','-w','net.ipv6.conf.br-core-l2.disable_ipv6=1'])
        g.run(['ip','link','set','dev',g.BR,'up'])
        after=g.state();g.save('after.json',after);g.check(after)
        assert before['forward4']==after['forward4'] and before['forward6']==after['forward6']
        assert before['ports']==after['ports'] and before['mirrors']==after['mirrors']
        assert {x['ifname']:x['addr_info'] for x in before['addresses']}=={x['ifname']:x['addr_info'] for x in after['addresses']}
    except Exception:
        g.run(['sh',str(work/'rollback-runtime.sh')])
        g.save('restored.json',g.state())
        raise
    public={'runtime_repaired':True,'traffic_tested':False,'backup':metadata,'old_bridge_ipv6_settings':old,
            'before':before,'after':after,'commands_log_retained_in_guest':str(work/'commands.jsonl')}
    g.save('result.json',public)
    print(json.dumps(public))


if __name__=='__main__':main()
