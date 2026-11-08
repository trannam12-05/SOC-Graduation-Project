# CHƯƠNG 1. THIẾT KẾ MÔ HÌNH SOC TRONG LAB NỘI BỘ

## 1.1. Phạm vi và căn cứ thiết kế

Bản hợp nhất ngày 05/11/2026, múi giờ UTC+07:00. Người dùng lựa chọn lab nội bộ trước; kết nối Internet là phần mở rộng dự kiến. Tài liệu này bổ sung bản Word M1 gốc, không thay đổi hay xóa tài liệu và minh chứng cũ. Đây là thiết kế có thể triển khai; không phải biên bản xác nhận toàn bộ topology đã được cấu hình trên EVE-NG.

Mục tiêu là phân vùng mạng, định tuyến có kiểm soát qua OPNsense, giám sát bản sao lưu lượng bằng Suricata và phân tích sự kiện bằng Wazuh. Core chỉ chuyển mạch Layer 2, không đặt IP quản trị, không làm gateway, không có SVI định tuyến hoặc ACL Layer 3. Quản trị Core dùng console EVE trong phạm vi lab. VLAN 99 phục vụ các thành phần quản trị khác.

Căn cứ nội bộ: AGENTS.md; báo cáo M2 ngày 03/11; nghiệm thu M3.1–M3.4; kiểm kê cấu trúc topology ngày 02/11; báo cáo Wazuh/replay ngày 02/11. Các kết quả này có thời điểm riêng, không xác nhận runtime ngày 05/11. Không SSH, bật/tắt node hoặc thay đổi hệ thống trong đợt hợp nhất hồ sơ.

## 1.2. Danh mục thành phần và số lượng

| Thành phần | Số node | Vai trò và trạng thái |
|---|---|---|
| SOC-Core-L2 | 1 | Ubuntu/Open vSwitch; chuyển mạch, access/trunk và mirror đã nghiệm thu M2 |
| OPNsense-Primary, OPNsense-Secondary | 2 | Gateway, firewall và HA; CARP/pfsync đã nghiệm thu trong phạm vi M3 |
| Data-Center | 1 | Endpoint đại diện VLAN 30; HTTP TCP8000 đã kiểm chứng, không suy thành máy chủ sản xuất |
| Employee | 1 | Endpoint đại diện VLAN 40; VPCS cho kiểm tra đơn giản, client Linux tạm dùng trong bài HTTP riêng |
| Guest | 1 | Endpoint đại diện VLAN 50; chưa nghiệm thu chính sách ứng dụng đầy đủ |
| DMZ | 1 | Endpoint đại diện VLAN 60; Web/DNS bổ sung không thuộc cấu hình đã nghiệm thu |
| Management | 1 | Endpoint đại diện VLAN 99 |
| Suricata-NIDS | 1 | Hai NIC tách capture và quản trị; có cảnh báo marker thật lịch sử |
| Wazuh-SOC | 1 | Manager đã xử lý replay; thiết kế nối vào VLAN 99, chưa có minh chứng kết nối này |

Tổng cộng 10 node trong thiết kế cơ sở. Mỗi vùng có một endpoint đại diện, không yêu cầu một node cho từng dịch vụ Web/DNS. Automation là thành phần logic, chưa ấn định máy chạy hay tạo node thứ 11; vị trí triển khai được chốt tại giai đoạn tích hợp. Thiết kế không yêu cầu bật đồng thời toàn bộ node; phải đo lại tài nguyên trước mỗi cửa sổ triển khai.

## 1.3. Sơ đồ và quy ước trạng thái

Sơ đồ nguồn có thể chỉnh sửa: network/topology/M1-internal-lab-20261105.mmd. Nét liền biểu diễn kết nối đã được ghi nhận trong hồ sơ; nét đứt biểu diễn đường nối hoặc tích hợp dự kiến. Sơ đồ là bản vẽ thiết kế, không phải ảnh chụp EVE-NG.

Hình 1.1. Kiến trúc lab nội bộ, Core L2, cặp OPNsense và khối giám sát (xem tệp Mermaid kèm theo).

Mục đích của hình là xác định ranh giới L2/L3 và tách đường capture khỏi đường vận chuyển log. Nội dung gồm năm vùng VLAN, hai trunk firewall, đường SYNC riêng và Wazuh dự kiến trên VLAN 99. Kết quả đối chiếu cho thấy cấu trúc lõi có minh chứng, còn kết nối Wazuh và đường log live chưa được nghiệm thu. Ý nghĩa là cung cấp đích triển khai thống nhất, tránh diễn giải mũi tên log như dây capture hoặc kết luận tích hợp đã hoàn thành.

