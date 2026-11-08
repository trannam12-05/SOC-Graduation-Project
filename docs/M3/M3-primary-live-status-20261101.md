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
| net0 | vunl0_1_0 | 50:00:00:01:00:00 | vtnet0 — đã đối chiếu | LAN hiện tại; dự kiến LAN trunk |
| net1 | vunl0_1_1 | 50:00:00:01:00:01 | vtnet1 — đã đối chiếu | WAN hiện tại; chưa nối upstream |
| net2 | vunl0_1_2 | 50:00:00:01:00:02 | vtnet2 — đã đối chiếu | Chưa gán; dự kiến SYNC |

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

## 3.5. Kiểm tra shell thực tế 12:59–13:00 UTC+07:00

Người dùng đăng nhập root, chọn shell. Chỉ gửi lệnh chẩn đoán cố định bằng `automation/m3_inspect_guest_console.py`; không gửi thông tin xác thực. `diskinfo vtbd0` trả 17179869184 byte (16 GiB), sector 512 byte, 33554432 sector. `gpart show vtbd0` trả `No such geom: vtbd0`: không có bảng phân vùng được GEOM nhận diện, **không phải chứng minh toàn bộ ổ không chứa dữ liệu**. Mount `/` vẫn là ISO read-only. Chưa chạy installer hoặc ghi ổ.

Ảnh `primary-disk-20261101T125957+0700.png` là Hình 3.2: xác minh đích và root filesystem để tránh chọn nhầm. Ảnh `primary-nics-20261101T130009+0700.png` và `primary-nic-summary-20261101T130025+0700.png` cùng xác nhận mapping trên; ảnh đầu thiếu dòng tiêu đề vtnet0 do màn hình hữu hạn nên dùng ảnh thứ hai bổ sung, không sửa/cắt ảnh gốc. Đây là Hình 3.3–3.4 về định danh cổng trước cấu hình VLAN. Link `active` của vNIC không chứng minh đã có peer; lab vẫn không nối link.

RAM Windows đo lại sau thông báo giải phóng là 0,49 GiB available, commit available 2,93 GiB. Installer bị tạm chặn do dưới dự phòng 1 GiB đã thông báo; yêu cầu giải phóng thêm RAM, không thay đổi Windows/VMware hoặc tự dừng VM. Không bật Core. Kết quả đo kế tiếp lưu `resource-before-install.json`; đây là mẫu tại thời điểm thu, không thay các số đo lịch sử.

Checkpoint M2 và trạng thái Live ban đầu đã push lên GitHub PRIVATE tại commit `3eae637fbfeba2d9b56647364292938091a50cf6`. Các kiểm tra shell bổ sung được lưu sau checkpoint đó.

## 3.6. Sao lưu an toàn và trạng thái mới nhất 13:03 UTC+07:00

Mẫu đo 13:01:16 lên 1,27 GiB RAM available/3,42 GiB commit available. Đã gửi `shutdown -p now` trong shell Primary để tạo backup nhất quán trước installer. Lần guard đầu phát hiện QEMU còn đang shutdown và chặn sao lưu; không đọc/ghi đĩa bằng qemu-img khi còn chạy. Lần sau xác nhận không còn QEMU rồi mới sao chép ổ runtime và lab XML.

**Primary hiện TẮT, Core vẫn TẮT; chưa chạy installer.** Backup `/root/m3-primary-preinstall-20261101T1302/virtioa.qcow2`, 197120 byte; SHA-256 `c09a6c5e5ac5090ab3bcefaccd0a97b6fc318f2f50cc1893aaaa1edac8f2ae83` khớp nguồn trước/sau và bản sao. Metadata ở `stopped-backup.json`; backing image gốc giữ nguyên. Ảnh `primary-graceful-poweroff-20261101T130147+0700.png` ghi shutdown mềm thực tế, không phải Reset.

Rollback dự kiến: chỉ khi Primary tắt và đã xác minh không còn tiến trình giữ ổ, bảo toàn runtime lỗi vào tên mới rồi phục hồi overlay đã sao lưu về đúng đường dẫn nguồn trong metadata; không thay image gốc. Chưa thử restore, không gọi rollback là PASS.

Sau tắt VM Windows vẫn chỉ 1,13 GiB available/3,41 GiB commit available. Chưa bật lại VM 3 GiB; yêu cầu dự phòng khoảng 4 GiB RAM available để khởi động lại an toàn. Mức 1 GiB trước đó dành cho VM đã chạy, không phải ngưỡng khởi động VM mới. Bước tiếp tục: đo lại tài nguyên, start đúng node ID 1, vào installer và xác minh đúng vtbd0; giữ mọi node khác tắt.

### 3.6.1. Quyết định tài nguyên được điều chỉnh và khởi động lại

Ngưỡng 4 GiB Windows nêu trên được đánh giá lại là quá bảo thủ cho QEMU lồng trong EVE đã được cấp 8 GiB; đây không phải tạo thêm VM Windows 3 GiB. Số đo khi tắt Primary cho thấy RAM Windows gần như không đổi, trong khi EVE available tăng. Chỉ bật lại Primary sau guard: Windows available ≥1 GiB, commit available ≥2 GiB; EVE available ≥4 GiB, swap chưa dùng và không có QEMU khác. Đây là ngưỡng vận hành tạm của phiên, không bảo đảm mọi tải tương lai an toàn.

