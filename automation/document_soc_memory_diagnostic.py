"""Tổng hợp dữ liệu bộ nhớ đã đo, không thay đổi hệ thống."""
import csv
import hashlib
import io
import json
from pathlib import Path
from export_m2_report_docx import build

root = Path(__file__).resolve().parents[1]
ev = root / 'docs/evidence/M2'
data = json.loads((ev/'M2-memory-diagnostic-20261031-02.json').read_text(encoding='utf-8'))
qemu = json.loads((ev/'M2-memory-eve-processes-20261031-01.json').read_text(encoding='utf-8'))
def write(path, text):
    with path.open('x', encoding='utf-8', newline='\n') as f:f.write(text)

table = ['| Ứng dụng/tiến trình | PID | Working set (MiB) | Private working set (MiB) |', '|---|---|---|---|']
output = io.StringIO(newline='')
writer = csv.writer(output)
writer.writerow(['Application','Process','PID','WorkingSetMiB','PrivateWorkingSetMiB'])
for item in data['Top10ByWorkingSet']:
    name = item['Application'] or item['Name']
    table.append(f"| {name} | {item['PID']} | {item['WorkingSetMiB']:.1f} | {item['PrivateWorkingSetMiB']:.1f} |")
    writer.writerow([name,item['Name'],item['PID'],item['WorkingSetMiB'],item['PrivateWorkingSetMiB']])
