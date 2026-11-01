# CHƯƠNG 3. THIẾT KẾ OPNsense VÀ KẾ HOẠCH TRIỂN KHAI TUẦN TỰ

## 3.1. Phạm vi và trạng thái

Bản thiết kế ngày 01/11/2026, UTC+07:00. **Toàn bộ nội dung M3 dưới đây là dự kiến, chưa triển khai hoặc kiểm thử.** Trong lần kiểm kê EVE lúc 07:57–07:58, chỉ thấy ba image Ubuntu, không có image/node OPNsense hoặc Suricata. Không tải image, không tạo hoặc bật firewall. Người dùng đang học Labtainer; mọi VM SOC phải giữ tắt cho đến khi người dùng thông báo tài nguyên sẵn sàng.

OPNsense là tên sản phẩm firewall; không tự khai triển tên này. Firewall đảm nhiệm gateway VLAN, định tuyến liên VLAN, lọc gói theo trạng thái và NAT. Core Ubuntu/Open vSwitch chỉ chuyển mạch Layer 2, không có IP/gateway. M1 chưa xác nhận địa chỉ; bảng dưới đây giữ địa chỉ ở dạng biến thay vì biến đề xuất thành cấu hình thực tế.

## 3.2. Phân chia cổng và địa chỉ dự kiến

| Thành phần | Primary | Secondary | Yêu cầu trước triển khai |
|---|---|---|---|
| LAN trunk | NIC riêng tới ens8 Core | NIC riêng tới ens9 Core | Xác minh tên interface/MAC thực tế; tạo hai segment riêng, không gộp trunk ngoài Core |
| VLAN | 30,40,50,60,99 trên NIC LAN | Cùng VLAN và thứ tự gán interface | Không bridge LAN/WAN; không dùng native VLAN cho trunk Core |
| WAN | NIC riêng, địa chỉ WAN-P | NIC riêng, địa chỉ WAN-S | Chưa chọn upstream; không tự nối pnet/NAT/VMware hoặc mạng thật |
| SYNC | NIC riêng, địa chỉ SYNC-P | NIC riêng, địa chỉ SYNC-S | Segment chỉ hai firewall, không nối Core hay sensor |
| Số NIC tối thiểu | 3: WAN/LAN trunk/SYNC | 3: WAN/LAN trunk/SYNC | Cổng quản trị dùng VLAN 99; thêm NIC quản trị chỉ khi có yêu cầu cụ thể |

| VLAN / vùng | Subnet | IP riêng Primary / Secondary | Gateway dự kiến cho client | Trạng thái |
|---|---|---|---|---|
| 30 / Data Center | DC_NET, cần chốt CIDR | DC_P / DC_S | DC_CARP_VIP | Chưa cấu hình |
| 40 / Employee | EMP_NET, cần chốt CIDR | EMP_P / EMP_S | EMP_CARP_VIP | Chưa cấu hình |
| 50 / Guest | GUEST_NET, cần chốt CIDR | GUEST_P / GUEST_S | GUEST_CARP_VIP | Chưa cấu hình |
| 60 / DMZ | DMZ_NET, cần chốt CIDR | DMZ_P / DMZ_S | DMZ_CARP_VIP | Chưa cấu hình |
| 99 / Management | MGMT_NET, cần chốt CIDR | MGMT_P / MGMT_S | MGMT_CARP_VIP | Chưa cấu hình |

Mỗi subnet cần ba địa chỉ khác nhau cho hai firewall và VIP, không nằm trong pool DHCP. Kiểm tra không trùng mạng EVE 192.168.220.0/24 hoặc các mạng Labtainer/VPN trước khi chốt. Không tự quét hoặc sửa mạng host. Khi chỉ chạy một firewall ở bản trình diễn tối thiểu, client tạm dùng địa chỉ interface của firewall đó; phải ghi rõ **single firewall, chưa HA**, không gọi địa chỉ này là CARP đã hoạt động.

## 3.3. Nguyên lý HA và các luồng đồng bộ

