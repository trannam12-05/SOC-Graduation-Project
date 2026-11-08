import sys,json
from pathlib import Path
sys.path.insert(0,'automation')
import m3_todo_console as c
c.OUT=Path(__file__).parent
role,phase=sys.argv[1:3]
d=c.run('OPNsense-'+role,role.lower()+'-state-'+phase,(c.OUT/'state-reader.py').read_text(encoding='utf-8'))
print(json.dumps({'role':role,'phase':phase,'blocks':d['blocks']},ensure_ascii=True))
