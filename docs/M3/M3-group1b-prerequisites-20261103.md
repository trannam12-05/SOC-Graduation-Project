# CHƯƠNG 3. M3 — NHÓM 1B: ĐIỀU KIỆN TRƯỚC KHI TẠO CARP VIP

## 3.1. Kết quả và phạm vi phê duyệt

Thời điểm tổng hợp: 2026-11-03T18:30:33.807929+07:00 (UTC+07:00). Năm VIP được phân loại **APPROVED trong phạm vi cấu hình đã kiểm tra**. Pfsync: **READY trong runtime hiện tại**, có cấu hình peer đúng và bằng chứng protocol240 hai chiều. Chưa tạo CARP VIP, chưa failover, không sửa M2, NAT/DHCP hoặc rule HA SYNC; không mở rộng sang WAN/LAN parent.

## 3.2. VIP/VHID: đối chiếu và bộ tham số cuối cùng

| VLAN | Interface hai phía | VIP | VHID | advbase | Advskew P/S | Kết quả |
|---|---|---|---|---|---|---|
| 30 | opt1 / vtnet0_vlan30 | 192.168.30.1/24 | 30 | 1 | 0 / 100 | APPROVED |
| 40 | opt2 / vtnet0_vlan40 | 192.168.40.1/24 | 40 | 1 | 0 / 100 | APPROVED |
| 50 | opt3 / vtnet0_vlan50 | 192.168.50.1/24 | 50 | 1 | 0 / 100 | APPROVED |
| 60 | opt4 / vtnet0_vlan60 | 192.168.60.1/24 | 60 | 1 | 0 / 100 | APPROVED |
| 99 | opt5 / vtnet0_vlan99 | 192.168.99.1/24 | 99 | 1 | 0 / 100 | APPROVED |


Primary giữ .2/24, Secondary giữ .3/24 trên từng VLAN. SYNC giữ nguyên **opt6/vtnet2**, Primary10.255.255.1/30, Secondary10.255.255.2/30. Các giá trị advbase1, advskew0/100 và VHID30/40/50/60/99 được chọn đúng quyền người dùng vừa cấp, không còn lấy ví dụ chưa duyệt của M1 làm cấu hình. Bảng chỉ là dữ liệu chuẩn bị, `applied=false`.

Phạm vi xác nhận xung đột: snapshot đầy đủ của hai firewall tại nhóm1B, runtime interface, cache ARP đọc thụ động; mười bản ghi cấu hình endpoint VPCS/seed đã lưu; và quy hoạch subnet. Không có tham chiếu gán năm IP đích trong XML hiện hành của hai firewall, không có VHID khác0, không thấy năm IP trong cache ARP hoặc các địa chỉ endpoint đã đối chiếu. VIP nằm trong đúng /24 và khác IP riêng .2/.3, network/broadcast. Năm VHID duy nhất, tương ứng mỗi VIP và phải giống nhau ở hai thành viên của cùng nhóm.

Core đang tắt theo quyền Nhóm1; đợt này không bật Core, không phát ARP probe hoặc thăm dò CARP trên các VLAN. **APPROVED không phải bảo đảm mọi thiết bị chưa khai báo hoặc đang tắt bên ngoài tập cấu hình đều không dùng IP/VHID.** Trước khi tạo VIP trong đợt được phép tiếp theo, cần đọc lại xung đột khi đường L2 phù hợp hoạt động. Không phát hiện CONFLICT để phải đổi địa chỉ; không thay bất kỳ địa chỉ nào.

## 3.3. Nguyên nhân pfsync và cách xử lý

Trước sửa: cả hai pfsync0 đều flags=0, không UP/syncdev/syncpeer. Cấu hình lưu vẫn có hasync.pfsyncinterface=opt6 và peer đúng phía đối diện. Mã cài `/usr/local/etc/inc/interfaces.inc` và đăng ký plugin cho thấy routine native áp những trường này để đưa pfsync0 lên, chọn syncdev/peer. Đây là trường hợp **cấu hình lưu chưa được áp vào runtime**, không có bằng chứng thiếu IP hoặc cần mở rộng rule HA SYNC. Không tự thêm trường enable hoặc sửa XML.

Đã thử configctl interface pfsync.configure; công cụ trả “Action not allowed or missing” dù exit code0. Runtime vẫn flags0 nên giữ kết quả đó là NOT READY, không coi exit code là thành công. Không sửa quyền configd hoặc restart dịch vụ khác. Sau khi đối chiếu action file thật, gọi trực tiếp backend mà action đó đăng ký: **/usr/local/sbin/pluginctl -c pfsync**, một lần trên mỗi firewall.

