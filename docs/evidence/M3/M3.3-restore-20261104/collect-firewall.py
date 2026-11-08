import sys,json
from pathlib import Path
sys.path.insert(0,'automation')
import m3_todo_console as c
c.OUT=Path('docs/evidence/M3/M3.3-restore-20261104')
a=sys.argv[1];d=c.run('OPNsense-'+a,a.lower()+'-runtime-restored', (c.OUT/'firewall-audit.py').read_text(encoding='utf-8'));print(json.dumps({'role':d['role'],'states':[(r['vlan'],r['state']) for r in d['rows']],'demotion':d['demotion'],'hook_this_boot':d['hook_this_boot']}))
