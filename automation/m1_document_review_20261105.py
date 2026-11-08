"""Xuất hồ sơ M1 cục bộ; không kết nối hoặc thay đổi EVE-NG."""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
ev = root / 'docs/evidence/M1/design-review-20261105'
report = root / 'docs/M1/M1-design-consolidated-20261105.md'
now = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
if report.with_suffix('.docx').exists():
    raise SystemExit('Không ghi đè báo cáo đã xuất.')
terms = (root / 'docs/TOPOLOGY_TERMS.md').read_text(encoding='utf-8')
terms = re.sub(r'^# 1\. .*$', '# PHỤ LỤC 1.A. GIẢI THÍCH THUẬT NGỮ', terms, flags=re.M)
terms = re.sub(r'^## 1\.(\d+)\.', r'## 1.A.\1.', terms, flags=re.M)
with report.open('a', encoding='utf-8') as f:
    f.write('\n\n' + terms)

refs = [
 ('docs/evidence/M2/topology-first-20261102/validation-topology-built.json', 'Cấu trúc topology; Wazuh và upstream còn thiếu', '2026-11-02T13:08:31.197173+07:00', '1.2, 1.5'),
 ('docs/M2/M2-final-summary-20261103.md', 'Core L2, routing, firewall và mirror', '2026-11-03; UTC+07:00, xem từng nguồn gốc', '1.5, 1.6'),
 ('docs/evidence/M3/M3.3-failover-20261104/run-105204/M3.3-acceptance.json', 'CARP failover/recovery', '2026-11-04T11:07:14.319327+07:00', '1.7'),
 ('docs/evidence/M3/M3.4B-pfsync-state-20261104/M3.4-acceptance.json', 'State sync và continuity một session', '2026-11-04T17:12:50.875586+07:00', '1.4, 1.7'),
 ('docs/M5-verification-and-demo-20261102.md', 'Wazuh replay; chưa live', '2026-11-02; UTC+07:00, xem từng nguồn gốc', '1.2, 1.6'),
]
for rel, *_ in refs:
    assert (root / rel).is_file(), rel
for rel in ['network/ip-plan/vlan-ip-plan.md', 'network/core-l2/port-mapping.md', 'docs/M1/open-questions.md', 'docs/SOC_TO_DO.md', 'docs/PROGRESS.md']:
    p = root / rel
    original = p.read_bytes()
    (ev / (p.name + '.before')).write_bytes(original)
    if rel.startswith('network/'):
        note = '# Cập nhật M1 — 05/11/2026, UTC+07:00\n\nBản hiện hành: [Thiết kế hợp nhất](../../docs/M1/M1-design-consolidated-20261105.md). Năm VLAN, IP firewall .2/.3 và VIP .1 đã được nghiệm thu M3. Core dùng Open vSwitch ens3–ens10, không IP; LACP không áp dụng. Wazuh VLAN99 là thiết kế chưa triển khai. Internet ngoài phạm vi cơ sở. Nội dung dưới đây là trích xuất M1 gốc giữ làm lịch sử; không dùng trạng thái chưa xác nhận hoặc tên cổng IOS cũ thay bản hợp nhất.\n\n---\n\n'
    elif rel.endswith('open-questions.md'):
        note = '# Cập nhật M1 — 05/11/2026, UTC+07:00\n\nXem [bản hợp nhất](M1-design-consolidated-20261105.md). Đã làm rõ VLAN60, subnet/VIP, SYNC /30, mapping OVS và nguồn mirror bằng nghiệm thu M2–M3. Người dùng chọn lab nội bộ, Internet là mở rộng. Thiết kế cơ sở dùng một endpoint mỗi vùng. Còn cần đối chiếu IP sensor/Wazuh trước triển khai, chốt máy automation và DNS/DHCP ở giai đoạn sau; thông tin bìa chưa cung cấp. Wazuh e0 → Management là thiết kế chưa áp dụng. Danh sách dưới đây là lịch sử.\n\n---\n\n'
    else:
        note = f'# CHECKPOINT M1 — HỒ SƠ THIẾT KẾ HỢP NHẤT — {now}\n\nNgười dùng chọn lab nội bộ; Internet là phần mở rộng. [Thiết kế M1](M1/M1-design-consolidated-20261105.md), bản Word cùng tên và sơ đồ network/topology/M1-internal-lab-20261105.mmd bổ sung số node, mapping, bảng IP, chính sách và thuật ngữ.\n\n**Hồ sơ thiết kế cơ sở đã hoàn thiện; topology EVE-NG thực tế chưa nghiệm thu hoàn chỉnh.** Wazuh e0 vào VLAN99 là thiết kế chưa áp dụng; cần triển khai và ảnh thật theo quyền riêng. Core không IP/Layer2; không thay hệ thống trong đợt này. [Danh mục rà soát](evidence/M1/design-review-20261105/evidence-index.csv). M3.4 giữ DONE/PASS lịch sử; các checkpoint dưới đây giữ nguyên.\n\n---\n\n'
    p.write_text(note + original.decode('utf-8-sig'), encoding='utf-8')
subprocess.run([sys.executable, str(root / 'automation/export_m2_report_docx.py'), str(report)], check=True)
with (ev / 'evidence-index.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['ten_tep', 'noi_dung', 'thoi_diem_kem_mui_gio', 'duong_dan', 'vi_tri_bao_cao', 'phan_loai'])
    for rel, desc, when, pos in refs:
        w.writerow([Path(rel).name, desc, when, rel, pos, 'Nguồn lịch sử; không thu lại runtime'])
    for rel, desc in [('docs/M1/M1-design-consolidated-20261105.md', 'Báo cáo hợp nhất'), ('docs/M1/M1-design-consolidated-20261105.docx', 'Word mới'), ('network/topology/M1-internal-lab-20261105.mmd', 'Sơ đồ thiết kế, không phải ảnh EVE'), ('docs/evidence/M1/design-review-20261105/manual-capture.md', 'Hướng dẫn ảnh chưa thu')]:
        w.writerow([Path(rel).name, desc, now, rel, 'Chương 1', 'Tài liệu mới; không phải minh chứng runtime'])
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(report.with_suffix('.docx')) as z:
    assert z.testzip() is None
    doc = ET.fromstring(z.read('word/document.xml'))
    margins = doc.find('.//w:pgMar', ns).attrib
    size = doc.find('.//w:pgSz', ns).attrib
    styles = z.read('word/styles.xml').decode()
    assert 'Times New Roman' in styles
    assert size['{' + ns['w'] + '}w'] == '11906'
    assert margins['{' + ns['w'] + '}left'] == '1701'
result = dict(review_time=now, docx_zip_valid=True, page_size=size, margins=margins, new_runtime_screenshots=0, system_changed=False, design_documentation='COMPLETE', eve_topology_acceptance='PENDING_WAZUH_LINK_AND_SCREENSHOT', word_gui_pagination_reviewed=False)
(ev / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
paths = [report, report.with_suffix('.docx'), root / 'network/topology/M1-internal-lab-20261105.mmd', *ev.glob('*.before')]
manifest = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(ev / 'sha256-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
