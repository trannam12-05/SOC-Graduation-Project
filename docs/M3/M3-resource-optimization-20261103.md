# CHƯƠNG 3. TỐI ƯU TÀI NGUYÊN LAB SOC NGÀY 03/11/2026

## 3.1. Kết luận và phạm vi

**RESOURCE OPTIMIZATION FAIL** theo điều kiện nghiệm thu bắt buộc: pfsync phải READY sau boot nhưng hiện chưa đạt trên cả hai firewall. **NOT READY TO APPLY CARP**. Phân bổ RAM mới và boot/L2 đạt trong cửa sổ quan sát; không đồng nhất lỗi pfsync với thiếu RAM. Chưa chứng minh nguyên nhân pfsync do resource mới. Không giảm RAM thêm để tạo kết quả PASS.

Đã đổi duy nhất RAM ba node từ 8192 xuống **5120 MiB**, giảm **3072 MiB (37,5%)**. vCPU giữ Core1/Primary2/Secondary2, tổng5 trên EVE4 logical CPU; không coi overcommit CPU tự động là lỗi. Không đổi disk/image, seed, interface mapping, mạng, VLAN/IP, OVS, firewall policy, NAT/DHCP hoặc cấu hình OPNsense. Không tạo VIP, không apply CARP, không failover, không triển khai M4/M5, không xóa minh chứng và không commit/push.

Lượt thu bắt đầu 2026-11-03T22:37:30.273541+07:00, mốc host bàn giao 2026-11-03T22:49:54.087900+07:00 (UTC+07:00). Giờ EVE lệch với collector; tên checkpoint remote chứa giờ host chỉ dùng định danh, không thay thời điểm thu. Trạng thái cuối giữ ba node M3 ON để điều tra; các QEMU còn lại OFF. VPCS chưa được kiểm kê tiến trình riêng, không kết luận OFF từ việc không có QEMU.

## 3.2. Checkpoint và thay đổi

Topology trước thay đổi: `/root/soc-resource-checkpoint-20261103T173005/SOC-M2-Core-L2.unl` trên EVE, SHA-256 `a588f348ef49d5bc92eb185f162368cba8618ee9509870135e27fd9b8b3d4879`. Bản metadata này chứa cấu hình RAM/CPU và mapping gốc. JSON `before.json` là inventory công khai; bản topology đầy đủ được giữ riêng trên host EVE. `resource-change.json` chứng minh mọi node mục tiêu đã OFF và chỉ thuộc tính RAM thay đổi; `after-change.json` xác nhận không còn QEMU trước boot lại.

Hai firewall được soft shutdown bằng `shutdown -p now`; không hard power-off. Trước đó đã sao lưu `/conf/config.xml` vào `/root/soc-resource-checkpoint-20261103/config.xml` với umask077, không xuất nội dung nhạy cảm. Ảnh checkpoint và HA sau boot xác nhận SHA-256 trước/sau khớp:

| Node | SHA-256 config.xml trước và sau |
|---|---|
| Primary | 2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2 |
| Secondary | fd0482546117a18254e05114dc1b101012b95c1388e4ba9ea4eaafce115c69bd |

Core không bị sửa cấu hình guest. Checkpoint M2 đã có trước được giữ nguyên; lượt này không tạo snapshot disk đang chạy hoặc đổi ảnh. Sau reboot, người dùng đăng nhập trực tiếp ba console và chuẩn bị sudo trên Core; công cụ không lấy mật khẩu từ chat, không đổi cơ chế xác thực. Helper Secondary kiểm tra credential có sẵn đã dừng do không có tệp DPAPI; không sinh credential thay thế.

## 3.3. Inventory BEFORE / AFTER và lựa chọn tài nguyên

