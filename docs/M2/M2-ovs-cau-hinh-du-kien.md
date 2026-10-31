## 2.19. Phương án bridge, access/trunk và mirror sau cài đặt

### 2.19.1. Điều kiện trước triển khai mạng

Toàn bộ mục này là **cấu hình dự kiến, chưa thực thi**. Đối chiếu đủ tám dòng EVE port → MAC QEMU → MAC/tên NIC Ubuntu → thiết bị/cổng peer. Có tám NIC trong guest không có nghĩa đã xác minh peer hoặc topology. Không lấy thứ tự ens3–ens10 làm căn cứ tự động gán vai trò. Vai trò dự kiến: năm access cho VLAN 30/40/50/60/99, hai trunk riêng tới OPNsense Primary/Secondary và một output mirror tới NIC capture Suricata.

Trước khi áp dụng cần ghi rõ allowed VLAN, chế độ tagged-only/native VLAN, hướng và nguồn mirror, peer hai đầu, khả năng quan sát khi failover, ngân sách RAM và tiêu chí thử. Hai trunk firewall không gộp LACP. Core chỉ chuyển mạch Layer 2; gateway, định tuyến liên VLAN, firewall rules và NAT đặt trên OPNsense.

### 2.19.2. Mẫu bridge và cổng VLAN

Các biến NIC_ACCESS30, NIC_TRUNK_PRIMARY và NIC_CAPTURE là ký hiệu cần thay sau khi xác minh, chưa được định nghĩa trong guest. Không chạy nguyên khối minh họa này trên hệ thống hiện tại. Mỗi lệnh tác động cấu hình đều cần được đối chiếu với mapping và phạm vi được duyệt trước khi chạy.

```sh
ovs-vsctl add-br br-core-l2
ovs-vsctl add-port br-core-l2 "$NIC_ACCESS30" -- set Port "$NIC_ACCESS30" vlan_mode=access tag=30
ovs-vsctl add-port br-core-l2 "$NIC_TRUNK_PRIMARY" -- set Port "$NIC_TRUNK_PRIMARY" vlan_mode=trunk trunks=30,40,50,60,99
```

Lệnh thứ nhất dự kiến tạo cầu nối OVS. Lệnh thứ hai gán một cổng vào VLAN 30 theo chế độ access. Lệnh thứ ba dự kiến cho trunk mang năm VLAN đã quy định. Các cổng access 40/50/60/99 và trunk Secondary phải được xác nhận độc lập; không suy ra peer từ mẫu này. Chưa gán địa chỉ IP hoặc gateway cho bridge. Cần kiểm thử loại bỏ lưu lượng untagged/VLAN ngoài danh sách theo chính sách chốt, thay vì mặc định coi danh sách trunk đã bao phủ mọi tình huống. [OVS Basic Configuration](https://docs.openvswitch.org/en/stable/faq/configuration/).

### 2.19.3. Mẫu mirror và giới hạn quan sát

Ví dụ dưới đây dự kiến sao chép toàn bộ lưu lượng đủ điều kiện trên bridge tới một cổng capture dành riêng. Phạm vi select-all chỉ là ví dụ để thảo luận; chưa chốt thay cho yêu cầu chọn nguồn/hướng. Khi triển khai có mirror sẵn, phải bổ sung giao dịch phù hợp để giữ các mirror hiện hữu.

```sh
ovs-vsctl add-port br-core-l2 "$NIC_CAPTURE"
ovs-vsctl -- --id=@cap get Port "$NIC_CAPTURE" -- --id=@mon create Mirror name=suricata-monitor select-all=true output-port=@cap -- set Bridge br-core-l2 mirrors=@mon
```

Giao dịch dự kiến tham chiếu port capture và gắn đối tượng Mirror vào bridge mới. Cổng output mirror không dùng làm cổng endpoint chuyển tiếp thông thường hoặc cổng quản trị Suricata. Suricata nhận bản sao hoạt động theo hướng IDS thụ động; nó không chặn được gói gốc bằng việc chỉ nhận mirror. Cần đo tỷ lệ mất gói khi mirror tổng hợp vượt tốc độ đầu ra, kiểm tra frame có thẻ VLAN, lưu lượng cùng VLAN không qua firewall và hiện tượng trùng gói. [OVS mirroring](https://docs.openvswitch.org/en/stable/faq/configuration/).

### 2.19.4. Tiêu chí nghiệm thu tiếp theo

| Bài kiểm thử dự kiến | Điều kiện đạt và minh chứng cần có | Trạng thái hiện tại |
|---|---|---|
| Mapping tám cổng | EVE/QEMU/Ubuntu khớp MAC, peer và network ID được ghi đầy đủ | Peer chưa xác minh |
| Access cùng VLAN | Hai endpoint cùng VLAN trao đổi được frame; lưu bảng MAC và capture | Chưa thử |
| Cách ly VLAN | Lưu lượng khác VLAN không đi trực tiếp qua Core; liên VLAN theo firewall | Chưa thử |
| Trunk | Capture xác nhận thẻ 30/40/50/60/99 và chính sách với untagged/VLAN lạ | Chưa thử |
| Mirror Suricata | NIC capture thấy đúng phạm vi/hướng; ghi số gói, tag và mất gói | Chưa thử |
| Khởi động lại | Cấu hình OVS được giữ sau restart trong đợt được duyệt riêng | Chưa thực hiện restart |
| HA firewall | Chuyển vai CARP, pfsync và duy trì quan sát; thuộc M3 | Chưa triển khai |
