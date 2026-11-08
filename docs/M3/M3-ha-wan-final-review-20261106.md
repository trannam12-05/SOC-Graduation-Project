# 3.8. Kiểm tra nguyên nhân snapshot HA và điều kiện NAT Internet

## 3.8.1. Phạm vi và kết quả
Ngày 06/11/2026, UTC+07:00. M3 tổng thể **PARTIAL**, không DONE vì NAT Internet BLOCKED. Toàn bộ PASS M3.5/M3.6 và XMLRPC được tái sử dụng; không chạy lại kiểm thử truy cập, DHCP hoặc failover. Không thay topology, Core L2, VLAN/IP, cấu hình mạng hoặc vòng đời node; không cài phần mềm, reload hay restart. Chỉ ghi dữ liệu tạm phục vụ đọc console, không phát sinh thay cấu hình cần backup mới.

## 3.8.2. Nguyên nhân và đính chính snapshot
Log Primary ghi `pfsync bulk start` và demotion +240 ở 19:20:25; `pfsync bulk done` giảm demotion về 0 ở 19:31:38; năm VHID chuyển BACKUP sang MASTER lúc 19:31:39. Log Secondary cùng thời điểm ghi MASTER sang BACKUP vì nhận quảng bá thường xuyên hơn. Đây là thời gian nguyên bản của guest có offset +00:00, chưa được xác minh đồng bộ; không quy đổi thành giờ Việt Nam để khẳng định thời gian tuyệt đối.

Metadata lần thu cũ ghi thời điểm bắt đầu execute Primary 19:30:27, Secondary 19:33:29 theo đồng hồ EVE. Collector đọc tuần tự, và thời gian tên file 19:36:30 UTC+07:00 chỉ là lúc lưu batch. Vì vậy hai giá trị BACKUP thuộc các thời điểm khác nhau, nằm hai phía của lần chuyển vai trò; **không có bằng chứng cả hai đồng thời BACKUP**. Đính chính diễn giải ở mục 3.7 và checkpoint cũ; giữ nguyên ảnh, JSON và lịch sử.

Cơ chế quan sát được: pfsync đang bulk sync làm Primary tăng demotion, giảm ưu tiên CARP; khi hoàn tất, Primary ưu tiên cao hơn lấy lại MASTER, Secondary về BACKUP. Chưa đủ bằng chứng xác định vì sao bulk kéo dài khoảng 11 phút theo log guest; không khẳng định tác nhân, mất kết nối hoặc lỗi phần mềm. Log và kernel events được lưu trong JSON và transition-events.csv.

## 3.8.3. Quan sát HA không gián đoạn
Bảy mẫu mỗi máy, cách nhau khoảng 10 giây, trong khoảng 60 giây mỗi máy: Primary MASTER và Secondary BACKUP trên VLAN30/40/50/60/99; pfsync UP/RUNNING, syncok1; demotion0 và carp.allow1 ở mọi mẫu. Hai cửa sổ thu tuần tự, không đồng thời; thời gian guest lưu nguyên bản trong ha-samples.csv. Kết quả **PASS trong cửa sổ quan sát**, không suy thành chứng minh độ ổn định dài hạn, zero packet loss hoặc SLA dịch vụ. Không tác động dịch vụ để kiểm thử.

## 3.8.4. WAN và NAT Internet: BLOCKED
Hai WAN vtnet1 được cấu hình IPv4 DHCP, nhưng runtime chỉ có IPv6 link-local, không có IPv4. Lệnh route get IPv4 default trả về route has not been found. pfctl -sn chỉ có no nat/no rdr, không có outbound NAT dịch địa chỉ. Phù hợp điều kiện WAN cô lập trong hồ sơ M3.5; chưa có điều kiện kiểm thử Internet. Không chạy thử Internet hoặc tự thay topology.

Điều kiện xử lý: cần upstream có Internet, địa chỉ WAN và gateway hợp lệ, cùng phương án thay đổi được phê duyệt trước khi thực hiện; sau đó mới có thể nghiệm thu NAT bằng luồng thực tế. Nếu cần điều tra thời gian bulk kéo dài, cần thêm quan sát/log pfsync có mốc đồng bộ; không tự reset demotion hoặc restart HA.

## 3.8.5. Minh chứng và chú thích hình
Thư mục docs/evidence/M3/M3-ha-wan-audit-20261106/. Tệp acceptance.json ghi kết luận; results-20261106T200230+0700.json chứa log, kernel events, cấu hình WAN đã lọc và mẫu runtime; ha-samples.csv và transition-events.csv phục vụ đối chiếu. evidence-index.csv liệt kê ảnh/log, thời điểm lưu kèm múi giờ, SHA-256 và vị trí báo cáo. Thời gian lưu batch không thay thế mốc guest chưa đồng bộ.

Hình 3.9. Ảnh console trạng thái/log/WAN Primary (tệp OPNsense-Primary-status-*.png trong đợt này). Mục đích xác nhận log bulk và vai trò hiện tại; nội dung gồm demotion, CARP và lệnh IPv4/default route. Kết quả giúp phân biệt phục hồi ưu tiên CARP với việc thiếu kết nối WAN.

Hình 3.10. Ảnh console trạng thái/log/WAN Secondary (OPNsense-Secondary-status-*.png). Mục đích đối chiếu phía dự phòng; nội dung gồm CARP BACKUP, demotion và WAN. Ý nghĩa xác nhận vai trò dự phòng hiện tại và điều kiện NAT chưa đáp ứng. Ảnh framebuffer thật, không sửa nội dung; ảnh trang dữ liệu truyền đi kèm JSON kiểm tra checksum, không phải ảnh mô phỏng.
