import sys,json,datetime as dt
from pathlib import Path
P=Path(__file__).parent
def read(n):return json.loads((P/(n+'.json')).read_text(encoding='utf-8'))
mode=sys.argv[1];a=read('primary-state-before');b=read('secondary-state-before')
def ids(d):
 assert d['pfctl_rc']==0 and d['blocks'] and all(r['established'] and r['id'] and r['creatorid'] for r in d['blocks']),d.get('blocks')
 return {(r['id'],r['creatorid']) for r in d['blocks']}
assert ids(a)==ids(b),'Native state IDs/creator IDs do not match'
assert a['local_sync_ip']=='10.255.255.1' and b['local_sync_ip']=='10.255.255.2'
assert all(r['state']==['MASTER'] and r['vip_ok'] for r in a['carp_all'])
assert all(r['state']==['BACKUP'] and r['vip_ok'] for r in b['carp_all'])
assert all('0:0 pkts' in r['text'] for r in b['blocks']),'Secondary carried traffic before takeover'
d={'status':'PASS','collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'session':'192.168.40.100:44341 -> 192.168.30.10:8000','native_state_ids_creator_ids':sorted(ids(a)),'primary_established':True,'secondary_before_established':True,'secondary_before_counters':'0:0','primary_before':'primary-state-before.json','secondary_before':'secondary-state-before.json'}
name='state-sync-acceptance'
if mode=='after':
 after=read('secondary-state-after-immediate');assert ids(after)==ids(a),'After takeover state differs'
 assert {r['vlan'] for r in after['carp_all']}=={30,40,50,60,99}
 assert all(r['state']==['MASTER'] and r['vip_ok'] for r in after['carp_all'])
 assert after['trigger']=='all five CARP MASTER' and after['trigger_to_state_capture_seconds']<1
 off=read('failover-off-host');assert {r['name'] for r in off['running']}=={'SOC-Core-L2','OPNsense-Secondary','Data-Center'}
 original={r['name']:r['pid'] for r in read('host-before')['running']}
 assert all(r['pid']==original[r['name']] for r in off['running'])
 d.update(secondary_after='secondary-state-after-immediate.json',secondary_after_established=True,secondary_master_five_vlans=True,primary_off_confirmed=True,trigger_to_native_read_seconds=after['trigger_to_state_capture_seconds'],core_secondary_server_pids_unchanged=True)
 name='failover-acceptance'
else:assert mode=='before'
with (P/(name+'.json')).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
print(json.dumps(d,ensure_ascii=True))
