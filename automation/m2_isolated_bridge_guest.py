"""Thực thi trong SOC-Core-L2 với root; phạm vi 7 cổng, không mirror/IP/forwarding.

prepare: kiểm tra xung đột, backup OVSDB online vào root-only, lập rollback.
apply: tạo bridge cô lập, xác minh; nếu lỗi sau commit thì hoàn nguyên snapshot.
verify: chỉ đọc. Chưa kiểm thử lưu lượng hoặc restart.
"""
import argparse
import configparser
import datetime as dt
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

WORK = Path(__file__).resolve().parent
BR = 'br-core-l2'
SOCK = 'unix:/var/run/openvswitch/db.sock'
VLAN = [30,40,50,60,99]
NIC_MAC = {'ens'+str(i+3):'02:53:45:f2:19:'+format(i,'02x') for i in range(8)}

def save(name,data):
    (WORK/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def run(args,check=True):
    result = subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=35,
                            env={**os.environ,'LC_ALL':'C','SYSTEMD_PAGER':'cat'})
    record = {'guest_time_untrusted':dt.datetime.now(dt.timezone.utc).isoformat(),
              'args':args,'rc':result.returncode,'output':result.stdout}
    with (WORK/'commands.jsonl').open('a') as stream:stream.write(json.dumps(record)+'\n')
    print('$ '+' '.join(args)+'\n'+result.stdout+'RC='+str(result.returncode),flush=True)
    if check and result.returncode:raise RuntimeError('Command failed: '+' '.join(args))
    return result.stdout

def table(name,columns):
    raw = json.loads(run(['ovs-vsctl','--timeout=10','--format=json','--columns='+columns,'list',name]))
    def value(v):
        if isinstance(v,list) and len(v)==2:
            if v[0] in ['uuid','named-uuid']:return v[1]
            if v[0]=='set':return [value(x) for x in v[1]]
            if v[0]=='map':return dict(v[1])
        return v
    return [dict(zip(raw['headings'],[value(v) for v in row])) for row in raw['data']]

def state(label):
    result = {'hostname':run(['hostname']).strip(),'version':run(['ovs-vsctl','--version']),
      'services':run(['systemctl','is-active','openvswitch-switch','ovsdb-server','ovs-vswitchd']),
      'links':json.loads(run(['ip','-j','link','show'])),
      'addresses':json.loads(run(['ip','-j','address','show'])),
      'routes4':json.loads(run(['ip','-j','route','show','table','all'])),
      'routes6':json.loads(run(['ip','-j','-6','route','show','table','all'])),
      'forward4':Path('/proc/sys/net/ipv4/ip_forward').read_text().strip(),
      'forward6':Path('/proc/sys/net/ipv6/conf/all/forwarding').read_text().strip(),
      'bridges':table('Bridge','name,datapath_type,fail_mode,ports,mirrors,controller'),
      'ports':table('Port','_uuid,name,vlan_mode,tag,trunks,interfaces'),
      'interfaces':table('Interface','_uuid,name,type,ofport,error,admin_state,link_state'),
      'mirrors':table('Mirror','name'),
      'show':run(['ovs-vsctl','--timeout=10','show'])}
    save(label+'.json',result)
    return result

def identity(s):
    assert s['hostname']=='soc-core-l2', 'Wrong guest'
    assert 'Open vSwitch) 3.3.9\n' in s['version'], 'Unexpected OVS version'
    assert s['services'].split()==['active','active','active'], 'Services not active'
    mac = {x['ifname']:x['address'] for x in s['links'] if x['ifname'] in NIC_MAC}
    assert mac == NIC_MAC, 'NIC mapping changed'
    assert s['forward4']==s['forward6']=='0', 'Unexpected forwarding state'

def network_files():
    output=[]
    for root in ['/etc/systemd/network','/run/systemd/network','/usr/lib/systemd/network']:
        for path in Path(root).glob('*.network'):
            parser=configparser.ConfigParser(strict=False,interpolation=None)
            parser.read(path)
            match=dict(parser['Match']) if parser.has_section('Match') else {}
            selected={k:v for k,v in dict(parser['Network']).items() if k.lower() in
               ['dhcp','linklocaladdressing','ipv6acceptra','address','gateway']} if parser.has_section('Network') else {}
            output.append({'path':str(path),'match':match,'network':selected})
            names=match.get('name','').split()
            if any(fnmatch.fnmatch(BR,n) for n in names if not n.startswith('!')):
                raise RuntimeError('Network manager configuration matches new bridge: '+str(path))
    save('network-manager-summary.json',output)
    return output

