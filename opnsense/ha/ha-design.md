# Thiết kế OPNsense HA (M1)

## Phân biệt nội dung

M1 mô tả kiến trúc HA ở mức thiết kế, chưa triển khai hoặc kiểm thử. Hai firewall, CARP/pfsync/XMLRPC là yêu cầu/định hướng; chi tiết IP, cổng và mạng WAN/SYNC dưới đây chỉ ghi nhận khi Word có nêu, các phần thiếu không tự bổ sung.

## Thành phần và đường kết nối

| Thành phần/đường | Nội dung trong Word | Trạng thái |
|---|---|---|
| WAN | Đường WAN từ ISP cần được cung cấp tới cả hai firewall nếu muốn Primary và Secondary có thể dùng đường đó sau failover | Yêu cầu thiết kế; ISP, số đường, topology, interface và IP WAN chưa nêu |
| LAN | Mỗi OPNsense nối Core L2 bằng trunk 802.1Q; trunk mang VLAN 30, 40, 50, 60, 99 theo bảng cổng M1; tạo interface VLAN trên OPNsense | Mapping/các VLAN là đề xuất M1; cổng ở hai đầu và IP chưa xác nhận |
| SYNC | Mạng đồng bộ pfsync/XMLRPC được đặt tách biệt khỏi các VLAN người dùng | Yêu cầu thiết kế; interface, subnet, IP hai đầu, kết nối vật lý/ảo chưa nêu |
| CARP | VIP làm gateway chung trên các VLAN; M1 đề xuất `.1` VIP, `.2` Primary, `.3` Secondary trong từng subnet ví dụ | Địa chỉ và subnet là ví dụ M1, chưa xác nhận trên EVE-NG |
| pfsync | Đồng bộ trạng thái kết nối giữa hai firewall | Cơ chế được yêu cầu/đề xuất; interface và kiểm thử chưa nêu |
| XMLRPC | Hỗ trợ đồng bộ cấu hình HA | Cơ chế được nêu; endpoint, phạm vi, tài khoản và kiểm soát truy cập chưa nêu |

## Địa chỉ VLAN được Word đề xuất

| VLAN | Subnet ví dụ | CARP VIP ví dụ | Primary ví dụ | Secondary ví dụ |
|---:|---|---|---|---|
| 30 – Data Center | `192.168.30.0/24` | `192.168.30.1` | `192.168.30.2` | `192.168.30.3` |
| 40 – Employee | `192.168.40.0/24` | `192.168.40.1` | `192.168.40.2` | `192.168.40.3` |
| 50 – Guest | `192.168.50.0/24` | `192.168.50.1` | `192.168.50.2` | `192.168.50.3` |
| 60 – DMZ (đề xuất) | `192.168.60.0/24` | `192.168.60.1` | `192.168.60.2` | `192.168.60.3` |
| 99 – Management | `192.168.99.0/24` | `192.168.99.1` | `192.168.99.2` | `192.168.99.3` |

Tất cả địa chỉ trên được Word mô tả là ví dụ cho lab/đề xuất, không phải thông số đã xác nhận. Không có địa chỉ WAN hoặc SYNC được cung cấp.

## Vai trò dịch vụ

- OPNsense đảm nhiệm default gateway, định tuyến liên VLAN, firewall rules, NAT và DHCP (DHCP cho VLAN người dùng nếu cần).
- Gateway client dùng CARP VIP khi HA được thiết lập.
- Core Switch chỉ Layer 2, không làm gateway hoặc định tuyến giữa VLAN.
- Cần cung cấp WAN cho cả hai firewall theo topology cho phép tiếp quản sau failover.
- Cần mạng SYNC tách biệt cho pfsync/XMLRPC theo thiết kế M1.

## Thông tin HA còn thiếu cần chốt

- Interface/node/cổng và sơ đồ WAN; ISP giả lập hay upstream nào, subnet, IP, gateway và cách Secondary tiếp quản.
- Interface/node/cổng và subnet/IP riêng cho SYNC; xác nhận SYNC tách biệt như thế nào trong EVE-NG.
- IP/subnet chính thức cho các VLAN, VIP, IP Primary và Secondary; VLAN 60 có được duyệt không.
- Tham số CARP cần thiết và chính sách failover; Word chưa nêu các giá trị cấu hình cụ thể.
- Phiên bản OPNsense, interface mapping và hỗ trợ của image EVE-NG.
- Phạm vi đồng bộ XMLRPC, quyền truy cập quản trị và cách bảo vệ kênh đồng bộ.
- Kiểm thử failover cho gateway, WAN/NAT, trạng thái kết nối và SPAN/giám sát.
- Chính sách DHCP, DNS và các firewall rules/NAT cụ thể.

Các nội dung trên là đầu vào thiết kế. Chưa chạy lệnh cấu hình thiết bị và chưa thay đổi EVE-NG.
