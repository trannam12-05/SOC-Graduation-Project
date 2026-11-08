# 1. Hướng dẫn thu ảnh topology thật

## 1.1. Giới hạn đợt hợp nhất

Đợt ngày 05/11/2026 chỉ thao tác tài liệu cục bộ, chưa truy cập GUI hoặc console EVE. Không có ảnh hiện trạng mới được thu. Sơ đồ Mermaid là thiết kế, không phải minh chứng triển khai.

## 1.2. Màn hình cần chụp

1. Mở EVE-NG, lab SOC-M2-Core-L2, chế độ xem toàn topology. Hiển thị tên 10 node, năm vùng, hai trunk, SYNC, capture và segment Management. Lưu `topology-overview-YYYYMMDDTHHMMSS+0700.png` trong thư mục này. Không tự bật node chỉ để chụp.
2. Sau khi việc nối Wazuh được phê duyệt và thực hiện, mở thông tin link/NIC để thấy Wazuh e0 thuộc cùng segment Management với Core e4 và Suricata e1. Lưu `wazuh-management-link-YYYYMMDDTHHMMSS+0700.png`. Không dùng ảnh trước thay đổi để kết luận đã nối.
3. Khi có quyền kiểm tra runtime, mở console Core, hiển thị mapping OVS, địa chỉ interface và forwarding; cần thấy đúng năm access, hai trunk, mirror ens10 và không IP ngoài loopback. Lưu `core-l2-runtime-YYYYMMDDTHHMMSS+0700.png`.
4. Khi firewall đang chạy theo cửa sổ được duyệt, mở trạng thái CARP/VIP hai phía; cần thấy năm VIP, MASTER/BACKUP. Lưu riêng ảnh mỗi phía, không mở màn hình chứa secret.

Mỗi ảnh phải rõ chữ, không cắt kết quả quan trọng, không chứa mật khẩu/token/private key. Ghi thời điểm thu UTC+07:00, đường dẫn, nội dung và vị trí báo cáo vào danh mục mới. Chú thích đánh số Hình 1.2 trở đi; giải thích mục đích, nội dung, kết quả và ý nghĩa. Ảnh lịch sử vẫn giữ nguyên thư mục cũ.
