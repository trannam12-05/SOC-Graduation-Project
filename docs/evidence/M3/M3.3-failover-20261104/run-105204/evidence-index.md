# CHƯƠNG 3. KIỂM THỬ CARP FAILOVER VÀ RECOVERY — M3.3B

## 3.3.1. Phạm vi, phương pháp và kết quả

Thời điểm tổng hợp: 2026-11-04T11:07:14.319327+07:00 (UTC+07:00). **DONE/PASS**. Failover PASS: Primary đã tắt, Secondary tự MASTER cả VLAN30/40/50/60/99, đủ VIP .1 và ARP qua Core; recovery PASS: Primary tự MASTER, Secondary BACKUP năm VLAN; pfsync UP/RUNNING, syncok1, demotion0 hai phía; Core/VLAN hoạt động. Không áp lại native pfsync hoặc sửa CARP để đạt kết quả.

Core chỉ thực hiện Layer 2; gateway dự phòng vẫn ở OPNsense. CARP (Common Address Redundancy Protocol — giao thức dự phòng địa chỉ chung) cho phép một firewall MASTER phục vụ địa chỉ ảo (VIP — Virtual IP address), firewall BACKUP tiếp quản khi không còn nhận quảng bá của MASTER. Trong topology SOC này, năm VIP 192.168.30.1/40.1/50.1/60.1/99.1 ứng với VLAN30/40/50/60/99. Phép thử sử dụng tắt mềm Primary, giữ Core và Secondary hoạt động, rồi boot lại Primary sau khi nghiệm thu failover.

pfsync là tên chính thức của giao diện/giao thức đồng bộ trạng thái Packet Filter, không tự tạo dạng khai triển. Vai trò trong SOC là đồng bộ trạng thái giữa hai firewall qua SYNC 10.255.255.1/30 ↔ 10.255.255.2/30. Kiểm tra syncok1 và gói protocol240 hai chiều trong lượt này xác nhận readiness trước/sau, chưa chứng minh giữ phiên ứng dụng.

## 3.3.2. Bảng kết quả

| Pha | Trạng thái | Minh chứng chính |
|---|---|---|
| BEFORE | PASS | before-acceptance.json, runtime/host/ARP/CARP tương ứng |
| FAILOVER | PASS | failover-acceptance.json, runtime/host/ARP/CARP tương ứng |
| RECOVERY | PASS | recovery-acceptance.json, runtime/host/ARP/CARP tương ứng |

Config hai firewall được kiểm tra SHA-256 với backup trước phép thử; persistent VIP/VHID/advbase/advskew được đối chiếu trước/sau. Core và Secondary không bị stop/reboot: PID host được đối chiếu qua các pha. Primary phải có boottime mới ở recovery. Không dùng ảnh cũ để kết luận runtime mới. Thời điểm thu dựa trên đồng hồ collector chuyển sang UTC+07:00; giờ bên trong EVE/guest được giữ riêng và không dùng thay giờ thu.

Các bản `failover-*` đầu tiên được thu trong quá trình shutdown; nghiệm thu pha failover sử dụng bộ `failover-confirmed-*` sau khi host xác nhận Primary đã tắt. Trường ARP `vip_conflict_seen` trong collector tái sử dụng chỉ mang nghĩa quan sát trả lời VIP; trong phép thử này VIP đã cấu hình, trường đó không phải kết luận xung đột.

Lệnh đọc OVSDB trước test bằng sudo -n không chạy vì sudo cache đã hết hạn; giữ ảnh lỗi, không thay đổi xác thực. Core được kiểm tra qua systemctl, địa chỉ/forwarding, PID liên tục và ARP trên năm access port; không tuyên bố đã audit lại đầy đủ OVSDB nếu không có output.

## 3.3.3. Ảnh minh họa thực tế

![Hình 3.1. Lệnh shutdown mềm Primary.](primary-soft-shutdown-20261104T105514+0700.png)

Hình 3.1. Lệnh shutdown mềm Primary.

Mục đích, nội dung và ý nghĩa: Xác nhận đúng node nhận shutdown -p now; host sau đó kiểm tra QEMU đã kết thúc. Kết quả xem bảng và JSON nghiệm thu tương ứng; không suy rộng ngoài phạm vi.

![Hình 3.2. Secondary MASTER sau khi Primary tắt.](secondary-failover-readable-20261104T105925+0700.png)

Hình 3.2. Secondary MASTER sau khi Primary tắt.

Mục đích, nội dung và ý nghĩa: Đọc MASTER/VHID của năm VLAN và VIP .1; kết hợp ARP và quảng bá từ .3 chứng minh tiếp quản. Kết quả xem bảng và JSON nghiệm thu tương ứng; không suy rộng ngoài phạm vi.