HA (High Availability, tính sẵn sàng cao) của cặp firewall cần ba cơ chế tách biệt. CARP (Common Address Redundancy Protocol, giao thức dự phòng địa chỉ chung) chọn firewall giữ VIP; pfsync là cơ chế đồng bộ trạng thái Packet Filter; XMLRPC (XML Remote Procedure Call, gọi thủ tục từ xa bằng XML) đồng bộ các mục cấu hình được chọn. Cấu hình dự kiến cho Primary có ưu tiên cao hơn; Secondary giữ vai trò BACKUP khi Primary bình thường. Không coi việc nhập cùng một VIP vào hai máy là HA đã đạt. [Tài liệu HA chính thức](https://docs.opnsense.org/manual/hacarp.html).

Trên từng VLAN, hai firewall phải trao đổi được CARP, dùng cùng VIP/VHID tương ứng và tránh trùng VHID ngoài cụm. CARP dùng IP protocol 112. SYNC dành cho pfsync và XMLRPC; chỉ cho phép hai IP peer trao đổi, kiểm tra cổng quản trị thực tế trước khi tạo rule XMLRPC. Đồng bộ cấu hình theo hướng Primary tới Secondary, không cấu hình đồng bộ ngược tự phát. Hai máy cần cùng phiên bản và ánh xạ interface tương ứng. Thông tin xác thực đồng bộ giữ riêng, không ghi vào Git hoặc báo cáo. [Hướng dẫn CARP/pfsync/XMLRPC](https://docs.opnsense.org/manual/how-tos/carp.html).

WAN HA cần upstream hỗ trợ địa chỉ và Layer 2 phù hợp. Nếu chỉ có một WAN DHCP chưa đánh giá khả năng CARP, chưa cam kết WAN failover hoặc NAT giữ phiên. Mẫu NAT dự kiến dùng WAN VIP làm địa chỉ nguồn khi WAN HA được chốt; chỉ xác minh bằng capture và phiên thật, không suy từ trạng thái MASTER/BACKUP.

## 3.4. Ma trận chính sách firewall dự kiến

Nguyên tắc đề xuất: mặc định chặn liên vùng, mở từng luồng có mục đích; lập alias theo subnet/server/port đã xác nhận. Rule xét tại interface nhận lưu lượng, có trạng thái cho luồng được phép. NAT không thay thế quyền truy cập; phải kiểm tra cả rule và state. [Nguyên lý firewall rules](https://docs.opnsense.org/manual/firewall.html).

| Nguồn | Đích | Chính sách dự kiến | Bằng chứng nghiệm thu cần có |
|---|---|---|---|
| Management | GUI/SSH firewall và server quản trị | Chỉ máy quản trị và cổng đã chốt; không mở cho toàn bộ VLAN khác | Rule, log, truy cập được từ máy quản trị và bị chặn từ Guest |
| Employee | Dịch vụ Data Center | Chỉ dịch vụ nghiệp vụ đã xác định | Đối chứng được phép/bị chặn theo port; capture và firewall log |
| Guest | Các mạng nội bộ | Chặn; cho DNS/DHCP được chỉ định và Internet khi WAN sẵn sàng | Không truy cập DC/DMZ/Management, Internet chỉ qua firewall |
| DMZ | Data Center / Management | Chặn mặc định; mở backend cụ thể khi có nhu cầu | Log luồng chặn và luồng backend được phép |
| Data Center | Internet | Chỉ cập nhật/dịch vụ cần thiết khi đã chốt | Rule/NAT/state và capture WAN |
| WAN | DMZ | Chỉ dịch vụ công bố và port-forward đã duyệt; còn lại chặn | Rule/NAT, log và thử từ nguồn WAN lab độc lập |
| SYNC-P | SYNC-S và chiều phản hồi | Chỉ đồng bộ pfsync/XMLRPC giữa peer | Capture SYNC, state được đồng bộ, không có client thường trên segment |
| Suricata capture | Bất kỳ mạng nào | Không IP/gateway, không dùng làm đường truyền dữ liệu | Mirror capture và phép thử ingress cổng mirror bị bỏ |

DHCP (Dynamic Host Configuration Protocol) cấp cấu hình địa chỉ/gateway/DNS cho client; chưa quyết định dịch vụ HA hoặc scope. Trình diễn M3 cơ bản nên dùng client thử địa chỉ tĩnh đã chốt để giảm biến số. Không bật hai DHCP độc lập cùng pool rồi coi là dự phòng.

## 3.5. Ngân sách và triển khai tuần tự trên Windows 16 GiB

Lúc 07:58 EVE có tổng 7897 MiB, available 6531 MiB, chưa có QEMU chạy. Windows khoảng 0,5 GiB available và sau đó thấp hơn; đây là số đo lịch sử, không phải quyền bật VM. Không tăng RAM EVE hoặc thay cấu hình VMware trong giai đoạn này.

Đề xuất chọn image amd64 DVD từ nguồn chính thức, đối chiếu SHA-256 và chữ ký trước khi dùng. Tài liệu OPNsense nêu mức RAM tối thiểu 3 GB; mức hợp lý 4 GB với SSD 40 GB. Dùng 3072/4096 MiB mỗi firewall để lập ngân sách lab bảo thủ; dung lượng đĩa phải đo lại trước khi tạo, không cộng trùng hai dòng df cùng filesystem. [Yêu cầu phần cứng](https://docs.opnsense.org/manual/hardware.html), [cài đặt và xác thực image](https://docs.opnsense.org/manual/install.html), [nguồn tải chính thức](https://opnsense.org/download/).

| Giai đoạn dự kiến | VM chạy đồng thời | Ngân sách khách | Điều kiện và kết quả có thể trình diễn |
|---|---|---|---|
| Hiện tại | Không VM SOC | 0 MiB | Chỉ tài liệu/script; Labtainer được ưu tiên |
| Hoàn tất M2 | Core | 2048 MiB | Người dùng xác nhận sẵn sàng, đo RAM; thử frame trên TAP, không thêm endpoint VM |
| Cài Primary | Một OPNsense; Core có thể giữ tắt trong bước cài | 3072–4096 MiB | Image chính thức đã xác thực, đủ đĩa và RAM host/EVE |
| Demo gateway tối thiểu | Core + Primary | 5120–6144 MiB | Cộng dự phòng EVE/Windows; cân nhắc client rất nhẹ hoặc công cụ đã có; chưa HA |
| Chuẩn bị Secondary tuần tự | Chỉ Secondary, Primary và Core tắt khi cài | 3072–4096 MiB | Ghi mapping, bản xuất cấu hình được giữ riêng; không chứng minh failover |
| Nghiệm thu HA | Core + hai firewall | Tối thiểu 8192 MiB, chưa tính EVE/sensor/client | Vượt tổng EVE 7897 MiB; chưa khả thi với phân bổ hiện có |

Chạy Primary rồi Secondary lần lượt chỉ chứng minh cài đặt/cấu hình từng máy, **không chứng minh HA, đồng bộ state hoặc chuyển VIP**. Cặp HA cần thêm tài nguyên được duyệt hoặc một môi trường lab khác phù hợp; một Core vẫn là điểm lỗi đơn dù firewall HA. Không đề xuất giảm firewall dưới yêu cầu để đổi lấy một ảnh nghiệm thu thiếu tin cậy.

## 3.6. Thứ tự triển khai và tiêu chí dừng

1. Sau thông báo tài nguyên sẵn sàng: hoàn tất M2 và persistence trước; đo lại Windows/EVE.
2. Chốt subnet/VIP, WAN lab cô lập, MAC và tên NIC; xác nhận dung lượng đĩa. Chưa có bước tự nối mạng thật.
3. Xác thực image chính thức rồi mới tạo Primary; sao lưu trước mỗi thay đổi quan trọng.
4. Thử một VLAN rồi năm VLAN: gateway, rule cho phép/chặn và log; giữ Core không IP/forwarding.
5. Chuẩn bị Secondary tuần tự; ghi rõ trạng thái chưa HA khi không chạy đồng thời.
6. Chỉ nghiệm thu HA khi đủ tài nguyên chạy cặp: xác minh MASTER/BACKUP, pfsync state, XMLRPC, ngắt Primary có kiểm soát, VIP tiếp quản và phiên có số đo gián đoạn; phục hồi vai trò sau thử.

Nếu thiếu image đã xác thực, RAM, đĩa, mapping WAN/SYNC hoặc nguồn/đích kiểm thử thì đánh dấu BLOCKED ở ca tương ứng, tiếp tục phần độc lập. Không bật thêm VM, thay firewall/NAT, tải image hoặc áp dụng kế hoạch trong chế độ nhẹ hiện tại.
