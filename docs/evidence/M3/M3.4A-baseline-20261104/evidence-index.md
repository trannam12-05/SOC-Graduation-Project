# CHƯƠNG 3. KHÔI PHỤC BASELINE M3.4A

## 3.4.1. Kết luận và phạm vi

**READY_FOR_RETEST**, tổng hợp lúc 2026-11-04T16:39:50.103201+07:00 (UTC+07:00). Chỉ boot và xác minh Core, hai OPNsense và Data-Center có sẵn; không state/failover test, không HTTP request, không M3.4B. Chưa kết luận toàn M3.4 DONE/PASS. Không sửa cấu hình guest; pfsync/CARP tự trở lại trạng thái yêu cầu sau boot.

Thời gian thu dùng collector chuyển sang UTC+07:00; giờ bên trong EVE/guest được lưu riêng, không thay giờ collector. Các banner/MOTD cũ trong console Linux không phải địa chỉ runtime; nghiệm thu dùng ip address, service/listener, OVS và ifconfig thực tế trong JSON có transport SHA-256.

## 3.4.2. Bảng kết quả

| Thành phần | Kết quả | Minh chứng |
|---|---|---|
| Đúng bốn node, RAM1024/2048/2048/1024 MiB | PASS | host-final.json; bốn start receipts |
| Core OVS active, Layer2, không IP ngoài loopback, forwarding0/0 | PASS | core-baseline.json; core-public-proof |
| Access ens3–ens7 và trunk ens8/ens9 đúng VLAN30/40/50/60/99 | PASS | core-baseline.json; core-ovs-proof; final-baseline-arp.json |
| Primary .2 và Secondary .3 đúng năm VLAN | PASS | primary/secondary-baseline.json |
| SYNC ping2/2 và pfsync READY, syncok1, demotion0 hai phía | PASS | hai baseline JSON; pfsync-proof; final-baseline-pfsync-packets.json |
| Primary MASTER / Secondary BACKUP năm VLAN, năm VIP .1 đúng | PASS | hai baseline JSON; carp-proof; final-baseline-carp.json |
| Data-Center .30.10/24, HTTP8000 active/LISTEN | PASS mức baseline | endpoint-baseline.json; endpoint-proof; không kiểm thử HTTP request |
| Evidence M3.4 cũ giữ nguyên | PASS | previous-evidence-integrity.json:137 tệp |
| State/failover/recovery test mới | NOT_RUN | Ngoài phạm vi M3.4A |

## 3.4.3. Giải thích và ý nghĩa

Open vSwitch (OVS — tên sản phẩm) làm switch Layer2: flow NORMAL và bảng port access/trunk phân phối frame theo Virtual Local Area Network (VLAN — mạng LAN ảo). Access port mang frame của một VLAN tới endpoint; trunk dùng cơ chế gắn thẻ IEEE802.1Q để mang nhiều VLAN giữa Core và firewall. Đã kiểm chứng mapping access30/40/50/60/99 và trunk năm VLAN, cùng ARP từ các access port tới .2/.3/.1. Core không làm gateway hoặc inter-VLAN routing.

OPNsense là tên sản phẩm firewall. Common Address Redundancy Protocol (CARP — giao thức dự phòng địa chỉ chung) dùng quảng bá để điều phối MASTER/BACKUP phục vụ Virtual IP address (VIP — địa chỉ IP ảo). Trong SOC, các VIP .1 của năm VLAN là gateway dự phòng trên OPNsense; lượt này chỉ xác nhận vai trò ban đầu, không chuyển vai.

pfsync là tên chính thức của giao diện/giao thức đồng bộ state Packet Filter, không tự tạo dạng khai triển. Baseline xác nhận UP/RUNNING, syncdev vtnet2, peer đối ứng đúng, syncok1 và demotion0; có gói protocol240 hai chiều. Không dùng readiness để thay kết luận giữ phiên hoặc state synchronization dưới failover. Kết quả lần test cũ vẫn là bằng chứng một phần của lần thử bị gián đoạn.