| Node | Vai trò | RAM trước (MiB) | vCPU trước | Trạng thái trước | RAM sau/đề xuất (MiB) | vCPU sau | Trạng thái sau | Lý do |
|---|---|---:|---:|---|---:|---:|---|---|
| SOC-Core-L2 | Core chuyển mạch Layer 2/OVS | 2048 | 1 | OFF | 1024 | 1 | ON | 1024 đã boot, OVS active; MemAvailable guest 639 MiB trong ảnh. |
| OPNsense-Primary | Firewall chính | 3072 | 2 | ON | 2048 | 2 | ON | 2048 đã boot và đủ năm VLAN; giữ 2 vCPU, pfsync chưa đạt sau reboot. |
| OPNsense-Secondary | Firewall dự phòng | 3072 | 2 | ON | 2048 | 2 | ON | 2048 đã boot và đủ năm VLAN; giữ 2 vCPU, pfsync chưa đạt sau reboot. |
| Data-Center | Máy chủ Data Center | 1024 | 1 | OFF | 1024 | 1 | OFF | Giữ nguyên; chưa có số đo guest mới để giảm tiếp. |
| Employee | Endpoint VPCS VLAN40 | N/A | N/A | QEMU OFF; VPCS chưa đo | N/A | N/A | VPCS chưa đo | VPCS không khai báo RAM/vCPU QEMU; cần đo RSS khi chạy, không coi tiêu thụ bằng 0. |
| Guest | Endpoint VPCS VLAN50 | N/A | N/A | QEMU OFF; VPCS chưa đo | N/A | N/A | VPCS chưa đo | VPCS không khai báo RAM/vCPU QEMU; cần đo RSS khi chạy, không coi tiêu thụ bằng 0. |
| DMZ | Máy chủ DMZ | 1024 | 1 | OFF | 1024 | 1 | OFF | Giữ nguyên; chưa có số đo guest mới để giảm tiếp. |
| Management | Endpoint VPCS VLAN99 | N/A | N/A | QEMU OFF; VPCS chưa đo | N/A | N/A | VPCS chưa đo | VPCS không khai báo RAM/vCPU QEMU; cần đo RSS khi chạy, không coi tiêu thụ bằng 0. |
| Suricata-NIDS | Cảm biến IDS | 1024 | 1 | OFF | 1024 | 1 | OFF | Giữ nguyên; chưa có số đo guest mới để giảm tiếp. |
| Wazuh-SOC | SOC/Wazuh, cần audit guest riêng | 4096 | 2 | OFF | 4096 | 2 | OFF | Giữ nguyên; chưa có số đo guest mới để giảm tiếp. |

RAM sau của ba node M3 là giá trị đã áp dụng; RAM các node khác giữ nguyên, chưa phải mức tối thiểu đã đo. Không có cơ sở giảm Wazuh hoặc Suricata chỉ từ tên vai trò. Không thay vCPU ở lượt đầu nhằm kiểm chứng tác động của RAM riêng biệt; tải boot cao không phải căn cứ giảm tiếp CPU ngay lúc guest khởi động.

## 3.4. Ngân sách và số đo host

| Chỉ tiêu | Giá trị | Kết quả / giới hạn |
|---|---:|---|
| Host MemTotal | 7897.78 MiB | Đọc /proc/meminfo |
| Guest allocated M3 trước | 8192 MiB | Vượt MemTotal, chưa tính host |
| Guest allocated M3 sau | 5120 MiB | PASS ngân sách |
| Host RAM trừ RAM guest khai báo | 2777.78 MiB | Reserve tính toán; không đồng nghĩa MemAvailable |
| Reserve tối thiểu thiết kế | 1536 MiB | Không hạ guard cũ1GiB; guard boot còn kiểm MemAvailable |
| MemAvailable tại bàn giao | 3390.91 MiB | PASS >1536 MiB trong mẫu |
| SwapTotal / swap dùng | 4096.00 / 0.00 MiB | Không dùng swap host |
| Kernel OOM host | Không có entry phù hợp | journalctl rc1 có stdout No entries, không phải lỗi kernel |
| CPU | 4 logical CPU; 5 vCPU guest | Tải boot cao, cuối cửa sổ vmstat idle92–93% |

`observation-1.json` và `observation-final.json` có cửa sổ vmstat20 mẫu, si/so0. Cuối cửa sổ thứ hai tải giảm rõ, không dùng load average lịch sử cao để kết luận CPU đang bão hòa. `handover-host.json` là số đo sau cùng; `runtime-final.json` là mốc trước đó, không nhầm tên tệp thành thứ tự thời gian.

