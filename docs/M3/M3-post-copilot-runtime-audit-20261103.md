# CHƯƠNG 3. M3 — RECOVERY CHECKPOINT SAU COPILOT

## 3.1. Kết luận và phạm vi

Ngày03/11/2026, thu console từ21:54 UTC+07:00; thời điểm tổng hợp **2026-11-03T22:13:03+07:00**. Primary và Secondary đang chạy đúng OPNsense26.7 (amd64), FreeBSD15.1-RELEASE-p1, shell root. **Cấu hình persistent cả hai khớp nguyên byte backup Nhóm1B; chưa có CARP VIP trong cấu hình lưu và chưa có CARP runtime trên năm VLAN.** Năm VLAN đều UP và đúng IP; pfsync hai phía READY trong phạm vi runtime được đọc.

**Rollback required: NO trong phạm vi kiểm tra. Next action: MORE EVIDENCE REQUIRED** trước khi áp CARP, vì Core đang tắt và chưa kiểm đường Layer2/xung đột trên VLAN khi Core hoạt động. Không có cơ sở yêu cầu repair/restore firewall từ lỗi nhập console cũ.

Chỉ truy cập EVE-NG qua SSH hiện có và framebuffer VNC hai firewall, đọc node/process/config/interface/log/counter. Không start/stop/reboot node, không chỉnh config.xml, không apply CARP, không tạo/xóa VLAN/VIP, không reload/restart/failover, không sửa Core/M2/firewall/NAT/DHCP, không cleanup/commit/push. Reader chỉ chạy trong bộ nhớ guest, không ghi helper/config/backup vào guest; snapshot công khai và báo cáo lưu trên Windows. Không lưu secret plaintext.

### 3.1.1. Căn cứ và giới hạn

Nguồn mới: `docs/evidence/M3/post-copilot-runtime-audit-20261103/`. Các tệp `primary-snapshot.json`, `secondary-snapshot.json` được giải mã glyph chính xác từ ảnh console, có SHA-256 toàn payload; không dùng OCR phỏng đoán. `comparison-results.json` đối chiếu backup và runtime; `recovery-result.json` lưu kết luận. `baseline-public.json` chỉ chứa checksum/interface đã lọc từ backup cục bộ.

Bản đọc snapshot diễn ra trong cửa sổ ảnh snapshot-ready khoảng22:06–22:07; các trang nhận và ảnh đọc bổ sung tới22:09, có thời gian collector cụ thể trong JSON/index. `host-inventory.json` không ghi chính xác acquisition timestamp lúc chạy, nên giữ chú thích giới hạn, không tự dựng giờ thu. Đồng hồ guest/EVE không được dùng thay collector Windows UTC+07:00.

HEALTHY bên dưới chỉ là OS/shell/interface/SYNC/pfsync hiện có trong phạm vi đọc; không phải nghiệm thu WAN/Internet/CARP/HA end-to-end. Một phép đọc lỗi không tự quy thành firewall hỏng. Kết quả snapshot/config được xác thực theo node UUID, MAC/SYNC IP và checksum backup riêng từng firewall; hostname hai máy giống nhau nên không dùng hostname đơn độc nhận dạng.

## 3.2. A. FIREWALL HEALTH

| Máy | Trạng thái | Nhận dạng đã kiểm chứng | Giới hạn |
|---|---|---|---|
| Primary | HEALTHY trong phạm vi đọc | EVE ID1; UUID fe606d13-1542-490b-b651-5c1c6289afde; OPNsense26.7/FreeBSD15.1-RELEASE-p1; UID0; SYNC10.255.255.1 | Chưa cấu hình/kiểm CARP; WAN không có IPv4/default route trong snapshot |
| Secondary | HEALTHY trong phạm vi đọc | EVE ID2; UUID64b94195-c24d-4107-95d4-737e0a4b3016; cùng phiên bản; UID0; SYNC10.255.255.2 | Cùng giới hạn, không suy HA PASS |

Chỉ hai QEMU firewall chạy; Core và các node khác không chạy ở kiểm kê. Các VLAN báo link active ở guest không chứng minh lưu lượng trao đổi qua Core khi Core tắt. vtnet3 không administratively UP và chưa có IP ở cả hai, giống bản đọc Nhóm1B; không tự nâng thành WAN phụ hoạt động. Không đổi IP/gateway hoặc phát DHCP renew để tìm kết quả.


