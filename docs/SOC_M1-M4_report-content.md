# CHƯƠNG 1. CƠ SỞ LÝ THUYẾT

## 1.1. SOC và mô hình giám sát an toàn thông tin

### 1.1.1. SOC — Security Operations Center

SOC là trung tâm điều hành an ninh, kết hợp con người, quy trình và công nghệ để giám sát, phân tích và phối hợp xử lý sự kiện. Một SOC không được xác định chỉ bởi số lượng phần mềm đã cài. Chất lượng vận hành còn phụ thuộc khả năng thu thập dữ liệu đúng nguồn, nhận diện sự kiện đáng chú ý, kiểm chứng kết luận và truy vết quá trình xử lý.

Nguyên lý làm việc là biến dấu vết từ các hệ thống thành thông tin phục vụ quyết định. Lưu lượng và nhật ký được thu nhận, đặt trong ngữ cảnh tài sản và thời gian, sau đó đối chiếu điều kiện phát hiện. Người vận hành đánh giá cảnh báo trước khi thực hiện phản ứng phù hợp. Vì vậy, việc máy chủ hoạt động không đồng nghĩa đã có giám sát đầu cuối hoàn chỉnh.

Trong đồ án, Core L2 và OPNsense cung cấp hạ tầng phân vùng; Suricata quan sát bản sao lưu lượng; Wazuh Manager phân tích sự kiện. Đây là các thành phần kỹ thuật của mô hình SOC. Minh chứng đã có xác nhận mạng, HA và hai chặng phát hiện/xử lý replay riêng; chưa đủ để kết luận SOC tích hợp liên tục đã hoàn thành. Tính sẵn sàng của gateway và chất lượng quan sát được đánh giá độc lập.

### 1.1.2. SIEM — Security Information and Event Management

SIEM là quản lý thông tin và sự kiện an ninh. Hệ thống này tập trung dữ liệu từ nhiều nguồn, tổ chức tìm kiếm và hỗ trợ liên hệ các dấu vết có chung ngữ cảnh. Khác với thiết bị chỉ quan sát một liên kết, SIEM có thể kết hợp thông tin mạng với tài khoản, máy chủ và lịch sử hành động.

Luồng xử lý thường gồm thu nhận, giải mã, chuẩn hóa, áp dụng quy tắc phân tích và trình bày kết quả. Mỗi tầng có một tiêu chí kiểm chứng riêng. Sự kiện tồn tại trong tệp nguồn chưa chứng minh máy chủ phân tích đã nhận; cảnh báo được ghi trên Manager chưa chứng minh đã được lập chỉ mục hoặc hiển thị trên Dashboard.

Trong dự án, Wazuh Manager đã tạo alert khi đọc replay EVE thật. Wazuh Indexer, Dashboard và Filebeat chưa có trong kiểm kê node Wazuh-SOC lịch sử; instance VMware ngày 07/11 chưa được kiểm kê lại đầy đủ. Vì vậy, báo cáo sử dụng cụm “Manager xử lý replay” thay cho “SIEM đầy đủ đang vận hành”. Kiến trúc sản phẩm được tham chiếu từ tài liệu chính thức, còn trạng thái triển khai căn cứ vào hồ sơ cục bộ. [T4; E15]

### 1.1.3. Event, log, alert, rule và signature

Event là sự kiện xảy ra ở hệ thống; log là bản ghi mô tả dấu vết sự kiện; alert là cảnh báo được tạo khi điều kiện phát hiện thỏa mãn. Ba đối tượng có liên hệ nhưng không đồng nhất. Chẳng hạn, một gói ICMP là dữ liệu đầu vào; dòng EVE chứa event_type=alert là bản ghi phát hiện; Manager có thể tạo một alert khác sau khi giải mã dòng đó.

Rule là quy tắc quy định điều kiện và hành động phân tích. Signature là dấu hiệu nhận diện mà quy tắc sử dụng, có thể dựa trên nội dung, giao thức hoặc thuộc tính luồng. Quy tắc cần được thử bằng trường hợp khớp và trường hợp không khớp; việc nạp tệp thành công chỉ xác nhận cú pháp, chưa xác nhận phát hiện đúng.

Ví dụ đã kiểm chứng: Suricata dùng SID1000001/rev1 phát hiện marker ICMP lành tính; Wazuh dùng rule86601 mức3 xử lý replay của sự kiện đó. SID và rule ID thuộc hai hệ thống khác nhau, không đổi chúng cho nhau. Alert mức3 không bị coi là thất bại chỉ vì quy tắc mô phỏng riêng của Wazuh có mức8. Dữ liệu liên kết gồm flow_id, địa chỉ, VLAN, nội dung signature và hash nguồn. [E14; E15]

## 1.2. Phát hiện và ngăn chặn xâm nhập

### 1.2.1. IDS, IPS, NIDS và HIDS

IDS — Intrusion Detection System là hệ thống phát hiện xâm nhập; IPS — Intrusion Prevention System là hệ thống ngăn chặn xâm nhập. IDS phân tích dữ liệu và phát cảnh báo; IPS được đặt ở vị trí có thể quyết định chuyển tiếp hoặc loại bỏ lưu lượng. Khả năng phần mềm hỗ trợ IPS không chứng minh một cấu hình cụ thể đang hoạt động theo chế độ đó.

NIDS — Network Intrusion Detection System là hệ thống phát hiện dựa trên mạng. Nó phân tích gói hoặc luồng tại một điểm quan sát. HIDS — Host-based Intrusion Detection System là hệ thống phát hiện dựa trên máy chủ, sử dụng nhật ký, thay đổi tệp hoặc dấu vết tiến trình. Hai nguồn bổ sung cho nhau: NIDS có thể thấy lưu lượng đi qua điểm thu nhưng không mặc nhiên thấy mọi hành vi nội bộ của máy; HIDS có thể thấy hoạt động cục bộ nhưng phụ thuộc phạm vi thu thập của host.

Trong topology đã nghiệm thu, Suricata là NIDS thụ động nối vào cổng mirror. Gói gốc không đi xuyên sensor để được chuyển tiếp nên sensor không tự chặn IP trên tuyến chính. Wazuh Manager cung cấp phân tích dữ liệu và có thể làm trung tâm cho agent, nhưng việc agent giám sát đầy đủ endpoint hoặc automation chặn IP thật chưa được nghiệm thu. Các chức năng này được trình bày ở phần hướng phát triển, không gán PASS. [E14–E16]

### 1.2.2. Suricata và EVE JSON

Suricata là tên chính thức của phần mềm phân tích lưu lượng và phát hiện/ngăn chặn xâm nhập; không tự tạo dạng khai triển cho tên sản phẩm. Engine thu gói, giải mã, theo dõi luồng và đối chiếu rule. Trạng thái service active và kiểm tra cấu hình hợp lệ là điều kiện cần, còn alert gắn với nguồn thử mới là bằng chứng chức năng.

EVE — Extensible Event Format là cơ chế xuất sự kiện JSON của Suricata. JSON — JavaScript Object Notation là cách biểu diễn dữ liệu có cấu trúc bằng đối tượng, mảng và giá trị. Một event có thể chứa timestamp, event_type, flow_id và thông tin giao thức. Các loại bản ghi được bật phụ thuộc cấu hình; có đối tượng flow trong một alert không đồng nghĩa đã thử riêng event_type=flow. EVE JSON khác EVE-NG, nền tảng mô phỏng mạng. [T3]

Ví dụ đã kiểm chứng trong dự án là Suricata7.0.3 nhận marker từ bản sao Core và ghi event_type=alert, VLAN[30], SID1000001. Báo cáo không suy rằng mọi loại DNS, HTTP, TLS hoặc toàn bộ bộ luật tấn công đã được thử. Phạm vi quan sát cũng bị giới hạn bởi các cổng/VLAN được chọn mirror, không phải mọi gói WAN và SYNC. [E14]

### 1.2.3. Wazuh Manager, Agent, Indexer và Dashboard

Wazuh là tên nền tảng an ninh; Manager là thành phần máy chủ xử lý và phân tích sự kiện. Agent là phần mềm ở endpoint thu dữ liệu và gửi về máy chủ. Indexer là bộ phận lập chỉ mục, lưu và tìm kiếm dữ liệu. Dashboard là giao diện người dùng truy vấn, trực quan hóa và quản trị. Tên các thành phần được giữ theo sản phẩm, không gán dạng viết tắt tự tạo. [T4]

Về nguyên lý, các thành phần tạo thành một chuỗi có hợp đồng dữ liệu và kết nối riêng. Agent kết nối chưa đủ chứng minh dữ liệu đã được phân tích; Manager có alert chưa đủ chứng minh Indexer đã lưu; mở trang đăng nhập Dashboard chưa đủ chứng minh cảnh báo thử xuất hiện. Nghiệm thu cần đi theo cùng sự kiện từ nguồn tới đích.

Tại Wazuh-SOC lịch sử, Manager4.14.9-1 được kiểm chứng hoạt động sau xử lý timeout và đã đọc tệp replay JSON để tạo alert. Kiểm kê không có gói Indexer, Dashboard và Filebeat. Trong báo cáo này không có ảnh Dashboard thực tế để trình bày như kết quả; ảnh mockup trong thuyết trình không được sử dụng thay minh chứng. Instance VMware .220.146 được ghi riêng vì chưa xác minh đồng nhất dữ liệu và cấu hình với node Wazuh-SOC trong EVE. [E15; E16]

## 1.3. Phân vùng và định tuyến mạng

### 1.3.1. VLAN, subnet và default gateway

VLAN — Virtual Local Area Network là mạng LAN ảo, tách miền quảng bá ở Layer2. Các cổng được gán vai trò và VLAN để giới hạn phạm vi chuyển frame Ethernet. VLAN không tự cung cấp chính sách ứng dụng: khi thiết bị Layer3 cho phép định tuyến giữa các vùng, cần thêm firewall rule để kiểm soát kết nối.

Subnet là mạng con IP, mô tả phần địa chỉ mạng thông qua prefix. Default gateway là cổng mặc định mà endpoint dùng khi không có route cụ thể hơn. VLAN thuộc lớp liên kết còn subnet thuộc lớp mạng; trong thiết kế này mỗi vùng VLAN gắn với một subnet /24 để quản trị rõ ràng, nhưng hai thuật ngữ không phải đồng nghĩa.

Ví dụ đã nghiệm thu: VLAN40 dùng 192.168.40.0/24; hai firewall có .2 và .3; CARP VIP .1 là gateway cung cấp cho Employee bằng DHCP. Địa chỉ .40.110 là lease endpoint trong ca thử, không phải VIP. Với DC, default route .30.2 vẫn được giữ trong bài continuity, chỉ thêm route riêng về client qua VIP .30.1; vì vậy không thể khẳng định mọi endpoint đã đổi default gateway sang VIP. [E1; E9; E10]

### 1.3.2. Core Switch Layer2, Layer3 và bridge

Core switch là thành phần chuyển mạch trung tâm trong topology. Ở Layer2, nó quyết định đường frame bằng thông tin MAC/VLAN. Thiết bị Layer3 có thể tra route IP và chuyển gói giữa subnet. Bridge là cầu chuyển mạch, liên kết các cổng trong miền L2 theo cấu hình. Việc bridge có interface nội bộ không bắt buộc phải gán IP hoặc bật định tuyến.

Trong dự án, Core dùng Open vSwitch, tên sản phẩm thường viết OVS. Bridge br-core-l2 chứa năm access port, hai trunk và output mirror. Core không có IP ngoài loopback, không default gateway và không làm inter-VLAN routing; forwarding IPv4/IPv6 của host bằng0 trong kiểm tra nghiệm thu. Tất cả gateway và kiểm soát Layer3 đặt trên OPNsense.

