# CHECKPOINT M3 — WAN/NAT DONE/PASS TRONG PHẠM VI ĐÃ DUYỆT — 06/11/2026, UTC+07:00

Đã backup và chuyển đúng hai WAN TAP+metadata sang pnet0/network12 với guard/watchdog180s; DHCP Primary192.168.220.144/24, Secondary192.168.220.145/24, gateway192.168.220.2. Hybrid SNAT+FW hai máy chỉ thêm Employee192.168.40.110/32→1.1.1.1/32 TCP443. Một HTTPS HEAD PASS: curlrc0/TLSverify0/HTTP301, không retry/proxy/redirect; PCAP chứng minh .40.110:52552→WAN.220.144:58206 cùng SYNsequence. Guard cuối PASS, HA/hook/rule cũ/route quản trị giữ nguyên, không restart node; watchdog đã thoát, không cần rollback. Giữ PASS M3.1–M3.6/XMLRPC lịch sử; các hạng mục M3 độc lập đã giao được đóng theo phạm vi nghiệm thu. Chưa nghiệm thu NAT HA giữ phiên/zero-loss hoặc M4/M5; không tự bổ sung các mục đó. [Báo cáo/ma trận/ảnh](M3/M3-WAN-NAT-final-acceptance-20261106.md), [nghiệm thu](evidence/M3/M3-WAN-NAT-live-20261106/M3-WAN-NAT-acceptance.json).

---

# CHECKPOINT M3 — EMPLOYEE LINUX READY/PASS — 06/11/2026, UTC+07:00

Đã tạo/bật Employee-Linux node11 1vCPU/1GiB trên VLAN40/network7, giữ VPCS node5. DHCP192.168.40.110/24, gateway192.168.40.1; curlHTTPS/PythonSSL/CA đã xác minh tại guest, chưa gửi HTTPS Internet. Overlay/seed riêng, topology backup có hash; mọi node/network cũ giữ nguyên, PID firewall/Core không đổi. Không sửa WAN/HA/hook, giữ PASS. M3 PARTIAL; WAN/NAT chờ phê duyệt riêng. [Báo cáo và ảnh](M3/M3-Employee-Linux-readiness-20261106.md), [guard/rollback WAN chưa thực hiện](M3/M3-WAN-guard-rollback-20261106.md), [nghiệm thu](evidence/M3/Employee-Linux-20261106/acceptance.json).

---

# CHECKPOINT M3 — WAN/EMPLOYEE LINUX BLOCKED — 06/11/2026, UTC+07:00

Chỉ đọc: xác minh Primary1/Secondary2 WAN TAP vunl0_1_1,vunl0_2_1→vnet0_4; API metadata không tự chuyển runtime. Đề xuất chuyển đúng TAP+metadata với guard/rollback, chưa thực nghiệm nên chưa chứng nhận an toàn. Có image Ubuntu console-test→ovs backing, chưa xác minh clientHTTPS/role sạch. Đã chuẩn bị script preflight chỉ đọc; chưa tạo/bật Employee-Linux hoặc đổi lab. Cần duyệt node Linux riêng network7 và phương thức chuyển WAN có guard; giữ PASS, M3 PARTIAL/NAT BLOCKED. [Chi tiết](M3/M3-readonly-WAN-Employee-preparation-20261106.md).

---

# CHECKPOINT M3 — NAT BLOCKED Ở PREFLIGHT — 06/11/2026, UTC+07:00

Đã backup topology và config hai firewall, quyền0600/hash khớp. pnet0/gateway quản trị giữ nguyên; topology cuối khớp backup. Chưa chuyển WAN: API đọc được chỉ cập nhật metadata, chưa xác minh đổi link live an toàn. Employee VPCS không chạy, chưa IP nguồn/clientHTTPS được xác minh. Không tự stop/boot/thay node, không dùng nguồn giả. Chưa áp rule/NAT hoặc gửiHTTPS; không cần rollback vì chưa đổi mạng/config. M3 PARTIAL; giữ mọi PASS. [Báo cáo và điều kiện tiếp tục](M3/M3-NAT-deployment-preflight-20261106.md), [kết quả/minh chứng](evidence/M3/M3-NAT-deployment-20261106/deployment-result.json).

---

# CHECKPOINT M3 — PHƯƠNG ÁN CUỐI CHỜ DUYỆT — 06/11/2026, UTC+07:00

Đã xác minh EVE6.2.0-4 không có type NAT trong listNetworkTypes; không nat0/dịch vụ NAT Cloud hoạt động. Host pnet0 DHCP192.168.220.143/24, gateway192.168.220.2, server192.168.220.254; chưa chứng minh Internet/lease WAN guest. Trình dùng Cloud0/pnet0, hai WANvtnet1 DHCP, Hybrid SNAT WAN address và firewall nguồn Employee cần xác minh→1.1.1.1 TCP443. Đích đã được duyệt; thay WAN/upstream và rule vẫn chờ phê duyệt riêng. Chưa đề xuất số IP tĩnh/VIP; không đổi HA/hook, không thử failover. M3 PARTIAL, NAT BLOCKED/PENDING_APPROVAL, giữ PASS. [Phương án cuối và rollback](M3/M3-WAN-final-approval-20261106.md), [cấu hình nháp](M3/M3-NAT-approval-draft-20261106.json).