Endpoint Data-Center đã tự phục hồi IP và listener nhưng default route gốc là .30.2, host route runtime riêng qua .30.1 của phép thử trước không còn sau reboot. Không thay route trong lượt này. Khi M3.4B được giao, cần setup lại client và chiều về CARP cho session mới theo phương án đã duyệt; đó là chuẩn bị retest, không phải lỗi IP/OVS/pfsync baseline.

## 3.4.4. Ảnh console thực tế

![Hình 3.1. Core chỉ Layer2 và dịch vụ OVS active.](core-public-proof-20261104T163628+0700.png)

Hình 3.1. Core chỉ Layer2 và dịch vụ OVS active.

Mục đích, nội dung, kết quả và ý nghĩa: Xem địa chỉ và forwarding0/0; xác nhận không chuyển routing lên Core.

![Hình 3.2. Bảng access/trunk và flow NORMAL.](core-ovs-proof-20261104T163914+0700.png)

Hình 3.2. Bảng access/trunk và flow NORMAL.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc tag/trunks cùng flow chuyển mạch; đối chiếu ARP năm VLAN.

![Hình 3.3. Primary MASTER cả năm CARP.](primary-carp-proof-20261104T163549+0700.png)

Hình 3.3. Primary MASTER cả năm CARP.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc IP .2, VIP .1 và VHID30/40/50/60/99; xác nhận vai trò chính.

![Hình 3.4. Secondary BACKUP cả năm CARP.](secondary-carp-proof-20261104T163549+0700.png)

Hình 3.4. Secondary BACKUP cả năm CARP.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc IP .3, VIP .1 và skew100; xác nhận dự phòng.

![Hình 3.5. Pfsync và SYNC trên Primary.](primary-pfsync-proof-20261104T163654+0700.png)

Hình 3.5. Pfsync và SYNC trên Primary.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc syncok1/demotion0 và ping đối ứng; xác nhận readiness phía chính.

![Hình 3.6. Pfsync và SYNC trên Secondary.](secondary-pfsync-proof-20261104T163654+0700.png)

Hình 3.6. Pfsync và SYNC trên Secondary.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc syncok1/demotion0 và ping đối ứng; đối chiếu hai phía.

![Hình 3.7. Data-Center đã boot và listener hoạt động.](endpoint-proof-20261104T163040+0700.png)

Hình 3.7. Data-Center đã boot và listener hoạt động.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc địa chỉ/route/service/ss; chỉ xác minh baseline, chưa HTTP request.

## 3.4.5. Checkpoint và giới hạn

Giữ bốn node đang chạy; không có node không liên quan được bật. Không chạy lại client cũ, không phục hồi session đã mất, không thu state-table của bài test hoặc thực hiện failover. M3.4 chỉ READY_FOR_RETEST, M3.4B chưa chạy. Config hai firewall khớp hash trước gián đoạn; không áp lại native pfsync để đạt kết quả. VIP/VHID/advbase/advskew, Core, topology và IP plan giữ nguyên.

Các capture baseline-* đầu được thu trong lúc guest hoàn tất boot; đối chiếu nghiệm thu dùng final-baseline-* sau boot, kết hợp JSON runtime. Trường vip_conflict_seen trong collector ARP tái sử dụng chỉ nghĩa có trả lời VIP, không có nghĩa phát hiện xung đột trong lượt này. Ảnh cũ và bằng chứng lần test trước không bị chỉnh hoặc xóa; previous-evidence-integrity.json xác nhận checksum.

## 3.4.6. Danh mục minh chứng

