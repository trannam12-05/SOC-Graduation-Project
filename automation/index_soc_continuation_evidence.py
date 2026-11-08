"""Lập danh mục tệp đã có; không tạo ảnh hoặc sửa log minh chứng."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / 'docs/evidence/M5/continuation-20261102'
zone = dt.timezone(dt.timedelta(hours=7))
rows = []
for p in sorted(EV.rglob('*')):
    if not p.is_file() or p.name.startswith('evidence-index'):
        continue
    stamp = None
    desc = 'Tệp hỗ trợ kiểm tra; không tự coi là kết quả đạt'
    if p.suffix == '.json':
        try:
            d = json.loads(p.read_text(encoding='utf-8-sig'))
            stamp = d.get('collector_time_end') or d.get('collector_time') or d.get('collected_at')
            if d.get('mode'):
                desc = f"Kiểm tra {d['mode']}: {d.get('result')}; session {d.get('session')}"
            elif 'running_qemu' in d:
                desc = 'Kiểm kê XML lab, QEMU và RAM EVE tại thời điểm thu'
            elif 'capture' in d:
                desc = 'Metadata ảnh console thật, lệnh đã gửi và SHA-256 ảnh'
        except (ValueError, AttributeError):
            pass
    elif p.suffix == '.png':
        meta = p.with_suffix('.json')
        if meta.exists():
            d = json.loads(meta.read_text(encoding='utf-8'))
            stamp = d.get('collector_time_end')
        desc = 'Ảnh console thật QEMU VNC; không chỉnh sửa nội dung kỹ thuật'
    if 'transfer' in p.parts or any('transfer' in part for part in p.parts):
        desc = 'Truyền/kiểm checksum console; ảnh này không thay kết quả nghiệp vụ'
    if not stamp:
        stamp = dt.datetime.fromtimestamp(p.stat().st_mtime, zone).isoformat()
        basis = 'mtime tệp; không phải thời điểm sự kiện guest'
    else:
        basis = 'Đồng hồ máy thu UTC+07:00 theo metadata'
    rows.append({'ten_tep': p.name, 'noi_dung': desc, 'thoi_diem_thu': stamp,
                 'co_so_thoi_gian': basis, 'duong_dan': p.relative_to(ROOT).as_posix(),
                 'vi_tri_bao_cao': 'Chương 5; ảnh truyền console dùng phụ lục phương pháp',
                 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
for path in [EV / 'evidence-index-final.csv', EV / 'evidence-index-final.md']:
    if path.exists():
        raise FileExistsError(path)
with (EV / 'evidence-index-final.csv').open('x', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
lines = ['# 1. Danh mục minh chứng M5 — tiếp quản ngày 02/11/2026', '',
         'Chỉ liệt kê tệp thực tế. Trạng thái nghiệp vụ xem báo cáo M5; không suy PASS từ việc có ảnh.', '',
         '| Tệp | Nội dung | Thời điểm thu | Đường dẫn | Vị trí báo cáo |',
         '|---|---|---|---|---|']
for row in rows:
    lines.append('| ' + ' | '.join(str(row[k]).replace('|', '/') for k in ('ten_tep', 'noi_dung', 'thoi_diem_thu', 'duong_dan', 'vi_tri_bao_cao')) + ' |')
(EV / 'evidence-index-final.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'files_indexed': len(rows), 'csv': str(EV / 'evidence-index-final.csv')}))