---

# CHECKPOINT M3 — PHƯƠNG ÁN CHỜ PHÊ DUYỆT — 06/11/2026, UTC+07:00

Chỉ lập kế hoạch, không thay lab. Ưu tiên NAT Cloud nếu bản Community6.2.0-4 thực tế hỗ trợ và đáp ứng upstream/VIP; dự phòng router giả lập+Cloud/pnet được duyệt. Chưa gán IP/gateway/VIP. Cần chốt upstream, hai link WANvtnet1, DHCP/subnet/gateway, nguồn Employee+đíchTCP443, mode/translation NAT và phạm vi NAT có HA. Hook96 giữ nguyên: tái khởi tạo bulk có rủi ro, bỏ hook cũng có nguy cơ mất persistent. Mọi sửa hook duyệt riêng. M3 PARTIAL, NAT BLOCKED, giữ PASS. [Phương án và bảng cần phê duyệt](M3/M3-WAN-upstream-approval-plan-20261106.md).

---

# CHECKPOINT M3 — READ-ONLY; PARTIAL / NAT BLOCKED — 06/11/2026, UTC+07:00

Log xác nhận hook96 gọi lại native pfsync sau bulk đầu đã hoàn tất, khởi phát đợt Primary ~673giây; chưa xác định nguyên nhân truyền chậm. Peer/version/rule pfsync khớp; counter lỗi tích lũy không đủ quy kết. WAN bridge chỉ hai firewall, chưa upstream; outbound mode Automatic đã bật, thiếu IPv4/default route. Đã viết phương án một upstream/WAN-ISP-1, egress một Employee host, NAT WAN VIP nếu yêu cầu HA; cần duyệt upstream, địa chỉ/gateway/VIP và rule/sync NAT trước áp dụng. Giữ mọi PASS, không kiểm thử lại hoặc đổi cấu hình. [Báo cáo và đề xuất](M3/M3-pfsync-cause-NAT-proposal-20261106.md), [đánh giá](evidence/M3/M3-cause-nat-plan-20261106/assessment.json). M3 chưa DONE.

---

# CHECKPOINT M3 — PARTIAL; NAT INTERNET BLOCKED — 06/11/2026, UTC+07:00

Đã xác minh cơ chế snapshot: Primary demotion240 trong pfsync bulk sync, hoàn tất rồi MASTER; Secondary về BACKUP. Hai bản thu cũ tuần tự, không chứng minh đồng thời hai BACKUP. 7/7 mẫu mỗi máy (~60giây riêng) giữ năm VHID đúng vai trò, syncok1/demotion0. Chưa rõ vì sao bulk kéo dài. WAN DHCP chưa nhận IPv4, không IPv4 default route/outbound NAT: BLOCKED; cần upstream/IP/gateway và phương án thay đổi được duyệt. Giữ toàn bộ PASS M3.5/M3.6; không kiểm thử lại, không thay mạng hoặc gián đoạn HA. [Báo cáo](M3/M3-ha-wan-final-review-20261106.md), [minh chứng](evidence/M3/M3-ha-wan-audit-20261106/acceptance.json). Không đánh dấu M3 DONE.

---

# CHECKPOINT M3 — XMLRPC PASS; M3 PARTIAL — 06/11/2026, UTC+07:00

Đã khắc phục transport bằng PowerShell/SSH và Python sẵn có trên EVE. Tám rule và ba pool DHCP khớp toàn bộ thuộc tính; 8/8 UUID rule đã nạp hai phía, Kea chạy. Ảnh cuối: Primary MASTER/Secondary BACKUP năm VLAN, pfsync syncok1. Snapshot trước bất thường được giữ nguyên, nguyên nhân chưa xác minh; không tự phục hồi HA. NAT Internet BLOCKED: WAN không IPv4/default route. Giữ PASS M3.5, không chạy lại hoặc thay cấu hình. [Báo cáo](M3/M3-runtime-verification-20261106.md), [nghiệm thu](evidence/M3/M3-runtime-review-20261106/acceptance.json).

---

# CHECKPOINT M3 — PARTIAL — 06/11/2026, UTC+07:00

Đã đối chiếu hồ sơ XMLRPC thực tế: tám mô tả rule và ba pool DHCP khớp; chưa so sánh đầy đủ thuộc tính và runtime cuối. NAT Internet BLOCKED vì WAN cô lập. DHCP/firewall giữ PASS M3.5 lịch sử. Runtime mới BLOCKED do không có Python sử dụng được; không thay hệ thống, không có ảnh mới. [Báo cáo](M3/M3.6-review-20261106.md), [kết quả](evidence/M3/M3.6-completion-20261106/review-result.json).

