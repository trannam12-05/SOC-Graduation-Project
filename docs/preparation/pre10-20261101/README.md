# Kết quả chuẩn bị trước 10 giờ, không phải minh chứng mạng

Thư mục chỉ lưu kết quả kiểm tra cục bộ tài liệu và luồng chương trình. Không gọi SSH tới EVE, không khởi động VM, không truy cập QCOW2, không phát frame, không tạo PCAP/screenshot mới.

- static-review.json và static-tests.log: lần đầu12 mock/static test tại mốc tạo báo cáo.
- static-final-review.json và static-tests-final.log: lần chốt theo hash script hiện hành, bổ sung kiểm tra đổi chéo QEMU/TAP/MAC; xem tests_run thực tế trong JSON. Không diễn giải thành PASS VLAN/trunk/mirror/reboot/HA/IDS.
- static-tests-mapping-first-attempt.log: lần thêm test mapping gặp BOM UTF-8 của fixture cũ; sửa cách đọc utf-8-sig, giữ nguyên minh chứng nguồn rồi thử lại. Đây là lỗi đọc fixture cục bộ, không phải kết quả mạng.
- docx-review.json:10 DOCX M2 kiểm cấu trúc ZIP/XML, A4, lề, sự hiện diện Times New Roman và số ảnh; không có lỗi theo các tiêu chí đó, chưa xem GUI phân trang.
- SHA256SUMS.txt: checksum các tệp gốc lúc xuất bản báo cáo; FINAL-SHA256SUMS.txt bổ sung nguồn/script/log tại lần chốt. Mọi báo cáo Word trước đợt này giữ nguyên.

Queue staging/m2-offline-plan-20261101 chỉ có các stage NOT_RUN, chưa phải phiên triển khai. Thời điểm10:00 không tự kích hoạt queue; phải có thông báo tài nguyên sẵn sàng rồi mới xét thực thi.
