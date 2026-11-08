"""Lập báo cáo tiếng Việt và danh mục từ các tệp thực đã thu của Nhóm 1B."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]).resolve()
state = json.loads((out / 'runtime.json').read_text())
backup = json.loads((out / 'backup-manifest.json').read_text())
comparison = json.loads((out / 'comparison.json').read_text())
report = root / 'docs/M2/M2-group1b-runtime-20261102.md'
assert not report.exists()
db = next(r for r in backup['files'] if r['name'] == 'ovsdb.snapshot')
ports = {p['name']: p for p in state['ports']}
lines = ['# 2. M2 — Nhóm 1B: backup và đối chiếu Core Layer 2', '',
         '## 2.1. Phạm vi và kết quả', '',
         f"Thời điểm thu backup theo máy Windows: {backup['collector_time']}. Trạng thái đối chiếu: **{comparison['status']}**. "
         'Đây là kiểm tra cấu hình runtime; không kiểm thử lưu lượng, không chạy lại bộ 95 ca M2 đã đạt trước đây.', '',
         'Ba thao tác được giao: khởi động riêng SOC-Core-L2; sao lưu OVSDB/cấu hình hiện tại về Windows; đối chiếu runtime trước khi quyết định sửa. '
         'Wazuh-SOC đã chạy từ trước, được giữ nguyên. Không bật node khác, không thay OPNsense hoặc kiến trúc Core.', '',
         '## 2.2. Backup đã thu', '',
         f"- Backup OVSDB tại Windows: `{db['path']}`.",
         f"- Kích thước: {db['bytes']} byte; SHA-256: `{db['sha256']}`.",
         f"- Thư mục backup trong guest: `{backup['guest_backup_directory']}`.",
         f"- Tên database: `{backup['database_name']}`; schema: `{backup['schema']}`.",
         '- Đã kiểm tra db-name/schema và compact bản sao bằng ovsdb-tool; không compact hoặc restore database đang chạy.',
         '- Toàn bộ reply console và từng tệp được đối chiếu SHA-256 sau truyền. Không ghi đè backup cũ.', '',
         'Cùng thư mục private-backups có `runtime.json`, `ovs-show.txt`, `systemd-units.txt` và `commands.jsonl`. '
         'Raw backup và dữ liệu console trung gian thuộc các đường dẫn được Git bỏ qua; không thực hiện commit/push. '
         'File manifest ghi tên, kích thước, đường dẫn và hash. Chưa thử restore backup trong lượt này.', '',
         '## 2.3. Cấu hình runtime đã đọc', '',
         '| Port | VLAN mode | Access tag | Trunk VLAN |', '|---|---|---|---|']
for name in ['ens3', 'ens4', 'ens5', 'ens6', 'ens7', 'ens8', 'ens9', 'ens10', 'br-core-l2']:
    p = ports[name]
    lines.append(f"| {name} | {p['vlan_mode']} | {p['tag']} | {p['trunks']} |")
lines += ['', 'NIC/MAC được đối chiếu với mapping đã xác nhận, không suy ofport từ tên ens. '
          'ens10 là cổng mirror output đã có, không chuyển thành cổng dữ liệu. '
          'Local port br-core-l2 thuộc VLAN 99, không phải NIC EVE bổ sung.', '',
          f"Boot ID hiện tại: `{state['boot_id']}`. IPv4/IPv6 forwarding: `{state['forward4']}/{state['forward6']}`. "
          f"Dịch vụ giữ Core không IP: `{state['noip_service']}`, trạng thái enable: `{state['noip_service_enabled']}`. "
          'Chi tiết dịch vụ OVS, MAC, địa chỉ, route, interface error và mirror nằm trong runtime.json; kết quả guard ở comparison.json.', '',
          '## 2.4. Thay đổi và mục giữ nguyên', '',
          'Không áp dụng thay đổi cấu hình trong lượt này. Không tạo VLAN/port/bond mới, không sửa SPAN. '
          'LACP (Link Aggregation Control Protocol — giao thức điều khiển gộp liên kết) không áp dụng: '
          'hai trunk đi tới hai firewall riêng, không có nhóm đường và peer phù hợp được xác nhận. Không cấu hình LACP.', '',
          'SPAN/port mirroring: mirror span-suricata chọn ingress ens3–ens9 của VLAN 30/40/50/60/99, output ens10; '
          'không chọn chiều đích. Đối chiếu theo tên port/VLAN, không nhầm UUID hoặc ofport với định danh cố định qua boot.', '',
          '## 2.5. Sai lệch và giới hạn', '']
if comparison['failures']:
    lines += [f"- {s}" for s in comparison['failures']]
    lines += ['', '**Dừng trước khi sửa. Chưa hoàn tất xác nhận cấu hình Nhóm 1B.**']
else:
    lines += ['Runtime khớp guard cấu hình đã xác nhận: VLAN/access/trunk, ánh xạ MAC, mirror, '
              'Core không IP/gateway, forwarding tắt, interface không báo lỗi và các dịch vụ liên quan. '
              'Không có mục VLAN/trunk cần sửa theo dữ liệu thu được. '
              'Cấu hình Nhóm 1B đạt đối chiếu; không suy từ đó rằng kiểm thử lưu lượng tổng thể mới đã đạt.']
lines += ['', '## 2.6. Ảnh minh chứng', '']
for label, caption, explanation in [
    ('runtime-ports', 'Bảng VLAN access và trunk trên Core đang chạy', 'Mục đích: kiểm tra từng port. Nội dung/kết quả: mode, tag và trunk đọc từ OVS runtime. Ý nghĩa: đối chiếu cấu hình, không phải phép thử frame.'),
    ('runtime-mirror', 'Mirror và định danh interface của Core', 'Mục đích: xác nhận SPAN giữ nguyên và NIC đúng mapping. Nội dung/kết quả: bảng Mirror/Interface lấy trực tiếp từ console. Ý nghĩa: trạng thái cấu hình quan sát được; không thay kiểm thử lưu lượng.'),
    ('backup-proof', 'Backup OVSDB và trạng thái dịch vụ', 'Mục đích: xác nhận backup hiện hữu. Nội dung/kết quả: hash/schema backup và dịch vụ được đọc từ guest. Ý nghĩa: backup đã tạo và có thể đối chiếu hash với Windows, chưa thử restore.')]:
    images = sorted(out.glob(label + '-*.png'))
    if images:
        q = images[-1]
        lines += [f'![{caption}](../evidence/M2/{out.name}/{q.name})', '',
                  f'Hình 2.{1 + len([x for x in lines if x.startswith("Hình 2.")])}. {caption}.', '', explanation, '']
lines += ['## 2.7. Điểm dừng', '',
          'Dừng sau Nhóm 1B và chờ người dùng xác nhận mới chuyển nhóm. Không triển khai OPNsense HA, '
          'không thử traffic, không tự tắt Core hoặc Wazuh. Checkpoint chờ đăng nhập trước đó được giữ làm lịch sử; '
          'báo cáo này phản ánh kết quả sau khi người dùng đăng nhập.', '',
          f'Danh mục ảnh/log/backup: `docs/evidence/M2/{out.name}/evidence-index-final.csv`. '
          'Bảng danh mục chỉ liệt kê tệp thực có, ghi thời điểm UTC+07:00 và vị trí báo cáo.']
report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
rows = []
for p in sorted(out.rglob('*')):
    if not p.is_file() or p.name.startswith('evidence-index'):
        continue
    stamp = None
    desc = 'Tệp hỗ trợ backup/đối chiếu cấu hình; không phải kiểm thử lưu lượng'
    if p.suffix == '.json':
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
            stamp = d.get('collector_time_end') or d.get('collector_time')
        except (ValueError, AttributeError):
            pass
    if p.suffix == '.png':
        d = json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))
        stamp = d['collector_time_end']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == d['capture']['sha256']
        desc = 'Ảnh console thật QEMU VNC, đầy đủ khung, không sửa nội dung kỹ thuật'
    if 'private-backups' in p.parts:
        stamp = backup['collector_time']
        desc = 'Backup/config đã chuyển về Windows và kiểm SHA-256; không công bố raw backup qua Git'
    if 'console-transfer-group1b' in p.parts:
        desc = 'Trung gian truyền console có checksum; không phải kết quả thử frame'
    basis = 'Đồng hồ máy thu UTC+07:00' if stamp else 'mtime tệp; không phải thời điểm sự kiện guest'
    stamp = stamp or dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone(dt.timedelta(hours=7))).isoformat()
    rows.append([p.name, desc, stamp, basis, p.relative_to(root).as_posix(), 'Chương 2, Nhóm 1B; phần 2.2–2.6', hashlib.sha256(p.read_bytes()).hexdigest()])
with (out / 'evidence-index-final.csv').open('x', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['filename', 'content', 'collected_at', 'time_basis', 'path', 'report_section', 'sha256'])
    w.writerows(rows)
print(json.dumps({'report': str(report), 'evidence_files': len(rows), 'status': comparison['status']}))