---

# CHECKPOINT M3.5 — CÁC BƯỚC 1–5 DONE/PASS — 05/11/2026, UTC+07:00

Đã hoàn thành năm bước được giao: backup/kiểm kê; Kea DHCP cho VLAN40 Employee và VLAN50 Guest; Employee/Guest dùng DHCP, Management tĩnh; tám rule firewall giới hạn; kiểm thử CARP VIP, DHCP, DNS và luồng allow/deny. Employee nhận `192.168.40.110`, Guest nhận `192.168.50.110`, cả hai dùng gateway/DNS VIP `.1`; Management dùng `192.168.99.100/24`, gateway `.99.1`. Bộ live test đạt 7/7: ba gateway PASS, DNS hai VLAN PASS, Employee → DC TCP/8000 PASS, Guest → DC TCP/8000 bị chặn đúng dự kiến.

Pool LAN IPv4 cũ được di chuyển nguyên trạng từ Dnsmasq sang Kea để giải quyết xung đột UDP/67; Dnsmasq tiếp tục DNS trên 53053. Core giữ Layer 2. NAT Internet chưa nghiệm thu vì WAN cô lập; DHCP HA/XMLRPC, failover với rule mới và automation block IP chưa thuộc bước 1–5. [Báo cáo](M3/M3.5-network-services-steps-1-5-20261105.md), [danh mục minh chứng](evidence/M3/M3.5-network-services-20261105/evidence-index.csv), [nghiệm thu](evidence/M3/M3.5-network-services-20261105/M3.5-acceptance.json).

---

# CHECKPOINT M1 — NHÃN TOPOLOGY ĐÃ ĐÍNH CHÍNH — 05/11/2026, UTC+07:00

Đã kiểm tra trạng thái Data-Center, Employee, Guest, DMZ, Management, Suricata và Wazuh. Data-Center/DMZ đã cài Ubuntu và có HTTP đã kiểm chứng; Suricata 7.0.3 và Wazuh Manager 4.14.9 đã cài. Đã loại bỏ bốn chú thích “chưa cài”/“NIC chưa nối” sai trên EVE-NG. Employee, Guest, Management là VPCS không cần cài OS nhưng chưa có bằng chứng cấu hình, nên giữ `VPCS · chưa cấu hình`. Chỉ textobject ID4/7/10/11 thay đổi; không node/link/guest config hoặc power operation. [Báo cáo và ảnh](M1/M1-topology-label-correction-20261105.md), [danh mục](evidence/M1/label-correction-20261105/evidence-index.csv).

---

# CHECKPOINT M1 — DONE/PASS — 05/11/2026, UTC+07:00

**M1 hoàn thành trong phạm vi thiết kế và topology lab nội bộ.** Ảnh EVE-NG thật lúc 09:18:48 hiển thị đủ 10 node, 11 segment và Wazuh e0 nối `VLAN99-Management`. Kết quả GUI khớp kiểm tra XML độc lập 12/12. Internet/upstream là phần mở rộng dự kiến. Chưa suy M1 thành đã kiểm chứng IP Wazuh, log live, NAT/DHCP hoặc automation. [Báo cáo nghiệm thu cuối](M1/M1-final-acceptance-20261105.md), bản Word cùng tên và [danh mục minh chứng](evidence/M1/wazuh-link-20261105/evidence-index.csv).

---

# CHECKPOINT M1 — KẾT NỐI WAZUH ĐÃ BỔ SUNG — 05/11/2026, UTC+07:00

Theo quyền người dùng, đã kiểm kê, sao lưu topology rồi nối Wazuh-SOC e0 vào VLAN99-Management/network10. Thao tác thành công lúc 09:15:50; đọc lại độc lập lúc 09:16:43 xác nhận đủ 12/12 kiểm tra cấu trúc, chỉ thêm đúng interface, giữ 10 node/11 segment. Không bật/tắt node hoặc cấu hình IP; mọi node tiếp tục tắt.

[Báo cáo bổ sung M1](M1/M1-wazuh-link-verified-20261105.md), bản Word cùng tên; [danh mục minh chứng](evidence/M1/wazuh-link-20261105/evidence-index.csv). Backup trên EVE: /root/soc-m1-wazuh-link-20261105T091550Z. Chi tiết hash và phạm vi tại connection-result.json và independent-verification.json.

**M1: hồ sơ thiết kế và cấu trúc kết nối cơ sở đã hoàn thiện; còn ảnh topology GUI để đóng nghiệm thu.** Không có cửa sổ trình duyệt EVE đang mở; chưa thu ảnh thật mới. Hướng dẫn chụp nằm trong mục 1.5 báo cáo bổ sung. Chưa nghiệm thu IP Wazuh, đường log live hoặc chức năng mạng từ lần nối này. Internet là phần mở rộng, không phải điều kiện lab cơ sở. Các đoạn dưới đây về Wazuh chưa nối là lịch sử trước thay đổi.