Lý do chọn cách phân vai này là tập trung routing, firewall, NAT và HA vào cặp firewall, đồng thời để Core làm chuyển mạch và tạo bản sao giám sát. Đây là ràng buộc của đồ án, không phải tuyên bố rằng Core Layer3 luôn không phù hợp cho mọi hệ thống. Một Core duy nhất vẫn là điểm lỗi đơn chưa được giải quyết bằng HA firewall. [E2; T1]

### 1.3.3. Access port, trunk port và IEEE802.1Q

Access port là cổng truy cập cho một VLAN; frame endpoint thường không gắn thẻ và được switch phân loại theo VLAN cấu hình. Trunk port là cổng mang nhiều VLAN; danh sách VLAN được phép giới hạn những vùng có thể đi trên liên kết. IEEE802.1Q là tên tiêu chuẩn mạng cầu nối/VLAN, quy định cơ chế gắn thẻ để phân biệt miền VLAN trên đường chung; đây không phải chữ viết tắt cần tự khai triển.

Về nguyên lý, switch nhận frame, xác định VLAN, tra quyết định chuyển tiếp rồi xử lý thẻ theo cổng ra. Hai đầu trunk phải thống nhất VLAN được phép và chính sách frame không tag. Cấu hình tên port đúng chưa chứng minh dữ liệu đi đúng đường; cần so MAC/cổng và kiểm tra frame tại cả access lẫn trunk.

Ví dụ đã nghiệm thu: ens3–ens7 lần lượt access VLAN30/40/50/60/99; ens8 tới Primary và ens9 tới Secondary đều mang năm VLAN. PCAP thử HTTP cho thấy cùng SYN có tag40 trước routing và tag30 sau routing tại Primary. Hai trunk đi hai firewall độc lập, không tạo một nhóm gộp liên kết chung. [E2; T1]

### 1.3.4. Inter-VLAN routing và firewall có trạng thái

Inter-VLAN routing là định tuyến giữa các VLAN/subnet. Endpoint gửi gói tới MAC gateway; thiết bị Layer3 tra route, giảm TTL và đóng frame mới cho mạng ra. Đổi VLAN ở switch không thay được chức năng gateway. Trong kiến trúc này, trunk đưa nhiều VLAN tới các interface VLAN trên OPNsense.

Firewall là tường lửa thực thi chính sách lưu lượng. Stateful firewall theo dõi trạng thái phiên; phản hồi thuộc kết nối đã cho phép có thể đi theo state mà không cần mở kết nối mới chiều ngược. ACL — Access Control List là danh sách kiểm soát truy cập; trong đồ án, nhu cầu ACL liên vùng được thực thi bằng firewall rule OPNsense, không đặt ACL Layer3 trên Core.

Bài M2 chứng minh HTTP .40.100→.30.10:8000 qua Primary với TTL64→63 và thay MAC đúng router. Ca ngược DC→Employee TCP8001 là một kết nối mới bị chặn, không mâu thuẫn với phản hồi HTTP được phép. NAT là chức năng khác; định tuyến liên VLAN trong ca này không đồng nghĩa dịch địa chỉ. [E2; T5]

## 1.4. Dịch vụ mạng và khả năng quan sát

### 1.4.1. NAT, SNAT và DNAT

NAT — Network Address Translation là dịch địa chỉ mạng. SNAT — Source Network Address Translation thay nguồn; DNAT — Destination Network Address Translation thay đích. Thiết bị duy trì thông tin ánh xạ để xử lý chiều về. NAT không thay firewall rule: có bảng dịch địa chỉ không đảm bảo gói được cho phép, có rule pass không đảm bảo upstream hoặc route tồn tại.

Trong dự án, Hybrid outbound NAT giữ cơ chế tự động và cho phép thêm rule thủ công ưu tiên. Một rule giới hạn được nghiệm thu cho .40.110→1.1.1.1 TCP443; địa chỉ nguồn ra WAN là IP interface Primary .220.144. Bằng chứng trước–sau cùng SYN xác nhận dịch nguồn. Không suy cả bảng NAT chỉ chứa một nguồn hoặc tất cả mạng nội bộ đều được mở Internet.

WAN VIP chưa tạo; hai firewall dùng WAN IP riêng. Bởi vậy PASS của một HTTPS không chứng minh giữ phiên NAT khi failover. Công bố Web/Mail DMZ bằng DNAT cũng chưa được nghiệm thu. Đây là giới hạn kỹ thuật cần được nêu ngay khi giới thiệu NAT. [E13; T6]

### 1.4.2. DHCP và DNS

DHCP — Dynamic Host Configuration Protocol là giao thức cấp phát cấu hình động. Máy chủ cung cấp lease địa chỉ và các tùy chọn như subnet, router và DNS. Với IPv4, quá trình trao đổi giúp client tìm server, yêu cầu và nhận tham số; cấu hình pool hợp lệ chưa đủ chứng minh client thực sự nhận lease đúng.

DNS — Domain Name System là hệ thống tên miền, hỗ trợ ánh xạ tên và thông tin liên quan qua truy vấn. Khả năng ping IP không chứng minh phân giải DNS; DNS trả lời cũng không chứng minh ứng dụng đích hoạt động. Trong SOC, lease và kết quả phân giải góp phần liên hệ địa chỉ với tài sản và thời điểm, nhưng phải bảo toàn nhật ký mới hỗ trợ điều tra được.

Kea DHCPv4 đã cấp .40.110 và .50.110 trong các pool .110–.199; gateway/DNS là VIP .1 tương ứng. Các ca DNS đã phân giải opnsense.internal. Tám rule có ngoại lệ DNS TCP/UDP cho Employee/Guest. Đồng bộ ba pool XML không đồng nghĩa đã đồng bộ lease hoặc nghiệm thu DHCP failover. [E10; E11]

### 1.4.3. SPAN, port mirroring và capture NIC

SPAN — Switched Port Analyzer là tên cơ chế quan sát bằng sao chép lưu lượng thường dùng trên thiết bị Cisco. Port mirroring là chức năng sao chép frame từ các cổng/hướng được chọn ra cổng đích. Trong lab, Core dùng đối tượng Mirror của OVS, không cấu hình SPAN bằng lệnh Cisco. [T1]

Capture NIC là giao diện card mạng thu nhận bản sao; NIC — Network Interface Card là giao diện kết nối mạng. Capture tách khỏi management NIC để đường quan sát không đồng nhất đường quản trị/log. Không gán IP cho capture không cản việc nhận frame; sensor đọc gói ở lớp liên kết. Tuy nhiên, mirror có thể trùng gói hoặc bỏ lỡ lưu lượng ngoài nguồn chọn, nên counter không tự trở thành số phiên duy nhất.

Ví dụ đã nghiệm thu: span-suricata chọn ingress ens3–ens9 và VLAN30/40/50/60/99, output ens10 tới capture0. select_dst_port rỗng, vì vậy không mô tả thành chọn mọi chiều của mọi cổng. Marker GET có trong PCAP mirror và counter đạt48. mgmt0 của sensor nằm trên segment Management nhưng địa chỉ .99.20 mới là đề xuất M1, chưa có nghiệm thu cấu hình IP đó. [E2; E14]

### 1.4.4. PCAP, TCP và tương quan gói

PCAP là định dạng lưu gói phục vụ phân tích; không tự suy là log ứng dụng. TCP — Transmission Control Protocol là giao thức truyền vận theo dõi phiên bằng sequence và acknowledgement. TTL — Time To Live là giới hạn bước của gói IPv4; router giảm TTL khi chuyển tiếp. MAC — Media Access Control address là địa chỉ liên kết dùng trong frame Ethernet.

Trong thử nghiệm, cùng tuple, sequence, marker, VLAN, TTL và MAC được kết hợp để chứng minh đường đi. Một timeout không đủ xác nhận firewall chặn nếu đích chưa có dịch vụ đối chứng. Tương tự, gói thấy tại mirror chưa chứng minh Suricata phát hiện; alert tại sensor chưa chứng minh Manager đã nhận. Dùng nhiều lớp quan sát giúp tránh kết luận vượt bằng chứng.

M3.4B kiểm một SYN, một request và response được tái lắp khớp hash. Đây là bằng chứng giữ cùng phiên TCP sau failover, nhưng không đo mất gói toàn hệ thống hoặc SLA. SHA-256 — Secure Hash Algorithm 256-bit dùng đối chiếu toàn vẹn dữ liệu, không thay thế diễn giải ngữ nghĩa của phép đo. [E2; E9]

## 1.5. Tính sẵn sàng cao của firewall

### 1.5.1. HA, failover và recovery

HA — High Availability là tính sẵn sàng cao, sử dụng thành phần dự phòng và cơ chế tiếp quản để giảm gián đoạn. Failover là chuyển vai sang thành phần dự phòng khi thành phần đang phục vụ không còn đáp ứng. Recovery là phục hồi thành phần và đưa hệ thống về vai trò mong muốn sau sự cố. Ba khái niệm liên quan nhưng yêu cầu bằng chứng khác nhau.

Active–Passive nghĩa là bình thường một node giữ vai trò phục vụ chính, node còn lại sẵn sàng tiếp nhận. Quan sát MASTER/BACKUP tại một thời điểm chưa chứng minh chuyển vai thành công. Muốn chứng minh continuity cần theo dõi cùng phiên trước–sau lỗi; tạo kết nối mới sau lỗi chỉ chứng minh khả năng phục vụ mới.

M3.3 đã kiểm chuyển năm VIP và recovery; M3.4B bổ sung continuity một phiên HTTP nội bộ. Recovery đã đưa Primary về MASTER, Secondary về BACKUP, nhưng request đã hoàn tất trước lúc boot Primary; không tuyên bố phiên đã đóng tiếp tục sống qua recovery. HA của hai firewall cũng không giải quyết lỗi đơn Core, host VMware hoặc nguồn điện lab. [E8; E9]

### 1.5.2. CARP và Virtual IP address

CARP — Common Address Redundancy Protocol là giao thức dự phòng địa chỉ chung. VIP — Virtual IP address là địa chỉ IP ảo được các node phối hợp sở hữu. VHID — Virtual Host Identifier định danh nhóm; advbase và advskew tham gia ưu tiên quảng bá. Endpoint trỏ tới VIP để việc đổi firewall sở hữu không đòi thay gateway từng client.

CARP xử lý quyền sở hữu địa chỉ, không tự đồng bộ firewall rule hoặc toàn bộ state TCP. Nhầm ba chức năng có thể dẫn đến tình huống VIP đã chuyển nhưng ứng dụng vẫn gián đoạn. Vì vậy, kiểm CARP cần quan sát đủ vai trò hai phía, đúng VIP và phản hồi L2; kiểm state và cấu hình được thực hiện riêng. [T2]

Năm VIP của đồ án là .1 trên các mạng30/40/50/60/99; Primary .2 ưu tiên skew0, Secondary .3 skew100, advbase1. Sau shutdown Primary, Secondary MASTER cả năm VLAN; sau recovery, hai phía trở lại vai trò ban đầu. Giao thức quảng bá112 được quan sát, nhưng không có WAN VIP đã nghiệm thu. [E7–E9]

### 1.5.3. pfsync và Packet Filter state

pfsync là tên cơ chế đồng bộ trạng thái của PF — Packet Filter, không tự tạo tên khai triển. State lưu các thông tin phục vụ theo dõi phiên. Các peer trao đổi cập nhật để node dự phòng có thể nhận biết kết nối đã tồn tại khi trở thành node phục vụ. Đây là đồng bộ trạng thái thời gian chạy, khác việc sao chép cấu hình rule.

