# 3.14. Phương án chuyển WAN sang pnet0 có guard/rollback — chưa được phép thực thi

## 3.14.1. Phạm vi
Chỉ hai WAN vtnet1; không HA/CARP/pfsync/hook, không trunk/Core, không VPCS hoặc WAN2. Employee-Linux mới được duyệt riêng không cấp quyền đổi WAN. Không tự thực hiện kế hoạch dưới đây.

## 3.14.2. Guard trước thay đổi
Đọc lại topology và QEMU PID/UUID/cmdline, không dùng node ID cũ như hằng số. Đối chiếu đúng tên Primary/Secondary, vtnet1→network4 và TAP tương ứng, master bridge thực tế; ghi nhận mọi interface khác. Xác minh pnet0 IP192.168.220.143/24 và route qua192.168.220.2 cùng SSH quản trị hiện hành. Lấy lock triển khai để tránh hai tiến trình cùng sửa, đồng thời dùng so sánh hash topology ngay trước commit để phát hiện thay đổi ngoài lock. Nếu mismatch hoặc endpoint không đúng, dừng.

Backup root-only topology/config hai máy và manifest bridge membership/IP/route/PID; SHA-256 khớp trước mutation. Đọc trạng thái HA làm guard, không chạy failover hoặc các test PASS. Xác nhận tài nguyên và đúng IP/MAC Employee-Linux từ lease/readiness mới, không reuse lease VPCS.

## 3.14.3. Giao dịch đề xuất sau phê duyệt riêng
Tạo đúng một network pnet0 trong metadata, giữ nguyên bridge WAN-ISP-1 cũ. Chuẩn bị XML tạm chỉ sửa network_id của hai WAN; xác minh mọi node/interface khác và VPCS giữ nguyên. Chuyển runtime đúng hai TAP WAN bằng cơ chế live được đánh giá/duyệt; cập nhật metadata đồng nhất có kiểm tra hash, không chỉ sửa API metadata rồi báo thành công. Không bridge cả vnet0_4 vào pnet0, không chuyển eth0 quản trị hoặc TAP Core/SYNC; không sửa host IP/route/iptables. Nếu live reattach không được xác nhận phù hợp trên bản EVE này hoặc yêu cầu stop/restart, dừng xin duyệt bảo trì riêng.

Đặt watchdog root-only trước mutation để tự hoàn tác đúng TAP/metadata nếu tiến trình mất kết nối hoặc chưa được disarm sau thời hạn đã duyệt. Đề xuất timeout180giây kể từ đổi link; cần chốt theo hành vi DHCP thực tế, không tự reboot/renew toàn interface vì chờ timeout. Yêu cầu hai lease WAN riêng trong subnet được duyệt, default route đúng và không sai lệch HA trước bước NAT. Quan sát bảo toàn network quản trị bằng so sánh IP/route và kết nối SSH read-only; kiểm tra không chứng minh zero packet loss.

## 3.14.4. Rollback chính xác
Lưu danh sách thay đổi và before/after hash từng bước. Nếu lỗi, trả từng WAN TAP về master ban đầu, rồi hoàn tác đúng hai liên kết và network metadata mới nếu không có chỉnh sửa cạnh tranh. Không ghi đè toàn lab khi hash không khớp after-hash của chính giao dịch; khi đó giữ log và dừng can thiệp tự động ngoài phần chắc chắn sở hữu. Giữ network cũ, không xóa node/image/Employee/VPCS/evidence.

Nếu NAT/rule mới đã được áp dụng trong giai đoạn được duyệt sau, gỡ theo UUID/description của đúng đợt và phục hồi mode trước đó; không restore toàn config đè các thay đổi hợp lệ khác. Không reset demotion hoặc restart HA. Watchdog chỉ disarm sau khi metadata/runtime đồng nhất, quản trị và guardHA phù hợp. Chưa có thao tác watchdog hoặc chuyển WAN trong lượt tạo Employee.

## 3.14.5. Điều kiện nghiệm thu kế tiếp
Đích1.1.1.1 TCP443 đã được duyệt, nhưng HTTPS chỉ chạy sau phê duyệt/triển khai WAN riêng và NAT đúng nguồn Employee-Linux đã xác minh. Không thử Internet trong đợt này; giữ PASS lịch sử. Không tự đặt WAN IP/VIP. NAT dùng WAN address riêng không chứng minh NAT HA giữ phiên.
