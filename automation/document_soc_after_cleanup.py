"""Tạo bản cập nhật M2 và danh mục minh chứng thật sau giải phóng ứng dụng."""
import csv
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from export_m2_report_docx import build

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'docs/evidence/M2'
data=json.loads((EV/'M2-memory-after-cleanup-20261031-02.json').read_text(encoding='utf-8'))
eve=json.loads((EV/'M2-eve-after-cleanup-memory-20261031-01.json').read_text(encoding='utf-8'))
status=json.loads((EV/'M2-core-after-cleanup-preflight-20261031-01.json').read_text(encoding='utf-8'))
assert data['AvailableMiB']<2048 and status['live_eve_node']['status']==0
assert not status['core_process_present'] and not status['core_runtime_directory_exists']
assert all(x['unchanged'] for x in status['protected_comparison'])
def write(path,text):
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
top=['| Tiến trình | PID | Working Set (MiB) | Private Bytes (MiB) |','|---|---|---|---|']
buf=io.StringIO(newline=''); writer=csv.writer(buf)
writer.writerow(['Process','PID','WorkingSetMiB','PrivateWorkingSetMiB','PrivateBytesMiB'])
for p in data['Top15ByPrivateBytes']:
    top.append(f"| {p['Name']} | {p['PID']} | {p['WorkingSetMiB']:.1f} | {p['PrivateBytesMiB']:.1f} |")
    writer.writerow([p['Name'],p['PID'],p['WorkingSetMiB'],p['PrivateWorkingSetMiB'],p['PrivateBytesMiB']])
csvpath=EV/'M2-memory-after-cleanup-top-private-bytes-20261031.csv';write(csvpath,buf.getvalue())
groups=['| Nhóm ứng dụng | Số tiến trình | Tổng Private Bytes (MiB) | Tổng Private Working Set (MiB) |','|---|---|---|---|']
for g in data['GroupsByPrivateBytes'][:8]:
    groups.append(f"| {g['Name']} | {g['Count']} | {g['PrivateBytesMiB']:.1f} | {g['PrivateWorkingSetMiB']:.1f} |")