## 1.4. Quy hoạch VLAN, IP và gateway

| VLAN | Vùng | Subnet | CARP VIP | Primary | Secondary |
|---|---|---|---|---|---|
| 30 | Data Center | 192.168.30.0/24 | 192.168.30.1 | 192.168.30.2 | 192.168.30.3 |
| 40 | Employee | 192.168.40.0/24 | 192.168.40.1 | 192.168.40.2 | 192.168.40.3 |
| 50 | Guest | 192.168.50.0/24 | 192.168.50.1 | 192.168.50.2 | 192.168.50.3 |
| 60 | DMZ | 192.168.60.0/24 | 192.168.60.1 | 192.168.60.2 | 192.168.60.3 |
| 99 | Management | 192.168.99.0/24 | 192.168.99.1 | 192.168.99.2 | 192.168.99.3 |

IP firewall và VIP trên năm VLAN đã được kiểm chứng ở M3, không còn chỉ là ví dụ M1. Thiết kế dùng VIP làm gateway cho endpoint. Không suy ra mọi endpoint hiện đã chuyển default route sang VIP: Data-Center giữ default route .30.2 trong bài M3.4, chỉ có host route riêng .40.100/32 qua .30.1 để kiểm thử.

SYNC dùng 10.255.255.0/30: Primary vtnet2 = 10.255.255.1, Secondary vtnet2 = 10.255.255.2; đã kiểm chứng. Không dùng SYNC làm đường người dùng hoặc đường log.

| Endpoint | Địa chỉ thiết kế | Mức xác nhận |
|---|---|---|
| Data-Center | 192.168.30.10/24 | Đã có minh chứng HTTP |
| Employee | 192.168.40.100/24 | Đã dùng làm nguồn test; không xác nhận VPCS đã cấu hình, tránh bật trùng client tạm |
| Guest | 192.168.50.100/24 | Dự kiến, kiểm tra trùng trước triển khai |
| DMZ | 192.168.60.10/24 | Quy hoạch thiết kế, chưa dùng làm kết luận dịch vụ đạt |
| Management | 192.168.99.100/24 | Quy hoạch thiết kế |
| Suricata quản trị | 192.168.99.20/24 | Đề xuất đích thiết kế; phải đối chiếu cấu hình hiện có trước thay đổi |
| Wazuh-SOC | 192.168.99.30/24 | Đề xuất mới; chưa nối NIC hoặc cấu hình IP |
| Suricata capture / Core | Không IP | Capture thụ động; Core giữ Layer 2 |

DHCP chưa triển khai: trước mắt dùng IP tĩnh cho lab. Dự kiến chỉ cấp DHCP cho Employee/Guest, dải .110–.199 để tránh .100 dùng thử; gateway là VIP tương ứng. DNS, lease và cơ chế DHCP HA phải chốt ở M3 trước khi bật dịch vụ; không dùng .60.30 làm DNS khi chưa có máy chủ thực. DNS không phải điều kiện cho bài HTTP nội bộ dùng IP trực tiếp.

## 1.5. Ánh xạ cổng và phân đoạn

| Core EVE / guest | Đích EVE / guest | Chức năng |
|---|---|---|
| e0 / ens3 | Data-Center e0 | Access VLAN 30 |
| e1 / ens4 | Employee e0 | Access VLAN 40 |
| e2 / ens5 | Guest e0 | Access VLAN 50 |
| e3 / ens6 | DMZ e0 | Access VLAN 60 |
| e4 / ens7 | Segment Management | Access VLAN 99; Management e0, Suricata e1; Wazuh e0 dự kiến bổ sung |
| e5 / ens8 | Primary e0 / vtnet0 | Trunk tagged 30,40,50,60,99 |
| e6 / ens9 | Secondary e0 / vtnet0 | Trunk tagged 30,40,50,60,99 |
| e7 / ens10 | Suricata e0 / capture | Output mirror riêng, không IP |

Primary e2/vtnet2 và Secondary e2/vtnet2 nối segment SYNC riêng. Mỗi firewall e1 dành WAN1, e3 dành WAN2 trong cấu trúc lịch sử; tên guest và cấu hình WAN2 không được suy từ thứ tự cổng. Hai segment WAN giữ cô lập, không nối pnet/VMware/Internet trong phạm vi M1 này. Không xóa các segment đã tồn tại.

