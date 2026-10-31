### 2.20.1. Các khái niệm phục vụ triển khai và giám sát

Các ví dụ cấu hình mạng trong mục này là thiết kế dự kiến; chưa nghiệm thu VLAN, trunk, mirror, firewall HA hoặc hệ thống phân tích SOC.

| Thuật ngữ và nghĩa tiếng Việt | Nguyên lý hoạt động, vai trò và ví dụ trong đồ án |
|---|---|
| SOC — Security Operations Center; trung tâm điều hành an ninh mạng | Kết hợp con người, quy trình và công cụ để thu thập, phân tích và xử lý sự kiện. Dự kiến Core đưa lưu lượng tới cảm biến, Suricata phát hiện và Wazuh hỗ trợ phân tích tập trung. |
| OVS — Open vSwitch; tên chính thức của bộ chuyển mạch phần mềm | ovsdb-server giữ cấu hình, ovs-vswitchd điều khiển chuyển tiếp, datapath xử lý gói. Trong đồ án chỉ sử dụng chức năng Layer 2; dự kiến tạo bridge br-core-l2 để nối các vùng SOC. [1] |
| Bridge; cầu nối lớp liên kết | Học địa chỉ MAC và chuyển frame trong miền Layer 2, áp dụng phân tách VLAN. Dự kiến br-core-l2 chứa các port access/trunk; bridge chưa tạo trong bước cài phần mềm. |
| VLAN — Virtual Local Area Network; mạng cục bộ ảo | Phân chia miền quảng bá trên cùng hạ tầng chuyển mạch. Đồ án quy định VLAN 30 Data Center, 40 Employee, 50 Guest, 60 DMZ, 99 Management; cấu hình thực tế còn chờ. |
| IEEE 802.1Q; tiêu chuẩn mạng cầu nối và VLAN | Cơ chế gắn thẻ VLAN trong Ethernet cho phép phân biệt lưu lượng trên liên kết chung. Dự kiến trunk tới OPNsense mang các VLAN 30/40/50/60/99; chưa kiểm thử frame có thẻ. |
| Trunk; cổng mang nhiều VLAN | Chuyển lưu lượng nhiều VLAN, thường giữ thẻ 802.1Q; danh sách allowed VLAN giới hạn VLAN được phép. Dự kiến có hai trunk riêng tới hai OPNsense. [2] |
| Access port; cổng truy nhập một VLAN | Gán frame không gắn thẻ của endpoint vào VLAN cấu hình và bỏ thẻ khi đưa ra endpoint. Ví dụ dự kiến tag=30 cho cổng Data Center; chưa gán ens3 hoặc cổng cụ thể. [2] |
| LACP — Link Aggregation Control Protocol; giao thức điều khiển gộp liên kết | Trao đổi thông tin để thống nhất thành viên trong nhóm liên kết với peer tương thích. Có thể dùng khi mở rộng Core, nhưng chưa triển khai; hai firewall HA độc lập không tự trở thành một peer LACP. |
| SPAN — Switched Port Analyzer; tên chức năng giám sát cổng thường dùng trong hệ sinh thái Cisco | Sao chép lưu lượng nguồn sang cổng quan sát. Với OVS, dự kiến dùng đối tượng Mirror để đạt chức năng tương tự, đưa bản sao tới Suricata; chưa cấu hình. [2] |
| Port mirroring; sao chép lưu lượng cổng | Chọn frame theo cổng/VLAN và hướng để tạo bản sao ngoài đường chuyển tiếp chính. Cổng output-port dành riêng cho capture; cần kiểm thử trùng gói, VLAN tag và mất gói. Dự kiến triển khai sau khi xác minh peer. [2] |
| QEMU; tên chính thức của phần mềm giả lập và ảo hóa | Cung cấp thiết bị ảo và thực thi guest, có thể dùng tăng tốc KVM. Tiến trình QEMU thực tế đang phục vụ SOC-Core-L2 với 8 thiết bị VirtIO; không khởi động QEMU phụ. |
| QCOW2 — QEMU Copy On Write, version 2; định dạng đĩa sao chép khi ghi | Có thể lưu các khối thay đổi và tham chiếu backing file, giúp phân biệt image nền với overlay runtime. Core dùng đĩa QCOW2; phiên này không sửa đĩa từ host khi VM đang chạy. [3] |
| cloud-init; tên chính thức của công cụ khởi tạo instance | Đọc datasource và thực thi tác vụ khởi tạo theo module, như tạo tài khoản hoặc cấu hình ban đầu. Người dùng xác nhận Core đã hoàn tất; phiên cài OVS không chạy lại cloud-init. |
| NoCloud; tên datasource chính thức của cloud-init | Cung cấp user-data, meta-data và dữ liệu mạng từ nguồn cục bộ hoặc nguồn được chỉ định. Core đã dùng seed ISO; không sửa seed hoặc instance-id để cài lại. [4] |
| SSH — Secure Shell; giao thức truy cập shell bảo mật | Mã hóa phiên và xác thực danh tính, ở đây dùng khóa công khai và ssh-agent ký xác thực. Đã dùng SSH tới EVE; không suy ra có SSH trực tiếp vào guest khi NIC chưa nối mạng. [9] |
| OPNsense; tên chính thức của nền tảng firewall | Dùng lọc gói theo trạng thái, định tuyến và các dịch vụ mạng. Trong thiết kế SOC, OPNsense chịu gateway, liên VLAN, firewall rules và NAT; các chức năng này không đặt trên Core. |
| CARP — Common Address Redundancy Protocol; giao thức dự phòng địa chỉ chung | Các firewall phối hợp quyền sở hữu địa chỉ IP ảo để tiếp quản gateway khi có sự cố. Dự kiến dùng ở M3; chưa tạo hoặc kiểm thử VIP. [5] |
| pfsync; tên chính thức của cơ chế đồng bộ trạng thái Packet Filter | Đồng bộ thông tin trạng thái kết nối giữa firewall để giảm gián đoạn khi đổi vai; không đồng nghĩa đồng bộ toàn bộ cấu hình. Dự kiến có đường đồng bộ riêng ở M3, chưa triển khai. [10] |
| HA — High Availability; tính sẵn sàng cao | Dùng dự phòng, phát hiện lỗi và tiếp quản dịch vụ. Dự kiến hai OPNsense hỗ trợ HA; một Core duy nhất vẫn là điểm lỗi đơn, cài OVS không chứng minh HA. [5] |
| NAT — Network Address Translation; chuyển đổi địa chỉ mạng | Thay địa chỉ hoặc cổng trong lưu lượng theo quy tắc và trạng thái. Dự kiến OPNsense thực hiện NAT ra WAN; Core không làm NAT. [11] |
| DHCP — Dynamic Host Configuration Protocol; giao thức cấu hình máy trạm động | Máy khách và máy chủ trao đổi để cấp thuê địa chỉ cùng các tùy chọn gateway/DNS. Dự kiến OPNsense cấp cho VLAN được chốt; chưa xác nhận scope hoặc cấp phát thực tế. |
| IDS — Intrusion Detection System; hệ thống phát hiện xâm nhập. IPS — Intrusion Prevention System; hệ thống ngăn chặn xâm nhập | IDS phân tích và cảnh báo; IPS cần nằm trên đường xử lý có quyền chặn. Suricata nhận mirror dự kiến làm IDS thụ động, không thể coi việc nhận bản sao là đã chặn lưu lượng gốc. [6] |
| Suricata; tên chính thức của công cụ phân tích an ninh mạng | Phân tích giao thức và so khớp quy tắc để phát hiện, hỗ trợ ngăn chặn khi triển khai phù hợp. Dự kiến NIC capture nhận bản sao từ OVS; chưa có cảm biến/capture được kiểm chứng trong bước này. [6] |
| Wazuh; tên chính thức của nền tảng giám sát an ninh | Agent và các thành phần trung tâm thu thập, phân tích, lưu trữ và trình bày sự kiện. Dự kiến kết hợp dữ liệu endpoint và cảnh báo Suricata trong SOC; chưa xác nhận luồng tích hợp thực tế. [7] |

