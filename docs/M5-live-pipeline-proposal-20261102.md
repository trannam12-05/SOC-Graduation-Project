# 1. Phương án hoàn thiện truyền log trực tiếp — chưa triển khai

## 1.1. Hiện trạng quan sát

Kiểm kê 20:33:51 ngày 02/11/2026 (UTC+07:00) xác nhận Wazuh-SOC có một NIC khai báo nhưng không có attachment segment trong XML lab. Tất cả QEMU đang tắt tại thời điểm đó. Sau phê duyệt, chỉ Wazuh-SOC được bật. Chưa sửa link, seed, image hoặc RAM.

RAM danh nghĩa từ XML: Core 2048 MiB, sensor 1024 MiB, Manager 4096 MiB. Tổng ba node là 7168 MiB, chưa tính bộ nhớ QEMU và EVE. EVE có 7897 MiB RAM nhìn thấy; lúc tất cả node tắt MemAvailable 6630 MiB. Với hiện trạng này chưa đủ căn cứ chạy cả ba node đồng thời an toàn. Windows 16 GB còn phải chạy VMware, công cụ truy cập và quay video.

## 1.2. Lộ trình đề xuất có thể phê duyệt riêng

1. Chốt Wazuh thuộc VLAN 99 Management, địa chỉ IPv4 cụ thể không trùng, đường nối segment Management hiện có và đường vận chuyển log. Đây là đề xuất, chưa phải mapping được duyệt.
2. Sao lưu XML lab và cấu hình guest trước khi nối NIC. Không cấu hình IP hoặc forwarding trên Core.
3. Đánh giá thu log bằng Wazuh agent trên sensor theo tài liệu chính thức; cần phê duyệt cài agent nếu chọn cách này. Kênh dữ liệu mặc định thường dùng TCP 1514; chốt bằng cấu hình thực tế, không tự mở cổng/enrollment từ giả định. Không đưa khóa agent vào log hoặc Git.
4. Kiểm thử truyền log sensor–Manager theo nhóm hai node (5120 MiB), Core giữ tắt. Chỉ khi sự kiện mới được sensor sinh và vận chuyển tự động mới ghi PASS cho đoạn sensor–Manager. Nếu dùng PCAP hoặc replay trong sensor, phải ghi rõ nguồn; không gọi là live Core–SOC.
5. Muốn nghiệm thu toàn chuỗi Core–sensor–Manager cần cả ba khối hoạt động đồng thời, tài nguyên đủ dự phòng và nguồn frame mới có marker riêng. Đánh giá giảm RAM chỉ sau shutdown được duyệt và sao lưu; không giảm trong lúc node chạy. Không đổi sang Docker khi chưa có đánh giá và sự đồng ý.

Phương án này chưa thực thi. Không nối mạng qua host EVE hoặc tự tạo đường hầm để bỏ qua giới hạn phê duyệt thay đổi topology.

## 1.3. Tiêu chí nghiệm thu live

Ghi thời điểm máy thu UTC+07:00, marker mới, boot_id và trạng thái các node. Quan sát frame nguồn đi vào Core và tới capture sensor; lấy sự kiện mới trong `eve.json` có SID, IP và marker tương ứng; xác nhận collector/agent vận chuyển tự động; lấy alert mới trong `alerts.json` có đúng trường sự kiện và nguồn log. Có đối chứng âm và không nạp thủ công JSON trong khoảng thử. Lưu snapshot cấu hình công khai và chụp ảnh từng chặng, không lấy việc dịch vụ `active` thay bằng chứng dữ liệu.

Chỉ có cảnh báo replay tại Manager thì trạng thái toàn chuỗi vẫn `NOT_VERIFIED_LIVE`. Thiếu Indexer/Dashboard không cản trở kiểm tra alert tệp trên Manager, nhưng không được báo giao diện SOC đã nghiệm thu.

## 1.4. Nguồn chính thức

[Wazuh Network IDS integration](https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html) mô tả agent đọc JSON `eve.json` trên máy Suricata. Đây là căn cứ đề xuất; không chứng minh agent đã có trong topology của đồ án.
