# CHƯƠNG 3. M3 — NHÓM 1: BACKUP VÀ ĐỐI CHIẾU KẾ HOẠCH CARP

## 3.1. Kết quả và giới hạn

Thời điểm tổng hợp: 2026-11-03T17:58:40.488965+07:00, UTC+07:00. Primary và Secondary cùng chạy OPNsense 26.7 (amd64), boot từ ổ cứng và có shell hợp lệ để đọc cấu hình. Đã tạo backup mới của cả hai trong guest, truyền dưới dạng mã hóa, giải mã tại thư mục riêng trên Windows và đối chiếu nguyên byte bằng SHA-256. Không áp dụng CARP, không failover, không sửa firewall/NAT/DHCP, Core hoặc các rule HA SYNC.

**Cả hai sẵn sàng cho việc đọc/đối chiếu và đã có backup; chưa sẵn sàng áp dụng hoặc nghiệm thu CARP.** Chưa có CARP VIP nào trong các nhánh cấu hình đã duyệt bằng bản backup đầy đủ và runtime chưa được dùng để chứng minh vai trò MASTER/BACKUP. VIP/VHID/advskew chưa được phê duyệt. Không coi net.inet.carp.allow bật hoặc dòng “CARP event system: OK” lúc boot là VIP đã hoạt động.

## 3.2. Quản lý RAM và trạng thái node

Trước đợt: Primary3072 MiB + Core2048 MiB chạy. Nếu bật Secondary3072 MiB sẽ thành8192 MiB, vượt tổng EVE khoảng7898 MiB. Người dùng đã cấp riêng quyền tắt mềm Core trong câu trả lời cho câu hỏi tài nguyên; đã gửi poweroff từ root shell và kiểm tra Core QEMU dừng trước khi start Secondary. Không sửa OVS, VLAN, trunk hoặc nội dung cấu hình M2.

Chỉ hai firewall chạy, tổng6144 MiB. `start-secondary.json` ghi guard RAM/start receipt; `inventory-both-running.json` ghi EVE còn khoảng3339 MiB available, swap0 tại mốc thu. Các endpoint M2 đã tắt từ trước; không bật Wazuh, Suricata hoặc node khác. Primary giữ hoạt động, không reboot. Kiểm kê cuối nằm trong `inventory-final.json`.

Core đang tắt để bảo đảm RAM, nên đường L2 giữa trunk Primary/Secondary qua Core chưa vận hành trong nhóm này. SYNC vtnet2 vẫn là segment riêng giữa hai firewall. Không suy boot hai firewall thành CARP đã có kênh bầu chọn trên năm VLAN; trước một đợt CARP tương lai cần phương án RAM/Layer2 phù hợp được duyệt, không tự thay Core hoặc hạ RAM firewall trong nhóm này.

## 3.3. Bảng CARP dự kiến đối chiếu thực tế

| Interface hai phía | VLAN | Primary IP | Secondary IP | VIP ví dụ M1 — chưa duyệt | Subnet/prefix | VHID | Advskew P/S | SYNC |
|---|---|---|---|---|---|---|---|---|
| opt1 / vtnet0_vlan30 | 30 | 192.168.30.2 | 192.168.30.3 | 192.168.30.1 | 192.168.30.0/24 | Chưa được chốt | Chưa chốt / Chưa chốt | opt6/vtnet2 (*) |
| opt2 / vtnet0_vlan40 | 40 | 192.168.40.2 | 192.168.40.3 | 192.168.40.1 | 192.168.40.0/24 | Chưa được chốt | Chưa chốt / Chưa chốt | opt6/vtnet2 (*) |
| opt3 / vtnet0_vlan50 | 50 | 192.168.50.2 | 192.168.50.3 | 192.168.50.1 | 192.168.50.0/24 | Chưa được chốt | Chưa chốt / Chưa chốt | opt6/vtnet2 (*) |
| opt4 / vtnet0_vlan60 | 60 | 192.168.60.2 | 192.168.60.3 | 192.168.60.1 | 192.168.60.0/24 | Chưa được chốt | Chưa chốt / Chưa chốt | opt6/vtnet2 (*) |
| opt5 / vtnet0_vlan99 | 99 | 192.168.99.2 | 192.168.99.3 | 192.168.99.1 | 192.168.99.0/24 | Chưa được chốt | Chưa chốt / Chưa chốt | opt6/vtnet2 (*) |