Windows host được đo riêng trong `windows-runtime.json`: mốc giữa lượt còn khoảng905 MiB RAM vật lý khả dụng và2813 MiB commit khả dụng; không tự tăng RAM VMware/EVE. Đây là điều kiện cần theo dõi khi chạy demo, không kết luận dư tài nguyên Windows chỉ vì EVE còn RAM. Dữ liệu này không phải mẫu đồng thời với host bàn giao.

Core guest nhận khoảng961 MiB usable từ1024 MiB khai báo; ảnh core-compact cho used321/available639 MiB, swap0, hai service active. Firewall `hw.physmem=2102890496` byte và swapinfo không liệt kê swap device; các ảnh vmstat guest là số đo ngắn, không nghiệm thu tải IDS/IPS hoặc session lớn.

## 3.5. Validation sau tối ưu

| Hạng mục | Kết quả | Minh chứng và phạm vi |
|---|---|---|
| Core boot | PASS | core-shell/core-compact, đúng hostname |
| Primary boot | PASS | primary-ready-screen, primary-shell, primary-interfaces |
| Secondary boot | PASS | secondary-ready-screen, secondary-shell, secondary-interfaces |
| OVS/br-core-l2 | PASS | core-compact/core-l2; service active, bridge tồn tại |
| Core Layer2 | PASS | Không IP dữ liệu, forwarding IPv4/IPv6 bằng0 |
| VLAN30 | PASS | ARP nhận192.168.30.2/.3; bảng OVS và ifconfig |
| VLAN40 | PASS | ARP nhận192.168.40.2/.3 |
| VLAN50 | PASS | ARP nhận192.168.50.2/.3 |
| VLAN60 | PASS | ARP nhận192.168.60.2/.3 |
| VLAN99 | PASS | ARP nhận192.168.99.2/.3 |
| Trunk/access | PASS cấu hình và ARP phạm vi năm VLAN | ens3–ens7 access30/40/50/60/99; ens8/ens9/ens10 trunk30/40/50/60/99 |
| SYNC | PASS | vtnet2 UP;10.255.255.1/30 ↔ .2/30; ping2/2 mỗi hướng |
| Sync peer persistent | PASS | pfsyncinterface=opt6; peer đối ứng đúng trong ảnh persistent |
| pfsync runtime | FAIL | flags=0; không syncdev/syncpeer cả hai ảnh HA |
| syncok | Có giá trị1, không đủ để PASS | Interface chưa UP/chưa gắn peer |
| Demotion | PASS giá trị hiện tại | 0 ở cả hai; không chứng minh HA sẵn sàng |
| Config OPNsense không đổi | PASS | SHA-256 khớp checkpoint cả hai |
| OOM/swap host | PASS trong mẫu | Kernel log không có entry, si/so0; không bảo đảm tải dài hạn |
| Guest memory stress / dài hạn | NOT TESTED | Chưa tạo workload nặng |

`l2-arp-observation.json` chứa kết quả ARP thật qua access TAP hiện hữu: hai probe/địa chỉ, nguồn0.0.0.0, không gán IP host/guest. Có phản hồi hai MAC firewall trên đủ năm VLAN. Phép thử không thay thế nghiệm thu đầy đủ M2 về isolation, mirror, LACP hoặc hiệu năng. NAT/DHCP/routing không được kiểm lại.

### 3.5.1. Vấn đề pfsync và điểm dừng

Trước shutdown, pfsync UP/RUNNING, syncdev vtnet2, peer đúng, syncok1/demotion0. Sau reboot, cả hai pfsync0 flags0, không syncdev/syncpeer; syncok1 vẫn hiển thị. Persistent peer và checksum config vẫn đúng, đường SYNC ping hai chiều đạt. Hiện tượng tương tự đã được ghi trong `group1b-prerequisites-20261103/primary-audit.json` trước tối ưu: khi đó phải gọi native action để kích hoạt runtime. Đây là bằng chứng tiền sử, không khẳng định nguyên nhân của lần này.

