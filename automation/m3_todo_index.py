"""Danh mục minh chứng M3 hiện hành; không sửa/xóa ảnh và log cũ."""
import csv,datetime as dt,hashlib,json
from m3_todo_console import OUT,ROOT
rows=[]
for p in sorted(OUT.iterdir()):
 if not p.is_file() or p.name.startswith('evidence-index'):continue
 timestamp=None;basis='Thời điểm ghi tệp nguồn/hướng dẫn, không phải kết quả guest'
 j=p if p.suffix=='.json' else p.with_suffix('.json') if p.suffix=='.png' else None
 if j and j.exists():
  try:
   d=json.loads(j.read_text(encoding='utf-8'));timestamp=d.get('collector_time_end') or d.get('collector_time');basis='Collector Windows, UTC+07:00; không dùng giờ EVE lệch để gán thời điểm thu'
  except (ValueError,AttributeError):pass
 if not timestamp:timestamp=dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone(dt.timedelta(hours=7))).isoformat()
 desc='Framebuffer console thật, không chỉnh sửa' if p.suffix=='.png' else 'Kết quả/metadata collector; trang glyph được kiểm SHA-256 nếu có JSON giải mã' if p.suffix=='.json' else 'Nguồn/lệnh đầu vào, không tự là bằng chứng chạy thành công'
 specific={
 'M3.1-acceptance.json':'Nghiệm thu pfsync: boot mới, hook cùng boot, peer/syncok/demotion/config hai phía',
 'M3.2-acceptance.json':'Nghiệm thu năm VIP persistent, MASTER/BACKUP và quảng bá protocol112',
 'carp-advertisements-after.json':'Metadata quảng bá CARP thật trên hai trunk; đường dẫn/SHA-256 PCAP root-only',
 'carp-vhid-observation-before.json':'Quan sát protocol112 trước apply: giới hạn cửa sổ20giây',
 'carp-vip-arp-before.json':'ARP trước apply: .2/.3 có phản hồi, .1 chưa thấy phản hồi trong cửa sổ thử',
 'carp-vip-arp-after.json':'ARP sau apply: năm VIP .1 và hai peer vật lý trả lời, kèm MAC thực',
 'm3-final-host.json':'Tài nguyên EVE, QEMU allocation, swap/vmstat và kernel OOM ở bàn giao',
 }
 if p.name in specific:desc=specific[p.name]
 elif p.name.endswith('-pfsync-postboot.json'):desc='Runtime/log pfsync guest sau reboot, chỉ đọc, đã kiểm SHA-256 console transport'
 elif p.name.endswith('-carp-apply.json'):desc='Kết quả model save và native VIP/filter reload; backup và guard cấu hình'
 elif p.name.endswith('-carp-verified.json'):desc='Đối chiếu từng VIP config/runtime, trạng thái CARP và pfsync/demotion'
 elif p.suffix=='.png' and '-carp-proof-' in p.name:desc='Ảnh console thật: năm VIP và CARP MASTER/BACKUP theo từng VLAN'
 elif p.suffix=='.png' and '-pfsync-proof-' in p.name:desc='Ảnh console thật: pfsync runtime và log hook cùng boot'
 rows.append([p.name,desc,timestamp,basis,p.relative_to(ROOT).as_posix(),'M3 TODO, mục3.1–3.4',hashlib.sha256(p.read_bytes()).hexdigest()])
fields=['Tệp','Nội dung','Thời điểm kèm múi giờ','Cơ sở thời gian','Đường dẫn','Vị trí báo cáo','SHA-256']
with (OUT/'evidence-index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(fields);w.writerows(rows)
with (OUT/'evidence-index.md').open('w',encoding='utf-8') as f:
 f.write('# Danh mục minh chứng hoàn thành TODO M3\n\n| '+' | '.join(fields)+' |\n|'+'---|'*len(fields)+'\n')
 for row in rows:f.write('| '+' | '.join(row)+' |\n')
print('Indexed',len(rows),'files; originals preserved')