Hai trunk tới hai firewall độc lập không tạo LAG chung; LACP không áp dụng. LAN parent quản trị lịch sử không được gọi là native VLAN được thiết kế mới. Chính sách frame không tag và các rule LAN parent rộng cần được rà riêng; không tự xóa trong nhiệm vụ M1.

Mirror hiện được mô tả ở M2: ingress ens3–ens9, VLAN30/40/50/60/99, output ens10. Cả hai trunk nằm trong phạm vi nguồn, hỗ trợ quan sát đường qua firewall đang hoạt động. Một gói có thể xuất hiện nhiều lần tại các cổng khác nhau; không diễn giải số frame mirror thành số phiên duy nhất. Chưa nghiệm thu cảnh báo Suricata liên tục trong failover.

## 1.6. Luồng dịch vụ và chính sách thiết kế

| Luồng | Chính sách / trạng thái |
|---|---|
| Employee .40.100 → DC .30.10 TCP8000 | Đã nghiệm thu cho phép trong M2 |
| Employee .40.101 → DC TCP8000 | Đã nghiệm thu bị chặn trong M2 |
| DC → Employee TCP8001, kết nối mới | Đã nghiệm thu bị chặn trong M2 |
| Guest → DC/Employee/Management | Thiết kế từ chối mặc định; chưa nghiệm thu từng luồng |
| DMZ → mạng nội bộ, kết nối mới | Thiết kế từ chối mặc định; ngoại lệ phải có yêu cầu dịch vụ |
| Management → giao diện quản trị | Chỉ nguồn và cổng được duyệt; chưa coi quản trị VLAN99 là đã nghiệm thu |
| Sensor → Wazuh qua VLAN99 | Dự kiến agent chuyển eve.json; chưa cài/đăng ký hay thử đường truyền live trong đợt này |
| Automation → OPNsense block IP | Luồng logic dành M4/M5; chưa có API block IP được nghiệm thu |
| Nội bộ → Internet / công bố DMZ | Ngoài phạm vi cơ sở; NAT và upstream thuộc phần mở rộng |

Trạng thái phiên và phản hồi được xử lý tại OPNsense. Luồng đã cho phép không có nghĩa mở kết nối mới chiều ngược. Suricata nhận bản sao nên đóng vai trò IDS, không phải IPS inline; hành động chặn dự kiến đi qua automation và firewall. XMLRPC mới có minh chứng alias thử, không suy thành đồng bộ toàn bộ cấu hình.

## 1.7. Tính sẵn sàng cao và giới hạn

CARP dùng VIP .1, VHID tương ứng VLAN30/40/50/60/99, advbase1, skew Primary0/Secondary100. M3.3 kiểm chứng chuyển MASTER sang Secondary khi Primary tắt và quay lại sau khôi phục. M3.4 kiểm chứng state ID/creator ID trên hai phía và một phiên TCP/HTTP giữ qua failover, hoàn tất HTTP200. Không kết luận không mất gói, không suy thành WAN/NAT/DHCP HA hoặc tất cả giao thức đã đạt.

Một Core là điểm lỗi đơn được chấp nhận trong phạm vi mô phỏng. Core thứ hai, ISP thứ hai có upstream, Indexer/Dashboard và máy automation riêng là mở rộng, không thuộc tiêu chí hoàn thành bản thiết kế cơ sở. Tài nguyên hiện có phải đo lại; các phép thử có thể thực hiện theo nhóm node và phải ghi rõ replay so với live.

## 1.8. Thuật ngữ

Phần giải thích đầy đủ được đính kèm ở Phụ lục 1.A trong bản Word, lấy từ docs/TOPOLOGY_TERMS.md: SOC, VLAN, IEEE 802.1Q, trunk, access port, LACP, SPAN, port mirroring, OVS, bridge, QEMU, QCOW2, cloud-init, NoCloud, SSH, OPNsense, CARP, pfsync, HA, NAT, DHCP, IDS/IPS, Suricata và Wazuh. Các ví dụ lịch sử trong phụ lục phải đọc cùng trạng thái tại các mục 1.4–1.7 của bản hợp nhất này.

## 1.9. Nghiệm thu hồ sơ và minh chứng còn cần

| Tiêu chí M1 | Kết quả đợt này |
|---|---|
| Chốt phạm vi lab nội bộ, Internet là mở rộng | Đạt theo lựa chọn người dùng |
| Quy hoạch VLAN/subnet/VIP và phân vai L2/L3 | Hoàn thiện hồ sơ, liên kết nghiệm thu thực tế |
| Đặc tả node/cổng và sơ đồ đích | Hoàn thiện thiết kế; Wazuh và IP mới vẫn dự kiến |
| Topology EVE-NG hoàn chỉnh, ảnh hiện trạng mới | Chưa đạt: chưa nối Wazuh hoặc kiểm kê trực tiếp trong đợt này |
| Thông tin bìa trường/khoa/MSSV/giảng viên | Chưa cung cấp; không tự điền |