(*) SYNC chung cho mọi dòng: Primary **opt6/vtnet2 10.255.255.1/30**, Secondary **opt6/vtnet2 10.255.255.2/30**. Đây là địa chỉ riêng đồng bộ, không đề xuất thêm CARP VIP lên đường SYNC. Tên assignment/device của hai phía khớp nhau trong bản đọc mới.

IP riêng Primary .2/24 và Secondary .3/24 là cấu hình thực tế đã đọc lại. Các VIP .1 được lấy nguyên từ tài liệu M1 và `configs/M3/address-proposal.json` (status PROPOSED_NOT_CONFIRMED_NOT_APPLIED, confirmed=false); **không phải VIP được người dùng phê duyệt hoặc đã kiểm tra không trùng**. Không tự tạo VIP/VHID hay nhập advskew mặc định/giá trị trong ví dụ tài liệu bên ngoài. Advbase cũng chưa được chốt; CSV lưu đầy đủ từng trường advskew hai phía, advbase và SYNC.

## 3.4. Mạng/interface ngoài năm VLAN cần làm rõ phạm vi HA

| Mạng/interface | Hiện trạng đã đọc | Kế hoạch CARP |
|---|---|---|
| LAN parent / vtnet0 | Primary192.168.1.1/24, Secondary192.168.1.2/24 trong hồ sơ và bản đọc mới | Chưa xác nhận có yêu cầu HA cho LAN parent; chưa có VIP/VHID/advskew được chốt. Không dùng lại .1 làm VIP vì Primary đang sở hữu địa chỉ đó |
| WAN / vtnet1 | Cấu hình DHCP; địa chỉ/gateway upstream và VIP WAN chưa được tài liệu chốt | Không đề xuất VIP/VHID số cụ thể, không thay NAT/DHCP |
| NIC WAN bổ sung vtnet3 | Có trong topology nhưng không tự suy thành interface HA đã được gán | Phạm vi/interface/IP/VIP cần xác nhận nếu muốn sử dụng |
| SYNC / opt6/vtnet2 | .1/.2 của mạng10.255.255.0/30 | Đường đồng bộ riêng; không đưa vào danh sách tạo CARP VIP |

Đợt này không có lease/gateway WAN nào được nâng thành quy hoạch được phê duyệt. Runtime ifconfig đầy đủ không nhạy cảm được lưu trong hai audit JSON, không phát DHCP renew hoặc phép thử mạng riêng.

## 3.5. Thông số đã xác nhận và phần còn thiếu

Đã xác nhận bằng dữ liệu mới: phiên bản hai firewall giống nhau, assignment opt1–opt5 và device VLAN khớp, năm subnet/prefix24, các IP riêng .2/.3, SYNC opt6/vtnet2 với .1/.2 /30. Tài liệu xác nhận **kiến trúc** CARP dùng VIP gateway, SYNC riêng, Core chỉ Layer2; không đồng nghĩa xác nhận các VIP ví dụ. Cấu hình pfsync/XMLRPC được đọc chọn lọc, không xuất thông tin xác thực hoặc thay cấu hình.

Các mục thiếu trước khi có thể áp dụng CARP trong nhóm sau:

1. Duyệt VIP cụ thể của từng VLAN, và xác nhận không trùng với thiết bị khác; .1 hiện chỉ là ví dụ M1.
2. Chốt VHID cho từng nhóm VIP, bảo đảm phù hợp miền L2 và không xung đột; chưa tìm thấy VHID số được duyệt trong tài liệu M1/M3.
3. Chốt advskew Primary/Secondary, advbase và ý định ưu tiên/khôi phục vai trò. Không lấy giá trị ví dụ trong hướng dẫn làm cấu hình đồ án.
4. Cách thiết lập secret CARP chung qua kênh riêng nếu cần khi cấu hình; không yêu cầu gửi password vào chat hoặc ghi vào báo cáo/Git.
5. Chốt có HA trên LAN parent/WAN không; WAN còn thiếu upstream/subnet/IP/gateway/VIP. Không tự mở rộng phạm vi sang NAT/DHCP.
6. Bảo đảm Layer2 giữa interface chứa VIP và phương án tài nguyên khi cần Core cùng hai firewall. Khả năng trao đổi CARP protocol112 và xung đột VIP/VHID chưa được thử trong nhóm chỉ đọc; không tự thêm rule hoặc phát packet để xác minh.