headroom=data['CommitLimitMiB']-data['CommittedMiB']
ratio=100*data['CommittedMiB']/data['CommitLimitMiB']
image=EV/'M2-memory-after-cleanup-real-terminal-full-20261031.png'
report=ROOT/'docs/M2/M2-report-stage2-after-cleanup-20261031.md'
appendix=f'''

## 2.18. Đo lại sau khi người dùng đóng ứng dụng Windows

### 2.18.1. Phạm vi, kết quả và quyết định khởi động

Người dùng đã xác nhận lưu công việc và đóng ứng dụng không cần. Phiên này đo lại Windows/EVE bằng thao tác chỉ đọc, bổ sung xếp hạng Private Bytes và chụp cửa sổ PowerShell thực tế. Không tự dừng tiến trình, không bật node hoặc thay đổi mạng/image/seed/lab. Các mục 2.1–2.17 phản ánh lịch sử; mục này là kết quả mới nhất của lần kiểm tra sau đóng ứng dụng.

| Chỉ số | Trước đóng ứng dụng, 20:24:37 | Sau đóng, 20:29:52 | Mẫu minh chứng, 20:30:50 |
|---|---|---|---|
| Available Windows (MiB) | 455,0 | 1410,2 | {data['AvailableMiB']:.1f} |
| Committed Windows (MiB) | 31883,3 | 29723,7 | {data['CommittedMiB']:.1f} |
| Commit limit (MiB) | 34245,7 | 34245,7 | {data['CommitLimitMiB']:.1f} |
| Tỷ lệ committed | 93,1% | 86,8% | {ratio:.1f}% |
| Pagefile đang dùng (MiB) | 2438 | 1996 | 1876 |

Tất cả thời điểm là ngày 31/10/2026, UTC+07:00, theo đồng hồ bộ thu Windows. Mẫu mới nhất: {data['CollectedAt']}. Tổng RAM lắp đặt 16384 MiB, Windows nhìn thấy 16087,9 MiB. Pagefile C:\\pagefile.sys vẫn do Windows quản lý tự động; cấp phát 18157 MiB, đỉnh sử dụng 3039 MiB. Không sửa pagefile.

Khoảng trống commit còn {headroom:.1f} MiB, tương đương {headroom/1024:.2f} GiB. Mức committed đã giảm, nhưng một mẫu đo và khoảng trống này không bảo đảm an toàn trong toàn bộ quá trình boot. Không lấy pagefile hoặc commit headroom thay cho RAM available. Điều kiện bắt buộc Windows available ≥ 2048 MiB vẫn không đạt; còn thiếu {2048-data['AvailableMiB']:.1f} MiB ở mẫu chụp. Vì vậy **không gửi lệnh start SOC-Core-L2**. Không tự thêm một ngưỡng phần trăm committed như thể đó là yêu cầu đã thống nhất; trước boot cần đánh giá lại khoảng trống commit và độ ổn định cùng điều kiện RAM.

EVE đọc lúc {eve['collector_time']}: MemAvailable 5446040 KiB = 5318,4 MiB, khoảng 5,19 GiB. Hai QEMU Ubuntu-Test (PID 287703) và Ubuntu-Console-Test (PID 297601) vẫn chạy. Core ID 3 vẫn status=0, không có QEMU/runtime; cấu hình 1 vCPU, 2048 MiB, 8 vNIC không nối mạng. Core disk/seed khớp hash marker; chín file cũ được bảo vệ giữ nguyên checksum. RAM Windows và EVE là hai lớp tài nguyên riêng, không cộng lại.

### 2.18.2. Các tiến trình có Private Bytes lớn

{chr(10).join(top)}

{chr(10).join(groups)}

Ví dụ thực tế: Code PID 21344 có Private Bytes khoảng 1023,1 MiB nhưng Working Set chỉ 145,8 MiB; mysqld PID 7596 có Private Bytes 580,7 MiB nhưng Working Set chỉ 1,7 MiB. Đóng một ứng dụng có Private Bytes lớn có thể giảm commit, nhưng không bảo đảm tăng RAM available bằng chính số Private Bytes đó.

Tổng Private Bytes của các tiến trình quan sát được là {data['ProcessPrivateBytesSumMiB']:.1f} MiB, không bằng system committed. Counter kernel nonpaged pool {data['PoolNonpagedMiB']:.1f} MiB, paged pool {data['PoolPagedMiB']:.1f} MiB. Chưa phân rã toàn bộ phần chênh lệch; không quy phần còn lại cho VMware hoặc kết luận rò rỉ bộ nhớ chỉ từ snapshot này.

VMware mksSandbox là thành phần VMware; bộ phân loại đã bổ sung tên này ở mẫu 02. Mẫu 01 ghi nhãn Other Windows do bộ lọc tên chưa bao phủ, vẫn giữ nguyên để truy vết. Các counter vmware-vmx/mksSandbox không đủ để suy ra toàn bộ chi phí vật lý của EVE. Không tự dừng những tiến trình này.

### 2.18.3. Giải thích thuật ngữ và vai trò trong phép kiểm tra SOC

| Thuật ngữ tiếng Anh | Nghĩa và nguyên lý | Vai trò, ví dụ trong SOC |
|---|---|---|
| Available physical memory | RAM vật lý sẵn sàng cấp phát | Ngưỡng trước khởi động Core: 2048 MiB trên Windows; mẫu mới chưa đạt |
| Working Set (WS) | Các trang của tiến trình hiện ở RAM, có thể gồm trang chia sẻ | Đánh giá resident; Code PID 21344 chỉ khoảng 145,8 MiB ở mẫu này |
| Private Working Set | Phần resident riêng của tiến trình | Tổng nhóm Code 823,1 MiB giúp xem xét ứng dụng có thể tự đóng; không cam kết mức thu hồi |
| Private Bytes | Bộ nhớ ảo riêng đã committed của tiến trình | Nhóm Code 3398,8 MiB; dùng tìm nhóm tiêu thụ commit, khác RAM đang resident |
| Committed memory / Commit limit | Bộ nhớ hệ thống đã cam kết và giới hạn hỗ trợ | Xem khoảng dự phòng trước boot; không đồng nhất committed với pagefile đang dùng |
| Pagefile / paging file | Tệp trên đĩa hỗ trợ lưu trang và giới hạn commit | Windows đang dùng 1876 MiB; không thay thế điều kiện RAM vật lý của lab |
| QEMU (tên phần mềm) | Phần mềm thực thi máy ảo và thiết bị ảo | Hai QEMU kiểm chứng chạy bên trong EVE; Core chưa có runtime |

Nguồn chính thức về các counter: [Microsoft Memory Performance Information](https://learn.microsoft.com/en-us/windows/win32/memory/memory-performance-information). Vai trò pagefile và system commit: [Microsoft Introduction to page files](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/introduction-to-the-page-file). Các con số và kết luận về node lấy từ log dự án, không lấy từ ví dụ trong tài liệu ngoài.

### 2.18.4. Minh chứng màn hình thực tế

![Cửa sổ PowerShell thật đo bộ nhớ Windows sau đóng ứng dụng](../evidence/M2/{image.name})

**Hình PL2.3. Kết quả đo bộ nhớ Windows và đối chiếu RAM EVE-NG sau khi đóng ứng dụng không cần thiết**

Mục đích: kiểm chứng điều kiện tài nguyên trước khởi động Core. Nội dung: cửa sổ PowerShell chạy bộ thu chỉ đọc, hiển thị available/commit/pagefile, 10 tiến trình theo Private Bytes, dữ liệu EVE và quyết định không start. Kết quả: Windows chỉ 1100,6 MiB available; Core tiếp tục tắt. Ý nghĩa: tài nguyên đã cải thiện so với trước nhưng chưa đáp ứng điều kiện vận hành đã được phê duyệt.

Ảnh chụp thật bằng Win32 PrintWindow lúc 20:31:32 UTC+07:00, kích thước 1199×882; Windows sample lúc 20:30:50, EVE sample lúc 20:29:56 được ghi riêng trên màn hình. Không diễn giải chúng thành mẫu đồng thời tuyệt đối. Đã mở rộng chiều cao cửa sổ thật trước chụp để hiện đủ kết quả; không sửa pixel, không dựng ảnh từ dữ liệu. Ảnh đầu 1199×616 bị thiếu phần cuối do cửa sổ thấp, giữ nguyên như bản chụp chưa đủ và không dùng làm minh chứng kết luận. Chỉ ảnh đầy đủ được nhúng ở đây. Cửa sổ chẩn đoán vẫn mở để người dùng xem và tự đóng.

### 2.18.5. Phương án xử lý tiếp theo

Ưu tiên giảm resident: tự đóng tab Chrome không cần và Edge nếu không dùng; lưu công việc rồi đóng cửa sổ VS Code không phục vụ SOC. Hiện chỉ quan sát được một cửa sổ Code có giao diện, nên không mặc định có nhiều cửa sổ Code để đóng; 16 tiến trình có thể thuộc cùng ứng dụng. Giữ cửa sổ SOC/Codex đang thực hiện phiên này. Không kill từng Code subprocess.

Để giảm commit, có thể thoát Zalo và Steam qua giao diện nếu không dùng (tổng Private Bytes các nhóm khoảng 945 và 861,9 MiB), nhưng hai nhóm này chỉ có private resident khoảng 65,1 và 26,4 MiB nên không hứa riêng chúng giải quyết thiếu RAM vật lý. MySQL đang có hai tiến trình; chưa rõ phục vụ công việc nào, không khuyến nghị dừng chỉ dựa trên Private Bytes. Không dừng Defender, Memory Compression, dịch vụ Windows hoặc VMware.

Người dùng có thể tự đóng cửa sổ chẩn đoán mới sau khi xem. Sau đợt giải phóng tiếp theo, đo lại available/commit/pagefile Windows và MemAvailable EVE, kiểm tra ngay trước boot; chỉ tiếp tục khởi động riêng SOC-Core-L2 khi đủ tài nguyên theo quyền đã có. Chưa cần xin lại quyền boot. Nếu không còn ứng dụng phù hợp để đóng, cần đánh giá phương án vận hành riêng; không tự dừng hai node kiểm chứng hoặc chỉnh RAM VMware.

Core chưa bật nên cloud-init, login, tám NIC Ubuntu, mapping tên/MAC, filesystem và tài nguyên runtime **chưa kiểm chứng**. Bảng cổng đã khai báo không được coi là NIC guest đã nhận đủ. Chưa cài OVS, chưa nối NIC hoặc cấu hình bridge/VLAN/trunk/mirror. Giữ nguyên các tài liệu và minh chứng cũ.
'''
prior=ROOT/'docs/M2/M2-report-stage2-preflight-20261031T2015+0700.md'
prior_diag=EV/'M2-memory-diagnostic-report-20261031.md'
write(report,prior.read_text(encoding='utf-8')+'\n\n'+prior_diag.read_text(encoding='utf-8')+appendix)
build(report)
meta=EV/'M2-memory-after-cleanup-capture-20261031.json'
write(meta,json.dumps({'captured_at':'2026-10-31T20:31:32.3764378+07:00','image':image.name,'dimensions':[1199,882],
    'source':'Actual PowerShell window via Win32 PrintWindow','window_action':'Expanded actual window height before capture to expose complete output',
    'image_content_edited':False,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
    'earlier_incomplete_capture':'M2-memory-after-cleanup-real-terminal-20261031.png','earlier_capture_role':'Retained; incomplete output; not used for conclusion'},ensure_ascii=False,indent=2)+'\n')
