"""Nghiệm thu CARP đúng hai vai trò, đủ năm VLAN, kèm quảng bá protocol112 thật."""
import datetime as dt,json
from m3_todo_console import OUT
assert json.loads((OUT/'M3.1-acceptance.json').read_text(encoding='utf-8'))['status']=='DONE/PASS'
evidence=[]
for role,expected,skew in [('primary','MASTER','0'),('secondary','BACKUP','100')]:
 d=json.loads((OUT/(role+'-carp-verified.json')).read_text(encoding='utf-8'))
 assert d['all_five_pass'] and d['vip_count']==5
 assert len(d['rows'])==5 and {x['vlan'] for x in d['rows']}=={30,40,50,60,99}
 assert all(x['expected_state']==expected and x['persistent']['advskew']==skew for x in d['rows'])
 assert d['demotion']['stdout'].strip()=='net.inet.carp.demotion: 0'
 s=d['pfsync']['stdout'];peer='10.255.255.2' if role=='primary' else '10.255.255.1'
 assert d['pfsync']['rc']==0 and 'UP' in s.splitlines()[0] and 'syncdev: vtnet2' in s and 'syncpeer: '+peer in s and 'syncok: 1' in s
 applied=json.loads((OUT/(role+'-carp-apply.json')).read_text(encoding='utf-8'))
 assert applied['model_save']['protected_sections_unchanged'] and applied['vip_native']['rc']==0 and applied['filter_reload']['rc']==0
 evidence.append(dict(role=role,state=expected,vlans=[30,40,50,60,99],json=role+'-carp-verified.json',pfsync_ready=True))
capture=json.loads((OUT/'carp-advertisements-after.json').read_text(encoding='utf-8'))
seen={p['vhid'] for p in capture['packets'] if p['source']=='192.168.%d.2'%p['vhid'] and p['ttl']==255 and p['destination']=='224.0.0.18' and p['advbase']==1 and p['advskew']==0}
assert seen=={30,40,50,60,99},'Missing real Primary CARP advertisements'
arp=json.loads((OUT/'carp-vip-arp-after.json').read_text(encoding='utf-8'))
assert len(arp['rows'])==5 and all(x['vip_reply_seen'] and x['primary_seen'] and x['secondary_seen'] for x in arp['rows'])
d={'TODO':'M3.2','status':'DONE/PASS','collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'evidence':evidence,'protocol112_advertisements_vhids':sorted(seen),'capture':'carp-advertisements-after.json','vip_arp_evidence':'carp-vip-arp-after.json','scope':'Five configured VLANs, persistent parameters and live MASTER/BACKUP roles; not failover/NAT/DHCP/WAN acceptance','failover_tested':False}
with (OUT/'M3.2-acceptance.json').open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
print(json.dumps(d,ensure_ascii=False))