def prepare():
    before=state('before')
    identity(before)
    assert not before['bridges'] and not before['ports'] and not before['interfaces'] and not before['mirrors'], 'Existing OVS configuration'
    assert BR not in [x['ifname'] for x in before['links']], 'Existing Linux interface'
    assert all(not x['addr_info'] for x in before['addresses'] if x['ifname'] in NIC_MAC), 'Existing NIC IP'
    network_files()
    backup=WORK/'ovsdb.before'
    assert not backup.exists(), 'Do not overwrite backup'
    with backup.open('xb') as stream:
        r=subprocess.run(['ovsdb-client','backup',SOCK,'Open_vSwitch'],stdout=stream,stderr=subprocess.PIPE,timeout=20)
    assert r.returncode==0, r.stderr.decode()
    os.chmod(backup,0o600)
    dbname=run(['ovsdb-tool','db-name',str(backup)]).strip()
    version=run(['ovsdb-tool','db-version',str(backup)]).strip()
    server_version=run(['ovsdb-client','get-schema-version',SOCK,'Open_vSwitch']).strip()
    assert dbname=='Open_vSwitch' and version==server_version=='8.5.1'
    # Compact chỉ đọc bản backup và ghi bản kiểm tra, không ghi DB đang chạy.
    run(['ovsdb-tool','compact',str(backup),str(WORK/'ovsdb.backup-validated')])
    metadata={'path':str(backup),'sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),
              'bytes':backup.stat().st_size,'mode':oct(backup.stat().st_mode&0o777),'schema':version,
              'root_only_directory':oct(WORK.stat().st_mode&0o777)}
    save('backup-metadata.json',metadata)
    (WORK/'rollback.sh').write_text('#!/bin/sh\nset -eu\n[ "$(hostname)" = soc-core-l2 ]\n'
      +'ovsdb-client restore '+SOCK+' Open_vSwitch < '+str(backup)+'\novs-vsctl --timeout=10 show\n')
    os.chmod(WORK/'rollback.sh',0o700)
    print('PREPARE_OK '+json.dumps(metadata),flush=True)

def transaction():
    args=['ovs-vsctl','--timeout=15','--','add-br',BR,'--','set','Bridge',BR,
          'datapath_type=system','fail_mode=standalone','--','set','Port',BR,'vlan_mode=access','tag=99']
    for nic,vid in zip(['ens3','ens4','ens5','ens6','ens7'],VLAN):
        args += ['--','add-port',BR,nic,'--','set','Port',nic,'vlan_mode=access','tag='+str(vid)]
    for nic in ['ens8','ens9']:
        args += ['--','add-port',BR,nic,'--','set','Port',nic,'vlan_mode=trunk','trunks=30,40,50,60,99']
    return args

def single(v):
    return v[0] if isinstance(v,list) and len(v)==1 else v