Bulk synchronization là đồng bộ hàng loạt state khi peer khởi tạo hoặc cần bắt kịp. Trong lab, quá trình bulk có thể làm Primary tăng demotion, tạm giảm ưu tiên CARP rồi lấy lại MASTER sau hoàn tất. syncok1 và có packet240 là bằng chứng sẵn sàng cơ chế, chưa đủ chứng minh một session cụ thể đã được chuyển đúng.

Đồ án dùng vtnet2 trên SYNC10.255.255.0/30. Hook96 giúp gọi backend native sau boot trong image đã kiểm tra; đã kiểm persistence sau reboot. M3.4B so state ID/creator giữa hai máy và tại Secondary sau takeover. Nguyên nhân sâu của thời gian bulk kéo dài chưa xác định, không báo cáo đã xử lý triệt để. [E6; E9; E12]

### 1.5.4. XMLRPC và đồng bộ cấu hình

XML-RPC — XML Remote Procedure Call là cơ chế gọi thủ tục từ xa bằng thông điệp XML. XML — Extensible Markup Language là ngôn ngữ đánh dấu mở rộng. Trong OPNsense, nhóm cấu hình được chọn có thể được gửi từ firewall chính sang dự phòng. Cần phân biệt thành công transport, thao tác đồng bộ và nội dung thực tế được nạp ở máy nhận.

Kiểm alias thử cho thấy đường đồng bộ hoạt động ở mức mẫu nhưng chưa đủ cho toàn bộ firewall/DHCP. Báo cáo nghiệm thu sau đã đối chiếu đầy đủ tám rule và ba pool, kể cả UUID và trường con, đồng thời xác minh rule runtime ở cả hai máy. Cách làm này gắn cấu hình persistent với trạng thái thực thi.

PASS ở đây không bao gồm mọi nhóm XMLRPC, lease DHCP, blocklist runtime hoặc NAT HA. Rule NAT mới được áp tương đương riêng từng máy mà không mở rộng nhóm sync. Chỉ có thể dùng kết quả đã kiểm cho nhóm đã đối chiếu; việc chọn thêm nhóm đồng bộ là thay đổi hệ thống khác. [E11; E13]

## 1.6. Hạ tầng ảo hóa, khởi tạo và quản trị

### 1.6.1. VMware, EVE-NG, QEMU và QCOW2

VMware Workstation là tên sản phẩm ảo hóa máy tính; EVE-NG là tên nền tảng mô phỏng mạng. QEMU là tên phần mềm giả lập/ảo hóa thực thi các node guest trong môi trường này. Không tự đặt dạng khai triển mới cho các tên sản phẩm. QCOW2 — QEMU Copy On Write version2 là định dạng đĩa có thể lưu thay đổi và tham chiếu backing file.

Nguyên lý nhiều lớp ảo hóa yêu cầu phân biệt metadata topology, runtime liên kết và trạng thái bên trong guest. Đổi trường network trong XML EVE chưa chắc đã chuyển TAP đang chạy sang bridge khác. Tương tự, image nền đã có không chứng minh overlay của node đã boot đúng hoặc dịch vụ đã cấu hình.

Trong đồ án, node Core dùng Ubuntu và tám VirtIO NIC; các guest chạy bằng QEMU, một số đĩa dùng backing/overlay. Bài WAN đã chuyển đúng TAP runtime và metadata với guard/watchdog. Báo cáo không coi sơ đồ canvas là bằng chứng đủ cho route, IP hoặc pipeline. Vị trí quản trị EVE .220.143 khác gateway các VLAN. [E3; E13]

### 1.6.2. cloud-init, NoCloud và seed

cloud-init là tên công cụ khởi tạo instance, đọc datasource để thực hiện thiết lập ban đầu. NoCloud là tên datasource hỗ trợ dữ liệu như user-data, meta-data và network-config. Seed là gói dữ liệu đầu vào cho quá trình này, trong lab thường được gắn dưới dạng ISO; tên sản phẩm và datasource không tự khai triển.

Để nghiệm thu khởi tạo, cần đọc trạng thái trong guest thay vì chỉ thấy CD-ROM trong EVE. Một seed có sẵn không đảm bảo instance đã sử dụng; instance-id và cache khởi tạo có thể ảnh hưởng việc chạy lại. Ghi vào image hoặc seed khi VM hoạt động còn có rủi ro làm sai trạng thái nên các thao tác đó được quản lý riêng trong hồ sơ triển khai.

Ví dụ đã kiểm: Ubuntu nhận DataSourceNoCloud từ /dev/sr0, cloud-init status=done, errors rỗng. Employee-Linux được chuẩn bị overlay/seed riêng để không thay node VPCS. Dữ liệu đăng nhập và khóa riêng không được đưa vào báo cáo; việc biên soạn hiện tại không chạy lại cloud-init hoặc thay seed. [E3; E13]

### 1.6.3. SSH, LACP, Syslog và HTTP/TLS

SSH — Secure Shell là giao thức truy cập quản trị được mã hóa và xác thực. LACP — Link Aggregation Control Protocol điều khiển gộp liên kết giữa các đối tác phù hợp. Syslog là tên cơ chế/giao thức chuyển nhật ký, không phải chữ viết tắt cần tự khai triển. HTTP — Hypertext Transfer Protocol truyền thông điệp ứng dụng Web; TLS — Transport Layer Security bảo vệ kênh truyền.

Trong dự án, SSH được dùng thu thập dữ liệu EVE và bị chặn ở bước xác thực Wazuh ngày07/11. TCP22 mở không có nghĩa shell đăng nhập được. LACP không áp dụng cho hai trunk đi hai firewall độc lập. Syslog OPNsense→Wazuh chưa cấu hình/nghiệm thu; TCP514 refused không chứng minh UDP514 cũng đóng.

HTTP nội bộ làm dịch vụ đối chứng; HTTPS HEAD ra1.1.1.1 dùng kiểm chứng chỉ TLS và trả HTTP301. HTTP301 vẫn chứng minh có response trong phạm vi ca thử, không yêu cầu đổi thành200 để kết luận đạt. Lệnh curl không retry, proxy hoặc theo redirect nên kết quả không bị mở rộng thành truy cập nhiều đích. [E2; E13; E16]

# CHƯƠNG 2. M1 — THIẾT KẾ HỆ THỐNG

## 2.1. Mục tiêu, yêu cầu và phạm vi cá nhân

M1 xác lập kiến trúc mạng cho mô hình SOC: phân vùng endpoint, tập trung kiểm soát ở firewall, tạo điểm quan sát và bố trí thành phần phân tích sự kiện. Ràng buộc cốt lõi là Core chỉ Layer2; OPNsense chịu inter-VLAN routing, gateway, firewall, NAT và DHCP. Thiết kế gắn với khả năng của lab hiện có, không sử dụng địa chỉ đề xuất như kết quả triển khai khi chưa đối chiếu.

Phần việc cá nhân được trình bày theo hồ sơ dự án gồm quy hoạch và mapping Core L2, triển khai/kiểm chứng OVS, xây dựng và nghiệm thu OPNsense HA, dịch vụ mạng, điểm thu Suricata và kiểm chứng dữ liệu tới Manager ở mức replay. Hồ sơ không có nhật ký tác giả đủ để xác nhận mọi tệp do một cá nhân duy nhất tạo; báo cáo không nhận thay các phần AI, ELK hoặc automation của thành viên khác.

Các yêu cầu phi chức năng gồm bảo toàn cấu hình trước thay đổi, có rollback phù hợp, kiểm soát tài nguyên và lưu minh chứng có timestamp. Việc bật node, sửa seed, thay image hoặc nối mạng phải có quyền riêng. Báo cáo này chỉ tái sử dụng kết quả; không chạy lại lab để tạo thêm hình hoặc cải thiện số liệu.

## 2.2. Kiến trúc và phân vùng

@TABLE|Các vùng mạng trong topology đã kiểm chứng
| VLAN | Vùng | Subnet | Vai trò và mức kiểm chứng |
|---|---|---|---|
| 30 | Data Center | 192.168.30.0/24 | Endpoint Ubuntu, HTTP8000 đã kiểm chứng; AAA/DB/File chưa được suy là đã có |
| 40 | Employee | 192.168.40.0/24 | VPCS và Linux phục vụ các cửa sổ thử riêng; DHCP và TCP8000 đã kiểm |
| 50 | Guest | 192.168.50.0/24 | VPCS nhận DHCP; Guest→DC TCP8000 bị chặn đúng kỳ vọng; chưa triển khai Wi-Fi |
| 60 | DMZ | 192.168.60.0/24 | Ubuntu/HTTP80 có minh chứng; công bố Internet/Mail chưa nghiệm thu |
| 99 | Management | 192.168.99.0/24 | Segment quản trị; endpoint .99.100 kiểm ICMP VIP; Wazuh nối cấu trúc EVE |

DMZ thực tế dùng VLAN60; VLAN10 trong một số slide cũ không phù hợp với triển khai. Các tên dịch vụ trên sơ đồ như AAA, database, mail hoặc Wi-Fi là chức năng dự kiến của vùng, không phải kết luận rằng dịch vụ tương ứng đã được cài. Vai trò vùng mạng phải được tách khỏi mức sẵn sàng ứng dụng. [E1; E2]

@FIG|docs/evidence/M1/label-correction-20261105/topology-labels-corrected-20261105T0928+0700.png|Topology EVE-NG sau đính chính nhãn M1|Mục đích: xác nhận bố trí node, năm VLAN và hai firewall. Nội dung: Core L2, cặp OPNsense, SYNC, sensor và Wazuh nối Management. Kết quả: cấu trúc M1 có bằng chứng GUI/XML. Ý nghĩa: xác nhận thiết kế lab, không chứng minh mọi guest đang chạy; nhãn HA/WAN cũ trong ảnh không thay kết quả M3 ngày04–06/11.|05/11/2026 09:28, UTC+07:00 theo tên batch

## 2.3. Quy hoạch địa chỉ và CARP VIP

@TABLE|Địa chỉ hai firewall và gateway VIP đã nghiệm thu M3
| VLAN | Primary | Secondary | CARP VIP | VHID |
|---|---|---|---|---|
| 30 | 192.168.30.2/24 | 192.168.30.3/24 | 192.168.30.1/24 | 30 |
| 40 | 192.168.40.2/24 | 192.168.40.3/24 | 192.168.40.1/24 | 40 |
| 50 | 192.168.50.2/24 | 192.168.50.3/24 | 192.168.50.1/24 | 50 |
| 60 | 192.168.60.2/24 | 192.168.60.3/24 | 192.168.60.1/24 | 60 |
| 99 | 192.168.99.2/24 | 192.168.99.3/24 | 192.168.99.1/24 | 99 |

VLAN gateway và VIP đã có nghiệm thu M3 nên không còn chỉ là ví dụ M1. Thiết kế VIP .1 tạo địa chỉ gateway chung, còn .2/.3 giữ danh tính từng firewall. SYNC dùng10.255.255.0/30 với Primary .1 và Secondary .2 trên vtnet2. Không trộn đường SYNC với đường capture hoặc log.

Địa chỉ sensor quản trị .99.20 và Wazuh .99.30 được đề xuất trong thiết kế; chưa có nghiệm thu hai IP này. Wazuh VMware .220.146 ngày07/11 là quan sát khác, không tự thay vào bảng VLAN như thể đã xác nhận di chuyển instance. WAN .220.144/.145 do DHCP cấp ngày06/11, không phải địa chỉ tĩnh bảo đảm dài hạn. [E1; E7; E13; E16]

## 2.4. Mapping cổng và đường đi dữ liệu

