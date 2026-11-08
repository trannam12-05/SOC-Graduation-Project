"""Thu checkpoint/ARP/CARP thật; riêng boot-primary chỉ start node 1 đã duyệt."""
import ast
import concurrent.futures
import datetime as dt
import json
import sys
from pathlib import Path
sys.path.insert(0,'automation')
from topology_remote import remote
from m3_resource_optimization import CODE as HOST
from m3_resource_l2_probe import CODE as ARP
from ha_pfsync_capture import CODE as PFSYNC

OUT=Path(__file__).parent
phase=sys.argv[1]
def collect(name,code,timeout=55):
    start=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    d=json.loads(remote(code,timeout=timeout))
    d['collector_time_start']=start
    d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    with (OUT/(name+'.json')).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
    return {'evidence':name,'running':d.get('running'),'packet_count':d.get('packet_count',len(d.get('packets',[])))}

if phase=='boot-primary':
    import runpy,m3_resource_optimization as m
    assert json.loads((OUT/'failover-acceptance.json').read_text())['status']=='PASS'
    m.OUT=OUT;sys.argv=['start','OPNsense-Primary']
    runpy.run_path('automation/m3_resource_start.py',run_name='__main__')
elif phase.endswith('-host'):
    print(json.dumps(collect(phase,HOST)))
else:
    tree=ast.parse(Path('automation/m3_todo_carp_capture.py').read_text(encoding='utf-8'))
    CARP=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='code' for t in n.targets))
    tasks=[(phase+'-arp',ARP),(phase+'-carp',CARP)]
    if not phase.startswith('failover'):tasks.append((phase+'-pfsync',PFSYNC))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for item in pool.map(lambda pair:collect(*pair),tasks):print(json.dumps(item),flush=True)
