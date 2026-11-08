"""Console M3: key events có thời gian ổn định; không sửa cơ chế xác thực."""
import argparse,sys
import capture_m2_core_console as cap
p=argparse.ArgumentParser();p.add_argument('--node',choices=['OPNsense-Primary','OPNsense-Secondary'],required=True);p.add_argument('--output-dir',required=True);p.add_argument('--label',required=True);p.add_argument('--command-file')
a=p.parse_args()
cap.REMOTE=cap.REMOTE.replace("n.get('name') == 'SOC-Core-L2'","n.get('name') == "+repr(a.node))
# Không dùng clipboard/ghi ảnh giả. Payload có hash trước khi thực thi.
# Dùng đúng nhịp đã kiểm chứng; đợt thử nhanh ban đầu bị mất ký tự và bị chặn trước backup.
sys.argv=[sys.argv[0],'--output-dir',a.output_dir,'--label',a.label]+(['--command-file',a.command_file] if a.command_file else [])
cap.main()