@TABLE|Mapping cổng Core đã đối chiếu runtime
| Core EVE / Ubuntu | Đích | Vai trò |
|---|---|---|
| e0 / ens3 | Data-Center e0 | Access VLAN30 |
| e1 / ens4 | Employee segment | Access VLAN40 |
| e2 / ens5 | Guest segment | Access VLAN50 |
| e3 / ens6 | DMZ segment | Access VLAN60 |
| e4 / ens7 | Management segment | Access VLAN99 |
| e5 / ens8 | Primary e0 / vtnet0 | Trunk30/40/50/60/99 |
| e6 / ens9 | Secondary e0 / vtnet0 | Trunk30/40/50/60/99 |
| e7 / ens10 | Suricata e0 / capture0 | Output mirror riêng |

Đường chuyển tiếp chính đi endpoint→Core→firewall→Core→endpoint ở vùng đích. Capture nhận bản sao từ Core, không là node nằm giữa hai vùng. Wazuh là đích phân tích log, không nhận raw mirror Ethernet thay sensor. Hai trunk đảm bảo mỗi firewall có kết nối tới đủ vùng, nhưng không tạo LACP xuyên hai node độc lập.

M1 cơ sở có10node/11segment và đã bổ sung Wazuh e0 vào VLAN99 lúc09:15:50 ngày05/11; kiểm tra cấu trúc độc lập12/12 lúc09:16:43, ảnh GUI09:18:48. Sau đó Employee-Linux và WAN pnet0 được bổ sung; nghiệm thu WAN ghi11node/12network. Ảnh M1 phải được chú thích theo thời điểm, không gọi là ảnh hiện trạng cuối sau WAN. [E1; E13]

## 2.5. Thiết kế HA, quan sát và lý do lựa chọn

Hai firewall dùng Active–Passive để duy trì gateway chung. CARP xử lý VIP, pfsync hỗ trợ state và XMLRPC chuyển nhóm cấu hình được chọn. Tách ba cơ chế cho phép kiểm thử riêng quyền sở hữu địa chỉ, continuity của luồng và tính nhất quán policy. Thiết kế này phù hợp mục tiêu học thuật vì kết quả có thể quan sát bằng protocol112/240, state native và dữ liệu cấu hình.

Suricata đặt tại output mirror giúp quan sát mà không thay tuyến forwarding của hệ thống thử. Quản trị và capture tách NIC nhằm tránh việc phải đặt IP lên cổng nhận raw traffic. Wazuh Manager được chọn để giải mã và áp rule với JSON, nhưng tích hợp live cần đường vận chuyển có bằng chứng; việc vẽ mũi tên trên sơ đồ không đáp ứng tiêu chí đó.

Open vSwitch phù hợp lab vì cung cấp bridge, access/trunk và mirror trong guest Ubuntu; OPNsense tập trung routing và bảo vệ liên vùng; EVE-NG tạo topology với các node/tệp có thể kiểm kê. Các lựa chọn là giải pháp cho phạm vi mô phỏng, chưa phải kết luận so sánh hiệu năng hoặc chi phí với thiết bị sản xuất. [T1–T4]

## 2.6. Kết quả và giới hạn M1

M1 đạt trong phạm vi thiết kế và cấu trúc topology nội bộ. Minh chứng gồm bảng IP, mapping, XML và ảnh thật; không dựa riêng vào canvas. Internet ban đầu là mở rộng và sau đó được nghiệm thu tối thiểu M3, không sửa lịch sử M1 thành đã có Internet ngay từ đầu.

Hạn chế gồm một Core duy nhất, tài nguyên không phù hợp bật mọi node đồng thời, dịch vụ ứng dụng chỉ có endpoint đại diện và pipeline SOC chưa hoàn chỉnh. Khi đánh giá M1, cần phân biệt “đã nối segment” với “đã cấu hình IP”, “đã có guest” với “đã có dịch vụ”, và “thiết kế HA” với “đã thử failover”. Các trạng thái sau chỉ được nâng khi có nghiệm thu các chương tiếp theo.

# CHƯƠNG 3. M2 — TRIỂN KHAI CORE LAYER2

## 3.1. Mục tiêu, môi trường và chuỗi triển khai

M2 triển khai Core Open vSwitch trên Ubuntu để chuyển mạch năm VLAN, kết nối trunk tới firewall và tạo output mirror. Tiêu chí nghiệm thu là hành vi frame thật và đường đi ứng dụng có đối chứng; cài gói hoặc có port trong OVSDB chưa đủ kết luận chuyển mạch đạt.

Môi trường sử dụng Windows/VMware, EVE-NG quản trị .220.143, node SOC-Core-L2 và các guest kiểm thử. Core có tám VirtIO NIC được đối chiếu bằng MAC giữa EVE/QEMU/Ubuntu; tên ens3–ens10 được ghi sau khi quan sát, không suy từ thứ tự thiết kế. Cấu hình tài nguyên thay đổi theo giai đoạn; không ghép các số RAM ở những mốc khác nhau thành một snapshot đồng thời.

Quy trình triển khai đi từ chuẩn bị image/seed, boot guest, cài OVS offline, xác minh dịch vụ, tạo bridge cô lập, nối peer sau phê duyệt, thử frame, kiểm persistence rồi nghiệm thu routing/policy với OPNsense. Các checkpoint chưa bridge hoặc chưa SPAN trong tài liệu đầu là lịch sử đúng tại thời điểm đó; kết quả cuối M2 ngày03/11 có cả mirror đã được kiểm chứng. [E3–E5]

## 3.2. Chuẩn bị image, NoCloud và cài OVS offline

Ubuntu24.04 được kiểm chứng khởi tạo bằng cloud-init. Trạng thái done, datasource NoCloud và danh sách lỗi rỗng chứng minh guest nhận seed; đồng hồ guest có mốc1970 không được sử dụng làm thời điểm thu. Timestamp collector được ghi riêng với UTC+07:00.

Quá trình cài OVS offline dùng kho cục bộ có metadata/chữ ký, không coi lỗi DNS của guest là đã được giải quyết bằng một lần cài offline. Nguồn noble-only ban đầu thiếu phiên bản cần; offline.list riêng bổ sung noble-updates và noble-security, dùng keyring Ubuntu. Đây là xử lý gói phần mềm, chưa thay đổi vai trò mạng của Core.

Kiểm kê sau cài ghi OVS3.3.9, schema8.5.1, ba gói OVS phiên bản3.3.9-0ubuntu0.24.04.1;70/70gói và6/6chỉ mục khớp, ba chữ ký tốt. Các chỉ số này là toàn vẹn/cài đặt, không cộng thành ca chuyển tiếp frame. Không ghi vào QCOW2 đang chạy từ host để sửa cấu hình. [E3]

@FIG|docs/evidence/M2/M2-cloud-init-success-20261031T184335+0700.png|cloud-init hoàn tất và nhận datasource NoCloud|Mục đích: kiểm tra nền hệ điều hành trước khi dựng switch. Nội dung: status done, datasource và errors. Kết quả: guest nhận khởi tạo, không dùng thời gian guest làm timestamp collector. Ý nghĩa: đủ nền quản trị; chưa chứng minh VLAN, routing hoặc HA.|31/10/2026 18:43, UTC+07:00 theo batch

@FIG|docs/evidence/M2/M2-ovs-installed-verification-20261031T235923+0700.png|Open vSwitch sau cài đặt offline|Mục đích: xác minh binary, service và OVSDB. Nội dung: trạng thái thực tế sau cài OVS. Kết quả: phần mềm có thể quản trị; tại mốc ảnh chưa phải nghiệm thu forwarding. Ý nghĩa: tách cài đặt thành công khỏi chuyển mạch thành công.|31/10/2026 23:59:23, UTC+07:00 theo tên ảnh

## 3.3. Tạo bridge và cấu hình access/trunk

Trước tạo br-core-l2, đã kiểm tra không có Bridge/Port/Interface/Mirror xung đột, lưu link/address/route làm baseline và backup OVSDB qua socket đang chạy. Backup có quyền0600 trong thư mục0700; kiểm schema trước sử dụng. Không dùng snapshot rỗng cũ để rollback một cấu hình mirror đã được bổ sung sau này.

Giao dịch OVS tạo bridge datapath system, fail_mode standalone, local port access99 không IP; năm access port và hai trunk được gán theo mapping. Không có controller, bond hoặc LACP. Các lệnh dưới đây là biểu diễn tương đương của các thuộc tính đã triển khai, phục vụ giải thích; không phải log terminal bổ sung và không được chạy lại trong đợt biên soạn.

```text
ovs-vsctl add-br br-core-l2
ovs-vsctl add-port br-core-l2 ens3 tag=30
ovs-vsctl add-port br-core-l2 ens4 tag=40
ovs-vsctl add-port br-core-l2 ens5 tag=50
ovs-vsctl add-port br-core-l2 ens6 tag=60
ovs-vsctl add-port br-core-l2 ens7 tag=99
ovs-vsctl add-port br-core-l2 ens8 trunks=30,40,50,60,99
ovs-vsctl add-port br-core-l2 ens9 trunks=30,40,50,60,99
```

tag xác định VLAN access; trunks là tập VLAN cho cổng trunk. Thực tế triển khai kiểm tra trước và áp giao dịch có bảo vệ, không chạy rời các lệnh mẫu mù quáng. Local internal interface không được đặt IP/gateway. Đường quản trị Core trong phạm vi lab sử dụng console EVE, không tự đặt SVI Layer3 cho VLAN99.

Lần áp đầu bị kiểm tra route chặn vì kernel sinh route multicast IPv6 ff00::/8 trên bridge mới. Đã restore snapshot thực tế, xác nhận quay baseline, rồi xử lý host IPv6 riêng trên interface mới trước áp lại. Không diễn giải route multicast là route inter-VLAN. Việc tắt host IPv6 trên internal interface cũng không chứng minh OVS chặn frame Ethernet IPv6. [E4]

@FIG|docs/evidence/M2/final-acceptance-20261103/core-runtime-root-20261103T171628+0700.png|Mapping port và trạng thái Core chỉ Layer2|Mục đích: xác nhận runtime của Core sau boot. Nội dung: các port/VLAN, forwarding0/0 và không IP ngoài loopback. Kết quả: khớp mapping nghiệm thu. Ý nghĩa: Core không đóng vai trò gateway; routing phải được chứng minh tại firewall.|03/11/2026 17:17:04, UTC+07:00 theo báo cáo M2

## 3.4. SPAN/Port Mirror và persistence

Mirror span-suricata được nghiệm thu sau giai đoạn bridge cô lập. Nguồn chọn ingress ens3–ens9, VLAN30/40/50/60/99; output ens10; select_all=false và select_dst_port rỗng. Đây là bản sao lưu lượng tại các data port đã chọn, không phải port mạng người dùng có gateway. Cổng mirror gửi ngược không được sử dụng như đường chuyển tiếp dữ liệu thông thường trong suite frame.

Nghiệm thu có dữ liệu trước/sau reboot và suite frame95/95đạt trong phạm vi M2. Mỗi snapshot runtime chỉ kiểm trạng thái tại thời điểm thu; không cộng ảnh chụp lặp thành ca thử mới. Trong cửa sổ HTTP cuối, PCAP mirror có marker GET; tx_packets tăng48 và tx_bytes4278. Số counter bao gồm frame ngoài filter HTTP như ARP nên không ép bằng số packet PCAP32.

@FIG|docs/evidence/M2/final-acceptance-20261103/core-mirror-after-tests-20261103T171916+0700.png|OVS Mirror và bộ đếm sau kiểm thử|Mục đích: kiểm nguồn, VLAN và output mirror. Nội dung: đối tượng span-suricata, select_vlan và counter. Kết quả:48frame theo counter; PCAP xác nhận có marker. Ý nghĩa: chức năng sao chép đã đạt, không đồng nghĩa Suricata/Wazuh đã nhận toàn chuỗi.|03/11/2026 17:19:23, UTC+07:00 theo báo cáo M2

## 3.5. Kết nối OPNsense và kiểm thử liên VLAN