Giới hạn công cụ của đợt này: chỉ đọc tệp cục bộ và xuất tài liệu, không có phiên GUI EVE được truy cập để chụp mới. Hướng dẫn chụp sau triển khai được ghi trong docs/evidence/M1/design-review-20261105/manual-capture.md. Không lấy sơ đồ tự vẽ làm ảnh hiện trạng; chưa chụp ảnh thì không ghi vào danh mục ảnh đã thu.

M1 hoàn thiện phần hồ sơ thiết kế cơ sở, chưa tuyên bố hoàn thành đầu việc topology EVE-NG thực tế. Bước thay đổi hệ thống cần xem xét riêng: nối Wazuh e0 vào segment Management hiện hữu, kiểm tra MAC/cổng/IP không trùng, cấu hình địa chỉ theo thiết kế được chốt và thu ảnh topology thật. Không thay WAN/seed/image hoặc cài thêm phần mềm từ nhiệm vụ viết hồ sơ này.


# PHỤ LỤC 1.A. GIẢI THÍCH THUẬT NGỮ

## 1.A.1. Mạng và phân vùng

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

## 1.A.2. Ảo hóa và khởi tạo máy

| Khái niệm và tên chính thức | Nghĩa tiếng Việt, nguyên lý | Vai trò và ví dụ trong đồ án |
|---|---|---|
| QEMU | Tên phần mềm giả lập và ảo hóa; trình bày CPU, đĩa và thiết bị mạng ảo cho guest. Không tự tạo dạng khai triển cho tên sản phẩm. | EVE điều phối tiến trình QEMU cho Ubuntu và OPNsense. UUID, MAC và TAP phải đối chiếu trước thao tác; node tạo trên GUI chưa chứng minh guest đã boot. |
| QCOW2 — QEMU Copy On Write version 2 | Định dạng đĩa ảo hỗ trợ cấp phát theo nhu cầu và backing file; overlay lưu phần thay đổi so với đĩa nền. | Các Linux mới dùng overlay riêng từ Ubuntu nền. Không lấy overlay Core đã cấu hình để nhân bản dịch vụ. Primary/Core đã được sao lưu và đối chiếu SHA-256 trước thay đổi topology. |
| cloud-init | Tên phần mềm khởi tạo Linux; đọc dữ liệu nguồn, cấu hình tài khoản/mạng và chạy tác vụ theo các giai đoạn boot. | Seed riêng của mỗi node mới chuẩn bị hostname, khóa SSH và tên NIC theo MAC. Seed đã tạo khác với tác vụ trong guest đã chạy thành công; phải xem kết quả và boot_id. |
| NoCloud | Tên datasource của cloud-init; lấy user-data, meta-data và tùy chọn network-config từ nguồn cục bộ hoặc đường dẫn được chỉ định. | ISO có volume label cidata của các Linux mới cung cấp dữ liệu khởi tạo offline. Seed Core cũ được giữ nguyên. |
| SSH — Secure Shell | Giao thức truy cập từ xa có mã hóa và xác thực, thường dùng khóa công khai để chứng minh quyền truy cập. | Windows dùng khóa ngoài repository để truy cập root EVE. Khóa riêng/passphrase không nằm trong minh chứng; SSH host EVE khác với SSH tới guest. |

Cơ chế seed và instance-id được tham chiếu từ [NoCloud — cloud-init](https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html). Trong lab cô lập, Linux mới dùng tài khoản soc-admin với SSH bằng khóa, khóa đăng nhập mật khẩu và console EVE tự đăng nhập để thực thi/thu minh chứng; đây là cấu hình dành cho môi trường mô phỏng có kiểm soát truy cập EVE, không phải kết quả kiểm chứng an toàn cho hệ thống sản xuất.

## 1.A.3. Firewall và dự phòng

