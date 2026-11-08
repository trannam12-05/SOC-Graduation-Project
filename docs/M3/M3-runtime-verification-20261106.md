# 3.7. Nghiệm thu bổ sung cấu hình và runtime M3

## 3.7.1. Phạm vi và phương pháp
Ngày 06/11/2026 (UTC+07:00), sử dụng PowerShell/OpenSSH và Python 3.10.12 có sẵn trên EVE-NG để thay transport Python cục bộ không hoạt động. Không cài phần mềm, sửa cấu hình, đổi topology, VLAN/IP, Core hoặc vòng đời node; không gọi reload, restart hay failover. Chỉ ghi tệp dữ liệu tạm phục vụ truyền console. Không có thay đổi cấu hình nên không phát sinh bước sao lưu mới; backup M3.6 đã có được giữ nguyên.

Dữ liệu được đọc trực tiếp từ config.xml trong guest, chỉ xuất tám rule SOC M35 và ba pool DHCP không chứa bí mật. Đối chiếu toàn bộ cây XML đã chuẩn hóa: tag, thuộc tính gồm UUID, nội dung và mọi trường con theo thứ tự. Dữ liệu qua console được kiểm tra SHA-256 trước giải mã. Các phép thử luồng truy cập/DHCP M3.5 đã PASS được tái sử dụng, không chạy lại.

## 3.7.2. Kết quả
| Hạng mục | Trạng thái | Minh chứng và giới hạn |
|---|---|---|
| Transport | PASS | PowerShell SSH và Python trên EVE hoạt động; không phụ thuộc Python cục bộ |
| XMLRPC config sync | PASS trong phạm vi yêu cầu | Tám rule và ba pool trùng toàn bộ thuộc tính; syncitems gồm aliases,rules,kea,dnsforwarder; kết hợp log XMLRPC HTTP200/restore true đã có tại M3.6-completion-20261106/m36-xmlrpc-sync-sanitized.json. Không gửi lại sync hoặc alias thử |
| Firewall runtime | PASS | 8/8 UUID xuất hiện trong pfctl -sr trên mỗi máy; rules-runtime.csv ghi từng rule |
| DHCP runtime | PASS về tiến trình | Kea DHCPv4 và control agent chạy trên cả hai; không suy thành đã nghiệm thu lease synchronization hoặc DHCP failover |
| HA runtime cuối | PASS tại thời điểm chụp | Primary MASTER, Secondary BACKUP đủ VHID30/40/50/60/99; pfsync UP/RUNNING, syncok1 hai phía |
| NAT Internet | BLOCKED | WAN vtnet1 không có IPv4, không có IPv4 default route; pfctl -sn chỉ có no nat/no rdr, không có outbound NAT dịch địa chỉ. Không thử Internet hoặc đổi mạng |

XMLRPC là cơ chế gọi thủ tục từ xa qua XML, được OPNsense dùng chuyển các nhóm cấu hình đã chọn từ Primary sang Secondary. Trong SOC, nó giúp hai firewall duy trì chính sách thống nhất. Ví dụ đã kiểm chứng ở đây là tám rule M3.5 và ba pool DHCP, không chỉ alias thử. Giải thích thuật ngữ DHCP và chính sách đã nằm trong báo cáo M3.5; CARP/pfsync và kiến trúc HA giữ theo hồ sơ M3 trước.

## 3.7.3. Sai lệch đã quan sát và việc còn lại
Bản thu 19:30–19:36 ghi nhận cả hai BACKUP, Primary syncok0. Ảnh kiểm tra cuối ghi nhận MASTER/BACKUP và syncok1 đúng; không có thao tác phục hồi do công cụ này thực hiện. Chưa xác minh nguyên nhân chuyển trạng thái, không kết luận HA ổn định liên tục hoặc không mất gói. Giữ nguyên cả hai bộ bằng chứng và các nghiệm thu PASS lịch sử.

M3 tổng thể PARTIAL vì NAT Internet BLOCKED. Các mục được yêu cầu về cấu hình XMLRPC và đọc runtime đã kiểm chứng; DHCP HA/failover không được kiểm thử lại. Nếu cần nghiệm thu ổn định dài hạn hoặc tìm nguyên nhân sai lệch HA, cần phạm vi riêng, ưu tiên log chỉ đọc; không tự thay hệ thống. Không chuyển M4/M5.

## 3.7.4. Hình và danh mục minh chứng
Thư mục: docs/evidence/M3/M3-runtime-review-20261106/. Xem acceptance.json, results-20261106T193630+0700.json, rules-runtime.csv và evidence-index.csv.

Hình 3.7. Primary: OPNsense-Primary-status-20261106T194814+0700.png.
Mục đích: xác nhận runtime cuối. Nội dung: năm CARP MASTER, pfsync syncok1 và Kea chạy. Ý nghĩa: Primary sẵn vai trò chủ tại thời điểm chụp, không chứng minh tính liên tục suốt quá trình.

Hình 3.8. Secondary: OPNsense-Secondary-status-20261106T194814+0700.png.
Mục đích: xác nhận phía dự phòng. Nội dung: năm CARP BACKUP, pfsync syncok1 và Kea chạy. Ý nghĩa: phù hợp cặp HA ở thời điểm chụp; không thay thế phép thử failover.

Ảnh before/execute/header/page là framebuffer VNC thật, không sửa nội dung. Trang header/page chứa dữ liệu mã hóa để truyền kết quả, cần đọc kèm JSON đã kiểm tra checksum. Thời gian tên ảnh là thời điểm lưu cả batch ở máy thu UTC+07:00; không phải thời điểm chính xác từng lệnh. Batch chính thu khoảng 19:30–19:36; batch trạng thái lưu 19:48.

Đính chính theo mục 3.8: snapshot BACKUP được thu tuần tự, không chứng minh đồng thời hai BACKUP. Log xác nhận Primary demotion do pfsync bulk và lấy lại MASTER sau bulk done. Xem M3-ha-wan-final-review-20261106.md; dữ liệu gốc giữ nguyên.
