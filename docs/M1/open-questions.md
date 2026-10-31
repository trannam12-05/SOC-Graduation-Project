# Câu hỏi còn mở sau khi đọc M1

## Cách hiểu trạng thái

M1 là báo cáo thiết kế, không xác nhận cấu hình đã chạy trên EVE-NG. Các subnet, VIP, IP firewall và cổng ở các bảng thiết kế được báo cáo gọi là ví dụ/đề xuất. Những câu hỏi dưới đây cần được trả lời trước khi chốt thiết kế dùng cho M2.

## Cần xác nhận với nhóm

1. **Địa chỉ mạng chính thức:** Có chấp thuận các subnet ví dụ `192.168.30.0/24`, `.40.0/24`, `.50.0/24`, `.60.0/24`, `.99.0/24` không? Có xung đột với kế hoạch IP chung hoặc mạng lab khác không?
2. **VLAN DMZ:** VLAN 60 được nêu là đề xuất. Nhóm có chốt VLAN 60 cho DMZ không? Danh sách VLAN chính thức có gồm 30, 40, 50, 60, 99 không?
3. **CARP và IP firewall:** Có chốt `.1` làm VIP, `.2` Primary, `.3` Secondary trên từng VLAN không? Các địa chỉ này vẫn cần kiểm tra trên EVE-NG.
4. **WAN:** Có bao nhiêu kết nối/ISP giả lập, node và interface nào kết nối vào từng firewall, địa chỉ WAN/transit/gateway nào được dùng, và Secondary có đường WAN để tiếp quản theo cách nào?
5. **HA SYNC:** SYNC tách biệt như Word yêu cầu bằng interface/mạng nào? Subnet và IP của hai firewall là gì? Cổng/node nào nối chúng?
6. **CARP/pfsync/XMLRPC:** Phiên bản OPNsense và image nào được dùng? Các thông số CARP, interface pfsync, phạm vi XMLRPC và phương thức bảo vệ truy cập quản trị cần chốt ra sao?
7. **DHCP:** VLAN nào bật DHCP? Scope, dải loại trừ, reservation, lease và gateway/DNS được cấp là gì?
8. **DNS:** DNS resolver/server nào phục vụ từng VLAN? Ví dụ `192.168.60.30` trong M1 chỉ nằm trong cột thiết bị ví dụ, chưa xác nhận vai trò hay việc cấp địa chỉ này cho client.
9. **Thiết bị và IP máy chủ:** Có chấp thuận các dải ví dụ Server `.10–.30`, PC/Guest `.100–.199`, Web `.10`, Core `.99.10` và Management PC `.99.100` không? Chúng cần đối chiếu bảng IP thống nhất toàn nhóm.
10. **Port mapping:** Image/model switch thực tế là gì? Các interface `Gi0/0` đến `Gi1/2` có tồn tại không? Cổng đích ở OPNsense/host chưa được Word nêu.
11. **Trunk/access:** Có chốt trunk OPNsense cho VLAN 30, 40, 50, 60, 99 không? Access port nào nối tới từng node thật? Có native VLAN hay giới hạn VLAN bổ sung không?
12. **SPAN/Suricata:** Nguồn mirror và hướng lưu lượng nào cần quan sát? Cổng đích Suricata là interface nào? Cần mirror trunk nào để vẫn bao phủ lưu lượng khi HA đổi vai?
13. **Core dự phòng:** M1 ghi nhận một Core L2 là điểm lỗi đơn. Phạm vi lab giữ một Core hay nhóm yêu cầu phương án Core thứ hai?
14. **Chính sách liên VLAN/NAT:** Ma trận M1 là tham chiếu. Các luồng được phép, dịch vụ/cổng cần thiết, outbound NAT và yêu cầu inbound DMZ nào được nhóm duyệt?
15. **Thông tin báo cáo:** Tên đề tài chính thức, trường/khoa, lớp, MSSV, giảng viên và phiên bản tài liệu/nguồn tham khảo còn là chỗ trống trong Word.

## Mâu thuẫn hoặc điểm cần làm rõ

- M1 dùng VLAN 30, 40, 50, 99 trong mô tả các nhóm đã phân công, đồng thời đề xuất VLAN 60 cho DMZ. Cần xác nhận 60 là VLAN đã duyệt hay mới là phương án.
- M1 đưa IP minh họa khá cụ thể nhưng đồng thời ghi đây là ví dụ cho lab và phải đối chiếu quy hoạch chính thức; không được xem là giá trị đã xác nhận.
- Bảng cổng chỉ nêu cổng phía Core và thiết bị/vùng đích, không nêu cổng phía thiết bị đích. Bảng cũng gọi tên interface IOSvL2 là ví dụ.
- Bảng cổng chỉ xác định SPAN destination, chưa xác định SPAN source hoặc phạm vi quan sát cần thiết khi failover.
- Yêu cầu SYNC tách biệt được nêu nhưng chưa có subnet, IP, cổng hay sơ đồ kết nối.
- DHCP được đề xuất trên OPNsense cho VLAN người dùng nếu cần; không có scope hoặc DNS client cụ thể.
- Bảng yêu cầu kỹ thuật gọi vùng là DMZ nhưng không ghi VLAN ID tại đó; VLAN 60 xuất hiện ở phần quy hoạch như đề xuất.

## Điều kiện đầu vào trước M2

Chốt ít nhất image và interface switch, VLAN được duyệt, port mapping hai đầu, trunk/access, SPAN source/destination, và quy hoạch IP chính thức. Mọi giá trị chưa được nhóm xác nhận tiếp tục phải được đánh dấu là đề xuất; không tạo IP hoặc cổng thay cho thông tin còn thiếu.
