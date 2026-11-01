# CHƯƠNG 3. MA TRẬN ĐỊA CHỈ VÀ CHECKLIST TRIỂN KHAI OPNsense

## 3.1. Phần bổ sung mới, chưa áp dụng

Tài liệu nối tiếp M3-OPNsense-HA-PROPOSED-20261101.md, không thay lịch sử. Bảng có địa chỉ cụ thể để giảm thao tác nhập sau này; mọi giá trị vẫn **DỰ KIẾN, CHƯA XÁC NHẬN/TRIỂN KHAI**. Nguồn VLAN là ví dụ M1 trong network/ip-plan/vlan-ip-plan.md; không tự cấp IP cho Core.

## 3.2. Ma trận đề xuất có thể kiểm tra bằng máy

| VLAN / vùng | Subnet dự kiến | Primary | Secondary | CARP VIP | DHCP dự kiến |
|---|---|---|---|---|---|
| 30 / Data Center | 192.168.30.0/24 | 192.168.30.2 | 192.168.30.3 | 192.168.30.1 | Chưa bật; ưu tiên server tĩnh |
| 40 / Employee | 192.168.40.0/24 | 192.168.40.2 | 192.168.40.3 | 192.168.40.1 | Đề xuất mới .100–.199, chưa duyệt scope |
| 50 / Guest | 192.168.50.0/24 | 192.168.50.2 | 192.168.50.3 | 192.168.50.1 | Đề xuất mới .100–.199, chưa duyệt scope |
| 60 / DMZ | 192.168.60.0/24 | 192.168.60.2 | 192.168.60.3 | 192.168.60.1 | Chưa bật |
| 99 / Management | 192.168.99.0/24 | 192.168.99.2 | 192.168.99.3 | 192.168.99.1 | Chưa bật; giữ IP quản trị xác định |
| SYNC riêng | 10.255.255.0/30 | 10.255.255.1 | 10.255.255.2 | Không cần VIP SYNC | Không DHCP |

SYNC /30 và scope DHCP là đề xuất bổ sung của đợt chuẩn bị, không nói rằng đã có trong M1. configs/M3/address-proposal.json là đầu vào duy nhất cho kiểm tra tĩnh địa chỉ; validate_m3_plan.py kiểm subnet chồng lấn, IP hợp lệ/khác nhau và pool không đè VIP. Kết quả design_checks_ok chỉ đánh giá tính nhất quán, luôn deployable=false vì chưa xác minh môi trường.

Còn phải chốt: xung đột Labtainer/VPN/lab khác; tên interface/MAC WAN-LAN-SYNC hai firewall; phiên bản image; WAN DHCP hay tĩnh, subnet/gateway/IP/VIP và upstream hỗ trợ CARP; DNS; backend DHCP và cơ chế HA phù hợp phiên bản; cổng GUI thực tế và chính sách quản trị. Không tạo cấu hình import XML đầy đủ khi các đầu vào này còn thiếu, không ghi config.xml hoặc bí mật đồng bộ vào Git.

## 3.3. Firewall policy theo vùng

| Vùng nguồn | Cho phép dự kiến | Chặn mặc định | Điều kiện trước áp dụng |
|---|---|---|---|
| Data Center | DNS/NTP/cập nhật tới đích xác định; log tới SOC khi có collector | DC tới Management/DMZ ngoài dịch vụ được chốt | IP server, DNS/NTP/collector và port cụ thể |
| Employee | Dịch vụ nghiệp vụ DC đã chọn, DNS/DHCP cần thiết, WAN nếu được phép | GUI firewall/Management, dịch vụ nội bộ không được giao | Alias server/port, nguồn quản trị ngoại lệ |
| Guest | DNS/DHCP chỉ định và WAN sau khi WAN thật sự sẵn sàng | Toàn bộ VLAN nội bộ và quản trị firewall | DNS resolver và địa chỉ internal alias; kiểm cả IPv6 nếu bật |
| DMZ | Backend DC cụ thể và log/cập nhật khi cần | Kết nối khởi tạo tới DC/Management ngoài allowlist | IP/port backend và luồng giám sát |
| Management | GUI/SSH từ máy quản trị, quản lý sensor/server xác định | Máy không phải quản trị truy cập các cổng điều khiển | IP máy quản trị, chống tự khóa console/GUI |
| WAN | Chỉ dịch vụ DMZ công bố bằng rule/NAT được duyệt | Mọi inbound khác | Upstream cô lập và nguồn thử bên WAN |
| SYNC | pfsync và XMLRPC giữa đúng hai peer | Client khác, đi sang WAN/VLAN người dùng | NIC riêng, cổng HTTPS thực tế, không sync cấu hình ngược |