---

# CHECKPOINT M1 — HỒ SƠ THIẾT KẾ HỢP NHẤT — 2026-11-05T09:11:36.571323+07:00

Người dùng chọn lab nội bộ; Internet là phần mở rộng. [Thiết kế M1](M1/M1-design-consolidated-20261105.md), bản Word cùng tên và sơ đồ network/topology/M1-internal-lab-20261105.mmd bổ sung số node, mapping, bảng IP, chính sách và thuật ngữ.

**Hồ sơ thiết kế cơ sở đã hoàn thiện; topology EVE-NG thực tế chưa nghiệm thu hoàn chỉnh.** Wazuh e0 vào VLAN99 là thiết kế chưa áp dụng; cần triển khai và ảnh thật theo quyền riêng. Core không IP/Layer2; không thay hệ thống trong đợt này. [Danh mục rà soát](evidence/M1/design-review-20261105/evidence-index.csv). M3.4 giữ DONE/PASS lịch sử; các checkpoint dưới đây giữ nguyên.

---

# CHECKPOINT MỚI NHẤT — M3.4 DONE/PASS — 2026-11-04T17:12:50.875586+07:00



## 0.1. Nghiệm thu M3.4B



**M3.4 — pfsync state synchronization khi CARP failover: DONE/PASS.** A. State synchronization PASS. B. Connection continuity PASS cho một session mới; recovery hoàn tất. Checkpoint này thay READY_FOR_RETEST của M3.4A; kết quả/evidence các lần trước giữ nguyên lịch sử, không sửa thành PASS.



- SESSION: `192.168.40.100:44341 → 192.168.30.10:8000/TCP`, client host EVE qua access VLAN40 sẵn có, Data-Center thật; một SYN, một HTTP request, không reconnect.

- Native Primary/Secondary BEFORE cùng hai ID `075deb6a00000000`, `085deb6a00000000`, creator ID `d57c33f6`, ESTABLISHED:ESTABLISHED; Secondary BACKUP có counter0:0. Có pfsync protocol240 hai chiều.

- FAILOVER: chỉ soft shutdown Primary; Core/Secondary/DC giữ PID. Watcher chỉ đọc đã lưu native snapshot ngay khi thấy đủ năm MASTER, giữ nguyên hai ID/creator và ESTABLISHED, VIP đúng. Ảnh native sau đó ghi counter tăng trên cùng state; không đổi VIP/VHID/advskew hoặc rule.

- CONTINUITY: cùng session nhận11 marker ACK sau Primary OFF rồi hoàn tất `HTTP/1.0 200 OK`,350 byte; PCAP tái lắp response khớp SHA-256. Retry counter client0, không thấy duplicate payload tại capture client; **không kết luận zero packet loss**. Request đã hoàn tất trước khi boot Primary.

- RECOVERY: Primary tự MASTER / Secondary BACKUP cả VLAN30/40/50/60/99, năm VIP .1 đúng; pfsync READY hai phía, syncok1/demotion0, SYNC ping2/2; Core OVS/VLAN hoạt động, Core giữ Layer2. Không gọi lại native pfsync hoặc đặt demotion thủ công.

- Backup mỗi firewall `/root/soc-m34b-20261104/config.before.xml`; DC `/root/soc-m34b-20261104/routes.before.json`. Chỉ thêm host route runtime `.40.100/32 via .30.1` để chiều về qua CARP; IP/default route/netplan không đổi. Route và helper/evidence được giữ lại theo yêu cầu không cleanup. Bốn node vẫn chạy, Primary đã boot mới; không node khác được bật.

- [Báo cáo/danh mục minh chứng](evidence/M3/M3.4B-pfsync-state-20261104/evidence-index.md), [nghiệm thu](evidence/M3/M3.4B-pfsync-state-20261104/M3.4-acceptance.json). M3.4 cũ137 tệp và M3.4A119 tệp giữ nguyên checksum.

- **NEXT TODO: chưa được giao. Dừng sau M3.4; không M3.5, NAT/DHCP, M4/M5 hoặc cleanup.**



---



# CHECKPOINT MỚI NHẤT — M3.4 READY_FOR_RETEST — 2026-11-04T16:39:50.103201+07:00



## 0.1. M3.4A — Baseline đã khôi phục



**M3.4 = READY_FOR_RETEST.** Chỉ nghiệm thu baseline M3.4A; chưa chạy M3.4B, chưa kết luận toàn bộ state/failover M3.4 DONE/PASS. Kết quả lần thử bị gián đoạn trước đây được giữ nguyên, không chuyển thành pfsync FAIL.



