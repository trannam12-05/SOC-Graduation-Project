"""Thu minh chứng host hiện tại, không đổi cấu hình hoặc vòng đời node."""
import datetime as dt,json,sys
from topology_remote import remote
from m3_todo_console import OUT
from m3_resource_optimization import CODE as RESOURCE_CODE
from ha_pfsync_capture import CODE as PACKET_CODE
label=sys.argv[1];code=PACKET_CODE if '--pfsync-packets' in sys.argv else RESOURCE_CODE
# Resource collector gốc tạo một bản backup metadata root-only; giữ nguyên guard.
d=json.loads(remote(code,timeout=55));d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
with (OUT/(label+'.json')).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
print(json.dumps({'evidence':label,'collector_time':d['collector_time'],'packet_count':d.get('packet_count'),'both_directions':d.get('both_directions'),'running':d.get('running')},ensure_ascii=False))