Sau backend native: cả hai pfsync0 có UP, syncdev vtnet2, syncpeer đúng .2 hoặc .1. **Không chốt READY tại thời điểm này:** ảnh đọc ngay sau áp còn syncok0; kiểm tra tiếp ghi nhận Primary vẫn demotion240 trong khi bulk chưa hoàn tất. Đã áp lại riêng backend native trên Primary khi Secondary đã ổn định, không đổi tham số, không ghi sysctl ép syncok/demotion. Ảnh ổn định cuối xác nhận hai phía syncok1 và demotion0; kernel log hai phía ghi “pfsync bulk done”, không phải “bulk fail”. Đây là điều kiện được dùng để chốt READY.

Cấu hình XML trước/sau khớp nguyên byte; các hash bảo vệ interfaces/filter/NAT/DHCP/hasync/virtualip/OPNsense giữ nguyên. Không thay rule HA SYNC, không thay IP10.255.255.1/30 hoặc10.255.255.2/30. Phiên bản pfsync mà backend áp từ cấu hình hiện hữu được giữ nguyên, không đổi phiên bản để dò lỗi.

Thu thụ động tại TAP SYNC Secondary trong cửa sổ áp backend ban đầu: protocol240 từ .1 sang .2 có 5 packet, từ .2 sang .1 có 8 packet. Chỉ nhận packet đúng cặp peer, không tạo HTTP/session thử hoặc failover. PCAP này không bao phủ lần áp lại Primary sau đó; bước hoàn tất bulk được chứng minh riêng bằng kernel log/ảnh syncok1/demotion0 cuối. Không chỉ dùng số gói hai chiều hoặc syncok1 đứng riêng để kết luận. `pfsync-control-decoded.json` giữ bản giải mã control packet; `settled-verification.json` ghi rõ phương pháp trích đọc ảnh gốc, không giả làm JSON native.

**Giới hạn READY:** đã sẵn sàng về device/peer và trao đổi protocol240 ở phiên hiện tại; chưa nghiệm thu giữ phiên/state table thực, chưa thử reboot hoặc failover. Mã có đường gọi routine pfsync liên quan cấu hình VIP/CARP và plugin riêng; khi chưa tạo CARP, không tự thêm hook khởi động để ép hành vi boot. Chưa khẳng định sửa runtime này đã được kiểm thử bền vững qua reboot. Không cần tạo một VIP giả để đưa pfsync lên.

## 3.4. Backup trước sửa và bảo toàn cấu hình

Backup mới trên hai guest: `/root/soc-m3-1b-primary-20261103/config.before.xml` và `/root/soc-m3-1b-secondary-20261103/config.before.xml`, thư mục0700 và tệp0600. Snapshot được tạo trước khi gọi bất kỳ backend áp pfsync nào.

Windows: `private-backups/Primary-before.xml`, `private-backups/Secondary-before.xml`. Các tệp local được nhân từ bản đầy đủ đã xác minh ở Nhóm1, **chỉ sau khi hash snapshot mới trên guest khớp chính xác**. Đây là tối ưu không truyền lại secret thừa, không báo nhầm lần tải mới: phương pháp và đường nguồn được ghi rõ trong `backup-before-manifest.json`.

| Firewall | SHA-256 backup trước sửa và cấu hình sau sửa |
|---|---|
| Primary | 2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2 |
| Secondary | fd0482546117a18254e05114dc1b101012b95c1388e4ba9ea4eaafce115c69bd |

`SHA256SUMS-before.txt` và manifest cung cấp đường dẫn/checksum. Toàn bộ thư mục private-backups được Git ignore và NTFS chỉ cấp quyền owner hiện hành; không đưa backup thô hoặc secret lên Git. Native repair không đổi file cấu hình nên Primary vẫn khớp snapshot M2. Các ảnh/log lịch sử M2 được giữ nguyên và không chạy lại suite đã PASS.

## 3.5. CARP password được chuẩn bị an toàn

Một secret ngẫu nhiên được tạo một lần bằng bộ sinh mật mã, lưu tại Windows dưới dạng DPAPI CurrentUser trong `private-backups/carp-shared-secret.dpapi`. Plaintext không được viết vào tệp Windows, lệnh shell, ảnh, report hoặc chat. Secret được mã hóa riêng theo RSA-OAEP-SHA256 public key của từng guest; chỉ decrypt vào tệp root-only0600.

Hai đường guest: `/root/soc-m3-1b-primary-20261103/carp-shared.secret` và `/root/soc-m3-1b-secondary-20261103/carp-shared.secret`. Thử thách HMAC riêng từng phía được kiểm với cùng secret gốc để xác nhận hai file nhận cùng giá trị; báo cáo chỉ lưu kết quả boolean, không lưu password hoặc fingerprint mật khẩu. Native pfsync repair được kiểm không đổi file secret. **Chưa ghi secret vào XML CARP, vì chưa tạo VIP.**

