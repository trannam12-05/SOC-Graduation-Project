import sys,json
from pathlib import Path
sys.path.insert(0,'automation')
import m3_todo_console as c
c.OUT=Path(__file__).parent
role,label=sys.argv[1:3]
d=c.run('OPNsense-'+role,role.lower()+'-'+label,(c.OUT/'firewall-audit.py').read_text(encoding='utf-8'));print(json.dumps({'role':d['role'],'states':[(r['vlan'],r['state']) for r in d['rows']],'demotion':d['demotion'],'pfsync':d['pfsync']},ensure_ascii=True))
