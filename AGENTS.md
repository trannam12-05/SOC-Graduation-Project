# Quy ước và ràng buộc dự án

- Core Switch chỉ hoạt động ở Layer 2.
- Inter-VLAN Routing, gateway, ACL được thay bằng firewall rules và NAT, xử lý trên OPNsense.
- VLAN 30: Data Center; VLAN 40: Employee; VLAN 50: Guest; VLAN 60: DMZ; VLAN 99: Management.
- Các địa chỉ IP và cổng trong thiết kế M1 chỉ là đề xuất cho đến khi được xác nhận trên EVE-NG.
- Mọi cấu hình phải kèm giải thích bằng tiếng Việt.

## QUY ĐỊNH BẮT BUỘC VỀ MINH CHỨNG VÀ BÁO CÁO ĐỒ ÁN

Các quy định dưới đây áp dụng cho M2, M3, M4 và M5, bổ sung cho các quy định hiện có của dự án.

### 1. Thu thập minh chứng

- Sau mỗi bước kỹ thuật quan trọng, chụp ảnh màn hình thực tế nếu công cụ hiện có cho phép.
- Ưu tiên ảnh topology EVE-NG, console, kết quả lệnh cấu hình, VLAN, trunk, OVS, OPNsense HA và các bước kiểm thử.
- Ảnh phải rõ, không cắt mất kết quả quan trọng và không chứa mật khẩu, private key, token hoặc dữ liệu đăng nhập nhạy cảm.
- Không tạo ảnh giả để thay thế ảnh thực tế; không chỉnh sửa nội dung kỹ thuật của ảnh làm sai lệch minh chứng.
- Nếu không thể chụp ảnh trực tiếp, ghi rõ giới hạn công cụ và hướng dẫn người dùng chụp thủ công, gồm màn hình cần mở, thao tác cần thực hiện, nội dung cần thấy và nơi lưu ảnh. Không báo cáo ảnh chưa chụp là minh chứng đã có.

### 2. Tổ chức thư mục

Lưu minh chứng theo từng giai đoạn:

- `docs/evidence/M1/`
- `docs/evidence/M2/`
- `docs/evidence/M3/`
- `docs/evidence/M4/`
- `docs/evidence/M5/`

Giữ nguyên các ảnh và log trước đây trong `docs/evidence/eve-ng/`. Không di chuyển hoặc xóa minh chứng cũ khi chưa được người dùng cho phép.

### 3. Viết báo cáo

- Áp dụng phong cách đồ án tốt nghiệp: tiếng Việt học thuật, rõ ràng, chính xác.
- Khi xuất Word: khổ giấy A4, phông Times New Roman, cỡ chữ 12–13; lề trái 3 cm, lề phải, trên và dưới 2 cm.
- Chương, mục và tiểu mục phải được đánh số.
- Hình minh họa phải được đánh số theo chương; chú thích đặt bên dưới hình.
- Mỗi hình phải có phần giải thích mục đích, nội dung, kết quả và ý nghĩa.
- Phân biệt rõ thiết kế dự kiến với cấu hình đã triển khai và kiểm chứng; không trình bày đề xuất hoặc thao tác chưa xác minh như kết quả thực tế.
- Trích dẫn nguồn chính thức khi sử dụng thông tin từ tài liệu bên ngoài.

### 4. Giải thích thuật ngữ

Mỗi khái niệm kỹ thuật quan trọng phải được giải thích đầy đủ:

- Tên tiếng Anh đầy đủ và viết tắt (nếu có); với tên sản phẩm hoặc tên riêng, ghi đúng tên chính thức, không tự tạo dạng khai triển.
- Nghĩa tiếng Việt.
- Nguyên lý hoạt động.
- Vai trò trong hệ thống SOC.
- Ví dụ áp dụng trong topology của đồ án; ghi rõ ví dụ là thiết kế dự kiến hay đã được kiểm chứng.

Các khái niệm cần giải thích bao gồm: SOC, VLAN, 802.1Q, trunk, access port, LACP, SPAN, port mirroring, OVS, bridge, QEMU, QCOW2, cloud-init, NoCloud, SSH, OPNsense, CARP, pfsync, HA, NAT, DHCP, IDS/IPS, Suricata và Wazuh.

### 5. Quản lý kết quả

Sau mỗi giai đoạn:

- Lưu ảnh chụp thật, log và cấu hình đã kiểm chứng vào thư mục minh chứng tương ứng.
- Tạo bảng danh mục minh chứng có ít nhất các trường: tên ảnh hoặc tệp minh chứng, nội dung, thời điểm thu thập (kèm múi giờ), đường dẫn và vị trí dự kiến trong báo cáo.
- Ghi rõ kết quả đạt/chưa đạt và các vấn đề còn tồn tại, gắn với minh chứng tương ứng; không kết luận đạt khi chưa có bằng chứng kiểm chứng.
- Chuẩn bị nội dung có thể đưa trực tiếp vào báo cáo Word, bao gồm phần thuyết minh, bảng kết quả, chú thích và giải thích hình.

### 6. Giới hạn quyền

Việc bổ sung quy tắc và thu thập minh chứng không đồng nghĩa với quyền tự ý cài đặt phần mềm, thay đổi cấu hình EVE-NG, khởi động hoặc xóa node. Mọi thao tác thay đổi hệ thống, bao gồm dừng VM/node, sửa seed, thay đổi mạng hoặc image, vẫn phải tuân theo quyền phê duyệt riêng của người dùng. Không suy diễn quyền thay đổi hệ thống từ yêu cầu chụp ảnh, ghi log hoặc viết báo cáo.