Không có bằng chứng OOM/thiếu RAM làm pfsync lỗi; tăng RAM mù quáng không giải quyết được căn cứ này. Chưa gọi `/usr/local/sbin/pluginctl -c pfsync`, chưa sửa boot hook hoặc config. Việc áp lại pfsync/reload backend cần được xử lý trong phạm vi HA runtime riêng vì quyền tự khắc phục lượt này giới hạn lỗi trực tiếp do resource. Cần giải quyết cơ chế kích hoạt sau reboot và kiểm lại READY; không dùng apply tạm để che lỗi persistence.

Không rollback RAM tự động: ba guest boot, L2 hoạt động và host còn reserve; trả cả hai firewall về3072 khi Core vẫn chạy sẽ tái vượt ngân sách an toàn. Bản trước đủ để phục hồi có kiểm soát khi node OFF nếu cần; chưa thực hiện rollback.

## 3.6. Wazuh và các node chưa boot trong lượt này

Tài liệu/mã bootstrap hiện có `automation/wazuh_manager_bootstrap.py` mô tả Manager-only, Indexer/Dashboard chưa cài ở checkpoint lịch sử. Lượt này Wazuh OFF, chưa đọc package/service/RSS trong guest; không biến ý định bootstrap thành audit hiện tại. Manager: có hồ sơ triển khai lịch sử, hiện tại NOT TESTED; Indexer/Dashboard: hồ sơ lịch sử chưa cài, hiện tại NOT TESTED; Filebeat/thành phần khác: NOT TESTED. Giữ4096 MiB/2vCPU, không giảm tùy tiện. Cần audit riêng `dpkg-query`, service, RSS, available, swap và workload khi được tiếp tục; không cài thêm phần mềm.

Suricata/DC/DMZ giữ1024MiB/1vCPU, chưa boot/retest lần này. VPCS cần đo RSS thực tế; không áp tài nguyên QEMU cho VPCS. Do M3 chưa đạt pfsync prerequisite, dừng trước chu kỳ boot luân phiên các node còn lại. JSON observation có một bản bootstrap DMZ lịch sử đọc từ serial, được gắn cờ historical_not_current_runtime; không dùng làm kết quả runtime mới.

## 3.7. Kế hoạch demo — dự kiến, chưa thực thi

| Scenario | Tập node / phase | Guest QEMU (MiB) | Reserve tính toán (MiB) | Đánh giá |
|---|---|---:|---:|---|
| A — Network/HA | Core1024 + Primary2048 + Secondary2048 + VPCS tối thiểu | 5120 + RSS VPCS | 2777.78 trừ VPCS/overhead | Ba QEMU đã boot/L2; HA chưa đạt pfsync, VPCS chưa đo |
| B — SOC full cùng lúc | Core1024 + Primary2048 + Suricata1024 + Wazuh4096 + endpoint | 8192 + endpoint | -294.22 trước overhead | Không an toàn, không chạy |
| B1 — Detection capture | Core1024 + Primary2048 + Suricata1024 + VPCS | 4096 + RSS VPCS | 3801.78 trừ overhead | Dự kiến; tắt Secondary/Wazuh bằng soft shutdown trước phase |
| B2 — Manager/replay | Core1024 + Wazuh4096 + VPCS nếu cần | 5120 + RSS VPCS | 2777.78 trừ overhead | Dự kiến; không có firewall/Suricata live, không gọi end-to-end realtime |
| C — Ứng viên tối đa theo ngân sách | Ba node M3 + Suricata1024 | 6144 | 1753.78 trước overhead | Chưa kiểm chứng runtime/CPU, chưa được gọi maximum safe |

Tập đồng thời lớn nhất thực sự đã boot trong lượt: Core + hai firewall. Chưa xác định được maximum safe có tải và đầy đủ HA do pfsync FAIL. Không thêm DC/DMZ vào ScenarioC khi chưa đo overhead vì chỉ còn khoảng217.78MiB ngoài reserve1536. B1/B2 là kế hoạch tách phase, không triển khai M4/M5 và không giả vờ có dashboard Wazuh. Nếu cần full SOC live, phải có ngân sách/môi trường đủ hoặc một đợt đánh giá Manager-only giảm RAM được đo riêng; chưa áp dụng.

## 3.8. CARP final readiness

