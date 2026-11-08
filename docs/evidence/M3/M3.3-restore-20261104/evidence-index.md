# 1. M3.3 — Khôi phục điều kiện đầu

## 1.1. Kết luận

**READY_FOR_FAILOVER** lúc 2026-11-04T10:48:54.279347+07:00 (UTC+07:00). Chỉ khôi phục điều kiện đầu; chưa chạy failover/recovery và chưa kết luận M3.3 DONE/PASS. Các kiểm tra bắt buộc đã đạt từ runtime guest, ARP qua Core và gói thật trên SYNC/trunk. Không sửa cấu hình guest; có gọi lại native pfsync trên Primary theo quyền khôi phục M3.1.

## 1.2. Bảng kết quả

| Hạng mục | Kết quả | Minh chứng |
|---|---|---|
| Đúng ba QEMU, RAM 1024/2048/2048 MiB | PASS | host-final.json |
| OVS, Core chỉ L2, access/trunk năm VLAN, flow NORMAL | PASS | core-public-proof, core-ovs-compact; arp-restored.json |
| Primary .2, Secondary .3 và VIP .1 cả năm VLAN | PASS | hai runtime-restored.json; arp-restored.json |
| SYNC ping; pfsync UP/RUNNING, đúng peer, syncok1 | PASS | hai runtime-restored.json; pfsync-restored.json |
| Demotion0; hook đúng boot | PASS | hai runtime-restored.json |
| Primary MASTER / Secondary BACKUP cả năm VLAN | PASS | hai runtime-restored.json; carp-restored.json |
| Cấu hình giữ nguyên từ M3.2 | PASS | hash trong runtime-restored.json đối chiếu carp-verified cũ |
| Failover/recovery | NOT_RUN | Ngoài phạm vi lượt này |

## 1.3. Ảnh minh họa

![Hình 3.1. Core sau boot: dịch vụ OVS, địa chỉ và forwarding.](core-public-proof-20261104T103549+0700.png)

Hình 3.1. Core sau boot: dịch vụ OVS, địa chỉ và forwarding.

Mục đích, nội dung, kết quả và ý nghĩa: Xác nhận Core chỉ chuyển mạch Layer 2; OVS active, không IP ngoài loopback và forwarding0/0.

![Hình 3.2. Bảng port VLAN/trunk và flow NORMAL.](core-ovs-compact-20261104T103726+0700.png)

Hình 3.2. Bảng port VLAN/trunk và flow NORMAL.

Mục đích, nội dung, kết quả và ý nghĩa: Xác nhận mapping access/trunk và flow chuyển mạch đã tự phục hồi; ARP năm VLAN kiểm chứng đường dữ liệu.

![Hình 3.3. Primary MASTER trên năm VLAN.](primary-carp-readable-20261104T104812+0700.png)

Hình 3.3. Primary MASTER trên năm VLAN.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc IP .2, VIP .1 và MASTER/VHID30/40/50/60/99, advbase1/skew0; khẳng định vai trò ban đầu đã khôi phục.

![Hình 3.4. Secondary BACKUP trên năm VLAN.](secondary-carp-readable-20261104T104812+0700.png)

Hình 3.4. Secondary BACKUP trên năm VLAN.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc IP .3, VIP .1 và BACKUP cả năm VHID, skew100; xác nhận thiết kế dự phòng.

![Hình 3.5. Pfsync và SYNC Primary sau khôi phục.](primary-pfsync-readable-20261104T104825+0700.png)

Hình 3.5. Pfsync và SYNC Primary sau khôi phục.

Mục đích, nội dung, kết quả và ý nghĩa: Pfsync UP/RUNNING, syncok1, demotion0 và ping SYNC thành công; chứng minh readiness hiện tại sau native restore.

![Hình 3.6. Pfsync và SYNC Secondary.](secondary-pfsync-readable-20261104T104825+0700.png)

Hình 3.6. Pfsync và SYNC Secondary.

Mục đích, nội dung, kết quả và ý nghĩa: Pfsync UP/RUNNING, syncok1, demotion0 và ping SYNC thành công; đối chiếu hai phía.