![Hình 3.3. Primary sau recovery.](primary-recovery-readable-20261104T110634+0700.png)

Hình 3.3. Primary sau recovery.

Mục đích, nội dung và ý nghĩa: Đọc vai trò và VIP sau boot mới; nghiệm thu dựa trên recovery-acceptance.json. Kết quả xem bảng và JSON nghiệm thu tương ứng; không suy rộng ngoài phạm vi.

![Hình 3.4. Secondary sau recovery.](secondary-recovery-readable-20261104T110555+0700.png)

Hình 3.4. Secondary sau recovery.

Mục đích, nội dung và ý nghĩa: Đọc vai trò và VIP tương ứng; xác minh trở về BACKUP khi Primary phục hồi. Kết quả xem bảng và JSON nghiệm thu tương ứng; không suy rộng ngoài phạm vi.

![Hình 3.5. Core và dịch vụ OVS sau recovery.](core-recovery-public-20261104T110425+0700.png)

Hình 3.5. Core và dịch vụ OVS sau recovery.

Mục đích, nội dung và ý nghĩa: Kiểm tra OVS active, không IP ngoài loopback, forwarding0/0; kết hợp ARP năm VLAN chứng minh Core/VLAN tiếp tục hoạt động. Kết quả xem bảng và JSON nghiệm thu tương ứng; không suy rộng ngoài phạm vi.

![Hình 3.6. Pfsync và SYNC Primary sau recovery.](primary-recovery-pfsync-20261104T110658+0700.png)

Hình 3.6. Pfsync và SYNC Primary sau recovery.

Mục đích, nội dung và ý nghĩa: Đọc syncok1, demotion0, đúng peer và ping SYNC thành công; xác nhận Primary tự phục hồi pfsync. Kết quả xem bảng và JSON nghiệm thu tương ứng; không suy rộng ngoài phạm vi.

![Hình 3.7. Pfsync và SYNC Secondary sau recovery.](secondary-recovery-pfsync-20261104T110658+0700.png)

Hình 3.7. Pfsync và SYNC Secondary sau recovery.

Mục đích, nội dung và ý nghĩa: Đọc syncok1, demotion0 và ping thành công phía đối ứng; đối chiếu readiness hai firewall. Kết quả xem bảng và JSON nghiệm thu tương ứng; không suy rộng ngoài phạm vi.

## 3.3.4. Danh mục minh chứng

