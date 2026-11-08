# CHƯƠNG 3. KIỂM THỬ ĐỒNG BỘ STATE PFSYNC KHI CARP FAILOVER — M3.4

## 3.4.1. Kết luận và phạm vi

**FAIL/BLOCKED**, tổng hợp lúc 2026-11-04T16:20:04.824645+07:00 (UTC+07:00). Đồng bộ state trước failover có bằng chứng PASS; đã quan sát dữ liệu tiếp tục qua Secondary sau khi Primary tắt. Gián đoạn/restart môi trường EVE: khi tiếp tục, host uptime khoảng 3 phút, không có QEMU hoặc client test chạy. Chưa thu đủ native state sau failover, chưa hoàn tất HTTP và chưa kiểm chứng recovery. Tác nhân gây restart chưa xác minh. Không biến phần kết quả đạt thành nghiệm thu toàn M3.4.

Thời gian thu dựa trên collector chuyển sang UTC+07:00. Giờ EVE/guest được ghi là untrusted. Khoảng thời gian tương đối trong client/wire dùng monotonic của lần chạy cũ; không dùng snapshot cũ để suy uptime hoặc kết nối hiện tại. Đợt gốc thu khoảng11:10–11:24; lượt tiếp quản thu lại khoảng16:14 trở đi cùng ngày04/11/2026.

## 3.4.2. Thiết kế phép thử và thuật ngữ

TCP (Transmission Control Protocol — giao thức điều khiển truyền vận) theo dõi sequence/acknowledgement để truyền dữ liệu tin cậy. State của Packet Filter (PF — tên bộ lọc gói) lưu flow và trạng thái hai chiều. pfsync là tên chính thức của cơ chế/giao diện đồng bộ state, không tự tạo dạng khai triển. Trong SOC, state đồng bộ cho phép firewall dự phòng xử lý flow đang có thay vì chỉ nhận kết nối mới. Ví dụ đã kiểm chứng: hai state ID của flow bên dưới hiện diện trên Secondary lúc BACKUP, có cùng creator ID và sequence window như Primary.

CARP (Common Address Redundancy Protocol — giao thức dự phòng địa chỉ chung) điều phối firewall phục vụ Virtual IP address (VIP — địa chỉ IP ảo). VIP VLAN40 .40.1 được client dùng làm gateway; chiều về dùng VIP VLAN30 .30.1. HTTP (Hypertext Transfer Protocol — giao thức truyền siêu văn bản) là lưu lượng ứng dụng lành tính trên dịch vụ DC đã có TCP8000. Lượt này mở đúng một TCP session và giữ một HTTP request chưa kết thúc header để đọc state; không tạo nhiều kết nối hoặc tấn công dịch vụ.

Client là script TCP qua AF_PACKET trên host EVE hiện có, gắn vào access TAP `vunl0_3_1` có sẵn, không thêm interface/link hoặc gán IP vào network stack host. Không báo đây là VPCS hay TCP socket kernel Linux. Employee VPCS không chạy; client kiểm tra ARP trùng IP trước khi dùng IP theo plan `.40.100`, MAC `02:53:4f:43:04:34`. Server là VM Data-Center thật `.30.10:8000` (đã boot node có sẵn). RAM Core/Primary/Secondary/DC lần lượt1024/2048/2048/1024 MiB.

Rule Primary hiện có cho phép `.40.100 → .30.10:8000`; Secondary không có rule tạo flow mới tương ứng. Không thêm allow-any hoặc sửa rule. Default route DC vẫn `.30.2`; chỉ thêm route runtime `.40.100/32 via .30.1` sau backup để flow thử quay về qua CARP. Ảnh xác nhận IP/default route giữ nguyên và backup route0600. Không sửa netplan; không cleanup route hoặc node sau thử. Sau gián đoạn, guest đều OFF và route chưa được xác minh lại.

## 3.4.3. Bảng kết quả và cách diễn giải

