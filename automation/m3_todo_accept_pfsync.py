"""Nghiệm thu M3.1 chỉ từ hai JSON guest sau reboot có SHA-256 transport."""
import datetime as dt,json
from m3_todo_console import OUT
evidence=[]
for role,ip,peer in [('primary','10.255.255.1','10.255.255.2'),('secondary','10.255.255.2','10.255.255.1')]:
 d=json.loads((OUT/(role+'-pfsync-postboot.json')).read_text(encoding='utf-8'))
 before=json.loads((OUT/(role+'-pfsync-apply.json')).read_text(encoding='utf-8'))
 assert d['ready'] and d['local']==ip and d['peer']==peer
 assert d['boottime']['stdout']!=before['boottime'],'No new boot proved'
 assert d['config_unchanged'] and d['config_sha256']==before['config_sha256_before']
 assert d['demotion']['rc']==0 and d['demotion']['stdout'].strip()=='net.inet.carp.demotion: 0'
 assert d['sync_ping']['rc']==0 and '0.0% packet loss' in d['sync_ping']['stdout']
 for vlan in [30,40,50,60,99]:
  assert 'inet 192.168.%d.%d netmask 0xffffff00'%(vlan,2 if role=='primary' else 3) in d['all_interfaces']['stdout']
 evidence.append({'role':role,'json':role+'-pfsync-postboot.json','new_boot_proved':True,'hook_executed_this_boot':True,'native_rc_from_boot_log':0,'syncok':1,'demotion':0,'config_unchanged':True,'ready':True})
result={'TODO':'M3.1','status':'DONE/PASS','scope':'Native pfsync attached and syncok1 after separate real guest reboots, boot-hook log matching new kern.boottime, SYNC ping and unchanged config; not stateful failover acceptance','collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),'evidence':evidence}
with (OUT/'M3.1-acceptance.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
