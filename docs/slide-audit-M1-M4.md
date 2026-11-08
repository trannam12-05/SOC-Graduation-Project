# 1. Đối chiếu slide 12, 13, 14 và 16 với triển khai M1–M4

## 1.1. Phạm vi và phương pháp

Ngày lập: **08/11/2026, UTC+07:00**. Đối tượng là bốn ảnh slide người dùng cung cấp; không chỉnh sửa tệp thuyết trình. Đối chiếu hồ sơ và minh chứng đã lưu tại `D:\SOC`; không truy cập hoặc thay đổi EVE-NG, VMware, OPNsense, Wazuh; không chạy lại phép thử đã nghiệm thu. Không tạo ảnh mới hoặc sửa ảnh gốc.

**PASS**: có minh chứng nghiệm thu đúng phạm vi; **PARTIAL**: một phần đã kiểm chứng, còn thiếu phạm vi hoặc tích hợp; **BLOCKED**: chưa thể nghiệm thu vì điều kiện cụ thể; **DESIGN ONLY**: phương án/chức năng chưa có minh chứng triển khai. Với phát biểu sai trên slide, bảng ghi rõ sai lệch; nhãn trạng thái mô tả hạng mục thực tế, không phải xác nhận câu sai là PASS.

PASS trong báo cáo là **kết quả lịch sử có thời điểm**, không chứng nhận hệ thống đang chạy ngày lập báo cáo. Hồ sơ mới nhất ngày 07/11 ghi EVE vừa reboot, không có QEMU và Primary offline; điều này chặn kiểm tra log M4, không hủy nghiệm thu M3 trước đó.

## 1.2. Hồ sơ nghiệm thu đã đối chiếu

| Mã | Báo cáo, hồ sơ chính | Phạm vi sử dụng |
|---|---|---|
| E1 | [M1 nghiệm thu cuối](M1/M1-final-acceptance-20261105.md), [thiết kế hợp nhất](M1/M1-design-consolidated-20261105.md), [đính chính nhãn](M1/M1-topology-label-correction-20261105.md) | Topology, VLAN/IP, mapping, phân biệt node và dịch vụ |
| E2 | [M2 tổng kết nghiệm thu](M2/M2-final-summary-20261103.md), [kết quả](evidence/M2/final-acceptance-20261103/M2-results.json) | Core L2, access/trunk, routing, firewall, mirror; tái sử dụng suite frame 95/95 |
| E3 | [M3.1–M3.2](M3/M3-todo-completion-20261103.md), [M3.3 nghiệm thu](evidence/M3/M3.3-failover-20261104/run-105204/M3.3-acceptance.json) | pfsync persistent, CARP năm VLAN, failover/recovery |
| E4 | [M3.4B báo cáo](evidence/M3/M3.4B-pfsync-state-20261104/evidence-index.md), [nghiệm thu](evidence/M3/M3.4B-pfsync-state-20261104/M3.4-acceptance.json) | Native state và một phiên TCP qua failover; recovery |
| E5 | [M3.5 dịch vụ mạng](M3/M3.5-network-services-steps-1-5-20261105.md), [nghiệm thu](evidence/M3/M3.5-network-services-20261105/M3.5-acceptance.json) | DHCP/DNS, endpoint và tám rule |
| E6 | [M3 XMLRPC/runtime](M3/M3-runtime-verification-20261106.md), [nghiệm thu](evidence/M3/M3-runtime-review-20261106/acceptance.json), [đính chính HA](M3/M3-ha-wan-final-review-20261106.md), [chẩn đoán bulk](M3/M3-pfsync-cause-NAT-proposal-20261106.md) | Đồng bộ tám rule/ba pool, runtime và giới hạn bulk sync |
| E7 | [M3 WAN/NAT nghiệm thu cuối](M3/M3-WAN-NAT-final-acceptance-20261106.md), [nghiệm thu](evidence/M3/M3-WAN-NAT-live-20261106/M3-WAN-NAT-acceptance.json) | Kết quả thay các checkpoint NAT BLOCKED trước đó |
| E8 | [M4 live mirror](evidence/M4/resume-20261102/live-mirror-frames.json), [sensor sau marker](evidence/M4/resume-20261102/sensor-public-after-marker.json), [cấu hình sensor](evidence/M4/topology-first-20261102/sensor-configuration-public.json) | Frame thực tới sensor, service và alert thật |
| E9 | [Báo cáo Manager/replay](M5-verification-and-demo-20261102.md), [đối chiếu dữ liệu](evidence/M5/continuation-20261102/decoded-field-validation.json), [đề xuất live](M5-live-pipeline-proposal-20261102.md) | Chỉ đọc phần liên quan đầu ra M4; không coi M5 hoàn thành |
| E10 | [M4.3–M4.4](evidence/M4/M4.3-M4.4-20261107/report.md), [chẩn đoán](evidence/M4/M4.3-M4.4-20261107/retry-diagnosis-20261107.txt) | Trạng thái quản trị/đường log mới nhất |

