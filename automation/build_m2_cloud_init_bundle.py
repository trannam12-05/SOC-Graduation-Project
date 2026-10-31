"""Lap danh muc, log chep tu anh va cap nhat bo sung preflight; khong SSH.

Tat ca tep minh chung moi dung che do tao moi. Preflight chi duoc noi them
mot muc co dau moc rieng; khong xoa/thay the cac ban ghi cu.
"""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'docs/evidence/M2'
STAMP='20261031T1844+0700'
SUCCESS='M2-cloud-init-success-20261031T184335+0700'
SYSTEM='M2-ubuntu-system-info-20261031T184400+0700'
REPORT='docs/M2/M2-cloud-init-validation-20261031.md'

def write_new(path,text):
    with path.open('x',encoding='utf-8',newline='\n') as out:
        out.write(text)

def main():
    index=DEST/('M2-evidence-index-'+STAMP+'.md')
    csv_path=index.with_suffix('.csv')
    log_path=DEST/('M2-cloud-init-validation-'+STAMP+'.log')
    for path in [index,csv_path,log_path]:
        if path.exists(): raise FileExistsError('Khong ghi de: '+str(path))
    entries=[]
    for snapshot in sorted(DEST.glob('*.json')):
        facts=json.loads(snapshot.read_text(encoding='utf-8'))
        if 'capture' not in facts: continue
        image=ROOT/facts['capture']['path']
        actual=hashlib.sha256(image.read_bytes()).hexdigest()
        if actual!=facts['capture']['sha256']: raise ValueError('Checksum sai: '+str(image))
        stem=image.stem
        if stem==SUCCESS:
            content='Cloud-init done, NoCloud /dev/sr0, errors [], recoverable_errors {}'
            position='Chương 2, mục 2.2, Hình 2.1'
            status='Ảnh chính, đã đọc kiểm tra; đầy đủ kết quả'
        elif stem==SYSTEM:
            content='Hostname, ens3, nproc=1, RAM guest 1967 MiB, whoami=soc-test, cloud-id=nocloud'
            position='Chương 2, mục 2.3, Hình 2.2'
            status='Ảnh chính, đã đọc kiểm tra; đầy đủ kết quả'
        elif 'console-initial' in stem:
            content='Console ban đầu: hostnamectl, Ubuntu 24.04.5 LTS, ens3, free -h'
            position='Minh chứng bổ trợ mục 2.3 / phụ lục'
            status='Ảnh thật; phần cloud-init trước đó đã cuộn ra ngoài màn hình'
        elif '184156' in stem:
            content='Đã gõ cloud-init status --long; khung hình chưa hiển thị kết quả'
            position='Lịch sử thu thập, không dùng cho Hình 2.1'
            status='Chưa đủ minh chứng dù tên file chứa success; không dùng kết luận'
        elif '184206' in stem or '184220' in stem:
            content='Cloud-init done; hostname/NIC/RAM; getconf lỗi do ký tự underscore bị nhận thành dấu gạch ngang'
            position='Lịch sử chẩn đoán, không dùng kết luận CPU'
            status='Ảnh thật được giữ nguyên; đã kiểm tra lại CPU bằng nproc'
        elif '184252' in stem:
            content='Cloud-init done đầy đủ; phía trên còn kết quả chẩn đoán getconf lỗi'
            position='Ảnh đối chiếu, không chọn làm Hình 2.1'
            status='Ảnh thật được giữ nguyên; thay bằng ảnh chính có màn hình rõ hơn'
        else:
            content='Hostname/NIC/nproc=1/RAM/cloud-id và output cloud-init từ lần kiểm tra trước'
            position='Ảnh đối chiếu, không chọn làm Hình 2.2'
            status='Ảnh thật được giữ nguyên; thay bằng ảnh chính có màn hình rõ hơn'
        entries.append({'ten_anh':image.name,'noi_dung':content,
                        'bat_dau':facts['collector_time_start'],'ket_thuc':facts['collector_time_end'],
                        'duong_dan':image.relative_to(ROOT).as_posix(),
                        'log_json':snapshot.relative_to(ROOT).as_posix(),
                        'vi_tri_bao_cao':position,'danh_gia':status,'sha256':actual})
    with csv_path.open('x',encoding='utf-8-sig',newline='') as target:
        writer=csv.DictWriter(target,fieldnames=list(entries[0]))
        writer.writeheader(); writer.writerows(entries)
    lines=['# Danh mục minh chứng M2: xác minh cloud-init và nền Ubuntu','',
           '## 1. Phạm vi và thời điểm','',
           'Ngày 31/10/2026. Thời gian dưới đây theo đồng hồ máy thu thập Windows, UTC+07:00 (Asia/Saigon). Đồng hồ EVE chưa đồng bộ NTP và cloud-init có last_update năm 1970; không dùng chúng làm thời điểm chụp.',
           '', 'Nguồn: framebuffer QEMU VNC thật, toàn màn hình 720 × 400; không cắt, ghép hoặc sửa nội dung. JSON cùng ảnh là dữ liệu đọc trực tiếp từ EVE và metadata của bộ thu thập; log .log là bản chép có ghi nguồn, không phải stdout guest xuất trực tiếp.',
           '', '## 2. Ảnh được sử dụng trong báo cáo','',
           f'- [Hình 2.1: cloud-init]({SUCCESS}.png)',
           f'- [Hình 2.2: hostname/NIC/CPU/RAM]({SYSTEM}.png)',
           '- [Bản thảo báo cáo Markdown](../../M2/M2-cloud-init-validation-20261031.md)',
           '- [Bản thảo báo cáo Word](../../M2/M2-cloud-init-validation-20261031.docx)',
           '', '## 3. Danh mục toàn bộ ảnh của phiên thu thập','',
           '| Tên ảnh / đường dẫn tương đối | Nội dung | Thời điểm bắt đầu → kết thúc (UTC+07:00) | Vị trí dự kiến trong báo cáo | Đánh giá |',
           '|---|---|---|---|---|']
    for entry in entries:
        lines.append(f'| [{entry["ten_anh"]}]({entry["ten_anh"]}) | {entry["noi_dung"]} | {entry["bat_dau"]} → {entry["ket_thuc"]} | {entry["vi_tri_bao_cao"]} | {entry["danh_gia"]} |')
    lines+=['','Mỗi ảnh nằm trong `docs/evidence/M2/`; JSON cùng tên lưu đường dẫn, node UUID, tham số QEMU và checksum. CSV cùng tên danh mục chứa đường dẫn đầy đủ tương đối từ gốc dự án và SHA-256 cho từng ảnh.',
            '', '## 4. Log, cấu hình quan sát và kiểm tra toàn vẹn','',
            f'- [{log_path.name}]({log_path.name}): bản chép kết quả đã quan sát, giới hạn và phân loại đạt/chưa đạt.',
            '- `*.json` đi kèm từng ảnh: snapshot cấu hình node XML, command line QEMU và liên kết mạng đọc trực tiếp. Đây là cấu hình quan sát, không phải cấu hình mới để áp dụng.',
            '- `M2-SHA256SUMS-'+STAMP+'.txt`: checksum các ảnh, JSON, log, danh mục và hai bản báo cáo; không chứa checksum của chính manifest.',
            '- Script tái thu thập: `automation/capture_m2_console_readonly.py`; script xuất Word: `automation/export_m2_report_docx.py`.',
            '', '## 5. Tình trạng và giới hạn','',
            'Đạt bước cloud-init/console và nhận diện hostname, NIC, CPU, RAM. Chưa hoàn thành toàn bộ M2; chưa cài OVS hoặc kiểm thử VLAN/trunk/mirror. 8 vNIC chỉ là đề xuất, node hiện vẫn 1 vNIC không nối mạng. IP và mapping cổng mới chưa chính thức.',
            '', 'Không ghi đè, di chuyển hoặc xóa ảnh/log cũ trong `docs/evidence/eve-ng/`. Các lần chụp trung gian và lần lệnh getconf lỗi được giữ nguyên, không dùng làm bằng chứng đạt CPU. Không có mật khẩu, private key, token hoặc hash mật khẩu trong bộ minh chứng này.','']
    write_new(index,'\n'.join(lines))
    log='''M2 - XAC MINH CLOUD-INIT / UBUNTU-CONSOLE-TEST
Ngày: 2026-10-31; múi giờ thu thập: UTC+07:00 (Asia/Saigon).
Loại log: bản chép kết quả từ ảnh console thật đã xem, không phải raw stdout guest.
User xác nhận trước phiên: soc-test đăng nhập console thành công; cloud-init done,
extended_status done, DataSourceNoCloud [seed=/dev/sr0], errors [], recoverable_errors {}.
Đối chiếu độc lập trong phiên: chạy lại các lệnh chỉ đọc tại shell soc-test.

Đối tượng: EVE 192.168.220.143 / SOC-Ubuntu-Image-Test / node 2 Ubuntu-Console-Test.
Node UUID: 09ac16f0-1614-48c5-8d01-ee1ab1b29582.
Nguồn ảnh: QEMU VNC :26870, TCP 32770 trên EVE, truy cập qua SSH có kiểm tra host key.
Ảnh nguyên framebuffer 720x400; PNG lossless; không sửa/cắt/ghép nội dung.
Không lưu password/hash/private key/token; không thử đăng nhập bằng mật khẩu.

Hình 2.1: M2-cloud-init-success-20261031T184335+0700.png
Khoảng thu: 2026-10-31T18:43:35+07:00 đến 18:43:42+07:00 (chi tiết trong JSON).
Lệnh thực tế: cloud-init status --long
status: done
extended_status: done
boot_status_code: enabled-by-generator
last_update: Thu, 01 Jan 1970 00:03:33 +0000
detail: DataSourceNoCloud [seed=/dev/sr0]
errors: []
recoverable_errors: {}
Đánh giá: ĐẠT cloud-init; chưa thu riêng exit code; không suy diễn mã thoát 0.

Hình 2.2: M2-ubuntu-system-info-20261031T184400+0700.png
Khoảng thu: 2026-10-31T18:44:00+07:00 đến 18:44:08+07:00 (chi tiết trong JSON).
Lệnh: hostname; ip -br link; nproc; free -m; whoami; cloud-id
hostname: soc-ubuntu-console-test
ip -br link: lo UNKNOWN; ens3 UP, MAC 00:50:00:00:02:00.
Chỉ ens3 là NIC Ethernet hiện có; lo không phải cổng topology.
nproc: 1
free -m: Mem total=1967, used=303, free=1494, shared=0, buff/cache=317, available=1664.
Swap total=0, used=0, free=0. Đơn vị các cột bộ nhớ: MiB theo free -m.
whoami: soc-test
cloud-id: nocloud
Đối chiếu XML/QEMU: cpu=1 / -smp 1; ram=2048 / -m 2048; ethernet=1, virtio-net-pci.
Lab test: 0 network object, 0 interface link. TAP vunl0_2_0 không có bridge master.
ens3 UP không chứng minh có IP/gateway/Internet. Không kiểm tra địa chỉ IP guest trong phiên.
Ảnh ban đầu hostnamectl: Ubuntu 24.04.5 LTS, x86-64, hostname soc-ubuntu-console-test.

Giới hạn thời gian: EVE báo Etc/UTC, NTPSynchronized=no, lệch đồng hồ Windows.
Không coi last_update năm 1970 hoặc đồng hồ EVE là thời điểm chụp; chưa sửa đồng hồ.

Lịch sử thu thập: ảnh 18:41:56 chứa lệnh nhưng chưa render kết quả; không dùng kết luận.
Lần system-info 18:42:06: underscore trong biến getconf bị bàn phím VNC nhận thành dấu -, lệnh lỗi.
Không lấy lần getconf lỗi làm kết quả CPU. Đã đổi sang nproc, trả về 1 ở ảnh chính.
Các ảnh/log trung gian giữ nguyên, xem danh mục để phân loại; không ghi đè bằng ảnh chụp lại.

ĐẠT: console soc-test; cloud-init/NoCloud; nhận diện hostname/NIC/CPU/RAM hiện tại.
CHƯA NGHIỆM THU: OVS package/runtime; VLAN, trunk, mirror, LACP, HA, thông lượng.
ĐỀ XUẤT: Core 8 vNIC = 5 access + 2 trunk OPNsense + 1 mirror; chưa áp dụng.
Chưa kiểm tra tên/giới hạn 8 NIC; chưa gán IP hoặc mapping cổng mới.
Quyền đã dùng: chỉ lệnh chẩn đoán đọc và tạo tài liệu/minh chứng trên D:\\SOC.
Không cài phần mềm, thay cấu hình mạng/seed/image, dừng/start/wipe/delete node.
Chưa đo lại checksum base/seed trong phiên này; kết quả bảo toàn checksum base ở phiên khôi phục trước.
'''
    write_new(log_path,log)
    preflight=ROOT/'docs/evidence/eve-ng/ubuntu-image-test-preflight.md'
    marker='## Xác nhận cloud-init thành công trên Ubuntu-Console-Test (2026-10-31; minh chứng M2)'
    existing=preflight.read_text(encoding='utf-8-sig')
    if marker in existing:
        raise RuntimeError('Muc cap nhat da ton tai; khong noi lap')
    addition=f'''

{marker}

> Cập nhật mới nhất này thay thế các kết luận **chưa xác minh cloud-init** đối với node `Ubuntu-Console-Test`. Các mục trước được giữ làm lịch sử; không suy rộng kết quả mới sang `Ubuntu-Test` cũ.

### Kết quả đã xác minh

- Người dùng xác nhận đã đăng nhập console thành công bằng `soc-test`. Trong phiên thu thập, console thật có shell `soc-test@soc-ubuntu-console-test`; `whoami` trả về `soc-test`.
- Đã chạy lại chỉ đọc `cloud-init status --long`: `status: done`, `extended_status: done`, `detail: DataSourceNoCloud [seed=/dev/sr0]`, `errors: []`, `recoverable_errors: {{}}`. **Cloud-init trên node console đã hoàn tất thành công theo báo cáo trạng thái guest.**
- Ảnh chính: [Hình 2.1](../M2/{SUCCESS}.png), thu lúc 18:43:35–18:43:42 ngày 31/10/2026, UTC+07:00 theo máy thu thập. Chú thích: **Hình 2.1. Kết quả kiểm tra trạng thái cloud-init trên Ubuntu Server 24.04**.
- [Hình 2.2](../M2/{SYSTEM}.png) xác nhận hostname `soc-ubuntu-console-test`, Ethernet `ens3` (MAC `00:50:00:00:02:00`) và loopback `lo`; `nproc=1`, RAM guest tổng 1967 MiB; `cloud-id=nocloud`. XML/QEMU xác nhận 1 vCPU, 2048 MiB RAM, 1 NIC VirtIO. NIC chưa nối mạng; `UP` không đồng nghĩa có kết nối ngoài.
- Node ID 2, UUID `09ac16f0-1614-48c5-8d01-ee1ab1b29582`, image variant `linux-ubuntu-24.04-soc-console-test`, CD-ROM riêng đã tồn tại và đang chạy khi kiểm tra. Không cần tạo lại node/seed. Phần 15:06 ghi chưa tạo node/ISO là snapshot lịch sử, không phải trạng thái hiện tại.

### Minh chứng, báo cáo và giới hạn

- Ảnh là framebuffer QEMU VNC thực tế toàn màn hình, không cắt/ghép/sửa nội dung; JSON cùng tên ghi nguồn, cấu hình quan sát, thời điểm và checksum. [Danh mục minh chứng](../M2/{index.name}), [log chép từ ảnh](../M2/{log_path.name}).
- [Báo cáo M2 Markdown](../../M2/M2-cloud-init-validation-20261031.md) và [bản Word](../../M2/M2-cloud-init-validation-20261031.docx) gồm Hình 2.1–2.2, giải thích bảy thuật ngữ, kiểm tra tài nguyên và đề xuất NIC.
- `last_update` trong guest ghi năm 1970; EVE chưa đồng bộ NTP và lệch giờ máy thu thập. Không dùng các giá trị đó làm thời điểm ảnh, chưa chỉnh giờ. Chưa thu riêng mã thoát của lệnh hoặc toàn bộ log cloud-init trong guest.
- Kết quả xác nhận nền Ubuntu quản trị được, **chưa nghiệm thu OVS/VLAN/trunk/mirror hoặc toàn bộ M2**. Theo hồ sơ OVS chưa được cài; phiên này không cài và chưa kiểm kê package/runtime guest.
- Khuyến nghị Core **8 vNIC** (5 access cho VLAN 30/40/50/60/99 + 2 trunk tới hai OPNsense + 1 mirror). Đây là đề xuất; chưa đổi số NIC, chưa xác nhận tên NIC bổ sung, số cổng peer, subnet/IP hoặc khả năng template ở cấu hình 8 NIC. Hai trunk HA không phải một bond LACP xuyên hai firewall.
- Phiên này chỉ chạy lệnh chẩn đoán đọc và ghi tài liệu/minh chứng trên Windows. Không sửa seed/image/mạng, không cài OVS, không dừng/start/wipe/xóa node. Các ảnh/log cũ được giữ nguyên; các lần chụp trung gian có giới hạn được phân loại trong danh mục.

### Bước tiếp theo cần phê duyệt

Chốt phương án NIC và node Core đích; phê duyệt riêng việc tăng NIC/vòng đời node nếu cần, kế hoạch cấp gói để cài OVS và mạng kiểm thử. Chưa tự nối pnet/NAT/Internet. Core tiếp tục chỉ Layer 2; gateway, inter-VLAN routing, firewall rules và NAT xử lý trên OPNsense.
'''
    with preflight.open('a',encoding='utf-8',newline='\n') as target:
        target.write(addition)
    print(json.dumps({'images':len(entries),'index':str(index),'csv':str(csv_path),'log':str(log_path),'preflight':'appended only'},ensure_ascii=False))

if __name__=='__main__': main()