## 1.4. Giới hạn và checkpoint tiếp tục

CARP (Common Address Redundancy Protocol — giao thức dự phòng địa chỉ chung) cho phép một firewall MASTER phục vụ VIP và firewall BACKUP tiếp quản khi mất quảng bá. Trong SOC, VIP là gateway dự phòng của năm VLAN. Lượt này đã xác minh vai trò ban đầu; việc tiếp quản và phục hồi chưa được kiểm thử. pfsync là tên giao diện/giao thức đồng bộ trạng thái của Packet Filter; gói hai chiều và syncok1 chứng minh readiness, không tự chứng minh giữ phiên khi failover. M3.1/M3.2 giữ PASS; bước tiếp tục duy nhất là phép thử M3.3 khi được yêu cầu.

Collector ARP tái sử dụng tên `vip_conflict_seen`; ở lượt này trường đó chỉ là quan sát trả lời VIP, không có nghĩa phát hiện xung đột. Collector đầu trên Primary có lỗi cú pháp và chưa chạy phần thân; giữ ảnh lỗi để truy vết, nghiệm thu dùng `runtime-restored.json` đã truyền và xác minh SHA-256. Không dùng ảnh boot hoặc ảnh lỗi để thay kết quả guest. Hai ảnh `carp-final-proof` không có output do tùy chọn grep qua keyboard bị đổi chữ hoa/thường; không dùng để nghiệm thu. Ảnh `carp-readable` là lần thu thay thế có đầy đủ nội dung, vẫn giữ nguyên ảnh lỗi.

Sau boot đồng thời, Primary từng BACKUP năm VLAN, syncok0/demotion240; Secondary MASTER, syncok1/demotion0. Đã backup config và gọi đúng `/usr/local/sbin/pluginctl -c pfsync` trên Primary, native_rc0; sau đó Primary syncok1/demotion0/MASTER, Secondary về BACKUP. Không đặt demotion thủ công, không đổi CARP parameters. Vì đã cần can thiệp runtime, lượt này không chứng minh hai firewall tự đạt readiness khi boot đồng thời; nguyên nhân bulk-sync ban đầu chưa được kết luận. Minh chứng trước/sau giữ nguyên.

Hai firewall tự khôi phục journal khi boot và báo hệ thống tệp sạch; không can thiệp thủ công. Node/resource/interface mapping trước/sau giữ nguyên khi bỏ qua tọa độ left/top của giao diện; không kết luận toàn tệp lab nguyên byte nếu hash khác.

## 1.5. Danh mục tệp và thời điểm

