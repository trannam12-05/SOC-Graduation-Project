"""Console read-only collector; Primary uses observed inverted alphabet case."""
import sys,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'automation'))
import capture_m2_core_console as cap
p=argparse.ArgumentParser();p.add_argument('--node',choices=['Primary','Secondary'],required=True);p.add_argument('--label',required=True);p.add_argument('--command-file',required=True);p.add_argument('--stdin-mode',action='store_true');a=p.parse_args()
cap.REMOTE=cap.REMOTE.replace("n.get('name') == 'SOC-Core-L2'","n.get('name') == 'OPNsense-"+a.node+"'")
old='key = ord(char)'
assert cap.REMOTE.count(old)==1
cap.REMOTE=cap.REMOTE.replace(old,"key = ord(shifted.get(char, char.lower() if char.isupper() else char))")
cap.REMOTE=cap.REMOTE.replace("facts['guest_command_sent'] = command","facts['guest_command_sent'] = command\n        facts['input_transport_note'] = 'Physical base key with Shift for uppercase/punctuation; no guest configuration write'")
if a.stdin_mode:
 begin=cap.REMOTE.index("        # Ctrl+L")
 end=cap.REMOTE.index("        for char in command:",begin)
 cap.REMOTE=cap.REMOTE[:begin]+cap.REMOTE[end:]
# Longer timeout only for deliberate console typing; no guest operation timeout removed.
import inspect
source=inspect.getsource(cap.main).replace('timeout=55','timeout=240')
exec(source,cap.__dict__)
sys.argv=['capture','--output-dir',str(Path(__file__).parent),'--label',a.label,'--command-file',a.command_file]
cap.main()