**Vấn đề runtime mới cần ghi nhận:** `ifconfig -a` trên cả hai firewall sau boot ghi `pfsync0: flags=0`, không có cờ UP, không có syncdev/syncpeer. Trong cấu hình, Primary vẫn chọn opt6/peer10.255.255.2 và Secondary chọn opt6/peer10.255.255.1. Không dùng `syncok: 1` đứng riêng để kết luận đồng bộ state đang hoạt động. Chưa xác định nguyên nhân khác biệt cấu hình/runtime; không sửa, restart pfsync hoặc bổ sung trường cấu hình trong Nhóm1. Điều này cần được xem xét trước nghiệm thu đồng bộ phiên HA; không tự kết luận CARP bầu chọn phụ thuộc pfsync.

Pfsync từng có bằng chứng gói hai chiều; chưa đánh đồng bằng chứng đó với nghiệm thu giữ phiên hoặc khẳng định nó đang chạy ở mốc mới. XMLRPC từng có bằng chứng thêm/xóa alias thử trên Secondary. Không cấu hình hoặc kiểm thử lại hai chức năng trong nhóm này; các audit mới chỉ phản ánh cấu hình hiện có, không tạo thêm một kết luận HA runtime PASS.

## 3.6. Backup đầy đủ và checksum

Thư mục riêng trên Windows: `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/`, NTFS bỏ quyền kế thừa và chỉ cấp quyền cho owner hiện hành; toàn bộ thư mục bị Git ignore. Không chỉ đổi tên tệp để che secret. Khi truyền console chỉ có mã reader không chứa xác thực, public key và ciphertext; trước khi chấp nhận backup đã kiểm hash payload, giải mã, giải nén, kiểm kích thước/hash plaintext và parse XML.

| Firewall | Backup tại Windows | SHA-256 |
|---|---|---|
| Primary | private-backups/Primary-config.xml | 2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2 |
| Secondary | private-backups/Secondary-config.xml | fd0482546117a18254e05114dc1b101012b95c1388e4ba9ea4eaafce115c69bd |

Checksum công khai: `backup-SHA256SUMS.txt`; manifest: `backup-manifest.json`. Bản backup tương ứng trong guest: `/root/soc-m3-group1-primary-20261103/config.xml` và `/root/soc-m3-group1-secondary-20261103/config.xml`, root-only thư mục0700/tệp0600. Public audit chỉ chứa metadata, IP/interface và thông số HA cho phép xuất, không có mật khẩu/hash đăng nhập/private key/API key/CARP secret.

Mỗi firewall có hash config trước/sau đọc bằng hash backup tại guest và Windows. Primary còn khớp nguyên hash snapshot M2; không thay các cấu hình M2. File private vận chuyển như key hoặc dữ liệu nén vẫn nằm trong thư mục riêng; không đưa chúng vào báo cáo hoặc Git. Không commit/push. Bản XML đầy đủ chỉ dùng phục hồi riêng, không công khai nội dung.

## 3.7. Thuật ngữ áp dụng

CARP — Common Address Redundancy Protocol, giao thức dự phòng địa chỉ chung — giúp hai firewall chia sẻ VIP (Virtual IP Address, địa chỉ IP ảo). VHID — Virtual Host Identifier, định danh nhóm host ảo — nhận diện nhóm bầu chọn. Advskew là tham số lệch thời gian quảng bá; mức thấp hơn có ưu tiên cao hơn theo cơ chế CARP. Advbase là thời gian cơ sở của chu kỳ quảng bá. CARP dùng IP protocol112, khác TCP/UDP port112. Trong SOC, các cơ chế này dự kiến duy trì gateway khi một firewall lỗi; trong topology này năm VLAN mới có IP riêng, VIP/VHID/advskew còn chưa chốt, chưa nghiệm thu dự phòng.