- Core1024 MiB: OVS active, đúng access/trunk năm VLAN, flow NORMAL; không IP ngoài loopback, forwarding IPv4/IPv6=0, giữ Layer2. ARP qua năm access port nhận đủ Primary .2, Secondary .3 và VIP .1.

- Primary2048 MiB: IP .2/24 và MASTER trên VLAN30/40/50/60/99. Secondary2048 MiB: IP .3/24 và BACKUP cả năm VLAN. VIP .1/24, VHID30/40/50/60/99, advbase1/skew0/100 đúng checkpoint.

- SYNC10.255.255.1/30 ↔ .2/30 ping2/2 hai chiều; pfsync UP/RUNNING, đúng vtnet2/peer, syncok1 và demotion0 hai phía. Hook chạy cùng boot; không phải gọi lại native pfsync hoặc đặt demotion thủ công.

- Endpoint duy nhất: Data-Center1024 MiB, `.30.10/24`, HTTP8000 active/LISTEN. Chỉ đọc dịch vụ, không HTTP request. Default route gốc vẫn `.30.2`; host route runtime riêng `.40.100/32 via .30.1` của lần test cũ không được dựng lại trong M3.4A; chuẩn bị đường client/return qua CARP thuộc bước setup của retest khi được giao.

- Config firewall khớp hash checkpoint trước; backup root-only mỗi firewall: `/root/soc-m34a-baseline-20261104/config.before.xml`. Không đổi topology/resource/IP/VIP/VHID/advskew, không Core/NAT/DHCP hoặc cleanup. Giữ đúng bốn node chạy.

- [Evidence mới](evidence/M3/M3.4A-baseline-20261104/evidence-index.md), [kết quả baseline](evidence/M3/M3.4A-baseline-20261104/M3.4A-readiness.json). Đã kiểm tra137 tệp minh chứng M3.4 cũ giữ nguyên SHA-256; không xóa/di chuyển.

- **Dừng tại READY_FOR_RETEST; chưa chạy M3.4B, chưa làm TODO khác.**



---



# CHECKPOINT MỚI NHẤT — M3.4 FAIL/BLOCKED — 2026-11-04T16:20:04.824645+07:00



## 0.1. Kết quả và nguyên nhân



**M3.4 chưa hoàn thành.** Gián đoạn/restart môi trường EVE: khi tiếp tục, host uptime khoảng 3 phút, không có QEMU hoặc client test chạy. Chưa thu đủ native state sau failover, chưa hoàn tất HTTP và chưa kiểm chứng recovery. Tác nhân gây restart chưa xác minh.



- STATE BEFORE/SYNC: đã kiểm chứng hai entry ESTABLISHED của flow TCP `192.168.40.100:44340 → 192.168.30.10:8000`; state ID `bf10eb6a00000000`, `c010eb6a00000000` và creator ID `c70da713` khớp trên Primary/Secondary. Secondary BACKUP có counter0:0 trước tiếp quản; có pfsync protocol240 hai chiều.

- FAILOVER: đã soft shutdown riêng Primary, host xác nhận Primary tắt và Core/Secondary/DC còn chạy; Secondary .3 quảng bá đủ VHID30/40/50/60/99, năm VIP .1 trả lời ARP. Bản native state sau failover đã tạo header checksum nhưng chưa nhận đủ payload; không coi là evidence đã giải mã.

- CONNECTION: 11 marker của cùng TCP session được ACK sau khi Primary tắt; một SYN, không reconnect, một retransmission được ghi nhận. Chưa hoàn tất HTTP; không kết luận zero packet loss hoặc kết nối hoạt động ở thời điểm hiện tại.

- RECOVERY: **NOT_RUN**. Kiểm tra tiếp quản thấy EVE uptime khoảng3 phút, không có QEMU và không còn process client; file live.json là snapshot cũ. Không tự bật lại node hoặc tạo kết nối khác để che mất session gốc.

- [Báo cáo/danh mục minh chứng](evidence/M3/M3.4-pfsync-state-20261104/evidence-index.md), [kết quả](evidence/M3/M3.4-pfsync-state-20261104/M3.4-result.json). Raw log/PCAP đã được bảo toàn byte gốc, các đuôi NUL/truncated được ghi rõ; chưa có client-result.json/wire-result.json.

- Backup: trên mỗi firewall `/root/soc-m34-20261104/config.before.xml`; trên DC `/root/soc-m34-20261104/routes.before.json` (0600). Chỉ thêm host route runtime `.40.100/32 via .30.1` để chiều về dùng CARP; IP/default route/netplan không đổi khi kiểm tra. Sau restart chưa đọc lại route trong guest. Không sửa rule, NAT/DHCP, CARP parameters, Core hoặc topology.

- Điểm tiếp tục: khôi phục đúng baseline rồi thử lại **duy nhất M3.4 với session mới**; không thể tiếp tục session TCP cũ. Nếu lấy lại payload state cũ để lưu trữ phải khớp hash trong staged-result-checkpoint.json; đó không phải runtime mới. M3.1–M3.3 giữ PASS lịch sử. **Không làm TODO khác; dừng tại đây.**



