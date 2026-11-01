"""PREPARED, NOT RUN. Guest root only: snapshot / add ingress mirror / rollback.

Do not execute until the user confirms resources are ready. Does not boot a VM,
assign IPs, change forwarding, install packages or EVE links. Persistence installs
only the reviewed no-IP unit/helper when explicitly invoked in a future run.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

BR = 'br-core-l2'
SOCKET = 'unix:/var/run/openvswitch/db.sock'
DATA = ['ens'+str(i) for i in range(3, 10)]
VLAN = [30, 40, 50, 60, 99]
WORK = None


def run(args, check=True, **kwargs):
    try:
        r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, **kwargs)
    except subprocess.TimeoutExpired:
        with (WORK/'commands.jsonl').open('a') as f:
            f.write(json.dumps({'args':args,'error':'timeout','time_untrusted':time.time()})+'\n')
        raise
    record = {'time_untrusted': time.time(), 'args': args, 'rc': r.returncode,
              'stdout': r.stdout.decode(errors='replace'), 'stderr': r.stderr.decode(errors='replace')}
    with (WORK/'commands.jsonl').open('a') as f:
        f.write(json.dumps(record)+'\n')
    if check and r.returncode:
        raise RuntimeError('Command failed: '+' '.join(args))
    return r.stdout


def save(name, data):
    (WORK/name).write_text(json.dumps(data, indent=2)+'\n')


def table(name, columns):
    data = json.loads(run(['ovs-vsctl', '--timeout=10', '--format=json', '--columns='+columns, 'list', name]))
    def value(x):
        if isinstance(x, list) and len(x) == 2 and x[0] == 'set':
            return [value(y) for y in x[1]]
        if isinstance(x, list) and len(x) == 2 and x[0] == 'uuid':
            return x[1]
        return x
    return [dict(zip(data['headings'], map(value, row))) for row in data['data']]


def state():
    return {'hostname': run(['hostname']).decode().strip(),
            'version': run(['ovs-vsctl','--version']).decode(),
            'services': run(['systemctl','is-active','openvswitch-switch','ovsdb-server','ovs-vswitchd']).decode(),
            'links': json.loads(run(['ip','-j','link'])),
            'addresses': json.loads(run(['ip','-j','address'])),
            'routes4': json.loads(run(['ip','-j','route','show','table','all'])),
            'routes6': json.loads(run(['ip','-j','-6','route','show','table','all'])),
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'forward4': Path('/proc/sys/net/ipv4/ip_forward').read_text().strip(),
            'forward6': Path('/proc/sys/net/ipv6/conf/all/forwarding').read_text().strip(),
            'ports': table('Port', '_uuid,name,vlan_mode,tag,trunks'),
            'interfaces': table('Interface', 'name,ofport,error'),
            'bridges': table('Bridge', 'name,datapath_type,fail_mode'),
            'mirrors': table('Mirror', 'name,select_all,select_src_port,select_dst_port,select_vlan,output_port'),
            'show': run(['ovs-vsctl','show']).decode()}


def check(s, mirror=False):
    assert s['hostname'] == 'soc-core-l2' and 'Open vSwitch) 3.3.9\n' in s['version']
    assert s['services'].split() == ['active']*3
    assert s['forward4'] == s['forward6'] == '0'
    assert {x['ifname']:x['address'] for x in s['links'] if x['ifname'].startswith('ens')} == {
        'ens'+str(i+3): '02:53:45:f2:19:'+format(i, '02x') for i in range(8)}
    assert all(not x['addr_info'] for x in s['addresses'] if x['ifname'] in DATA+['ens10', BR])
    assert 'UP' in next(x['flags'] for x in s['links'] if x['ifname']==BR), 'Bridge not administratively UP'
    assert all(r.get('dst')!='default' and not r.get('gateway') for r in s.get('routes4',[])+s.get('routes6',[])), 'Unexpected gateway/default route'
    assert len(s['bridges']) == 1 and s['bridges'][0]['name'] == BR
    assert s['bridges'][0]['datapath_type'] == 'system' and s['bridges'][0]['fail_mode'] == 'standalone'
    ports = {x['name']:x for x in s['ports']}
    assert set(ports) == set(DATA+[BR]+(['ens10'] if mirror else []))
    for name, vid in zip(DATA[:5]+[BR], VLAN+[99]):
        assert ports[name]['vlan_mode'] == 'access' and ports[name]['tag'] == vid and ports[name]['trunks'] == []
    for name in ['ens8','ens9']:
        assert ports[name]['vlan_mode'] == 'trunk' and ports[name]['tag'] == []
        assert sorted(ports[name]['trunks']) == VLAN
    assert {x['name'] for x in s['interfaces']} == set(ports)
    assert all(isinstance(x['ofport'], int) and x['ofport'] > 0 and x['error'] == [] for x in s['interfaces'])
    assert len(s['mirrors']) == int(mirror)
    if mirror:
        m = s['mirrors'][0]
        assert m['name'] == 'span-suricata' and not m['select_all']
        assert len(m['select_src_port']) == 7 and m['select_dst_port'] == [] and sorted(m['select_vlan']) == VLAN
        assert set(m['select_src_port']) == {ports[x]['_uuid'] for x in DATA}
        assert m['output_port'] == ports['ens10']['_uuid']
        assert ports['ens10']['vlan_mode'] == 'trunk' and ports['ens10']['tag'] == []
        assert sorted(ports['ens10']['trunks']) == VLAN


def backup():
    before = state()
    check(before)
    save('before.json', before)
    target = WORK/'ovsdb.before'
    assert not target.exists()
    command = ['ovsdb-client','backup',SOCKET,'Open_vSwitch']
    process = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    with (WORK/'commands.jsonl').open('a') as log:
        log.write(json.dumps({'args':command,'rc':process.returncode,'stdout':'Binary database retained root-only, not logged'})+'\n')
    assert process.returncode == 0, 'OVSDB backup failed'
    raw = process.stdout
    with target.open('xb') as f:
        f.write(raw)
    os.chmod(target, 0o600)
    assert run(['ovsdb-tool','db-version',str(target)]).decode().strip() == '8.5.1'
    run(['ovsdb-tool','compact',str(target),str(WORK/'ovsdb.validated')])
    save('backup-metadata.json', {'path':str(target), 'sha256':hashlib.sha256(raw).hexdigest(),
                                'bytes':len(raw), 'schema':'8.5.1'})


def restore():
    before = json.loads((WORK/'before.json').read_text())
    check(before)
    current = state()
    assert current['hostname'] == before['hostname'] and current['version'] == before['version']
    assert {x['ifname']:x['address'] for x in current['links'] if x['ifname'].startswith('ens')} == {
        x['ifname']:x['address'] for x in before['links'] if x['ifname'].startswith('ens')}
    assert {x['name'] for x in current['bridges']} == {BR}, 'Unexpected bridge; stop rollback'
    assert {x['name'] for x in current['ports']} <= set(DATA+[BR,'ens10']), 'Unexpected port; stop rollback'
    save('before-rollback.json',current)
    restore_persistence()
    raw = (WORK/'ovsdb.before').read_bytes()
    meta = json.loads((WORK/'backup-metadata.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == meta['sha256']
    # Binary DB is never logged. Restore via stdin; original files remain intact.
    run(['ovsdb-client','restore',SOCKET,'Open_vSwitch'],input=raw)
    flags = next(x['flags'] for x in before['links'] if x['ifname'] == 'ens10')
    run(['ip','link','set','dev','ens10','up' if 'UP' in flags else 'down'])
    after = state()
    save('restored.json',after)
    check(after)
    assert before['forward4'] == after['forward4'] and before['forward6'] == after['forward6']
    for key in ['addresses','routes4','routes6']:
        assert before[key]==after[key], 'Rollback network state mismatch: '+key
    save('rollback-result.json', {'configuration_restored':True, 'note':'OVS row UUIDs may change; network persistence files not changed by this script'})


def mirror():
    assert (WORK/'backup-metadata.json').is_file()
    current = state()
    check(current)
    before = json.loads((WORK/'before.json').read_text())
    for key in ['addresses','routes4','routes6','forward4','forward6']:
        assert current[key] == before[key], 'Baseline changed since backup: '+key
    command = ['ovs-vsctl','--timeout=10','--','add-port',BR,'ens10','--','set','Port','ens10',
               'vlan_mode=trunk','trunks=30,40,50,60,99']
    for i, name in enumerate(DATA+['ens10']):
        command += ['--','--id=@p'+str(i),'get','Port',name]
    command += ['--','--id=@m','create','Mirror','name=span-suricata','select_all=false',
                'select_src_port='+','.join('@p'+str(i) for i in range(7)),
                'select_dst_port=[]','select_vlan=30,40,50,60,99','output_port=@p7',
                '--','set','Bridge',BR,'mirrors=@m']
    try:
        run(command)
        run(['ip','link','set','dev','ens10','up'])
        s = state()
        save('after.json',s)
        check(s,mirror=True)
        save('result.json',{'static_mirror_verified':True,'traffic_tested':False})
    except Exception as exc:
        save('mirror-failure.json',{'error_type':type(exc).__name__,'rollback_attempted':True})
        try:
            restore()
        except Exception as rollback_error:
            save('rollback-failure.json',{'error_type':type(rollback_error).__name__,'manual_console_required':True})
            raise RuntimeError('Mirror failed and rollback could not be verified; stop, preserve logs') from exc
        raise


def restore_persistence():
    registry = WORK/'persistence-files.json'
    if not registry.exists():
        return
    data = json.loads(registry.read_text())
    for entry in data:
        path=Path(entry['target'])
        if path.exists():
            assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'], 'Persistence file changed; stop before disabling'
    run(['systemctl','disable','--now','soc-core-l2-noip.service'],check=False)
    for entry in data:
        path = Path(entry['target'])
        if path.exists():
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], 'Persistence file changed; manual rollback needed'
            destination = WORK/('retained-'+path.name)
            assert not destination.exists()
            path.rename(destination)
    run(['systemctl','daemon-reload'])


def persist():
    s = state()
    check(s,mirror=True)
    sources = [(Path(__file__).parent/'soc-core-l2-noip.service',Path('/etc/systemd/system/soc-core-l2-noip.service'),0o644),
               (Path(__file__).parent/'soc-core-l2-noip.sh',Path('/usr/local/sbin/soc-core-l2-noip.sh'),0o755)]
    assert not (WORK/'persistence-files.json').exists()
    for source,target,mode in sources:
        assert source.is_file() and not target.exists() and not target.is_symlink(), 'Existing persistence file; stop'
    save('before-persistence.json',s)
    entries=[]
    try:
        for source,target,mode in sources:
            # Record ownership/hash before creation, so partial failure is recoverable.
            entries.append({'target':str(target),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
            save('persistence-files.json',entries)
            with target.open('xb') as f:
                f.write(source.read_bytes())
            os.chmod(target,mode)
        run(['sh','-n','/usr/local/sbin/soc-core-l2-noip.sh'])
        run(['systemctl','daemon-reload'])
        run(['systemctl','enable','--now','soc-core-l2-noip.service'])
        check(state(),mirror=True)
    except Exception:
        restore_persistence()
        raise


def main():
    global WORK
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['backup','mirror','verify','baseline','persist','rollback'])
    parser.add_argument('--work',type=Path,required=True)
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError('Do not run with Python -O')
    assert os.geteuid() == 0
    assert args.work.parent == Path('/root') and re.fullmatch(r'm2-traffic-[A-Za-z0-9_-]+',args.work.name)
    assert not args.work.is_symlink(), 'Refuse symlink work directory'
    WORK = args.work
    if args.action in ['backup','baseline']:
        WORK.mkdir(mode=0o700,exist_ok=False)
    assert WORK.is_dir() and WORK.stat().st_uid == 0 and WORK.stat().st_mode & 0o077 == 0
    if args.action == 'backup': backup()
    elif args.action == 'mirror': mirror()
    elif args.action == 'rollback': restore()
    elif args.action == 'persist': persist()
    elif args.action == 'baseline':
        s = state()
        save('baseline.json',s)
        check(s)
    else:
        s = state()
        save('verify.json',s)
        check(s,mirror=bool(s['mirrors']))
    public = {'action':args.action,'state':state(),'traffic_tested':False}
    if (WORK/'backup-metadata.json').is_file():
        public['backup'] = json.loads((WORK/'backup-metadata.json').read_text())
    print(json.dumps(public))


if __name__ == '__main__':
    main()