**Trạng thái mới nhất: Primary đã bật lại, Core tắt; chưa chạy installer.** Receipt `start-primary-after-backup.json` lưu Windows available 1,128 GiB, commit available 3,421 GiB; EVE available 6354 MiB trước start. Ảnh `primary-restarted-20261101T130415+0700.png` là màn hình boot thực tế, không chứng minh cài đặt. Chờ người dùng đăng nhập `installer` trực tiếp, dừng tại Keymap. Đã chuẩn bị `m3_installer_keys.py`, chỉ gửi phím điều hướng sau khi xem từng màn hình; chưa chạy script này, không chứa thông tin xác thực.

Mẫu sau start có Windows available 0,86 GiB, commit available 3,33 GiB; EVE available 6175 MiB, swap 0. Tiếp tục theo dõi, không bật Core hoặc tăng tải khi RAM dưới ngưỡng. Việc bật Primary không tự đồng nghĩa đã đủ tài nguyên để bật thêm VM hay nghiệm thu gateway.

## 3.7. Installer đã chọn UFS, chưa ghi ổ — 13:18 UTC+07:00

Lưu ý: phần 3.7 ghi lịch sử tạm dừng. Trạng thái mới hơn ở 3.8 bên dưới.

Người dùng đăng nhập installer, xác nhận màn hình Keymap. Công cụ chụp đúng trạng thái rồi gửi Enter để giữ keymap US mặc định; tiếp tục Down/Enter từ menu để chọn Install (UFS). Đây là phương án filesystem đơn giản cho lab một ổ, không triển khai ZFS trong phiên này. Tùy chọn UFS hiện diện trong installer thật; không gọi việc chọn menu là cài thành công.

Ảnh `installer-ufs-target-20261101T131826+0700.png` xác nhận danh sách gồm `vtbd0 <Unknown disk> (16GB)` và `cd0 <QEMU QEMU DVDROM 25> (1GB)`. Thanh chọn đang ở vtbd0; chưa nhấn OK hoặc xác nhận phân vùng. Dung lượng hiển thị DVD của installer không thay thế kích thước tệp ISO đã đo trên EVE.

Windows trước bước này available 0,37 GiB, commit available 3,01 GiB; EVE available 5035 MiB, swap 0. Tạm dừng thao tác ghi/tăng tải cho đến khi Windows đạt khoảng 1 GiB available. Giữ nguyên phiên installer để tiếp tục ngay, không tắt/bật lại VM. Core tắt. Người dùng được đề nghị đóng các ứng dụng không cần thiết, không tự dừng tiến trình hoặc thay cấu hình host.

Hình 3.5–3.7: các ảnh `installer-keymap-20261101T131744+0700.png`, `installer-options-20261101T131807+0700.png`, `installer-ufs-target-20261101T131826+0700.png`. Mục đích: ghi nhận diễn biến installer và xác minh đích trước ghi. Kết quả: keymap mặc định và UFS đã chọn, đúng ổ vtbd0 16GB hiển thị. Ý nghĩa: tránh chọn nhầm DVD và tránh tuyên bố cài xong khi mới ở menu. Metadata JSON cùng tên ghi phím đã gửi, thời điểm và SHA-256; ảnh nguyên framebuffer.

## 3.8. Thực thi cài UFS từ 13:26 UTC+07:00

Sau đánh giá lại tài nguyên, tiếp tục duy nhất Primary đang chạy: EVE available 4988 MiB, swap 0; Windows available 0,61 GiB nhưng commit available 4,24 GiB. Mốc Windows 1 GiB trước đó là dự phòng vận hành tạm, không phải yêu cầu bắt buộc của installer; giữ nguyên hạn chế không tăng RAM/khởi động thêm VM hoặc thử song song. Không tiếp tục dừng ở menu chỉ vì mốc tạm đó khi ngân sách trong EVE còn đủ; tiếp tục theo dõi thực tế.

Đã xem ảnh xác nhận ghi chỉ liệt kê `vtbd0`, rồi gửi Enter tại YES theo quyền cài đặt người dùng đã duyệt. Backup offline đã có trước thao tác này. Installer ghi từ bên trong guest vào ổ runtime; không mở QCOW2 để sửa từ host, không thay image gốc.

Ảnh `installer-write-started-20261101T132632+0700.png` ghi phân vùng đang khởi tạo; ảnh `installer-progress-20261101T132703+0700.png` ghi khởi tạo 100%. Sau đó chuyển sang Cloning current system, Verifying resulting files, Preparing target system. Ảnh `installer-copy-progress2-20261101T132908+0700.png` ghi cloning 1%, các bước sau chưa chạy. Đây là **IN_PROGRESS**, không phải PASS cài đặt hoặc boot từ ổ.

Mẫu tài nguyên trong khi cài: Windows available 0,91 GiB, commit available 4,35 GiB; EVE available 4982 MiB/swap 0. Kiểm tra metadata tệp runtime bằng stat thấy 366411776 byte đang tăng, filesystem EVE còn khoảng 35 GiB. Không đọc nội dung QCOW2 hoặc gọi qemu-img trong lúc VM chạy.