---



# CHECKPOINT MỚI NHẤT — M3.3 DONE/PASS — 2026-11-04T11:07:14.319327+07:00



## 0.1. Kết quả M3.3B



**M3.3 — CARP failover/recovery: DONE/PASS.** Failover PASS: Primary đã tắt, Secondary tự MASTER cả VLAN30/40/50/60/99, đủ VIP .1 và ARP qua Core; recovery PASS: Primary tự MASTER, Secondary BACKUP năm VLAN; pfsync UP/RUNNING, syncok1, demotion0 hai phía; Core/VLAN hoạt động. Không áp lại native pfsync hoặc sửa CARP để đạt kết quả.



- Minh chứng BEFORE / FAILOVER / RECOVERY: [danh mục](evidence/M3/M3.3-failover-20261104/run-105204/evidence-index.md), [kết quả](evidence/M3/M3.3-failover-20261104/run-105204/M3.3-acceptance.json). Checkpoint này thay trạng thái READY_FOR_FAILOVER trước đó; các phần bên dưới giữ làm lịch sử.

- Backup config root-only trên mỗi firewall: `/root/soc-m33b-20261104/config.before.xml`; bản sao tài liệu và metadata lab được giữ trong đợt này. Không đổi VIP/VHID/advbase/advskew, topology, resource, Core, VLAN/IP hoặc NAT/DHCP.

- Không suy phép thử CARP thành nghiệm thu giữ phiên/kết nối liên tục, WAN/NAT/DHCP HA hoặc toàn bộ SOC. Không làm M3.4/M4/M5, không cleanup.

- **Dừng tại đây. NEXT TODO: chưa được giao; không tự tạo hoặc triển khai mục mới.**



---



# CHECKPOINT MỚI NHẤT — M3.3 READY_FOR_FAILOVER — 2026-11-04T10:48:54.279347+07:00



## 0.1. Phạm vi và trạng thái



Đã khôi phục đúng điều kiện đầu theo quyền người dùng: chỉ boot Core L2 1024 MiB, OPNsense Primary 2048 MiB và Secondary 2048 MiB. **M3.3: READY_FOR_FAILOVER; chưa chạy failover/recovery, chưa DONE/PASS M3.3.** Checkpoint này thay trạng thái BLOCKED trước đó; các phần phía dưới giữ làm lịch sử.



- Core: OVS active; access VLAN30/40/50/60/99 và trunk đúng; flow NORMAL; không IP ngoài loopback; forwarding IPv4/IPv6=0. ARP qua cả năm access port nhận đủ .2/.3/.1.

- Primary: IP 192.168.VLAN.2/24, CARP MASTER cả năm VLAN; Secondary: IP 192.168.VLAN.3/24, BACKUP cả năm VLAN. VIP 192.168.30.1, .40.1, .50.1, .60.1, .99.1/24 đúng VHID30/40/50/60/99; advbase1, skew0/100 giữ nguyên.

- SYNC 10.255.255.1/30 ↔ 10.255.255.2/30 ping được; pfsync UP/RUNNING, đúng peer/vtnet2, syncok1, demotion0 hai phía; hook chạy trong boot hiện tại; có gói protocol240 hai chiều.

- Config hai firewall khớp SHA-256 đã nghiệm thu M3.2; đã cần gọi lại native pfsync trên Primary để khôi phục runtime M3.1 (syncok0/demotion240 → syncok1/demotion0); không sửa cấu hình lưu, VIP/VHID/skew hoặc hook. Backup root-only trên mỗi firewall: `/root/soc-m33-restore-20261104/config.before.xml`; bản sao tài liệu và checkpoint metadata lab đã lưu.

- [Danh mục minh chứng](evidence/M3/M3.3-restore-20261104/evidence-index.md), [kết quả kiểm chứng](evidence/M3/M3.3-restore-20261104/M3.3-readiness.json). Giữ ba node chạy; không NAT/DHCP, không đổi topology/Core/VLAN/IP, không cleanup, không M4/M5. **Dừng trước failover.**



---



# CHECKPOINT MỚI NHẤT — M3.3 BLOCKED — 2026-11-04T10:27:35.821104+07:00



Người dùng đã bổ sung **M3.3 — CARP failover và recovery thực tế trên năm VLAN**. Các dòng cũ nói không có TODO sau M3.2 là lịch sử.



- BEFORE: **BLOCKED** — SSH EVE-NG thành công nhưng không có tiến trình QEMU đang chạy. Không xác minh được Primary MASTER, Secondary BACKUP, VIP, pfsync READY hoặc demotion.

- FAILOVER / RECOVERY: **NOT_RUN**; PFSYNC: **NOT_VERIFIED**. Dừng theo yêu cầu khi trạng thái đầu không đúng; không tự bật node. M3.1/M3.2 giữ PASS lịch sử.