Đã đọc [SOC_TO_DO.md](SOC_TO_DO.md) và quy định `AGENTS.md`. Các checkpoint cũ trong TODO là lịch sử: “chưa failover”, “WAN cô lập”, “Wazuh chưa nối” phải đọc cùng nghiệm thu mới tương ứng; không chọn một dòng cũ làm kết luận hiện hành. Các bản PREPARED/PROPOSED chỉ dùng phân biệt thiết kế với kết quả. Dùng báo cáo Markdown và JSON gốc liên quan, không giải nén gói nguồn hoặc đọc lặp bản Word cùng nội dung.

# 2. Kết quả triển khai có thể trình bày

## 2.1. VLAN, subnet và gateway

Các địa chỉ dưới đây **đã kiểm chứng M3**, không còn chỉ là đề xuất M1 (E3, E4).

| VLAN / vùng | Subnet | Primary | Secondary | CARP VIP / gateway thiết kế endpoint | Trạng thái |
|---|---|---|---|---|---|
| 30 / Data Center | 192.168.30.0/24 | 192.168.30.2/24 | 192.168.30.3/24 | 192.168.30.1/24 | PASS |
| 40 / Employee | 192.168.40.0/24 | 192.168.40.2/24 | 192.168.40.3/24 | 192.168.40.1/24 | PASS |
| 50 / Guest | 192.168.50.0/24 | 192.168.50.2/24 | 192.168.50.3/24 | 192.168.50.1/24 | PASS |
| 60 / DMZ | 192.168.60.0/24 | 192.168.60.2/24 | 192.168.60.3/24 | 192.168.60.1/24 | PASS |
| 99 / Management | 192.168.99.0/24 | 192.168.99.2/24 | 192.168.99.3/24 | 192.168.99.1/24 | PASS |

**VLAN 10, subnet 192.168.10.0/24 và VIP 192.168.10.1 trên slide 12–13 sai so với triển khai.** Phải thay bằng VLAN 60 và dải `.60`.

Không suy mọi endpoint đã dùng VIP làm default gateway. DC `.30.10` giữ default route `.30.2`; bài M3.4 chỉ thêm route runtime `.40.100/32 via .30.1`. Employee/Guest nhận DHCP `.40.110`/`.50.110`, gateway và DNS VIP `.1`; Management tĩnh `.99.100/24`, gateway `.99.1` (E5). Employee-Linux bổ sung ngày 06/11 nhận `.40.110` trong cửa sổ riêng (E7); không khẳng định VPCS và Linux dùng địa chỉ đó đồng thời.

SYNC: `10.255.255.0/30`, Primary `vtnet2=10.255.255.1`, Secondary `vtnet2=10.255.255.2` — PASS. Không dùng mạng này làm đường log người dùng. IP quản trị sensor `.99.20` và Wazuh `.99.30` trong M1 vẫn **DESIGN ONLY**; hồ sơ mới xác nhận Wazuh VMware `.220.146`, không chứng minh `.99.30` đã triển khai hoặc đồng nhất hai instance.

## 2.2. Ma trận xác minh chức năng