Do resource validation bắt buộc chưa PASS, không chạy một đợt CARP FINAL READINESS mới hoàn chỉnh. Kết quả hiện có: Core/L2 và năm VLAN đạt phạm vi đã kiểm; VIP .1 không trả ARP trong hai probe/VLAN (INCONCLUSIVE, không bảo đảm FREE); VHID conflict NOT TESTED; persistent VIP count0 ở cả hai từ ảnh persistent; pfsync FAIL; demotion0; RAM budget PASS. Chưa bắt protocol112 để xác minh VHID hoặc khả năng nhận CARP. Không dùng việc chưa có VIP nội bộ để loại trừ xung đột bên ngoài.

**NOT READY TO APPLY CARP.** Dừng ở báo cáo lỗi prerequisite, không tạo VIP và không chạy failover.

## 3.9. Hình minh chứng và giải thích

![OVS và RAM Core](../evidence/M3/resource-optimization-20261103/core-compact-20261103T224651+0700.png)

**Hình 3.1. RAM và bảng cổng OVS của Core sau tối ưu.** Mục đích: kiểm tài nguyên và giữ thiết kế M2. Nội dung: free, trạng thái service, access/trunk. Kết quả: service active, usable961MiB/available639MiB và đủ VLAN. Ý nghĩa: có bằng chứng guest sau giảm RAM; chưa thay cho kiểm tải dài hạn.

![Core Layer2](../evidence/M3/resource-optimization-20261103/core-l2-20261103T224744+0700.png)

**Hình 3.2. Core tiếp tục hoạt động Layer2.** Mục đích: bảo vệ kiến trúc. Nội dung: địa chỉ interface, forwarding và tên bridge. Kết quả: không có IP dữ liệu, forwarding0. Ý nghĩa: gateway/inter-VLAN vẫn thuộc OPNsense; journal filter trong ảnh bị console đổi chữ hoa nên không dùng riêng ảnh này để khẳng định mọi loại OOM guest đều vắng mặt.

![Primary HA](../evidence/M3/resource-optimization-20261103/primary-ha-20261103T224618+0700.png)

**Hình 3.3. Checksum và pfsync Primary sau boot.** Mục đích: kiểm giữ cấu hình và HA runtime. Nội dung: hai SHA-256, physmem, demotion, pfsync. Kết quả: checksum khớp nhưng flags0, thiếu peer. Ý nghĩa: ghi nhận lỗi thực tế, không kết luận READY từ syncok1.

![Secondary HA](../evidence/M3/resource-optimization-20261103/secondary-ha-20261103T224635+0700.png)

**Hình 3.4. Checksum và pfsync Secondary sau boot.** Mục đích: đối chiếu phía dự phòng. Nội dung và kết quả: checksum khớp, demotion0 nhưng pfsync chưa UP/chưa có peer. Ý nghĩa: lỗi prerequisite xuất hiện hai phía và cần xử lý riêng.

Các ảnh lấy từ framebuffer QEMU/RFB thực, toàn màn hình, không tạo ảnh từ text và không chỉnh nội dung kỹ thuật. Có ảnh boot trung gian và ảnh lệnh đầu dài làm trôi output; giữ nguyên, ưu tiên bốn hình trên và ảnh persistent/SYNC để đưa vào báo cáo. Lệnh grep -E trong lần thu đầu bị console nhận thành -e; không dùng phần grep rỗng làm bằng chứng mất SYNC, đã thu ifconfig trực tiếp và ping lại. Chưa có screenshot topology EVE/web hoặc terminal host; log host là output SSH thật. Xem manual-screenshot-guide.md để bổ sung ảnh thủ công, không coi hướng dẫn là ảnh đã có.

## 3.10. Thuật ngữ, nguồn và định dạng Word

RAM — Random Access Memory, bộ nhớ truy cập ngẫu nhiên — chứa dữ liệu làm việc của host/guest; cấp ít quá có thể gây lỗi boot/service, cấp quá tổng vật lý làm host thiếu reserve. Trong SOC này đã áp1024/2048/2048 và đo runtime. vCPU — virtual Central Processing Unit, CPU ảo — là luồng xử lý guest được host lập lịch; tổng5 vCPU hiện chia sẻ4 logical CPU, chưa kiểm tải SOC nặng. RSS — Resident Set Size, bộ nhớ thường trú tiến trình — đo trang đang ở RAM, khác RAM khai báo; chưa dùng RSS thấp để vượt budget. MemAvailable là ước lượng RAM Linux có thể cấp mà ít cần swap; reserve là phần ngân sách dành cho host/QEMU/console/cache, không phải một vùng RAM đã khóa.

