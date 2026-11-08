# Cập nhật M1 — 05/11/2026, UTC+07:00

Bản hiện hành: [Thiết kế hợp nhất](../../docs/M1/M1-design-consolidated-20261105.md). Năm VLAN, IP firewall .2/.3 và VIP .1 đã được nghiệm thu M3. Core dùng Open vSwitch ens3–ens10, không IP; LACP không áp dụng. Wazuh VLAN99 là thiết kế chưa triển khai. Internet ngoài phạm vi cơ sở. Nội dung dưới đây là trích xuất M1 gốc giữ làm lịch sử; không dùng trạng thái chưa xác nhận hoặc tên cổng IOS cũ thay bản hợp nhất.

---

# Kế hoạch VLAN và địa chỉ IP (M1)

## Quy ước trạng thái

- **Nêu trong Word – đề xuất M1:** giá trị xuất hiện trong báo cáo nhưng được ghi rõ là ví dụ/đề xuất, chưa xác nhận trên EVE-NG hoặc với quy hoạch chính thức của nhóm.
- **Nêu trong Word – yêu cầu thiết kế:** nguyên tắc có trong báo cáo; không đồng nghĩa đã cấu hình hoặc nghiệm thu.
- **Chưa nêu:** Word không cung cấp giá trị; để trống cho đến khi nhóm xác nhận.

Không có thông số địa chỉ nào được xác nhận là cấu hình chạy thực tế. Theo yêu cầu kiến trúc, Core Switch chỉ switching Layer 2; OPNsense đảm nhiệm gateway, định tuyến liên VLAN, firewall và NAT.

## Bảng VLAN và địa chỉ

| VLAN | Mục đích | Subnet | Mask | Gateway CARP VIP | OPNsense Primary | OPNsense Secondary | Trạng thái / ghi chú |
|---:|---|---|---|---|---|---|---|
| 30 | Data Center | `192.168.30.0/24` | `255.255.255.0` | `192.168.30.1` | `192.168.30.2` | `192.168.30.3` | Các địa chỉ là ví dụ M1, chưa xác nhận |
| 40 | Employee | `192.168.40.0/24` | `255.255.255.0` | `192.168.40.1` | `192.168.40.2` | `192.168.40.3` | Các địa chỉ là ví dụ M1, chưa xác nhận |
| 50 | Guest | `192.168.50.0/24` | `255.255.255.0` | `192.168.50.1` | `192.168.50.2` | `192.168.50.3` | Các địa chỉ là ví dụ M1, chưa xác nhận |
| 60 | DMZ | `192.168.60.0/24` | `255.255.255.0` | `192.168.60.1` | `192.168.60.2` | `192.168.60.3` | VLAN 60 và các địa chỉ đều là đề xuất M1 |
| 99 | Management | `192.168.99.0/24` | `255.255.255.0` | `192.168.99.1` | `192.168.99.2` | `192.168.99.3` | Các địa chỉ là ví dụ M1, chưa xác nhận |

Word quy hoạch `.1` làm CARP VIP, `.2` cho Primary và `.3` cho Secondary trên từng VLAN. Đây là phương án thiết kế minh họa, không phải địa chỉ đã được xác nhận. Word cũng nêu Core L2 chỉ có một địa chỉ quản trị trong VLAN 99; địa chỉ ví dụ `192.168.99.10` chưa được xác nhận.

## DHCP và DNS

| Hạng mục | Nội dung trích từ M1 | Trạng thái |
|---|---|---|
| Nơi đảm nhiệm DHCP | OPNsense; DHCP cho VLAN người dùng nếu cần | Nguyên tắc đề xuất, chưa triển khai |
| VLAN bật DHCP | Chưa chốt; M1 chỉ nói VLAN người dùng nếu cần | Cần xác nhận |
| Dải cấp phát / exclusion / reservation | Chưa nêu phạm vi DHCP. M1 đưa ví dụ máy chủ `.10–.30`, PC/Guest `.100–.199`, Web `.10`, DNS `.30`, nhưng đây là IP thiết bị ví dụ, không phải scope DHCP đã chốt | Chưa xác nhận; không suy ra scope |
| DNS server / địa chỉ DNS cấp cho client | Chưa nêu địa chỉ DNS. M1 có ví dụ DNS `.30` trong VLAN 60 nhưng không xác nhận đó là DNS resolver cho client | Cần xác nhận |
| Gateway và DNS do DHCP cấp | DHCP có thể cấp gateway và DNS theo phần giải thích khái niệm, nhưng giá trị cụ thể chưa chốt | Cần xác nhận |

## Vai trò định tuyến

OPNsense tạo interface VLAN trên LAN trunk, giữ CARP VIP làm default gateway, định tuyến giữa các VLAN và áp dụng firewall rules. NAT ra Internet xử lý trên OPNsense. Core L2 không tạo SVI làm gateway và không thực hiện inter-VLAN routing/ACL Layer 3.

## Cần xác nhận trước khi dùng

- Quy hoạch subnet/IP chính thức của nhóm, tránh trùng với các mạng hiện có.
- VLAN 60 có được chốt cho DMZ không; danh sách VLAN chính thức.
- VIP và IP riêng Primary/Secondary trên từng VLAN.
- VLAN nào cấp DHCP, scope, reservation, DNS resolver và các địa chỉ tĩnh loại trừ.
- WAN/transit, mạng HA sync và địa chỉ thiết bị trên các mạng này (không có trong bảng trên).