![Hình 3.1. Xác nhận shell và hệ điều hành Primary.](../evidence/M3/post-copilot-runtime-audit-20261103/primary-proof-raw-20261103T215853+0700.png)

**Hình 3.1. Xác nhận shell và hệ điều hành Primary.**

Mục đích: nhận dạng guest trước đọc cấu hình. Nội dung: opnsense-version, uname, whoami và ifconfig -l. Kết quả: OPNsense26.7, FreeBSD15.1-RELEASE-p1, root và đủ tên VLAN. Ý nghĩa: xác nhận đang ở shell hợp lệ; UUID và SYNC dùng bổ sung nhận dạng.


![Hình 3.2. Xác nhận shell và hệ điều hành Secondary.](../evidence/M3/post-copilot-runtime-audit-20261103/secondary-shell-proof-20261103T215641+0700.png)

**Hình 3.2. Xác nhận shell và hệ điều hành Secondary.**

Mục đích và nội dung tương tự phía Primary. Kết quả: cùng phiên bản, root, đủ VLAN. Ý nghĩa: không suy trạng thái Secondary từ riêng Primary; hostname giống nhau không phải bằng chứng nhầm node.

## 3.3. B. VLAN VÀ SYNC

| VLAN | Primary runtime | Secondary runtime | Expected | Result |
|---|---|---|---|---|
| 30 | UP;192.168.30.2/24 | UP;192.168.30.3/24 | vtnet0_vlan30; tag30, parent vtnet0; IP .2/.3 /24 | PASS đối chiếu cấu hình/runtime, không phải traffic test |
| 40 | UP;192.168.40.2/24 | UP;192.168.40.3/24 | vtnet0_vlan40; tag40, parent vtnet0; IP .2/.3 /24 | PASS đối chiếu cấu hình/runtime, không phải traffic test |
| 50 | UP;192.168.50.2/24 | UP;192.168.50.3/24 | vtnet0_vlan50; tag50, parent vtnet0; IP .2/.3 /24 | PASS đối chiếu cấu hình/runtime, không phải traffic test |
| 60 | UP;192.168.60.2/24 | UP;192.168.60.3/24 | vtnet0_vlan60; tag60, parent vtnet0; IP .2/.3 /24 | PASS đối chiếu cấu hình/runtime, không phải traffic test |
| 99 | UP;192.168.99.2/24 | UP;192.168.99.3/24 | vtnet0_vlan99; tag99, parent vtnet0; IP .2/.3 /24 | PASS đối chiếu cấu hình/runtime, không phải traffic test |

Cả mười VLAN interface tồn tại, UP/RUNNING/LOWER_UP, netmask0xffffff00, đúng tag/parent, không có alias VIP .1. SYNC vtnet2/opt6 UP và active: Primary10.255.255.1/30, Secondary10.255.255.2/30. Không thấy interface ngoài tập vtnet0–3, lo0, enc0, pflog0, pfsync0 và năm VLAN.

Đối chiếu toàn bộ block ifconfig với `group1b-prerequisites-20261103/{primary,secondary}-audit.json`: mọi block ngoài pfsync0 giống nguyên văn. pfsync0 trong bản audit đầu Nhóm1B là trước repair; hiện tại khác đúng phần đã được sửa native và khớp điều kiện ảnh ổn định Nhóm1B. Không dùng khác biệt này để quy cho Copilot tạo thay đổi mới. Kết quả máy đọc nằm trong comparison-results.json; full ifconfig và route nằm trong snapshot cùng TXT trích xuất.


![Hình 3.3. VLAN/IP hiện tại trên Primary.](../evidence/M3/post-copilot-runtime-audit-20261103/primary-vlan-proof-20261103T220834+0700.png)

**Hình 3.3. VLAN/IP hiện tại trên Primary.**

Mục đích: đọc nhanh IP và cờ interface. Nội dung: trích xuất ifconfig gồm năm VLAN và SYNC. Kết quả: đủ VLAN/IP riêng đúng phía, không thấy VIP .1 hoặc dòng vai trò CARP. Ý nghĩa: ảnh bổ trợ; kết luận ABSENT dựa full ifconfig đã nhận có checksum, không phụ thuộc duy nhất grep.