SOC — Security Operations Center, trung tâm vận hành an toàn thông tin — kết hợp giám sát/phân tích/xử lý; lab này mới đo nhóm mạng M3. VLAN — Virtual Local Area Network, mạng LAN ảo — tách miền quảng bá Layer2; IEEE802.1Q gắn thẻ VLAN trên trunk, access port mang một VLAN cho endpoint. Ví dụ đã kiểm: ens3 access30, ens8/ens9 trunk năm VLAN, ARP hai firewall nhận đủ. OVS — Open vSwitch — là phần mềm chuyển mạch; bridge là thực thể nối các cổng cùng datapath, ở đây br-core-l2 đã kiểm. QEMU là tên sản phẩm ảo hóa, không tự khai triển; host chạy ba tiến trình guest với RAM đã xác nhận.

OPNsense là tên sản phẩm firewall, không tự khai triển. HA — High Availability, tính sẵn sàng cao — dùng nhiều thành viên và cơ chế phối hợp để giảm gián đoạn; chưa được nghiệm thu lần này. CARP — Common Address Redundancy Protocol, giao thức dự phòng địa chỉ chung — dự kiến bầu chọn chủ VIP qua quảng bá, VIP/VHID chưa apply. pfsync là cơ chế đồng bộ trạng thái PF qua interface/peer; lab dùng vtnet2 và mạng10.255.255.0/30, persistent peer đúng nhưng runtime không READY. Demotion là mức giảm ưu tiên CARP,0 không đồng nghĩa pfsync đã hoạt động.

Suricata là tên sản phẩm IDS/IPS; IDS — Intrusion Detection System, hệ thống phát hiện xâm nhập — phân tích traffic theo rule, IPS — Intrusion Prevention System, hệ thống ngăn chặn xâm nhập — có thể chặn trong đường truyền. Lab dự kiến cảm biến riêng, chưa kiểm tài nguyên mới. Wazuh là tên nền tảng bảo mật; Manager phân tích log, Indexer lưu/lập chỉ mục, Dashboard hiển thị, Filebeat chuyển log trong kiến trúc sử dụng thành phần này. Lượt này chỉ có hồ sơ Manager-only lịch sử, không suy diễn thành full stack đã kiểm.

Các thuật ngữ LACP, SPAN/port mirroring, QCOW2, cloud-init/NoCloud, SSH, NAT và DHCP cùng nguyên lý/vai trò/ví dụ được trình bày trong [TOPOLOGY_TERMS.md](../TOPOLOGY_TERMS.md); không triển khai hoặc nghiệm thu mới ở lượt này. Các kết luận dựa trên output nội bộ và hồ sơ dự án; không lấy minimum vendor chưa đối chiếu làm căn cứ cắt RAM. Khi xuất Word: A4, Times New Roman12–13, lề trái3cm/còn lại2cm, hình đánh số và chú thích phía dưới. Lượt này xuất Markdown, chưa xuất Word.

## 3.11. Bàn giao và phần chưa hoàn tất

Phần đã đạt: thay RAM có checkpoint, ba node boot, Core Layer2/OVS/VLAN đúng, hai firewall IP đúng, SYNC hai chiều, host không swap/OOM trong các cửa sổ đo. Phần chưa đạt: pfsync runtime sau reboot. Chưa thực hiện audit guest các node còn lại, kiểm workload dài hạn, maximum safe có tải hoặc readiness CARP đầy đủ. Báo cáo không thay kết luận chưa đạt thành hoàn thành toàn bộ mục tiêu.

Điểm cần xử lý tiếp là HA runtime/pfsync sau reboot, gồm native backend và cơ chế kích hoạt; chưa thực hiện vì chưa chứng minh lỗi trực tiếp do resource. RAM hiện giữ nguyên mức mới; ba console để sẵn shell. Toàn bộ evidence cũ được giữ nguyên.