Rule có trạng thái đặt theo interface nhận lưu lượng; cần kiểm tra thứ tự, log và state cũ khi thử thay đổi. NAT không làm nhiệm vụ phân quyền liên VLAN. Không dùng allow-any liên vùng để đạt một phép ping. Ma trận là ý định chính sách, chưa phải bộ rule đã nhập. [Tài liệu firewall chính thức](https://docs.opnsense.org/manual/firewall.html).

## 3.4. Quy trình Primary trước, Secondary sau

1. Sau khi đủ tài nguyên: hoàn tất M2, xác thực image chính thức và đo đĩa. Cài duy nhất Primary khi Core có thể tắt, không tải image trong đợt này.
2. Xác minh MAC/tên NIC, cấu hình console/GUI quản trị có đường phục hồi; sao lưu root-only. Chốt WAN lab riêng, không tự đụng mạng Windows/VMware.
3. Nối LAN Primary riêng tới ens8 theo mapping đã duyệt, tạo một VLAN rồi đủ năm VLAN; thử rule/gateway bằng client thử nhẹ. Ở bản một firewall, gateway client dùng IP interface Primary tạm thời, không giả làm VIP HA.
4. Chuẩn bị Secondary tuần tự, Primary tắt trong bước cài nếu thiếu RAM. Cùng phiên bản/interface assignment; giữ hai địa chỉ riêng. Chưa gọi là HA khi không chạy đồng thời.
5. Chỉ khi có tài nguyên được duyệt mới chạy hai firewall + Core; tạo CARP VIP, pfsync trên SYNC, XMLRPC Primary→Secondary có chọn mục đồng bộ. DHCP HA là kiểm thử riêng, không suy từ sync rule. [CARP/pfsync/XMLRPC](https://docs.opnsense.org/manual/how-tos/carp.html).

## 3.5. Checklist nghiệm thu, tất cả NOT_RUN

| ID | Mục tiêu và thao tác tương lai | Đối chứng/kết quả cần thấy | Bằng chứng |
|---|---|---|---|
| M3-01 | Phiên bản/NIC: collect readonly trên từng firewall, đối chiếu cổng/MAC | Đúng image, WAN/LAN/SYNC, không bridge sai | version/interfaces/routes, ảnh GUI assignment |
| M3-02 | Inter-VLAN: thử một dịch vụ được phép và một bị chặn | Đi qua gateway OPNsense; capture hai VLAN; rule/log khớp, Core vẫn không IP | PCAP hai phía, rule ID, log/state |
| M3-03 | CARP: chạy cặp, xem vai trò/VIP mỗi VLAN | Một MASTER/một BACKUP; protocol112 qua đúng VLAN; không split-brain | ifconfig/GUI VIP, capture CARP, boot/time |
| M3-04 | pfsync: tạo một phiên thật, xem state hai máy | State tương ứng trên peer SYNC, không chỉ dịch vụ active | State chọn lọc đã ẩn dữ liệu, PCAP SYNC |
| M3-05 | XMLRPC: thêm rule thử vô hại trên Primary, sync mục đã chọn | Secondary có cấu hình tương ứng; IP/role riêng không bị đảo | Ảnh rule trước/sau, log sync; không chụp credentials |
| M3-06 | Failover: giữ phiên liên tục, ngắt Primary có kiểm soát | VIP chuyển Secondary, đo mất gói/thời gian và state giữ hay mất | Timeline UTC+07:00, ping/phiên/log/pcap, không chỉ ảnh MASTER |
| M3-07 | DHCP: chọn backend đúng phiên bản, release/renew client trong VLAN40/50 | Đúng pool, mask, DNS, gateway; VIP/IP node không bị cấp | DORA/lease/client config, log DHCP |
| M3-08 | DHCP HA riêng khi đủ cặp | Không hai pool độc lập trùng nhau; renew hoạt động theo cơ chế đã cấu hình | Lease hai máy, log, thử khi Primary dừng |
| M3-09 | NAT: mở phiên outbound tới đích WAN lab, thử inbound DMZ nếu được duyệt | Địa chỉ/port trước-sau đúng; NAT failover dùng WAN VIP chỉ khi upstream hỗ trợ | PCAP LAN/WAN, NAT/rule/state, đối chứng không NAT nếu phù hợp |
| M3-10 | Phục hồi | Bật lại Primary đúng quy trình, vai trò không dao động; các rule vẫn đúng | CARP timeline, state, phép thử lại luồng đã cho/chặn |

DHCP hiện có nhiều lựa chọn backend theo phiên bản; không mang hướng dẫn ISC cũ sang mặc định mới mà chưa kiểm tra. [Tài liệu DHCP](https://docs.opnsense.org/manual/dhcp.html). automation/m3_collect_readonly.sh chỉ thu thông tin không thay cấu hình; không kết luận các ca này đạt từ output inventory. Chưa chạy script trên firewall.
