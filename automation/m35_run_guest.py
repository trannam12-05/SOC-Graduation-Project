"""Chạy payload M3.5 qua console đã xác thực và lưu evidence riêng."""
from pathlib import Path
import json,sys
import m3_todo_console as transport
from topology_remote import ROOT

OUT=ROOT/'docs/evidence/M3/M3.5-network-services-20261105'
OUT.mkdir(parents=True,exist_ok=True)
transport.OUT=OUT
node,label,source=sys.argv[1:]
d=transport.run(node,label,Path(source).read_text(encoding='utf-8'))
print(json.dumps(d,ensure_ascii=False))