## 3.6. Hình minh chứng và thuật ngữ

Các ảnh `console-primary-audit/execute-audit-*.png` và phía Secondary ghi snapshot trước sửa; `console-primary-apply/` giữ kết quả lỗi dispatcher; `console-primary-repair/execute-repair-*.png` và phía Secondary ghi pfsync runtime sau backend đúng. JSON đọc qua glyph khớp chính xác và SHA-256 toàn payload, không dùng OCR đoán ký tự hoặc sửa ảnh.

![Primary đã ổn định](../evidence/M3/group1b-prerequisites-20261103/primary-pfsync-retry-stable-20261103T182701+0700.png)

**Hình 3.3. Primary pfsync đã ổn định sau áp lại tuần tự.**

Mục đích: kiểm tra sau khởi tạo bulk. Nội dung: UP, syncdev/peer, syncok1, demotion0 và hash. Kết quả: đúng tham số, không còn demotion do bulk pending. Ý nghĩa: kết hợp kernel bulk done để chốt READY thay vì chỉ dựa vào UP. Ảnh thu lúc18:27:03 UTC+07:00.

![Secondary đã ổn định](../evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-final-20261103T182701+0700.png)

**Hình 3.4. Secondary pfsync đã ổn định.**

Mục đích: xác nhận phía peer. Nội dung: syncpeer .1, syncok1, demotion0 và hash không đổi. Kết quả: cùng sẵn sàng trong phiên hiện tại. Ý nghĩa: không suy tình trạng Secondary từ riêng Primary. Ảnh thu lúc18:27:10 UTC+07:00. Hai ảnh kernel bulk done tương ứng được lưu cùng evidence index; các ảnh trung gian syncok0 vẫn giữ nguyên.

CARP — Common Address Redundancy Protocol, giao thức dự phòng địa chỉ chung — dùng VIP (Virtual IP Address, IP ảo) và VHID (Virtual Host Identifier, định danh nhóm host ảo) để bầu chọn thành viên. Advbase là khoảng cơ sở; advskew là độ lệch quảng bá để thể hiện ưu tiên. Trong SOC, mục tiêu là dự phòng gateway; tại đợt này các tham số mới được chốt, chưa có bầu chọn.

Pfsync là tên giao thức đồng bộ trạng thái PF (Packet Filter, bộ lọc gói); dùng IP protocol240, không phải TCP/UDP port240. Runtime đúng và gói hai chiều hỗ trợ mục tiêu HA (High Availability, sẵn sàng cao), chưa thay cho nghiệm thu giữ phiên. SYNC là tên đường riêng của dự án; opt6 là assignment, vtnet2 là device. HMAC — Hash-based Message Authentication Code, mã xác thực thông điệp có khóa — dùng làm kiểm chứng bí mật mà không công khai bí mật. DPAPI — Windows Data Protection API — bảo vệ bản lưu theo tài khoản Windows hiện hành. Ví dụ đã kiểm là peer SYNC và secret staged; CARP/failover vẫn chưa áp dụng.

Nguồn chính thức đối chiếu nguyên lý/backend: [OPNsense core26.7 interfaces.inc](https://raw.githubusercontent.com/opnsense/core/26.7/src/etc/inc/interfaces.inc), [actions_interface.conf](https://raw.githubusercontent.com/opnsense/core/26.7/src/opnsense/service/conf/actions.d/actions_interface.conf). Quyết định thao tác ưu tiên mã **cài thực tế** đã đọc, vì số dòng/version có thể khác bản tag trên web; không lấy ví dụ bên ngoài thay giá trị người dùng duyệt.

## 3.7. Bàn giao và điểm dừng

VIP năm VLAN APPROVED trong phạm vi kiểm tra; pfsync READY ở runtime hiện tại. Bộ tham số cuối là `CARP-final-parameters.csv/json`, chưa áp vào thiết bị. Primary/Secondary giữ chạy; Core/endpoint khác vẫn tắt. Không đổi VLAN/access/trunk/OVS, NAT/DHCP hoặc HA SYNC rules; không mở rộng WAN/LAN parent.

Đã lưu `result.json`, backup/checksum, metadata capture, PCAP, audit/repair JSON, ảnh và `evidence-index.csv` có tên/nội dung/thời điểm UTC+07:00/đường dẫn/vị trí báo cáo/hash. Timestamp guest/PCAP được ghi riêng, không suy thành đồng hồ chuẩn của máy thu. **Dừng trước khi tạo CARP VIP và chờ người dùng xác nhận.**