Bài nghiệm thu cuối dùng Linux network namespace m2-client40 trong VM Data-Center với NIC thứ hai tạm nối VLAN40. Client và server có stack/interface/route riêng; không đặt hai IP cùng một interface để giả lập inter-VLAN. Client .40.100/24 đi .40.2, server .30.10/24 đi .30.2 trong cửa sổ M2, trước khi dùng VIP ở bài M3.4.

Đường thực đi client0→access ens4→Core→trunk ens8→Primary VLAN40→routing/firewall→Primary VLAN30→trunk ens8→access ens3→server. PCAP cùng SYN giữ IP ID60023, sequence3060261172, tag40→30, TTL64→63 và MAC router Primary. Điều này chứng minh có chuyển tiếp L3 tại OPNsense thay vì đường tắt trong guest.

@TABLE|Ba ca kiểm thử ứng dụng và policy của M2
| Mã | Luồng | Kết quả và bằng chứng | Kết luận |
|---|---|---|---|
| M2-P01 | .40.100→.30.10 TCP8000 | HTTP200/164byte; cùng SYN tag40→30, TTL64→63; rule pass có counter | PASS |
| M2-N01 | .40.101→cùng server TCP8000 | Có đối chứng dịch vụ;6SYN ingress,0frame egress phù hợp; timeout | PASS: deny đúng |
| M2-N02 | .30.10→.40.100 TCP8001 mới | Dịch vụ tạm có đối chứng cục bộ;6SYN ingress,0frame egress; timeout | PASS: deny đúng |

Không dùng timeout riêng lẻ làm bằng chứng chặn. Default deny tăng12packet trong cửa sổ; rule pass tạo một state và10packet. Hai rule LAN parent rộng được ghi nhận vẫn giữ nguyên; M2 không chứng nhận least-privilege toàn hệ thống hoặc mọi cặp VLAN/port/IPv6.

@FIG|docs/evidence/M2/final-acceptance-20261103/dc-http-results-summary-20261103T171916+0700.png|Kết quả HTTP dương và hai ca âm|Mục đích: kiểm khả năng ứng dụng đi qua firewall. Nội dung: một HTTP200 và hai timeout đúng kỳ vọng. Kết quả: đối chiếu thêm PCAP/counter mới kết luận policy đạt. Ý nghĩa: chứng minh các ca cụ thể, không phải kiểm hết ma trận phân vùng.|03/11/2026 17:19:59, UTC+07:00 theo báo cáo M2

@FIG|docs/evidence/M2/final-acceptance-20261103/primary-rule-after-tests-20261103T171843+0700.png|Counter firewall sau các ca thử M2|Mục đích: bổ sung bằng chứng quyết định pass/deny. Nội dung: counter rule và hash cấu hình. Kết quả: tăng phù hợp ca thử, cấu hình không thay đổi để làm PASS. Ý nghĩa: liên hệ packet với chính sách thực thi.|03/11/2026 17:18:53, UTC+07:00 theo báo cáo M2

## 3.6. Khôi phục, lỗi thực tế và kết luận M2

Sau nghiệm thu, server TCP8001 tạm đã kết thúc; DC shutdown mềm, NIC tạm gỡ và topology phục hồi nguyên byte theo backup khi điều kiện hash phù hợp. Không dừng Core/Primary hoặc thay firewall để tạo kết quả. Cấu hình Primary giữ hash2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2 trong đợt M2.

Các lỗi đã xử lý gồm thiếu nguồn offline đúng phiên bản, route multicast phát sinh khi tạo bridge, lỗi kiểm đường dẫn XML/visibility khi chuẩn bị NIC tạm và sudo hết hạn. Cảnh báo OVS_CTL_OPTS chưa đặt còn xuất hiện trong journal trong khi service active; không che cảnh báo hoặc tự sửa unit để làm báo cáo đẹp hơn.

Kết luận M2 PASS trong phạm vi Core L2, access/trunk, mirror/persistence và các ca routing/policy đã giao. Chưa từ M2 suy thành HA, NAT, DHCP, IDS live hoặc SOC end-to-end đã đạt. LACP không áp dụng trong topology hiện hữu. Các minh chứng cũ giữ nguyên thư mục và hash, không di chuyển/xóa trong quá trình viết báo cáo.

# CHƯƠNG 4. M3 — OPNsense FIREWALL VÀ HIGH AVAILABILITY

## 4.1. Mục tiêu và quá trình cài đặt nền tảng

M3 đưa thiết kế gateway/firewall vào vận hành và nghiệm thu theo từng chức năng độc lập: pfsync persistent, CARP năm VLAN, failover/recovery, continuity phiên, DHCP/DNS/firewall, XMLRPC và WAN/NAT tối thiểu. Trình tự có checkpoint để không coi một snapshot MASTER/BACKUP hoặc cài OS thành công là nghiệm thu tất cả HA.

Primary được cài OPNsense26.7 amd64 lên vtbd0 16GiB bằng UFS ngày01/11. Trước ghi đã xác minh đúng ổ; sau cài có boot từ ổ cứng, GPT/rootfs và phiên bản trong shell. Đổi boot order thành order=c thay vì xóa/đổi tên ISO. Backup overlay thực hiện khi QEMU đã dừng; restore đĩa chưa thử không được kết luận rollback đĩa PASS. [E5]

Secondary đã được kiểm kê và tham gia nghiệm thu hai phía ở M3.1–M3.4; báo cáo không suy rằng mọi màn hình installer Secondary giống Primary nếu không có ảnh riêng. Bằng chứng chức năng hai firewall sau boot là cơ sở xác nhận Secondary có thể phục vụ vai trò HA. Tài nguyên tối ưu về Core1024MiB và mỗi firewall2048MiB tại một số cửa sổ sau, không thay thế thông số cài Primary ban đầu3072MiB.

@FIG|docs/evidence/M3/primary-installed-20261101/primary-version-20261101T221706+0700.png|Phiên bản OPNsense và filesystem sau cài Primary|Mục đích: xác nhận firewall chạy hệ điều hành đã cài. Nội dung: phiên bản, dung lượng filesystem và thông tin guest. Kết quả: OPNsense26.7 hoạt động tại shell. Ý nghĩa: đây là nghiệm thu nền tảng một máy, chưa phải HA hoặc NAT.|01/11/2026 22:17:06, UTC+07:00 theo tên ảnh

## 4.2. Interface LAN, WAN, VLAN và SYNC

@TABLE|Phân vai interface hai OPNsense
| Interface | Chức năng | Kết quả đã có |
|---|---|---|
| vtnet0 | LAN parent/trunk tới Core | Parent VLAN30/40/50/60/99; không suy LAN parent là native VLAN được thiết kế mới |
| VLAN opt1–opt5 | Interface vùng30/40/50/60/99 | Primary .2, Secondary .3, CARP VIP .1 trên mỗi /24 |
| vtnet1 | WAN1 | Sau06/11: DHCP .220.144/.145, gateway .220.2, pnet0/network12 |
| vtnet2 | SYNC riêng | 10.255.255.1/30↔10.255.255.2/30, pfsync peer đối ứng |
| WAN2 trong thiết kế | Đường mở rộng | Chưa nghiệm thu upstream/multi-WAN; không gán trạng thái PASS |

Cấu hình VLAN trên firewall được đối chiếu parent, tag, assignment và IP thực tế thay vì chỉ nhìn tên opt. Khi có CARP, IP riêng vẫn tồn tại song song VIP. Quyền quản trị lịch sử trên LAN parent được giữ theo phạm vi thay đổi; không coi sự tồn tại rule quản trị rộng là đã đạt chính sách quản trị tối thiểu toàn mạng.

## 4.3. pfsync persistent sau reboot

Ở bước đầu, cấu hình peer tồn tại nhưng boot chưa áp runtime đúng khi chưa có VIP. Kiểm mã cài trên image cho thấy routine pfsync được gọi ở luồng liên quan CARP nhưng thiếu tại đường khởi tạo mạng đã quan sát. Không quy nguyên nhân cho giảm RAM khi không có bằng chứng.

Đã bổ sung syshook /usr/local/etc/rc.syshook.d/start/96-soc-pfsync, mode0700, gọi pluginctl -c pfsync bằng backend native sau khởi tạo mạng. Log root-only gắn kern.boottime và native exit code. Hai firewall được reboot mềm lần lượt để xác minh hook tự chạy, không gọi lại apply bằng tay sau reboot nhằm tạo kết quả. [E6]

@TABLE|Điều kiện nghiệm thu M3.1 sau reboot từng firewall
| Chỉ tiêu | Primary | Secondary |
|---|---|---|
| Boot mới và hook được boot sequence gọi | PASS | PASS |
| Native exit code | 0 | 0 |
| pfsync runtime | UP/RUNNING, syncdev vtnet2 | UP/RUNNING, syncdev vtnet2 |
| Peer | 10.255.255.2 | 10.255.255.1 |
| Runtime version / syncok / demotion | 1400 / 1 / 0 | 1400 / 1 / 0 |
| Ping SYNC | 2/2 | 2/2 |

Một log hook lúc mới khởi tạo có syncok0, sau đó runtime hội tụ về1 khi peer sẵn sàng. Vì vậy, kết luận dựa trên điều kiện cuối hai phía và log boot, không chọn trạng thái tức thời làm kết luận thất bại hoặc bỏ qua nó. M3.1 chưa tự chứng minh continuity; M3.4B xử lý câu hỏi đó bằng session thật.

@FIG|docs/evidence/M3/todo-completion-20261103/primary-pfsync-proof-20261103T232422+0700.png|pfsync Primary tự áp sau reboot|Mục đích: kiểm persistence của cơ chế đồng bộ. Nội dung: boot log và pfsync runtime. Kết quả: syncok1/demotion0 ở thời điểm nghiệm thu, native_rc0. Ý nghĩa: tự khởi tạo đúng, không phải apply thủ công sau boot để tạo ảnh.|03/11/2026 23:24:22, UTC+07:00 theo tên batch

## 4.4. Triển khai CARP và nghiệm thu năm VIP

Trước áp đã kiểm IP .2/.3 và quan sát không có .1 trả ARP trong phạm vi probe, không có quảng bá protocol112 trong cửa sổ thu. Điều này là tiền kiểm có giới hạn, không bảo đảm phát hiện thiết bị offline hoặc chưa khai báo. Shared secret được quản lý riêng; không xuất password, private key hoặc fingerprint mật khẩu vào báo cáo.

CARP được áp qua model native OPNsense Interfaces VIP, có validation trước save, sau đó nạp VIP/filter. Mỗi máy có đúng năm VIP, VHID bằng VLAN, advbase1, skew0/100. Quyền sở hữu được kiểm trực tiếp Primary MASTER/Secondary BACKUP; không suy Secondary BACKUP chỉ từ việc không thấy quảng bá của máy này.

@FIG|docs/evidence/M3/todo-completion-20261103/primary-carp-proof-20261103T233424+0700.png|Primary MASTER trên năm VLAN sau áp CARP|Mục đích: xác minh VIP và vai trò tại firewall chính. Nội dung: runtime năm interface/VHID. Kết quả: MASTER/skew0 đúng quy hoạch. Ý nghĩa: tham số thiết kế trở thành cấu hình thực tế; ảnh chưa thay phép thử failover.|03/11/2026 23:34:24, UTC+07:00 theo tên batch

@FIG|docs/evidence/M3/todo-completion-20261103/secondary-carp-proof-20261103T233530+0700.png|Secondary BACKUP trên năm VLAN|Mục đích: kiểm máy dự phòng độc lập. Nội dung: VIP/VHID và BACKUP/skew100. Kết quả: đủ năm vùng, pfsync vẫn sẵn sàng. Ý nghĩa: xác nhận cặp HA tại thời điểm nghiệm thu, chưa tự suy giữ phiên.|03/11/2026 23:35:30, UTC+07:00 theo tên batch