| Tệp | Nội dung | Thời điểm thu (UTC+07:00) | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
| __pycache__ | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:42:56.848821+07:00 | docs/evidence/M3/M3.3-restore-20261104/__pycache__ | M3.3 — điều kiện đầu/phụ lục truy vết |
| arp-after-boot.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:33:32.496615+07:00 | docs/evidence/M3/M3.3-restore-20261104/arp-after-boot.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| arp-boot-observation.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:30:23.515338+07:00 | docs/evidence/M3/M3.3-restore-20261104/arp-boot-observation.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| arp-restored.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:46:27.071146+07:00 | docs/evidence/M3/M3.3-restore-20261104/arp-restored.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| authenticated-check-0-20261104T103814+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:38:17.389899+07:00 | docs/evidence/M3/M3.3-restore-20261104/authenticated-check-0-20261104T103814+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| authenticated-check-0-20261104T103814+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:38:17.392593+07:00 | docs/evidence/M3/M3.3-restore-20261104/authenticated-check-0-20261104T103814+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| authenticated-check-1-20261104T103814+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:38:17.619562+07:00 | docs/evidence/M3/M3.3-restore-20261104/authenticated-check-1-20261104T103814+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| authenticated-check-1-20261104T103814+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:38:17.621075+07:00 | docs/evidence/M3/M3.3-restore-20261104/authenticated-check-1-20261104T103814+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| authenticated-check-2-20261104T103814+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:38:17.707097+07:00 | docs/evidence/M3/M3.3-restore-20261104/authenticated-check-2-20261104T103814+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| authenticated-check-2-20261104T103814+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:38:17.708606+07:00 | docs/evidence/M3/M3.3-restore-20261104/authenticated-check-2-20261104T103814+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-check-0-20261104T103240+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:32:45.669449+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-check-0-20261104T103240+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-check-0-20261104T103240+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:32:45.671472+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-check-0-20261104T103240+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-check-1-20261104T103240+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:32:45.825656+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-check-1-20261104T103240+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-check-1-20261104T103240+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:32:45.828797+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-check-1-20261104T103240+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-check-2-20261104T103240+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:32:45.655624+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-check-2-20261104T103240+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-check-2-20261104T103240+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:32:45.658156+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-check-2-20261104T103240+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-complete-check-0-20261104T103743+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:37:47.110042+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-complete-check-0-20261104T103743+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-complete-check-0-20261104T103743+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:37:47.112074+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-complete-check-0-20261104T103743+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-complete-check-1-20261104T103743+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:37:47.437746+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-complete-check-1-20261104T103743+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-complete-check-1-20261104T103743+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:37:47.440430+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-complete-check-1-20261104T103743+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-final-observe-0-20261104T103528+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:35:35.543153+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-final-observe-0-20261104T103528+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-final-observe-0-20261104T103528+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:35:35.548599+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-final-observe-0-20261104T103528+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-final-observe-1-20261104T103528+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:35:35.152316+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-final-observe-1-20261104T103528+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-final-observe-1-20261104T103528+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:35:35.159806+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-final-observe-1-20261104T103528+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-final-observe-2-20261104T103528+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:35:35.444281+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-final-observe-2-20261104T103528+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-final-observe-2-20261104T103528+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:35:35.445985+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-final-observe-2-20261104T103528+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-observe-20261104T102931+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:29:35.993174+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-observe-20261104T102931+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-observe-20261104T102931+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:29:35.994997+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-observe-20261104T102931+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-progress-0-20261104T103138+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:31:42.745951+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-progress-0-20261104T103138+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-progress-0-20261104T103138+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:31:42.758995+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-progress-0-20261104T103138+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-progress-1-20261104T103138+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:31:42.971563+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-progress-1-20261104T103138+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-progress-1-20261104T103138+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:31:42.976468+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-progress-1-20261104T103138+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-progress-2-20261104T103138+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:31:42.956152+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-progress-2-20261104T103138+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-progress-2-20261104T103138+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:31:42.961094+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-progress-2-20261104T103138+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| boot-wait.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:31:01.516401+07:00 | docs/evidence/M3/M3.3-restore-20261104/boot-wait.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| carp-after-boot.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:34:30.305066+07:00 | docs/evidence/M3/M3.3-restore-20261104/carp-after-boot.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| carp-boot-passive.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:31:36.662006+07:00 | docs/evidence/M3/M3.3-restore-20261104/carp-boot-passive.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| carp-restored.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:46:29.324115+07:00 | docs/evidence/M3/M3.3-restore-20261104/carp-restored.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| console-current-0-20261104T103425+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:34:29.990868+07:00 | docs/evidence/M3/M3.3-restore-20261104/console-current-0-20261104T103425+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| console-current-0-20261104T103425+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:34:29.992532+07:00 | docs/evidence/M3/M3.3-restore-20261104/console-current-0-20261104T103425+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| console-current-1-20261104T103425+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:34:30.065614+07:00 | docs/evidence/M3/M3.3-restore-20261104/console-current-1-20261104T103425+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| console-current-1-20261104T103425+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:34:30.068928+07:00 | docs/evidence/M3/M3.3-restore-20261104/console-current-1-20261104T103425+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| console-current-2-20261104T103425+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:34:30.262805+07:00 | docs/evidence/M3/M3.3-restore-20261104/console-current-2-20261104T103425+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| console-current-2-20261104T103425+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:34:30.264827+07:00 | docs/evidence/M3/M3.3-restore-20261104/console-current-2-20261104T103425+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| core-ovs-compact-20261104T103726+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:37:36.399617+07:00 | docs/evidence/M3/M3.3-restore-20261104/core-ovs-compact-20261104T103726+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| core-ovs-compact-20261104T103726+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:37:36.401644+07:00 | docs/evidence/M3/M3.3-restore-20261104/core-ovs-compact-20261104T103726+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| core-ovs-proof-20261104T103703+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:37:12.679015+07:00 | docs/evidence/M3/M3.3-restore-20261104/core-ovs-proof-20261104T103703+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| core-ovs-proof-20261104T103703+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:37:12.680158+07:00 | docs/evidence/M3/M3.3-restore-20261104/core-ovs-proof-20261104T103703+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| core-public-proof-20261104T103549+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:36:02.607740+07:00 | docs/evidence/M3/M3.3-restore-20261104/core-public-proof-20261104T103549+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| core-public-proof-20261104T103549+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:36:02.611194+07:00 | docs/evidence/M3/M3.3-restore-20261104/core-public-proof-20261104T103549+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| fw-boot-wait-0-20261104T103646+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:36:50.588929+07:00 | docs/evidence/M3/M3.3-restore-20261104/fw-boot-wait-0-20261104T103646+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| fw-boot-wait-0-20261104T103646+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:36:50.590524+07:00 | docs/evidence/M3/M3.3-restore-20261104/fw-boot-wait-0-20261104T103646+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| fw-boot-wait-1-20261104T103646+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:36:50.570894+07:00 | docs/evidence/M3/M3.3-restore-20261104/fw-boot-wait-1-20261104T103646+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| fw-boot-wait-1-20261104T103646+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:36:50.573004+07:00 | docs/evidence/M3/M3.3-restore-20261104/fw-boot-wait-1-20261104T103646+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| fw-ready-0-20261104T103342+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:33:49.408970+07:00 | docs/evidence/M3/M3.3-restore-20261104/fw-ready-0-20261104T103342+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| fw-ready-0-20261104T103342+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:33:49.409979+07:00 | docs/evidence/M3/M3.3-restore-20261104/fw-ready-0-20261104T103342+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| fw-ready-1-20261104T103342+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:33:49.018091+07:00 | docs/evidence/M3/M3.3-restore-20261104/fw-ready-1-20261104T103342+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| fw-ready-1-20261104T103342+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:33:49.023818+07:00 | docs/evidence/M3/M3.3-restore-20261104/fw-ready-1-20261104T103342+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| host-before.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:29:09.613796+07:00 | docs/evidence/M3/M3.3-restore-20261104/host-before.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| host-booting.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:32:01.426552+07:00 | docs/evidence/M3/M3.3-restore-20261104/host-booting.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| host-final.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:48:54.279347+07:00 | docs/evidence/M3/M3.3-restore-20261104/host-final.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| M3.3-readiness.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:48:54.279347+07:00 | docs/evidence/M3/M3.3-restore-20261104/M3.3-readiness.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| pfsync-passive-after-boot.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:34:05.682959+07:00 | docs/evidence/M3/M3.3-restore-20261104/pfsync-passive-after-boot.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| pfsync-restored.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:46:43.731111+07:00 | docs/evidence/M3/M3.3-restore-20261104/pfsync-restored.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-boot-20261104T102943+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:29:45.900556+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-boot-20261104T102943+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-boot-20261104T102943+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:29:45.901057+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-boot-20261104T102943+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-carp-diagnostic-20261104T104348+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:43:57.079080+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-carp-diagnostic-20261104T104348+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-carp-diagnostic-20261104T104348+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:43:57.080251+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-carp-diagnostic-20261104T104348+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-carp-final-proof-20261104T104746+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:47:55.500335+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-carp-final-proof-20261104T104746+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-carp-final-proof-20261104T104746+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:47:55.500827+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-carp-final-proof-20261104T104746+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-carp-readable-20261104T104812+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:48:19.516019+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-carp-readable-20261104T104812+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-carp-readable-20261104T104812+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:48:19.517026+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-carp-readable-20261104T104812+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-native-pfsync-restore-20261104T104434+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:44:50.173200+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-native-pfsync-restore-20261104T104434+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-native-pfsync-restore-20261104T104434+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:44:50.173704+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-native-pfsync-restore-20261104T104434+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-native-pfsync-settled-20261104T104514+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:45:17.346185+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-native-pfsync-settled-20261104T104514+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-native-pfsync-settled-20261104T104514+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:45:17.347186+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-native-pfsync-settled-20261104T104514+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-pfsync-readable-20261104T104825+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:48:35.344983+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-pfsync-readable-20261104T104825+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-pfsync-readable-20261104T104825+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:48:35.346246+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-pfsync-readable-20261104T104825+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-execute-20261104T103915+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:40:31.361906+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-execute-20261104T103915+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-execute-20261104T103915+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:40:31.364409+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-execute-20261104T103915+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-header-20261104T104031+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:40:56.557903+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-header-20261104T104031+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-header-20261104T104031+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:40:56.558903+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-header-20261104T104031+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-restored-execute-20261104T104530+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:46:48.545193+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-restored-execute-20261104T104530+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-restored-execute-20261104T104530+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:46:48.547379+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-restored-execute-20261104T104530+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-restored-header-20261104T104649+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:47:14.419589+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-restored-header-20261104T104649+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-restored-header-20261104T104649+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:47:14.420598+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-restored-header-20261104T104649+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-restored-page-0-20261104T104714+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:47:40.172008+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-restored-page-0-20261104T104714+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-restored-page-0-20261104T104714+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:47:40.173520+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-restored-page-0-20261104T104714+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-restored.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:47:40.317194+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-restored.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-valid-execute-20261104T104106+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:42:23.128890+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-valid-execute-20261104T104106+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-valid-execute-20261104T104106+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:42:23.130274+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-valid-execute-20261104T104106+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-valid-header-20261104T104223+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:42:49.421027+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-valid-header-20261104T104223+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-valid-header-20261104T104223+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:42:49.422093+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-valid-header-20261104T104223+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-valid-page-0-20261104T104249+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:43:12.292833+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-valid-page-0-20261104T104249+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-valid-page-0-20261104T104249+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:43:12.296010+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-valid-page-0-20261104T104249+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| primary-runtime-valid.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:43:12.442479+07:00 | docs/evidence/M3/M3.3-restore-20261104/primary-runtime-valid.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| PROGRESS.md.before | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:28:08.740929+07:00 | docs/evidence/M3/M3.3-restore-20261104/PROGRESS.md.before | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-boot-20261104T102943+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:29:46.216955+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-boot-20261104T102943+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-boot-20261104T102943+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:29:46.218073+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-boot-20261104T102943+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-carp-diagnostic-20261104T104326+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:43:36.988019+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-carp-diagnostic-20261104T104326+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-carp-diagnostic-20261104T104326+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:43:36.989633+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-carp-diagnostic-20261104T104326+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-carp-final-proof-20261104T104746+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:47:54.433486+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-carp-final-proof-20261104T104746+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-carp-final-proof-20261104T104746+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:47:54.435088+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-carp-final-proof-20261104T104746+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-carp-readable-20261104T104812+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:48:19.554165+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-carp-readable-20261104T104812+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-carp-readable-20261104T104812+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:48:19.557123+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-carp-readable-20261104T104812+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-confirm-shell-enter-20261104T103909+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:39:14.765529+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-confirm-shell-enter-20261104T103909+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-confirm-shell-enter-20261104T103909+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:39:14.776619+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-confirm-shell-enter-20261104T103909+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-pfsync-readable-20261104T104825+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:48:35.394050+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-pfsync-readable-20261104T104825+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-pfsync-readable-20261104T104825+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:48:35.396061+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-pfsync-readable-20261104T104825+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-restored-execute-20261104T104530+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:46:48.647409+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-restored-execute-20261104T104530+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-restored-execute-20261104T104530+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:46:48.649421+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-restored-execute-20261104T104530+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-restored-header-20261104T104649+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:47:14.941780+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-restored-header-20261104T104649+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-restored-header-20261104T104649+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:47:14.942809+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-restored-header-20261104T104649+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-restored-page-0-20261104T104715+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:47:40.236234+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-restored-page-0-20261104T104715+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-restored-page-0-20261104T104715+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:47:40.237475+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-restored-page-0-20261104T104715+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-restored.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:47:40.369790+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-restored.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-valid-execute-20261104T103944+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:41:00.843708+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-valid-execute-20261104T103944+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-valid-execute-20261104T103944+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:41:00.846372+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-valid-execute-20261104T103944+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-valid-header-20261104T104101+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:41:26.091407+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-valid-header-20261104T104101+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-valid-header-20261104T104101+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:41:26.092471+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-valid-header-20261104T104101+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-valid-page-0-20261104T104126+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:41:49.672347+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-valid-page-0-20261104T104126+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-valid-page-0-20261104T104126+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:41:49.676606+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-valid-page-0-20261104T104126+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-runtime-valid.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:41:49.836043+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-runtime-valid.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-shell-check-20261104T103854+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:38:56.932865+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-shell-check-20261104T103854+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| secondary-shell-check-20261104T103854+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:38:56.936902+07:00 | docs/evidence/M3/M3.3-restore-20261104/secondary-shell-check-20261104T103854+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| settled-0-20261104T103017+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:30:21.378080+07:00 | docs/evidence/M3/M3.3-restore-20261104/settled-0-20261104T103017+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| settled-0-20261104T103017+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:30:21.379377+07:00 | docs/evidence/M3/M3.3-restore-20261104/settled-0-20261104T103017+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| settled-1-20261104T103017+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:30:21.385747+07:00 | docs/evidence/M3/M3.3-restore-20261104/settled-1-20261104T103017+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| settled-1-20261104T103017+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:30:21.386764+07:00 | docs/evidence/M3/M3.3-restore-20261104/settled-1-20261104T103017+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| settled-2-20261104T103017+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:30:21.297991+07:00 | docs/evidence/M3/M3.3-restore-20261104/settled-2-20261104T103017+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| settled-2-20261104T103017+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:30:21.299690+07:00 | docs/evidence/M3/M3.3-restore-20261104/settled-2-20261104T103017+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| SOC_TO_DO.md.before | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:28:08.739650+07:00 | docs/evidence/M3/M3.3-restore-20261104/SOC_TO_DO.md.before | M3.3 — điều kiện đầu/phụ lục truy vết |
| start-OPNsense-Primary.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:29:23.992218+07:00 | docs/evidence/M3/M3.3-restore-20261104/start-OPNsense-Primary.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| start-OPNsense-Secondary.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:29:26.359476+07:00 | docs/evidence/M3/M3.3-restore-20261104/start-OPNsense-Secondary.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| start-SOC-Core-L2.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:29:21.635885+07:00 | docs/evidence/M3/M3.3-restore-20261104/start-SOC-Core-L2.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| wait-boot-0-20261104T103059+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:31:03.341913+07:00 | docs/evidence/M3/M3.3-restore-20261104/wait-boot-0-20261104T103059+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| wait-boot-0-20261104T103059+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:31:03.349865+07:00 | docs/evidence/M3/M3.3-restore-20261104/wait-boot-0-20261104T103059+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| wait-boot-1-20261104T103059+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:31:03.508566+07:00 | docs/evidence/M3/M3.3-restore-20261104/wait-boot-1-20261104T103059+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| wait-boot-1-20261104T103059+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:31:03.510597+07:00 | docs/evidence/M3/M3.3-restore-20261104/wait-boot-1-20261104T103059+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
| wait-boot-2-20261104T103059+0700.json | Log/JSON runtime hoặc metadata; xem tên và nội dung tệp | 2026-11-04T10:31:03.947568+07:00 | docs/evidence/M3/M3.3-restore-20261104/wait-boot-2-20261104T103059+0700.json | M3.3 — điều kiện đầu/phụ lục truy vết |
| wait-boot-2-20261104T103059+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T10:31:03.951136+07:00 | docs/evidence/M3/M3.3-restore-20261104/wait-boot-2-20261104T103059+0700.png | M3.3 — điều kiện đầu/phụ lục truy vết |