files=[EV/'M2-memory-after-cleanup-20261031-01.json',EV/'M2-memory-after-cleanup-20261031-02.json',EV/'M2-core-after-cleanup-preflight-20261031-01.json',EV/'M2-eve-after-cleanup-memory-20261031-01.json',csvpath,image,EV/'M2-memory-after-cleanup-real-terminal-20261031.png',meta,report,report.with_suffix('.docx')]
index=EV/'M2-memory-after-cleanup-evidence-index-20261031.md'
write(index,'# Danh mục minh chứng M2 sau đóng ứng dụng\n\nThời điểm 31/10/2026 UTC+07:00. Core chưa bật vì Windows available chưa đủ 2048 MiB.\n\n| Tệp | Nội dung | Thời điểm | Vị trí báo cáo |\n|---|---|---|---|\n'+
      '\n'.join(f'| [{p.name}]('+('../../M2/' if p.parent!=EV else '')+p.name+') | '+('Ảnh đầy đủ, dùng minh chứng' if p==image else 'Ảnh thiếu phần cuối, chỉ giữ truy vết' if p.suffix=='.png' else 'Log số đo/cấu hình hoặc báo cáo tổng hợp')+' | 20:29–20:31; thời điểm chi tiết trong JSON | 2.18; ảnh đầy đủ: Hình PL2.3 |' for p in files)+'\n')
files.append(index)
write(EV/'M2-memory-after-cleanup-SHA256SUMS-20261031.txt',''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files))
with zipfile.ZipFile(report.with_suffix('.docx')) as z:
    assert z.testzip() is None
    for name in z.namelist():
        if name.endswith('.xml'):ET.fromstring(z.read(name))
    assert any(z.read(n)==image.read_bytes() for n in z.namelist() if n.startswith('word/media/'))
    doc=z.read('word/document.xml').decode('utf-8')
    assert '2.18.' in doc and 'PL2.3' in doc and 'w:left="1701"' in doc
print('PASS: Core OFF; report DOCX/XML and real image bytes validated; 11-file manifest; no evidence overwrite.')