| Khái niệm và tên chính thức | Nghĩa tiếng Việt, nguyên lý | Vai trò và ví dụ trong đồ án |
|---|---|---|
| OPNsense | Tên chính thức nền tảng firewall; xử lý lưu lượng theo interface, bảng trạng thái và bộ quy tắc. Không có dạng khai triển tự tạo. | Đảm nhiệm gateway, inter-VLAN routing, firewall rules và NAT. Primary đã có bằng chứng cài ổ từ M3; thêm dây không xác nhận gateway/HA. |
| HA — High Availability | Tính sẵn sàng cao; dùng thành phần dự phòng và cơ chế phát hiện/chuyển vai để giảm gián đoạn khi xảy ra lỗi. | Cặp Primary/Secondary là thiết kế HA. Cần kiểm tra chuyển vai và lưu lượng thực tế; hai biểu tượng firewall không đủ để kết luận HA đạt. |
| CARP — Common Address Redundancy Protocol | Giao thức dự phòng địa chỉ chung; các thành viên trao đổi thông báo và bầu thiết bị giữ địa chỉ ảo. | Dự kiến VIP .1 mỗi VLAN, Primary .2 và Secondary .3 theo M1. Chưa mặc định VIP hoạt động khi mới dựng topology. |
| pfsync | Tên giao thức đồng bộ trạng thái của Packet Filter; trao đổi thông tin trạng thái kết nối giữa các thành viên. Không tự đặt dạng khai triển chữ cái. | Dự kiến sử dụng mạng SYNC riêng trên vtnet2. Có dây SYNC chưa chứng minh trạng thái kết nối đã được đồng bộ. |
| NAT — Network Address Translation | Biên dịch địa chỉ mạng; thay đổi địa chỉ và có thể cả cổng trong gói, theo dõi ánh xạ để xử lý lưu lượng trả về. | Dự kiến outbound NAT qua OPNsense và công bố dịch vụ DMZ nếu có policy. Bridge WAN cô lập chưa có upstream nên chưa thể nghiệm thu NAT Internet. |
| DHCP — Dynamic Host Configuration Protocol | Giao thức cấp tham số mạng động; máy chủ cấp lease gồm địa chỉ, subnet, gateway và các tùy chọn như DNS. | M1 đề xuất cấp động cho Employee/Guest. Chưa suy có DHCP server/scope hoạt động từ tên VLAN hay từ dải IP dự kiến. |

Vai trò CARP và cơ chế dự phòng được đối chiếu với [High Availability — OPNsense](https://docs.opnsense.org/manual/hacarp.html). Các chức năng này vẫn cần được kiểm chứng trong đúng lab và phiên bản đang cài.

## 1.A.4. Phát hiện và phân tích sự kiện

| Khái niệm và tên chính thức | Nghĩa tiếng Việt, nguyên lý | Vai trò và ví dụ trong đồ án |
|---|---|---|
| IDS/IPS — Intrusion Detection System / Intrusion Prevention System | Hệ thống phát hiện/ngăn chặn xâm nhập; phân tích gói, luồng và quy tắc để phát cảnh báo hoặc thực thi hành động chặn khi triển khai ở vị trí cho phép. | Sensor nối bản sao lưu lượng của Core là IDS thụ động; không được gọi là IPS chặn inline chỉ vì Suricata hỗ trợ tính năng đó. |
| Suricata | Tên chính thức công cụ phân tích lưu lượng mạng; giải mã giao thức, theo dõi luồng và so khớp quy tắc để phát cảnh báo/log. | NIC capture0 dự kiến không IP, NIC mgmt0 tách biệt. Rule SID 1000001 trong repo dùng marker ICMP vô hại; chỉ khi có alert thật tương ứng mới xác nhận phát hiện, không suy từ service active. |
| Wazuh | Tên chính thức nền tảng giám sát an ninh; agent gửi dữ liệu tới thành phần phân tích, indexer phục vụ lưu/tìm kiếm và dashboard trình bày kết quả. | M1 có khối Wazuh/SOC. Node đã tạo không chứng minh đã có server/indexer/dashboard; vị trí NIC/VLAN chưa rõ nên không tự nối vào một VLAN. |

Phân biệt kiểm tra cấu hình, đọc PCAP offline và capture live theo [Suricata 7.0.3 — Command Line Options](https://docs.suricata.io/en/suricata-7.0.3/command-line-options.html). Cấu hình YAML theo [Suricata 7.0.3 — Suricata.yaml](https://docs.suricata.io/en/suricata-7.0.3/configuration/suricata-yaml.html). Thành phần nền tảng Wazuh đối chiếu [Wazuh components](https://documentation.wazuh.com/current/getting-started/components/index.html). Các ví dụ triển khai phải đọc cùng trạng thái và minh chứng trong báo cáo bàn giao, không dùng phần giải thích thuật ngữ thay cho kết quả nghiệm thu.
