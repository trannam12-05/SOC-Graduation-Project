import json,datetime as dt
from pathlib import Path
P=Path(__file__).parent
def read(n):return json.loads((P/(n+'.json')).read_text(encoding='utf-8'))
h=read('recovery-host');before=read('host-before');expected={'SOC-Core-L2':1024,'OPNsense-Primary':2048,'OPNsense-Secondary':2048,'Data-Center':1024}
assert {n['name']:int(n['ram']) for n in h['running']}==expected
original={n['name']:n['pid'] for n in before['running']}
assert all(n['pid']==original[n['name']] for n in h['running'] if n['name']!='OPNsense-Primary')
norm=lambda h:{n['name']:{k:v for k,v in n.items() if k not in ['left','top']} for n in h['nodes']}
assert norm(h)==norm(before),'Topology/resource/interface changed'
roles={}
for role,state,local,peer in [('primary','MASTER','10.255.255.1','10.255.255.2'),('secondary','BACKUP','10.255.255.2','10.255.255.1')]:
 d=read(role+'-recovery');old=read(role+'-before')
 assert len(d['rows'])==5 and {r['vlan'] for r in d['rows']}=={30,40,50,60,99}
 for r in d['rows']:
  assert r['state']==[state] and r['physical_ip_ok'] and r['vip_ok'] and r['up'] and r['active'],r
  assert r['persistent']==next(o['persistent'] for o in old['rows'] if o['vlan']==r['vlan'])
 s=d['pfsync']['out'];assert d['pfsync']['rc']==0 and 'UP' in s.splitlines()[0] and 'RUNNING' in s.splitlines()[0]
 assert all(v in s for v in ['syncdev: vtnet2','syncpeer: '+peer,'syncok: 1']),s
 assert d['demotion']['out'].strip()=='0' and d['ping']['rc']==0 and '2 packets received' in d['ping']['out']
 assert 'inet '+local+' netmask 0xfffffffc' in d['sync']['out']
 assert d['hook_this_boot'] and d['hook_native_rc0'] and d['config_unchanged']
 assert d['config_sha256']==d['backup_sha256']==old['config_sha256']
 if role=='primary':assert d['boottime']['out']!=old['boottime']['out']
 else:assert d['boottime']['out']==old['boottime']['out']
 roles[role]={'CARP':state,'vlans':[30,40,50,60,99],'VIPs_correct':True,'pfsync_ready':True,'syncok':1,'demotion':0,'SYNC_ping':'2/2','config_unchanged':True}
core=read('core-recovery')
assert core['services']['out'].split()==['active']*3
assert core['ipv4_forwarding']['out'].strip()==core['ipv6_forwarding']['out'].strip()=='0'
assert 'actions=NORMAL' in core['flow']['out'] and core['ports']['rc']==0
assert not [a for n in json.loads(core['addresses']['out']) if n['ifname']!='lo' for a in n.get('addr_info',[])]
t=json.loads(core['ports']['out']);ports={r[0]:dict(zip(t['headings'],r)) for r in t['data']}
for n,v in zip(['ens3','ens4','ens5','ens6','ens7'],[30,40,50,60,99]):assert ports[n]['tag']==v and ports[n]['vlan_mode']=='access'
for n in ['ens8','ens9']:assert set(ports[n]['trunks'][1])=={30,40,50,60,99} and ports[n]['vlan_mode']=='trunk'
arp=read('recovery-arp');assert len(arp['rows'])==5 and all(r['primary_seen'] and r['secondary_seen'] and r['vip_conflict_seen'] for r in arp['rows'])
carp=read('recovery-carp');assert {r['vhid'] for r in carp['packets'] if r['source']=='192.168.%d.2'%r['vhid'] and r['advskew']==0}=={30,40,50,60,99}
assert read('recovery-pfsync')['both_directions']
ep=read('endpoint-recovery');assert ep['http_service']['out'].strip()=='active' and '192.168.30.10:8000' in ep['listening']['out']
assert any(r.get('gateway')=='192.168.30.1' for r in json.loads(ep['route_to_client']['out']))
d={'status':'PASS','collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'firewalls':roles,'core_L2_OVS_VLAN':'PASS','VIPs':'PASS 5 VLAN','endpoint':'Existing DC IP/service and scoped return route present','native_pfsync_reapply_during_recovery':False,'Core_Secondary_DC_pids_unchanged':True,'primary_new_boot':True,'node_resource_interface_mapping_unchanged':True,'lab_byte_hash_unchanged':h['lab_sha256']==before['lab_sha256']}
with (P/'recovery-acceptance.json').open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
print(json.dumps(d,ensure_ascii=True))