| Hạng mục | Kết quả | Minh chứng |
|---|---|---|
| BEFORE: Primary MASTER, Secondary BACKUP năm VLAN, syncok1/demotion0 | PASS | before-acceptance.json; hai before.json |
| State ESTABLISHED trên Primary | PASS | primary-state-before.json; ảnh state-readable-before |
| Đồng bộ hai state ID/creator ID sang Secondary BACKUP | PASS | state-sync-acceptance.json; secondary-state-before.json, counter0:0 |
| Primary tắt; Secondary quảng bá đủ năm VHID và VIP trả lời ARP | Đã quan sát qua gói và host | failover-off-host.json; failover-confirmed-carp/arp.json |
| Native state cũ còn tồn tại trên Secondary sau tiếp quản | CHƯA THU ĐỦ | mới có header checksum và một phần transport; không có JSON đã giải mã |
| Cùng session tiếp tục gửi/ACK sau khi Primary tắt | Đã quan sát11 marker ACK | interrupted-analysis.json; client-events-valid-records.json; wire-valid-records.json |
| HTTP request hoàn tất | CHƯA ĐẠT NGHIỆM THU | không có HTTP200 và không có client-result.json |
| Recovery Primary MASTER / Secondary BACKUP / pfsync READY | NOT_RUN | host-resume-check.json: không QEMU; resume-process-check.json |
| Tổng M3.4 | FAIL/BLOCKED | M3.4-result.json |

Hai state ID là `bf10eb6a00000000`, `c010eb6a00000000`; cùng creator ID `c70da713`. Primary có counter và origif tương ứng ingress VLAN40/egress VLAN30; Secondary BACKUP có counter0:0. Không coi hai entry là hai TCP session: chúng thuộc cùng4-tuple. Log client ghi một SYN và giữ nguyên client/server initial sequence numbers; không tự reconnect. Wire capture cho thấy trước chuyển vai, gói đi qua trunk Primary với MAC `50:00:00:01:00:00`; sau khi Primary OFF, gói hai chiều xuất hiện trên trunk Secondary với MAC `50:00:00:02:00:00`, VLAN40↔30 và TTL qua router. Bằng chứng này hỗ trợ kết luận dữ liệu đã tiếp tục trong khoảng quan sát, không thay thế native state sau failover đang thiếu.

Có một TCP retransmission được ghi nhận quanh chuyển vai; đây không phải phép đo toàn bộ mất gói. Không tuyên bố zero packet loss, gián đoạn bằng0 hoặc hoàn tất HTTP. Nguyên nhân kết thúc phép thử là môi trường bị gián đoạn/restart theo host uptime/process mất; chưa xác định tác nhân, không quy kết CARP làm đứt kết nối.

## 3.4.4. Minh họa thực tế

![Hình 3.1. Data-Center trước test.](dc-before-public-20261104T111451+0700.png)

Hình 3.1. Data-Center trước test.

Mục đích, nội dung, kết quả và ý nghĩa: Xác nhận IP .30.10, HTTP8000 active và default route .30.2; chọn đúng endpoint đã có.

![Hình 3.2. Backup route và chiều về qua CARP.](dc-backup-proof-20261104T112342+0700.png)

Hình 3.2. Backup route và chiều về qua CARP.

Mục đích, nội dung, kết quả và ý nghĩa: Ảnh đọc tệp route gốc mode0600 và route get .40.100 qua .30.1; minh chứng backup trước đổi runtime.

![Hình 3.3. State trên Primary.](primary-state-readable-before-20261104T112039+0700.png)

Hình 3.3. State trên Primary.

Mục đích, nội dung, kết quả và ý nghĩa: Hai entry ESTABLISHED cùng4-tuple; đọc ID/creator, counter, origif để thiết lập baseline.

![Hình 3.4. State đồng bộ trên Secondary BACKUP.](secondary-state-readable-before-20261104T112039+0700.png)

Hình 3.4. State đồng bộ trên Secondary BACKUP.

Mục đích, nội dung, kết quả và ý nghĩa: Đọc cùng ID/creator và window; counter0:0 hỗ trợ việc state được đồng bộ trước khi mang traffic.

![Hình 3.5. Controlled failover bằng tắt mềm Primary.](primary-soft-shutdown-20261104T112122+0700.png)

Hình 3.5. Controlled failover bằng tắt mềm Primary.

Mục đích, nội dung, kết quả và ý nghĩa: Lệnh shutdown -p now trên đúng console; kết hợp host xác nhận Primary OFF.

## 3.4.5. Tính toàn vẹn và checkpoint

