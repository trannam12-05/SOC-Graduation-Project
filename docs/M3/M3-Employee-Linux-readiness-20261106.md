# 3.15. Employee Linux — cấu hình và readiness đã kiểm chứng

## 3.15.1. Thực hiện theo phê duyệt
Ngày06/11/2026 UTC+07:00, đã tạo/bật node11 Employee-Linux,1vCPU/1024MiB, một NIC nối network7 VLAN40-Employee. Giữ nguyên VPCS Employee node5, không bật/thay VPCS. Đã sao lưu topology trước thay đổi: /root/soc-employee-linux-20261106T210505Z/lab-before.unl. Base linux-ubuntu-24.04-ovs được kiểm tra offline read-only: thư mục netplan không có cấu hình cũ, có curl/CA. Image node mới linux-soc-employee-20261106 là overlay riêng trên base sẵn có, seed NoCloud riêng; không sửa backing/image hoặc seed của node khác. Không cài gói, update/upgrade hoặc truy cập Internet.

NoCloud là nguồn metadata/user-data cục bộ cho cloud-init; trong node mới nó đặt hostname/identity mới và NIC employee0 khớp MAC nhận DHCP. Không tự cấp IP/gateway. Overlay QCOW2 giữ các ghi mới riêng, base phải được giữ nguyên. Console soc-admin autologin chỉ dùng cho console EVE được kiểm soát; SSH password bị khóa, không tạo mật khẩu/token trong báo cáo.

## 3.15.2. Kết quả PASS trong phạm vi local readiness
| Nội dung | Kết quả và bằng chứng |
|---|---|
| DHCP IPv4 | 192.168.40.110/24, dynamic trên employee0; readiness.json |
| Gateway | 192.168.40.1 qua DHCP; không dùng IP vật lý firewall |
| HTTPS client | curl8.5.0 có protocol https/SSL; Python ssl OpenSSL3.0.13; CA bundle tồn tại |
| Forwarding | IPv4 forwarding0, node làm endpoint |
| Node/network cũ | Nội dung XML mọi node cũ và danh sách network giữ nguyên; readiness.json |
| Firewall/Core | PID QEMU cũ khớp trước/sau; không có thao tác restart hoặc thay cấu hình; final-host-state.json |

IP .40.110 là lease mới do DHCP cấp, không sao chép IP VPCS bằng tay. VPCS cũ vẫn tắt; khi dùng lại phải kiểm tra DHCP/lease để tránh dùng địa chỉ lịch sử trùng với endpoint mới. Trước áp NAT phải đọc lại IP/MAC/lease, không coi IP dynamic cố định.

Không gửi HTTPS tới1.1.1.1 hoặc đích khác; chưa kiểm chứng handshake từ xa, NAT hoặc Internet. PASS chỉ về IP/route và client/CA tại node mới. Không lặp kiểm thử M3.5/M3.6 hoặc failover. So sánh PID/topology chứng minh không restart/sửa node cũ trong đợt, không phải đo SLA hoặc chứng minh không mất gói.

## 3.15.3. Minh chứng và hình
Thư mục docs/evidence/M3/Employee-Linux-20261106/. create-result.json có backup/hash/MAC/node/seed, readiness.json có dữ liệu thật từ marker serial do script trong guest xuất; acceptance.json ghi phạm vi kết luận. Base-readonly-inspection.json là lần gọi guestfish sai tùy chọn đã thất bại, không dùng làm PASS; bản v2 read-only thành công được giữ kèm để truy vết. Không chỉnh/xóa log lỗi.

Hình 3.15. Employee-Linux-status-20261106T211238+0700.png — ảnh console thật hiển thị IP, gateway, TLS/CA và trạng thái readiness. Mục đích xác nhận endpoint mới; kết quả đủ chuẩn bị nguồn NAT, không chứng minh Internet. Ảnh before ghi nhận boot và shell trước lệnh; không chỉnh nội dung. Thời điểm file là lúc lưu batch theo máy thu UTC+07:00; giờ guest chưa đồng bộ được giữ riêng. Danh mục evidence-index.csv ghi tên/nội dung/thời điểm/múi giờ/đường dẫn/vị trí/hash.

## 3.15.4. WAN chưa thực hiện
Phương án docs/M3/M3-WAN-guard-rollback-20261106.md đã lập: xác minh mapping/PID/hash, sao lưu XML/config/membership, giới hạn đúng hai TAP WAN, cập nhật runtime+metadata có guard/rollback/watchdog dự kiến, dừng nếu không có lease/gateway hoặc có sai lệch HA. Chưa triển khai bất kỳ phần WAN nào; cần phê duyệt riêng trước mutation. Không sửa HA/CARP/pfsync/hook hoặc Core.

M3 tổng thể PARTIAL; Employee local readiness PASS, WAN/NAT BLOCKED/PENDING_APPROVAL. Các PASS trước giữ nguyên. Việc còn lại chỉ được thực hiện sau quyền riêng: WAN an toàn→lease/gateway hai máy→rule nguồn Employee mới tới1.1.1.1 TCP443 và Hybrid SNAT→một HTTPS tối thiểu kèm ảnh/log.