| Hạng mục | Phân loại | Bằng chứng và giới hạn |
|---|---|---|
| Core chỉ Layer 2; access/trunk năm VLAN | PASS | E2: không IP ngoài loopback, IPv4/IPv6 forwarding=0; suite frame 95/95; routing thực tại OPNsense |
| Inter-VLAN qua OPNsense | PASS | E2: HTTP200 `.40.100 → .30.10:8000`, cùng SYN đổi tag40→30, TTL64→63 |
| CARP năm VIP | PASS | E3: VHID30/40/50/60/99; advbase1, skew Primary0/Secondary100; đúng VIP và ARP |
| CARP failover và recovery M3.3 | PASS | 04/11, nghiệm thu 11:07:14+07:00: shutdown mềm Primary, Secondary MASTER năm VLAN; boot Primary tự MASTER, Secondary BACKUP; không sửa tham số CARP để tạo kết quả |
| pfsync persistent và đồng bộ state | PASS | E3–E4: sau reboot tự áp; pfsync UP/RUNNING, syncok1; hai state ID/creator khớp trước và sau takeover |
| Một phiên TCP nội bộ qua failover M3.4B | PASS | 04/11, nghiệm thu 17:12:50+07:00: `.40.100:44341 → .30.10:8000`, một SYN, không reconnect, 11 marker ACK sau Primary OFF, HTTP200/350 byte; recovery đúng năm VLAN |
| Giữ phiên qua cả recovery, zero loss, SLA failover | DESIGN ONLY | Chưa nghiệm thu các bảo đảm này. HTTP đã đóng trước recovery; khoảng watcher→read-start không phải downtime |
| XMLRPC cấu hình | PASS | E6: log sync HTTP200/restore true, đầy đủ XML tám rule/ba pool khớp; 8/8 UUID nạp trên mỗi firewall. Không suy đồng bộ mọi nhóm hoặc blocklist runtime |
| DHCP/DNS Employee và Guest | PASS | E5: lease, gateway/DNS VIP và ca DNS thực; Kea chạy hai bên trong E6 |
| DHCP lease HA/failover | DESIGN ONLY | Đồng bộ cấu hình pool và service running không chứng minh lease synchronization/failover |
| Firewall các ca đã nghiệm thu | PASS | E2: một ca dương/hai ca âm kèm PCAP/counter; E5: Employee→DC TCP8000 cho phép, Guest→DC TCP8000 chặn |
| Toàn bộ ma trận phân vùng/least privilege | PARTIAL | Chưa kiểm mọi cặp VLAN/port/IPv6; hai rule LAN parent rộng còn được ghi nhận. Management chỉ có kiểm ICMP VIP, chưa chứng minh toàn bộ quyền quản trị |
| WAN và SNAT tối thiểu | PASS | E7: WAN Primary `.220.144/24`, Secondary `.220.145/24`, gateway `.220.2`; Hybrid SNAT, một HTTPS HEAD `.40.110→1.1.1.1:443`, HTTP301/TLSverify0/curlrc0; PCAP chứng minh dịch nguồn |
| WAN VIP, NAT HA giữ phiên; Internet→DMZ | DESIGN ONLY | Chưa có WAN VIP; NAT dùng địa chỉ WAN riêng; chưa nghiệm thu DNAT/công bố DMZ hoặc continuity Internet |
| SPAN/Port Mirror | PASS | E2: mirror ingress ens3–ens9, chọn VLAN30/40/50/60/99, output ens10; marker GET trong PCAP, counter48. Không phải SPAN toàn bộ mọi traffic WAN/SYNC |
| Sensor Suricata thụ động và alert live | PASS | E8: Suricata7.0.3 active, capture0 không IP, nhận marker và tạo SID1000001. Nguồn là frame lành tính từ host bơm vào TAP access Core, không phải ping endpoint hay tấn công thật |
| EVE JSON → Wazuh xử lý replay cục bộ | PASS | E9: đọc `/var/log/soc-suricata-replay.json` thành rule86601 level3; hash, flow_id, SID, IP và VLAN khớp |
| Toàn chuỗi live Core→sensor→Wazuh | PARTIAL | Hai chặng phát hiện và replay đã đạt riêng; chưa triển khai/kiểm chứng vận chuyển tự động sensor→Manager |
| M4.3 kết nối quản trị/phục vụ tích hợp | BLOCKED | E10: EVE SSH đã phục hồi, nhưng Primary offline, Wazuh `.146` từ chối khóa soc-admin; ping/SSH TCP không chứng minh ingest log |
| M4.4 log firewall OPNsense→Wazuh | BLOCKED | Chưa cấu hình/nhận Syslog; TCP514 refused. Không suy UDP514 cũng đóng |

