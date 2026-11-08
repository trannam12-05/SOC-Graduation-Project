"""Chụp console thật theo tên node; phím/lệnh chỉ dùng sau khi đã xem ảnh."""
import argparse,sys
import capture_m2_core_console as cap

p=argparse.ArgumentParser();p.add_argument('--node',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--label',required=True)
p.add_argument('--command-file');p.add_argument('--keys',nargs='*',choices=['Enter','Down','Up','Left','Right','Tab','Space','Escape','Eight','Cancel'])
a=p.parse_args()
assert a.node in ['OPNsense-Primary','OPNsense-Secondary','Suricata-NIDS','Data-Center','DMZ','Wazuh-SOC']
cap.REMOTE=cap.REMOTE.replace("n.get('name') == 'SOC-Core-L2'", "n.get('name') == "+repr(a.node))
if a.keys:
 assert len(a.keys)<=6 and not a.command_file
 keys={'Enter':0xff0d,'Down':0xff54,'Up':0xff52,'Left':0xff51,'Right':0xff53,'Tab':0xff09,'Space':0x20,'Escape':0xff1b,'Eight':0x38,'Cancel':0x63}
 injection='    facts["navigation_keys"] = '+repr(a.keys)+'\n'
 if a.keys==['Cancel']:
  injection+='    sock.sendall(struct.pack(">BBHI",4,1,0,0xffe3))\n'
 injection+='    for key in '+repr([keys[k] for k in a.keys])+':\n        sock.sendall(struct.pack(">BBHI",4,1,0,key)+struct.pack(">BBHI",4,0,0,key))\n        time.sleep(0.4)\n    time.sleep(2)\n'
 if a.keys==['Cancel']:
  injection+='    sock.sendall(struct.pack(">BBHI",4,0,0,0xffe3))\n'
 cap.REMOTE=cap.REMOTE.replace('    pixel_format = struct.pack',injection+'    pixel_format = struct.pack')
sys.argv=[sys.argv[0],'--output-dir',a.output_dir,'--label',a.label]+(['--command-file',a.command_file] if a.command_file else [])
cap.main()
