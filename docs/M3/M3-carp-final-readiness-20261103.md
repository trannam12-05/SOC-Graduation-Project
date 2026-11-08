# CHƯƠNG 3. M3 — CARP FINAL READINESS NGÀY03/11/2026

## 3.1. Quyết định và điểm dừng

**NOT READY TO APPLY CARP**

Resources FAIL: tổng RAM khai báo của Core L2 và hai firewall vượt MemTotal EVE-NG, chưa tính dự phòng cho hệ điều hành. Đã dừng ngay sau kiểm tài nguyên theo yêu cầu người dùng. Không boot Core, không bật node khác, không kiểm tiếp guest/L2/VIP/VHID/pfsync, không sửa tài nguyên hoặc cấu hình, không apply CARP.

Cửa sổ thu: **2026-11-03T22:16:20.158928+07:00 → 2026-11-03T22:16:24.650427+07:00 (UTC+07:00)**. Windows resource được thu ngay sau cửa sổ SSH, trong cùng lượt collector; JSON chưa ghi timestamp riêng cho lệnh Windows, không diễn giải timestamp end SSH thành giờ Windows chính xác. Minh chứng: `docs/evidence/M3/carp-final-readiness-20261103/resources-before.json` và các stdout TXT trích xuất từ JSON.

## 3.2. Bảng kết quả

NOT RUN nghĩa là chưa thực hiện do điều kiện dừng Resources; không được ép thành PASS hoặc FAIL kỹ thuật của Core/VLAN/pfsync. INCONCLUSIVE nghĩa là chưa đủ bằng chứng đánh giá xung đột. Lượt này không lấy checkpoint trước thay cho phép đo mới.

| Check | Result |
|---|---|
|Resources|FAIL|
|Core L2|NOT RUN — chưa boot/kiểm; không kết luận Core hỏng|
|VLAN30 L2|NOT RUN|
|VLAN40 L2|NOT RUN|
|VLAN50 L2|NOT RUN|
|VLAN60 L2|NOT RUN|
|VLAN99 L2|NOT RUN|
|VIP30|INCONCLUSIVE|
|VIP40|INCONCLUSIVE|
|VIP50|INCONCLUSIVE|
|VIP60|INCONCLUSIVE|
|VIP99|INCONCLUSIVE|
|VHID|INCONCLUSIVE|
|pfsync|NOT RUN — chưa phân loại READY/NOT READY bằng số đo mới|

Checkpoint recovery trước đó ghi pfsync hai phía READY, syncok1/demotion0; đó là lịch sử đã kiểm, không bị phủ nhận bởi việc dừng tài nguyên này. VIP persistent/runtime đều chưa tồn tại ở recovery, nhưng điều đó không chứng minh VIP không bị một thiết bị khác dùng khi topology hoạt động.

## 3.3. Tài nguyên thực tế

### 3.3.1. RAM EVE-NG và ngân sách tối thiểu

| Hạng mục | MiB | Căn cứ |
|---|---:|---|
|EVE MemTotal|7897.78|/proc/meminfo: 8087324 KiB|
|EVE MemAvailable|2771.18|/proc/meminfo: 2837688 KiB|
|Core L2 khai báo|2048|Lab XML, hiện không chạy|
|Primary khai báo|3072|Lab XML/QEMU PID4159, đang chạy|
|Secondary khai báo|3072|Lab XML/QEMU PID49523, đang chạy|
|Tổng ba node|8192|2048+3072+3072|
|Thiếu ngay ở tổng RAM guest so với MemTotal|294.22|Chưa tính EVE/kernel/cache/dự phòng|
|Dự phòng theo guard dự án|1024|1 GiB, giữ nguyên quy tắc không tự hạ ngưỡng|
|Mục tiêu tổng guest + dự phòng|9216|Điều kiện ngân sách, không phải thay RAM đã thực hiện|
|Thiếu so với mục tiêu trên|1318.22|Chỉ là tính toán từ cấu hình hiện tại|
|Available còn lại nếu cấp đủ RAM khai báo cho Core|723.18|Không phải dự báo RSS chính xác; thấp hơn dự phòng1 GiB|