## 4.5. Kiểm thử CARP failover và recovery M3.3

M3.3 thu ba pha BEFORE/FAILOVER/RECOVERY. BEFORE xác nhận Primary MASTER, Secondary BACKUP, đủ VIP, syncok1/demotion0. FAILOVER chỉ shutdown mềm Primary; host xác nhận Primary tắt, Core và Secondary giữ PID; Secondary tự MASTER năm VLAN và VIP trả ARP. RECOVERY boot lại Primary, quan sát tự trở lại MASTER và Secondary BACKUP, không đổi VIP/VHID/advskew hoặc gọi lại pfsync để làm đạt.

Nghiệm thu tổng hợp lúc11:07:14.319327 ngày04/11/2026 UTC+07:00 ghi DONE/PASS. Phạm vi M3.3 là chuyển quyền sở hữu gateway và readiness sau phục hồi; chưa kiểm session preservation. Bản READY_FOR_FAILOVER trước đó không thay được kết quả nghiệm thu mới, nhưng vẫn giữ làm lịch sử, không sửa nội dung cũ thành đã thử. [E8]

## 4.6. Kiểm thử state và duy trì một TCP session M3.4B

Một thử nghiệm M3.4 trước bị gián đoạn do môi trường EVE restart: đã có một phần state/ACK nhưng thiếu HTTP hoàn tất và recovery. Hồ sơ cũ được giữ FAIL/BLOCKED theo phạm vi thiếu chứng cứ; không đổi thành PASS hoặc che lỗi. Sau khôi phục baseline M3.4A, bài M3.4B tạo session mới và nghiệm thu đầy đủ. Hai lần thử có source port/state ID khác nhau, không gộp thành một phiên liên tục.

Client bài thành công là bộ thực thi TCP qua AF_PACKET trên host EVE, dùng access TAP VLAN40 đã có, không phải VPCS và không phải socket TCP kernel của Employee-Linux triển khai sau. Server là VM DC thật .30.10:8000. Chỉ thêm route runtime .40.100/32 via .30.1 để chiều về qua CARP; IP/default route/netplan DC giữ nguyên.

@TABLE|Định danh và kết quả session M3.4B
| Thuộc tính | Giá trị đã kiểm chứng |
|---|---|
| Tuple | 192.168.40.100:44341→192.168.30.10:8000/TCP |
| State ID | 075deb6a00000000 và 085deb6a00000000 |
| Creator ID | d57c33f6 |
| Trước failover | Hai phía có cùng ID/creator và ESTABLISHED; Secondary BACKUP counter0:0 |
| Sau Primary OFF | Secondary MASTER5VLAN; state ID/creator giữ nguyên, counter tăng sau chuyển dữ liệu |
| Continuity | Một SYN; một request;11marker ACK sau Primary OFF; không reconnect |
| Hoàn tất ứng dụng | HTTP/1.0 200 OK;350byte; response tái lắp PCAP khớp hash |
| Recovery | Primary MASTER/Secondary BACKUP;5VIP đúng, pfsync READY, syncok1/demotion0 |

Watcher chỉ đọc CARP/PF, lưu snapshot native ngay khi quan sát đủ năm MASTER. Khoảng read-start so với watcher là độ trễ công cụ, không phải downtime hoặc thời gian hội tụ HA. Counter0 tại snapshot takeover sớm không bị coi là state vô dụng; counter tăng và marker ACK sau đó chứng minh state được sử dụng.

M3.4B DONE/PASS lúc17:12:50.875586 ngày04/11. Client retry0 và không duplicate payload quan sát tại capture không đủ để khẳng định zero packet loss toàn hệ thống. HTTP hoàn tất qua Secondary trước recovery; không tuyên bố cùng session sống qua recovery khi nó đã đóng. [E9]

@FIG|docs/evidence/M3/M3.4B-pfsync-state-20261104/secondary-state-before-readable-20261104T165544+0700.png|State native tại Secondary trước failover|Mục đích: xác minh state đã đồng bộ tới node BACKUP. Nội dung: tuple, state ID/creator và trạng thái TCP. Kết quả: khớp Primary trước lỗi. Ý nghĩa: bằng chứng trực tiếp state, không chỉ có packet240 hoặc dòng syncok.|04/11/2026 16:55:44, UTC+07:00 theo tên batch

@FIG|docs/evidence/M3/M3.4B-pfsync-state-20261104/secondary-after-native-readable-20261104T165711+0700.png|Secondary MASTER và state TCP sau failover|Mục đích: xác minh node tiếp quản sử dụng state cũ. Nội dung: năm MASTER và hai entry ESTABLISHED cùng ID/creator. Kết quả: counter tăng trên state; đọc cùng client/wire log xác nhận HTTP hoàn tất. Ý nghĩa: continuity của một phiên nội bộ đã đạt, không suy NAT HA.|04/11/2026 16:57:11, UTC+07:00 theo tên ảnh

@FIG|docs/evidence/M3/M3.4B-pfsync-state-20261104/primary-recovery-carp-readable-20261104T170827+0700.png|Primary lấy lại MASTER sau recovery|Mục đích: kiểm vai trò và VIP khi khôi phục. Nội dung: IP .2, VIP .1 và năm MASTER. Kết quả: đúng trạng thái đích; Secondary về BACKUP theo JSON nghiệm thu. Ý nghĩa: recovery đạt; request HTTP đã kết thúc trước pha này.|04/11/2026 17:08:27, UTC+07:00 theo tên batch

## 4.7. DHCP, DNS, endpoint và firewall M3.5

Kea DHCPv4 cấp pool .40.110–.40.199 cho Employee và .50.110–.50.199 cho Guest; gateway/DNS là CARP VIP .1. Management dùng tĩnh .99.100/24 và gateway .99.1. Tại lần đầu, Dnsmasq chiếm UDP67 làm Kea không mở socket. Đã di chuyển nguyên pool LAN cũ .1.100–.1.199 từ Dnsmasq sang Kea, giữ Dnsmasq DNS phụ53053; không coi bước sửa xung đột là mở rộng DHCP HA.

Tám rule được thêm theo chức năng: DNS TCP/UDP và ICMP tới VIP cho Employee/Guest; Employee tới DC TCP8000; Management .99.100 ICMP tới VIP. Guest không có rule tới DC nên default deny xử lý ca thử. Không mở any-any cho các vùng để tiện demo.

@TABLE|Kết quả live M3.5 theo phạm vi bảy ca
| Nhóm ca | Kết quả |
|---|---|
| Employee→VIP .40.1 | PASS, ICMP3/3 |
| Guest→VIP .50.1 | PASS, ICMP3/3 |
| Management→VIP .99.1 | PASS, ICMP3/3 |
| Employee DNS qua VIP | PASS, opnsense.internal |
| Guest DNS qua VIP | PASS, opnsense.internal |
| Employee→DC TCP8000 | PASS,3/3 kết nối |
| Guest→DC TCP8000 | PASS,3/3 timeout đúng kỳ vọng |

Ca VPCS không có framebuffer theo công cụ thu hiện tại nên log console JSON là bằng chứng chính; không tạo ảnh VPCS giả. PASS chính sách chỉ áp dụng các ca trên. Chưa nghiệm thu mọi cặp VLAN, quyền quản trị thiết bị, firewall failover lại với rule mới hoặc lease HA. [E10]

## 4.8. XMLRPC và kiểm nhất quán runtime

Hồ sơ XMLRPC cuối ngày06/11 đối chiếu đầy đủ cây XML tám rule và ba pool: tag, thuộc tính UUID, nội dung và trường con. Tất cả8/8UUID xuất hiện trong pfctl -sr của mỗi firewall; Kea DHCPv4/control agent chạy trên hai máy. Kết hợp log sync HTTP200/restore true đã có để xác nhận đồng bộ cấu hình đúng nhóm, không chỉ tên mô tả trùng. [E11]

Nhóm sync ghi nhận aliases,rules,kea,dnsforwarder. Rule NAT mới ở bước sau được áp tương đương riêng từng máy, không gửi sync toàn cấu hình hoặc tự chọn thêm nhóm NAT. Kết quả Kea running không thay bài kiểm lease synchronization; cấu hình rule trùng không tự chứng minh mọi state đã đồng bộ. Các điểm này được kiểm ở các nhóm nghiệm thu độc lập.

@FIG|docs/evidence/M3/M3-runtime-review-20261106/OPNsense-Primary-status-20261106T194814+0700.png|Runtime Primary trong đợt xác minh cấu hình M3|Mục đích: đối chiếu trạng thái cuối với dữ liệu XML đã so sánh. Nội dung: CARP MASTER, pfsync và Kea. Kết quả: đúng vai trò tại thời điểm ảnh. Ý nghĩa: hỗ trợ nghiệm thu runtime; không thay bằng chứng đầy đủ tám rule/ba pool trong JSON.|06/11/2026 19:48:14, UTC+07:00 theo batch

## 4.9. Điều tra bulk sync và diễn giải snapshot

Một cặp snapshot cũ ghi BACKUP ở cả hai máy nhưng được thu tuần tự. Log cho thấy Primary demotion240 trong pfsync bulk, hoàn tất rồi MASTER; Secondary về BACKUP sau quảng bá Primary. Không có bằng chứng hai máy đồng thời BACKUP từ hai bản thu đó. Báo cáo giữ dữ liệu gốc và sửa diễn giải, không xóa dấu vết bất thường.

Chẩn đoán tiếp xác nhận hook96 gọi lại native sau khi bulk đầu hoàn tất, khởi phát đợt thứ hai ở Primary khoảng673giây theo đồng hồ guest. Tác nhân tái khởi tạo đã xác định; nguyên nhân sâu của thời gian truyền/chờ chưa rõ. Bảy mẫu mỗi máy trong cửa sổ khoảng60giây riêng cho thấy vai trò/syncok đúng, không chứng nhận ổn định dài hạn hoặc sửa xong lỗi độ trễ. [E12]

## 4.10. Employee-Linux và WAN/NAT Internet tối thiểu

Employee-Linux node11 được bổ sung với1vCPU/1GiB, overlay/seed riêng và một NIC VLAN40, giữ VPCS node5. Guest xác nhận DHCP .40.110, gateway .40.1, công cụ curl/SSL và CA trước khi truy cập Internet. Không coi client raw M3.4 hoặc namespace M2 là cùng node Linux này.

EVE6.2.0-4 kiểm kê không có type NAT Cloud hoạt động như dự định ban đầu. Phương án sau duyệt dùng pnet0/network12 và gateway .220.2. Việc chỉ cập nhật API metadata chưa chứng minh chuyển runtime nên giao dịch cuối đổi đúng hai WAN TAP vunl0_1_1/vunl0_2_1 cùng metadata; không chuyển bridge quản trị EVE.

Trước đổi đã sao lưu lab/config và arm watchdog180giây. Guard kiểm node UUID/PID, đúng TAP, route quản trị, CARP/syncok/demotion và hash các phần bảo vệ. Watchdog chỉ rollback theo điều kiện giao dịch nhằm tránh ghi đè thay đổi cạnh tranh; được disarm khi kết quả đúng. Không restart node để đổi WAN trong cửa sổ nghiệm thu. [E13]

@TABLE|WAN và NAT được nghiệm thu ngày06/11
| Thuộc tính | Kết quả |
|---|---|
| Primary WAN vtnet1 | DHCP192.168.220.144/24 |
| Secondary WAN vtnet1 | DHCP192.168.220.145/24 |
| Gateway/default route | 192.168.220.2, đã có IPv4 default route |
| EVE quản trị | pnet0 vẫn192.168.220.143/24; SSH thu kết quả được |
| Rule mới | Nguồn .40.110/32→1.1.1.1/32 TCP443, pass và keep state |
| NAT | Hybrid SNAT cùng phạm vi, translation WAN interface address |
| HTTPS | Một HEAD, curlrc0, TLSverify0, HTTP301; không retry/proxy/redirect |
| SYN trước NAT | .40.110:52552→1.1.1.1:443 |
| SYN sau NAT | .220.144:58206→1.1.1.1:443; cùng sequence240639040 |

