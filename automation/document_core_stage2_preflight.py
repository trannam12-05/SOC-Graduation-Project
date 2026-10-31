"""Ghi báo cáo tiền kiểm tra từ snapshot thật; không điều khiển EVE/VM."""
import csv
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from export_m2_report_docx import build

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / 'docs/evidence/M2'
STEM = 'M2-core-stage2-preflight-20261031T2015+0700'
snapshot = EV / (STEM + '.json')
data = json.loads(snapshot.read_text(encoding='utf-8'))
memory = data['windows_memory']
free_mib = memory['FreePhysicalMemoryKiB'] / 1024
assert free_mib < 2048
assert data['live_eve_node']['status'] == 0
assert not data['core_process_present'] and not data['core_runtime_directory_exists']
assert all(x['unchanged'] for x in data['protected_comparison'])
report = ROOT / 'docs/M2/M2-report-stage2-preflight-20261031T2015+0700.md'
mapping = EV / (STEM + '-nic-mapping.csv')
index = EV / (STEM + '-evidence-index.md')
log = EV / (STEM + '.log')

def write_new(path, text):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)

rows = ['| Cổng EVE | MAC khai báo | NIC Ubuntu | QEMU runtime | Vai trò dự kiến, chưa cấu hình |',
        '|---|---|---|---|---|']
roles = ['Access VLAN 30', 'Access VLAN 40', 'Access VLAN 50', 'Access VLAN 60',
         'Access VLAN 99', 'Trunk OPNsense Primary', 'Trunk OPNsense Secondary', 'Mirror Suricata']
csv_output = io.StringIO(newline='')
writer = csv.writer(csv_output)
writer.writerow(['eve_port', 'configured_mac', 'guest_nic', 'qemu_runtime', 'network_id', 'proposed_role', 'verification'])
for nic, role in zip(data['live_eve_node']['interfaces'], roles):
    rows.append(f"| {nic['eve_name']} | {nic['mac']} | Chưa xác minh | Chưa khởi động | {role} |")
    writer.writerow([nic['eve_name'], nic['mac'], '', '', nic['network_id'], role, 'EVE configuration only; guest mapping pending boot'])
write_new(mapping, csv_output.getvalue())
write_new(log, f"Collector: {data['collected_at_windows']}\nWindows sample: {memory['CollectedAt']}\n"
          f"Windows FreePhysicalMemory: {memory['FreePhysicalMemoryKiB']} KiB = {free_mib:.1f} MiB\n"
          "Required Windows minimum: 2097152 KiB = 2048 MiB\nDecision: DO NOT START; Windows memory gate failed.\n"
          "EVE free -m (available column, not free column):\n" + data['free_memory'] +
          "Core status=0; CPU=1; RAM=2048 MiB; configured ethernet=8; network links=0.\n"
          "Core QEMU process absent; Core runtime directory absent.\n"
          "Core disk and seed SHA256 match stage1 markers. Nine protected file hashes unchanged.\n"
          "Old Ubuntu-Test and Ubuntu-Console-Test processes still present.\n"
          "Only read-only checks performed. No start/stop/install/network/seed/template change.\n"
          "Guest diagnostics and screenshots of boot/runtime NOT performed.\n")