| Tệp | Nội dung | Thời điểm thu (múi giờ) | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
| auth-observe-0-20261104T163124+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:31:27.263006+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/auth-observe-0-20261104T163124+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| auth-observe-0-20261104T163124+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:31:27.265123+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/auth-observe-0-20261104T163124+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| auth-observe-1-20261104T163124+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:31:27.322756+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/auth-observe-1-20261104T163124+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| auth-observe-1-20261104T163124+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:31:27.325481+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/auth-observe-1-20261104T163124+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| auth-observe-2-20261104T163124+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:31:27.297059+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/auth-observe-2-20261104T163124+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| auth-observe-2-20261104T163124+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:31:27.298159+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/auth-observe-2-20261104T163124+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| baseline-arp.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:28:23.878771+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/baseline-arp.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| baseline-carp.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:28:21.878202+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/baseline-carp.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| baseline-pfsync-packets.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:28:36.832827+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/baseline-pfsync-packets.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-0-20261104T162525+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:25:29.889535+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-0-20261104T162525+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-0-20261104T162525+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:25:29.890031+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-0-20261104T162525+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-1-20261104T162525+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:25:29.984542+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-1-20261104T162525+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-1-20261104T162525+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:25:29.985778+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-1-20261104T162525+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-2-20261104T162525+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:25:29.670774+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-2-20261104T162525+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-2-20261104T162525+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:25:29.673112+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-2-20261104T162525+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-3-20261104T162525+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:25:29.763476+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-3-20261104T162525+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-3-20261104T162525+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:25:29.765066+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-3-20261104T162525+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-progress-0-20261104T162727+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:27:30.941246+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-progress-0-20261104T162727+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-progress-0-20261104T162727+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:27:30.942258+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-progress-0-20261104T162727+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-progress-1-20261104T162727+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:27:31.061353+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-progress-1-20261104T162727+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-progress-1-20261104T162727+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:27:31.062376+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-progress-1-20261104T162727+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-progress-2-20261104T162727+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:27:31.001023+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-progress-2-20261104T162727+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-progress-2-20261104T162727+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:27:31.002032+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-progress-2-20261104T162727+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-progress-3-20261104T162727+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:27:30.926185+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-progress-3-20261104T162727+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| boot-progress-3-20261104T162727+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:27:30.927732+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/boot-progress-3-20261104T162727+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| console-wait-0-20261104T162942+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:29:51.399304+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/console-wait-0-20261104T162942+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| console-wait-0-20261104T162942+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:29:51.402730+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/console-wait-0-20261104T162942+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| console-wait-1-20261104T162942+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:29:51.477528+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/console-wait-1-20261104T162942+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| console-wait-1-20261104T162942+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:29:51.479564+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/console-wait-1-20261104T162942+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| console-wait-2-20261104T162942+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:29:51.436772+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/console-wait-2-20261104T162942+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| console-wait-2-20261104T162942+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:29:51.437866+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/console-wait-2-20261104T162942+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-baseline-execute-20261104T163328+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:09.036643+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-baseline-execute-20261104T163328+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-baseline-execute-20261104T163328+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:34:09.038270+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-baseline-execute-20261104T163328+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-baseline-header-20261104T163409+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:33.238560+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-baseline-header-20261104T163409+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-baseline-header-20261104T163409+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:34:33.239459+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-baseline-header-20261104T163409+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-baseline-page-0-20261104T163433+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:55.926712+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-baseline-page-0-20261104T163433+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-baseline-page-0-20261104T163433+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:34:55.927728+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-baseline-page-0-20261104T163433+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-baseline.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:56.062914+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-baseline.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-ovs-proof-20261104T163914+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:39:25.375472+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-ovs-proof-20261104T163914+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-ovs-proof-20261104T163914+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:39:25.378786+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-ovs-proof-20261104T163914+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-public-proof-20261104T163628+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:36:39.922809+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-public-proof-20261104T163628+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-public-proof-20261104T163628+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:36:39.923924+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-public-proof-20261104T163628+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-root-confirm-20261104T163318+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:33:21.397599+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-root-confirm-20261104T163318+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-root-confirm-20261104T163318+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:33:21.401333+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-root-confirm-20261104T163318+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-shell-check-20261104T163239+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:32:41.109337+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-shell-check-20261104T163239+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| core-shell-check-20261104T163239+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:32:41.109337+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/core-shell-check-20261104T163239+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-baseline-execute-20261104T162750+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:28:38.706915+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-baseline-execute-20261104T162750+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-baseline-execute-20261104T162750+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:28:38.709526+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-baseline-execute-20261104T162750+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-baseline-header-20261104T162838+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:29:04.985680+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-baseline-header-20261104T162838+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-baseline-header-20261104T162838+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:29:04.986776+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-baseline-header-20261104T162838+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-baseline-page-0-20261104T162905+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:29:30.383817+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-baseline-page-0-20261104T162905+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-baseline-page-0-20261104T162905+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:29:30.385535+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-baseline-page-0-20261104T162905+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-baseline.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:29:30.558408+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-baseline.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-proof-20261104T163040+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:30:50.040245+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-proof-20261104T163040+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| endpoint-proof-20261104T163040+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:30:50.041771+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/endpoint-proof-20261104T163040+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| final-baseline-arp.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:30:51.698230+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/final-baseline-arp.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| final-baseline-carp.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:30:51.247617+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/final-baseline-carp.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| final-baseline-pfsync-packets.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:31:06.947492+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/final-baseline-pfsync-packets.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| host-before.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:24:35.190024+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/host-before.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| host-booting.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:27:16.202280+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/host-booting.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| host-final.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:37:08.101822+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/host-final.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| M3.4A-readiness.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:39:50.103201+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/M3.4A-readiness.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| previous-evidence-integrity.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:29:41.512121+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/previous-evidence-integrity.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-baseline-execute-20261104T163212+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:33:28.568383+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-baseline-execute-20261104T163212+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-baseline-execute-20261104T163212+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:33:28.570623+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-baseline-execute-20261104T163212+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-baseline-header-20261104T163328+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:33:53.143042+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-baseline-header-20261104T163328+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-baseline-header-20261104T163328+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:33:53.145732+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-baseline-header-20261104T163328+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-baseline-page-0-20261104T163353+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:16.246186+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-baseline-page-0-20261104T163353+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-baseline-page-0-20261104T163353+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:34:16.247799+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-baseline-page-0-20261104T163353+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-baseline.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:16.363493+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-baseline.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-carp-proof-20261104T163549+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:35:59.377003+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-carp-proof-20261104T163549+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-carp-proof-20261104T163549+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:35:59.378518+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-carp-proof-20261104T163549+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-pfsync-proof-20261104T163654+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:37:04.171882+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-pfsync-proof-20261104T163654+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| primary-pfsync-proof-20261104T163654+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:37:04.173585+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/primary-pfsync-proof-20261104T163654+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| PROGRESS.md.before | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:20:04.863078+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/PROGRESS.md.before | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-baseline-execute-20261104T163229+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:33:45.244515+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-baseline-execute-20261104T163229+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-baseline-execute-20261104T163229+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:33:45.246693+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-baseline-execute-20261104T163229+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-baseline-header-20261104T163345+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:10.675599+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-baseline-header-20261104T163345+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-baseline-header-20261104T163345+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:34:10.676105+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-baseline-header-20261104T163345+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-baseline-page-0-20261104T163410+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:33.934601+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-baseline-page-0-20261104T163410+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-baseline-page-0-20261104T163410+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:34:33.936709+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-baseline-page-0-20261104T163410+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-baseline.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:34:34.077865+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-baseline.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-carp-proof-20261104T163549+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:35:58.935679+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-carp-proof-20261104T163549+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-carp-proof-20261104T163549+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:35:58.938277+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-carp-proof-20261104T163549+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-pfsync-proof-20261104T163654+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:37:05.098721+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-pfsync-proof-20261104T163654+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-pfsync-proof-20261104T163654+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:37:05.100294+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-pfsync-proof-20261104T163654+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-shell-enter-20261104T163203+0700.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:32:10.722668+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-shell-enter-20261104T163203+0700.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| secondary-shell-enter-20261104T163203+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T16:32:10.725341+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/secondary-shell-enter-20261104T163203+0700.png | M3.4A — thành phần tương ứng/phụ lục truy vết |
| SOC_TO_DO.md.before | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:20:04.860967+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/SOC_TO_DO.md.before | M3.4A — thành phần tương ứng/phụ lục truy vết |
| start-Data-Center.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:24:45.971118+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/start-Data-Center.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| start-OPNsense-Primary.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:24:42.938129+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/start-OPNsense-Primary.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| start-OPNsense-Secondary.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:24:40.695035+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/start-OPNsense-Secondary.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
| start-SOC-Core-L2.json | Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần | 2026-11-04T16:24:38.472573+07:00 | docs/evidence/M3/M3.4A-baseline-20261104/start-SOC-Core-L2.json | M3.4A — thành phần tương ứng/phụ lục truy vết |