![Hình 3.4. VLAN/IP hiện tại trên Secondary.](../evidence/M3/post-copilot-runtime-audit-20261103/secondary-vlan-proof-20261103T220834+0700.png)

**Hình 3.4. VLAN/IP hiện tại trên Secondary.**

Mục đích: đọc nhanh IP và cờ interface. Nội dung: trích xuất ifconfig gồm năm VLAN và SYNC. Kết quả: đủ VLAN/IP riêng đúng phía, không thấy VIP .1 hoặc dòng vai trò CARP. Ý nghĩa: ảnh bổ trợ; kết luận ABSENT dựa full ifconfig đã nhận có checksum, không phụ thuộc duy nhất grep.

## 3.4. C. CARP PERSISTENT CONFIG

**Phân loại cả hai: NOT PRESENT. Tổng VIP nodes=0, CARP mode nodes=0; số CARP VIP=0, duplicate=0.** Không có bản ghi để gán trạng thái PRESENT BUT NOT APPLIED/PRESENT AND CONSISTENT/PRESENT BUT INVALID. Các trường actual interface/VHID/advbase/advskew đều N/A vì bản ghi không tồn tại, không tự điền thông số dự kiến làm thực tế.

| VLAN | VIP dự kiến đã duyệt | Primary | Secondary | Result |
|---|---|---|---|---|
| 30 |192.168.30.1/24 | NOT PRESENT | NOT PRESENT | PENDING triển khai; actual fields N/A |
| 40 |192.168.40.1/24 | NOT PRESENT | NOT PRESENT | PENDING triển khai; actual fields N/A |
| 50 |192.168.50.1/24 | NOT PRESENT | NOT PRESENT | PENDING triển khai; actual fields N/A |
| 60 |192.168.60.1/24 | NOT PRESENT | NOT PRESENT | PENDING triển khai; actual fields N/A |
| 99 |192.168.99.1/24 | NOT PRESENT | NOT PRESENT | PENDING triển khai; actual fields N/A |

Bộ tham số **đã duyệt nhưng chưa triển khai** từ CARP-final-parameters.json: opt1–opt5 tương ứng VLAN30/40/50/60/99; VHID tương ứng số VLAN; advbase1; advskew Primary0/Secondary100. Không thêm VIP vào SYNC/WAN/LAN parent trong lượt này. Không đọc/xuất shared secret.


![Hình 3.5. Số VIP và CARP mode trong config hiện tại của Primary.](../evidence/M3/post-copilot-runtime-audit-20261103/primary-persistent-vip-proof-verified-20261103T220925+0700.png)

**Hình 3.5. Số VIP và CARP mode trong config hiện tại của Primary.**

Mục đích: xác minh có ghi persistent CARP sau thử apply hay không. Nội dung: chỉ đếm vip node và mode=carp, không xuất XML/secret. Kết quả: cả hai bằng0. Ý nghĩa: kết hợp checksum nguyên byte backup để khẳng định NOT PRESENT; hai ảnh giống nhau là kết quả đếm giống nhau, metadata node được giữ riêng.


![Hình 3.6. Số VIP và CARP mode trong config hiện tại của Secondary.](../evidence/M3/post-copilot-runtime-audit-20261103/secondary-persistent-vip-proof-verified-20261103T220925+0700.png)

**Hình 3.6. Số VIP và CARP mode trong config hiện tại của Secondary.**

Mục đích: xác minh có ghi persistent CARP sau thử apply hay không. Nội dung: chỉ đếm vip node và mode=carp, không xuất XML/secret. Kết quả: cả hai bằng0. Ý nghĩa: kết hợp checksum nguyên byte backup để khẳng định NOT PRESENT; hai ảnh giống nhau là kết quả đếm giống nhau, metadata node được giữ riêng.

## 3.5. D. CARP RUNTIME