Biểu diễn PF đã nạp theo báo cáo nghiệm thu:

```text
nat log on vtnet1 inet proto tcp from 192.168.40.110 to 1.1.1.1 port = https -> (vtnet1:0) port 1024:65535
```

vtnet1 xác định egress; nguồn/đích/cổng giới hạn ca thử; địa chỉ WAN động được dùng làm nguồn ra. NAT giữ cơ chế state để phản hồi quay về endpoint. Một ca HTTPS thành công có chứng chỉ kiểm đúng là bằng chứng dịch nguồn và ứng dụng, không chứng minh mọi website hoặc DNS Internet.

@FIG|docs/evidence/M3/M3-WAN-NAT-live-20261106/OPNsense-Primary-status-20261106T214654+0700.png|Primary sau WAN/NAT: địa chỉ, SNAT và HA|Mục đích: kiểm cấu hình runtime sau đổi WAN. Nội dung: WAN .144/gateway .2, rule dịch nguồn và năm MASTER/syncok1. Kết quả: guard cuối đạt. Ý nghĩa: bảo toàn HA trong cửa sổ đổi mạng, chưa kiểm NAT failover.|06/11/2026 21:46:54, UTC+07:00 theo batch

@FIG|docs/evidence/M3/M3-WAN-NAT-live-20261106/OPNsense-Secondary-status-20261106T214654+0700.png|Secondary sau WAN/NAT và trạng thái BACKUP|Mục đích: xác minh máy dự phòng có cấu hình tương đương. Nội dung: WAN .145, rule NAT và năm BACKUP/syncok1. Kết quả: vai trò cuối phù hợp. Ý nghĩa: không suy hai địa chỉ WAN riêng thành WAN VIP hoặc continuity Internet.|06/11/2026 21:46:54, UTC+07:00 theo batch

@FIG|docs/evidence/M3/M3-WAN-NAT-live-20261106/Employee-Linux-status-20261106T214535+0700.png|Employee-Linux nhận phản hồi HTTPS qua SNAT|Mục đích: chứng minh đúng nguồn/đích và kết quả ứng dụng. Nội dung: .40.110→1.1.1.1:443, HTTP301, TLSverify0/curlrc0, request1. Kết quả: PASS trong một lần HEAD. Ý nghĩa: PCAP cùng SYN bổ sung chứng minh NAT; không dùng thời gian curl làm SLA.|06/11/2026 21:45:35, UTC+07:00 theo batch

## 4.11. Tổng hợp nghiệm thu và giới hạn M3

@TABLE|Kết luận theo từng hạng mục M3
| Hạng mục | Kết luận | Giới hạn chính |
|---|---|---|
| M3.1 pfsync persistent | PASS | Đúng boot/runtime đã thử |
| M3.2 CARP5VLAN | PASS | Địa chỉ/VHID/role đúng |
| M3.3 failover/recovery | PASS | Chuyển VIP và phục hồi readiness |
| M3.4B state/continuity | PASS | Một phiên TCP/HTTP nội bộ |
| M3.5 DHCP/DNS/firewall | PASS | Bảy ca live và tám rule đã giao |
| XMLRPC/runtime | PASS phạm vi | Tám rule/ba pool, không toàn cấu hình |
| WAN/NAT | PASS phạm vi | Một HTTPS từ Employee tới1.1.1.1 |
| NAT HA, DHCP lease HA, zero loss/SLA | DESIGN ONLY/chưa nghiệm thu | Không có WAN VIP, không có bài thử tương ứng |

M3 DONE/PASS theo các hạng mục độc lập đã giao và nghiệm thu, theo báo cáo cuối06/11. Trạng thái NAT BLOCKED trong các checkpoint sớm không còn là kết luận cuối của phần NAT tối thiểu. Đồng thời, không mở rộng PASS thành toàn bộ SOC, mọi protocol, mọi endpoint hoặc mọi tình huống hỏng đã được kiểm. Sự kiện EVE reboot/ngừng QEMU ngày07/11 chặn M4 hiện hành nhưng không xóa kết quả nghiệm thu lịch sử M3.

# CHƯƠNG 5. M4 — TRIỂN KHAI GIÁM SÁT SOC

## 5.1. Mục tiêu và kiến trúc dữ liệu

M4 nối hạ tầng mạng với khả năng quan sát, phát hiện và thu nhận sự kiện. Có hai nhánh cần phân biệt: Core mirror→Suricata→EVE JSON và OPNsense Syslog→Wazuh. Nhánh phân tích EVE ở Manager còn cần cơ chế chuyển dữ liệu sensor→Manager; không dùng kết quả Syslog để thay nghiệm thu EVE hoặc ngược lại.

Kiến trúc đã có bằng chứng ở các phần riêng: Core tạo bản sao, sensor phát hiện marker thật, Manager xử lý replay thật. Đường live giữa sensor và Manager chưa được nghiệm thu. Trong hồ sơ, thử Manager/replay được lưu dưới thư mục M5 lịch sử; báo cáo sử dụng phần liên quan tích hợp M4 và giữ rõ xuất xứ, không kết luận giai đoạn M5 đã hoàn thành.

## 5.2. Cài và cấu hình Suricata NIDS

Suricata7.0.3 được cài trên node sensor hai NIC: capture0/enp0s3 không IP cho bản sao, mgmt0/enp0s4 riêng trên segment Management. Cấu hình công khai lịch sử cho thấy cả hai interface chưa có IP ở thời điểm thu; không tự gán .99.20 từ thiết kế thành kết quả đã triển khai.

Kiểm suricata cấu hình PASS và service active chỉ là baseline. Unit thực tế sử dụng chế độ pcap capture0, runmode single, tệp cấu hình Suricata, bộ rule lab và thư mục log riêng. Ý nghĩa là engine đọc gói từ NIC capture thay vì inline forwarding, không tạo cơ chế chặn ngay trên tuyến người dùng.

```text
/usr/bin/suricata --pcap=capture0 --runmode=single -c /etc/suricata/suricata.yaml -S /etc/suricata/rules/soc-lab.rules -l /var/log/suricata
```

Đây là ExecStart đã ghi trong sensor-configuration-public.json. capture0 chọn điểm thu; -c chọn cấu hình; -S chọn bộ rule lab; -l chọn thư mục log. Không từ lệnh này suy mọi rule sản xuất đã nạp hoặc gói nào cũng được phát hiện. Cảnh báo offloading/ethtool trong journal được giữ nguyên, chưa có kết luận xử lý hết cảnh báo hoặc tối ưu hiệu năng. [E14]

@FIG|docs/evidence/M4/topology-first-20261102/sensor-configure-result-20261102T132952+0700.png|Kết quả cấu hình sensor tại console thực tế|Mục đích: ghi nhận bước áp cấu hình và kiểm engine. Nội dung: kết quả công cụ tại guest sensor. Kết quả chức năng được đọc thêm từ JSON public và alert live ở phần sau. Ý nghĩa: ảnh bước cấu hình không được thay bằng chứng phát hiện hoặc vận chuyển log.|02/11/2026 13:29:52, UTC+07:00 theo tên batch

## 5.3. Kiểm thử frame thật và cảnh báo EVE

Nguồn thử là host bơm hữu hạn hai frame ICMP lành tính vào TAP Core access30: một marker khớp, một marker không khớp rule. Cả hai tới TAP sensor. Đây không phải ping từ VPCS/DC hoặc tấn công thật; không yêu cầu reply để chứng minh sensor quan sát được bản sao. File live-mirror-frames.json nêu rõ scope này.

Sự kiện sau marker ghi service active, capture0 UP và không IP; alert thật có SID1000001, rev1, ICMP, .30.101→.30.102, VLAN[30], flow_id9396033340943. Đó là bằng chứng engine phát hiện nguồn thử trong đường mirror live, vượt mức chỉ kiểm cấu hình. Không suy toàn bộ bộ luật hoặc mọi event giao thức đã được nghiệm thu.

@TABLE|Các trường EVE thật được dùng đối chiếu
| Trường | Giá trị có trong hồ sơ |
|---|---|
| event_type / in_iface | alert / capture0 |
| src_ip / dest_ip | 192.168.30.101 / 192.168.30.102 |
| proto / icmp_type | ICMP / 8 |
| vlan | [30] |
| signature_id / rev | 1000001 / 1 |
| signature | SOC M4 benign ICMP marker |
| flow_id | 9396033340943 |
| action / severity | allowed / 3 |

action=allowed phù hợp quan sát IDS thụ động, không chứng minh chặn IP. Bản tóm tắt TAP có vlan=null trong khi JSON Suricata có VLAN[30]; không sửa tệp nguồn để đồng nhất. Thời gian guest có offset+0000 nhưng chưa tin cậy, dùng collector17:01–17:02 UTC+07:00 và marker/flow để liên hệ, không quy đổi giờ guest thành mốc thu chính xác. [E14]

@FIG|docs/evidence/M4/resume-20261102/sensor-export-after-marker-20261102T170219+0700.png|Console sensor xuất trạng thái sau marker live|Mục đích: truy vết dữ liệu sau thử marker. Nội dung: lệnh đọc EVE/runtime và thông báo đã xuất public state. Kết quả alert được xác nhận ở sensor-public-after-marker.json, không tuyên bố toàn bộ JSON xuất hiện trên ảnh. Ý nghĩa: ảnh là minh chứng thao tác thu thực tế, đi kèm tệp dữ liệu để kiểm giá trị.|02/11/2026 17:02:19, UTC+07:00 theo tên batch

## 5.4. Wazuh Manager và lỗi startup timeout

Manager4.14.9-1 có gói cài trước khi thử. Audit ngày02/11 phát hiện service failed do TimeoutStartUSec45s, chưa có drop-in hiệu lực; logcollector không chạy và tệp replay còn rỗng. Đây là lỗi khởi động dịch vụ, không chứng minh rule EVE sai hoặc mọi thành phần Wazuh đã mất.

Sau lưu unit/config theo hồ sơ, đã tạo drop-in soc-timeout.conf trong /etc/systemd/system/wazuh-manager.service.d với TimeoutStartSec300, nạp lại systemd và start Manager. Audit sau xác nhận active/running, timeout5phút và đúng đường drop-in. Chưa thử reboot sau sửa nên không khẳng định persistence timeout đã được nghiệm thu qua reboot.

analysisd, logcollector, remoted, db và apid có chạy; một số daemon tùy chọn không chạy được giữ nguyên trong output. wazuh-control status có thể rc1 khi còn thành phần không chạy, không chỉ từ mã này kết luận Manager hỏng. Không nới quyền tệp replay để tiện thử; logcollector đọc tệp root:root mode0644 theo hồ sơ. [E15]

@FIG|docs/evidence/M5/continuation-20261102/timeout-effective-20261102T204330+0700.png|Timeout Manager300giây được cấu hình trên đĩa và có hiệu lực|Mục đích: xác nhận cách xử lý lỗi startup. Nội dung: drop-in và TimeoutStartUSec5min. Kết quả: timeout được nạp; service tại ảnh còn activating, trạng thái active được xác nhận ở ảnh tiếp theo. Ý nghĩa: không dùng ảnh đang khởi động để khẳng định Manager đã hoạt động.|02/11/2026 20:43:30, UTC+07:00 theo tên batch