Đã sao chép byte gốc log/PCAP còn trên EVE vào `interrupted-artifacts/`, đối chiếu SHA-256 trong interrupted-artifact-manifest.json; không sửa bản gốc. Client JSONL có263 byte NUL cuối, wire JSONL có714 byte NUL cuối. Các bản derived chỉ phân tích143 client records và133 wire records nguyên vẹn; vị trí/độ dài/hash phần hỏng được ghi rõ. Không nội suy hoặc tái tạo dữ liệu mất. PCAP có thể kết thúc giữa record do gián đoạn; chỉ các frame đầy đủ mới được dùng khi phân tích sau này. Không có kết quả đóng bình thường client-result.json hoặc wire-result.json.

Bản native after-failover nằm dự kiến tại `/var/tmp/soc-m3-todo-secondary-state-after-failover.b64` trong Secondary. Header đã nhận khai báo1748 byte encoded, SHA-256 `1d85e1fba1077f1d1da92d2723605423f7c8213f4355b3c39dde4998e5285448`; chưa nhận đủ payload. Có thể lấy lại để lưu trữ nếu file còn và hash khớp, nhưng không trình bày nó như runtime mới. Không boot node chỉ để lấy ảnh hoặc ghi log trong lượt kết thúc này.

Checkpoint: M3.1–M3.3 giữ PASS lịch sử; M3.4 chưa DONE. Hiện không QEMU chạy, client cũ đã mất. Cần khôi phục baseline rồi thực hiện lại duy nhất M3.4 bằng session mới; không thể tiếp tục sequence cũ hoặc dùng snapshot live.json làm kết nối hiện tại. Không chạy lại payload native apply đã nghiệm thu để ép kết quả, không NAT/DHCP, không M4/M5 hoặc cleanup.

## 3.4.6. Danh mục minh chứng