| VLAN | VIP kiểm tra | Primary | Secondary | Result |
|---|---|---|---|---|
|30|192.168.30.1|ABSENT|ABSENT|Không có VIP .1 và không có block CARP/VHID; chưa MASTER/BACKUP|
|40|192.168.40.1|ABSENT|ABSENT|Không có VIP .1 và không có block CARP/VHID; chưa MASTER/BACKUP|
|50|192.168.50.1|ABSENT|ABSENT|Không có VIP .1 và không có block CARP/VHID; chưa MASTER/BACKUP|
|60|192.168.60.1|ABSENT|ABSENT|Không có VIP .1 và không có block CARP/VHID; chưa MASTER/BACKUP|
|99|192.168.99.1|ABSENT|ABSENT|Không có VIP .1 và không có block CARP/VHID; chưa MASTER/BACKUP|

Phương pháp: đọc ifconfig -a đầy đủ, tách block từng interface, xét danh sách inet và dòng CARP/vhid; đối chiếu route và persistent config. Interface VLAN có tồn tại, vì vậy ABSENT là CARP/VIP không tồn tại, không phải VLAN mất. `carp.allow=1` nếu bật không thay thế bằng chứng có VIP. Không apply/reload để tạo runtime. Không có failover hoặc kiểm tra giữ phiên.

## 3.6. E. PFSYNC

| Máy | pfsync0 | syncdev / peer | syncok / demotion | Phân loại |
|---|---|---|---|---|
|Primary|UP/RUNNING/LOWER_UP|vtnet2 /10.255.255.2|1 /0|READY|
|Secondary|UP/RUNNING/LOWER_UP|vtnet2 /10.255.255.1|1 /0|READY|

**Overall: READY trong phạm vi runtime.** Version1400, maxupd128, defer off, giống mốc ổn định Nhóm1B. Kernel log đọc còn ghi bulk start rồi bulk done: Primary uptime8799→9229, Secondary2414→2419. Đây là dấu lịch sử từ boot, không tự gán thành sự kiện mới lúc audit.

Counter tích lũy: Primary nhận20/gửi19 IPv4; Secondary nhận18/gửi21. Có state inserts và bulk marks; send errors0, bad interface/TTL/version/HMAC/action0. **Mỗi phía có2 failed state lookup/inserts tích lũy**; chưa xác định thời điểm/nguyên nhân, không che giấu và không suy counter đó là lỗi mới do Copilot. UP/syncpeer/syncok/demotion hiện tại vẫn đạt điều kiện READY Nhóm1B. Bộ đếm không được lấy mẫu tốc độ, không chứng minh vừa có packet mới trong cửa sổ audit. Chưa nghiệm thu toàn bộ state table/giữ phiên/reboot/failover; không kết luận HA PASS.


![Hình 3.7. Pfsync và checksum hiện tại trên Primary.](../evidence/M3/post-copilot-runtime-audit-20261103/primary-pfsync-proof-20261103T220826+0700.png)

**Hình 3.7. Pfsync và checksum hiện tại trên Primary.**

Mục đích: đối chiếu pfsync sau chuỗi thử Copilot. Nội dung: pfsync0, peer, syncok, demotion và hash config. Kết quả: UP, đúng peer, syncok1, demotion0; hash khớp backup. Ý nghĩa: đạt READY runtime, không cần restart/backend repair trong lượt này.


![Hình 3.8. Pfsync và checksum hiện tại trên Secondary.](../evidence/M3/post-copilot-runtime-audit-20261103/secondary-pfsync-proof-20261103T220826+0700.png)

**Hình 3.8. Pfsync và checksum hiện tại trên Secondary.**

Mục đích: đối chiếu pfsync sau chuỗi thử Copilot. Nội dung: pfsync0, peer, syncok, demotion và hash config. Kết quả: UP, đúng peer, syncok1, demotion0; hash khớp backup. Ý nghĩa: đạt READY runtime, không cần restart/backend repair trong lượt này.

## 3.7. F. COPILOT SIDE EFFECTS VÀ SO SÁNH BACKUP

### 3.7.1. Persistent

**Không có delta persistent còn tồn tại trong /conf/config.xml.** Full byte equality và SHA-256 trùng backup Nhóm1B trên guest, đồng thời trùng backup đã kiểm ở Windows. Cấu hình cũng giữ nguyên trong khoảng trước/sau snapshot.