### 2.20.2. Tài liệu chính thức

[1] Open vSwitch, What Is Open vSwitch: https://docs.openvswitch.org/en/stable/intro/what-is-ovs/ .

[2] Open vSwitch, Basic Configuration: https://docs.openvswitch.org/en/stable/faq/configuration/ . Tài liệu stable hiện hành phục vụ giải thích nguyên lý; không thay kết quả kiểm tra binary 3.3.9 trong guest.

[3] QEMU, Disk Images: https://www.qemu.org/docs/master/system/images.html .

[4] cloud-init, NoCloud: https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html .

[5] OPNsense, High Availability: https://docs.opnsense.org/manual/hacarp.html .

[6] Suricata, What is Suricata: https://docs.suricata.io/en/latest/what-is-suricata.html .

[7] Wazuh, Components: https://documentation.wazuh.com/current/getting-started/components/index.html .

[8] Ubuntu Noble, apt-get manual: https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html .

[9] RFC Editor, RFC 4251, The Secure Shell Protocol Architecture: https://www.rfc-editor.org/info/rfc4251/ .

[10] OPNsense, Configure CARP, mục Terminology/pfSync: https://docs.opnsense.org/manual/how-tos/carp.html .

[11] RFC Editor, RFC 3022, Traditional NAT: https://www.rfc-editor.org/info/rfc3022/ .