HA — High Availability, tính sẵn sàng cao — là mục tiêu dự phòng, không phải trạng thái chỉ vì hai VM chạy. Pfsync là tên giao thức đồng bộ trạng thái PF; XMLRPC là cơ chế đồng bộ cấu hình hiện có của OPNsense. OPNsense là tên sản phẩm, không tự khai triển. SYNC là tên đường đồng bộ của dự án, không tự coi là VIP. Vai trò và các thuật ngữ SOC/VLAN/802.1Q/trunk/OVS/QEMU/SSH/NAT/DHCP dùng `docs/TOPOLOGY_TERMS.md` cùng trạng thái của báo cáo này; nhóm này không thay cấu hình các thành phần đó.

Cơ sở nguyên lý: [OPNsense — Configure CARP](https://docs.opnsense.org/manual/how-tos/carp.html), đối chiếu ngày03/11/2026. Hướng dẫn chính thức yêu cầu assignment phù hợp và khả năng nhận CARP trên interface; các ví dụ địa chỉ/VHID/skew của hướng dẫn không phải dữ liệu được chốt cho đồ án. Không làm theo các bước NAT/DHCP/reboot trong hướng dẫn vì ngoài quyền Nhóm1.

## 3.8. Hình và giới hạn thu thập

![Backup Primary](../evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/backup-execute-20261103T174724+0700.png)

**Hình 3.1. Tạo backup mới trên Primary trước kế hoạch CARP.**

Mục đích: xác nhận snapshot mới. Nội dung: M3_BACKUP_READY, hash, config unchanged và VIP_count. Kết quả: backup guest có trước khi chuyển mã hóa; checksum Windows được kiểm riêng trong audit. Ý nghĩa: không dùng backup M2 cũ thay snapshot mới. Ảnh toàn màn hình, không sửa nội dung kỹ thuật; thời điểm thu có trong JSON cùng tên.

![Backup Secondary](../evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/backup-execute-20261103T174741+0700.png)

**Hình 3.2. Tạo backup mới trên Secondary.**

Mục đích: xác nhận snapshot phía dự phòng. Nội dung: cùng bộ metadata không nhạy cảm cho Secondary. Kết quả: có backup mới, cấu hình không đổi. Ý nghĩa: hai phía có mốc phục hồi trước mọi thay đổi CARP tương lai; không phải ảnh MASTER/BACKUP.

Mốc thu dùng máy thu UTC+07:00; giờ guest có thể lệch. Các ảnh boot/shell và trang mã hóa được giữ trong thư mục minh chứng. Lần thử truyền bàn phím nhanh đầu tiên bị mất ký tự; kiểm hash/chạy reader bị chặn trước khi tạo backup, giữ ảnh lỗi, sau đó dùng nhịp console đã kiểm chứng. Primary stdout QEMU là pipe, không phải serial.log đọc được; vì vậy chuyển backup bằng trang glyph đã xác minh, không đổi xác thực/console/serial config hoặc tạo kết nối mạng mới. Không sửa ảnh để che lỗi truyền.

## 3.9. Trạng thái bàn giao

Ba việc Nhóm1 hoàn tất khi hai backup đã được xác minh và bảng đối chiếu được lưu. Primary + Secondary giữ chạy; Core tắt mềm theo quyền riêng; endpoint khác giữ tắt. **Không cấu hình CARP, không failover, không sửa rule HA SYNC, NAT/DHCP hoặc M2.** VIP/VHID/advskew vẫn chờ xác nhận. Không tự chuyển Nhóm2.

Danh mục `evidence-index.csv` có tên tệp, nội dung, thời điểm kèm múi giờ, đường dẫn, vị trí báo cáo và checksum. Private backup chỉ được liệt kê metadata/hash; không nhúng nội dung vào ảnh/báo cáo. Báo cáo này chuẩn bị nội dung học thuật cho Word; nếu xuất cần A4, Times New Roman12–13, lề trái3 cm/còn lại2 cm và chú thích dưới hình.