def verify():
    now=state('after')
    before=json.loads((WORK/'before.json').read_text())
    identity(now)
    assert len(now['bridges'])==1 and now['bridges'][0]['name']==BR
    bridge=now['bridges'][0]
    assert bridge['datapath_type']=='system' and single(bridge['fail_mode'])=='standalone'
    assert not bridge['mirrors'] and not bridge['controller'] and not now['mirrors']
    ports={x['name']:x for x in now['ports']}
    assert set(ports)=={BR,'ens3','ens4','ens5','ens6','ens7','ens8','ens9'}
    for nic,vid in [(BR,99),*zip(['ens3','ens4','ens5','ens6','ens7'],VLAN)]:
        assert single(ports[nic]['vlan_mode'])=='access' and single(ports[nic]['tag'])==vid
        assert not ports[nic]['trunks']
    for nic in ['ens8','ens9']:
        assert single(ports[nic]['vlan_mode'])=='trunk' and sorted(ports[nic]['trunks'])==VLAN and not ports[nic]['tag']
    for port in ports.values():assert not isinstance(port['interfaces'],list) or len(port['interfaces'])==1
    interfaces={x['name']:x for x in now['interfaces']}
    assert set(interfaces)==set(ports) and all(not x['error'] and int(single(x['ofport']))>=0 for x in interfaces.values())
    assert all(not x['addr_info'] for x in now['addresses'] if x['ifname'] in {*NIC_MAC,BR}), 'Unexpected IP on Core'
    assert before['routes4']==now['routes4'] and before['routes6']==now['routes6'], 'Routing changed'
    old10=next(x for x in before['links'] if x['ifname']=='ens10')
    new10=next(x for x in now['links'] if x['ifname']=='ens10')
    assert old10==new10, 'ens10 changed'
    brlink=next(x for x in now['links'] if x['ifname']==BR)
    assert 'UP' in brlink['flags'], 'Bridge administratively down'
    (WORK/'datapath.txt').write_text(run(['ovs-appctl','dpif/show']))
    (WORK/'flows.txt').write_text(run(['ovs-ofctl','dump-flows',BR]))
    (WORK/'services.txt').write_text(run(['systemctl','--no-pager','status','openvswitch-switch','ovsdb-server','ovs-vswitchd']))
    (WORK/'networkctl.txt').write_text(run(['networkctl','list','--no-pager']))
    save('result.json',{'configuration_verified':True,'traffic_tested':False,'mirror_created':False,
                       'ens10_unchanged':True,'forwarding_unchanged':True,'no_core_ip_or_route':True,
                       'restart_tested':False,'port_count_excluding_local':7})
    print('VERIFY_OK: isolated bridge; 5 access, 2 trunk; ens10 untouched; no traffic test',flush=True)

def apply():
    baseline=json.loads((WORK/'before.json').read_text())
    current=state('preapply')
    identity(current)
    assert all(not current[k] for k in ['bridges','ports','interfaces','mirrors']), 'Conflict: stop before transaction'
    assert current['addresses']==baseline['addresses'] and current['links']==baseline['links'], 'Guest network changed'
    metadata=json.loads((WORK/'backup-metadata.json').read_text())
    assert hashlib.sha256((WORK/'ovsdb.before').read_bytes()).hexdigest()==metadata['sha256']
    args=transaction();save('applied-transaction.json',args)
    attempted=False
    try:
        attempted=True
        run(args)
        # Ngăn kernel sinh IPv6 link-local trên interface mới, không sửa forwarding.
        run(['ip','link','set','dev',BR,'addrgenmode','none'])
        # Chỉ tắt host IPv6 trên bridge mới; OVS vẫn chuyển frame Ethernet IPv6.
        run(['sysctl','-w','net.ipv6.conf.'+BR+'.disable_ipv6=1'])
        # Chỉ xóa link-local tự sinh trên interface mới do chính giao dịch vừa tạo.
        addresses=json.loads(run(['ip','-j','address','show','dev',BR]))[0]['addr_info']
        assert all(a['family']=='inet6' and a['scope']=='link' for a in addresses), 'Unexpected address on new bridge'
        if addresses:run(['ip','-6','addr','flush','dev',BR,'scope','link'])
        run(['ip','link','set','dev',BR,'up'])
        time.sleep(2)
        verify()
    except Exception as exc:
        save('failure.json',{'error':str(exc),'transaction_attempted':attempted})
        if attempted:
            with (WORK/'ovsdb.before').open('rb') as stream:
                r=subprocess.run(['ovsdb-client','restore',SOCK,'Open_vSwitch'],stdin=stream,capture_output=True,timeout=20)
            save('rollback-result.json',{'rc':r.returncode,'stdout':r.stdout.decode(),'stderr':r.stderr.decode()})
            assert r.returncode==0,'ROLLBACK FAILED; stop and report'
            time.sleep(2)
            restored=state('restored')
            assert all(not restored[k] for k in ['bridges','ports','interfaces','mirrors']), 'Rollback incomplete'
            identity(restored)
            assert restored['routes4']==baseline['routes4'] and restored['routes6']==baseline['routes6'], 'Routes not restored'
        raise

def main():
    assert os.geteuid()==0 and subprocess.check_output(['hostname'],text=True).strip()=='soc-core-l2'
    assert WORK.stat().st_mode&0o777==0o700, 'Work directory must be root-only'
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','apply','verify'])
    options=parser.parse_args()
    {'prepare':prepare,'apply':apply,'verify':verify}[options.action]()

if __name__=='__main__':main()
