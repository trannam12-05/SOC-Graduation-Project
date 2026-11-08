"""Console resource: dùng phím vật lý đã kiểm chứng, lưu ảnh thật."""
import sys, argparse, inspect
import capture_m2_core_console as cap
p=argparse.ArgumentParser();p.add_argument('node');p.add_argument('label');p.add_argument('--command-file');p.add_argument('--output-dir',default='docs/evidence/M3/resource-optimization-20261103');a=p.parse_args()
cap.REMOTE=cap.REMOTE.replace("n.get('name') == 'SOC-Core-L2'","n.get('name') == "+repr(a.node))
cap.REMOTE=cap.REMOTE.replace('key = ord(char)',"key = ord(shifted.get(char, char.lower() if char.isupper() else char))")
exec(inspect.getsource(cap.main).replace('timeout=55','timeout=240'),cap.__dict__)
sys.argv=['capture','--output-dir',a.output_dir,'--label',a.label]+(['--command-file',a.command_file] if a.command_file else [])
cap.main()