M3 DONE/PASS **trong các hạng mục đã giao/nghiệm thu**, theo E7; không hạ thành chưa failover hoặc NAT còn BLOCKED từ checkpoint cũ. Đồng thời không mở rộng thành toàn bộ HA/SOC hoàn thành. Bulk sync dài và tác động hook96 đã được chẩn đoán một phần; chưa chứng nhận đã khắc phục nguyên nhân sâu hoặc ổn định dài hạn (E6–E7).

## 2.3. Vị trí sensor và luồng EVE JSON

Đường đã kiểm chứng: **Core `e7/ens10` → segment SPAN → Suricata `e0/capture0` → Suricata → EVE JSON**. Nguồn mirror là ingress `ens3–ens9`, gồm năm access và hai trunk. `select_dst_port` rỗng, không mô tả thành mirror hai chiều tất cả cổng. Sensor `e1/mgmt0` tách riêng trên segment Management; cấu hình công khai lịch sử chưa có IP trên cả hai NIC. Capture không làm gateway hoặc forward đường chính.

SID1000001, ICMP `.30.101→.30.102`, VLAN[30], flow_id `9396033340943` có trong alert thật. Bản tóm tắt TAP ghi `vlan=null`; không sửa thành đã xác minh tag tại TAP, vì VLAN30 được xác nhận ở JSON sensor. Đồng hồ guest chưa tin cậy; dùng timestamp collector có múi giờ và marker/flow để đối chiếu.

Đường đã kiểm chứng riêng tại Manager: **sự kiện thật đã lưu → nạp lại có kiểm soát vào `/var/log/soc-suricata-replay.json` → logcollector → JSON decoder/rule86601 → `alerts.json`**. Đây là replay, không phải sensor tự chuyển log. Phương án agent đọc `/var/log/suricata/eve.json` rồi gửi Manager vẫn DESIGN ONLY. Chưa đủ bằng chứng agent cài/đăng ký, quyền đọc, đường truyền và sự kiện mới tương quan hai đầu. EVE JSON là định dạng sự kiện Suricata, không phải dữ liệu topology EVE-NG.

# 3. Bảng đối chiếu và câu chữ thay thế từng slide

## 3.1. Slide 12 — Topology mạng

| Nội dung trên slide | Đánh giá / trạng thái thực tế | Câu chữ hoặc sửa hình cần áp dụng |
|---|---|---|
| Core L2; OPNsense định tuyến liên VLAN; trunk802.1Q | Đúng — PASS, E2 | “Core Open vSwitch chỉ chuyển mạch L2; OPNsense xử lý routing và firewall giữa VLAN.” |
| VLAN10/DMZ, `.10.0/24` | Sai với triển khai — VLAN60 PASS, E3 | Thay tất cả bằng “DMZ · VLAN60 · 192.168.60.0/24”. Dải tiêu đề: “30 · 40 · 50 · 60 · 99”. |
| HA là thiết kế, “chưa có kết quả failover live” | Lỗi thời — PASS phạm vi M3, E3–E4 | “CARP failover/recovery năm VLAN và một phiên TCP nội bộ đã nghiệm thu M3; chưa nghiệm thu NAT HA/zero loss.” |
| Internet nối firewall | PASS tối thiểu, E7; chưa chứng minh mọi dịch vụ Internet | “WAN/NAT: đã thử một Employee-Linux→1.1.1.1 TCP443; chưa có WAN VIP.” |
| Wazuh · Suricata · Elasticsearch/Kibana trong SOC/SIEM | PARTIAL; Elasticsearch/Kibana chưa có bằng chứng triển khai | “Suricata7.0.3 + Wazuh Manager4.14.9; xử lý replay đã đạt; Indexer/Dashboard chưa triển khai theo kiểm kê.” Tách sensor khỏi khối nhận log. |
| Nhánh thu log từ Core tới SOC | DESIGN ONLY về vận chuyển live; dễ nhầm mirror với log | Vẽ “Core mirror→Suricata” là nhánh capture; “Suricata→Wazuh: chưa nghiệm thu truyền live” là nhánh log nét đứt. |
| Web/Mail; AAA/Database/File; Wi-Fi; Windows/Linux | PARTIAL: có endpoint lab; chưa chứng minh đủ các dịch vụ | “DC: Ubuntu/HTTP8000; DMZ: Ubuntu/HTTP80; Employee: VPCS và Linux kiểm thử; Guest: VPCS, chưa triển khai Wi-Fi; AAA/DB/File/Mail/Windows: dự kiến.” |

