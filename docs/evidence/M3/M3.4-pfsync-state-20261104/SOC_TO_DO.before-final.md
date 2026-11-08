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
| M3.4 — Kiểm thử pfsync state synchronization khi CARP failover | IN_PROGRESS — 2026-11-04T11:14:31.347431+07:00 | `evidence/M3/M3.4-pfsync-state-20261104/`; chưa nghiệm thu |

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