- Backup: bản sao hai tài liệu trước cập nhật và metadata lab root-only trên EVE. Chưa tạo backup guest vì firewall không chạy. Không sửa cấu hình, CARP parameters, Core, topology, VLAN/IP hoặc NAT/DHCP; không M4/M5, không cleanup.

- [Minh chứng và checkpoint](evidence/M3/M3.3-failover-20261104/evidence-index.md). Cần khôi phục điều kiện đầu theo quyền riêng rồi thử lại duy nhất M3.3. Dừng tại đây.



---



# 1. SOC TO DO — bản theo dõi dự án D:\SOC



## 1.1. Bàn giao M2 ngày 03/11/2026, UTC+07:00



Đây là bản theo dõi riêng trong workspace, không phải bản sửa tài liệu nhóm gốc. Mục công việc hiện hành được gọi đúng kiến trúc: **Cấu hình Core L2 Switch (Open vSwitch)**, thay cách gọi Core L3. Không thay các đoạn lịch sử giải thích phương án L3 cũ thành kết quả mới.



| Hạng mục | Trạng thái | Minh chứng |

|---|---|---|

| Cấu hình Core L2 Switch (Open vSwitch) | PASS | 95/95 ca frame; runtime mới forwarding0/0, không IP ngoài loopback |

| VLAN30/40/50/60/99, access/trunk | PASS | Suite năm VLAN; PCAP access/trunk mới |

| Inter-VLAN Routing qua Primary | PASS | HTTP200 .40.100 → .30.10:8000; tag40→30, TTL64→63 |

| ACL/firewall theo ngoại lệ đã xác nhận | PASS | Một ca dương/hai ca âm, PCAP và counter |

| LACP | N/A | Hai trunk tới hai firewall riêng, không thiết kế LAG chung |

| SPAN/Port Mirroring | PASS | Marker GET trong PCAP mirror; counter48 |

| Báo cáo tổng kết M2 và evidence index | Hoàn tất | [Báo cáo M2](M2/M2-final-summary-20261103.md), `evidence/M2/final-acceptance-20261103/evidence-index.csv` |



**M2 hoàn thành trong phạm vi nghiệm thu đã duyệt.** Không suy ACL PASS thành đã thử mọi cặp VLAN/IPv6 hoặc quản trị least-privilege toàn hệ thống. Ghi chú LAN parent rộng/nguồn quản trị VLAN99 ở Nhóm2C vẫn giữ nguyên.



## 1.2. Trạng thái dừng tại bàn giao M2 (lịch sử)



Core + Primary giữ chạy. DC tắt mềm, topology phục hồi nguyên byte, NIC/namespace client tạm đã gỡ sau đợt. VPCS Employee không bật nên không trùng IP.



M3/M4/M5, CARP/HA, NAT/DHCP và pipeline live giữ trạng thái hồ sơ trước. Không tự chuyển giai đoạn hoặc nhận hoàn thành toàn dự án SOC. Dừng chờ người dùng.



## 1.3. TODO M3 — tiếp tục theo chỉ thị người dùng ngày 03/11/2026, UTC+07:00



Các mục dưới đây ghi lại đúng thứ tự công việc M3 người dùng vừa giao; bản trước của tệp chưa có danh sách M3. Không tự bổ sung hạng mục khác hoặc chuyển M4/M5. Trạng thái ở mục 1.2 là lịch sử, không thay quyền thực hiện M3 mới.



| TODO | STATUS | EVIDENCE |

|---|---|---|

| M3.1 — Sửa pfsync persistent; tự hoạt động sau reboot từng firewall; xác minh runtime hai phía | DONE/PASS — 2026-11-03T23:22:49+07:00 | `evidence/M3/todo-completion-20261103/M3.1-acceptance.json`; `primary-pfsync-postboot.json`, `secondary-pfsync-postboot.json`: boot mới, log hook cùng boot, UP/peer đúng/syncok1/demotion0, config không đổi |

| M3.2 — Triển khai CARP năm VLAN theo bộ VIP/VHID đã duyệt, advbase1, skew Primary0/Secondary100; xác minh Primary MASTER / Secondary BACKUP | DONE/PASS — 2026-11-03T23:35:30+07:00 | `evidence/M3/todo-completion-20261103/M3.2-acceptance.json`; `primary-carp-verified.json`, `secondary-carp-verified.json`; ảnh carp-proof hai phía; `carp-advertisements-after.json`, `carp-vip-arp-after.json` |

| M3.3 — CARP failover/recovery | DONE/PASS — 2026-11-04T11:07:14.319327+07:00 | `evidence/M3/M3.3-failover-20261104/run-105204/M3.3-acceptance.json`; BEFORE/FAILOVER/RECOVERY |