| Máy | SHA-256 current = backup guest = backup Windows |
|---|---|
|Primary|`2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2`|
|Secondary|`fd0482546117a18254e05114dc1b101012b95c1388e4ba9ea4eaafce115c69bd`|

Mọi top-level XML node hiện có đều so sánh bằng nhau: interfaces/vlans/virtualip/hasync/filter/nat/system và các nhánh còn lại, gồm OPNsense chứa model dịch vụ. DHCP nếu không có nhánh độc lập vẫn nằm trong phạm vi full-byte comparison; không tự coi DHCP server đã hoạt động. Không có thay đổi CARP hoặc ngoài CARP trong file cấu hình này. Không khẳng định mọi tệp khác trên filesystem guest bất biến vì không kiểm toàn ổ đĩa.

### 3.7.2. Runtime-only

Không thấy interface/VIP lạ, không thấy IP bị gán khác; các block VLAN/SYNC và interface khác khớp Nhóm1B. `/root/m3-vlan30.out` không tồn tại tại lúc đọc trên cả hai. Pfsync đang ở trạng thái đã đạt Nhóm1B, không phải side effect mới được quy cho Copilot. Không có runtime residual cần rollback đã được xác nhận.

### 3.7.3. Phân loại dấu vết A–D

| Nhóm | Kết luận có thể xác nhận | Giới hạn |
|---|---|---|
|A. Chỉ gõ nhưng chưa thực thi|Một số ảnh apply cũ chỉ dòng lệnh/dấu chờ, giữ là UNKNOWN về hoàn tất|Không tự kết luận cả chuỗi chưa hề chạy|
|B. Thực thi/được shell xử lý nhưng không tạo thay đổi cấu hình|Ảnh cũ/mới cho Command not found/redirect error; snapshot hiện tại không có delta|Không nói mọi câu lệnh trong mọi chuỗi lỗi đều chắc chắn không từng tác động runtime|
|C. Tạo runtime tạm|Không phát hiện thay đổi còn tồn tại trong interface/VIP được đọc|Không loại trừ thao tác thoáng qua đã tự mất/được hoàn nguyên trước audit|
|D. Tạo persistent|Không có delta còn tồn tại trong config.xml so với backup|Không kiểm mọi file ngoài config.xml; không có audit history đầy đủ để quy tác giả|

### 3.7.4. Console probe và lỗi thu thập

Lỗi HOSTNAME/WHOAMI/IFCONFIG cũ liên quan đường nhập, không chứng minh chương trình hệ điều hành bị mất. Một lần Caps Lock và thử đảo chữ/bỏ Shift chưa giải quyết đầy đủ. Collector riêng trên Windows sau đó dùng phím nền kèm Shift cho ký tự đặc biệt; chuỗi code quan trọng truyền bằng hex chữ thường và kiểm SHA-256 trước exec, tránh biến dạng chữ HOA trong tên module. Reader JSON được giải mã glyph chính xác và kiểm SHA-256 toàn payload.

Lần ảnh bổ sung persistent-vip-proof đầu bị `ModuleNotFoundError: xml.etree.elementtree` do ElementTree thành chữ thường; đây là **FAIL của phép thu ảnh**, không phải lỗi config/CARP. Ảnh lỗi được giữ nguyên; ảnh hậu tố persistent-vip-proof-verified dùng code hex cho kết quả0/0 hợp lệ. Xem collection-method.md và mọi command/metadata trong evidence. Không sửa collector gốc, không thay keyboard config guest; có một thao tác phím Caps Lock nhất thời được ghi metadata. Reader in-memory đã thoát về shell.

## 3.8. G. ROLLBACK REQUIRED?

**NO trong phạm vi cấu hình persistent và interface/CARP runtime được kiểm tra.** Chưa có đối tượng cụ thể cần rollback; không restore XML, không xóa VLAN/VIP và không restart pfsync. Không suy kết luận này thành chứng nhận mọi thao tác quá khứ hoặc mọi file guest chưa từng thay đổi.

M2 giữ kết quả nghiệm thu lịch sử, không chạy lại suite và không sửa Core. Core đang tắt là trạng thái đã bàn giao ở Nhóm1 để quản lý RAM, không tự kết luận hỏng M2 hoặc mất cấu hình.

