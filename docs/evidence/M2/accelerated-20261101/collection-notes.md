# Ghi chú thu thập 01/11/2026 — UTC+07:00

- Lần kiểm kê/console đầu trả lỗi SSH `Permission denied (publickey,password)`; `ssh-add -l` báo không kết nối agent, dịch vụ lúc đó Stopped. Sau khi người dùng khôi phục agent, lệnh SSH `true` trả mã 0.
- `preflight-local.json` được thu lúc 07:57:52+07:00, khi agent đã Running. Trường `SshResult` trong tệp này nhắc lại **lỗi của lần trước**, không phải kết quả xác thực đồng thời với mẫu RAM. Dùng kết quả thu thành công của `port-design-20261101T075757+0700/eve-inventory.json` để xác nhận SSH đã phục hồi. Giữ tệp gốc, không sửa minh chứng để che khác biệt thời điểm.
- Script `inspect_m2_port_design_readonly.py` kết thúc mã 0, ghi inventory EVE và RAM Windows. Không có QEMU đang chạy; console collector dừng ở guard không có đúng một QEMU Core, không tự khởi động node. Không chụp được ảnh console mới.
- `unl_wrapper -h` trong stopped-host-inspection.json trả mã 3 vì thiếu action; đây là truy vấn usage, không phải lệnh start/stop/wipe đã chạy. Danh sách action xuất hiện trong help không có nghĩa các action đó được thực hiện.
- Script sao lưu overlay lần đầu dừng do Python EVE không có `hashlib.file_digest`. Lỗi xảy ra khi tính hash trước sao chép; đã giữ thư mục được tạo, đổi SHA-256 sang đọc theo khối rồi chạy lại. Lần sau mã 0; metadata `stopped-backup.json` cho ba hash bằng nhau. Chỉ copy khi không có tiến trình QEMU Core; không ghi vào QCOW2 nguồn hoặc image gốc. Chưa restore overlay.
- Tên thư mục backup dùng đồng hồ UTC của EVE, **không phải thời điểm UTC+07:00 đã đồng bộ**. Số đo uptime/giờ EVE được giữ nguyên trong JSON, không dùng thay collector time. Backup được thu giữa kiểm kê lúc 07:58 và kiểm tra cục bộ sau đó; không gán giây thu thập chính xác khi không có receipt riêng.
- Sau yêu cầu chế độ nhẹ trong lúc người dùng học Labtainer: không gửi thêm thao tác thay đổi tới EVE, không bật VM, không chạy script frame/mirror/persistence, không tải OPNsense. Tài liệu mới chỉ sử dụng ảnh cũ; PCAP thử nghiệm chưa tồn tại.

Tệp kiểm kê thô có cấu hình host hiện hữu phục vụ đối chiếu; không phải cấu hình do đợt này áp dụng. Không lưu thông tin xác thực trong các tệp minh chứng này.
