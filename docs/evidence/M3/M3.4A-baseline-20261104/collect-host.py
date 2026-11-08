"""Chỉ kiểm kê host và kiểm tra baseline; không tạo flow TCP hay đổi vai CARP."""
import ast,concurrent.futures,datetime as dt,json,sys
from pathlib import Path
sys.path.insert(0,'automation')
from topology_remote import remote
from m3_resource_optimization import CODE as HOST
from m3_resource_l2_probe import CODE as ARP
from ha_pfsync_capture import CODE as PFSYNC
OUT=Path(__file__).parent
def collect(label,code):
    started=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    d=json.loads(remote(code,timeout=55));d['collector_time_start']=started;d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    with (OUT/(label+'.json')).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
    return dict(evidence=label,running=d.get('running'),packets=d.get('packet_count',len(d.get('packets',[]))))
if sys.argv[1].startswith('network'):
    tree=ast.parse(Path('automation/m3_todo_carp_capture.py').read_text(encoding='utf-8'))
    CARP=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='code' for t in n.targets))
    prefix='' if sys.argv[1]=='network' else 'final-'
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for d in pool.map(lambda x:collect(*x),[(prefix+'baseline-arp',ARP),(prefix+'baseline-carp',CARP),(prefix+'baseline-pfsync-packets',PFSYNC)]):print(json.dumps(d),flush=True)
else:print(json.dumps(collect(sys.argv[1],HOST)))
