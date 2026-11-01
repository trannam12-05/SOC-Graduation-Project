# 3. Tiếp quản OPNsense Primary thực tế

## 3.1. Mốc kiểm tra 01/11/2026, 12:57 UTC+07:00

Ưu tiên theo yêu cầu mới: còn 9 giờ 30 phút tại thời điểm người dùng giao việc; không dùng hạn cũ 05/11 để trì hoãn. Đây là nhật ký kỹ thuật, chưa phải báo cáo nghiệm thu M3.

- SSH đã khôi phục sau khi người dùng nạp khóa vào ssh-agent. Không thay đổi dịch vụ Windows bởi công cụ triển khai.
- EVE có đúng một tiến trình QEMU Primary: UUID `fe606d13-1542-490b-b651-5c1c6289afde`, node ID 1, 2 vCPU, 3072 MiB, ba NIC. Core ID 3 không chạy.
- EVE available 5114 MiB, swap used 0 MiB. Windows đo kế tiếp chỉ khoảng 0,40 GiB RAM available, commit available 2,89 GiB. Không bật Core hoặc tăng tải khi thiếu dự phòng.
- Lab hiện không có network/link. ISO gắn từ `/opt/unetlab/addons/qemu/opnsense-26.7-soc/cdrom.iso`; đĩa runtime có tên `virtioa.qcow2`. Chưa kiểm tra partition hoặc nội dung ổ, không ghi trực tiếp vào QCOW2.
- **Console thật xác nhận OPNsense 26.7 chạy Live từ ISO**, root filesystem `/dev/iso9660/OPNSENSE_INSTALL`. Điều này không chứng minh ổ cứng trống hoặc đã cài; phải đọc partition trước thao tác installer.
- Console mặc định LAN `vtnet0`, IPv4 `192.168.1.1/24`; WAN `vtnet1`. Không lấy thứ tự cổng thiết kế làm mapping đã kiểm chứng.

## 3.2. Mapping quan sát từ tiến trình QEMU

| Netdev | TAP | MAC | Tên guest | Vai trò |
|---|---|---|---|---|
| net0 | vunl0_1_0 | 50:00:00:01:00:00 | Chờ đối chiếu ifconfig | Chưa chốt |
| net1 | vunl0_1_1 | 50:00:00:01:00:01 | Chờ đối chiếu ifconfig | Chưa chốt |
| net2 | vunl0_1_2 | 50:00:00:01:00:02 | Chờ đối chiếu ifconfig | Chưa chốt |

## 3.3. Bước tiếp tục

1. Từ shell Live đã xác thực: đọc `opnsense-version`, `mount`, `gpart show`, `geom disk list`, `ifconfig -a`; không xuất config.xml chứa bí mật.
2. Chỉ cài vào ổ runtime được xác minh đúng. Nếu có hệ điều hành/dữ liệu cũ, dừng bước ghi, chuẩn bị sao lưu phù hợp; không coi việc boot Live là bằng chứng ổ trống.
3. Installer chỉ ghi ổ ảo từ bên trong guest; không dùng qemu-img sửa đĩa đang mở. Bước boot lại phải chứng minh root filesystem nằm trên ổ, không còn ISO Live. Không xóa hoặc ghi đè image/ISO gốc.
4. Cấu hình Primary riêng trước, theo ma trận M3; gateway tạm thời là IP Primary `.2`, không gọi là CARP VIP. WAN/upstream và các chính sách đích cụ thể còn phải chốt. Không nối mạng thật.
5. Khi đủ RAM mới bật Core và nối trunk riêng đã đối chiếu MAC; kiểm thử routing/firewall thật. Không chạy lại 95 ca M2 còn bằng chứng hợp lệ chỉ vì mô tả đầu vào ghi chưa kiểm thử.

Nguồn quy trình installer: [OPNsense — Initial Installation & Configuration](https://docs.opnsense.org/manual/install.html). Không lưu thông tin xác thực vào nhật ký này.

## 3.4. Minh chứng hiện có

Hình 3.1: `../evidence/M3/primary-live-20261101/primary-initial-20261101T125710+0700.png`.

Mục đích: xác định trạng thái khởi động trước khi cài. Nội dung: màn hình Live OPNsense 26.7, root filesystem ISO, tên LAN/WAN và login. Kết quả: chưa chứng minh cài đặt vào đĩa. Ý nghĩa: tránh cấu hình Live rồi nhầm là cấu hình persistent. Ảnh framebuffer thật, không chỉnh sửa; metadata cùng tên JSON ghi UUID, cấu hình QEMU, thời điểm và SHA-256.

Các ca cài ổ, boot ổ, gateway, routing, firewall, NAT, HA và IDS: **NOT_RUN trong phiên này**. M2 đã có 95/95 ca frame thật và persistence trong báo cáo riêng; không quy đổi thành PASS của M3.