Topology M1 ngày05/11 là 10node/11segment; E7 đã bổ sung Employee-Linux và upstream thành 11node/12network. Ảnh M1 không được chú thích như topology cuối sau mở rộng WAN. Wazuh e0 nối VLAN99 là PASS cấu trúc EVE; instance VMware `.146` ngày07/11 cần ghi riêng, chưa chứng minh pipeline giữa hai môi trường.

## 3.2. Slide 13 — VLAN và phân vùng bảo mật

| Nội dung trên slide | Đánh giá / trạng thái thực tế | Câu thay thế |
|---|---|---|
| Năm vùng, gateway VIP `.1` | PASS cho cấu hình firewall, E3–E4 | Dùng nguyên bảng mục2.1; ghi “Gateway CARP đã cấu hình/kiểm chứng; không suy mọi endpoint đã đổi default route.” |
| DMZ VLAN10 / `.10.0/24` / `.10.1` | Sai | “60 / DMZ / 192.168.60.0/24 / 192.168.60.1”. |
| Guest→mạng nội bộ: chặn | PARTIAL: mới chứng minh một đích/dịch vụ, E5 | “Guest→DC TCP8000 bị chặn; các luồng nội bộ khác chưa nghiệm thu đầy đủ.” |
| Employee→DC: chỉ dịch vụ nghiệp vụ cho phép | PASS cho TCP8000; PARTIAL nếu hiểu mọi nghiệp vụ | “Employee→192.168.30.10 TCP8000 được phép theo rule đã kiểm thử.” |
| Internet→DMZ/Web-Mail: giới hạn | DESIGN ONLY | “Công bố Web/Mail từ Internet: chưa triển khai/kiểm chứng DNAT.” |
| Management→thiết bị: giới hạn máy/quyền | PARTIAL | “Management .99.100→VIP .99.1 ICMP đã đạt; quyền/cổng quản trị thiết bị chưa nghiệm thu đầy đủ.” |
| Guest ngoại lệ DNS/DHCP | PASS phần đã thử, E5 | “Guest nhận DHCP và DNS qua VIP .50.1; đã kiểm chứng lease/DNS.” Không kết luận HA lease. |
| “Chính sách & HA là phương án thiết kế” | Lỗi thời, đánh đồng mức hoàn thành | “VLAN/CARP và các rule kiểm thử đã triển khai; ma trận phân vùng đầy đủ còn PARTIAL.” |

## 3.3. Slide 14 — OPNsense firewall và HA

| Nội dung trên slide | Đánh giá / trạng thái thực tế | Câu thay thế |
|---|---|---|
| Active–Passive, Primary MASTER/Secondary BACKUP | PASS lịch sử, E3–E4 | “Trạng thái nghiệm thu: Primary MASTER, Secondary BACKUP trên VLAN30/40/50/60/99.” |
| CARP VIP = gateway `.1` | PASS | Giữ; bổ sung năm VLAN đúng và SYNC riêng `10.255.255.0/30`. Không coi WAN cũng có VIP. |
| pfsync đồng bộ state, giảm gián đoạn | PASS trong một phiên nội bộ | “Đã đối chiếu state ID/creator trước–sau failover; một TCP/HTTP session hoàn tất qua Secondary, không reconnect.” |
| XMLRPC đồng bộ cấu hình được chọn | PASS phạm vi E6 | “Đã xác minh tám firewall rule và ba pool DHCP đồng bộ; chưa nghiệm thu lease HA hoặc mọi nhóm cấu hình.” |
| “FW2 tiếp nhận VIP; state và policy cần kiểm chứng riêng” | Đúng nguyên tắc nhưng thiếu kết quả mới | “FW2 tiếp nhận năm VIP; state/continuity đã đạt M3.4B; tám rule đã xác minh runtime hai máy; chưa thử failover lại với bộ rule mới.” |
| “HA/failover live: chưa có phép đo” | Sai với hồ sơ nghiệm thu | “M3.3 failover/recovery PASS; M3.4B giữ một phiên TCP nội bộ PASS. Chưa đo zero loss/SLA; chưa nghiệm thu NAT HA.” |
| Không mặc định đồng bộ blocklist runtime | Đúng giới hạn — DESIGN ONLY cho chức năng này | Giữ: “Chưa kiểm chứng đồng bộ blocklist runtime hoặc automation chặn IP.” |

