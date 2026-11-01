# Minh chứng M2 thực tế ngày 01/11/2026

## 1. Kết quả và phạm vi

95/95 ca frame thật PASS,0 FAIL: vlan-trunk31, mirror-traffic32, postboot-traffic32. final-collection chứa bộ cuối gồm24 PCAP theo tám TAP,178 frame thu từ guest và CSV95 dòng. pre-reboot-collection là bản thu sớm của63 ca đầu, không phải63 ca bổ sung. Một PCAP cuối không có gói trên cổng ens10 trước khi cấu hình mirror là kết quả quan sát trong cửa sổ đo.

Phát128byte/frame có marker riêng, Ethernet0x88b5; không phải ping, IPS/IDS hoặc stress test. Nhận124/128/132byte do bỏ/giữ/thêm tag. Mỗi suite mirror có26 bản sao: VLAN30=6,VLAN40/50/60/99=5 mỗi VLAN. Mirror counter26 gói/3328byte và PCAP3372byte khác điểm đếm44byte tương ứng11 thẻ4byte; không suy packet drop từ chênh byte này.

## 2. Dấu mốc lệnh thực tế

- Bộ điều phối: `py -3.12 -X utf8 automation/m2_run_queue.py --execute --resources-ready --run-dir staging/m2-live-20261101a`; lần đầu bị SSH agent, chưa start. Sau phục hồi/RAM đạt ngưỡng, chỉ start node3 qua EVE wrapper.
- Sau user tự đăng nhập/sudo: `sudo -n -i` trên chính console dùng chung timestamp. Không mật khẩu trong lệnh/log, không sửa sudoers.
- Baseline đầu bị chặn vì br-core-l2 admin DOWN; không chạy frame lúc đó. Hai lần helper runtime bị guard chặn/rollback, giữ recover-6 và recover-10 trong guest-public-replies. Helper lịch sử không dùng lại.
- Lệnh backup trực tiếp và chuẩn hóa runtime nằm nguyên trong metadata ảnh runtime-backup/runtime-restored-up. Backup `/root/m2-runtime-final-20261101/ovsdb.before` đã compact sang bản kiểm tra; chỉ chuẩn hóa IPv6/cờ UP của bridge nội bộ, không đổi VLAN/forwarding.
- Tiếp tục `m2_run_queue.py --execute --resources-ready --console-shell-ready ...`: baseline/backup/31frame/mirror/32frame/persist. Snapshot chính `/root/m2-traffic-m2-live-20261101a/ovsdb.before`, schema8.5.1, hash trong queue-receipt/backup reply. Không dùng snapshot OVS rỗng trước đây để rollback hiện tại.
- Sau ảnh preboot-idle xác nhận không có apt/dpkg job: thêm `--reboot-ready`. Guest reboot mềm qua `sudo -n systemd-run --unit=soc-m2-controlled-reboot --on-active=5s /usr/bin/systemctl reboot`. Không reboot EVE/Windows hoặc Reset node.
- Boot ID3060cddc-e143-4e13-b739-76f4f2b96deb đổi thành6b7326c8-146a-45f7-b373-1a014d0021e2. User tự đăng nhập/sudo lại; unit enabled/active và không IP/forwarding0 được chụp thật.
- Bundle/tmp mất sau reboot, lần truyền lớn tiếp theo lỗi giải nén và shell chờ chuỗi. Hash guard ngăn job thực thi. Dừng đúng python/client SSH của phiên và Ctrl+C dòng nhập dở; không can thiệp VM. `stopped-own-console-controller.json` và ảnh console-line-cancel ghi sự kiện.
- Adapter được đổi sang /var/tmp, literal JSON và hash từng phần/toàn bộ. Bản xuất chỉ đọc nhỏ `m2_postboot_readonly_export.py` dùng thư viện cũ có SHA263c27f2b85f742fd15e8f9eef0c44831e52ae1bbf4a18234e7b7387985c9123. Dữ liệu trả qua glyph/SHA hợp lệ, bộ guard hiện hành kiểm đầy đủ VLAN/Mirror/MAC/noIP và bootID.
- `m2_resume_verified_postboot.py --run-dir staging/m2-live-20261101a --verified-reply staging/m2-live-20261101a/postboot-readonly-console/export-5-verified-reply.json --resources-ready` dùng Queue/frame_test của cùng bộ điều phối để chạy32 ca thật cuối. Không đánh PASS từ hình hoặc từ mô hình.

## 3. Log, backup và thời gian

final-collection có JSON/CSV, queue/events và các public reply đã kiểm SHA qua console. Log lệnh chi tiết đầy đủ trong guest: `/root/m2-traffic-m2-live-20261101a/commands.jsonl`; bộ xuất sau boot ở `/root/m2-postboot-export-20261101/commands.jsonl`. Chúng chưa được sao chép toàn bộ về Windows. Raw OVSDB chỉ giữ root-only trong guest, không đưa vào Git. Registry persistence-files.json cho unit/helper giữ ở workdir chính; phục hồi phải kiểm schema/hash và trạng thái trước, không ghi vào đĩa VM từ host.

Mốc collector UTC+07:00 là thời gian thu; guest/EVE clock và timestamp PCAP không được coi là đã đồng bộ. Bảng danh mục phân biệt thời gian collector có trong metadata với thời gian Windows nhận/ghi tệp khi không có timestamp độc lập. Không tự thêm giây thu thập không có bằng chứng.

Các ảnh là framebuffer QEMU nguyên byte, một số trước/sau có nội dung giống nhau và hash giống nhau là bình thường, không chỉnh ảnh để tạo khác biệt. Word mới nhúng8 ảnh; ảnh FDB/journal và boot/diagnosis khác giữ ở thư mục này. Chưa có GUI topology hoặc review phân trang Word; có thể mở lab trên EVE Web, chụp canvas một node/không link bằng Win+Shift+S, lưu vào thư mục này và cập nhật danh mục. Không ghi ảnh chưa chụp là đã có.

## 4. Lỗi còn lại và việc tiếp theo

Journal vẫn có cảnh báo biến OVS_CTL_OPTS trống; các daemon/unit active và suite đạt. Không sửa thêm unit OVS chỉ để bỏ cảnh báo sau khi chức năng đã kiểm chứng. Các sự kiện FAILED_OR_BLOCKED cũ của queue khi transport lỗi không phải kết quả unit cuối; đã đối chiếu enabled/active sau boot và cập nhật stage hiện hành, giữ lịch sử events.

M3/M4, routing/NAT/HA/IDS, IPv6 payload và tải cao chưa thử. Chỉ một Core đang chạy, không peer/link/sensor/firewall mới. M3 Primary cần phạm vi được giao, image chính thức đã xác thực, tài nguyên mới đo và mapping/subnet/WAN được chốt; không tự khởi động từ checkpoint này.

Raw PCAP bị .gitignore loại trừ nhưng còn trên Windows và EVE. Danh mục/checksum có thể nhắc tệp chỉ giữ cục bộ; không hiểu manifest là mọi tệp đã upload. Không có mật khẩu, private key hoặc token trong bộ log/báo cáo đã chọn công bố.
