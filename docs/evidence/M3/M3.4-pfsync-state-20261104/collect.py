import sys,json
from pathlib import Path
sys.path.insert(0,'automation')
import m3_todo_console as c
c.OUT=Path('docs/evidence/M3/M3.4-pfsync-state-20261104')
role,phase=sys.argv[1:3];source=(c.OUT/'firewall-audit.py').read_text()
if phase=='before':
 source='src='+repr(source)+'\nexec(src)\npathlib.Path("/root/soc-m34-20261104/audit.py").write_text(src)'
else:source='import pathlib;exec(pathlib.Path("/root/soc-m34-20261104/audit.py").read_text())'
d=c.run('OPNsense-'+role,role.lower()+'-'+phase,source);print(json.dumps({'role':d['role'],'states':[(r['vlan'],r['state']) for r in d['rows']],'demotion':d['demotion'],'pfsync':d['pfsync']},ensure_ascii=True))