Hai điều kiện đều không đạt: tổng guest8192 MiB vượt MemTotal7897.78 MiB; MemAvailable2771.18 MiB thấp hơn Core2048+reserve1024=3072 MiB. Dù QEMU cấp phát theo nhu cầu, không dùng mức RSS tức thời hoặc khả năng overcommit để bỏ ngân sách đã đặt. SwapTotal4096.00 MiB, SwapFree bằng SwapTotal; swap dùng0, vmstat si/so0. Swap chưa dùng không chứng minh đủ RAM để start node thứ ba.

Hai firewall hiện có VmRSS lần lượt3140.71 và3138.65 MiB; VmSwap0. Đây là RSS tiến trình, không cộng hoặc trừ trực tiếp thay MemAvailable vì có thể có vùng chia sẻ/overhead.

Guard `automation/start_topology_node.py` cũ còn có ngân sách nhóm cứng5120/6144 MiB và không biểu diễn đúng nhóm8192 MiB này. Không chạy script đó, không sửa/bỏ guard để ép boot. Phân tích hiện tại dùng cấu hình ba node và số đo MemTotal/MemAvailable thật; bản thân ngân sách mới đã không đạt.

### 3.3.2. CPU và Windows host

EVE có4 logical CPU. Cấu hình tối thiểu là Core1+Primary2+Secondary2=5 vCPU; số vCPU là phân bổ của guest, không tự coi vượt logical CPU là lỗi tuyệt đối. Load average1/5/15 phút: 3.75, 3.68, 3.72. Hai mẫu vmstat sau khoảng chờ có idle96%/93%, iowait0, si/so0; CPU không phải nguyên nhân quyết định FAIL trong cửa sổ này. Không kết luận CPU đáp ứng mọi tải tương lai từ các mẫu ngắn.

Windows: physical available365.44 MiB; commit available3490.83 MiB; logical processors12. Dự phòng commit2 GiB từng dùng còn đạt, nhưng RAM vật lý khả dụng thấp. Không tự tăng RAM VMware/EVE, giảm RAM firewall/Core hoặc tắt firewall để giải quyết.

## 3.4. Trạng thái node và phạm vi chưa kiểm

Kiểm kê /proc QEMU chỉ thấy Primary và Secondary, khớp UUID riêng từng node; Core không có tiến trình chạy. Không bật Wazuh/Suricata/endpoint. Chưa boot Core nên chưa có phép đọc mới về br-core-l2, access/trunk/allowed VLAN hoặc forwarding/IP của Core; không ghi Core PASS chỉ từ nghiệm thu M2 trước đó.

Chưa phát benign traffic, ARP probe hoặc bắt protocol112; chưa xác minh broadcast domain chung của năm VLAN, chưa kết luận FREE cho năm VIP và chưa kiểm VHID30/40/50/60/99 trong môi trường L2 hoạt động. Không thay VHID/VIP đã duyệt, không tạo VIP để thử. Pfsync không bị gọi backend/restart để lấy kết quả; không vào console guest sau khi Resources FAIL.

## 3.5. Minh chứng và giới hạn ảnh

Đã lưu output thật free/vmstat/lscpu/uptime/process usage, thông số Windows, cấu hình RAM/CPU đọc từ lab và danh sách QEMU vào thư mục evidence mới. `readiness-result.json` có phép tính ngân sách/điểm dừng. `evidence-index.csv/md` ghi tên/nội dung/thời điểm/múi giờ/path/vị trí báo cáo/SHA-256.