## 3.9. H. NEXT ACTION

**4. MORE EVIDENCE REQUIRED.** Checkpoint firewall đã được xác nhận, không cần rollback/repair được chứng minh. Trước CARP apply cần phương án RAM được duyệt để có đường Layer2 qua Core, xác minh xung đột VIP/VHID và điều kiện nhận CARP trên từng VLAN ở topology hoạt động. Chưa đủ cơ sở ghi SAFE TO CONTINUE CARP theo nghĩa được áp ngay ở trạng thái Core tắt.

Bước tiếp theo đề xuất: lập đợt readiness có kiểm tài nguyên và quyền riêng nếu phải bật Core; đọc lại L2/VIP/VHID/rule CARP trước triển khai persistent bằng backend phù hợp. Chưa bật Core, chưa sửa tài nguyên, chưa apply/reload/failover. Không mở rộng WAN/LAN parent/NAT/DHCP/M4/M5.

## 3.10. Danh mục minh chứng và giải thích thuật ngữ

`evidence-index.csv` và `evidence-index.md` có tên/nội dung/thời điểm UTC+07:00/path/vị trí báo cáo/hash. Ảnh gốc không sửa nội dung; không có ảnh giả. Tệp command/code là đầu vào thu thập, không được trình bày như kết quả. Thời điểm snapshot derived ghi theo metadata snapshot-ready, thời điểm tạo tài liệu ghi rõ là mtime thay vì acquisition. Giữ mọi ảnh lỗi và minh chứng cũ nguyên vị trí; không cleanup.

CARP — Common Address Redundancy Protocol, giao thức dự phòng địa chỉ chung — dự kiến cho hai firewall dùng chung VIP (Virtual IP Address, địa chỉ IP ảo), quảng bá/bầu vai trò để dự phòng gateway SOC. Trong topology này VIP .1 và VHID (Virtual Host Identifier, định danh nhóm host ảo) đã được duyệt nhưng chưa tồn tại thực tế. Advbase/advskew là tham số nhịp/độ lệch quảng bá, không được suy từ kế hoạch thành runtime.

Pfsync là tên cơ chế đồng bộ trạng thái PF (Packet Filter, bộ lọc gói), phục vụ HA (High Availability, tính sẵn sàng cao). Đường SYNC riêng vtnet2 hiện có peer/syncok và bộ đếm, nhưng chưa chứng minh giữ kết nối khi chuyển vai. VLAN (Virtual Local Area Network, mạng LAN ảo) tách miền chuyển mạch; tag IEEE802.1Q/parent xác định các VLAN trên trunk vtnet0. Core L2 chuyển frame; gateway/firewall liên VLAN nằm trên OPNsense. OPNsense là tên sản phẩm, không tự khai triển.

SHA-256 (Secure Hash Algorithm 256-bit, hàm băm256 bit) dùng đối chiếu bytes config/payload; equality được kiểm thêm bằng so sánh trực tiếp trên guest, không chỉ dựa tên file. SSH (Secure Shell, truy cập shell bảo mật) dùng kênh hiện có tới EVE; QEMU là phần mềm ảo hóa đang chạy guest, VNC (Virtual Network Computing) cung cấp framebuffer/nhập phím. Các thuật ngữ SOC, trunk/access, OVS/bridge, LACP, SPAN/port mirroring, QCOW2, cloud-init/NoCloud, NAT/DHCP, IDS/IPS, Suricata, Wazuh được giải thích theo tên/nguyên lý/vai trò/ví dụ trong docs/TOPOLOGY_TERMS.md và báo cáo M1/M2; không phải đầu ra nghiệm thu mới của checkpoint này.

Nguồn kết luận là output cấu hình/runtime/log và backup nội bộ đã dẫn; không dùng trích dẫn ngoài mới thay bằng chứng. Báo cáo chuẩn bị nội dung đưa vào Word: nếu xuất dùng A4, Times New Roman12–13, lề trái3 cm/còn lại2 cm; hình đánh số và giải thích như trên. Chưa tạo Word trong lượt này.

**Dừng sau recovery checkpoint. Không thay cấu hình, không rollback, không tiếp tục CARP.**
