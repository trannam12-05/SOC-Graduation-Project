# Phương pháp thu thập recovery checkpoint M3

## 1. Phạm vi

Lượt này được phép đọc EVE-NG và hai firewall; không thay cấu hình, không apply CARP, không tạo/xóa VLAN/VIP, không reload/restart/reboot/shutdown/failover. Evidence mới chỉ ghi tại Windows.

## 2. Xác thực console

Ảnh initial giữ nguyên lỗi cũ. Lệnh hostname trên Secondary thành công; Primary ban đầu thành HOSTNAME. Một thử Caps Lock, thử đảo chữ và thử bỏ Shift chưa giải quyết đầy đủ dấu câu. Các ảnh lỗi được giữ nguyên.

Collector cũ tính bảng phím nền nhưng vẫn gửi keysym của ký tự đã Shift. Bản collector riêng trong thư mục evidence dùng phím nền và Shift khi cần. Phép thử print chuỗi đã xuất đúng dấu câu, sau đó đọc chỉ trong bộ nhớ. Không sửa collector gốc hoặc cấu hình keyboard guest.

## 3. Dữ liệu trong bộ nhớ

Khởi tạo một process Python nhận từng dòng từ stdin, không dùng interactive history và không viết helper/config/backup vào guest. Reader được truyền dưới dạng hexadecimal chữ thường theo từng đoạn400 ký tự để tránh vấn đề chữ HOA. Trước exec, bắt buộc SHA-256 bytes reader khớp bản Windows. Nội dung reader chỉ đọc config.xml/backup có sẵn, chạy ifconfig, netstat, sysctl, dmesg và lệnh nhận dạng hệ điều hành; không ghi cấu hình.

Output dùng whitelist cho VIP/interface, chỉ xuất boolean so sánh top-level XML và full-config checksum. Không xuất password/CARP secret/key hoặc toàn bộ XML. Snapshot JSON public nén/base64, được hiển thị theo trang trên console thật; giải mã glyph đúng mẫu và kiểm SHA-256 toàn payload, không đoán bằng OCR. Process reader thoát sau nhận đủ dữ liệu.

## 4. Giới hạn

Ảnh chunk chứng minh truyền code, không chứng minh phép đọc đã thành công. Chỉ snapshot có checksum được chấp nhận làm kết quả. SHA-256 file/metadata không tự xác thực nguồn độc lập; đối chiếu node UUID/QEMU, SYNC IP và backup checksum để xác nhận guest.

Thời gian chuẩn báo cáo dùng collector Windows UTC+07:00; đồng hồ EVE/guest không được mặc định đồng bộ. Host inventory không ghi acquisition timestamp chính xác lúc chạy, phải ghi giới hạn này thay vì tự dựng thời điểm thu. Không coi lỗi script đọc là lỗi CARP hay mất hệ điều hành.