Không có ảnh screenshot tài nguyên mới. Công cụ đọc được stdout SSH nhưng chưa có phương tiện chụp cửa sổ terminal thực đang hiển thị output đó. Không dựng ảnh text giả. Xem `manual-screenshot-guide.md`: mở SSH EVE, chạy date/free/vmstat/nproc/uptime, mở Windows Task Manager Memory, chụp đầy đủ và lưu timestamp thực mới trong thư mục evidence. Không báo ảnh chưa chụp là minh chứng đã có. Không tạo hình/chú thích đánh số cho một hình chưa tồn tại.

## 3.6. Bước tiếp theo đề xuất, chưa thực hiện

Cần một phương án tài nguyên được người dùng duyệt trước khi chạy lại readiness: hoặc đủ ngân sách EVE và Windows cho cả ba node, hoặc thay đổi phân bổ được duyệt riêng và kiểm ảnh hưởng. Không suy quyền boot Core thành quyền thay RAM/image/seed/mạng hoặc shutdown firewall. Điều kiện cần đo lại trước boot: MemTotal đủ tổng RAM ba node cộng1 GiB dự phòng; MemAvailable đủ RAM Core cộng1 GiB; không có swap-in/out và có dự phòng Windows phù hợp. Đây là điều kiện tính theo phân bổ hiện tại, không tự áp dụng thay đổi.

Khi điều kiện tài nguyên đạt ở lượt sau mới boot Core theo phạm vi được duyệt, đọc nguyên cấu hình M2 và dừng nếu sai; sau đó kiểm L2, VIP/VHID và pfsync. Chưa có quyền/tiến hành CARP apply từ báo cáo readiness này.

## 3.7. Thuật ngữ và căn cứ

RAM (Random Access Memory, bộ nhớ truy cập ngẫu nhiên) chứa bộ nhớ làm việc của EVE và guest; MemAvailable là ước lượng RAM Linux có thể cấp mà không cần swap, khác MemFree chỉ đếm phần chưa dùng. RSS (Resident Set Size, bộ nhớ tiến trình hiện thường trú) đo footprint hiện tại, không thay RAM khai báo khi lập ngân sách. vCPU (virtual Central Processing Unit, CPU ảo) là đơn vị CPU được cấp cho guest và được host lập lịch. Trong SOC này ba node dự kiến cần8192 MiB/5 vCPU; số RAM/CPU khai báo và số đo host đã được đọc, chưa kiểm tải ba node.

CARP (Common Address Redundancy Protocol, dự phòng địa chỉ chung) dự kiến chia sẻ VIP (Virtual IP Address, địa chỉ IP ảo) giữa hai OPNsense để dự phòng gateway; VHID (Virtual Host Identifier) nhận diện nhóm quảng bá. VLAN (Virtual Local Area Network, mạng LAN ảo) phân tách miền L2; trunk IEEE802.1Q mang nhiều VLAN qua cổng chung. Readiness cần đường L2 thực tế tới hai firewall trước khi kết luận xung đột/bầu chọn. Trong lượt này các phép thử đó chưa chạy. Pfsync là cơ chế đồng bộ trạng thái PF; READY cũ chưa được tái đo trong lượt bị dừng. OPNsense là tên sản phẩm, không tự khai triển.

Vai trò/nguyên lý/ví dụ các khái niệm SOC, access port, OVS/bridge, LACP, SPAN/port mirroring, QEMU/QCOW2, cloud-init/NoCloud, SSH, HA, NAT/DHCP, IDS/IPS, Suricata và Wazuh được giữ trong `docs/TOPOLOGY_TERMS.md` và các báo cáo M1/M2/M3; chúng không được nghiệm thu mới bởi lần đo tài nguyên này. Kết luận dùng output hệ thống nội bộ, không sử dụng nguồn ngoài mới. Nếu xuất Word: A4, Times New Roman12–13, lề trái3 cm, các lề còn lại2 cm; chưa xuất Word trong lượt này.

Đã dừng tại Resources FAIL; không boot Core, không thay cấu hình và không apply CARP.