csvpath = ev/'M2-memory-top10-20261031.csv'
write(csvpath, output.getvalue())
vmx = next(p for p in data['VMwareProcesses'] if p['Name']=='vmware-vmx')
report = ev/'M2-memory-diagnostic-report-20261031.md'
text = f'''# 2.17. Chẩn đoán bộ nhớ trước khởi động Core M2

## 2.17.1. Phạm vi và kết luận

Thu thập chỉ đọc tại {data['CollectedAt']} (UTC+07:00); EVE đọc tại {qemu['collector_time']}. Người dùng xác nhận chưa đóng ứng dụng và muốn hoàn tất báo cáo trước. Vì vậy, các số đo này chưa phải kết quả sau giải phóng RAM. Không dừng Windows/VMware/node; không bật Core; không thay đổi OVS, NIC, mạng, image, seed hoặc template.

| Chỉ số | Kết quả |
|---|---|
| RAM vật lý lắp đặt | 16384 MiB = 16 GiB; 2 module DIMM |
| RAM Windows nhìn thấy | {data['VisiblePhysicalMiB']:.1f} MiB, khoảng 15,71 GiB |
| RAM available | {data['AvailableMiB']:.1f} MiB; chưa đạt 2048 MiB |
| Committed / commit limit | {data['CommittedMiB']:.1f} / {data['CommitLimitMiB']:.1f} MiB, khoảng {100*data['CommittedMiB']/data['CommitLimitMiB']:.1f}% |
| Pagefile | C:\\pagefile.sys, Windows quản lý tự động |
| Pagefile cấp phát / đang dùng / đỉnh sử dụng | 18157 / 2438 / 3039 MiB |
| EVE RAM available | 5458800 KiB = 5330,9 MiB, khoảng 5,21 GiB |
| SOC-Core-L2 | Tắt, không tiến trình QEMU/runtime; 1 vCPU, 2048 MiB, 8 vNIC chưa nối mạng |

Mẫu Windows trước đó lúc 20:23:32 có available 231,2 MiB; RAM biến động trong quá trình làm việc. Số 455,0 MiB là mẫu chẩn đoán mới hơn lúc 20:24:37, không chứng minh người dùng đã giải phóng RAM. Chưa đạt điều kiện khởi động. File mẫu 01 có trường InstalledPhysicalMiB lấy từ Win32_ComputerSystem nên thực tế là RAM nhìn thấy; mẫu 02 đã phân biệt đúng RAM lắp đặt từ tổng Capacity của DIMM với RAM nhìn thấy. Giữ cả hai mẫu để truy vết.

## 2.17.2. Mười tiến trình dùng nhiều RAM nhất

Xếp theo Working Set tại cùng mẫu đo; đây là từng tiến trình, không phải tổng ứng dụng nhiều tiến trình.

{chr(10).join(table)}

Tổng private working set theo nhóm: Chrome 856,9 MiB (20 tiến trình), Visual Studio Code 805,1 MiB (16 tiến trình), Edge 146,0 MiB (10 tiến trình), Zalo 107,5 MiB (8 tiến trình). Những số này giúp chọn ứng dụng để xem xét; không bảo đảm đóng ứng dụng sẽ tăng available đúng từng ấy MiB.

Working Set là các trang bộ nhớ đang resident của tiến trình, có thể chứa trang chia sẻ. Private Working Set là phần resident riêng. Private Bytes là bộ nhớ ảo riêng đã committed, không phải lượng RAM resident. Không cộng các working set để suy ra tổng RAM máy vì trang chia sẻ có thể bị đếm nhiều lần. Tham chiếu chính thức: [Microsoft Memory Performance Information](https://learn.microsoft.com/en-us/windows/win32/memory/memory-performance-information).

## 2.17.3. Phân biệt Windows, VMware và các node lồng trong EVE

Phát hiện tiến trình vmware-vmx PID {vmx['PID']}: working set {vmx['WorkingSetMiB']:.1f} MiB, private working set {vmx['PrivateWorkingSetMiB']:.1f} MiB, private bytes {vmx['PrivateBytesMiB']:.1f} MiB. Đây chỉ là các counter của tiến trình mà API trả về; **không đủ để quy toàn bộ chi phí RAM của VMware/EVE cho số này**. Chưa xác định được tên VM từ command line trong quyền đọc hiện tại; không kết luận đã đối chiếu trực tiếp PID vmware-vmx với file VMX EVE. Không đọc/chỉnh sửa cấu hình VMware để xử lý thiếu RAM.

EVE là hệ điều hành máy ảo có MemTotal 7897,8 MiB. Ubuntu-Test và Ubuntu-Console-Test là hai tiến trình QEMU bên trong EVE, không phải hai tiến trình Windows riêng. Không cộng RAM guest EVE, RAM QEMU lồng bên trong và working set Windows như ba phần RAM vật lý độc lập.

| Node trong EVE | PID | RAM cấu hình | RSS theo /proc/PID/status | PSS theo smaps_rollup | Trạng thái |
|---|---|---|---|---|---|
| Ubuntu-Test | 287703 | 2048 MiB | 575,5 MiB | 417,4 MiB | QEMU vẫn chạy, UUID khớp |
| Ubuntu-Console-Test | 297601 | 2048 MiB | 676,6 MiB | 505,1 MiB | QEMU vẫn chạy, UUID khớp |

RSS (Resident Set Size) là các trang resident của tiến trình; PSS (Proportional Set Size) chia tỷ lệ trang dùng chung giữa các tiến trình. Hai giá trị RSS/PSS không phải dung lượng RAM cấu hình. Số đo /proc và smaps lấy nối tiếp nên có thể lệch nhẹ. Không đăng nhập hoặc thay đổi hai guest trong phiên này.

Nếu người dùng quyết định dừng sạch hai node ở một bước được phê duyệt riêng, bộ nhớ của QEMU sẽ được giải phóng bên trong EVE. Không hứa thu hồi 4096 MiB thực, vì 4096 MiB là tổng RAM cấu hình, khác lượng resident; cũng không hứa Windows tăng available tương ứng vì EVE vẫn là VM đang chạy. Chưa đo tác động thực tế của việc dừng node. EVE hiện có khoảng 5,21 GiB available nên phương án ưu tiên là xử lý ứng dụng Windows; tiếp tục giữ hai node kiểm chứng.

## 2.17.4. Phương án giải phóng tài nguyên

1. Lưu công việc; tự đóng tab/cửa sổ Chrome không cần. Không đóng tab đang phục vụ phiên làm việc hoặc dữ liệu chưa lưu.
2. Đóng cửa sổ VS Code không dùng, giữ cửa sổ SOC/Codex đang hoạt động. Không end task toàn bộ Code/codex.
3. Nếu không cần, thoát Edge và Zalo qua giao diện ứng dụng. Nhóm này nhỏ hơn Chrome/Code nhưng có thể góp phần giảm tải.
4. Giữ VMware/EVE và hai node Ubuntu kiểm chứng. Không dừng Memory Compression, MsMpEng (Microsoft Defender) hoặc dịch vụ Windows để lấy RAM.
5. Khi người dùng báo hoàn tất, đo lại Windows/EVE ngay trước boot. Chỉ khởi động riêng SOC-Core-L2 nếu Windows đạt ít nhất 2048 MiB và EVE còn đủ tài nguyên; phê duyệt Giai đoạn 2 vẫn có hiệu lực. Nếu còn thiếu thì báo kết quả, không tự đóng thêm ứng dụng.

Committed memory là tổng bộ nhớ ảo hệ thống đã cam kết; commit limit là giới hạn có thể hỗ trợ. Pagefile là tệp trên đĩa hỗ trợ các trang bộ nhớ và giới hạn commit; tăng pagefile không biến nó thành RAM vật lý available để vượt điều kiện 2 GiB của dự án. Giữ cấu hình pagefile tự động hiện có, không chỉnh Windows. Tham chiếu: [Microsoft Introduction to page files](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/introduction-to-the-page-file).

## 2.17.5. Minh chứng và giới hạn ảnh chụp

Đã lưu dữ liệu thật từ Windows CIM/performance counters và /proc EVE, CSV top 10, snapshot trạng thái Core/checksum. Không có cửa sổ Task Manager đang mở trong lần kiểm tra; chưa chụp ảnh RAM mới. Công cụ chụp từng cửa sổ có sẵn nhưng chưa có cửa sổ chẩn đoán phù hợp để chụp. Không dùng ảnh màn hình cũ hoặc ảnh dựng từ JSON làm minh chứng màn hình hiện tại.

Người dùng có thể mở Task Manager → Performance → Memory và chụp nguyên vùng thông tin Installed/Available/Committed; sau đó mở Processes hoặc Details, sắp xếp Memory giảm dần và chụp đủ 10 dòng, không lộ dữ liệu nhạy cảm. Lưu PNG nguyên bản vào docs/evidence/M2 với tên M2-Windows-memory-before-cleanup-THOIDIEM.png và M2-Windows-top-processes-THOIDIEM.png. Sau khi đóng ứng dụng, chụp thêm mẫu after-cleanup. Không cắt mất tên cột hoặc kết quả quan trọng.

Chú thích dự kiến cho phụ lục, **chưa có ảnh**: “Hình PL2.1. Tài nguyên bộ nhớ Windows trước giải phóng RAM”; “Hình PL2.2. Các tiến trình sử dụng nhiều RAM trên Windows”. Mục đích là chứng minh điều kiện tài nguyên trước boot; nội dung cần thể hiện available/commit hoặc tên ứng dụng và RAM; kết quả và ý nghĩa chỉ bổ sung sau khi có ảnh thật. Không chiếm số Hình 2.5–2.9 đã dành cho kiểm tra Core.

Báo cáo Word kèm theo chỉ được kiểm tra gói ZIP/XML, chưa kiểm tra bố cục trực quan bằng Word. Chưa có ảnh mới để nhúng.
'''
write(report, text)
build(report)
files = [ev/'M2-memory-diagnostic-20261031-01.json',ev/'M2-memory-diagnostic-20261031-02.json',
         ev/'M2-memory-eve-status-20261031-01.json',ev/'M2-memory-eve-processes-20261031-01.json',csvpath,report,report.with_suffix('.docx')]
index = ev/'M2-memory-evidence-index-20261031.md'
write(index, '# Danh mục minh chứng chẩn đoán RAM M2\n\nNgày 31/10/2026 UTC+07:00. Chưa có ảnh mới; hướng dẫn chụp tại mục 2.17.5 của báo cáo.\n\n| Tệp/đường dẫn | Nội dung | Thời điểm | Vị trí báo cáo |\n|---|---|---|---|\n'+
      '\n'.join(f'| [{p.name}]({p.name}) | '+('Dữ liệu đo Windows' if 'diagnostic-20261031-0' in p.name else 'Trạng thái EVE và tài nguyên' if 'eve-' in p.name else 'Tổng hợp kết quả chẩn đoán')+f' | 20:23–20:24 UTC+07:00; thời điểm chi tiết trong JSON | 2.17 |' for p in files)+'\n')
files.append(index)
write(ev/'M2-memory-SHA256SUMS-20261031.txt',''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
import zipfile
import xml.etree.ElementTree as ET
with zipfile.ZipFile(report.with_suffix('.docx')) as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.endswith('.xml'):ET.fromstring(z.read(name))
print('Validated: 10-process CSV; report Markdown/DOCX; evidence index; 8-file checksum manifest. No system mutations.')