| Tệp | Nội dung | Thời điểm thu (múi giờ) | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
| before-acceptance.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:14:31.347431+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/before-acceptance.json | M3.4 — pha tương ứng/phụ lục truy vết |
| client-after-primary-off-live.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:13:49.123671+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/client-after-primary-off-live.json | M3.4 — pha tương ứng/phụ lục truy vết |
| client-during-shutdown.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:22:03.575301+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/client-during-shutdown.json | M3.4 — pha tương ứng/phụ lục truy vết |
| client-established-before-failover.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:19:33.097595+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/client-established-before-failover.json | M3.4 — pha tương ứng/phụ lục truy vết |
| client-events-valid-records.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:16:58.429041+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/client-events-valid-records.json | M3.4 — pha tương ứng/phụ lục truy vết |
| client-failover-start.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:21:21.922561+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/client-failover-start.json | M3.4 — pha tương ứng/phụ lục truy vết |
| client-handshake.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:17:15.656168+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/client-handshake.json | M3.4 — pha tương ứng/phụ lục truy vết |
| client-primary-off.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:22:25.931776+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/client-primary-off.json | M3.4 — pha tương ứng/phụ lục truy vết |
| client-start.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:16:59.699109+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/client-start.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-backup-proof-20261104T112342+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:23:53.414714+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-backup-proof-20261104T112342+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-backup-proof-20261104T112342+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:23:53.415733+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-backup-proof-20261104T112342+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-before-public-20261104T111451+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:15:01.166037+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-before-public-20261104T111451+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-before-public-20261104T111451+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:15:01.167131+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-before-public-20261104T111451+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-boot-1-20261104T111142+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:11:44.572262+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-boot-1-20261104T111142+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-boot-1-20261104T111142+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:11:44.572764+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-boot-1-20261104T111142+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-boot-2-20261104T111413+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:14:17.166874+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-boot-2-20261104T111413+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-boot-2-20261104T111413+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:14:17.167632+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-boot-2-20261104T111413+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-capslock-correction-20261104T111857+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:19:01.076112+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-capslock-correction-20261104T111857+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-capslock-correction-20261104T111857+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:19:01.077285+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-capslock-correction-20261104T111857+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-route-confirmed-20261104T111922+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:19:31.717591+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-route-confirmed-20261104T111922+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-route-confirmed-20261104T111922+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:19:31.719700+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-route-confirmed-20261104T111922+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-route-readback-20261104T111716+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:17:25.771699+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-route-readback-20261104T111716+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-route-readback-20261104T111716+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:17:25.772877+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-route-readback-20261104T111716+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-test-route-20261104T111533+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:15:50.900698+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-test-route-20261104T111533+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| dc-test-route-20261104T111533+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:15:50.901706+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/dc-test-route-20261104T111533+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| endpoint-processes-before.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:11:41.568684+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/endpoint-processes-before.json | M3.4 — pha tương ứng/phụ lục truy vết |
| failover-confirmed-arp.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:22:58.611443+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/failover-confirmed-arp.json | M3.4 — pha tương ứng/phụ lục truy vết |
| failover-confirmed-carp.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:22:57.629183+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/failover-confirmed-carp.json | M3.4 — pha tương ứng/phụ lục truy vết |
| failover-off-host.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:22:02.148550+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/failover-off-host.json | M3.4 — pha tương ứng/phụ lục truy vết |
| host-before.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:11:01.730814+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/host-before.json | M3.4 — pha tương ứng/phụ lục truy vết |
| host-resume-check.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:15:14.614352+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/host-resume-check.json | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-analysis.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:16:58.502631+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-analysis.json | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifact-manifest.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:16:58.386292+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifact-manifest.json | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifacts/client-events.jsonl | Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới | 2026-11-04T16:16:58.383506+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifacts/client-events.jsonl | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifacts/client.pcap | Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới | 2026-11-04T16:16:58.384065+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifacts/client.pcap | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifacts/daemon.log | Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới | 2026-11-04T16:16:58.384065+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifacts/daemon.log | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifacts/live.json | Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới | 2026-11-04T16:16:58.382497+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifacts/live.json | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifacts/vunl0_3_5-flow.pcap | Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới | 2026-11-04T16:16:58.385064+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifacts/vunl0_3_5-flow.pcap | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifacts/vunl0_3_6-flow.pcap | Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới | 2026-11-04T16:16:58.385064+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifacts/vunl0_3_6-flow.pcap | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifacts/wire-daemon.log | Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới | 2026-11-04T16:16:58.385064+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifacts/wire-daemon.log | M3.4 — pha tương ứng/phụ lục truy vết |
| interrupted-artifacts/wire.jsonl | Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới | 2026-11-04T16:16:58.385064+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/interrupted-artifacts/wire.jsonl | M3.4 — pha tương ứng/phụ lục truy vết |
| M3.4-result.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:20:04.824645+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/M3.4-result.json | M3.4 — pha tương ứng/phụ lục truy vết |
| m34-primary-shell-20261104T111102+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:11:05.509146+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/m34-primary-shell-20261104T111102+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| m34-primary-shell-20261104T111102+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:11:05.513972+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/m34-primary-shell-20261104T111102+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| m34-secondary-shell-20261104T111102+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:11:05.509646+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/m34-secondary-shell-20261104T111102+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| m34-secondary-shell-20261104T111102+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:11:05.513972+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/m34-secondary-shell-20261104T111102+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| pfsync-during-state-creation.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:17:26.238466+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/pfsync-during-state-creation.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before-execute-20261104T111119+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:12:45.092202+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before-execute-20261104T111119+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before-execute-20261104T111119+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:12:45.093710+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before-execute-20261104T111119+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before-header-20261104T111245+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:13:11.993472+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before-header-20261104T111245+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before-header-20261104T111245+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:13:11.994997+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before-header-20261104T111245+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before-page-0-20261104T111312+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:13:34.897861+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before-page-0-20261104T111312+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before-page-0-20261104T111312+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:13:34.899959+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before-page-0-20261104T111312+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before-page-1440-20261104T111335+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:14:00.488744+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before-page-1440-20261104T111335+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before-page-1440-20261104T111335+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:14:00.492638+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before-page-1440-20261104T111335+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-before.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:14:00.555878+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-before.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-soft-shutdown-20261104T112122+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:21:29.736152+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-soft-shutdown-20261104T112122+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-soft-shutdown-20261104T112122+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:21:29.738857+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-soft-shutdown-20261104T112122+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before-execute-20261104T111750+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:18:52.470167+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before-execute-20261104T111750+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before-execute-20261104T111750+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:18:52.471171+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before-execute-20261104T111750+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before-header-20261104T111852+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:19:17.503495+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before-header-20261104T111852+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before-header-20261104T111852+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:19:17.505650+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before-header-20261104T111852+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before-page-0-20261104T111917+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:19:40.848275+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before-page-0-20261104T111917+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before-page-0-20261104T111917+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:19:40.849276+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before-page-0-20261104T111917+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before-page-1440-20261104T111941+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:20:04.196489+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before-page-1440-20261104T111941+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before-page-1440-20261104T111941+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:20:04.198689+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before-page-1440-20261104T111941+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-before.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:20:04.269337+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-before.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-readable-before-20261104T112039+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:20:50.163616+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-readable-before-20261104T112039+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| primary-state-readable-before-20261104T112039+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:20:50.165631+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/primary-state-readable-before-20261104T112039+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| PROGRESS.before-final.md | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:07:14.364327+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/PROGRESS.before-final.md | M3.4 — pha tương ứng/phụ lục truy vết |
| PROGRESS.md.before | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:07:14.364327+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/PROGRESS.md.before | M3.4 — pha tương ứng/phụ lục truy vết |
| resume-process-check.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:15:15.211521+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/resume-process-check.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-before-execute-20261104T111119+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:12:44.887502+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-before-execute-20261104T111119+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-before-execute-20261104T111119+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:12:44.888002+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-before-execute-20261104T111119+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-before-header-20261104T111245+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:13:12.225704+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-before-header-20261104T111245+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-before-header-20261104T111245+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:13:12.227693+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-before-header-20261104T111245+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-before-page-0-20261104T111312+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:13:35.261667+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-before-page-0-20261104T111312+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-before-page-0-20261104T111312+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:13:35.263184+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-before-page-0-20261104T111312+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-before.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:13:35.414363+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-before.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-after-failover-execute-20261104T112226+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:23:35.718128+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-after-failover-execute-20261104T112226+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-after-failover-execute-20261104T112226+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:23:35.720138+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-after-failover-execute-20261104T112226+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-after-failover-header-20261104T112335+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:24:01.071031+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-after-failover-header-20261104T112335+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-after-failover-header-20261104T112335+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:24:01.072621+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-after-failover-header-20261104T112335+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before-execute-20261104T111750+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:18:53.050651+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before-execute-20261104T111750+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before-execute-20261104T111750+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:18:53.052607+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before-execute-20261104T111750+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before-header-20261104T111853+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:19:19.187432+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before-header-20261104T111853+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before-header-20261104T111853+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:19:19.190101+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before-header-20261104T111853+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before-page-0-20261104T111919+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:19:42.695332+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before-page-0-20261104T111919+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before-page-0-20261104T111919+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:19:42.696410+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before-page-0-20261104T111919+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before-page-1440-20261104T111943+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:20:06.078408+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before-page-1440-20261104T111943+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before-page-1440-20261104T111943+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:20:06.079420+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before-page-1440-20261104T111943+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-before.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:20:06.154782+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-before.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-readable-before-20261104T112039+0700.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:20:50.641818+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-readable-before-20261104T112039+0700.json | M3.4 — pha tương ứng/phụ lục truy vết |
| secondary-state-readable-before-20261104T112039+0700.png | Ảnh console thực tế, nguyên nội dung | 2026-11-04T11:20:50.642329+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/secondary-state-readable-before-20261104T112039+0700.png | M3.4 — pha tương ứng/phụ lục truy vết |
| shutdown-action.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:21:22.655712+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/shutdown-action.json | M3.4 — pha tương ứng/phụ lục truy vết |
| SOC_TO_DO.before-final.md | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:14:31.347925+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/SOC_TO_DO.before-final.md | M3.4 — pha tương ứng/phụ lục truy vết |
| SOC_TO_DO.md.before | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:07:14.362248+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/SOC_TO_DO.md.before | M3.4 — pha tương ứng/phụ lục truy vết |
| staged-result-checkpoint.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:17:57.524246+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/staged-result-checkpoint.json | M3.4 — pha tương ứng/phụ lục truy vết |
| start-Data-Center.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:11:18.277086+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/start-Data-Center.json | M3.4 — pha tương ứng/phụ lục truy vết |
| state-sync-acceptance.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:20:39.170428+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/state-sync-acceptance.json | M3.4 — pha tương ứng/phụ lục truy vết |
| wire-live-summary.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:23:15.219139+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/wire-live-summary.json | M3.4 — pha tương ứng/phụ lục truy vết |
| wire-start.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T11:18:45.234642+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/wire-start.json | M3.4 — pha tương ứng/phụ lục truy vết |
| wire-valid-records.json | Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp | 2026-11-04T16:16:58.455812+07:00 | docs/evidence/M3/M3.4-pfsync-state-20261104/wire-valid-records.json | M3.4 — pha tương ứng/phụ lục truy vết |
