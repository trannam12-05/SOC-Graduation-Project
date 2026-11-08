"""Quan sát hữu hạn host và đọc bản ghi bootstrap công khai lịch sử."""
import json,sys
from topology_remote import remote
from m3_resource_optimization import save
CODE=r'''
import pathlib,json,subprocess,os
v=subprocess.run(['vmstat','1','20'],capture_output=True,text=True,timeout=25)
base=pathlib.Path('/opt/unetlab/tmp/0/f39cfc8c-5eaf-461e-bb0c-60b5fde848b7');historical=[]
for id in ['4','7','9','10']:
 p=base/id/'serial.log'
 if p.exists():
  for l in p.read_text(errors='replace').splitlines():
   if l.startswith('SOC_BOOTSTRAP_RESULT '):
    try:historical.append({'node_id':id,'historical_not_current_runtime':True,'data':json.loads(l.split(' ',1)[1])})
    except ValueError:pass
print(json.dumps({'vmstat':v.stdout,'historical_bootstrap':historical,'meminfo':pathlib.Path('/proc/meminfo').read_text(),'loadavg':os.getloadavg()}))
'''
d=save(sys.argv[1],json.loads(remote(CODE,timeout=35)))
print(json.dumps({'vmstat':d['vmstat'],'historical_count':len(d['historical_bootstrap'])}))