Không thêm con số downtime từ độ trễ watcher. Recovery chỉ chứng minh vai trò/VIP/pfsync trở lại; không tuyên bố phiên HTTP đã đóng còn sống qua recovery.

## 3.4. Slide 16 — Sensor Suricata NIDS

| Nội dung trên slide | Đánh giá / trạng thái thực tế | Câu thay thế |
|---|---|---|
| Sensor nhận bản sao từ Core, nằm ngoài forwarding chính | Đúng — PASS E2/E8 | “Core ens10→Suricata capture0; sensor thụ động, capture NIC không IP; mgmt0 tách riêng.” |
| SPAN/luồng live cần kiểm chứng riêng | Lỗi thời nếu hiểu chưa từng kiểm chứng | “SPAN đã nghiệm thu M2; Suricata đã phát hiện marker ICMP live M4 (SID1000001).” |
| Thu nhận gói: SPAN/capture NIC/HOME_NET | PARTIAL: gộp ba khái niệm khác nhau | “Nhận gói trên capture0 từ mirror; HOME_NET là biến phạm vi luật, không phải cổng thu.” Chưa ghi giá trị HOME_NET đã xác minh khi thiếu trích cấu hình. |
| Phát hiện chữ ký, SID/rev, flow/giao thức | PASS cho rule marker đã thử | “Đã kiểm rule marker lành tính SID1000001/rev1; chưa nghiệm thu toàn bộ bộ luật/phát hiện tấn công.” |
| EVE: alert/flow/dns/http/tls | PARTIAL | “Đã kiểm chứng event_type=alert có flow_id và dữ liệu flow; chưa nghiệm thu riêng các event flow/dns/http/tls.” Không coi object flow trong alert là event_type=flow. |
| Chuyển tiếp dữ liệu giám sát | PARTIAL | “Wazuh đã xử lý replay EVE thật thành alert86601; truyền trực tiếp sensor→Wazuh chưa nghiệm thu.” |
| timestamp/flow_id/IP/rule ID để đối soát | PASS cho replay | Giữ; thêm VLAN/SID và hash; phân biệt SID1000001 với Wazuh rule86601. Timestamp guest chưa tin cậy. |
| Chặn do firewall/Automation | DESIGN ONLY về tự động hóa | “Suricata đang ở chế độ IDS thụ động; automation chặn IP chưa triển khai/kiểm chứng.” |

# 4. Thành phần SOC còn thiếu và giới hạn kết luận

| Thành phần/kết quả còn thiếu | Trạng thái | Căn cứ |
|---|---|---|
| Agent/forwarder tự động đưa EVE mới từ sensor sang Manager | DESIGN ONLY | E1/E9: phương án, chưa nghiệm thu cài/đăng ký và truyền trực tiếp |
| Chuỗi live từ traffic Core tới alert Wazuh | PARTIAL | Chỉ có hai đoạn tách thời điểm; replay không thay tích hợp live |
| Wazuh Indexer, Dashboard, Filebeat | DESIGN ONLY | E9 kiểm kê không có gói trên Wazuh-SOC; chưa có bằng chứng cài mới trên instance VMware |
| Elasticsearch/Kibana hoạt động | DESIGN ONLY | Không có nghiệm thu trong hồ sơ liên quan; không dùng slide làm bằng chứng đã triển khai |
| Syslog firewall vào Wazuh | BLOCKED | E10: Primary offline, xác thực Wazuh bị từ chối, chưa có log thực tế |
| Automation/API chặn IP, đồng bộ blocklist runtime | DESIGN ONLY | E1/E5/E7: chưa nghiệm thu; không biến rule firewall thủ công thành automation |
| IPS inline, phát hiện tấn công đầy đủ, vận hành SOC liên tục | DESIGN ONLY | Chỉ chứng minh IDS thụ động/rule marker và Manager replay; chưa có nghiệm thu tương ứng |
| AAA, database, file, mail, Wi-Fi, endpoint Windows | DESIGN ONLY | M1 phân vai dự kiến; endpoint HTTP/VPCS/Linux không chứng minh các dịch vụ này |
| NAT HA, DHCP lease HA, toàn ma trận liên vùng | DESIGN ONLY / PARTIAL | Theo từng dòng mục2.2; không thuộc PASS tối thiểu M3 |

