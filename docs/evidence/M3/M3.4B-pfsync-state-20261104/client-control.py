"""Điều khiển một client test hữu hạn; không cấu hình host network."""
import datetime as dt,json,sys
from pathlib import Path
sys.path.insert(0,'automation')
from topology_remote import remote
OUT=Path(__file__).parent
action=sys.argv[1];label=sys.argv[2] if len(sys.argv)>2 else action
prefix="import pathlib,json,subprocess,sys,os,time;os.umask(0o077);p=pathlib.Path('/root/soc-m34b-20261104')\n"
if action=='start':
    source=(OUT/'tcp-client.py').read_text(encoding='utf-8');compile(source,'client','exec')
    code=prefix+"p.mkdir(mode=0o700,exist_ok=True)\nassert not (p/'client.py').exists(),'Refuse duplicate client'\n"
    code+="for f in pathlib.Path('/proc').glob('[0-9]*/cmdline'):\n try:\n  a=f.read_bytes().split(b'\\0');assert not (a and a[0].endswith(b'/vpcs')),'Existing VPCS; do not claim Employee IP'\n except (FileNotFoundError,ProcessLookupError):pass\n"
    code+="(p/'client.py').write_text("+repr(source)+")\n(p/'phase').write_text('before')\nf=(p/'daemon.log').open('x');q=subprocess.Popen([sys.executable,str(p/'client.py'),str(p)],stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True);(p/'client.pid').write_text(str(q.pid));print(json.dumps({'pid':q.pid,'directory':str(p),'one_connection_no_reconnect':True}))"
elif action=='status':
    code=prefix+"d={'live':json.loads((p/'live.json').read_text()) if (p/'live.json').exists() else None,'result':json.loads((p/'client-result.json').read_text()) if (p/'client-result.json').exists() else None,'events':(p/'client-events.jsonl').read_text().splitlines() if (p/'client-events.jsonl').exists() else [],'daemon':(p/'daemon.log').read_text() if (p/'daemon.log').exists() else ''};print(json.dumps(d))"
elif action=='phase':
    value=sys.argv[3];assert value in ['before','failover-start','primary-off','secondary-master']
    code=prefix+"(p/'phase').write_text("+repr(value)+");print(json.dumps({'phase':"+repr(value)+",'host_clock_untrusted':time.time()}))"
elif action=='finish':
    code=prefix+"(p/'finish-request').touch(exist_ok=False);print(json.dumps({'finish_requested':True,'host_clock_untrusted':time.time()}))"
else:raise RuntimeError('Unknown action')
started=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
d=json.loads(remote(code,timeout=30));d['collector_time_start']=started;d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
with (OUT/('client-'+label+'.json')).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
if action=='status':
    d={k:v for k,v in d.items() if k!='events'}
    if d.get('live'):d['live']['steps']=d['live'].get('steps',[])[-4:]
print(json.dumps(d,ensure_ascii=True))
