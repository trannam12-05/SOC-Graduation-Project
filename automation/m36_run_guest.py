"""Chạy payload M3.6 qua console đã xác thực và lưu minh chứng tách biệt."""
from pathlib import Path
import json
import sys

import m3_todo_console as transport
from topology_remote import ROOT

OUT = ROOT / "docs/evidence/M3/M3.6-completion-20261106"
OUT.mkdir(parents=True, exist_ok=True)
transport.OUT = OUT

node, label, source = sys.argv[1:]
result = transport.run(node, label, Path(source).read_text(encoding="utf-8"))
print(json.dumps(result, ensure_ascii=False))