Không kết luận Wazuh Manager “chưa cài”: E9 chứng minh 4.14.9-1 và replay; E10 xác nhận instance VMware truy cập được ở mức mạng. Cũng không suy Manager cũ và VMware hiện tại có cùng cấu hình, bộ dữ liệu hoặc mức hoàn thiện.

# 5. Danh mục ảnh thật tái sử dụng

Thời gian dưới đây là collector/lưu ảnh theo hồ sơ; không dùng đồng hồ guest làm mốc tuyệt đối. Giữ nguyên đường dẫn, không sao chép/xóa/sửa nội dung ảnh. Các liên kết là nguồn minh chứng; mỗi ảnh cần đi kèm giới hạn nêu dưới đây khi đưa vào slide/báo cáo.

| Tệp minh chứng / đường dẫn | Nội dung, mục đích và kết quả | Thời điểm thu (UTC+07:00) | Vị trí dự kiến |
|---|---|---|---|
| [topology-overview-20261105T091848+0700.png](evidence/M1/wazuh-link-20261105/topology-overview-20261105T091848+0700.png) | Topology M1, Wazuh nối VLAN99; xác nhận cấu trúc, không chứng minh log live hoặc topology sau mở rộng WAN | 05/11/2026 09:18:48 | Slide12; Hình5.1 |
| [core-runtime-root-20261103T171628+0700.png](evidence/M2/final-acceptance-20261103/core-runtime-root-20261103T171628+0700.png) | Port/VLAN, không IP và forwarding0/0; chứng minh vai trò Core L2 | 03/11/2026 17:17:04 | Slide12–13; Hình5.2 |
| [core-mirror-after-tests-20261103T171916+0700.png](evidence/M2/final-acceptance-20261103/core-mirror-after-tests-20261103T171916+0700.png) | Mirror và counter48; kết hợp PCAP chứng minh bản sao traffic, không chứng minh Wazuh | 03/11/2026 17:19:23 | Slide16; Hình5.3 |
| [secondary-recovery-carp-readable-20261104T170827+0700.png](evidence/M3/M3.4B-pfsync-state-20261104/secondary-recovery-carp-readable-20261104T170827+0700.png) | Vai trò Secondary sau recovery; đọc cùng recovery-acceptance.json để xác nhận đủ hai phía | 04/11/2026 17:08:35.732426 | Slide14; Hình5.4 |
| [secondary-recovery-pfsync-readable-20261104T170914+0700.png](evidence/M3/M3.4B-pfsync-state-20261104/secondary-recovery-pfsync-readable-20261104T170914+0700.png) | pfsync sau recovery; minh họa sẵn sàng đồng bộ, không thay packet/state proof | 04/11/2026 17:09:24.153578 | Slide14; Hình5.5 |
| [sensor-export-after-marker-20261102T170219+0700.png](evidence/M4/resume-20261102/sensor-export-after-marker-20261102T170219+0700.png) | Console xuất kết quả sensor sau marker; đọc kèm sensor-public-after-marker.json để xác minh alert thật | 02/11/2026 khoảng17:02, theo tên batch +0700 | Slide16; Hình5.6 |
| [real-replay-verified-20261102T205956+0700.png](evidence/M5/continuation-20261102/real-replay-verified-20261102T205956+0700.png) | Tóm tắt replay sự kiện Suricata thật; rule86601, dữ liệu đối chiếu; chỉ minh chứng ingest cục bộ | 02/11/2026 20:59:56, theo tên ảnh +0700 | Slide16; Hình5.7 |