| M3.4 — Kiểm thử pfsync state synchronization khi CARP failover | DONE/PASS — 2026-11-04T17:12:50.875586+07:00; state sync, continuity của một session mới và recovery PASS | `evidence/M3/M3.4B-pfsync-state-20261104/M3.4-acceptance.json`; native state trước/sau, PCAP và recovery |



**Hai TODO M3 được liệt kê ở trên đã hoàn thành.** M3.1 được nghiệm thu từ reader chỉ đọc sau reboot, không chạy lại native apply sau boot; M3.2 có đủ năm VIP lưu trong config và runtime MASTER/BACKUP, quảng bá protocol112 cùng ARP thực tế. [Báo cáo nghiệm thu](M3/M3-todo-completion-20261103.md), [danh mục minh chứng](evidence/M3/todo-completion-20261103/evidence-index.md).



**TODO tiếp theo: không có mục M3 chưa hoàn thành nào được liệt kê trong tệp hiện hành.** Dừng trong phạm vi này; không tự tạo thêm failover, NAT/DHCP hoặc chuyển M4/M5. Chưa nghiệm thu giữ phiên/failover hoặc CARP sau reboot riêng; không suy MASTER/BACKUP PASS thành đã thử các chức năng đó. Core Layer2 và phân bổ RAM1024/2048/2048MiB giữ nguyên.



## 1.4. Checkpoint tiếp quản — 2026-11-03T23:44:19+07:00



- **Đã DONE tới M3.2**; M3.1 và M3.2 giữ DONE/PASS. Đã đọc lại toàn bộ TODO: **không có TODO M3 chưa DONE tiếp theo**. Không bắt đầu thay đổi lớn hoặc tạo thêm công việc.

- **Trạng thái vừa đọc:** Core ON1024MiB/1vCPU; Primary ON2048MiB/2vCPU; Secondary ON2048MiB/2vCPU. Host xác nhận ba tiến trình QEMU. Core giữ Layer2 theo checkpoint M2/M3 trước; lượt này không đọc lại toàn bộ OVS trong guest và không thay cấu hình Core.

- **CARP hiện tại, ảnh thật lúc23:44:11 UTC+07:00:** Primary MASTER, Secondary BACKUP trên đủ VHID30/40/50/60/99; advbase1, skew0/100. VIP đã lưu:192.168.30.1/24,192.168.40.1/24,192.168.50.1/24,192.168.60.1/24,192.168.99.1/24.

- **Pfsync hiện tại:** hai phía UP/RUNNING, syncdev vtnet2, peer Primary→10.255.255.2/Secondary→10.255.255.1, version1400, syncok1, demotion0. Hook persistent `/usr/local/etc/rc.syshook.d/start/96-soc-pfsync` đã được nghiệm thu qua reboot ở M3.1.

- **Thay đổi hệ thống cuối:** lưu năm VIP CARP trên Secondary và native VIP/filter reload trong M3.2; sau đó chỉ kiểm thử/đọc trạng thái. Lượt checkpoint23:44 chỉ đọc và lưu ảnh/log, cập nhật tài liệu; không đổi resource, topology, policy, NAT/DHCP hoặc vòng đời node.

- **Việc còn phải làm trong TODO M3 hiện hành: không có.** Failover/giữ phiên và CARP sau reboot riêng chưa nghiệm thu, nhưng không tự thêm thành TODO. Không chuyển M4/M5, không cleanup/commit/push. Khi tiếp quản, đọc checkpoint đầu PROGRESS.md; không chạy lại payload apply đã hoàn tất.

- **Evidence mới:** [danh mục checkpoint](evidence/M3/checkpoint-20261103T2343/evidence-index.md), `host-readonly.json`, hai ảnh `primary-checkpoint-20261103T234400+0700.png` / `secondary-checkpoint-20261103T234400+0700.png` và JSON cùng tên. Evidence nghiệm thu chính: `docs/evidence/M3/todo-completion-20261103/`; [báo cáo](M3/M3-todo-completion-20261103.md).



## Checkpoint rà soát phạm vi M3 — 2026-11-04T10:25:14+07:00



- STATUS: **BLOCKED** — không có TODO M3 chưa DONE trong SOC_TO_DO.md; danh sách chỉ có M3.1 và M3.2, đều DONE/PASS.

- Đã đọc TODO và PROGRESS; giữ nguyên kết quả nghiệm thu lịch sử. Không thực hiện kiểm thử runtime hoặc thay đổi hệ thống vì chưa có TODO tiếp theo để lựa chọn trong phạm vi yêu cầu.

- Điểm tiếp tục: người dùng xác định TODO M3 mới; không tự thêm failover/NAT/DHCP, không chuyển M4/M5. Dừng tại đây.

- Minh chứng rà soát và bản sao tài liệu trước cập nhật: [danh mục](evidence/M3/todo-scope-check-20261104T102514/evidence-index.md). Không có minh chứng runtime mới.










