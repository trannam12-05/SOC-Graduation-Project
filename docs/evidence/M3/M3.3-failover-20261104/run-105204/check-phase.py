"""Nghiệm thu từng pha từ runtime, host và gói thật; không đổi hệ thống."""
import datetime as dt,json,sys
from pathlib import Path
OUT=Path(__file__).parent
phase=sys.argv[1]
label=sys.argv[2] if len(sys.argv)>2 else phase
def read(name):return json.loads((OUT/(name+'.json')).read_text(encoding='utf-8'))
vlans={30,40,50,60,99}
def firewall(role,state,label,ready=True):
    d=read(role+'-'+label);before=read(role+'-before') if label!='before' else d
    assert d['role']==role and len(d['rows'])==5 and {r['vlan'] for r in d['rows']}==vlans
    for row in d['rows']:
        assert row['state']==[state] and all(row[k] for k in ['physical_ip_ok','vip_ok','up','active']),row
        old=next(r for r in before['rows'] if r['vlan']==row['vlan'])
        assert row['persistent']==old['persistent']
        assert row['persistent']['vhid']==str(row['vlan']) and row['persistent']['advbase']=='1'
        assert row['persistent']['advskew']==('0' if role=='primary' else '100')
    assert d['config_unchanged'] and d['config_sha256']==d['backup_sha256']==before['config_sha256']
    if ready:
        p=d['pfsync']['out'];peer='10.255.255.2' if role=='primary' else '10.255.255.1'
        assert d['pfsync']['rc']==0 and 'UP' in p.splitlines()[0] and 'RUNNING' in p.splitlines()[0]
        assert all(x in p for x in ['syncdev: vtnet2','syncpeer: '+peer,'syncok: 1'])
        assert d['demotion']['out'].strip()=='0' and d['ping']['rc']==0
        assert d['hook_this_boot'] and d['hook_native_rc0']
    return d

expected={'SOC-Core-L2':1024,'OPNsense-Primary':2048,'OPNsense-Secondary':2048}
h=read('host-before' if phase=='before' else label+'-host')
actual={n['name']:int(n['ram']) for n in h['running']}
assert actual==({k:v for k,v in expected.items() if k!='OPNsense-Primary'} if phase=='failover' else expected),actual
if phase!='before':
    original={n['name']:n['pid'] for n in read('host-before')['running']}
    assert all(n['pid']==original[n['name']] for n in h['running'] if n['name']!='OPNsense-Primary')
roles={}
if phase=='failover':roles['secondary']=firewall('secondary','MASTER',label,False)
else:
    roles['primary']=firewall('primary','MASTER',label)
    roles['secondary']=firewall('secondary','BACKUP',label)
if phase=='recovery':assert roles['primary']['boottime']['out']!=read('primary-before')['boottime']['out']
a=read(label+'-arp')
assert len(a['rows'])==5 and {r['vlan'] for r in a['rows']}==vlans
assert all(r['secondary_seen'] and r['vip_conflict_seen'] for r in a['rows'])
if phase!='failover':assert all(r['primary_seen'] for r in a['rows'])
for row in a['rows']:
    vip='192.168.%d.1'%row['vlan'];mac='00:00:5e:00:01:%02x'%row['vlan']
    assert any(r['ip']==vip and r['mac']==mac for r in row['responses'])
c=read(label+'-carp');last=3 if phase=='failover' else 2
assert {p['vhid'] for p in c['packets'] if p['source']=='192.168.%d.%d'%(p['vhid'],last) and p['ttl']==255 and p['destination']=='224.0.0.18' and p['advbase']==1}==vlans
if phase!='failover':assert read(label+'-pfsync')['both_directions']
d={'phase':phase,'status':'PASS','collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'roles':{role:{'vlans':[{'vlan':r['vlan'],'state':r['state'][0],'vip_ok':r['vip_ok']} for r in data['rows']],'demotion':data['demotion']['out'].strip(),'pfsync':data['pfsync']['out']} for role,data in roles.items()},'primary_off_confirmed':phase=='failover','core_secondary_pids_unchanged':phase!='before','scope':'CARP roles/VIP and specified readiness; not session preservation or NAT/DHCP'}
with (OUT/(phase+'-acceptance.json')).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
print(json.dumps({'phase':phase,'status':d['status'],'roles':{role:[(r['vlan'],r['state'][0]) for r in data['rows']] for role,data in roles.items()}}))
