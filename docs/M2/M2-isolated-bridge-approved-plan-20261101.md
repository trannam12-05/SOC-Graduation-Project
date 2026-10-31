# 2.28. Phạm vi được duyệt: cấu hình Core cô lập, chưa thực thi tại thời điểm lập kế hoạch

Người dùng phê duyệt tạo br-core-l2, năm access ens3–ens7 và hai trunk ens8/ens9 trên SOC-Core-L2; không nối link EVE, không bật VM, không cấp IP/gateway, không thay IPv4/IPv6 forwarding. Nội dung này thay phạm vi của mẫu M2-ovs-config-PROPOSED-20261101.txt: **bỏ ens10 và toàn bộ Mirror**. ens10 giữ nguyên thiết bị, MAC và trạng thái, không nằm trong bridge ở giai đoạn hiện tại.

## 2.28.1. Điều kiện trước thay đổi

Xác minh đúng hostname, UUID/QEMU từ host EVE, OVS 3.3.9 và ba dịch vụ active; tám MAC không đổi; không có OVS bridge/port/interface/mirror hoặc Linux interface trùng tên; các NIC chưa có IP; forwarding IPv4/IPv6 đều 0. Đọc cấu hình quản lý mạng để phát hiện rule có thể tự cấu hình bridge mới. Nếu có xung đột, dừng trước giao dịch.

## 2.28.2. Sao lưu và rollback

Trong guest, tạo thư mục /root/m2-isolated-20261101T0035 mode 0700. Dùng ovsdb-client backup qua socket OVS đang chạy để lưu ovsdb.before mode 0600, không đọc/ghi đĩa VM từ host. Đối chiếu schema snapshot với server, kiểm tra định dạng bằng ovsdb-tool compact trên **bản backup riêng**, ghi SHA-256 và giữ nguyên snapshot. Lưu các truy vấn cấu hình, link/address/route/forwarding trước thay đổi và một rollback.sh root-only.

Rollback dự kiến dùng ovsdb-client restore snapshot qua socket đang chạy, không cần dừng daemon hoặc VM; schema phải trùng, không dùng --force. Nếu lỗi sau giao dịch thì thực hiện restore và kiểm tra lại cấu hình rỗng ban đầu, mapping, route và forwarding. Restore có thể đổi UUID hàng OVSDB, nên đối chiếu cấu hình tương đương thay vì cam kết UUID không đổi. Bản backup có khả năng chứa cấu hình nhạy cảm trong trường hợp hệ thống mở rộng; giữ trong guest root-only, không đưa nội dung raw vào báo cáo hoặc log công khai. [Tài liệu ovsdb-client](https://www.openvswitch.org/support/dist-docs/ovsdb-client.1.html).

## 2.28.3. Thay đổi mạng bên trong guest đã duyệt

Một giao dịch OVSDB tạo bridge system/standalone, local Port VLAN 99 không IP, access ens3/30, ens4/40, ens5/50, ens6/60, ens7/99 và hai trunk ens8/ens9 chỉ mang 30,40,50,60,99. Không dùng may-exist; không tạo ens10 Port hoặc Mirror; không sửa mapping hoặc MAC vNIC. Không tạo controller hay bond/LACP.

Để giữ bridge không có IP khi bật interface nội bộ mới, đặt addrgenmode none **chỉ trên br-core-l2 mới tạo** trước khi bật; nếu kernel đã tự sinh địa chỉ IPv6 link-local trong thời gian tạo interface, chỉ loại bỏ link-local tự sinh trên interface mới đó. Không thay bất kỳ sysctl forwarding nào hoặc thiết lập IPv6 trên NIC cũ. Nếu thấy địa chỉ ngoài link-local tự sinh trên bridge mới thì coi là xung đột, rollback và báo cáo. Việc cấu hình này không chứng minh chính sách được duy trì sau reboot; chưa restart trong phạm vi hiện tại.

## 2.28.4. Kiểm chứng tĩnh sau giao dịch

Đọc show, Bridge, Port, Interface, Mirror; kiểm tra đúng một bridge, bảy port vật lý và một local port, đúng VLAN/mode/trunks, Interface.error rỗng và ofport hợp lệ. Đọc dpif/show và dump-flows để xác nhận datapath, cổng và NORMAL; kiểm tra bridge admin UP, địa chỉ và route không phát sinh, forwarding vẫn 0/0, ens10 nguyên trạng và ngoài OVS. Kiểm tra daemon, lưu ảnh console thật và log/JSON. Không gửi traffic thử hoặc tuyên bố switching, isolation, trunk, HA hoặc SPAN đã nghiệm thu.

Tình trạng khi lập kế hoạch: sudo cache trên guest đã hết hạn; chưa thực hiện prepare/apply. Người dùng được yêu cầu tự xác thực trên console bằng sudo -v, không cung cấp mật khẩu cho công cụ hoặc chat. Tài liệu này là kế hoạch chuẩn bị, không thay cho kết quả thực tế sau cấu hình.