appendix = f'''

## 2.16. Giai đoạn 2: tiền kiểm tra khởi động Core ngày 31/10/2026

Mục này cập nhật trạng thái sau các mốc lịch sử ở mục 2.1–2.15. Người dùng đã phê duyệt khởi động duy nhất SOC-Core-L2 trong SOC-M2-Core-L2, với điều kiện Windows có ít nhất 2 GiB RAM khả dụng. Quyền khởi động đã được cấp; trở ngại hiện tại là tài nguyên, không phải thiếu phê duyệt. Không cài OVS hoặc nối mạng trong giai đoạn này.

### 2.16.1. Kết quả kiểm tra tài nguyên và quyết định

Thời điểm snapshot: {data['collected_at_windows']}; mẫu RAM Windows: {memory['CollectedAt']}. Dùng giờ bộ thu Windows UTC+07:00; đồng hồ EVE chưa được coi là nguồn thời gian đáng tin cậy.

| Hạng mục | Kết quả đo | Đánh giá |
|---|---|---|
| Windows RAM khả dụng | {memory['FreePhysicalMemoryKiB']:,} KiB = {free_mib:.1f} MiB, khoảng {free_mib/1024:.3f} GiB | Không đạt điều kiện bắt buộc 2 GiB |
| EVE RAM available | 5335 MiB, khoảng 5.21 GiB; tổng 7897 MiB | Đạt mức dự phòng 3 GiB đề xuất trong kế hoạch |
| EVE swap | 0 MiB đang dùng | Số liệu tại thời điểm đọc |
| Core ID 3 | status=0; không có tiến trình QEMU hoặc thư mục runtime | Vẫn tắt, chưa gửi lệnh start |
| Cấu hình node | 1 vCPU, 2048 MiB, 8 vNIC; 0 network/link | Đã đọc trực tiếp cấu hình EVE; chưa phải thông số guest runtime |
| Image Core và seed | SHA-256 hiện tại khớp marker giai đoạn 1 | Không thay image/seed |
| Tài nguyên cũ | 9 checksum được bảo vệ giữ nguyên; hai tiến trình Ubuntu kiểm chứng vẫn chạy | Không thay đổi vòng đời hoặc cấu hình cũ |

Kết luận: **chưa khởi động Core vì Windows không đạt ngưỡng RAM**. RAM khả dụng bên trong EVE không thay thế điều kiện RAM của Windows. Chưa thể nghiệm thu Giai đoạn 2; đây là điểm dừng trước khởi động theo điều kiện của người dùng, không phải lỗi boot Ubuntu.

Nguồn trực tiếp: [snapshot JSON](../evidence/M2/{snapshot.name}) và [log tiền kiểm tra](../evidence/M2/{log.name}). Dung lượng đĩa 8 GiB và kiểm tra QCOW2 trước đây là kết quả giai đoạn 1; lần này đối chiếu checksum, chưa kiểm tra phân vùng hoặc filesystem trong guest.

### 2.16.2. Bảng đối chiếu cổng: cấu hình đã đọc và mapping chưa xác minh

{chr(10).join(rows)}

Bảng này là danh mục cổng EVE/MAC đã khai báo, **chưa phải mapping NIC thực tế trong Ubuntu**. Không điền ens3, ens4 hoặc tên PCI/QEMU khi chưa có runtime. Mọi cổng vẫn network_id=0; vai trò VLAN/trunk/mirror chỉ là thiết kế. Sau boot, đối chiếu MAC từ `ip -br link` hoặc `ip -j link` với MAC trong đối số QEMU và cổng EVE, kiểm tra đủ tám MAC duy nhất; loại giao diện loopback khỏi số lượng vNIC. [CSV mapping chờ kiểm chứng](../evidence/M2/{mapping.name}).

### 2.16.3. Kiểm tra và ảnh thực tế còn chờ

Chưa có runtime Core để xác minh firmware, CPU/RAM QEMU, tám thiết bị mạng, ổ đĩa runtime hoặc CD-ROM NoCloud đang gắn. Chưa quan sát màn hình login và chưa chạy bất kỳ lệnh nào trong guest Core. Kết quả cloud-init thành công của Ubuntu-Console-Test ở mục trước không được suy rộng sang SOC-Core-L2.

Sau khi đạt điều kiện tài nguyên, kiểm tra đúng UUID node, đường dẫn lab và ID 3 trước khi bật riêng Core. Đọc tiến trình QEMU và chuỗi backing của ổ đĩa runtime; ghi nhận CPU, RAM, NIC/MAC/backend, firmware thực tế và seed CD-ROM. Không suy diễn BIOS/UEFI chỉ từ tên template. Nếu đến login, người dùng tự nhập tài khoản soc-core-admin và mật khẩu trên console; không thu thập phím nhập, mật khẩu hoặc hash.

Các lệnh chẩn đoán được phê duyệt, chỉ thực hiện sau khi xác nhận đã đăng nhập đúng guest:

```text
cloud-init status --long
cloud-id
hostnamectl
ip -br link
lsblk
free -h
nproc
```

| Mốc ảnh dự kiến | Chú thích dự kiến | Trạng thái hiện tại |
|---|---|---|
| Node chạy trong lab riêng | Hình 2.5. Trạng thái hoạt động của SOC-Core-L2 trên EVE-NG | Chưa chụp vì chưa bật Core |
| Console tới login | Hình 2.6. Màn hình đăng nhập Ubuntu của SOC-Core-L2 | Chưa chụp |
| cloud-init và cloud-id | Hình 2.7. Kết quả khởi tạo NoCloud trên SOC-Core-L2 | Chưa chụp |
| NIC và MAC | Hình 2.8. Tám giao diện mạng ảo thực tế trên Ubuntu Core | Chưa chụp |
| Hostname, CPU/RAM và đĩa | Hình 2.9. Thông tin hệ thống và tài nguyên của Ubuntu Core | Chưa chụp |

Các chú thích trên là kế hoạch, không phải minh chứng đã có. Không tạo ảnh thay thế, không dùng ảnh node cũ để minh chứng Core. Công cụ RFB hiện có hỗ trợ chụp framebuffer QEMU thật khi node chạy; giai đoạn này không có framebuffer Core. Nếu không truy cập được GUI EVE, người dùng mở đúng lab, chụp nguyên màn hình trạng thái node bằng Snipping Tool, lưu PNG vào docs/evidence/M2 kèm thời điểm UTC+07:00. Với console, ảnh phải chứa đủ lệnh, kết quả và dấu nhắc nhận diện guest; chia thành nhiều ảnh nếu cần, tránh cắt kết quả quan trọng. Mỗi ảnh sau thu thập phải bổ sung mục đích, nội dung, kết quả và ý nghĩa; tuyệt đối không chụp nội dung bí mật.

### 2.16.4. Thuật ngữ phục vụ diễn giải kết quả

Các giải thích chi tiết cloud-init, NoCloud, datasource, seed ISO, QEMU, QCOW2, console và vNIC đã có tại mục 2.5 và 2.13, cùng nguồn chính thức trong bản báo cáo trước. Khi sử dụng cho Core, phải giữ các trạng thái sau:

| Thuật ngữ | Ý nghĩa trong phép kiểm tra Core |
|---|---|
| QEMU runtime | Phiên máy ảo đang thực thi; phải đọc tiến trình thực tế để xác nhận CPU, bộ nhớ và thiết bị, hiện chưa tồn tại |
| vNIC — Virtual Network Interface Card | Card mạng ảo; tám cổng đã khai báo trong EVE, số lượng Ubuntu nhận diện còn chờ boot |
| MAC — Media Access Control address | Địa chỉ lớp liên kết của NIC; dùng đối chiếu EVE, QEMU và Ubuntu, không thay thế xác minh đường nối vật lý/ảo |
| Firmware | Phần mềm khởi động máy ảo trước hệ điều hành; loại BIOS/UEFI và cấu hình thực tế của Core chưa xác minh |
| cloud-init / NoCloud | Cơ chế khởi tạo từ dữ liệu cục bộ; chuẩn bị seed chưa đồng nghĩa guest đã xử lý seed thành công |
| QCOW2 overlay | Lớp lưu thay đổi runtime của QEMU; Core hiện chưa có runtime để kiểm tra chuỗi đĩa |
| Available RAM | Chỉ số tài nguyên dùng làm điều kiện trước boot ở từng lớp host; số đo Windows và EVE phải đánh giá riêng, không cộng lại |

Trong SOC dự kiến, Core dùng vNIC cho access/trunk/mirror Layer 2; OPNsense xử lý gateway, định tuyến, firewall và NAT. Hiện chưa có OVS bridge hoặc cấu hình chuyển mạch để kiểm thử.

### 2.16.5. Hướng xử lý và bước tiếp tục

Người dùng lưu công việc rồi tự đóng ứng dụng/tab trình duyệt hoặc cửa sổ terminal đã dùng xong để giải phóng RAM. Không tự dừng Ubuntu-Test, Ubuntu-Console-Test, EVE hoặc thay RAM VMware. Sau khi giải phóng, đo lại Windows và EVE ngay trước boot; chỉ tiếp tục khi Windows đạt ít nhất 2048 MiB và tài nguyên EVE phù hợp. Không cần xin lại quyền boot đã được phê duyệt nếu điều kiện và phạm vi không thay đổi.

Sau khi kiểm tra runtime, đăng nhập, cloud-init, tám NIC, tài nguyên và ổ đĩa đều đạt, mới trình phương án cài OVS offline v2 để phê duyệt riêng. Phương án phải kiểm tra phiên bản/kiến trúc/kernel và trạng thái gói thực tế, xác thực bundle/checksum, mô phỏng giải phụ thuộc với nguồn Noble offline trước khi cài; không cài mù toàn bộ 70 gói hoặc nối mạng để lấy phụ thuộc. Hiện chưa đề nghị thực hiện cài đặt vì Giai đoạn 2 chưa được nghiệm thu.

[Danh mục minh chứng tiền kiểm tra Giai đoạn 2](../evidence/M2/{index.name}). Báo cáo Word được kiểm tra cấu trúc ZIP/XML, A4, font và ảnh nhúng; chưa kiểm tra bố cục bằng giao diện Word. Các ảnh ở mục trước giữ nguyên và chỉ chứng minh các thời điểm lịch sử tương ứng.
'''
previous = ROOT / 'docs/M2/M2-report-stage1-core-preparation-20261031-final.md'
write_new(report, previous.read_text(encoding='utf-8') + appendix)
build(report)
write_new(index, f'''# Danh mục minh chứng M2 – tiền kiểm tra Giai đoạn 2

Thời điểm: {data['collected_at_windows']} (UTC+07:00). Kết luận: Windows {free_mib:.1f} MiB < 2048 MiB, Core chưa bật. Không có ảnh mới của Core đang chạy; ảnh dự kiến chưa được coi là minh chứng.

| Tệp | Nội dung | Thời điểm | Vị trí báo cáo |
|---|---|---|---|
| [{snapshot.name}]({snapshot.name}) | Snapshot đọc trực tiếp Windows/EVE và checksum | {data['collected_at_windows']} | 2.16.1 |
| [{log.name}]({log.name}) | Tóm tắt kết quả và quyết định không start | Cùng snapshot | 2.16.1 |
| [{mapping.name}]({mapping.name}) | EVE/MAC đã đọc, tên guest/QEMU còn trống | Cùng snapshot | 2.16.2 |
| [{report.name}](../../M2/{report.name}) | Bản cập nhật giữ nội dung lịch sử và thêm trạng thái mới | 31/10/2026 UTC+07:00 | 2.16 |
| [{report.with_suffix('.docx').name}](../../M2/{report.with_suffix('.docx').name}) | Báo cáo Word A4, Times New Roman | 31/10/2026 UTC+07:00 | 2.16 |

Kế hoạch ảnh và chú thích Hình 2.5–2.9 tại mục 2.16.3; tất cả chưa chụp. Minh chứng cũ không ghi đè/xóa/di chuyển. Phê duyệt boot có điều kiện đã nhận; thiếu RAM là điều kiện chưa đạt. Các lệnh guest và cài OVS chưa thực hiện.
''')
paths = [snapshot, mapping, log, report, report.with_suffix('.docx'), index]
write_new(EV / (STEM + '-SHA256SUMS.txt'), ''.join(
    hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(ROOT).as_posix() + '\n' for p in paths))
with zipfile.ZipFile(report.with_suffix('.docx')) as archive:
    assert archive.testzip() is None
    for name in archive.namelist():
        if name.endswith('.xml'):
            ET.fromstring(archive.read(name))
    document = archive.read('word/document.xml').decode('utf-8')
    assert '2.16.' in document and '572.6 MiB' in document
print('PASS: report, DOCX, mapping, log, index and 6-entry SHA256 manifest created without overwrites.')
