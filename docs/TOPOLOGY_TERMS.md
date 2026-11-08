# 1. Thuật ngữ phục vụ mô hình SOC

## 1.1. Mạng và phân vùng

| Khái niệm và tên chính thức | Nghĩa tiếng Việt, nguyên lý | Vai trò và ví dụ trong đồ án |
|---|---|---|
| SOC — Security Operations Center | Trung tâm điều hành an ninh; phối hợp con người, quy trình và công cụ để thu thập, phân tích và xử lý sự kiện. | Là mục tiêu tổng thể của đồ án. Khối Wazuh/SOC trong M1 mới là kiến trúc; tạo node không chứng minh SOC vận hành. |
| VLAN — Virtual Local Area Network | Mạng LAN ảo; chia miền quảng bá Layer 2 theo định danh VLAN. Frame khác VLAN cần đi qua thiết bị Layer 3 để liên lạc. | VLAN 30/40/50/60/99 tương ứng Data Center/Employee/Guest/DMZ/Management. Cấu hình và các ca frame M2 đã có minh chứng riêng. |
| IEEE 802.1Q | Tiêu chuẩn cầu nối và mạng có cầu nối của IEEE; thẻ VLAN trong frame Ethernet cho phép nhận diện miền VLAN trên đường mang nhiều VLAN. Đây là tên tiêu chuẩn, không phải chữ viết tắt tự khai triển. | Hai trunk Core–firewall dự kiến mang VLAN 30/40/50/60/99; mapping Core đã có bằng chứng M2, gateway trên firewall chưa được suy là đã hoạt động. |
| Trunk | Cổng/đường truyền mang nhiều VLAN; frame được phân loại theo thẻ và chính sách VLAN của cổng. Cần thống nhất VLAN được phép và cách xử lý frame không gắn thẻ ở hai đầu. | Core e5/ens8 tới Primary LAN và e6/ens9 tới Secondary LAN. Hai segment riêng, không nối WAN hoặc SYNC vào trunk người dùng. |
| Access port | Cổng truy cập thuộc một VLAN; frame từ endpoint thường không gắn thẻ và được switch phân loại vào VLAN access. | Core e0–e4 lần lượt phục vụ năm vùng. Đây là mapping guest M2 được giữ lại khi dựng dây EVE. |
| LACP — Link Aggregation Control Protocol | Giao thức điều khiển gộp liên kết; hai đầu thương lượng thành viên của một nhóm liên kết logic nhằm phân phối lưu lượng và dự phòng. | Không triển khai LACP xuyên hai firewall độc lập. M1 nhắc dự phòng Core như phương án mở rộng; đợt này vẫn chỉ một Core. |
| SPAN — Switched Port Analyzer | Tên cơ chế sao chép lưu lượng quan sát thường dùng trong thiết bị Cisco; cấu hình nguồn, hướng và cổng đích để đưa bản sao tới thiết bị phân tích. | M1 yêu cầu SPAN cho Suricata. Core thực tế dùng tính năng Mirror của OVS, không chạy lệnh SPAN của Cisco. |
| Port mirroring | Sao chép frame từ các cổng/VLAN được chọn sang cổng quan sát; bản sao phục vụ phân tích, không phải đường định tuyến gốc. | M2 đã kiểm chứng output ens10 và chiều ingress đã chọn. Node Suricata nối NIC capture tới Core e7; đây là dây mới, không tự suy toàn pipeline đã VERIFIED. |
| Bridge | Cầu nối Layer 2; học địa chỉ MAC, chuyển frame và quản lý miền quảng bá theo khả năng triển khai. | Phải phân biệt bridge EVE dùng làm segment nối dây với bridge OVS trong guest Core. Các segment WAN EVE cô lập không đồng nghĩa có Internet. |
| OVS — Open vSwitch | Tên sản phẩm switch phần mềm; cấu hình qua cơ sở dữ liệu OVSDB, thực hiện chuyển frame trong datapath với port, VLAN và Mirror. | Ubuntu Core chạy br-core-l2; OVS đã cài và kiểm chứng M2. Không cài lại OVS hoặc biến Core thành gateway khi bổ sung node. |

