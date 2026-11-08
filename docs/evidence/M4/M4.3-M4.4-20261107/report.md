# 4. Báo cáo M4.3 và M4.4 — 07/11/2026, UTC+07:00

## 4.3. Kết nối Wazuh với OPNsense — PARTIAL / nghiệm thu BLOCKED

Máy thao tác bắt tay TCP/22 với Wazuh 192.168.220.146 thành công. EVE-NG 192.168.220.143 không phản hồi SSH ngoài sandbox và TCP/443 timeout. Đây là kiểm tra từ máy thao tác, không chứng minh đường OPNsense → Wazuh. Không lặp ping/HTTPS WAN hoặc kiểm thử M2–M3 đã PASS. Manager hoạt động và Wazuh ↔ EVE-NG PASS là thông tin người dùng xác nhận, chưa kiểm tra lại.

Chưa có phương thức xác thực Wazuh được xác nhận trong các tệp đã kiểm tra; không đoán tài khoản/mật khẩu. Chưa đọc được route, interface, listener và dịch vụ hai đầu. Phương án dự kiến: OPNsense chủ động gửi Syslog tới Wazuh, không cần mở HTTPS quản trị WAN. Chưa chốt nguồn, giao thức/cổng hoặc đường WAN/Management. Chỉ chọn đường policy hiện hữu cho phép; nếu phải sửa firewall rule, NAT, VLAN, HA hoặc mạng thì dừng BLOCKED.

## 4.4. Thu thập log — BLOCKED

Chưa cấu hình Syslog, chưa nhận log firewall thực tế; chưa xác minh nguồn, thời gian, múi giờ và nội dung. TCP/22 CONNECTED không chứng minh bộ thu Syslog hoạt động. Không tạo log giả hoặc lưu lượng tấn công, không sửa chính sách để kiểm thử.

Syslog là tên cơ chế/giao thức chuyển thông điệp nhật ký, không tự tạo dạng khai triển. Thiết bị gửi thông điệp nguồn/thời gian/nội dung tới bộ thu. Trong Security Operations Center (SOC, trung tâm điều hành an ninh), cơ chế này đưa sự kiện mạng vào giám sát. OPNsense và Wazuh là tên sản phẩm chính thức; ví dụ OPNsense → Wazuh ở đây mới là thiết kế dự kiến, chưa triển khai.

## 4.4.1. Bảo toàn và điều kiện tiếp tục

Không thay đổi hệ thống, cài phần mềm, restart dịch vụ/node, Core, CARP, pfsync, HA, NAT, VLAN hoặc firewall rule. Không cần rollback vì chưa chỉnh cấu hình. Không mở rộng M4.5/M5. Không có minh chứng guest hoặc ảnh mới; không kết luận PASS cho đường log.

Cần khôi phục đường quản trị EVE-NG/console OPNsense và có phương thức xác thực Wazuh được xác nhận. Trước chỉnh sửa: sao lưu config OPNsense và ossec.conf trên máy đích với quyền hạn chế, ghi vị trí/hash, không xuất bí mật. Rollback dự kiến: phục hồi đúng phần cấu hình log đã lưu và nạp lại dịch vụ liên quan; không phục hồi toàn firewall làm mất thay đổi khác.

Khi truy cập được: đọc mạng/dịch vụ và policy; chọn đường được phép; backup; cấu hình tối thiểu đích gửi và bộ thu; quan sát log firewall phát sinh tự nhiên. Nghiệm thu phải phân biệt nhận gói, ghi log và sinh alert; cần nguồn IP/hostname, thời gian có múi giờ và nội dung firewall thực tế tại phía nhận.

## 4.4.2. Minh chứng và hướng dẫn chụp

Không chụp được console do EVE-NG không truy cập được. Khi có truy cập, mở cấu hình đích Syslog OPNsense, trạng thái listener Wazuh và log nhận có nguồn/thời gian/nội dung. Chụp rõ toàn bộ kết quả, che bí mật và lưu ảnh gốc tại thư mục này. Dự kiến Hình 4.3: Đích gửi Syslog; Hình 4.4: Log firewall tại Wazuh. Chưa có hai ảnh này; khi có phải giải thích mục đích, nội dung, kết quả và ý nghĩa dưới hình.

| Kiểm tra | Kết quả | Minh chứng |
|---|---|---|
| Máy thao tác → Wazuh TCP/22 | PASS riêng bắt tay TCP | access-probes.json |
| EVE SSH/HTTPS | BLOCKED | transport-failure.txt; access-probes.json |
| OPNsense → Wazuh đường log | BLOCKED, chưa xác minh | Chưa có |
| Log firewall thực tế | BLOCKED, chưa kiểm thử | Chưa có |

## 4.4.3. Kiểm tra tiếp tục ngày 07/11/2026

SSH quản trị EVE-NG bằng khóa đã cấu hình đã hoạt động. EVE-NG vừa khởi động lúc 12:09:43 UTC và không có tiến trình QEMU; OPNsense Primary `192.168.220.144` đang tắt, ping từ EVE thất bại và neighbor `FAILED`. Đây là nguyên nhân trực tiếp khiến chưa thể xác minh OPNsense → Wazuh hoặc cấu hình Syslog.

Wazuh `192.168.220.146` vẫn hoạt động ngoài runtime QEMU của EVE: ping từ EVE đạt 2/2, SSH TCP/22 mở, MAC `00:0c:29:d0:c4:d8` thuộc VMware. TCP/514 trả `Connection refused`, chưa có listener Syslog TCP trên cổng này; kết quả không kết luận về UDP/514. Host key được thu qua EVE và ghim vào tệp riêng, không sửa known_hosts toàn cục. `soc-admin` với khóa EVE là phương thức từng được seed, nhưng Wazuh hiện từ chối khóa. Không thử mật khẩu hoặc tài khoản khác.

Trạng thái: **M4.3 PARTIAL/BLOCKED; M4.4 BLOCKED**. Chưa thay đổi nên chưa cần rollback. Để tiếp tục, quản trị viên cần: (1) bật riêng OPNsense Primary trong EVE-NG; không bật node Wazuh trong EVE khi `.146` đang tồn tại trên VMware để tránh trùng IP; (2) tại console VMware của Wazuh, khôi phục public key hiện hành `C:\Users\ACER\.ssh\eve-ng-root-ed25519.pub` cho `soc-admin`, đúng owner/quyền `.ssh` và `authorized_keys`, hoặc chỉ ra đường dẫn khóa hợp lệ đã cấu hình mà không chia sẻ khóa riêng. Sau đó mới sao lưu cấu hình, cấu hình Syslog tối thiểu và nghiệm thu log firewall tự nhiên.