| Tệp | Nội dung | Thời điểm thu, múi giờ | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
| before-acceptance.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:55:01.766058+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/before-acceptance.json | M3.3 — pha tương ứng/phụ lục truy vết |
| before-arp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:53:29.116465+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/before-arp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| before-carp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:53:31.086503+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/before-carp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| before-pfsync.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:53:46.857971+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/before-pfsync.json | M3.3 — pha tương ứng/phụ lục truy vết |
| core-before-ovs-20261104T105429+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:54:39.688523+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-before-ovs-20261104T105429+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| core-before-ovs-20261104T105429+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:54:39.690604+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-before-ovs-20261104T105429+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| core-before-public-20261104T105328+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:53:39.395283+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-before-public-20261104T105328+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| core-before-public-20261104T105328+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:53:39.396373+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-before-public-20261104T105328+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| core-during-failover-20261104T105728+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:57:39.266418+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-during-failover-20261104T105728+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| core-during-failover-20261104T105728+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:57:39.267473+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-during-failover-20261104T105728+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| core-recovery-public-20261104T110425+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:04:36.000196+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-recovery-public-20261104T110425+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| core-recovery-public-20261104T110425+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:04:36.002521+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-recovery-public-20261104T110425+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| core-recovery-public-observation.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:29.685373+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/core-recovery-public-observation.json | M3.3 — pha tương ứng/phụ lục truy vết |
| failover-acceptance.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:59:25.297430+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/failover-acceptance.json | M3.3 — pha tương ứng/phụ lục truy vết |
| failover-arp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:55:57.676994+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/failover-arp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| failover-carp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:55:56.004642+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/failover-carp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| failover-confirmed-arp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:57:01.841677+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/failover-confirmed-arp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| failover-confirmed-carp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:57:02.270726+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/failover-confirmed-carp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| failover-confirmed-host.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:56:39.645053+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/failover-confirmed-host.json | M3.3 — pha tương ứng/phụ lục truy vết |
| failover-host.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:55:33.983393+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/failover-host.json | M3.3 — pha tương ứng/phụ lục truy vết |
| host-before.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:52:10.386320+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/host-before.json | M3.3 — pha tương ứng/phụ lục truy vết |
| M3.3-acceptance.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:07:14.319327+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/M3.3-acceptance.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-before-execute-20261104T105235+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:53:56.247821+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-before-execute-20261104T105235+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-before-execute-20261104T105235+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:53:56.249454+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-before-execute-20261104T105235+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-before-header-20261104T105356+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:54:20.285244+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-before-header-20261104T105356+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-before-header-20261104T105356+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:54:20.286313+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-before-header-20261104T105356+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-before-page-0-20261104T105420+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:54:44.362307+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-before-page-0-20261104T105420+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-before-page-0-20261104T105420+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:54:44.363414+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-before-page-0-20261104T105420+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-before.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:54:44.522254+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-before.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-1-20261104T110003+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:00:06.473216+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-1-20261104T110003+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-1-20261104T110003+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:00:06.474224+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-1-20261104T110003+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-2-20261104T110051+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:00:55.552088+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-2-20261104T110051+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-2-20261104T110051+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:00:55.554765+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-2-20261104T110051+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-3-20261104T110150+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:01:53.040876+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-3-20261104T110150+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-3-20261104T110150+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:01:53.044550+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-3-20261104T110150+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-4-20261104T110302+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:03:05.403063+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-4-20261104T110302+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-4-20261104T110302+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:03:05.405815+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-4-20261104T110302+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-5-20261104T110346+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:03:48.852588+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-5-20261104T110346+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-reboot-observe-5-20261104T110346+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:03:48.853665+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-reboot-observe-5-20261104T110346+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-execute-20261104T110503+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:34.967688+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-execute-20261104T110503+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-execute-20261104T110503+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:05:34.969833+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-execute-20261104T110503+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-header-20261104T110535+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:59.661231+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-header-20261104T110535+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-header-20261104T110535+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:05:59.662341+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-header-20261104T110535+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-page-0-20261104T110559+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:06:23.143210+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-page-0-20261104T110559+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-page-0-20261104T110559+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:06:23.146338+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-page-0-20261104T110559+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-pfsync-20261104T110658+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:07:06.805325+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-pfsync-20261104T110658+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-pfsync-20261104T110658+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:07:06.809014+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-pfsync-20261104T110658+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-readable-20261104T110634+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:06:43.938473+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-readable-20261104T110634+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-readable-20261104T110634+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:06:43.940500+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-readable-20261104T110634+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-shell-check-20261104T110446+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:04:48.164176+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-shell-check-20261104T110446+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery-shell-check-20261104T110446+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:04:48.165180+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery-shell-check-20261104T110446+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-recovery.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:06:23.279185+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-recovery.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-soft-shutdown-20261104T105514+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:55:21.395472+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-soft-shutdown-20261104T105514+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| primary-soft-shutdown-20261104T105514+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:55:21.396484+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/primary-soft-shutdown-20261104T105514+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| PROGRESS.md.before | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:48:57.094871+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/PROGRESS.md.before | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-acceptance.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:06:33.449061+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-acceptance.json | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-arp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:32.049488+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-arp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-booting-host.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:00:10.436513+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-booting-host.json | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-carp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:31.030469+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-carp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-host.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:12.555303+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-host.json | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-observe-arp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:04:16.568608+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-observe-arp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-observe-carp.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:04:15.574274+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-observe-carp.json | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-observe-pfsync.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:04:32.142075+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-observe-pfsync.json | M3.3 — pha tương ứng/phụ lục truy vết |
| recovery-pfsync.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:45.495696+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/recovery-pfsync.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-before-execute-20261104T105235+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:53:55.493471+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-before-execute-20261104T105235+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-before-execute-20261104T105235+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:53:55.496121+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-before-execute-20261104T105235+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-before-header-20261104T105355+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:54:19.652014+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-before-header-20261104T105355+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-before-header-20261104T105355+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:54:19.653083+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-before-header-20261104T105355+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-before-page-0-20261104T105419+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:54:43.846180+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-before-page-0-20261104T105419+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-before-page-0-20261104T105419+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:54:43.847326+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-before-page-0-20261104T105419+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-before.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:54:43.975929+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-before.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-confirmed-execute-20261104T105710+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:57:34.821985+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-confirmed-execute-20261104T105710+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-confirmed-execute-20261104T105710+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:57:34.825784+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-confirmed-execute-20261104T105710+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-confirmed-header-20261104T105735+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:57:59.478655+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-confirmed-header-20261104T105735+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-confirmed-header-20261104T105735+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:57:59.481244+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-confirmed-header-20261104T105735+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-confirmed-page-0-20261104T105759+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:58:23.966309+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-confirmed-page-0-20261104T105759+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-confirmed-page-0-20261104T105759+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:58:23.968480+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-confirmed-page-0-20261104T105759+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-confirmed.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:58:24.107265+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-confirmed.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-execute-20261104T105545+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:56:09.482543+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-execute-20261104T105545+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-execute-20261104T105545+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:56:09.484610+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-execute-20261104T105545+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-header-20261104T105609+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:56:33.563707+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-header-20261104T105609+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-header-20261104T105609+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:56:33.564924+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-header-20261104T105609+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-page-0-20261104T105633+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:56:58.065049+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-page-0-20261104T105633+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-page-0-20261104T105633+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:56:58.066647+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-page-0-20261104T105633+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-readable-20261104T105925+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:59:35.212646+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-readable-20261104T105925+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover-readable-20261104T105925+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T10:59:35.213144+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover-readable-20261104T105925+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-failover.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:56:58.194820+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-failover.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-execute-20261104T110415+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:04:39.722015+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-execute-20261104T110415+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-execute-20261104T110415+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:04:39.723835+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-execute-20261104T110415+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-header-20261104T110439+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:04.311297+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-header-20261104T110439+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-header-20261104T110439+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:05:04.312326+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-header-20261104T110439+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-page-0-20261104T110504+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:33.470912+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-page-0-20261104T110504+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-page-0-20261104T110504+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:05:33.473605+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-page-0-20261104T110504+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-pfsync-20261104T110658+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:07:07.167017+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-pfsync-20261104T110658+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-pfsync-20261104T110658+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:07:07.169140+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-pfsync-20261104T110658+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-readable-20261104T110555+0700.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:06:03.285975+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-readable-20261104T110555+0700.json | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery-readable-20261104T110555+0700.png | Ảnh console thật, nguyên nội dung | 2026-11-04T11:06:03.287627+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery-readable-20261104T110555+0700.png | M3.3 — pha tương ứng/phụ lục truy vết |
| secondary-recovery.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T11:05:33.614750+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/secondary-recovery.json | M3.3 — pha tương ứng/phụ lục truy vết |
| shutdown-action.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:55:14.322394+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/shutdown-action.json | M3.3 — pha tương ứng/phụ lục truy vết |
| shutdown-wait-host.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:56:13.605138+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/shutdown-wait-host.json | M3.3 — pha tương ứng/phụ lục truy vết |
| SOC_TO_DO.md.before | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:48:57.083541+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/SOC_TO_DO.md.before | M3.3 — pha tương ứng/phụ lục truy vết |
| start-OPNsense-Primary.json | Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha | 2026-11-04T10:59:43.934710+07:00 | docs/evidence/M3/M3.3-failover-20261104/run-105204/start-OPNsense-Primary.json | M3.3 — pha tương ứng/phụ lục truy vết |
| m33b-primary-shell-20261104T105211+0700.json | Kiểm tra console/shell trước gửi lệnh; ảnh thật và metadata | 2026-11-04T10:52:14.159657+07:00 | docs/evidence/M3/M3.3-failover-20261104/m33b-primary-shell-20261104T105211+0700.json | M3.3 — kiểm tra transport ban đầu |
| m33b-primary-shell-20261104T105211+0700.png | Kiểm tra console/shell trước gửi lệnh; ảnh thật và metadata | 2026-11-04T10:52:14.160161+07:00 | docs/evidence/M3/M3.3-failover-20261104/m33b-primary-shell-20261104T105211+0700.png | M3.3 — kiểm tra transport ban đầu |
| m33b-secondary-shell-20261104T105211+0700.json | Kiểm tra console/shell trước gửi lệnh; ảnh thật và metadata | 2026-11-04T10:52:13.654780+07:00 | docs/evidence/M3/M3.3-failover-20261104/m33b-secondary-shell-20261104T105211+0700.json | M3.3 — kiểm tra transport ban đầu |
| m33b-secondary-shell-20261104T105211+0700.png | Kiểm tra console/shell trước gửi lệnh; ảnh thật và metadata | 2026-11-04T10:52:13.656804+07:00 | docs/evidence/M3/M3.3-failover-20261104/m33b-secondary-shell-20261104T105211+0700.png | M3.3 — kiểm tra transport ban đầu |

## 3.3.5. Giới hạn và điểm dừng

Failover PASS: Primary đã tắt, Secondary tự MASTER cả VLAN30/40/50/60/99, đủ VIP .1 và ARP qua Core; recovery PASS: Primary tự MASTER, Secondary BACKUP năm VLAN; pfsync UP/RUNNING, syncok1, demotion0 hai phía; Core/VLAN hoạt động. Không áp lại native pfsync hoặc sửa CARP để đạt kết quả. Không kiểm thử giữ phiên TCP/UDP, thời gian gián đoạn ứng dụng, NAT/DHCP hoặc M4/M5. Dừng sau M3.3; chưa có NEXT TODO được giao.
