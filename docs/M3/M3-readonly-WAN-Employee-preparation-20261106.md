# 3.13. Chuẩn bị Employee Linux và xác minh chuyển WAN — chỉ đọc

## 3.13.1. Kết luận
M3 PARTIAL; bước WAN/NAT BLOCKED. Không sửa topology, network, HA hoặc hook; không tạo/bật/dừng node, clone disk, cài gói hay gửi HTTPS. Giữ PASS trước. Đây là chuẩn bị tài liệu và script local, không phải Employee Linux đã triển khai.

## 3.13.2. Mapping WAN đã xác minh
Inventory hiện tại: Primary node1, Secondary node2; cả hai WAN là interface1/vtnet1 vào network4 WAN-ISP-1. TAP tương ứng vunl0_1_1 và vunl0_2_1 cùng master vnet0_4. pnet0 có192.168.220.143/24. Không suy node ID từ tên ảnh hoặc báo cáo cũ; phải đọc lại mapping/QEMU cmdline ngay trước thi hành.

API connectNode→linkInterface→Interfc.edit trong bằng chứng preflight3.12 chỉ sửa metadata, không tự chuyển TAP runtime. Ứng viên chuyển live là reattach CHỈ hai TAP WAN sang pnet0 và đồng thời cập nhật metadata sang một network pnet0 mới, giữ nguyên bridge cũ; rollback trả đúng hai TAP về vnet0_4 và khôi phục metadata trước thay đổi. Không di chuyển eth0 của host, không gán IP cho bridge, không chạm trunk/SYNC/Core; không chỉ sửa XML rồi báo link live đã đổi.

Đã xác minh mapping nhưng CHƯA thực nghiệm tính an toàn của thao tác live, DHCP hoặc tác động HA. Không kết luận phải stop VM; cũng không hứa zero downtime. Bước tiếp theo cần duyệt kế hoạch triển khai có backup cả XML và bridge membership, khóa chống chỉnh đồng thời, guard topology/hash/QEMU PID/mapping, kiểm tra pnet0 route trước/sau, rollback tự động nếu không có hai lease/gateway hợp lệ hoặc xuất hiện sai lệch HA. Nếu phương thức không được hỗ trợ hoặc cần node stop/restart, dừng xin duyệt riêng. Không thực hiện trong lượt chỉ đọc này.

## 3.13.3. Chuẩn bị Employee Linux
Employee node5 hiện là VPCS trên network7 VLAN40, không phải Linux. Đã tìm thấy image linux-ubuntu-24.04-soc-console-test, backing về linux-ubuntu-24.04-ovs/virtioa.qcow2. qemu-img info backing chain đọc thành công; metadata không báo corrupt/dirty. Điều đó không chứng minh guest sạch, boot được hoặc có HTTPS client. Không clone trực tiếp từ disk Core/DC/DMZ đang dùng và không sửa backing image chung.

Đề xuất SAU PHÊ DUYỆT: tạo Employee-Linux riêng từ image/bản clone độc lập đã xác minh nội dung, dự kiến1vCPU/1GiB RAM và một NIC nối network7 sẵn có, không đổi Core hoặc VPCS cũ. Kiểm tra tài nguyên/khả năng boot trước khi chốt. Dùng seed NoCloud riêng, hostname/machine identity riêng; NIC DHCP, không đặt IP/gateway tĩnh. Vì base có tên OVS, cần kiểm tra loại bỏ nguy cơ kế thừa role, netplan tĩnh, OVS bridge/service hoặc forwarding ngoài ý muốn trước nối VLAN; không mặc định image sạch từ tên.

Script automation/employee_linux_readonly_preflight.sh đã chuẩn bị, chưa chạy: đọc hostname/IP/route và kiểm tra curl hoặc Python3 ssl sẵn có, không thử mạng. Nếu thiếu client/CA hoặc IP/gateway đúng VLAN40 thì BLOCKED; không tự cài gói. Chỉ sau khi node được duyệt tạo/bật, lease được xác minh và WAN/NAT đã cấu hình mới dùng một HTTPS đến1.1.1.1 TCP443 theo quyền đã có. Không tự cấp lại IP .40.110 của VPCS hoặc giả nguồn từ host/firewall.

## 3.13.4. Điều kiện tiếp tục và minh chứng
Cần phê duyệt tạo/bật Employee-Linux và nguồn image/seed cụ thể, nối một NIC network7; riêng WAN cần duyệt cách cập nhật runtime+metadata và rollback có guard. Phê duyệt cũ về upstream/NAT không tự áp dụng cho việc thêm Linux node. Không tái nghiệm thu mục PASS; chỉ xác minh các điều kiện mới.

Minh chứng mới: docs/evidence/M3/M3-readonly-WAN-Employee-20261106/inventory.json và linux-image-chain.json; danh mục evidence-index.csv. Dùng lại code-path/API trong M3-NAT-deployment-20261106. Không có ảnh lab mới vì chỉ đọc inventory/metadata qua SSH; không báo node/HTTPS hoặc chuyển WAN đã hoàn thành.