Chú thích đề nghị đặt dưới ảnh: **Hình5.1. Cấu trúc topology M1 trước mở rộng WAN. Hình5.2. Core Open vSwitch hoạt động ở Layer2. Hình5.3. Mirror phát bản sao lưu lượng kiểm thử. Hình5.4. Secondary trở về BACKUP sau recovery. Hình5.5. pfsync sẵn sàng sau recovery. Hình5.6. Kết quả sensor sau marker live. Hình5.7. Wazuh xử lý replay EVE thật.** Cột nội dung trên giải thích mục đích, kết quả và ý nghĩa; không thay chú thích bằng tuyên bố end-to-end PASS.

Không có ảnh Syslog M4.4 đã nghiệm thu hoặc Dashboard để tái sử dụng. Không yêu cầu chụp/kiểm thử mới trong đợt đối chiếu này. Các danh mục gốc E1–E10 giữ timestamp chính xác, log/JSON/PCAP và hash phục vụ truy vết; không di chuyển minh chứng trong `docs/evidence/eve-ng/`.

# 6. Thuật ngữ và cách sử dụng trong báo cáo

Tham chiếu giải thích đầy đủ tên, nghĩa tiếng Việt, nguyên lý, vai trò SOC và ví dụ tại [TOPOLOGY_TERMS.md](TOPOLOGY_TERMS.md), mục2.8 của E2 và mục3.4.2 của E4. Các trạng thái ví dụ cũ trong tài liệu thuật ngữ phải cập nhật cách diễn giải theo mục2 của báo cáo này. Các thuật ngữ hạ tầng QEMU, QCOW2, cloud-init, NoCloud, SSH và LACP không phát sinh cấu hình mới; LACP không áp dụng vì hai trunk đi tới hai firewall riêng, không gắn nhãn PASS cho LACP.

SOC (Security Operations Center) là trung tâm điều hành an ninh; VLAN (Virtual Local Area Network) phân miền quảng bá. IEEE802.1Q mang thẻ VLAN trên trunk; access port phục vụ VLAN đầu cuối. Open vSwitch (OVS) dùng bridge chuyển frame tại Core. SPAN (Switched Port Analyzer)/port mirroring sao chép frame được chọn tới sensor, phục vụ quan sát; ví dụ ens10→capture0 đã kiểm chứng.

OPNsense là tên sản phẩm firewall/gateway. HA (High Availability) là tính sẵn sàng cao; CARP (Common Address Redundancy Protocol) bầu firewall sở hữu VIP (Virtual IP address); pfsync là tên cơ chế đồng bộ state PF, không tự tạo dạng khai triển. XMLRPC (XML Remote Procedure Call) chuyển nhóm cấu hình được chọn. Vai trò SOC là duy trì gateway và chính sách khi chuyển vai; ví dụ năm VIP và một phiên TCP đã kiểm chứng, không suy WAN HA.

NAT (Network Address Translation) dịch địa chỉ, SNAT dịch nguồn; DHCP (Dynamic Host Configuration Protocol) cấp tham số mạng. Ví dụ HTTPS giới hạn và lease Employee/Guest đã đạt; không thay kiểm soát firewall hoặc chứng minh DHCP HA. IDS/IPS (Intrusion Detection/Prevention System) lần lượt phát hiện/ngăn chặn xâm nhập. Suricata là tên sản phẩm, hiện dùng IDS thụ động; Wazuh là tên nền tảng phân tích an ninh, Manager đã xử lý replay. EVE (Extensible Event Format) xuất sự kiện JSON; HOME_NET là biến phạm vi mạng trong luật, không phải thiết bị nhận gói. Vai trò chuỗi này là quan sát→phát hiện→phân tích; đoạn vận chuyển trực tiếp còn thiếu.

Báo cáo chỉ đối chiếu nguồn nội bộ đã nghiệm thu, không dùng tài liệu web mới để nâng trạng thái triển khai. Nếu xuất Word: A4, Times New Roman12–13, lề trái3cm, phải/trên/dưới2cm; giữ đánh số mục/hình và chú thích dưới hình.
