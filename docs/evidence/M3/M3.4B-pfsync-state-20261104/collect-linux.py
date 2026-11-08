import sys,json
from pathlib import Path
sys.path.insert(0,'automation')
import m3_todo_console as c
c.OUT=Path(__file__).parent
which=sys.argv[1];assert which in ['core','endpoint']
node='SOC-Core-L2' if which=='core' else 'Data-Center'
d=c.run(node,which+'-recovery',(c.OUT/(which+'-reader.py')).read_text(encoding='utf-8'))
print(json.dumps({'node':node,'evidence':which+'-recovery.json'},ensure_ascii=True))