@FIG|docs/evidence/M5/continuation-20261102/manager-components-packages-20261102T204613+0700.png|Manager và phạm vi thành phần Wazuh đã cài|Mục đích: kiểm kê chính xác thành phần. Nội dung: Manager, daemon và truy vấn gói. Kết quả: Manager4.14.9-1 active; chưa có Indexer/Dashboard/Filebeat trên node lịch sử. Ý nghĩa: không trình bày bộ Wazuh đầy đủ hoặc giao diện Dashboard đang vận hành.|02/11/2026 20:46:13, UTC+07:00 theo tên batch

## 5.5. Replay EVE thật vào Wazuh và giới hạn tích hợp

Bài thử nạp lại một dòng EVE thật đã lưu vào /var/log/soc-suricata-replay.json. localfile JSON để logcollector đọc tự động; Manager giải mã và tạo alert mới trong alerts.json. Mốc byte trước append được lưu để chỉ tìm phần alert phát sinh sau lần thử, không dùng alert cũ làm kết quả mới.

Nguồn thật có SHA-256 ce69196abe7eb37559d534040eed5d41ae3fc09e6fc0e0116b61bd85b0aec5f6; dữ liệu khớp IP, ICMP, VLAN[30], capture0, SID1000001, signature và flow_id9396033340943. Wazuh rule86601 mức3 xử lý dữ liệu này. Alert không có full_log trong mẫu nên đối chiếu trường giải mã; category rỗng bị lược trong data không được diễn giải là nguyên byte JSON giống nhau. [E15]

Verifier đầu chỉ tìm rule100101 hoặc full_log nên ghi chưa khớp. Sau xem alert thật, phần đọc lại vùng mới từ mốc cũ xác nhận rule86601; không append lại chỉ để tạo bằng chứng. Các kết quả thiếu khớp ban đầu được giữ làm chẩn đoán. JSON mô phỏng riêng có soc_test_id và rule100101/mức8, được dán nhãn synthetic, không giả làm sự kiện mạng thật.

@FIG|docs/evidence/M5/continuation-20261102/real-replay-verified-20261102T205956+0700.png|Wazuh tạo cảnh báo từ replay EVE thật|Mục đích: kiểm chặng tệp JSON→phân tích Manager→alert. Nội dung: nguồn/hash, rule86601 và trường tương quan. Kết quả: replay đạt, không xác nhận truyền sensor trực tiếp. Ý nghĩa: hai chặng ở hai thời điểm chưa thay bài nghiệm thu live Core→Suricata→Wazuh.|02/11/2026 20:59:56, UTC+07:00 theo tên batch

## 5.6. Kết nối OPNsense–Wazuh và Syslog ngày07/11

Checkpoint mới nhất ghi M4.3 PARTIAL/BLOCKED và M4.4 BLOCKED. Sau chẩn đoán, EVE SSH bằng khóa hợp lệ đã hoạt động, nhưng EVE vừa reboot và không có QEMU; Primary .220.144 offline, ping không đạt và neighbor FAILED. Wazuh .220.146 hoạt động ngoài runtime QEMU EVE, ping từ EVE2/2 và TCP22 mở; khóa soc-admin đã seed bị từ chối.

TCP514 tại Wazuh trả Connection refused, chưa có listener Syslog TCP tại cổng đó trong phép kiểm. Không suy trạng thái UDP514 hoặc cho rằng SSH mở chứng minh ingest log. Chưa cấu hình đích gửi Syslog, chưa xác minh log firewall có nguồn/thời gian/nội dung ở phía nhận. Không có ảnh Dashboard hoặc Syslog thật đã đạt để đưa vào báo cáo. [E16]

@TABLE|Trạng thái cuối của các tầng giám sát
| Tầng | Kết luận | Bằng chứng/thiếu hụt |
|---|---|---|
| Core Mirror | PASS lịch sử | OVS Mirror, PCAP marker, counter |
| Sensor service và marker alert live | PASS phạm vi | Public sensor JSON và frame thật |
| Manager xử lý replay | PASS phạm vi | Alert mới rule86601, hash/field khớp |
| Sensor→Manager tự động live | PARTIAL toàn chuỗi | Chặng vận chuyển chưa triển khai/kiểm chứng |
| Quản trị phục vụ M4.3 | BLOCKED nghiệm thu | Primary offline; Wazuh từ chối khóa |
| Syslog firewall M4.4 | BLOCKED | Chưa cấu hình/nhận log thật |
| Indexer/Dashboard/Filebeat | DESIGN ONLY theo kiểm kê lịch sử | Chưa có gói; chưa kiểm kê đầy đủ instance VMware |
| Automation block IP thật | DESIGN ONLY | Chưa có nghiệm thu thay đổi firewall tự động |

## 5.7. Phương án hoàn thiện và tiêu chí nghiệm thu còn lại

Phương án tiếp tục không thực thi trong đợt viết báo cáo. Trước hết cần cửa sổ được duyệt để có Primary và đường quản trị Wazuh xác thực hợp lệ. Không bật thêm node Wazuh EVE nếu .146 VMware đang tồn tại mà chưa kiểm trùng IP. Sau đó sao lưu config OPNsense/ossec.conf trước cấu hình log tối thiểu, giữ Core, HA, NAT và policy ngoài phạm vi được phép.

Với Syslog, cần chốt nguồn/đích/giao thức/cổng thực tế, kiểm listener, nhận log firewall phát sinh tự nhiên và đối chiếu host/IP, timestamp/múi giờ, nội dung. Phân biệt nhận packet, ghi log và tạo alert. Với EVE, phương án agent đọc eve.json cần bằng chứng cài/đăng ký, quyền đọc và sự kiện mới tự chuyển tới Manager; replay trong sensor hoặc copy thủ công vẫn phải ghi đúng nguồn thử.

Nghiệm thu toàn chuỗi phải có nguồn frame mới với marker riêng, Core/sensor/Manager đồng thời hoạt động đủ tài nguyên và cùng sự kiện được liên hệ ở cả hai đầu. Nếu muốn Dashboard, cần cài/kiểm Indexer và Dashboard, sau đó truy vấn đúng alert mới; không dùng ảnh mockup hoặc ảnh giao diện bên ngoài. Tài nguyên, đồng bộ thời gian và rollback phải được đánh giá trước khi thay hệ thống. [E15; E16]

# CHƯƠNG 6. ĐÁNH GIÁ VÀ KẾT LUẬN

## 6.1. Tổng hợp M1–M4

@TABLE|Đối chiếu kết quả theo giai đoạn và bằng chứng mới nhất
| Giai đoạn | Kết quả đã có | Phân loại cuối | Không suy rộng |
|---|---|---|---|
| M1 | Thiết kế, mapping, năm VLAN, topology EVE và Wazuh nối cấu trúc | PASS phạm vi | Không phải mọi dịch vụ/endpoint đã hoạt động |
| M2 | Core L2, access/trunk/mirror,95/95frame; ba ca routing/policy | PASS phạm vi | Không mọi cặp VLAN/port/IPv6; LACP không áp dụng |
| M3 | CARP/pfsync, failover/recovery, một TCP; DHCP/DNS/rule/XMLRPC; một HTTPS NAT | PASS hạng mục được giao | Không NAT HA, lease HA, zero loss/SLA |
| M4 | Sensor marker live và Manager replay đã đạt riêng | PARTIAL; M4.3–M4.4 BLOCKED | Chưa log live, Syslog, Dashboard hoặc automation thật |

## 6.2. Vai trò cá nhân và đóng góp kỹ thuật

Đóng góp trọng tâm nằm ở biến sơ đồ phân vùng thành topology có mapping, xây dựng Core L2 và kiểm chứng hành vi frame, đưa các gateway/firewall lên OPNsense và xác minh HA theo nhiều lớp. Giá trị không chỉ là cấu hình “có” trên giao diện mà là chuỗi bằng chứng từ persistent config tới runtime và traffic.

Đối với M3, phần việc thể hiện ở phân biệt state sync với config sync, dùng cùng TCP session để kiểm continuity, thiết kế guard/rollback khi chuyển WAN và giữ phạm vi egress tối thiểu. Đối với giám sát, phần việc là xác định điểm mirror đúng, chứng minh sensor tạo alert thật, sau đó đánh giá chặng replay Manager và chỉ ra đoạn vận chuyển còn thiếu.

Báo cáo cá nhân dựa trên hồ sơ nghiệm thu thuộc phạm vi này, không khẳng định tác giả duy nhất của mọi script/tệp hoặc nhận toàn bộ hệ thống nhóm là sản phẩm cá nhân. Họ tên/MSSV và xác nhận phân công chính thức được để trống ở trang đầu khi chưa có dữ liệu định danh đáng tin cậy cho người yêu cầu.

## 6.3. Khó khăn và bài học rút ra

Các lỗi chuẩn bị/cài đặt cho thấy phải phân biệt offline repository với kết nối Internet, route multicast host với route người dùng, và metadata với liên kết runtime. Từ đó, mỗi bước cần baseline, guard và cách kiểm độc lập để tránh “sửa cho chạy” mà không biết điều gì đã thay đổi.

Các lỗi HA cho thấy trạng thái thu tuần tự có thể bị đọc sai như quan sát đồng thời; packet pfsync hai chiều không đủ chứng minh state một flow. Bài thử gián đoạn cần giữ nguyên trạng thái thiếu dữ liệu, tạo session mới ở lần thử được phép và không gộp kết quả. Tương tự, Manager active không chứng minh Dashboard hoặc live pipeline, còn sai điều kiện tìm alert trong verifier không tự là lỗi engine phân tích.

Việc lưu cấu hình raw có thể chứa bí mật nên báo cáo chỉ sử dụng dữ liệu public, hash và vị trí backup thay vì đưa password/config thô vào phụ lục. Ảnh thật cần được giải thích bằng mục đích, nội dung, kết quả và ý nghĩa, tránh để một màn hình nhiều dòng dẫn tới kết luận rộng hơn ca thử.

## 6.4. Hạn chế và hướng phát triển

Hạn chế kỹ thuật còn gồm single Core, giới hạn RAM/đồng thời node, chưa đồng bộ thời gian đầy đủ, chưa điều tra xong bulk kéo dài, chưa kiểm mọi protocol và tải dài hạn. Chính sách liên vùng mới có các ca chọn lọc, hai rule LAN parent rộng còn cần rà soát trong phạm vi thay đổi được duyệt. WAN VIP và continuity NAT/DHCP chưa nghiệm thu.

Hướng phát triển ưu tiên hoàn thiện quản trị Wazuh, Syslog và vận chuyển EVE live; đồng bộ thời gian, bổ sung kiểm thử có nguồn/đích và tiêu chí rõ; sau đó mới hoàn thiện Indexer/Dashboard và đánh giá automation. Các mở rộng phải giữ protected scope của Core L2 và HA đã nghiệm thu, có backup/rollback và không dùng lưu lượng gây hại để thay việc kiểm thử được kiểm soát.

## 6.5. Kết luận

Đồ án đã có nền mạng phân vùng hoạt động, gateway tập trung trên OPNsense và HA được kiểm chứng ở mức CARP, state và một phiên TCP. Cùng với DHCP/DNS/firewall, XMLRPC và NAT tối thiểu, các kết quả này đáp ứng các hạng mục M1–M3 đã được giao và nghiệm thu. Bằng chứng gồm ảnh console/topology, JSON, log và PCAP có liên kết tới từng kết luận.

Giám sát SOC mới hoàn thiện từng phần: điểm sao chép và phát hiện Suricata đã có cảnh báo thật, Manager đã phân tích replay có đối chiếu nguồn; tích hợp truyền log trực tiếp và Syslog còn thiếu, M4 hiện chưa hoàn thành. Báo cáo phản ánh chính xác ranh giới đó để kết quả có thể được bảo vệ bằng bằng chứng, đồng thời chỉ rõ điều kiện kỹ thuật cho bước triển khai tiếp theo.