Nguyên lý access và mirror trên OVS được đối chiếu với [tài liệu chính thức Open vSwitch](https://docs.openvswitch.org/en/latest/faq/configuration/). Phiên bản tài liệu trực tuyến có thể mới hơn OVS 3.3.9 của Core; cấu hình thực tế dựa trên minh chứng M2, không suy khả năng phiên bản từ tài liệu mới.

## 1.2. Ảo hóa và khởi tạo máy

| Khái niệm và tên chính thức | Nghĩa tiếng Việt, nguyên lý | Vai trò và ví dụ trong đồ án |
|---|---|---|
| QEMU | Tên phần mềm giả lập và ảo hóa; trình bày CPU, đĩa và thiết bị mạng ảo cho guest. Không tự tạo dạng khai triển cho tên sản phẩm. | EVE điều phối tiến trình QEMU cho Ubuntu và OPNsense. UUID, MAC và TAP phải đối chiếu trước thao tác; node tạo trên GUI chưa chứng minh guest đã boot. |
| QCOW2 — QEMU Copy On Write version 2 | Định dạng đĩa ảo hỗ trợ cấp phát theo nhu cầu và backing file; overlay lưu phần thay đổi so với đĩa nền. | Các Linux mới dùng overlay riêng từ Ubuntu nền. Không lấy overlay Core đã cấu hình để nhân bản dịch vụ. Primary/Core đã được sao lưu và đối chiếu SHA-256 trước thay đổi topology. |
| cloud-init | Tên phần mềm khởi tạo Linux; đọc dữ liệu nguồn, cấu hình tài khoản/mạng và chạy tác vụ theo các giai đoạn boot. | Seed riêng của mỗi node mới chuẩn bị hostname, khóa SSH và tên NIC theo MAC. Seed đã tạo khác với tác vụ trong guest đã chạy thành công; phải xem kết quả và boot_id. |
| NoCloud | Tên datasource của cloud-init; lấy user-data, meta-data và tùy chọn network-config từ nguồn cục bộ hoặc đường dẫn được chỉ định. | ISO có volume label cidata của các Linux mới cung cấp dữ liệu khởi tạo offline. Seed Core cũ được giữ nguyên. |
| SSH — Secure Shell | Giao thức truy cập từ xa có mã hóa và xác thực, thường dùng khóa công khai để chứng minh quyền truy cập. | Windows dùng khóa ngoài repository để truy cập root EVE. Khóa riêng/passphrase không nằm trong minh chứng; SSH host EVE khác với SSH tới guest. |

Cơ chế seed và instance-id được tham chiếu từ [NoCloud — cloud-init](https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html). Trong lab cô lập, Linux mới dùng tài khoản soc-admin với SSH bằng khóa, khóa đăng nhập mật khẩu và console EVE tự đăng nhập để thực thi/thu minh chứng; đây là cấu hình dành cho môi trường mô phỏng có kiểm soát truy cập EVE, không phải kết quả kiểm chứng an toàn cho hệ thống sản xuất.

## 1.3. Firewall và dự phòng

| Khái niệm và tên chính thức | Nghĩa tiếng Việt, nguyên lý | Vai trò và ví dụ trong đồ án |
|---|---|---|
| OPNsense | Tên chính thức nền tảng firewall; xử lý lưu lượng theo interface, bảng trạng thái và bộ quy tắc. Không có dạng khai triển tự tạo. | Đảm nhiệm gateway, inter-VLAN routing, firewall rules và NAT. Primary đã có bằng chứng cài ổ từ M3; thêm dây không xác nhận gateway/HA. |
| HA — High Availability | Tính sẵn sàng cao; dùng thành phần dự phòng và cơ chế phát hiện/chuyển vai để giảm gián đoạn khi xảy ra lỗi. | Cặp Primary/Secondary là thiết kế HA. Cần kiểm tra chuyển vai và lưu lượng thực tế; hai biểu tượng firewall không đủ để kết luận HA đạt. |
| CARP — Common Address Redundancy Protocol | Giao thức dự phòng địa chỉ chung; các thành viên trao đổi thông báo và bầu thiết bị giữ địa chỉ ảo. | Dự kiến VIP .1 mỗi VLAN, Primary .2 và Secondary .3 theo M1. Chưa mặc định VIP hoạt động khi mới dựng topology. |
| pfsync | Tên giao thức đồng bộ trạng thái của Packet Filter; trao đổi thông tin trạng thái kết nối giữa các thành viên. Không tự đặt dạng khai triển chữ cái. | Dự kiến sử dụng mạng SYNC riêng trên vtnet2. Có dây SYNC chưa chứng minh trạng thái kết nối đã được đồng bộ. |
| NAT — Network Address Translation | Biên dịch địa chỉ mạng; thay đổi địa chỉ và có thể cả cổng trong gói, theo dõi ánh xạ để xử lý lưu lượng trả về. | Dự kiến outbound NAT qua OPNsense và công bố dịch vụ DMZ nếu có policy. Bridge WAN cô lập chưa có upstream nên chưa thể nghiệm thu NAT Internet. |
| DHCP — Dynamic Host Configuration Protocol | Giao thức cấp tham số mạng động; máy chủ cấp lease gồm địa chỉ, subnet, gateway và các tùy chọn như DNS. | M1 đề xuất cấp động cho Employee/Guest. Chưa suy có DHCP server/scope hoạt động từ tên VLAN hay từ dải IP dự kiến. |

Vai trò CARP và cơ chế dự phòng được đối chiếu với [High Availability — OPNsense](https://docs.opnsense.org/manual/hacarp.html). Các chức năng này vẫn cần được kiểm chứng trong đúng lab và phiên bản đang cài.

## 1.4. Phát hiện và phân tích sự kiện

| Khái niệm và tên chính thức | Nghĩa tiếng Việt, nguyên lý | Vai trò và ví dụ trong đồ án |
|---|---|---|
| IDS/IPS — Intrusion Detection System / Intrusion Prevention System | Hệ thống phát hiện/ngăn chặn xâm nhập; phân tích gói, luồng và quy tắc để phát cảnh báo hoặc thực thi hành động chặn khi triển khai ở vị trí cho phép. | Sensor nối bản sao lưu lượng của Core là IDS thụ động; không được gọi là IPS chặn inline chỉ vì Suricata hỗ trợ tính năng đó. |
| Suricata | Tên chính thức công cụ phân tích lưu lượng mạng; giải mã giao thức, theo dõi luồng và so khớp quy tắc để phát cảnh báo/log. | NIC capture0 dự kiến không IP, NIC mgmt0 tách biệt. Rule SID 1000001 trong repo dùng marker ICMP vô hại; chỉ khi có alert thật tương ứng mới xác nhận phát hiện, không suy từ service active. |
| Wazuh | Tên chính thức nền tảng giám sát an ninh; agent gửi dữ liệu tới thành phần phân tích, indexer phục vụ lưu/tìm kiếm và dashboard trình bày kết quả. | M1 có khối Wazuh/SOC. Node đã tạo không chứng minh đã có server/indexer/dashboard; vị trí NIC/VLAN chưa rõ nên không tự nối vào một VLAN. |

Phân biệt kiểm tra cấu hình, đọc PCAP offline và capture live theo [Suricata 7.0.3 — Command Line Options](https://docs.suricata.io/en/suricata-7.0.3/command-line-options.html). Cấu hình YAML theo [Suricata 7.0.3 — Suricata.yaml](https://docs.suricata.io/en/suricata-7.0.3/configuration/suricata-yaml.html). Thành phần nền tảng Wazuh đối chiếu [Wazuh components](https://documentation.wazuh.com/current/getting-started/components/index.html). Các ví dụ triển khai phải đọc cùng trạng thái và minh chứng trong báo cáo bàn giao, không dùng phần giải thích thuật ngữ thay cho kết quả nghiệm thu.
