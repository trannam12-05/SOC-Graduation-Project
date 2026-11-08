# BÁO CÁO AUDIT VÀ CHECKPOINT TIẾP QUẢN M3 — 03/11/2026

Phạm vi: audit filesystem/Git/tài liệu/minh chứng có sẵn tại `D:\SOC`; chỉ tạo báo cáo này. Không kết nối lab, không gửi phím console, không chạy automation dự án, không thay đổi EVE-NG/OPNsense, không cleanup, không commit/push. Thời điểm kiểm kê được ghi tại phụ lục, múi giờ UTC+07:00.

Đã đối chiếu AGENTS.md, SOC_TO_DO.md, PROGRESS.md, M1 Word/câu hỏi mở, báo cáo tổng kết và JSON kết quả M2, báo cáo M3 Nhóm1/1B, backup XML riêng (không xuất credential), mã console, Git history/diff, lệnh debug root và ảnh then chốt. Phụ lục bao phủ từng tệp modified/untracked theo metadata; không có nghĩa mọi ảnh hoặc mọi dòng của 1.456 tệp untracked đã được kiểm chứng nội dung.

## 1. A. PROJECT STATUS

| Giai đoạn | Kết luận | Căn cứ và giới hạn |
|---|---|---|
| M1 | PARTIAL | Đã có Word thiết kế Core L2/OPNsense; còn placeholder thông tin đồ án/phê duyệt và câu hỏi WAN, DHCP, chính sách. Chưa thấy nghiệm thu M1 toàn bộ. Các thông số được chốt ở M2/M3 không biến toàn bộ đề xuất M1 thành cấu hình đã triển khai. |
| M2 | DONE trong phạm vi đã nghiệm thu | `docs/M2/M2-final-summary-20261103.md` và `docs/evidence/M2/final-acceptance-20261103/M2-results.json`: 95/95 ca frame lịch sử, 3/3 ca ứng dụng mới; Core L2, VLAN/access/trunk, routing qua Primary, firewall các ca được duyệt và SPAN PASS; LACP N/A. Không tái kiểm lab trong lượt này. |
| M3 | PARTIAL | Hai firewall đã cài, có VLAN/SYNC, XMLRPC đã kiểm alias; Nhóm1B có pfsync READY và tham số VIP APPROVED. Nhóm2 mới có thử apply/verify lỗi; CARP persistent/runtime, MASTER/BACKUP và failover chưa được chứng minh. NAT/DHCP chưa nghiệm thu. |

M2 PASS không bao hàm mọi cặp VLAN/port/IPv6, least-privilege toàn hệ thống, HA, NAT/DHCP hoặc pipeline SOC. README/PROGRESS/SOC_TO_DO đang dẫn đầu bằng checkpoint M2, chưa phản ánh đầy đủ Nhóm1B và chuỗi thử Nhóm2.

### 1.1. Quy ước kết luận

- CONFIGURED: bản đọc cấu hình lưu có tham số; không tự chứng minh chức năng chạy.
- VERIFIED: đã đối chiếu dữ liệu/ảnh đầu ra cho phạm vi và thời điểm cụ thể.
- PASS: phép thử đáp ứng tiêu chí có bằng chứng; không dựa riêng vào file/script.
- FAIL: lệnh/phép thử cụ thể có lỗi, không đồng nghĩa toàn hệ thống hỏng.
- PENDING: chưa chạy hoặc thiếu bằng chứng; UNVERIFIED nhấn mạnh chưa xác minh.
- N/A: không áp dụng theo kiến trúc/phạm vi đã chốt.

## 2. B. M3 CHECKPOINT

Tiền tố minh chứng trong bảng: `docs/evidence/M3/`.

| Hạng mục | Trạng thái | Evidence | Ghi chú |
|---|---|---|---|
| Primary/Secondary | CONFIGURED, VERIFIED lịch sử | `group1-carp-readiness-20261103/primary-audit.json`, `secondary-audit.json`; backup/checksum | Hồ sơ cùng OPNsense26.7 amd64, boot ổ cứng; không xác nhận lại runtime trực tiếp. |
| VLAN interfaces | CONFIGURED, VERIFIED trước Nhóm2; hiện tại PENDING | Hai audit trên; hai audit Nhóm1B | opt1–5/vtnet0_vlan30/40/50/60/99; Primary .2/24, Secondary .3/24. Sau đó có thử create/reload chưa xác minh. |
| SYNC | CONFIGURED, VERIFIED tại Nhóm1B | Ảnh pfsync cuối, `group1b-prerequisites-20261103/pfsync.pcap` và bản giải mã | opt6/vtnet2; 10.255.255.1/30 và .2/30. |
| pfsync | VERIFIED, READY tại18:27–18:30; nghiệm thu giữ phiên PENDING | `group1b-prerequisites-20261103/result.json`, `settled-verification.json`, ảnh cuối/kernel bulk log | Đã xem hai ảnh UP, syncdev/peer đúng, syncok1, demotion0. PCAP lần đầu báo5/8 packet hai chiều; chưa bao phủ retry sau, chưa nghiệm thu reboot/failover/giữ phiên. |
| XMLRPC | CONFIGURED, VERIFIED/PASS riêng alias thử lịch sử | `resume-20261102/xmlrpc-target-probe-check-20261102T163938+0700.png`, `xmlrpc-target-cleanup-verified-20261102T164809+0700.png` | Đã xem ảnh đích có alias thử và sau đó rỗng, protected network true. Không suy VIP/NAT/DHCP đã đồng bộ đầy đủ. |
| CARP planning | VERIFIED hồ sơ APPROVED | `group1b-prerequisites-20261103/CARP-final-parameters.csv/json` | VIP192.168.VLAN.1/24, VHID30/40/50/60/99, advbase1, skew0/100; applied=false. Không mở rộng sang WAN/LAN parent. |
| CARP persistent config | PENDING / UNVERIFIED | Bốn backup trước CARP đều0 vip; thiếu snapshot đầy đủ sau Nhóm2 | Không kết luận config hiện tại chắc chắn bằng0; lệnh apply tìm thấy là ifconfig runtime. |
| CARP apply | FAIL ở lần có ảnh lỗi; toàn bộ PENDING | `group2a-apply-20261103/primary-carp-apply-20261103T193209+0700.png`, Secondary19:32:58 | Primary lỗi redirect, Secondary chỉ dòng lệnh/dấu chờ. Chưa có bằng chứng apply thành công. |
| CARP runtime | PENDING / UNVERIFIED | Hai ảnh verify19:34, runtime-primary21:08 | Không có output hợp lệ thể hiện VIP/VHID/vai trò. |
| MASTER/BACKUP | PENDING | Không tìm được minh chứng vai trò hợp lệ trong chuỗi Nhóm2 | Không dùng pfsync READY hoặc carp.allow/boot event làm chứng cứ bầu chọn. |
| Failover | PENDING | Nhóm1B result.json: failover_run=false; không thấy nghiệm thu sau | Chưa có ca chuyển vai/đo gián đoạn/giữ phiên. |
| NAT M3 | CONFIGURED chế độ automatic trong backup; chức năng PENDING | Hai backup trước CARP có nat/outbound/mode=automatic | Chưa có bằng chứng egress/WAN HA. |
| DHCP M3 | PENDING | Hồ sơ M1 còn hỏi scope/DNS; không có nghiệm thu lease ở Nhóm1B/2 | WAN DHCP client không đồng nghĩa DHCP server VLAN hoạt động. |
| Firewall M3 | CONFIGURED; VERIFIED phạm vi SYNC/XMLRPC lịch sử; CARP policy PENDING | HA SYNC/pfsync/alias và M2 final | Chưa kiểm protocol112 trên L2 phù hợp; không suy M2 thành nghiệm thu rule CARP. |
| LACP Core | N/A | M2 final | Hai trunk tới hai firewall độc lập, không thiết kế LAG chung. |

### 2.1. Điểm dừng thực sự

**Checkpoint chắc chắn cuối: Nhóm1B hoàn tất chuẩn bị; Nhóm2 đã thử apply/verify nhưng chưa đạt CARP CONFIGURED/VERIFIED/PASS.** Ảnh runtime mới nhất được xem là Primary21:08 ngày03/11; thời điểm chính xác từ JSON nằm ở phụ lục.

Ảnh apply/verify cho thấy `Ambiguous output redirect` hoặc chỉ dòng lệnh đã nhập. Ảnh echo20:04 và runtime21:08 cho thấy `ECHO/WHOAMI/HOSTNAME/IFCONFIG/SYSCTL: Command not found`, với chữ HOA khác lệnh chữ thường trong JSON. Đây là bằng chứng đường nhập lệnh/shell không đáng tin ở những lần thử; chưa chứng minh binary hệ điều hành bị mất. Lỗi redirect gợi ý khác biệt cú pháp shell. Nguyên nhân chữ HOA/chế độ bàn phím chưa được kiểm chứng. Nhiều JSON ghi guest_command_sent bắt đầu BOM U+FEFF, cũng cần review. Không sửa transport/shell để tìm câu trả lời trong audit.

Đã tìm thấy lệnh thử `configctl interface reload`, create `vtnet0_vlan30`, vòng lặp create VLAN/gán .2 và runtime ifconfig VIP trong TXT/JSON. Ảnh đã xem chủ yếu lỗi hoặc không có kết quả. **Chưa chứng minh thay VLAN runtime ngoài ý muốn; cũng chưa loại trừ được.** Chưa có đối tượng tạm nào đủ bằng chứng để yêu cầu rollback cụ thể. `/root/m3-vlan30.out` chỉ là path trong lệnh thử, chưa xác nhận tồn tại. Không tự xóa VLAN hoặc restore XML.

### 2.2. Backup và nguy cơ mất cấu hình

Đã đọc XML, đếm vip và kiểm SHA-256 lại cả bốn bản cục bộ, không xuất credential:

| Tệp dưới docs/evidence/M3 | SHA-256 | Kết quả |
|---|---|---|
| `group1-carp-readiness-20261103/private-backups/Primary-config.xml` | `2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2` | VERIFIED, XML hợp lệ,0 vip trước CARP |
| `group1b-prerequisites-20261103/private-backups/Primary-before.xml` | Như Primary trên | VERIFIED; bản trùng có chủ đích phục hồi theo mốc |
| `group1-carp-readiness-20261103/private-backups/Secondary-config.xml` | `fd0482546117a18254e05114dc1b101012b95c1388e4ba9ea4eaafce115c69bd` | VERIFIED, XML hợp lệ,0 vip trước CARP |
| `group1b-prerequisites-20261103/private-backups/Secondary-before.xml` | Như Secondary trên | VERIFIED |

Primary hash còn khớp mốc M2. Chưa thấy bằng chứng mất/ghi đè backup; chưa có snapshot sau Nhóm2 để bảo đảm config/runtime lab hiện tại nguyên vẹn. Rủi ro khác là nhiều kết quả chưa theo dõi Git: HEAD01/11 không chứa đầy đủ công việc02–03/11. Không dùng reset/clean/checkout để dọn.

## 3. C. COPILOT FILE AUDIT

### 3.1. Giới hạn quy kết tác giả

Git không ghi công cụ tạo file chưa commit. Nội dung/mtime khoanh vùng chuỗi thử Nhóm2 khoảng19:19–21:08 ngày03/11; không được quy mọi thay đổi từ01/11 cho Copilot. Mtime có thể đổi khi sao chép, không thay collector_time. Phụ lục phân loại từng tệp modified/untracked; nhiều hàng chỉ kiểm metadata/vai trò và ghi REVIEW.

A=chính thức; B=evidence; C=automation; D=tạm/debug; E=trùng; F=sai vị trí; G=sai/chưa kiểm chứng; H=nhạy cảm. Mọi MOVE/DELETE LATER chỉ là đề xuất.

| File/nhóm | Loại | Keep/Move/Delete-later/Review | Lý do |
|---|---|---|---|
| `docs/M3/M3-group1-CARP-readiness-20261103.md`, `M3-group1b-prerequisites-20261103.md` | A | KEEP | Checkpoint chuẩn bị, giới hạn rõ |
| evidence Nhóm1/1B, backup/hash/index/PCAP | B/H | KEEP | Giá trị phục hồi/kiểm chứng; giữ private và ignore |
| `automation/m3_group1_*.py`, `m3_1b_*.py` | C | KEEP + REVIEW | Backup/transport/secret/pfsync có giá trị; nhiều đường có tác dụng ghi/thay runtime, không tự chạy |
| `automation/m3_inspect_guest_console.py` | C | KEEP | Diff thêm6 phép đọc NIC/API/schema, không implementation CARP |
| evidence `group2a-apply-20261103/` | B/G | KEEP + REVIEW | Trace lỗi có giá trị; thiếu index/kết luận, tên apply không chứng minh thành công |
| 18 cặp PNG/JSON rời trong evidence/M3 | B/F/G | MOVE sau duyệt | Gom chuỗi debug Nhóm2, giữ cặp metadata |
| evidence `runtime-primary/`, `recovery-check/` | B/G | KEEP hoặc gom sau duyệt | Probe chưa có kết quả runtime hợp lệ |
| 31 TXT project root | D/F; một số G/H | MOVE hoặc DELETE LATER | Lệnh thử đơn lẻ, phải giữ trace trước dọn |
| `temp/primary_runtime_probe.ps1`, `recover_primary_probe.ps1` | D/G | REVIEW → DELETE LATER | Wrapper console/output cố định; không tự chạy lại |
| `tmp_config_xml_inspect_primary.txt`, raw XML printers | D/G/H | REVIEW | Có thể in credential từ hasync/virtualip nếu chạy |
| PNG trong docs/M2 | B/F hoặc E | REVIEW → MOVE | Evidence lẫn báo cáo; kiểm hash/ref trước đổi |
| README/PROGRESS/SOC_TO_DO | A/G | KEEP + REVIEW | Chưa đồng bộ checkpoint M3 mới |
| evidence/eve-ng | B/H | KEEP nguyên vị trí | Ràng buộc bảo toàn minh chứng cũ |

### 3.2. Duplicate và độ tin cậy

Hash xác nhận hai ảnh VLAN30-create19:59:13/20:02:55 giống nguyên byte; hostname20:10:34/20:27:34 cũng giống nhau. Các trang vận chuyển “stable” giống lần đầu không phải kiểm thử độc lập, không xóa chỉ vì trùng.

Cần REVIEW thêm các ảnh Secondary02/11 trùng ảnh installer Primary01/11: ví dụ `secondary-20261102/secondary-install-started-20261102T131518+0700.png` và `primary-live-20261101/installer-write-started-20261101T132632+0700.png`. Một số stage reader Primary/Secondary cũng trùng. Màn hình giống có thể cho framebuffer giống; **không đủ kết luận ảnh giả hoặc sai node**, nhưng không dùng ảnh đó đứng riêng chứng minh cài đặt từng firewall. Ưu tiên audit node/config và checksum backup khác nhau.

## 4. D. DIRECTORY CLEANUP PLAN — CHƯA THỰC HIỆN

| Current | Recommended | Reason |
|---|---|---|
| root `tmp_*.txt`, `primary_*probe.txt` | `automation/debug/M3/20261103/` hoặc evidence đợt/debug/commands; sau lưu trace mới DELETE LATER bản dư | Chọn một bản chuẩn, phân biệt đầu vào và kết quả |
| `temp/*probe.ps1` | `automation/debug/M3/20261103/` nếu cần dùng tiếp | Wrapper không nằm lẫn report; review trước chạy |
| evidence/M3 PNG/JSON rời | `docs/evidence/M3/group2-console-debug-20261103/` | Gom theo đợt và thêm index/ref |
| evidence/M3 `runtime-primary/`, `recovery-check/`, `temp-carp-check/` | Thư mục con trong đợt debug trên | Tên có thời gian/liên hệ checkpoint |
| `docs/M2/M2-core-l2-cloud-init-success.png`, `M2-ubuntu-core-l2-boot-success.png` | evidence/M2 đúng đợt sau kiểm hash/ref | Có thể đã có bản chuẩn evidence, tránh nhân bản |
| command/stage payload trong evidence | Giữ nếu là đầu vào thực tế; implementation dùng lại ở automation | Không ép move chỉ vì chứa code, trace vẫn có giá trị |
| private-backups và evidence/eve-ng | Giữ nguyên | Nhạy cảm và bảo toàn lịch sử |

Cấu trúc docs/M1/M2/M3, automation, network, opnsense vẫn dùng được. Vấn đề chính: debug ở root, ảnh M3 rời, thiếu index/ref và checkpoint chung chậm cập nhật; chưa cần tái cấu trúc toàn dự án.

## 5. E. SECURITY CHECK

SAFE chỉ áp dụng kiểm tra đã nêu, không phải chứng nhận mọi byte/ảnh/lịch sử Git. Không in giá trị secret.

| File/path | SAFE / REVIEW / DANGEROUS | Nhận định |
|---|---|---|
| XML trong hai private-backups Nhóm1/1B | DANGEROUS nếu công khai | Backup đầy đủ có credential; hiện ignored, ACL owner-only |
| Nhóm1 private-backups/transport-private.key | DANGEROUS nếu công khai | Có private key, ignored |
| Nhóm1B private-backups/carp-shared-secret.dpapi | REVIEW | Secret mã hóa theo user Windows; ignored, không giải mã trong audit |
| `docs/evidence/eve-ng/ubuntu-image-test-config/node-config.json` | DANGEROUS nếu công khai | accountPassword không phải placeholder; ignore đích danh. Chưa thử credential còn hiệu lực |
| TXT/script in raw XML/hasync/virtualip | REVIEW | Chưa xác nhận plaintext trong file lệnh; nguy cơ xuất credential khi chạy |
| `automation/xmlrpc_config_private.php`, `xmlrpc_prompt_private.py`, `m3_1b_secret.py` | REVIEW | Xử lý credential; tên private không đủ bảo vệ |
| `docs/evidence/M2/M2-core-stage1-seed-redacted-20261031.json` | SAFE ở trường passwd đã kiểm | Có marker REDACTED |
| TXT root đã đọc; ảnh apply/verify/echo/runtime đã xem | SAFE với secret trực tiếp trong phạm vi đã xem | Chỉ thấy path/biến secret, không thấy giá trị thực |
| Ảnh/PCAP/payload khác chưa kiểm thủ công đầy đủ | REVIEW | Không bảo đảm an toàn từ quét text |

.gitignore bảo vệ .env, secrets/credentials/auth, private key/SSH key, private-backups, opnsense/private, config-OPNsense*.xml, console-transfer, staging, image/DB/PCAP. Đã kiểm check-ignore secret DPAPI/private key/node-config. Hai thư mục backup NTFS chỉ cấp Full Control cho ACER xuống tệp con. Ignore không bảo vệ file đã tracked và không thay ACL; XML ở ngoài pattern vẫn có thể add nhầm. TXT root/temp/*.ps1 không bị ignore.

Quét token có false positive “sk-” trong tên “disk-...” và thuật toán OpenSSH security-key của hai log tracked; đã phân loại lại. Không phát hiện bằng chứng secret thật bị commit/push trong tập kiểm; chưa quét mọi blob lịch sử, chưa chứng minh chưa từng lộ nơi khác. Không tự rotate/delete.

## 6. F. GIT STATUS

- HEAD `7ab1652`, 01/11/2026 13:06:05 +07:00; không staged change khi kiểm.
- Modified4: README.md (39 thêm/27 xóa); automation/m3_inspect_guest_console.py (6 thêm); docs/M3/M3-primary-live-status-20261101.md (22 thêm); docs/PROGRESS.md (170 thêm/137 xóa).
- Untracked trước audit1.456: evidence M3=859, M2=286, M5=120, M4=65, M1=4; cùng automation/report/TXT root và file khác. Trải nhiều ngày, không quy tất cả cho Copilot.
- Ignored1.234 file gồm image/cache/staging/private, không phải tất cả secret. Báo cáo này thêm1 untracked.
- Suspicious: raw XML printers, lệnh reload/create/apply, ảnh chỉ đầu vào, ảnh trùng giữa node/thời điểm. Không thấy deleted tracked; không suy trước audit chưa từng xóa untracked.
- git diff --check báo trailing whitespace ở các diff có sẵn (nhiều dòng CRLF); chưa sửa vì ngoài phạm vi. Đây không phải bằng chứng mất cấu hình.

## 7. G. NEXT SAFE ACTION — CHỈ ĐỀ XUẤT

1. Giữ checkpoint/backup. Sau rà secret, đề nghị sao lưu an toàn hoặc Git checkpoint phần công khai theo quyền riêng; không reset/clean.
2. Lượt được duyệt đọc lab: xác minh console bằng một lệnh chữ thường ngắn và output thực. Nếu vẫn đổi chữ/nhập sai thì dừng gửi lệnh, dùng người dùng thao tác console trực tiếp. Chưa sửa transport/bàn phím/shell.
3. Sau khi lệnh đọc tin cậy: đọc hostname/version, hash config, VIP chọn lọc không secret, VLAN runtime, pfsync/demotion và vai trò CARP cả hai. So sánh subtree interfaces/filter/NAT/DHCP/HA với backup; lưu snapshot riêng, public output đã lọc. Không dùng raw XML printer hiện tại. Chỉ đề xuất rollback khi có delta xác nhận.
4. Sau checkpoint và phương án RAM/Core L2 được duyệt mới lập apply persistent CARP, kiểm MASTER/BACKUP, rồi failover/giữ phiên trong phạm vi riêng. Chưa thực hiện ở lượt này.

Minh chứng thủ công cho lượt sau: mở đúng console Primary rồi Secondary, xác nhận node; chạy từng phép đọc được duyệt, chờ output/prompt; chụp toàn màn hình gồm lệnh/kết quả/interface/vai trò, tránh secret. Lưu `docs/evidence/M3/checkpoint-readonly-<timestamp>/`, index có tên/nội dung/thời điểm UTC+07:00/path/vị trí báo cáo. Đây là hướng dẫn, không phải ảnh đã thu. Audit dùng ảnh cũ, không chụp lab mới.

## 8. PHỤ LỤC KIỂM KÊ

### 8.1. Giải thích thuật ngữ và nguồn nội bộ

Phần giải thích SOC, VLAN, 802.1Q, trunk/access, LACP, SPAN/port mirroring, OVS/bridge, QEMU/QCOW2, cloud-init/NoCloud, SSH, OPNsense, CARP/pfsync/HA, NAT/DHCP, IDS/IPS, Suricata và Wazuh nằm trong docs/TOPOLOGY_TERMS.md, M1 và thuyết minh M2/M3. Audit không mặc nhiên khắc phục thiếu sót thuật ngữ của hồ sơ cũ. Tên sản phẩm không tự tạo dạng khai triển.

CARP (Common Address Redundancy Protocol, dự phòng địa chỉ chung) dự kiến chia sẻ VIP gateway và bầu vai trò bằng quảng bá; chưa có bằng chứng bầu chọn ở topology. Pfsync đồng bộ trạng thái PF để hỗ trợ HA (High Availability, sẵn sàng cao); Nhóm1B đã có runtime/gói trao đổi, chưa nghiệm thu giữ phiên. XMLRPC (XML Remote Procedure Call, gọi thủ tục từ xa bằng XML) đồng bộ cấu hình; alias thử đã kiểm, không suy mọi cấu hình đều đồng bộ. NAT (Network Address Translation, chuyển đổi địa chỉ mạng) có automatic trong backup nhưng egress chưa kiểm. DHCP (Dynamic Host Configuration Protocol, cấp cấu hình mạng động) cho VLAN chưa nghiệm thu scope/lease/gateway. Core chỉ chuyển frame theo VLAN; gateway và firewall liên VLAN do OPNsense xử lý.

Căn cứ kết luận là ảnh/log/config nội bộ đã dẫn; không dùng tài liệu ngoài mới để thay thực nghiệm, không truy cập web trong audit. Các trích dẫn chính thức ở báo cáo gốc giữ nguyên, không khẳng định đã tái kiểm nguồn bên ngoài.

**Dừng sau audit. Không cleanup, không tiếp tục CARP, không chuyển M4/M5.**

### 8.2. Danh mục từng tệp modified/untracked

Thời điểm tổng hợp: 2026-11-03T21:50:17+07:00. Mtime là metadata filesystem UTC+07:00, không thay thời điểm thu minh chứng. Bảng phân loại theo vai trò; KEEP không đồng nghĩa nội dung đã VERIFIED.

| File | Loại | Keep/Move/Delete-later/Review | Mtime UTC+07:00 | Lý do |
|---|---|---|---|---|
| `README.md` | G | REVIEW | 2026-11-03T17:29:00+07:00 | Ngoài chuỗi Nhóm2; không quy tác giả từ Git |
| `automation/capture_topology_window.ps1` | C | KEEP + REVIEW | 2026-11-02T12:54:58+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/collect_service_results.py` | C | KEEP + REVIEW | 2026-11-02T17:14:12+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/collect_wazuh_verification.py` | C | KEEP + REVIEW | 2026-11-02T20:38:47+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/configure_vpcs_endpoints.py` | C | KEEP + REVIEW | 2026-11-02T16:49:46+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/core_monitor_capture.py` | C | KEEP + REVIEW | 2026-11-02T17:08:05+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/ha_pfsync_capture.py` | C | KEEP + REVIEW | 2026-11-02T16:21:50+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/ha_sync_rules.php` | C | KEEP + REVIEW | 2026-11-02T15:32:19+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/index_soc_continuation_evidence.py` | C | KEEP + REVIEW | 2026-11-02T20:59:06+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/linux_role_bootstrap.py` | C | KEEP + REVIEW | 2026-11-02T17:09:27+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_acceptance_cleanup.py` | C | KEEP + REVIEW | 2026-11-03T17:22:23+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_acceptance_prepare.py` | C | KEEP + REVIEW | 2026-11-03T17:09:15+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_analyze_packets.py` | C | KEEP + REVIEW | 2026-11-03T17:15:55+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_dc_acceptance_guest.py` | C | KEEP + REVIEW | 2026-11-03T17:11:16+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_finalize_delivery.py` | C | KEEP + REVIEW | 2026-11-03T17:28:58+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_group1b_backup_guest.py` | C | KEEP + REVIEW | 2026-11-02T21:20:52+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_group1b_backup_host.py` | C | KEEP + REVIEW | 2026-11-02T21:22:49+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_group1b_compare.py` | C | KEEP + REVIEW | 2026-11-02T21:23:25+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_group1b_report.py` | C | KEEP + REVIEW | 2026-11-02T21:37:12+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_guest_console_stage.py` | C | KEEP + REVIEW | 2026-11-03T17:11:01+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m2_packet_capture.py` | C | KEEP + REVIEW | 2026-11-03T17:13:24+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_1b_capture.py` | C | KEEP + REVIEW | 2026-11-03T18:12:03+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_1b_finalize.py` | C | KEEP + REVIEW | 2026-11-03T18:30:32+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_1b_guest.py` | C | KEEP + REVIEW | 2026-11-03T18:06:05+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_1b_secret.py` | C | KEEP + REVIEW | 2026-11-03T18:07:39+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_1b_settled_observations.py` | C | KEEP + REVIEW | 2026-11-03T18:30:32+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_1b_transport.py` | C | KEEP + REVIEW | 2026-11-03T18:17:01+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_group1_backup_guest.py` | C | KEEP + REVIEW | 2026-11-03T17:43:24+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_group1_backup_host.py` | C | KEEP + REVIEW | 2026-11-03T17:43:24+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_group1_console.py` | C | KEEP + REVIEW | 2026-11-03T17:43:24+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_group1_finalize.py` | C | KEEP + REVIEW | 2026-11-03T17:58:06+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m3_inspect_guest_console.py` | C | KEEP + REVIEW | 2026-11-01T22:16:00+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/m4_live_mirror_frames.py` | C | KEEP + REVIEW | 2026-11-02T17:00:40+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/prepare_remaining_linux_roles.py` | C | KEEP + REVIEW | 2026-11-02T17:09:27+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/prepare_suricata_offline.py` | C | KEEP + REVIEW | 2026-11-02T13:10:43+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/prepare_topology_linux_seeds.py` | C | KEEP + REVIEW | 2026-11-02T13:20:05+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/prepare_wazuh_manager_offline.py` | C | KEEP + REVIEW | 2026-11-02T16:02:11+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/primary_group2a_audit.py` | C | KEEP + REVIEW | 2026-11-02T22:07:10+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/primary_group2a_collect_public.py` | C | KEEP + REVIEW | 2026-11-02T22:20:01+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/primary_group2a_compare.py` | C | KEEP + REVIEW | 2026-11-02T22:12:07+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/primary_group2a_host.py` | C | KEEP + REVIEW | 2026-11-02T22:15:16+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/secondary_backup_boot_disk.py` | C | KEEP + REVIEW | 2026-11-02T16:08:58+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/secondary_preserve_network.py` | C | KEEP + REVIEW | 2026-11-02T15:39:15+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/secondary_secure_console.py` | C | KEEP + REVIEW | 2026-11-02T13:12:25+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/sensor_bootstrap.py` | C | KEEP + REVIEW | 2026-11-02T13:26:22+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/sensor_export_guest.py` | C | KEEP + REVIEW | 2026-11-02T13:31:01+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/sensor_public_state.py` | C | KEEP + REVIEW | 2026-11-02T17:00:40+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/stage_ha_console.py` | C | KEEP + REVIEW | 2026-11-02T15:32:19+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/stage_secondary_network.py` | C | KEEP + REVIEW | 2026-11-02T15:59:41+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/stage_xmlrpc_prompt.py` | C | KEEP + REVIEW | 2026-11-02T16:29:07+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/start_topology_node.py` | C | KEEP + REVIEW | 2026-11-02T16:50:54+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/topology_console.py` | C | KEEP + REVIEW | 2026-11-02T15:44:07+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/topology_console_job.py` | C | KEEP + REVIEW | 2026-11-02T15:44:07+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/topology_first_build.py` | C | KEEP + REVIEW | 2026-11-02T13:01:04+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/topology_first_inventory.py` | C | KEEP + REVIEW | 2026-11-02T16:33:44+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/topology_first_labels.py` | C | KEEP + REVIEW | 2026-11-02T13:04:36+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/topology_first_prepare.py` | C | KEEP + REVIEW | 2026-11-02T13:20:05+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/topology_remote.py` | C | KEEP + REVIEW | 2026-11-02T13:20:05+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/vpcs_live_tests.py` | C | KEEP + REVIEW | 2026-11-02T16:55:51+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/wazuh_manager_bootstrap.py` | C | KEEP + REVIEW | 2026-11-02T16:32:11+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/wazuh_native_replay_collect.py` | C | KEEP + REVIEW | 2026-11-02T20:48:21+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/wazuh_pipeline_verify.py` | C | KEEP + REVIEW | 2026-11-02T20:58:35+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/xmlrpc_config_private.php` | C | KEEP + REVIEW | 2026-11-02T16:30:48+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `automation/xmlrpc_prompt_private.py` | C | KEEP + REVIEW | 2026-11-02T16:29:07+07:00 | Có giá trị tự động hóa; đọc tác dụng trước chạy |
| `configs/M3/deployment-observed-20261102.json` | G | REVIEW | 2026-11-02T16:33:44+07:00 | Ngoài chuỗi Nhóm2; không quy tác giả từ Git |
| `configs/topology-first-plan.json` | G | REVIEW | 2026-11-02T13:00:00+07:00 | Ngoài chuỗi Nhóm2; không quy tác giả từ Git |
| `docs/AUTONOMOUS_PROGRESS.md` | A | KEEP + REVIEW | 2026-11-03T17:29:00+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-acceptance-group1-20261103.md` | A | KEEP + REVIEW | 2026-11-03T17:04:39+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-final-summary-20261103.docx` | A | KEEP + REVIEW | 2026-11-03T17:29:01+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-final-summary-20261103.md` | A | KEEP + REVIEW | 2026-11-03T17:27:49+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group1-review-20261102-2116.md` | A | KEEP + REVIEW | 2026-11-02T21:17:21+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group1b-checkpoint-20261102-2124.md` | A | KEEP + REVIEW | 2026-11-02T21:46:55+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group1b-runtime-20261102.md` | A | KEEP + REVIEW | 2026-11-02T21:46:55+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group2a-checkpoint-20261102-2156.md` | A | KEEP + REVIEW | 2026-11-02T22:25:52+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group2a-primary-vlans-20261102.md` | A | KEEP + REVIEW | 2026-11-02T22:25:52+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group2b-policy-review-20261103.md` | A | KEEP + REVIEW | 2026-11-03T10:35:19+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group2b1-vlan30-rule-proposal-20261103.csv` | A | KEEP + REVIEW | 2026-11-03T10:39:37+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group2b1-vlan30-rule-proposal-20261103.md` | A | KEEP + REVIEW | 2026-11-03T10:39:37+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group2c-intervlan-policy-20261103.csv` | A | KEEP + REVIEW | 2026-11-03T16:57:07+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M2/M2-group2c-intervlan-policy-20261103.md` | A | KEEP + REVIEW | 2026-11-03T16:56:39+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M3/M3-group1-CARP-readiness-20261103.md` | A | KEEP + REVIEW | 2026-11-03T17:58:40+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M3/M3-group1b-prerequisites-20261103.md` | A | KEEP + REVIEW | 2026-11-03T18:30:33+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M3/M3-primary-live-status-20261101.md` | A | KEEP + REVIEW | 2026-11-01T13:29:31+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M3/M3-report-primary-installed-verified-20261101.docx` | A | KEEP + REVIEW | 2026-11-01T22:18:47+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M3/M3-report-primary-installed-verified-20261101.md` | A | KEEP + REVIEW | 2026-11-01T22:18:47+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M5-live-pipeline-proposal-20261102.md` | A | KEEP + REVIEW | 2026-11-02T20:40:00+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/M5-verification-and-demo-20261102.md` | A | KEEP + REVIEW | 2026-11-02T21:03:48+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/PROGRESS.md` | A | KEEP + REVIEW | 2026-11-03T17:29:00+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/SOC-video-demo-20261102.md` | A | KEEP + REVIEW | 2026-11-02T20:56:03+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/SOC_TO_DO.md` | A | KEEP + REVIEW | 2026-11-03T17:27:49+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/TOPOLOGY_GAP_ANALYSIS.md` | A | KEEP + REVIEW | 2026-11-02T13:02:04+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/TOPOLOGY_TERMS.md` | A | KEEP + REVIEW | 2026-11-02T13:23:49+07:00 | Hồ sơ báo cáo; đối chiếu checkpoint/refs |
| `docs/evidence/M1/topology-source-review-20261102/M1-extracted.txt` | B | KEEP | 2026-11-02T12:53:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M1/topology-source-review-20261102/design-file-inventory.json` | B | KEEP | 2026-11-02T12:53:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M1/topology-source-review-20261102/embedded-media-inventory.json` | B | KEEP | 2026-11-02T13:26:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M1/topology-source-review-20261102/image1.png` | B | KEEP | 2026-11-02T12:53:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/acceptance-group1-20261103/employee-client-capability-review.json` | B | KEEP | 2026-11-03T17:03:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/acceptance-group1-20261103/evidence-index.csv` | B | KEEP | 2026-11-03T17:04:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/acceptance-group1-20261103/inventory-before.json` | B | KEEP | 2026-11-03T17:02:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/acceptance-group1-20261103/primary-preflight-observe-20261103T170340+0700.json` | B | KEEP | 2026-11-03T17:03:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/acceptance-group1-20261103/primary-preflight-observe-20261103T170340+0700.png` | B | KEEP | 2026-11-03T17:03:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/acceptance-group1-20261103/result.json` | B | KEEP | 2026-11-03T17:04:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/M2-results.csv` | B | KEEP | 2026-11-03T17:29:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/M2-results.json` | B | KEEP | 2026-11-03T17:29:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/cleanup-receipt.json` | B | KEEP | 2026-11-03T17:22:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/command-0001.txt` | B | KEEP | 2026-11-03T17:13:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/command-0002.txt` | B | KEEP | 2026-11-03T17:14:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/command-0003.txt` | B | KEEP | 2026-11-03T17:14:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/command-0004.txt` | B | KEEP | 2026-11-03T17:15:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/command-0005.txt` | B | KEEP | 2026-11-03T17:16:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/command-0006.txt` | B | KEEP | 2026-11-03T17:16:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/command-0007.txt` | B | KEEP | 2026-11-03T17:17:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/command-0008.txt` | B | KEEP | 2026-11-03T17:17:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job1-20261103T171327+0700.json` | B | KEEP | 2026-11-03T17:14:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job1-20261103T171327+0700.png` | B | KEEP | 2026-11-03T17:14:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job2-20261103T171406+0700.json` | B | KEEP | 2026-11-03T17:14:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job2-20261103T171406+0700.png` | B | KEEP | 2026-11-03T17:14:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job3-20261103T171445+0700.json` | B | KEEP | 2026-11-03T17:15:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job3-20261103T171445+0700.png` | B | KEEP | 2026-11-03T17:15:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job4-20261103T171525+0700.json` | B | KEEP | 2026-11-03T17:16:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job4-20261103T171525+0700.png` | B | KEEP | 2026-11-03T17:16:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job5-20261103T171605+0700.json` | B | KEEP | 2026-11-03T17:16:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job5-20261103T171605+0700.png` | B | KEEP | 2026-11-03T17:16:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job6-20261103T171644+0700.json` | B | KEEP | 2026-11-03T17:17:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job6-20261103T171644+0700.png` | B | KEEP | 2026-11-03T17:17:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job7-20261103T171723+0700.json` | B | KEEP | 2026-11-03T17:17:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job7-20261103T171723+0700.png` | B | KEEP | 2026-11-03T17:17:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job8-20261103T171739+0700.json` | B | KEEP | 2026-11-03T17:17:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/console-soc-m2-final-reader/job8-20261103T171739+0700.png` | B | KEEP | 2026-11-03T17:17:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-boot-initial-20261103T170928+0700.json` | B | KEEP | 2026-11-03T17:09:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-boot-initial-20261103T170928+0700.png` | B | KEEP | 2026-11-03T17:09:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-mirror-after-tests-20261103T171916+0700.json` | B | KEEP | 2026-11-03T17:19:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-mirror-after-tests-20261103T171916+0700.png` | B | KEEP | 2026-11-03T17:19:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-mirror-command.txt` | B | KEEP | 2026-11-03T17:17:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-mirror-runtime-20261103T171747+0700.json` | B | KEEP | 2026-11-03T17:17:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-mirror-runtime-20261103T171747+0700.png` | B | KEEP | 2026-11-03T17:17:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-ready-check-20261103T171117+0700.json` | B | KEEP | 2026-11-03T17:11:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-ready-check-20261103T171117+0700.png` | B | KEEP | 2026-11-03T17:11:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-root-confirm-20261103T171616+0700.json` | B | KEEP | 2026-11-03T17:16:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-root-confirm-20261103T171616+0700.png` | B | KEEP | 2026-11-03T17:16:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-runtime-command.txt` | B | KEEP | 2026-11-03T17:14:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-runtime-ports-l2-20261103T171400+0700.json` | B | KEEP | 2026-11-03T17:14:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-runtime-ports-l2-20261103T171400+0700.png` | B | KEEP | 2026-11-03T17:14:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-runtime-root-20261103T171628+0700.json` | B | KEEP | 2026-11-03T17:17:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-runtime-root-20261103T171628+0700.png` | B | KEEP | 2026-11-03T17:17:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-shell-confirm-20261103T171243+0700.json` | B | KEEP | 2026-11-03T17:12:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/core-shell-confirm-20261103T171243+0700.png` | B | KEEP | 2026-11-03T17:12:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-addresses-command.txt` | B | KEEP | 2026-11-03T17:21:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-boot-initial-20261103T170928+0700.json` | B | KEEP | 2026-11-03T17:09:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-boot-initial-20261103T170928+0700.png` | B | KEEP | 2026-11-03T17:09:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-graceful-poweroff-request-20261103T172156+0700.json` | B | KEEP | 2026-11-03T17:22:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-graceful-poweroff-request-20261103T172156+0700.png` | B | KEEP | 2026-11-03T17:22:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-http-results-summary-20261103T171916+0700.json` | B | KEEP | 2026-11-03T17:19:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-http-results-summary-20261103T171916+0700.png` | B | KEEP | 2026-11-03T17:19:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-ip-service-before-20261103T171200+0700.json` | B | KEEP | 2026-11-03T17:12:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-ip-service-before-20261103T171200+0700.png` | B | KEEP | 2026-11-03T17:12:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-poweroff-command.txt` | B | KEEP | 2026-11-03T17:21:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-precheck-command.txt` | B | KEEP | 2026-11-03T17:12:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-ready-check-20261103T171117+0700.json` | B | KEEP | 2026-11-03T17:11:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-ready-check-20261103T171117+0700.png` | B | KEEP | 2026-11-03T17:11:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-summary-command.txt` | B | KEEP | 2026-11-03T17:19:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-tests-screen-20261103T171831+0700.json` | B | KEEP | 2026-11-03T17:18:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/dc-tests-screen-20261103T171831+0700.png` | B | KEEP | 2026-11-03T17:18:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/delivery-checks.json` | B | KEEP | 2026-11-03T17:29:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/endpoint-ip-mask-gateway-20261103T172108+0700.json` | B | KEEP | 2026-11-03T17:21:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/endpoint-ip-mask-gateway-20261103T172108+0700.png` | B | KEEP | 2026-11-03T17:21:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/evidence-index.csv` | B | KEEP | 2026-11-03T17:29:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/firewall-counter-observations.json` | B | KEEP | 2026-11-03T17:29:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/http-response-body.html` | B | KEEP | 2026-11-03T17:29:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/http-response-headers.txt` | B | KEEP | 2026-11-03T17:29:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/lab-client-topology.unl` | B | KEEP | 2026-11-03T17:09:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/packet-analysis.json` | B | KEEP | 2026-11-03T17:18:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/packet-collect-result.json` | B | KEEP | 2026-11-03T17:18:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/packet-start.json` | B | KEEP | 2026-11-03T17:13:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/packet-stop.json` | B | KEEP | 2026-11-03T17:18:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/packets-decoded.csv` | B | KEEP | 2026-11-03T17:18:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/prepare-error.json` | B | KEEP | 2026-11-03T17:08:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/prepare-receipt.json` | B | KEEP | 2026-11-03T17:09:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/primary-counters-command.txt` | B | KEEP | 2026-11-03T17:17:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/primary-rule-after-tests-20261103T171843+0700.json` | B | KEEP | 2026-11-03T17:18:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/primary-rule-after-tests-20261103T171843+0700.png` | B | KEEP | 2026-11-03T17:18:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/primary-rule-before-tests-20261103T171719+0700.json` | B | KEEP | 2026-11-03T17:17:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/primary-rule-before-tests-20261103T171719+0700.png` | B | KEEP | 2026-11-03T17:17:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/final-acceptance-20261103/source-manifest.json` | B | KEEP | 2026-11-03T17:29:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1-audit-20261102T211609+0700/evidence-index.csv` | B | KEEP | 2026-11-02T21:17:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1-audit-20261102T211609+0700/inventory.json` | B | KEEP | 2026-11-02T21:16:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1-audit-20261102T211609+0700/lab-observed.unl` | B | KEEP | 2026-11-02T21:16:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/authenticated-console-20261102T213357+0700.json` | B | KEEP | 2026-11-02T21:34:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/authenticated-console-20261102T213357+0700.png` | B | KEEP | 2026-11-02T21:34:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/backup-manifest.json` | B | KEEP | 2026-11-02T21:44:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/backup-proof-20261102T214603+0700.json` | B | KEEP | 2026-11-02T21:46:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/backup-proof-20261102T214603+0700.png` | B | KEEP | 2026-11-02T21:46:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/backup-proof.txt` | B | KEEP | 2026-11-02T21:40:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/comparison.json` | B | KEEP | 2026-11-02T21:45:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/core-boot-observe-20261102T212053+0700.json` | B | KEEP | 2026-11-02T21:20:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/core-boot-observe-20261102T212053+0700.png` | B | KEEP | 2026-11-02T21:20:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/core-boot-ready-20261102T212119+0700.json` | B | KEEP | 2026-11-02T21:21:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/core-boot-ready-20261102T212119+0700.png` | B | KEEP | 2026-11-02T21:21:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/core-console-ready-20261102T212206+0700.json` | B | KEEP | 2026-11-02T21:22:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/core-console-ready-20261102T212206+0700.png` | B | KEEP | 2026-11-02T21:22:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/evidence-index-final.csv` | B | KEEP | 2026-11-02T21:46:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/evidence-index.csv` | B | KEEP | 2026-11-02T21:25:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/login-state-20261102T212422+0700.json` | B | KEEP | 2026-11-02T21:24:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/login-state-20261102T212422+0700.png` | B | KEEP | 2026-11-02T21:24:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/runtime-mirror-20261102T214552+0700.json` | B | KEEP | 2026-11-02T21:46:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/runtime-mirror-20261102T214552+0700.png` | B | KEEP | 2026-11-02T21:46:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/runtime-mirror.txt` | B | KEEP | 2026-11-02T21:40:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/runtime-ports-20261102T214541+0700.json` | B | KEEP | 2026-11-02T21:45:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/runtime-ports-20261102T214541+0700.png` | B | KEEP | 2026-11-02T21:45:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/runtime-ports.txt` | B | KEEP | 2026-11-02T21:40:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/runtime.json` | B | KEEP | 2026-11-02T21:44:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group1b-20261102T212014+0700/start-core.json` | B | KEEP | 2026-11-02T21:20:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/backup-permissions-20261102T222329+0700.json` | B | KEEP | 2026-11-02T22:23:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/backup-permissions-20261102T222329+0700.png` | B | KEEP | 2026-11-02T22:23:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/backup-permissions.txt` | B | KEEP | 2026-11-02T22:22:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/backup-precheck-20261102T221905+0700.json` | B | KEEP | 2026-11-02T22:19:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/backup-precheck-20261102T221905+0700.png` | B | KEEP | 2026-11-02T22:19:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/cancel-transport-input-20261102T221813+0700.json` | B | KEEP | 2026-11-02T22:18:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/cancel-transport-input-20261102T221813+0700.png` | B | KEEP | 2026-11-02T22:18:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/check-backup-existing.txt` | B | KEEP | 2026-11-02T22:19:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/connected-routes-20261102T222320+0700.json` | B | KEEP | 2026-11-02T22:23:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/connected-routes-20261102T222320+0700.png` | B | KEEP | 2026-11-02T22:23:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/connected-routes.txt` | B | KEEP | 2026-11-02T22:22:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/evidence-index-final.csv` | B | KEEP | 2026-11-02T22:25:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/final-integrity.json` | B | KEEP | 2026-11-02T22:22:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/inventory-after-wazuh-shutdown.json` | B | KEEP | 2026-11-02T22:05:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/inventory-before.json` | B | KEEP | 2026-11-02T21:56:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/inventory-primary-running.json` | B | KEEP | 2026-11-02T22:09:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-audit-before.json` | B | KEEP | 2026-11-02T22:21:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-audit-direct-20261102T221926+0700.json` | B | KEEP | 2026-11-02T22:19:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-audit-direct-20261102T221926+0700.png` | B | KEEP | 2026-11-02T22:19:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-authenticated-shell-20261102T220927+0700.json` | B | KEEP | 2026-11-02T22:09:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-authenticated-shell-20261102T220927+0700.png` | B | KEEP | 2026-11-02T22:09:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-boot-observe-20261102T220617+0700.json` | B | KEEP | 2026-11-02T22:06:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-boot-observe-20261102T220617+0700.png` | B | KEEP | 2026-11-02T22:06:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-boot-ready-20261102T220711+0700.json` | B | KEEP | 2026-11-02T22:07:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-boot-ready-20261102T220711+0700.png` | B | KEEP | 2026-11-02T22:07:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-comparison.json` | B | KEEP | 2026-11-02T22:21:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-console-state-20261102T220807+0700.json` | B | KEEP | 2026-11-02T22:08:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/primary-console-state-20261102T220807+0700.png` | B | KEEP | 2026-11-02T22:08:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/run-audit-direct.txt` | B | KEEP | 2026-11-02T22:19:26+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/shutdown-wazuh.txt` | B | KEEP | 2026-11-02T22:05:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/vlan-config-table-20261102T222255+0700.json` | B | KEEP | 2026-11-02T22:23:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/vlan-config-table-20261102T222255+0700.png` | B | KEEP | 2026-11-02T22:23:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/vlan-config-table.txt` | B | KEEP | 2026-11-02T22:22:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/wazuh-before-shutdown-20261102T220455+0700.json` | B | KEEP | 2026-11-02T22:04:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/wazuh-before-shutdown-20261102T220455+0700.png` | B | KEEP | 2026-11-02T22:04:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/wazuh-graceful-poweroff-20261102T220505+0700.json` | B | KEEP | 2026-11-02T22:05:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2a-20261102T215617+0700/wazuh-graceful-poweroff-20261102T220505+0700.png` | B | KEEP | 2026-11-02T22:05:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b-policy-review-20261103T103519+0700/evidence-index.csv` | B | KEEP | 2026-11-03T10:35:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b-policy-review-20261103T103519+0700/policy-review.json` | B | KEEP | 2026-11-03T10:35:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b1-20261103/evidence-index.csv` | B | KEEP | 2026-11-03T10:39:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b1-20261103/primary-readonly-availability.json` | B | KEEP | 2026-11-03T10:37:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b1-20261103/source-manifest.json` | B | KEEP | 2026-11-03T10:39:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/M2-group2b2-firewall-results.md` | B | KEEP | 2026-11-03T16:50:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/M2-group2b2-report.md` | B | KEEP | 2026-11-03T16:51:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/collect-rules-readonly.py` | B | KEEP | 2026-11-03T16:40:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/collect-via-console.py` | B | KEEP | 2026-11-03T16:40:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/configured-firewall-rules.csv` | B | KEEP | 2026-11-03T16:51:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/current-rules-tail-20261103T164800+0700.json` | B | KEEP | 2026-11-03T16:48:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/current-rules-tail-20261103T164800+0700.png` | B | KEEP | 2026-11-03T16:48:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/delivery-checks.json` | B | KEEP | 2026-11-03T16:51:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/evidence-index-final.csv` | B | KEEP | 2026-11-03T16:51:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/evidence-index.csv` | B | KEEP | 2026-11-03T16:37:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/finalize-evidence.py` | B | KEEP | 2026-11-03T16:51:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/firewall-current-public.json` | B | KEEP | 2026-11-03T16:47:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/inventory-final.json` | B | KEEP | 2026-11-03T16:37:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/pf-anchor-filter-current.txt` | B | KEEP | 2026-11-03T16:47:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/pf-filter-rules-current.txt` | B | KEEP | 2026-11-03T16:47:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/pf-filter-verbose-current.txt` | B | KEEP | 2026-11-03T16:47:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/preflight.json` | B | KEEP | 2026-11-03T10:43:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/primary-boot-observe-20261103T104401+0700.json` | B | KEEP | 2026-11-03T10:44:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/primary-boot-observe-20261103T104401+0700.png` | B | KEEP | 2026-11-03T10:44:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/primary-boot-ready-check-20261103T163653+0700.json` | B | KEEP | 2026-11-03T16:36:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/primary-boot-ready-check-20261103T163653+0700.png` | B | KEEP | 2026-11-03T16:36:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/primary-boot-state-20261103T104437+0700.json` | B | KEEP | 2026-11-03T10:44:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/primary-boot-state-20261103T104437+0700.png` | B | KEEP | 2026-11-03T10:44:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/primary-shell-confirm-20261103T163911+0700.json` | B | KEEP | 2026-11-03T16:39:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/primary-shell-confirm-20261103T163911+0700.png` | B | KEEP | 2026-11-03T16:39:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/read-pf-tail.txt` | B | KEEP | 2026-11-03T16:48:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-collection-error.json` | B | KEEP | 2026-11-03T16:44:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0001.txt` | B | KEEP | 2026-11-03T16:40:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0002.txt` | B | KEEP | 2026-11-03T16:41:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0003.txt` | B | KEEP | 2026-11-03T16:42:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0004.txt` | B | KEEP | 2026-11-03T16:42:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0005.txt` | B | KEEP | 2026-11-03T16:43:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0006.txt` | B | KEEP | 2026-11-03T16:43:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0007.txt` | B | KEEP | 2026-11-03T16:44:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0008.txt` | B | KEEP | 2026-11-03T16:44:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0009.txt` | B | KEEP | 2026-11-03T16:45:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0010.txt` | B | KEEP | 2026-11-03T16:46:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/command-0011.txt` | B | KEEP | 2026-11-03T16:46:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job1-20261103T164040+0700.json` | B | KEEP | 2026-11-03T16:41:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job1-20261103T164040+0700.png` | B | KEEP | 2026-11-03T16:41:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job10-20261103T164615+0700.json` | B | KEEP | 2026-11-03T16:46:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job10-20261103T164615+0700.png` | B | KEEP | 2026-11-03T16:46:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job11-20261103T164641+0700.json` | B | KEEP | 2026-11-03T16:47:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job11-20261103T164641+0700.png` | B | KEEP | 2026-11-03T16:47:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job2-20261103T164121+0700.json` | B | KEEP | 2026-11-03T16:42:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job2-20261103T164121+0700.png` | B | KEEP | 2026-11-03T16:42:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job3-20261103T164202+0700.json` | B | KEEP | 2026-11-03T16:42:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job3-20261103T164202+0700.png` | B | KEEP | 2026-11-03T16:42:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job4-20261103T164242+0700.json` | B | KEEP | 2026-11-03T16:43:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job4-20261103T164242+0700.png` | B | KEEP | 2026-11-03T16:43:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job5-20261103T164321+0700.json` | B | KEEP | 2026-11-03T16:43:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job5-20261103T164321+0700.png` | B | KEEP | 2026-11-03T16:43:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job6-20261103T164342+0700.json` | B | KEEP | 2026-11-03T16:44:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job6-20261103T164342+0700.png` | B | KEEP | 2026-11-03T16:44:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job7-20261103T164402+0700.json` | B | KEEP | 2026-11-03T16:44:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job7-20261103T164402+0700.png` | B | KEEP | 2026-11-03T16:44:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job8-20261103T164424+0700.json` | B | KEEP | 2026-11-03T16:44:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job8-20261103T164424+0700.png` | B | KEEP | 2026-11-03T16:44:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job9-20261103T164548+0700.json` | B | KEEP | 2026-11-03T16:46:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/job9-20261103T164548+0700.png` | B | KEEP | 2026-11-03T16:46:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/public-page-1440-20261103T164613+0700.json` | B | KEEP | 2026-11-03T16:46:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/public-page-1440-20261103T164613+0700.png` | B | KEEP | 2026-11-03T16:46:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/public-page-2880-20261103T164638+0700.json` | B | KEEP | 2026-11-03T16:46:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/public-page-2880-20261103T164638+0700.png` | B | KEEP | 2026-11-03T16:46:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/public-page-4320-20261103T164704+0700.json` | B | KEEP | 2026-11-03T16:47:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-console/public-page-4320-20261103T164704+0700.png` | B | KEEP | 2026-11-03T16:47:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-page-observe-20261103T164519+0700.json` | B | KEEP | 2026-11-03T16:45:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/readonly-page-observe-20261103T164519+0700.png` | B | KEEP | 2026-11-03T16:45:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/resume-public-pages.py` | B | KEEP | 2026-11-03T16:45:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/running-pf-rules.csv` | B | KEEP | 2026-11-03T16:51:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2b2-20261103/start-primary.json` | B | KEEP | 2026-11-03T10:43:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2c-20261103/evidence-index.csv` | B | KEEP | 2026-11-03T16:57:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/group2c-20261103/source-manifest.json` | B | KEEP | 2026-11-03T16:56:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/port-design-20261102T125730+0700/eve-inventory.json` | B | KEEP | 2026-11-02T12:57:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/port-design-20261102T125730+0700/windows-memory.json` | B | KEEP | 2026-11-02T12:57:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/port-design-20261102T130406+0700/eve-inventory.json` | B | KEEP | 2026-11-02T13:04:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/port-design-20261102T130406+0700/windows-memory.json` | B | KEEP | 2026-11-02T13:04:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/resume-20261102/core-acpi-powerdown-request-20261102T170839+0700.json` | B | KEEP | 2026-11-02T17:08:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/resume-20261102/core-acpi-powerdown-request-20261102T170839+0700.png` | B | KEEP | 2026-11-02T17:08:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/resume-20261102/core-current-boot-20261102T165739+0700.json` | B | KEEP | 2026-11-02T16:57:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/resume-20261102/core-current-boot-20261102T165739+0700.png` | B | KEEP | 2026-11-02T16:57:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/resume-20261102/core-qemu-monitor-before-acpi-20261102T170806+0700.json` | B | KEEP | 2026-11-02T17:08:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/resume-20261102/core-qemu-monitor-before-acpi-20261102T170806+0700.png` | B | KEEP | 2026-11-02T17:08:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/resume-20261102/vpcs-configured.json` | B | KEEP | 2026-11-02T16:50:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/build-receipt.json` | B | KEEP | 2026-11-02T13:03:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/interfaces-before-sensor-group.csv` | B | KEEP | 2026-11-02T16:52:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/interfaces-before-services-group.csv` | B | KEEP | 2026-11-02T17:09:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/interfaces-ha-pair-current.csv` | B | KEEP | 2026-11-02T15:21:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/interfaces-ha-pfsync-configured.csv` | B | KEEP | 2026-11-02T16:33:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/interfaces-resume-1515.csv` | B | KEEP | 2026-11-02T15:15:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/interfaces-topology-built.csv` | B | KEEP | 2026-11-02T13:08:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/inventory-before-sensor-group.json` | B | KEEP | 2026-11-02T16:52:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/inventory-before-services-group.json` | B | KEEP | 2026-11-02T17:09:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/inventory-before.json` | B | KEEP | 2026-11-02T13:00:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/inventory-ha-pair-current.json` | B | KEEP | 2026-11-02T15:21:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/inventory-ha-pfsync-configured.json` | B | KEEP | 2026-11-02T16:33:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/inventory-resume-1515.json` | B | KEEP | 2026-11-02T15:15:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/inventory-topology-built.json` | B | KEEP | 2026-11-02T13:08:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/lab-before-sensor-group.unl` | B | KEEP | 2026-11-02T16:52:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/lab-before-services-group.unl` | B | KEEP | 2026-11-02T17:09:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/lab-ha-pair-current.unl` | B | KEEP | 2026-11-02T15:21:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/lab-ha-pfsync-configured.unl` | B | KEEP | 2026-11-02T16:33:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/lab-resume-1515.unl` | B | KEEP | 2026-11-02T15:15:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/lab-topology-built.unl` | B | KEEP | 2026-11-02T13:08:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/labels-receipt.json` | B | KEEP | 2026-11-02T13:04:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/nodes-before-sensor-group.csv` | B | KEEP | 2026-11-02T16:52:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/nodes-before-services-group.csv` | B | KEEP | 2026-11-02T17:09:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/nodes-ha-pair-current.csv` | B | KEEP | 2026-11-02T15:21:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/nodes-ha-pfsync-configured.csv` | B | KEEP | 2026-11-02T16:33:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/nodes-resume-1515.csv` | B | KEEP | 2026-11-02T15:15:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/nodes-topology-built.csv` | B | KEEP | 2026-11-02T13:08:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-DMZ-171010.json` | B | KEEP | 2026-11-02T17:10:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-Data-Center-171006.json` | B | KEEP | 2026-11-02T17:10:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-OPNsense-Primary-152006.json` | B | KEEP | 2026-11-02T15:20:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-OPNsense-Primary-220531.json` | B | KEEP | 2026-11-02T22:05:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-SOC-Core-L2-165214.json` | B | KEEP | 2026-11-02T16:52:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-Suricata-NIDS-131923.json` | B | KEEP | 2026-11-02T13:19:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-Suricata-NIDS-165410.json` | B | KEEP | 2026-11-02T16:54:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-Wazuh-SOC-171002.json` | B | KEEP | 2026-11-02T17:10:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/start-Wazuh-SOC-203444.json` | B | KEEP | 2026-11-02T20:34:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/topology-after.png` | B | KEEP | 2026-11-02T13:04:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/topology-before.png` | B | KEEP | 2026-11-02T13:00:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/validation-before-sensor-group.json` | B | KEEP | 2026-11-02T16:52:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/validation-before-services-group.json` | B | KEEP | 2026-11-02T17:09:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/validation-ha-pair-current.json` | B | KEEP | 2026-11-02T15:21:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/validation-ha-pfsync-configured.json` | B | KEEP | 2026-11-02T16:33:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/validation-resume-1515.json` | B | KEEP | 2026-11-02T15:15:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M2/topology-first-20261102/validation-topology-built.json` | B | KEEP | 2026-11-02T13:08:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/backup-SHA256SUMS.txt` | B | KEEP | 2026-11-03T17:58:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/backup-manifest.json` | B | KEEP | 2026-11-03T17:58:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/backup-storage-protection.json` | B | KEEP | 2026-11-03T17:37:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/carp-planning-table.csv` | B | KEEP | 2026-11-03T17:58:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/carp-planning-table.json` | B | KEEP | 2026-11-03T17:58:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/backup-execute-20261103T174724+0700.json` | B | KEEP | 2026-11-03T17:47:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/backup-execute-20261103T174724+0700.png` | B | KEEP | 2026-11-03T17:47:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/backup-execute.txt` | B | KEEP | 2026-11-03T17:47:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-0-20261103T174325+0700.json` | B | KEEP | 2026-11-03T17:44:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-0-20261103T174325+0700.png` | B | KEEP | 2026-11-03T17:44:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-0.txt` | B | KEEP | 2026-11-03T17:43:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-1350-20261103T174511+0700.json` | B | KEEP | 2026-11-03T17:45:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-1350-20261103T174511+0700.png` | B | KEEP | 2026-11-03T17:45:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-1350.txt` | B | KEEP | 2026-11-03T17:45:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-1800-20261103T174546+0700.json` | B | KEEP | 2026-11-03T17:46:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-1800-20261103T174546+0700.png` | B | KEEP | 2026-11-03T17:46:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-1800.txt` | B | KEEP | 2026-11-03T17:45:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-2250-20261103T174623+0700.json` | B | KEEP | 2026-11-03T17:46:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-2250-20261103T174623+0700.png` | B | KEEP | 2026-11-03T17:46:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-2250.txt` | B | KEEP | 2026-11-03T17:46:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-2700-20261103T174658+0700.json` | B | KEEP | 2026-11-03T17:47:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-2700-20261103T174658+0700.png` | B | KEEP | 2026-11-03T17:47:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-2700.txt` | B | KEEP | 2026-11-03T17:46:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-450-20261103T174402+0700.json` | B | KEEP | 2026-11-03T17:44:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-450-20261103T174402+0700.png` | B | KEEP | 2026-11-03T17:44:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-450.txt` | B | KEEP | 2026-11-03T17:44:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-900-20261103T174435+0700.json` | B | KEEP | 2026-11-03T17:45:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-900-20261103T174435+0700.png` | B | KEEP | 2026-11-03T17:45:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/chunk-900.txt` | B | KEEP | 2026-11-03T17:44:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/header-20261103T174741+0700.json` | B | KEEP | 2026-11-03T17:48:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/header-20261103T174741+0700.png` | B | KEEP | 2026-11-03T17:48:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/header-stable-20261103T174807+0700.json` | B | KEEP | 2026-11-03T17:48:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/header-stable-20261103T174807+0700.png` | B | KEEP | 2026-11-03T17:48:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/header.txt` | B | KEEP | 2026-11-03T17:47:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-0-20261103T174809+0700.json` | B | KEEP | 2026-11-03T17:48:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-0-20261103T174809+0700.png` | B | KEEP | 2026-11-03T17:48:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-0-stable-20261103T174830+0700.json` | B | KEEP | 2026-11-03T17:48:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-0-stable-20261103T174830+0700.png` | B | KEEP | 2026-11-03T17:48:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-0.txt` | B | KEEP | 2026-11-03T17:48:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-10080-20261103T175056+0700.json` | B | KEEP | 2026-11-03T17:51:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-10080-20261103T175056+0700.png` | B | KEEP | 2026-11-03T17:51:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-10080-stable-20261103T175119+0700.json` | B | KEEP | 2026-11-03T17:51:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-10080-stable-20261103T175119+0700.png` | B | KEEP | 2026-11-03T17:51:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-10080.txt` | B | KEEP | 2026-11-03T17:50:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-11520-20261103T175121+0700.json` | B | KEEP | 2026-11-03T17:51:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-11520-20261103T175121+0700.png` | B | KEEP | 2026-11-03T17:51:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-11520-stable-20261103T175142+0700.json` | B | KEEP | 2026-11-03T17:51:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-11520-stable-20261103T175142+0700.png` | B | KEEP | 2026-11-03T17:51:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-11520.txt` | B | KEEP | 2026-11-03T17:51:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-12960-20261103T175144+0700.json` | B | KEEP | 2026-11-03T17:52:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-12960-20261103T175144+0700.png` | B | KEEP | 2026-11-03T17:52:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-12960-stable-20261103T175206+0700.json` | B | KEEP | 2026-11-03T17:52:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-12960-stable-20261103T175206+0700.png` | B | KEEP | 2026-11-03T17:52:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-12960.txt` | B | KEEP | 2026-11-03T17:51:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-1440-20261103T174833+0700.json` | B | KEEP | 2026-11-03T17:48:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-1440-20261103T174833+0700.png` | B | KEEP | 2026-11-03T17:48:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-1440-stable-20261103T174854+0700.json` | B | KEEP | 2026-11-03T17:48:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-1440-stable-20261103T174854+0700.png` | B | KEEP | 2026-11-03T17:48:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-1440.txt` | B | KEEP | 2026-11-03T17:48:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-14400-20261103T175209+0700.json` | B | KEEP | 2026-11-03T17:52:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-14400-20261103T175209+0700.png` | B | KEEP | 2026-11-03T17:52:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-14400-stable-20261103T175230+0700.json` | B | KEEP | 2026-11-03T17:52:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-14400-stable-20261103T175230+0700.png` | B | KEEP | 2026-11-03T17:52:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-14400.txt` | B | KEEP | 2026-11-03T17:52:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-15840-20261103T175233+0700.json` | B | KEEP | 2026-11-03T17:52:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-15840-20261103T175233+0700.png` | B | KEEP | 2026-11-03T17:52:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-15840-stable-20261103T175254+0700.json` | B | KEEP | 2026-11-03T17:52:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-15840-stable-20261103T175254+0700.png` | B | KEEP | 2026-11-03T17:52:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-15840.txt` | B | KEEP | 2026-11-03T17:52:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-17280-20261103T175257+0700.json` | B | KEEP | 2026-11-03T17:53:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-17280-20261103T175257+0700.png` | B | KEEP | 2026-11-03T17:53:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-17280-stable-20261103T175318+0700.json` | B | KEEP | 2026-11-03T17:53:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-17280-stable-20261103T175318+0700.png` | B | KEEP | 2026-11-03T17:53:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-17280.txt` | B | KEEP | 2026-11-03T17:52:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-18720-20261103T175322+0700.json` | B | KEEP | 2026-11-03T17:53:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-18720-20261103T175322+0700.png` | B | KEEP | 2026-11-03T17:53:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-18720-stable-20261103T175343+0700.json` | B | KEEP | 2026-11-03T17:53:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-18720-stable-20261103T175343+0700.png` | B | KEEP | 2026-11-03T17:53:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-18720.txt` | B | KEEP | 2026-11-03T17:53:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-20160-20261103T175345+0700.json` | B | KEEP | 2026-11-03T17:54:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-20160-20261103T175345+0700.png` | B | KEEP | 2026-11-03T17:54:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-20160-stable-20261103T175407+0700.json` | B | KEEP | 2026-11-03T17:54:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-20160-stable-20261103T175407+0700.png` | B | KEEP | 2026-11-03T17:54:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-20160.txt` | B | KEEP | 2026-11-03T17:53:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-21600-20261103T175409+0700.json` | B | KEEP | 2026-11-03T17:54:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-21600-20261103T175409+0700.png` | B | KEEP | 2026-11-03T17:54:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-21600-stable-20261103T175431+0700.json` | B | KEEP | 2026-11-03T17:54:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-21600-stable-20261103T175431+0700.png` | B | KEEP | 2026-11-03T17:54:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-21600.txt` | B | KEEP | 2026-11-03T17:54:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-2880-20261103T174857+0700.json` | B | KEEP | 2026-11-03T17:49:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-2880-20261103T174857+0700.png` | B | KEEP | 2026-11-03T17:49:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-2880-stable-20261103T174918+0700.json` | B | KEEP | 2026-11-03T17:49:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-2880-stable-20261103T174918+0700.png` | B | KEEP | 2026-11-03T17:49:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-2880.txt` | B | KEEP | 2026-11-03T17:48:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-4320-20261103T174921+0700.json` | B | KEEP | 2026-11-03T17:49:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-4320-20261103T174921+0700.png` | B | KEEP | 2026-11-03T17:49:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-4320-stable-20261103T174941+0700.json` | B | KEEP | 2026-11-03T17:49:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-4320-stable-20261103T174941+0700.png` | B | KEEP | 2026-11-03T17:49:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-4320.txt` | B | KEEP | 2026-11-03T17:49:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-5760-20261103T174944+0700.json` | B | KEEP | 2026-11-03T17:50:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-5760-20261103T174944+0700.png` | B | KEEP | 2026-11-03T17:50:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-5760-stable-20261103T175006+0700.json` | B | KEEP | 2026-11-03T17:50:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-5760-stable-20261103T175006+0700.png` | B | KEEP | 2026-11-03T17:50:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-5760.txt` | B | KEEP | 2026-11-03T17:49:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-7200-20261103T175008+0700.json` | B | KEEP | 2026-11-03T17:50:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-7200-20261103T175008+0700.png` | B | KEEP | 2026-11-03T17:50:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-7200-stable-20261103T175030+0700.json` | B | KEEP | 2026-11-03T17:50:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-7200-stable-20261103T175030+0700.png` | B | KEEP | 2026-11-03T17:50:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-7200.txt` | B | KEEP | 2026-11-03T17:50:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-8640-20261103T175032+0700.json` | B | KEEP | 2026-11-03T17:50:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-8640-20261103T175032+0700.png` | B | KEEP | 2026-11-03T17:50:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-8640-stable-20261103T175054+0700.json` | B | KEEP | 2026-11-03T17:50:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-8640-stable-20261103T175054+0700.png` | B | KEEP | 2026-11-03T17:50:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary-v2/page-8640.txt` | B | KEEP | 2026-11-03T17:50:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/backup-execute-20261103T174049+0700.json` | B | KEEP | 2026-11-03T17:41:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/backup-execute-20261103T174049+0700.png` | B | KEEP | 2026-11-03T17:41:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/backup-execute.txt` | B | KEEP | 2026-11-03T17:40:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-0-20261103T173907+0700.json` | B | KEEP | 2026-11-03T17:39:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-0-20261103T173907+0700.png` | B | KEEP | 2026-11-03T17:39:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-0.txt` | B | KEEP | 2026-11-03T17:39:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-1400-20261103T173952+0700.json` | B | KEEP | 2026-11-03T17:40:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-1400-20261103T173952+0700.png` | B | KEEP | 2026-11-03T17:40:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-1400.txt` | B | KEEP | 2026-11-03T17:39:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-2100-20261103T174014+0700.json` | B | KEEP | 2026-11-03T17:40:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-2100-20261103T174014+0700.png` | B | KEEP | 2026-11-03T17:40:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-2100.txt` | B | KEEP | 2026-11-03T17:40:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-2800-20261103T174037+0700.json` | B | KEEP | 2026-11-03T17:40:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-2800-20261103T174037+0700.png` | B | KEEP | 2026-11-03T17:40:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-2800.txt` | B | KEEP | 2026-11-03T17:40:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-700-20261103T173930+0700.json` | B | KEEP | 2026-11-03T17:39:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-700-20261103T173930+0700.png` | B | KEEP | 2026-11-03T17:39:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-primary/chunk-700.txt` | B | KEEP | 2026-11-03T17:39:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/backup-execute-20261103T174741+0700.json` | B | KEEP | 2026-11-03T17:48:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/backup-execute-20261103T174741+0700.png` | B | KEEP | 2026-11-03T17:48:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/backup-execute.txt` | B | KEEP | 2026-11-03T17:47:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-0-20261103T174340+0700.json` | B | KEEP | 2026-11-03T17:44:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-0-20261103T174340+0700.png` | B | KEEP | 2026-11-03T17:44:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-0.txt` | B | KEEP | 2026-11-03T17:43:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-1350-20261103T174524+0700.json` | B | KEEP | 2026-11-03T17:46:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-1350-20261103T174524+0700.png` | B | KEEP | 2026-11-03T17:46:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-1350.txt` | B | KEEP | 2026-11-03T17:45:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-1800-20261103T174603+0700.json` | B | KEEP | 2026-11-03T17:46:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-1800-20261103T174603+0700.png` | B | KEEP | 2026-11-03T17:46:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-1800.txt` | B | KEEP | 2026-11-03T17:46:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-2250-20261103T174639+0700.json` | B | KEEP | 2026-11-03T17:47:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-2250-20261103T174639+0700.png` | B | KEEP | 2026-11-03T17:47:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-2250.txt` | B | KEEP | 2026-11-03T17:46:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-2700-20261103T174715+0700.json` | B | KEEP | 2026-11-03T17:47:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-2700-20261103T174715+0700.png` | B | KEEP | 2026-11-03T17:47:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-2700.txt` | B | KEEP | 2026-11-03T17:47:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-450-20261103T174414+0700.json` | B | KEEP | 2026-11-03T17:44:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-450-20261103T174414+0700.png` | B | KEEP | 2026-11-03T17:44:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-450.txt` | B | KEEP | 2026-11-03T17:44:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-900-20261103T174447+0700.json` | B | KEEP | 2026-11-03T17:45:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-900-20261103T174447+0700.png` | B | KEEP | 2026-11-03T17:45:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/chunk-900.txt` | B | KEEP | 2026-11-03T17:44:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/header-20261103T174803+0700.json` | B | KEEP | 2026-11-03T17:48:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/header-20261103T174803+0700.png` | B | KEEP | 2026-11-03T17:48:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/header-stable-20261103T174826+0700.json` | B | KEEP | 2026-11-03T17:48:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/header-stable-20261103T174826+0700.png` | B | KEEP | 2026-11-03T17:48:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/header.txt` | B | KEEP | 2026-11-03T17:48:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-0-20261103T174830+0700.json` | B | KEEP | 2026-11-03T17:48:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-0-20261103T174830+0700.png` | B | KEEP | 2026-11-03T17:48:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-0-stable-20261103T174851+0700.json` | B | KEEP | 2026-11-03T17:48:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-0-stable-20261103T174851+0700.png` | B | KEEP | 2026-11-03T17:48:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-0.txt` | B | KEEP | 2026-11-03T17:48:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-10080-20261103T175121+0700.json` | B | KEEP | 2026-11-03T17:51:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-10080-20261103T175121+0700.png` | B | KEEP | 2026-11-03T17:51:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-10080-stable-20261103T175142+0700.json` | B | KEEP | 2026-11-03T17:51:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-10080-stable-20261103T175142+0700.png` | B | KEEP | 2026-11-03T17:51:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-10080.txt` | B | KEEP | 2026-11-03T17:51:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-11520-20261103T175144+0700.json` | B | KEEP | 2026-11-03T17:52:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-11520-20261103T175144+0700.png` | B | KEEP | 2026-11-03T17:52:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-11520-stable-20261103T175206+0700.json` | B | KEEP | 2026-11-03T17:52:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-11520-stable-20261103T175206+0700.png` | B | KEEP | 2026-11-03T17:52:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-11520.txt` | B | KEEP | 2026-11-03T17:51:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-12960-20261103T175210+0700.json` | B | KEEP | 2026-11-03T17:52:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-12960-20261103T175210+0700.png` | B | KEEP | 2026-11-03T17:52:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-12960-stable-20261103T175231+0700.json` | B | KEEP | 2026-11-03T17:52:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-12960-stable-20261103T175231+0700.png` | B | KEEP | 2026-11-03T17:52:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-12960.txt` | B | KEEP | 2026-11-03T17:52:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-1440-20261103T174853+0700.json` | B | KEEP | 2026-11-03T17:49:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-1440-20261103T174853+0700.png` | B | KEEP | 2026-11-03T17:49:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-1440-stable-20261103T174915+0700.json` | B | KEEP | 2026-11-03T17:49:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-1440-stable-20261103T174915+0700.png` | B | KEEP | 2026-11-03T17:49:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-1440.txt` | B | KEEP | 2026-11-03T17:48:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-14400-20261103T175234+0700.json` | B | KEEP | 2026-11-03T17:52:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-14400-20261103T175234+0700.png` | B | KEEP | 2026-11-03T17:52:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-14400-stable-20261103T175256+0700.json` | B | KEEP | 2026-11-03T17:52:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-14400-stable-20261103T175256+0700.png` | B | KEEP | 2026-11-03T17:52:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-14400.txt` | B | KEEP | 2026-11-03T17:52:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-15840-20261103T175258+0700.json` | B | KEEP | 2026-11-03T17:53:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-15840-20261103T175258+0700.png` | B | KEEP | 2026-11-03T17:53:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-15840-stable-20261103T175320+0700.json` | B | KEEP | 2026-11-03T17:53:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-15840-stable-20261103T175320+0700.png` | B | KEEP | 2026-11-03T17:53:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-15840.txt` | B | KEEP | 2026-11-03T17:52:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-17280-20261103T175322+0700.json` | B | KEEP | 2026-11-03T17:53:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-17280-20261103T175322+0700.png` | B | KEEP | 2026-11-03T17:53:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-17280-stable-20261103T175343+0700.json` | B | KEEP | 2026-11-03T17:53:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-17280-stable-20261103T175343+0700.png` | B | KEEP | 2026-11-03T17:53:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-17280.txt` | B | KEEP | 2026-11-03T17:53:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-18720-20261103T175345+0700.json` | B | KEEP | 2026-11-03T17:54:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-18720-20261103T175345+0700.png` | B | KEEP | 2026-11-03T17:54:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-18720-stable-20261103T175407+0700.json` | B | KEEP | 2026-11-03T17:54:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-18720-stable-20261103T175407+0700.png` | B | KEEP | 2026-11-03T17:54:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-18720.txt` | B | KEEP | 2026-11-03T17:53:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-20160-20261103T175410+0700.json` | B | KEEP | 2026-11-03T17:54:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-20160-20261103T175410+0700.png` | B | KEEP | 2026-11-03T17:54:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-20160-stable-20261103T175431+0700.json` | B | KEEP | 2026-11-03T17:54:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-20160-stable-20261103T175431+0700.png` | B | KEEP | 2026-11-03T17:54:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-20160.txt` | B | KEEP | 2026-11-03T17:54:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-21600-20261103T175434+0700.json` | B | KEEP | 2026-11-03T17:54:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-21600-20261103T175434+0700.png` | B | KEEP | 2026-11-03T17:54:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-21600-stable-20261103T175456+0700.json` | B | KEEP | 2026-11-03T17:55:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-21600-stable-20261103T175456+0700.png` | B | KEEP | 2026-11-03T17:55:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-21600.txt` | B | KEEP | 2026-11-03T17:54:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-2880-20261103T174918+0700.json` | B | KEEP | 2026-11-03T17:49:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-2880-20261103T174918+0700.png` | B | KEEP | 2026-11-03T17:49:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-2880-stable-20261103T174938+0700.json` | B | KEEP | 2026-11-03T17:49:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-2880-stable-20261103T174938+0700.png` | B | KEEP | 2026-11-03T17:49:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-2880.txt` | B | KEEP | 2026-11-03T17:49:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-4320-20261103T174941+0700.json` | B | KEEP | 2026-11-03T17:50:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-4320-20261103T174941+0700.png` | B | KEEP | 2026-11-03T17:50:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-4320-stable-20261103T175003+0700.json` | B | KEEP | 2026-11-03T17:50:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-4320-stable-20261103T175003+0700.png` | B | KEEP | 2026-11-03T17:50:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-4320.txt` | B | KEEP | 2026-11-03T17:49:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-5760-20261103T175006+0700.json` | B | KEEP | 2026-11-03T17:50:26+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-5760-20261103T175006+0700.png` | B | KEEP | 2026-11-03T17:50:26+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-5760-stable-20261103T175028+0700.json` | B | KEEP | 2026-11-03T17:50:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-5760-stable-20261103T175028+0700.png` | B | KEEP | 2026-11-03T17:50:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-5760.txt` | B | KEEP | 2026-11-03T17:50:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-7200-20261103T175031+0700.json` | B | KEEP | 2026-11-03T17:50:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-7200-20261103T175031+0700.png` | B | KEEP | 2026-11-03T17:50:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-7200-stable-20261103T175053+0700.json` | B | KEEP | 2026-11-03T17:50:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-7200-stable-20261103T175053+0700.png` | B | KEEP | 2026-11-03T17:50:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-7200.txt` | B | KEEP | 2026-11-03T17:50:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-8640-20261103T175055+0700.json` | B | KEEP | 2026-11-03T17:51:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-8640-20261103T175055+0700.png` | B | KEEP | 2026-11-03T17:51:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-8640-stable-20261103T175117+0700.json` | B | KEEP | 2026-11-03T17:51:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-8640-stable-20261103T175117+0700.png` | B | KEEP | 2026-11-03T17:51:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/console-backup-secondary-v2/page-8640.txt` | B | KEEP | 2026-11-03T17:50:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/core-before-poweroff-20261103T173651+0700.json` | B | KEEP | 2026-11-03T17:36:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/core-before-poweroff-20261103T173651+0700.png` | B | KEEP | 2026-11-03T17:36:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/core-graceful-poweroff-request-20261103T173718+0700.json` | B | KEEP | 2026-11-03T17:37:26+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/core-graceful-poweroff-request-20261103T173718+0700.png` | B | KEEP | 2026-11-03T17:37:26+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/core-poweroff.txt` | B | KEEP | 2026-11-03T17:37:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/delivery-checks.json` | B | KEEP | 2026-11-03T17:58:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/evidence-index.csv` | B | KEEP | 2026-11-03T17:58:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/inventory-before.json` | B | KEEP | 2026-11-03T17:34:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/inventory-both-running.json` | B | KEEP | 2026-11-03T17:46:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/inventory-final.json` | B | KEEP | 2026-11-03T17:53:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/primary-audit.json` | B | KEEP | 2026-11-03T17:58:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/primary-pfsync-runtime-20261103T175808+0700.json` | B | KEEP | 2026-11-03T17:58:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/primary-pfsync-runtime-20261103T175808+0700.png` | B | KEEP | 2026-11-03T17:58:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/primary-shell-current-20261103T173655+0700.json` | B | KEEP | 2026-11-03T17:36:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/primary-shell-current-20261103T173655+0700.png` | B | KEEP | 2026-11-03T17:36:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/read-sync-runtime.txt` | B | KEEP | 2026-11-03T17:58:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-audit.json` | B | KEEP | 2026-11-03T17:58:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-boot-observe-20261103T173907+0700.json` | B | KEEP | 2026-11-03T17:39:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-boot-observe-20261103T173907+0700.png` | B | KEEP | 2026-11-03T17:39:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-boot-ready-check-20261103T174058+0700.json` | B | KEEP | 2026-11-03T17:41:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-boot-ready-check-20261103T174058+0700.png` | B | KEEP | 2026-11-03T17:41:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-login-state-20261103T174009+0700.json` | B | KEEP | 2026-11-03T17:40:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-login-state-20261103T174009+0700.png` | B | KEEP | 2026-11-03T17:40:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-pfsync-runtime-20261103T175808+0700.json` | B | KEEP | 2026-11-03T17:58:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-pfsync-runtime-20261103T175808+0700.png` | B | KEEP | 2026-11-03T17:58:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-shell-confirm-20261103T174325+0700.json` | B | KEEP | 2026-11-03T17:43:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/secondary-shell-confirm-20261103T174325+0700.png` | B | KEEP | 2026-11-03T17:43:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/source-manifest.json` | B | KEEP | 2026-11-03T17:58:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/start-secondary.json` | B | KEEP | 2026-11-03T17:37:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1-carp-readiness-20261103/transport-public.der` | B | KEEP | 2026-11-03T17:37:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/CARP-final-parameters.csv` | B | KEEP | 2026-11-03T18:30:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/CARP-final-parameters.json` | B | KEEP | 2026-11-03T18:30:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/SHA256SUMS-before.txt` | B | KEEP | 2026-11-03T18:13:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/backup-before-manifest.json` | B | KEEP | 2026-11-03T18:13:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/baseline-conflict-review.json` | B | KEEP | 2026-11-03T18:03:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/check-pfsync-settled.txt` | B | KEEP | 2026-11-03T18:21:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/cipher-args-20261103T181332+0700.json` | B | KEEP | 2026-11-03T18:14:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/cipher-args-20261103T181332+0700.png` | B | KEEP | 2026-11-03T18:14:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/cipher-args.txt` | B | KEEP | 2026-11-03T18:13:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/execute-apply-20261103T181410+0700.json` | B | KEEP | 2026-11-03T18:14:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/execute-apply-20261103T181410+0700.png` | B | KEEP | 2026-11-03T18:14:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/execute-apply.txt` | B | KEEP | 2026-11-03T18:14:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/header-20261103T181431+0700.json` | B | KEEP | 2026-11-03T18:14:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/header-20261103T181431+0700.png` | B | KEEP | 2026-11-03T18:14:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/header-stable-20261103T181454+0700.json` | B | KEEP | 2026-11-03T18:14:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/header-stable-20261103T181454+0700.png` | B | KEEP | 2026-11-03T18:14:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/header.txt` | B | KEEP | 2026-11-03T18:14:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/page-0-20261103T181457+0700.json` | B | KEEP | 2026-11-03T18:15:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/page-0-20261103T181457+0700.png` | B | KEEP | 2026-11-03T18:15:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/page-0-stable-20261103T181517+0700.json` | B | KEEP | 2026-11-03T18:15:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/page-0-stable-20261103T181517+0700.png` | B | KEEP | 2026-11-03T18:15:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-apply/page-0.txt` | B | KEEP | 2026-11-03T18:14:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/execute-audit-20261103T181106+0700.json` | B | KEEP | 2026-11-03T18:11:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/execute-audit-20261103T181106+0700.png` | B | KEEP | 2026-11-03T18:11:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/execute-audit.txt` | B | KEEP | 2026-11-03T18:11:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/header-20261103T181125+0700.json` | B | KEEP | 2026-11-03T18:11:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/header-20261103T181125+0700.png` | B | KEEP | 2026-11-03T18:11:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/header-stable-20261103T181147+0700.json` | B | KEEP | 2026-11-03T18:11:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/header-stable-20261103T181147+0700.png` | B | KEEP | 2026-11-03T18:11:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/header.txt` | B | KEEP | 2026-11-03T18:11:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-0-20261103T181149+0700.json` | B | KEEP | 2026-11-03T18:12:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-0-20261103T181149+0700.png` | B | KEEP | 2026-11-03T18:12:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-0-stable-20261103T181210+0700.json` | B | KEEP | 2026-11-03T18:12:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-0-stable-20261103T181210+0700.png` | B | KEEP | 2026-11-03T18:12:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-0.txt` | B | KEEP | 2026-11-03T18:11:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-1440-20261103T181213+0700.json` | B | KEEP | 2026-11-03T18:12:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-1440-20261103T181213+0700.png` | B | KEEP | 2026-11-03T18:12:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-1440-stable-20261103T181234+0700.json` | B | KEEP | 2026-11-03T18:12:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-1440-stable-20261103T181234+0700.png` | B | KEEP | 2026-11-03T18:12:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-1440.txt` | B | KEEP | 2026-11-03T18:12:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-2880-20261103T181236+0700.json` | B | KEEP | 2026-11-03T18:12:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-2880-20261103T181236+0700.png` | B | KEEP | 2026-11-03T18:12:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-2880-stable-20261103T181257+0700.json` | B | KEEP | 2026-11-03T18:12:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-2880-stable-20261103T181257+0700.png` | B | KEEP | 2026-11-03T18:12:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/page-2880.txt` | B | KEEP | 2026-11-03T18:12:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-0-20261103T180606+0700.json` | B | KEEP | 2026-11-03T18:06:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-0-20261103T180606+0700.png` | B | KEEP | 2026-11-03T18:06:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-0.txt` | B | KEEP | 2026-11-03T18:06:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-1350-20261103T180752+0700.json` | B | KEEP | 2026-11-03T18:08:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-1350-20261103T180752+0700.png` | B | KEEP | 2026-11-03T18:08:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-1350.txt` | B | KEEP | 2026-11-03T18:07:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-1800-20261103T180828+0700.json` | B | KEEP | 2026-11-03T18:09:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-1800-20261103T180828+0700.png` | B | KEEP | 2026-11-03T18:09:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-1800.txt` | B | KEEP | 2026-11-03T18:08:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-2250-20261103T180904+0700.json` | B | KEEP | 2026-11-03T18:09:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-2250-20261103T180904+0700.png` | B | KEEP | 2026-11-03T18:09:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-2250.txt` | B | KEEP | 2026-11-03T18:09:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-2700-20261103T180939+0700.json` | B | KEEP | 2026-11-03T18:10:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-2700-20261103T180939+0700.png` | B | KEEP | 2026-11-03T18:10:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-2700.txt` | B | KEEP | 2026-11-03T18:09:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-3150-20261103T181015+0700.json` | B | KEEP | 2026-11-03T18:10:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-3150-20261103T181015+0700.png` | B | KEEP | 2026-11-03T18:10:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-3150.txt` | B | KEEP | 2026-11-03T18:10:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-3600-20261103T181049+0700.json` | B | KEEP | 2026-11-03T18:11:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-3600-20261103T181049+0700.png` | B | KEEP | 2026-11-03T18:11:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-3600.txt` | B | KEEP | 2026-11-03T18:10:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-450-20261103T180640+0700.json` | B | KEEP | 2026-11-03T18:07:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-450-20261103T180640+0700.png` | B | KEEP | 2026-11-03T18:07:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-450.txt` | B | KEEP | 2026-11-03T18:06:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-900-20261103T180716+0700.json` | B | KEEP | 2026-11-03T18:07:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-900-20261103T180716+0700.png` | B | KEEP | 2026-11-03T18:07:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-audit/stage-900.txt` | B | KEEP | 2026-11-03T18:07:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/execute-repair-20261103T181832+0700.json` | B | KEEP | 2026-11-03T18:18:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/execute-repair-20261103T181832+0700.png` | B | KEEP | 2026-11-03T18:18:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/execute-repair.txt` | B | KEEP | 2026-11-03T18:18:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/header-20261103T181849+0700.json` | B | KEEP | 2026-11-03T18:19:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/header-20261103T181849+0700.png` | B | KEEP | 2026-11-03T18:19:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/header-stable-20261103T181912+0700.json` | B | KEEP | 2026-11-03T18:19:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/header-stable-20261103T181912+0700.png` | B | KEEP | 2026-11-03T18:19:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/header.txt` | B | KEEP | 2026-11-03T18:18:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/page-0-20261103T181914+0700.json` | B | KEEP | 2026-11-03T18:19:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/page-0-20261103T181914+0700.png` | B | KEEP | 2026-11-03T18:19:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/page-0-stable-20261103T181934+0700.json` | B | KEEP | 2026-11-03T18:19:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/page-0-stable-20261103T181934+0700.png` | B | KEEP | 2026-11-03T18:19:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/page-0.txt` | B | KEEP | 2026-11-03T18:19:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-0-20261103T181703+0700.json` | B | KEEP | 2026-11-03T18:17:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-0-20261103T181703+0700.png` | B | KEEP | 2026-11-03T18:17:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-0.txt` | B | KEEP | 2026-11-03T18:17:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-450-20261103T181740+0700.json` | B | KEEP | 2026-11-03T18:18:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-450-20261103T181740+0700.png` | B | KEEP | 2026-11-03T18:18:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-450.txt` | B | KEEP | 2026-11-03T18:17:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-900-20261103T181815+0700.json` | B | KEEP | 2026-11-03T18:18:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-900-20261103T181815+0700.png` | B | KEEP | 2026-11-03T18:18:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-primary-repair/repair-chunk-900.txt` | B | KEEP | 2026-11-03T18:18:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/cipher-args-20261103T181332+0700.json` | B | KEEP | 2026-11-03T18:14:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/cipher-args-20261103T181332+0700.png` | B | KEEP | 2026-11-03T18:14:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/cipher-args.txt` | B | KEEP | 2026-11-03T18:13:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/execute-apply-20261103T181410+0700.json` | B | KEEP | 2026-11-03T18:14:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/execute-apply-20261103T181410+0700.png` | B | KEEP | 2026-11-03T18:14:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/execute-apply.txt` | B | KEEP | 2026-11-03T18:14:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/header-20261103T181431+0700.json` | B | KEEP | 2026-11-03T18:14:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/header-20261103T181431+0700.png` | B | KEEP | 2026-11-03T18:14:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/header-stable-20261103T181454+0700.json` | B | KEEP | 2026-11-03T18:14:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/header-stable-20261103T181454+0700.png` | B | KEEP | 2026-11-03T18:14:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/header.txt` | B | KEEP | 2026-11-03T18:14:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/page-0-20261103T181457+0700.json` | B | KEEP | 2026-11-03T18:15:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/page-0-20261103T181457+0700.png` | B | KEEP | 2026-11-03T18:15:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/page-0-stable-20261103T181517+0700.json` | B | KEEP | 2026-11-03T18:15:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/page-0-stable-20261103T181517+0700.png` | B | KEEP | 2026-11-03T18:15:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-apply/page-0.txt` | B | KEEP | 2026-11-03T18:14:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/execute-audit-20261103T181106+0700.json` | B | KEEP | 2026-11-03T18:11:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/execute-audit-20261103T181106+0700.png` | B | KEEP | 2026-11-03T18:11:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/execute-audit.txt` | B | KEEP | 2026-11-03T18:11:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/header-20261103T181125+0700.json` | B | KEEP | 2026-11-03T18:11:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/header-20261103T181125+0700.png` | B | KEEP | 2026-11-03T18:11:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/header-stable-20261103T181147+0700.json` | B | KEEP | 2026-11-03T18:11:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/header-stable-20261103T181147+0700.png` | B | KEEP | 2026-11-03T18:11:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/header.txt` | B | KEEP | 2026-11-03T18:11:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-0-20261103T181149+0700.json` | B | KEEP | 2026-11-03T18:12:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-0-20261103T181149+0700.png` | B | KEEP | 2026-11-03T18:12:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-0-stable-20261103T181210+0700.json` | B | KEEP | 2026-11-03T18:12:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-0-stable-20261103T181210+0700.png` | B | KEEP | 2026-11-03T18:12:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-0.txt` | B | KEEP | 2026-11-03T18:11:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-1440-20261103T181213+0700.json` | B | KEEP | 2026-11-03T18:12:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-1440-20261103T181213+0700.png` | B | KEEP | 2026-11-03T18:12:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-1440-stable-20261103T181234+0700.json` | B | KEEP | 2026-11-03T18:12:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-1440-stable-20261103T181234+0700.png` | B | KEEP | 2026-11-03T18:12:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-1440.txt` | B | KEEP | 2026-11-03T18:12:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-2880-20261103T181236+0700.json` | B | KEEP | 2026-11-03T18:12:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-2880-20261103T181236+0700.png` | B | KEEP | 2026-11-03T18:12:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-2880-stable-20261103T181257+0700.json` | B | KEEP | 2026-11-03T18:12:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-2880-stable-20261103T181257+0700.png` | B | KEEP | 2026-11-03T18:12:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/page-2880.txt` | B | KEEP | 2026-11-03T18:12:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-0-20261103T180606+0700.json` | B | KEEP | 2026-11-03T18:06:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-0-20261103T180606+0700.png` | B | KEEP | 2026-11-03T18:06:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-0.txt` | B | KEEP | 2026-11-03T18:06:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-1350-20261103T180752+0700.json` | B | KEEP | 2026-11-03T18:08:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-1350-20261103T180752+0700.png` | B | KEEP | 2026-11-03T18:08:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-1350.txt` | B | KEEP | 2026-11-03T18:07:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-1800-20261103T180828+0700.json` | B | KEEP | 2026-11-03T18:09:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-1800-20261103T180828+0700.png` | B | KEEP | 2026-11-03T18:09:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-1800.txt` | B | KEEP | 2026-11-03T18:08:28+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-2250-20261103T180904+0700.json` | B | KEEP | 2026-11-03T18:09:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-2250-20261103T180904+0700.png` | B | KEEP | 2026-11-03T18:09:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-2250.txt` | B | KEEP | 2026-11-03T18:09:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-2700-20261103T180939+0700.json` | B | KEEP | 2026-11-03T18:10:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-2700-20261103T180939+0700.png` | B | KEEP | 2026-11-03T18:10:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-2700.txt` | B | KEEP | 2026-11-03T18:09:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-3150-20261103T181015+0700.json` | B | KEEP | 2026-11-03T18:10:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-3150-20261103T181015+0700.png` | B | KEEP | 2026-11-03T18:10:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-3150.txt` | B | KEEP | 2026-11-03T18:10:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-3600-20261103T181049+0700.json` | B | KEEP | 2026-11-03T18:11:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-3600-20261103T181049+0700.png` | B | KEEP | 2026-11-03T18:11:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-3600.txt` | B | KEEP | 2026-11-03T18:10:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-450-20261103T180640+0700.json` | B | KEEP | 2026-11-03T18:07:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-450-20261103T180640+0700.png` | B | KEEP | 2026-11-03T18:07:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-450.txt` | B | KEEP | 2026-11-03T18:06:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-900-20261103T180716+0700.json` | B | KEEP | 2026-11-03T18:07:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-900-20261103T180716+0700.png` | B | KEEP | 2026-11-03T18:07:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-audit/stage-900.txt` | B | KEEP | 2026-11-03T18:07:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/execute-repair-20261103T181832+0700.json` | B | KEEP | 2026-11-03T18:18:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/execute-repair-20261103T181832+0700.png` | B | KEEP | 2026-11-03T18:18:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/execute-repair.txt` | B | KEEP | 2026-11-03T18:18:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/header-20261103T181849+0700.json` | B | KEEP | 2026-11-03T18:19:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/header-20261103T181849+0700.png` | B | KEEP | 2026-11-03T18:19:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/header-stable-20261103T181912+0700.json` | B | KEEP | 2026-11-03T18:19:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/header-stable-20261103T181912+0700.png` | B | KEEP | 2026-11-03T18:19:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/header.txt` | B | KEEP | 2026-11-03T18:18:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/page-0-20261103T181914+0700.json` | B | KEEP | 2026-11-03T18:19:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/page-0-20261103T181914+0700.png` | B | KEEP | 2026-11-03T18:19:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/page-0-stable-20261103T181935+0700.json` | B | KEEP | 2026-11-03T18:19:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/page-0-stable-20261103T181935+0700.png` | B | KEEP | 2026-11-03T18:19:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/page-0.txt` | B | KEEP | 2026-11-03T18:19:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-0-20261103T181703+0700.json` | B | KEEP | 2026-11-03T18:17:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-0-20261103T181703+0700.png` | B | KEEP | 2026-11-03T18:17:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-0.txt` | B | KEEP | 2026-11-03T18:17:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-450-20261103T181739+0700.json` | B | KEEP | 2026-11-03T18:18:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-450-20261103T181739+0700.png` | B | KEEP | 2026-11-03T18:18:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-450.txt` | B | KEEP | 2026-11-03T18:17:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-900-20261103T181816+0700.json` | B | KEEP | 2026-11-03T18:18:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-900-20261103T181816+0700.png` | B | KEEP | 2026-11-03T18:18:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/console-secondary-repair/repair-chunk-900.txt` | B | KEEP | 2026-11-03T18:18:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/endpoint-address-review.json` | B | KEEP | 2026-11-03T18:09:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/evidence-index.csv` | B | KEEP | 2026-11-03T18:30:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/inventory-before.json` | B | KEEP | 2026-11-03T18:02:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/pfsync-bulk-log.txt` | B | KEEP | 2026-11-03T18:27:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/pfsync-capture-start.json` | B | KEEP | 2026-11-03T18:13:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/pfsync-capture-stop.json` | B | KEEP | 2026-11-03T18:20:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/pfsync-control-decoded.json` | B | KEEP | 2026-11-03T18:24:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/pfsync-errors.txt` | B | KEEP | 2026-11-03T18:23:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/pfsync-final-readonly.txt` | B | KEEP | 2026-11-03T18:27:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/pfsync-sequential-retry.txt` | B | KEEP | 2026-11-03T18:25:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-apply.json` | B | KEEP | 2026-11-03T18:15:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-audit.json` | B | KEEP | 2026-11-03T18:12:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-carp-recipient-public.der` | B | KEEP | 2026-11-03T18:13:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-bulk-log-20261103T182737+0700.json` | B | KEEP | 2026-11-03T18:27:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-bulk-log-20261103T182737+0700.png` | B | KEEP | 2026-11-03T18:27:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-errors-20261103T182315+0700.json` | B | KEEP | 2026-11-03T18:23:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-errors-20261103T182315+0700.png` | B | KEEP | 2026-11-03T18:23:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-retry-stable-20261103T182701+0700.json` | B | KEEP | 2026-11-03T18:27:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-retry-stable-20261103T182701+0700.png` | B | KEEP | 2026-11-03T18:27:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-sequential-retry-20261103T182549+0700.json` | B | KEEP | 2026-11-03T18:26:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-sequential-retry-20261103T182549+0700.png` | B | KEEP | 2026-11-03T18:26:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-settled-20261103T182141+0700.json` | B | KEEP | 2026-11-03T18:21:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-pfsync-settled-20261103T182141+0700.png` | B | KEEP | 2026-11-03T18:21:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-repair.json` | B | KEEP | 2026-11-03T18:19:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-shell-initial-20261103T180211+0700.json` | B | KEEP | 2026-11-03T18:02:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/primary-shell-initial-20261103T180211+0700.png` | B | KEEP | 2026-11-03T18:02:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/result.json` | B | KEEP | 2026-11-03T18:30:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-apply.json` | B | KEEP | 2026-11-03T18:15:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-audit.json` | B | KEEP | 2026-11-03T18:12:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-carp-recipient-public.der` | B | KEEP | 2026-11-03T18:13:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-bulk-log-20261103T182737+0700.json` | B | KEEP | 2026-11-03T18:27:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-bulk-log-20261103T182737+0700.png` | B | KEEP | 2026-11-03T18:27:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-errors-20261103T182315+0700.json` | B | KEEP | 2026-11-03T18:23:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-errors-20261103T182315+0700.png` | B | KEEP | 2026-11-03T18:23:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-final-20261103T182701+0700.json` | B | KEEP | 2026-11-03T18:27:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-final-20261103T182701+0700.png` | B | KEEP | 2026-11-03T18:27:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-settled-20261103T182141+0700.json` | B | KEEP | 2026-11-03T18:21:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-settled-20261103T182141+0700.png` | B | KEEP | 2026-11-03T18:21:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-repair.json` | B | KEEP | 2026-11-03T18:19:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-shell-initial-20261103T180211+0700.json` | B | KEEP | 2026-11-03T18:02:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/secondary-shell-initial-20261103T180211+0700.png` | B | KEEP | 2026-11-03T18:02:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group1b-prerequisites-20261103/settled-verification.json` | B | KEEP | 2026-11-03T18:30:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/group2a-apply-20261103/console-hello-20261103T192904+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:29:11+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/console-hello-20261103T192904+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:29:11+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-apply-20261103T193209+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:32:27+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-apply-20261103T193209+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:32:27+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-commands-20261103T192725+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:27:49+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-commands-20261103T192725+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:27:49+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-probe-20261103T192450+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:25:12+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-probe-20261103T192450+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:25:12+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-verify-20261103T193403+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:34:23+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-verify-20261103T193403+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:34:23+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-status-20261103T192325+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:23:33+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-status-20261103T192325+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:23:33+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-xml-shape-20261103T192547+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:26:07+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/primary-xml-shape-20261103T192547+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:26:07+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/secondary-carp-apply-20261103T193258+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:33:16+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/secondary-carp-apply-20261103T193258+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:33:16+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/secondary-carp-verify-20261103T193443+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:35:02+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/group2a-apply-20261103/secondary-carp-verify-20261103T193443+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:35:02+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-absolute-probe-20261103T202600+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:26:28+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-absolute-probe-20261103T202600+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:26:28+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-carp-runtime-setup-20261103T200121+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:01:38+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-carp-runtime-setup-20261103T200121+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:01:38+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-echo-test-20261103T200418+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:04:28+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-echo-test-20261103T200418+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:04:28+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-hostname-check-20261103T201034+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:10:41+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-hostname-check-20261103T201034+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:10:41+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-hostname-test-20261103T202734+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:27:43+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-hostname-test-20261103T202734+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:27:43+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-installed-20261101/command-config-api.txt` | B | KEEP | 2026-11-01T22:13:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/command-disk.txt` | B | KEEP | 2026-11-01T22:12:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/command-interface-entry.txt` | B | KEEP | 2026-11-01T22:16:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/command-nic-mac.txt` | B | KEEP | 2026-11-01T22:13:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/command-version.txt` | B | KEEP | 2026-11-01T22:17:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/command-vlan-api.txt` | B | KEEP | 2026-11-01T22:14:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/command-vlan-runtime-api.txt` | B | KEEP | 2026-11-01T22:15:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/command-vlan-schema.txt` | B | KEEP | 2026-11-01T22:15:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-config-api-20261101T221344+0700.json` | B | KEEP | 2026-11-01T22:13:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-config-api-20261101T221344+0700.png` | B | KEEP | 2026-11-01T22:13:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-disk-20261101T221251+0700.json` | B | KEEP | 2026-11-01T22:12:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-disk-20261101T221251+0700.png` | B | KEEP | 2026-11-01T22:12:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-interface-entry-20261101T221601+0700.json` | B | KEEP | 2026-11-01T22:16:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-interface-entry-20261101T221601+0700.png` | B | KEEP | 2026-11-01T22:16:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-nic-mac-20261101T221304+0700.json` | B | KEEP | 2026-11-01T22:13:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-nic-mac-20261101T221304+0700.png` | B | KEEP | 2026-11-01T22:13:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-version-20261101T221706+0700.json` | B | KEEP | 2026-11-01T22:17:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-version-20261101T221706+0700.png` | B | KEEP | 2026-11-01T22:17:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-vlan-api-20261101T221435+0700.json` | B | KEEP | 2026-11-01T22:14:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-vlan-api-20261101T221435+0700.png` | B | KEEP | 2026-11-01T22:14:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-vlan-runtime-api-20261101T221525+0700.json` | B | KEEP | 2026-11-01T22:15:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-vlan-runtime-api-20261101T221525+0700.png` | B | KEEP | 2026-11-01T22:15:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-vlan-schema-20261101T221512+0700.json` | B | KEEP | 2026-11-01T22:15:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-installed-20261101/primary-vlan-schema-20261101T221512+0700.png` | B | KEEP | 2026-11-01T22:15:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/disk-boot-start.json` | B | KEEP | 2026-11-01T22:08:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installed-backup-boot-disk.json` | B | KEEP | 2026-11-01T22:07:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installed-root-shell-20261101T221244+0700.json` | B | KEEP | 2026-11-01T22:12:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installed-root-shell-20261101T221244+0700.png` | B | KEEP | 2026-11-01T22:12:46+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-copy-progress-20261101T132813+0700.json` | B | KEEP | 2026-11-01T13:28:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-copy-progress-20261101T132813+0700.png` | B | KEEP | 2026-11-01T13:28:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-copy-progress2-20261101T132908+0700.json` | B | KEEP | 2026-11-01T13:29:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-copy-progress2-20261101T132908+0700.png` | B | KEEP | 2026-11-01T13:29:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-copy-status-20261101T132739+0700.json` | B | KEEP | 2026-11-01T13:27:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-copy-status-20261101T132739+0700.png` | B | KEEP | 2026-11-01T13:27:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-disk-confirm-20261101T132621+0700.json` | B | KEEP | 2026-11-01T13:26:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-disk-confirm-20261101T132621+0700.png` | B | KEEP | 2026-11-01T13:26:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-keymap-20261101T131744+0700.json` | B | KEEP | 2026-11-01T13:17:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-keymap-20261101T131744+0700.png` | B | KEEP | 2026-11-01T13:17:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-options-20261101T131807+0700.json` | B | KEEP | 2026-11-01T13:18:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-options-20261101T131807+0700.png` | B | KEEP | 2026-11-01T13:18:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-progress-20261101T132703+0700.json` | B | KEEP | 2026-11-01T13:27:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-progress-20261101T132703+0700.png` | B | KEEP | 2026-11-01T13:27:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-resume-check-20261101T132603+0700.json` | B | KEEP | 2026-11-01T13:26:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-resume-check-20261101T132603+0700.png` | B | KEEP | 2026-11-01T13:26:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-ufs-target-20261101T131826+0700.json` | B | KEEP | 2026-11-01T13:18:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-ufs-target-20261101T131826+0700.png` | B | KEEP | 2026-11-01T13:18:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-write-started-20261101T132632+0700.json` | B | KEEP | 2026-11-01T13:26:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/installer-write-started-20261101T132632+0700.png` | B | KEEP | 2026-11-01T13:26:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-boot-complete-check-20261101T221159+0700.json` | B | KEEP | 2026-11-01T22:12:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-boot-complete-check-20261101T221159+0700.png` | B | KEEP | 2026-11-01T22:12:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-disk-boot-20261101T220858+0700.json` | B | KEEP | 2026-11-01T22:09:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-disk-boot-20261101T220858+0700.png` | B | KEEP | 2026-11-01T22:09:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-disk-login-ready-20261101T221051+0700.json` | B | KEEP | 2026-11-01T22:10:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-disk-login-ready-20261101T221051+0700.png` | B | KEEP | 2026-11-01T22:10:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-installed-console-20261101T220953+0700.json` | B | KEEP | 2026-11-01T22:09:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-installed-console-20261101T220953+0700.png` | B | KEEP | 2026-11-01T22:09:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-installed-login-20261101T221029+0700.json` | B | KEEP | 2026-11-01T22:10:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-20261101/primary-installed-login-20261101T221029+0700.png` | B | KEEP | 2026-11-01T22:10:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/primary-live-state-20261103T195034+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:50:57+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-live-state-20261103T195034+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:50:57+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-login-root-attempt-20261103T202219+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:22:27+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-login-root-attempt-20261103T202219+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:22:27+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-recovery-check-20261103T203042+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:30:52+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-recovery-check-20261103T203042+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:30:52+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-reload-abs-20261103T195757+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:58:07+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-reload-abs-20261103T195757+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:58:07+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-reload-check-20261103T195230+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:52:55+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-reload-check-20261103T195230+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:52:55+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-reload-single-20261103T195455+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:55:11+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-reload-single-20261103T195455+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:55:11+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-reload-single-20261103T195711+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:57:19+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-reload-single-20261103T195711+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:57:19+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-shell-probe-20261103T202324+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:23:59+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-shell-probe-20261103T202324+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:23:59+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-shell-probe-csh-20261103T202447+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:25:17+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-shell-probe-csh-20261103T202447+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:25:17+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-shell-verify-20261103T200832+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:09:04+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-shell-verify-20261103T200832+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:09:04+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-vlan30-create-20261103T195913+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T19:59:26+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-vlan30-create-20261103T195913+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T19:59:26+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-vlan30-create-20261103T200255+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:03:07+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-vlan30-create-20261103T200255+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:03:07+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-vlan30-fileproof-20261103T200330+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T20:03:43+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/primary-vlan30-fileproof-20261103T200330+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T20:03:43+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/recovery-check/primary-recovery-shell-20261103T210659+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T21:07:18+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/recovery-check/primary-recovery-shell-20261103T210659+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T21:07:18+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/resume-20261102/filter-backend-version-20261102T152939+0700.json` | B | KEEP | 2026-11-02T15:29:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/filter-backend-version-20261102T152939+0700.png` | B | KEEP | 2026-11-02T15:29:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/filter-config-schema-20261102T152854+0700.json` | B | KEEP | 2026-11-02T15:29:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/filter-config-schema-20261102T152854+0700.png` | B | KEEP | 2026-11-02T15:29:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-native-api-20261102T152621+0700.json` | B | KEEP | 2026-11-02T15:26:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-native-api-20261102T152621+0700.png` | B | KEEP | 2026-11-02T15:26:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/command-0001.txt` | B | KEEP | 2026-11-02T15:32:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/command-0002.txt` | B | KEEP | 2026-11-02T15:32:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/command-0003.txt` | B | KEEP | 2026-11-02T15:33:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/command-0004.txt` | B | KEEP | 2026-11-02T15:34:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/command-0005.txt` | B | KEEP | 2026-11-02T15:35:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/command-0006.txt` | B | KEEP | 2026-11-02T15:35:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/command-0007.txt` | B | KEEP | 2026-11-02T15:35:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job1-20261102T153250+0700.json` | B | KEEP | 2026-11-02T15:32:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job1-20261102T153250+0700.png` | B | KEEP | 2026-11-02T15:32:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job2-20261102T153257+0700.json` | B | KEEP | 2026-11-02T15:33:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job2-20261102T153257+0700.png` | B | KEEP | 2026-11-02T15:33:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job3-20261102T153338+0700.json` | B | KEEP | 2026-11-02T15:34:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job3-20261102T153338+0700.png` | B | KEEP | 2026-11-02T15:34:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job4-20261102T153420+0700.json` | B | KEEP | 2026-11-02T15:35:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job4-20261102T153420+0700.png` | B | KEEP | 2026-11-02T15:35:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job5-20261102T153501+0700.json` | B | KEEP | 2026-11-02T15:35:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job5-20261102T153501+0700.png` | B | KEEP | 2026-11-02T15:35:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job6-20261102T153521+0700.json` | B | KEEP | 2026-11-02T15:35:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job6-20261102T153521+0700.png` | B | KEEP | 2026-11-02T15:35:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job7-20261102T153553+0700.json` | B | KEEP | 2026-11-02T15:36:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Primary/job7-20261102T153553+0700.png` | B | KEEP | 2026-11-02T15:36:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/command-0001.txt` | B | KEEP | 2026-11-02T15:32:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/command-0002.txt` | B | KEEP | 2026-11-02T15:32:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/command-0003.txt` | B | KEEP | 2026-11-02T15:33:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/command-0004.txt` | B | KEEP | 2026-11-02T15:33:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/command-0005.txt` | B | KEEP | 2026-11-02T15:34:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/command-0006.txt` | B | KEEP | 2026-11-02T15:34:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/command-0007.txt` | B | KEEP | 2026-11-02T15:35:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job1-20261102T153220+0700.json` | B | KEEP | 2026-11-02T15:32:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job1-20261102T153220+0700.png` | B | KEEP | 2026-11-02T15:32:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job2-20261102T153229+0700.json` | B | KEEP | 2026-11-02T15:33:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job2-20261102T153229+0700.png` | B | KEEP | 2026-11-02T15:33:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job3-20261102T153311+0700.json` | B | KEEP | 2026-11-02T15:33:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job3-20261102T153311+0700.png` | B | KEEP | 2026-11-02T15:33:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job4-20261102T153352+0700.json` | B | KEEP | 2026-11-02T15:34:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job4-20261102T153352+0700.png` | B | KEEP | 2026-11-02T15:34:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job5-20261102T153433+0700.json` | B | KEEP | 2026-11-02T15:34:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job5-20261102T153433+0700.png` | B | KEEP | 2026-11-02T15:34:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job6-20261102T153453+0700.json` | B | KEEP | 2026-11-02T15:35:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job6-20261102T153453+0700.png` | B | KEEP | 2026-11-02T15:35:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job7-20261102T153525+0700.json` | B | KEEP | 2026-11-02T15:35:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/ha-stage-Secondary/job7-20261102T153525+0700.png` | B | KEEP | 2026-11-02T15:35:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/pfsync-helper-and-disk-sync-20261102T161619+0700.json` | B | KEEP | 2026-11-02T16:16:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/pfsync-helper-and-disk-sync-20261102T161619+0700.png` | B | KEEP | 2026-11-02T16:16:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/pfsync-native-function-20261102T155952+0700.json` | B | KEEP | 2026-11-02T16:00:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/pfsync-native-function-20261102T155952+0700.png` | B | KEEP | 2026-11-02T16:00:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/pfsync-packets.json` | B | KEEP | 2026-11-02T16:22:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-authenticated-shell-20261102T152759+0700.json` | B | KEEP | 2026-11-02T15:28:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-authenticated-shell-20261102T152759+0700.png` | B | KEEP | 2026-11-02T15:28:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-boot-current-20261102T152030+0700.json` | B | KEEP | 2026-11-02T15:20:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-boot-current-20261102T152030+0700.png` | B | KEEP | 2026-11-02T15:20:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-current-after-boot-20261102T152301+0700.json` | B | KEEP | 2026-11-02T15:23:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-current-after-boot-20261102T152301+0700.png` | B | KEEP | 2026-11-02T15:23:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-employee-diagnostic-rules-20261102T165019+0700.json` | B | KEEP | 2026-11-02T16:50:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-employee-diagnostic-rules-20261102T165019+0700.png` | B | KEEP | 2026-11-02T16:50:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-ha-checkpoint-park-20261102T170706+0700.json` | B | KEEP | 2026-11-02T17:07:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-ha-checkpoint-park-20261102T170706+0700.png` | B | KEEP | 2026-11-02T17:07:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-ha-rules-applied-20261102T153652+0700.json` | B | KEEP | 2026-11-02T15:37:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-ha-rules-applied-20261102T153652+0700.png` | B | KEEP | 2026-11-02T15:37:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pfsync-configured-20261102T161130+0700.json` | B | KEEP | 2026-11-02T16:11:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pfsync-configured-20261102T161130+0700.png` | B | KEEP | 2026-11-02T16:11:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pfsync-native-20261102T161429+0700.json` | B | KEEP | 2026-11-02T16:14:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pfsync-native-20261102T161429+0700.png` | B | KEEP | 2026-11-02T16:14:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pfsync-peer-test-20261102T162201+0700.json` | B | KEEP | 2026-11-02T16:22:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pfsync-peer-test-20261102T162201+0700.png` | B | KEEP | 2026-11-02T16:22:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pfsync-with-helper-20261102T161847+0700.json` | B | KEEP | 2026-11-02T16:19:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pfsync-with-helper-20261102T161847+0700.png` | B | KEEP | 2026-11-02T16:19:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pre-ha-backup-20261102T152811+0700.json` | B | KEEP | 2026-11-02T15:28:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-pre-ha-backup-20261102T152811+0700.png` | B | KEEP | 2026-11-02T15:28:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-sync-after-rules-20261102T153822+0700.json` | B | KEEP | 2026-11-02T15:38:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-sync-after-rules-20261102T153822+0700.png` | B | KEEP | 2026-11-02T15:38:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-sync-https-api-20261102T154234+0700.json` | B | KEEP | 2026-11-02T15:42:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/primary-sync-https-api-20261102T154234+0700.png` | B | KEEP | 2026-11-02T15:42:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-alias-and-pfsync-persisted-20261102T162607+0700.json` | B | KEEP | 2026-11-02T16:26:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-alias-and-pfsync-persisted-20261102T162607+0700.png` | B | KEEP | 2026-11-02T16:26:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-cancel-incomplete-transfer-20261102T154407+0700.json` | B | KEEP | 2026-11-02T15:44:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-cancel-incomplete-transfer-20261102T154407+0700.png` | B | KEEP | 2026-11-02T15:44:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-config-api-probe-20261102T152739+0700.json` | B | KEEP | 2026-11-02T15:27:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-config-api-probe-20261102T152739+0700.png` | B | KEEP | 2026-11-02T15:27:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-config-backup-20261102T151606+0700.json` | B | KEEP | 2026-11-02T15:16:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-config-backup-20261102T151606+0700.png` | B | KEEP | 2026-11-02T15:16:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-current-20261102T151529+0700.json` | B | KEEP | 2026-11-02T15:15:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-current-20261102T151529+0700.png` | B | KEEP | 2026-11-02T15:15:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-disk-boot-check-20261102T161149+0700.json` | B | KEEP | 2026-11-02T16:11:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-disk-boot-check-20261102T161149+0700.png` | B | KEEP | 2026-11-02T16:11:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-disk-config-ro-20261102T152049+0700.json` | B | KEEP | 2026-11-02T15:21:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-disk-config-ro-20261102T152049+0700.png` | B | KEEP | 2026-11-02T15:21:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-disk-current-20261102T151821+0700.json` | B | KEEP | 2026-11-02T15:18:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-disk-current-20261102T151821+0700.png` | B | KEEP | 2026-11-02T15:18:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-graceful-poweroff-request-20261102T160747+0700.json` | B | KEEP | 2026-11-02T16:07:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-graceful-poweroff-request-20261102T160747+0700.png` | B | KEEP | 2026-11-02T16:07:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-ha-rules-applied-20261102T153803+0700.json` | B | KEEP | 2026-11-02T15:38:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-ha-rules-applied-20261102T153803+0700.png` | B | KEEP | 2026-11-02T15:38:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-ha-saved-park-request-20261102T165009+0700.json` | B | KEEP | 2026-11-02T16:50:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-ha-saved-park-request-20261102T165009+0700.png` | B | KEEP | 2026-11-02T16:50:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-installed-auth-shell-20261102T161335+0700.json` | B | KEEP | 2026-11-02T16:13:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-installed-auth-shell-20261102T161335+0700.png` | B | KEEP | 2026-11-02T16:13:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-installed-config-readonly-20261102T152006+0700.json` | B | KEEP | 2026-11-02T15:20:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-installed-config-readonly-20261102T152006+0700.png` | B | KEEP | 2026-11-02T15:20:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-installed-disk-backup.json` | B | KEEP | 2026-11-02T16:09:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-live-vs-disk-interfaces-20261102T152238+0700.json` | B | KEEP | 2026-11-02T15:22:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-live-vs-disk-interfaces-20261102T152238+0700.png` | B | KEEP | 2026-11-02T15:22:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-preserved-on-disk-20261102T160608+0700.json` | B | KEEP | 2026-11-02T16:06:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-preserved-on-disk-20261102T160608+0700.png` | B | KEEP | 2026-11-02T16:06:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0001.txt` | B | KEEP | 2026-11-02T15:41:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0002.txt` | B | KEEP | 2026-11-02T15:41:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0003.txt` | B | KEEP | 2026-11-02T15:59:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0004.txt` | B | KEEP | 2026-11-02T15:59:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0005.txt` | B | KEEP | 2026-11-02T16:00:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0006.txt` | B | KEEP | 2026-11-02T16:01:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0007.txt` | B | KEEP | 2026-11-02T16:01:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0008.txt` | B | KEEP | 2026-11-02T16:02:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0009.txt` | B | KEEP | 2026-11-02T16:03:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/command-0010.txt` | B | KEEP | 2026-11-02T16:03:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job1-20261102T154112+0700.json` | B | KEEP | 2026-11-02T15:41:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job1-20261102T154112+0700.png` | B | KEEP | 2026-11-02T15:41:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job10-20261102T160349+0700.json` | B | KEEP | 2026-11-02T16:03:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job10-20261102T160349+0700.png` | B | KEEP | 2026-11-02T16:03:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job2-20261102T154119+0700.json` | B | KEEP | 2026-11-02T15:41:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job2-20261102T154119+0700.png` | B | KEEP | 2026-11-02T15:41:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job3-20261102T155942+0700.json` | B | KEEP | 2026-11-02T15:59:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job3-20261102T155942+0700.png` | B | KEEP | 2026-11-02T15:59:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job4-20261102T155950+0700.json` | B | KEEP | 2026-11-02T16:00:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job4-20261102T155950+0700.png` | B | KEEP | 2026-11-02T16:00:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job5-20261102T160031+0700.json` | B | KEEP | 2026-11-02T16:01:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job5-20261102T160031+0700.png` | B | KEEP | 2026-11-02T16:01:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job6-20261102T160114+0700.json` | B | KEEP | 2026-11-02T16:01:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job6-20261102T160114+0700.png` | B | KEEP | 2026-11-02T16:01:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job7-20261102T160157+0700.json` | B | KEEP | 2026-11-02T16:02:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job7-20261102T160157+0700.png` | B | KEEP | 2026-11-02T16:02:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job8-20261102T160240+0700.json` | B | KEEP | 2026-11-02T16:03:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job8-20261102T160240+0700.png` | B | KEEP | 2026-11-02T16:03:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job9-20261102T160317+0700.json` | B | KEEP | 2026-11-02T16:03:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-network-stage/job9-20261102T160317+0700.png` | B | KEEP | 2026-11-02T16:03:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-persistent-config-backup-20261102T152143+0700.json` | B | KEEP | 2026-11-02T15:21:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-persistent-config-backup-20261102T152143+0700.png` | B | KEEP | 2026-11-02T15:21:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-pfsync-native-20261102T161521+0700.json` | B | KEEP | 2026-11-02T16:15:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-pfsync-native-20261102T161521+0700.png` | B | KEEP | 2026-11-02T16:15:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-pfsync-peer-test-20261102T162222+0700.json` | B | KEEP | 2026-11-02T16:22:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-pfsync-peer-test-20261102T162222+0700.png` | B | KEEP | 2026-11-02T16:22:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-pfsync-version-persisted-20261102T163820+0700.json` | B | KEEP | 2026-11-02T16:38:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-pfsync-version-persisted-20261102T163820+0700.png` | B | KEEP | 2026-11-02T16:38:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-pfsync-with-helper-20261102T162043+0700.json` | B | KEEP | 2026-11-02T16:21:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-pfsync-with-helper-20261102T162043+0700.png` | B | KEEP | 2026-11-02T16:21:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-root-shell-20261102T151554+0700.json` | B | KEEP | 2026-11-02T15:15:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-root-shell-20261102T151554+0700.png` | B | KEEP | 2026-11-02T15:15:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-sync-after-rules-20261102T154033+0700.json` | B | KEEP | 2026-11-02T15:40:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-sync-after-rules-20261102T154033+0700.png` | B | KEEP | 2026-11-02T15:40:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-sync-nics-20261102T151713+0700.json` | B | KEEP | 2026-11-02T15:17:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/secondary-sync-nics-20261102T151713+0700.png` | B | KEEP | 2026-11-02T15:17:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/sync-before-rules-20261102T152345+0700.json` | B | KEEP | 2026-11-02T15:23:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/sync-before-rules-20261102T152345+0700.png` | B | KEEP | 2026-11-02T15:23:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/sync-pretest-result-20261102T152604+0700.json` | B | KEEP | 2026-11-02T15:26:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/sync-pretest-result-20261102T152604+0700.png` | B | KEEP | 2026-11-02T15:26:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-alias-scope-option-20261102T162522+0700.json` | B | KEEP | 2026-11-02T16:25:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-alias-scope-option-20261102T162522+0700.png` | B | KEEP | 2026-11-02T16:25:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-alias-sync-request-20261102T163806+0700.json` | B | KEEP | 2026-11-02T16:38:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-alias-sync-request-20261102T163806+0700.png` | B | KEEP | 2026-11-02T16:38:19+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-authentication-result-20261102T163600+0700.json` | B | KEEP | 2026-11-02T16:36:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-authentication-result-20261102T163600+0700.png` | B | KEEP | 2026-11-02T16:36:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-backend-fields-20261102T162249+0700.json` | B | KEEP | 2026-11-02T16:22:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-backend-fields-20261102T162249+0700.png` | B | KEEP | 2026-11-02T16:22:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-cleanup-sync-request-20261102T164434+0700.json` | B | KEEP | 2026-11-02T16:44:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-cleanup-sync-request-20261102T164434+0700.png` | B | KEEP | 2026-11-02T16:44:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-probe-alias-created-20261102T163703+0700.json` | B | KEEP | 2026-11-02T16:37:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-probe-alias-created-20261102T163703+0700.png` | B | KEEP | 2026-11-02T16:37:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-probe-cleanup-source-20261102T164234+0700.json` | B | KEEP | 2026-11-02T16:42:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-probe-cleanup-source-20261102T164234+0700.png` | B | KEEP | 2026-11-02T16:42:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-source-protected-check-20261102T163928+0700.json` | B | KEEP | 2026-11-02T16:40:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-source-protected-check-20261102T163928+0700.png` | B | KEEP | 2026-11-02T16:40:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/command-0001.txt` | B | KEEP | 2026-11-02T16:29:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/command-0002.txt` | B | KEEP | 2026-11-02T16:29:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/command-0003.txt` | B | KEEP | 2026-11-02T16:29:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/command-0004.txt` | B | KEEP | 2026-11-02T16:30:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/command-0005.txt` | B | KEEP | 2026-11-02T16:31:26+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/command-0006.txt` | B | KEEP | 2026-11-02T16:31:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/command-0007.txt` | B | KEEP | 2026-11-02T16:32:37+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job1-20261102T162908+0700.json` | B | KEEP | 2026-11-02T16:29:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job1-20261102T162908+0700.png` | B | KEEP | 2026-11-02T16:29:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job2-20261102T162917+0700.json` | B | KEEP | 2026-11-02T16:29:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job2-20261102T162917+0700.png` | B | KEEP | 2026-11-02T16:29:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job3-20261102T162958+0700.json` | B | KEEP | 2026-11-02T16:30:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job3-20261102T162958+0700.png` | B | KEEP | 2026-11-02T16:30:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job4-20261102T163040+0700.json` | B | KEEP | 2026-11-02T16:31:26+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job4-20261102T163040+0700.png` | B | KEEP | 2026-11-02T16:31:26+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job5-20261102T163126+0700.json` | B | KEEP | 2026-11-02T16:31:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job5-20261102T163126+0700.png` | B | KEEP | 2026-11-02T16:31:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job6-20261102T163151+0700.json` | B | KEEP | 2026-11-02T16:32:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job6-20261102T163151+0700.png` | B | KEEP | 2026-11-02T16:32:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job7-20261102T163237+0700.json` | B | KEEP | 2026-11-02T16:32:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-stage/job7-20261102T163237+0700.png` | B | KEEP | 2026-11-02T16:32:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-target-cleanup-verified-20261102T164809+0700.json` | B | KEEP | 2026-11-02T16:48:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-target-cleanup-verified-20261102T164809+0700.png` | B | KEEP | 2026-11-02T16:48:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-target-probe-check-20261102T163938+0700.json` | B | KEEP | 2026-11-02T16:40:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/resume-20261102/xmlrpc-target-probe-check-20261102T163938+0700.png` | B | KEEP | 2026-11-02T16:40:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/runtime-primary/primary-runtime-state-20261103T210805+0700.json` | B/G | KEEP + REVIEW | 2026-11-03T21:08:20+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/runtime-primary/primary-runtime-state-20261103T210805+0700.png` | B/G | KEEP + REVIEW | 2026-11-03T21:08:20+07:00 | Trace Nhóm2 chưa chứng minh CARP thành công |
| `docs/evidence/M3/secondary-20261102/secondary-boot-initial-20261102T130641+0700.json` | B | KEEP | 2026-11-02T13:06:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-boot-initial-20261102T130641+0700.png` | B | KEEP | 2026-11-02T13:06:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-boot-later-20261102T130831+0700.json` | B | KEEP | 2026-11-02T13:08:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-boot-later-20261102T130831+0700.png` | B | KEEP | 2026-11-02T13:08:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-boot-progress-20261102T130701+0700.json` | B | KEEP | 2026-11-02T13:07:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-boot-progress-20261102T130701+0700.png` | B | KEEP | 2026-11-02T13:07:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-copy-progress-20261102T131758+0700.json` | B | KEEP | 2026-11-02T13:18:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-copy-progress-20261102T131758+0700.png` | B | KEEP | 2026-11-02T13:18:00+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-copy-progress2-20261102T132055+0700.json` | B | KEEP | 2026-11-02T13:20:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-copy-progress2-20261102T132055+0700.png` | B | KEEP | 2026-11-02T13:20:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-copy-stage-20261102T132450+0700.json` | B | KEEP | 2026-11-02T13:24:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-copy-stage-20261102T132450+0700.png` | B | KEEP | 2026-11-02T13:24:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-disk-ready-20261102T131455+0700.json` | B | KEEP | 2026-11-02T13:14:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-disk-ready-20261102T131455+0700.png` | B | KEEP | 2026-11-02T13:14:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-check-20261102T133830+0700.json` | B | KEEP | 2026-11-02T13:38:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-check-20261102T133830+0700.png` | B | KEEP | 2026-11-02T13:38:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-completion-screen-20261102T133150+0700.json` | B | KEEP | 2026-11-02T13:31:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-completion-screen-20261102T133150+0700.png` | B | KEEP | 2026-11-02T13:31:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-disk-20261102T131418+0700.json` | B | KEEP | 2026-11-02T13:14:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-disk-20261102T131418+0700.png` | B | KEEP | 2026-11-02T13:14:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-next-20261102T134536+0700.json` | B | KEEP | 2026-11-02T13:45:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-next-20261102T134536+0700.png` | B | KEEP | 2026-11-02T13:45:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-options-20261102T131405+0700.json` | B | KEEP | 2026-11-02T13:14:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-options-20261102T131405+0700.png` | B | KEEP | 2026-11-02T13:14:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-progress-20261102T131648+0700.json` | B | KEEP | 2026-11-02T13:16:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-progress-20261102T131648+0700.png` | B | KEEP | 2026-11-02T13:16:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-stage-late-20261102T132759+0700.json` | B | KEEP | 2026-11-02T13:28:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-stage-late-20261102T132759+0700.png` | B | KEEP | 2026-11-02T13:28:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-started-20261102T131518+0700.json` | B | KEEP | 2026-11-02T13:15:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-started-20261102T131518+0700.png` | B | KEEP | 2026-11-02T13:15:23+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-status-20261102T133348+0700.json` | B | KEEP | 2026-11-02T13:33:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-install-status-20261102T133348+0700.png` | B | KEEP | 2026-11-02T13:33:50+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-installer-keymap-20261102T131308+0700.json` | B | KEEP | 2026-11-02T13:13:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-installer-keymap-20261102T131308+0700.png` | B | KEEP | 2026-11-02T13:13:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-installer-login-screen-20261102T131124+0700.json` | B | KEEP | 2026-11-02T13:11:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-installer-login-screen-20261102T131124+0700.png` | B | KEEP | 2026-11-02T13:11:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-keymap-ready-20261102T131351+0700.json` | B | KEEP | 2026-11-02T13:13:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-keymap-ready-20261102T131351+0700.png` | B | KEEP | 2026-11-02T13:13:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-live-login-20261102T130949+0700.json` | B | KEEP | 2026-11-02T13:09:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-live-login-20261102T130949+0700.png` | B | KEEP | 2026-11-02T13:09:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-live-ready-20261102T130907+0700.json` | B | KEEP | 2026-11-02T13:09:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-live-ready-20261102T130907+0700.png` | B | KEEP | 2026-11-02T13:09:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-services-status-20261102T131227+0700.json` | B | KEEP | 2026-11-02T13:12:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-services-status-20261102T131227+0700.png` | B | KEEP | 2026-11-02T13:12:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-write-confirmation-20261102T131506+0700.json` | B | KEEP | 2026-11-02T13:15:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/secondary-20261102/secondary-write-confirmation-20261102T131506+0700.png` | B | KEEP | 2026-11-02T13:15:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M3/temp-carp-check/cmd.txt` | B | KEEP | 2026-11-03T19:05:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/live-mirror-frames.json` | B | KEEP | 2026-11-02T17:01:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-current-20261102T151650+0700.json` | B | KEEP | 2026-11-02T15:16:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-current-20261102T151650+0700.png` | B | KEEP | 2026-11-02T15:16:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-export-after-marker-20261102T170219+0700.json` | B | KEEP | 2026-11-02T17:02:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-export-after-marker-20261102T170219+0700.png` | B | KEEP | 2026-11-02T17:02:53+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-export-before-marker-20261102T170041+0700.json` | B | KEEP | 2026-11-02T17:01:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-export-before-marker-20261102T170041+0700.png` | B | KEEP | 2026-11-02T17:01:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-graceful-shutdown-20261102T151704+0700.json` | B | KEEP | 2026-11-02T15:17:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-graceful-shutdown-20261102T151704+0700.png` | B | KEEP | 2026-11-02T15:17:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-live-boot-check-20261102T165437+0700.json` | B | KEEP | 2026-11-02T16:54:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-live-boot-check-20261102T165437+0700.png` | B | KEEP | 2026-11-02T16:54:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-live-evidence-saved-park-20261102T170716+0700.json` | B | KEEP | 2026-11-02T17:07:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-live-evidence-saved-park-20261102T170716+0700.png` | B | KEEP | 2026-11-02T17:07:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-public-after-marker.json` | B | KEEP | 2026-11-02T17:02:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-public-before-marker.json` | B | KEEP | 2026-11-02T17:01:16+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-ready-check-20261102T165631+0700.json` | B | KEEP | 2026-11-02T16:56:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/sensor-ready-check-20261102T165631+0700.png` | B | KEEP | 2026-11-02T16:56:33+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/suricata-real-alert-replay.jsonl` | B | KEEP | 2026-11-02T17:07:06+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/resume-20261102/vpcs-inventory.json` | B | KEEP | 2026-11-02T16:56:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/collect-4-verified-reply.json` | B | KEEP | 2026-11-02T13:34:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/command-0001.txt` | B | KEEP | 2026-11-02T13:31:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/command-0002.txt` | B | KEEP | 2026-11-02T13:31:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/command-0003.txt` | B | KEEP | 2026-11-02T13:31:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/command-0004.txt` | B | KEEP | 2026-11-02T13:32:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/command-0005.txt` | B | KEEP | 2026-11-02T13:32:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/command-0006.txt` | B | KEEP | 2026-11-02T13:33:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/command-0007.txt` | B | KEEP | 2026-11-02T13:33:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/command-0008.txt` | B | KEEP | 2026-11-02T13:34:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job1-20261102T133102+0700.json` | B | KEEP | 2026-11-02T13:31:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job1-20261102T133102+0700.png` | B | KEEP | 2026-11-02T13:31:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job2-20261102T133110+0700.json` | B | KEEP | 2026-11-02T13:31:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job2-20261102T133110+0700.png` | B | KEEP | 2026-11-02T13:31:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job3-20261102T133155+0700.json` | B | KEEP | 2026-11-02T13:32:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job3-20261102T133155+0700.png` | B | KEEP | 2026-11-02T13:32:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job4-20261102T133217+0700.json` | B | KEEP | 2026-11-02T13:32:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job4-20261102T133217+0700.png` | B | KEEP | 2026-11-02T13:32:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job5-20261102T133251+0700.json` | B | KEEP | 2026-11-02T13:33:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job5-20261102T133251+0700.png` | B | KEEP | 2026-11-02T13:33:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job6-20261102T133330+0700.json` | B | KEEP | 2026-11-02T13:33:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job6-20261102T133330+0700.png` | B | KEEP | 2026-11-02T13:33:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job7-20261102T133347+0700.json` | B | KEEP | 2026-11-02T13:34:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job7-20261102T133347+0700.png` | B | KEEP | 2026-11-02T13:34:05+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job8-20261102T133405+0700.json` | B | KEEP | 2026-11-02T13:34:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/console-export/job8-20261102T133405+0700.png` | B | KEEP | 2026-11-02T13:34:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/linux-seed-preparation.json` | B | KEEP | 2026-11-02T13:16:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/offline-bundle.json` | B | KEEP | 2026-11-02T13:12:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-boot-initial-20261102T132019+0700.json` | B | KEEP | 2026-11-02T13:20:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-boot-initial-20261102T132019+0700.png` | B | KEEP | 2026-11-02T13:20:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-bootstrap-stage-20261102T132359+0700.json` | B | KEEP | 2026-11-02T13:24:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-bootstrap-stage-20261102T132359+0700.png` | B | KEEP | 2026-11-02T13:24:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-cloud-init-status-20261102T132137+0700.json` | B | KEEP | 2026-11-02T13:21:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-cloud-init-status-20261102T132137+0700.png` | B | KEEP | 2026-11-02T13:21:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-configuration-public.json` | B | KEEP | 2026-11-02T13:34:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-configure-result-20261102T132952+0700.json` | B | KEEP | 2026-11-02T13:29:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-configure-result-20261102T132952+0700.png` | B | KEEP | 2026-11-02T13:29:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-console-prompt-20261102T132426+0700.json` | B | KEEP | 2026-11-02T13:24:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-console-prompt-20261102T132426+0700.png` | B | KEEP | 2026-11-02T13:24:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-dependency-error-20261102T132506+0700.json` | B | KEEP | 2026-11-02T13:25:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-dependency-error-20261102T132506+0700.png` | B | KEEP | 2026-11-02T13:25:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-install-error-20261102T132442+0700.json` | B | KEEP | 2026-11-02T13:24:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-install-error-20261102T132442+0700.png` | B | KEEP | 2026-11-02T13:24:49+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-install-resume-status-20261102T132804+0700.json` | B | KEEP | 2026-11-02T13:28:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-install-resume-status-20261102T132804+0700.png` | B | KEEP | 2026-11-02T13:28:07+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-local-package-resume-20261102T132622+0700.json` | B | KEEP | 2026-11-02T13:26:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M4/topology-first-20261102/sensor-local-package-resume-20261102T132622+0700.png` | B | KEEP | 2026-11-02T13:26:54+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/actual-suricata-alerts-20261102T205713+0700.json` | B | KEEP | 2026-11-02T20:57:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/actual-suricata-alerts-20261102T205713+0700.png` | B | KEEP | 2026-11-02T20:57:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/actual-suricata-alerts.txt` | B | KEEP | 2026-11-02T20:57:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/apply-persistent-timeout-20261102T204302+0700.json` | B | KEEP | 2026-11-02T20:43:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/apply-persistent-timeout-20261102T204302+0700.png` | B | KEEP | 2026-11-02T20:43:17+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/backup-systemd-20261102T204235+0700.json` | B | KEEP | 2026-11-02T20:42:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/backup-systemd-20261102T204235+0700.png` | B | KEEP | 2026-11-02T20:42:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/backup-systemd.txt` | B | KEEP | 2026-11-02T20:42:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/boot-observation-20261102T203457+0700.json` | B | KEEP | 2026-11-02T20:35:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/boot-observation-20261102T203457+0700.png` | B | KEEP | 2026-11-02T20:35:01+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/boot-ready-20261102T203556+0700.json` | B | KEEP | 2026-11-02T20:35:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/boot-ready-20261102T203556+0700.png` | B | KEEP | 2026-11-02T20:35:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/decoded-field-validation.json` | B | KEEP | 2026-11-02T20:59:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/evidence-index-final.csv` | B | KEEP | 2026-11-02T21:02:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/evidence-index-final.md` | B | KEEP | 2026-11-02T21:02:43+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/inventory-initial.json` | B | KEEP | 2026-11-02T20:33:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/inventory-running.json` | B | KEEP | 2026-11-02T20:45:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/logtest-real.txt` | B | KEEP | 2026-11-02T20:47:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/manager-components-packages-20261102T204613+0700.json` | B | KEEP | 2026-11-02T20:46:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/manager-components-packages-20261102T204613+0700.png` | B | KEEP | 2026-11-02T20:46:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/manager-components.txt` | B | KEEP | 2026-11-02T20:46:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer-inspect-20261102T205612+0700.json` | B | KEEP | 2026-11-02T20:56:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer-inspect-20261102T205612+0700.png` | B | KEEP | 2026-11-02T20:56:15+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/command-0001.txt` | B | KEEP | 2026-11-02T20:48:35+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/command-0002.txt` | B | KEEP | 2026-11-02T20:48:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/command-0003.txt` | B | KEEP | 2026-11-02T20:49:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/command-0004.txt` | B | KEEP | 2026-11-02T20:49:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/command-0005.txt` | B | KEEP | 2026-11-02T20:56:32+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/command-0006.txt` | B | KEEP | 2026-11-02T20:58:18+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/command-0007.txt` | B | KEEP | 2026-11-02T20:58:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job1-20261102T204835+0700.json` | B | KEEP | 2026-11-02T20:48:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job1-20261102T204835+0700.png` | B | KEEP | 2026-11-02T20:48:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job2-20261102T204844+0700.json` | B | KEEP | 2026-11-02T20:49:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job2-20261102T204844+0700.png` | B | KEEP | 2026-11-02T20:49:25+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job3-20261102T204925+0700.json` | B | KEEP | 2026-11-02T20:49:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job3-20261102T204925+0700.png` | B | KEEP | 2026-11-02T20:49:57+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job5-20261102T205632+0700.json` | B | KEEP | 2026-11-02T20:56:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job5-20261102T205632+0700.png` | B | KEEP | 2026-11-02T20:56:42+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job6-20261102T205818+0700.json` | B | KEEP | 2026-11-02T20:58:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job6-20261102T205818+0700.png` | B | KEEP | 2026-11-02T20:58:47+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job7-20261102T205847+0700.json` | B | KEEP | 2026-11-02T20:58:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/native-transfer/job7-20261102T205847+0700.png` | B | KEEP | 2026-11-02T20:58:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/privilege-check.txt` | B | KEEP | 2026-11-02T20:36:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/privilege-service-20261102T203611+0700.json` | B | KEEP | 2026-11-02T20:36:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/privilege-service-20261102T203611+0700.png` | B | KEEP | 2026-11-02T20:36:20+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/real-event-provenance.json` | B | KEEP | 2026-11-02T20:49:34+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/real-logtest-diagnostic-20261102T204714+0700.json` | B | KEEP | 2026-11-02T20:47:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/real-logtest-diagnostic-20261102T204714+0700.png` | B | KEEP | 2026-11-02T20:47:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/real-replay-verified-20261102T205956+0700.json` | B | KEEP | 2026-11-02T21:00:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/real-replay-verified-20261102T205956+0700.png` | B | KEEP | 2026-11-02T21:00:24+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/real-summary.txt` | B | KEEP | 2026-11-02T20:59:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/seed-readonly-20261102T204408+0700.json` | B | KEEP | 2026-11-02T20:44:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/seed-readonly-20261102T204408+0700.png` | B | KEEP | 2026-11-02T20:44:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/seed-readonly.txt` | B | KEEP | 2026-11-02T20:44:08+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/soc-audit-04b085ca9029.json` | B | KEEP | 2026-11-02T20:41:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/soc-audit-141cfe755e9d.json` | B | KEEP | 2026-11-02T20:44:58+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/soc-real-fc29ab1fc31a.json` | B | KEEP | 2026-11-02T20:46:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/soc-real-native-fc29ab1fc31a.json` | B | KEEP | 2026-11-02T20:56:48+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/soc-real-native-fields-fc29ab1fc31a.json` | B | KEEP | 2026-11-02T20:59:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/soc-synthetic-fd76fcab059c.json` | B | KEEP | 2026-11-02T20:45:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/synthetic-collection-verified-20261102T210111+0700.json` | B | KEEP | 2026-11-02T21:01:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/synthetic-collection-verified-20261102T210111+0700.png` | B | KEEP | 2026-11-02T21:01:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/synthetic-summary.txt` | B | KEEP | 2026-11-02T21:01:11+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/timeout-diagnostic-20261102T204159+0700.json` | B | KEEP | 2026-11-02T20:42:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/timeout-diagnostic-20261102T204159+0700.png` | B | KEEP | 2026-11-02T20:42:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/timeout-diagnostic.txt` | B | KEEP | 2026-11-02T20:41:59+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/timeout-effective-20261102T204330+0700.json` | B | KEEP | 2026-11-02T20:43:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/timeout-effective-20261102T204330+0700.png` | B | KEEP | 2026-11-02T20:43:44+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/timeout-effective.txt` | B | KEEP | 2026-11-02T20:43:30+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0001.txt` | B | KEEP | 2026-11-02T20:36:31+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0002.txt` | B | KEEP | 2026-11-02T20:36:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0003.txt` | B | KEEP | 2026-11-02T20:37:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0004.txt` | B | KEEP | 2026-11-02T20:38:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0005.txt` | B | KEEP | 2026-11-02T20:38:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0006.txt` | B | KEEP | 2026-11-02T20:39:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0007.txt` | B | KEEP | 2026-11-02T20:40:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0008.txt` | B | KEEP | 2026-11-02T20:40:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0009.txt` | B | KEEP | 2026-11-02T20:41:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0010.txt` | B | KEEP | 2026-11-02T20:44:41+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0011.txt` | B | KEEP | 2026-11-02T20:45:04+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/command-0012.txt` | B | KEEP | 2026-11-02T20:45:40+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job1-20261102T203632+0700.json` | B | KEEP | 2026-11-02T20:36:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job1-20261102T203632+0700.png` | B | KEEP | 2026-11-02T20:36:39+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job10-20261102T204441+0700.json` | B | KEEP | 2026-11-02T20:44:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job10-20261102T204441+0700.png` | B | KEEP | 2026-11-02T20:44:51+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job11-20261102T204504+0700.json` | B | KEEP | 2026-11-02T20:45:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job11-20261102T204504+0700.png` | B | KEEP | 2026-11-02T20:45:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job12-20261102T204540+0700.json` | B | KEEP | 2026-11-02T20:45:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job12-20261102T204540+0700.png` | B | KEEP | 2026-11-02T20:45:52+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job2-20261102T203639+0700.json` | B | KEEP | 2026-11-02T20:37:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job2-20261102T203639+0700.png` | B | KEEP | 2026-11-02T20:37:21+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job3-20261102T203721+0700.json` | B | KEEP | 2026-11-02T20:38:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job3-20261102T203721+0700.png` | B | KEEP | 2026-11-02T20:38:03+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job4-20261102T203803+0700.json` | B | KEEP | 2026-11-02T20:38:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job4-20261102T203803+0700.png` | B | KEEP | 2026-11-02T20:38:45+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job5-20261102T203846+0700.json` | B | KEEP | 2026-11-02T20:39:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job5-20261102T203846+0700.png` | B | KEEP | 2026-11-02T20:39:29+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job6-20261102T203929+0700.json` | B | KEEP | 2026-11-02T20:40:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job6-20261102T203929+0700.png` | B | KEEP | 2026-11-02T20:40:13+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job7-20261102T204013+0700.json` | B | KEEP | 2026-11-02T20:40:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job7-20261102T204013+0700.png` | B | KEEP | 2026-11-02T20:40:55+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job8-20261102T204055+0700.json` | B | KEEP | 2026-11-02T20:41:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job8-20261102T204055+0700.png` | B | KEEP | 2026-11-02T20:41:27+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job9-20261102T204127+0700.json` | B | KEEP | 2026-11-02T20:41:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/transfer/job9-20261102T204127+0700.png` | B | KEEP | 2026-11-02T20:41:38+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/verifier-executed-v1.py` | B | KEEP | 2026-11-02T20:35:56+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/windows-memory.json` | B | KEEP | 2026-11-02T20:38:09+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/continuation-20261102/write-timeout.txt` | B | KEEP | 2026-11-02T20:43:02+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/data-center-bootstrap-public.json` | B | KEEP | 2026-11-02T17:14:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/dc-first-boot-20261102T171319+0700.json` | B | KEEP | 2026-11-02T17:13:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/dc-first-boot-20261102T171319+0700.png` | B | KEEP | 2026-11-02T17:13:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/dmz-bootstrap-public.json` | B | KEEP | 2026-11-02T17:14:14+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/dmz-first-boot-20261102T171319+0700.json` | B | KEEP | 2026-11-02T17:13:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/dmz-first-boot-20261102T171319+0700.png` | B | KEEP | 2026-11-02T17:13:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/service-seed-preparation.json` | B | KEEP | 2026-11-02T17:09:36+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/wazuh-first-boot-20261102T171319+0700.json` | B | KEEP | 2026-11-02T17:13:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/wazuh-first-boot-20261102T171319+0700.png` | B | KEEP | 2026-11-02T17:13:22+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/wazuh-manager-offline-prepared.json` | B | KEEP | 2026-11-02T16:03:12+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/wazuh-package-install-progress-20261102T171701+0700.json` | B | KEEP | 2026-11-02T17:17:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `docs/evidence/M5/resume-20261102/wazuh-package-install-progress-20261102T171701+0700.png` | B | KEEP | 2026-11-02T17:17:10+07:00 | Bảo toàn lịch sử; chưa kiểm nội dung toàn bộ |
| `primary_recovery_probe.txt` | D/F/H | MOVE hoặc DELETE LATER | 2026-11-03T21:06:58+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; rà đường xuất dữ liệu |
| `primary_runtime_probe.txt` | D/F/H | MOVE hoặc DELETE LATER | 2026-11-03T21:08:04+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; rà đường xuất dữ liệu |
| `temp/primary_runtime_probe.ps1` | D/G | REVIEW → DELETE LATER | 2026-11-03T21:10:16+07:00 | Wrapper debug console; không tự chạy lại |
| `temp/recover_primary_probe.ps1` | D/G | REVIEW → DELETE LATER | 2026-11-03T21:10:16+07:00 | Wrapper debug console; không tự chạy lại |
| `tmp_carp_probe.txt` | D/F/H | MOVE hoặc DELETE LATER | 2026-11-03T19:30:12+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; rà đường xuất dữ liệu |
| `tmp_carp_verify_primary.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:34:03+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_carp_verify_secondary.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:34:43+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_config_xml_inspect_primary.txt` | D/F/H | MOVE hoặc DELETE LATER | 2026-11-03T19:44:06+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; rà đường xuất dữ liệu |
| `tmp_console_test.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:29:03+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_echo_test.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T20:04:20+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_m3_group2_primary_apply_probe.txt` | D/F/G/H | MOVE hoặc DELETE LATER | 2026-11-03T19:24:49+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; có thể đổi runtime; rà đường xuất dữ liệu |
| `tmp_m3_group2_primary_carp_cmds.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:27:25+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_m3_group2_primary_cmd.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:19:03+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_m3_group2_primary_status.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:23:25+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_m3_group2_xml_shape.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:25:46+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_absolute_probe.txt` | D/F/H | MOVE hoặc DELETE LATER | 2026-11-03T20:31:36+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; rà đường xuất dữ liệu |
| `tmp_primary_carp_apply.txt` | D/F/G | MOVE hoặc DELETE LATER | 2026-11-03T19:32:08+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; có thể đổi runtime |
| `tmp_primary_carp_setup.txt` | D/F/G | MOVE hoặc DELETE LATER | 2026-11-03T20:01:05+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; có thể đổi runtime |
| `tmp_primary_carp_state.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:47:09+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_hostname.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T20:10:17+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_hostname_test.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T20:31:36+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_lowercase_test.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T20:10:02+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_ls.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T20:21:20+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_recovery_check.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T20:31:36+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_reload_check.txt` | D/F/G | MOVE hoặc DELETE LATER | 2026-11-03T19:52:29+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; có thể đổi runtime |
| `tmp_primary_reload_single.txt` | D/F/G | MOVE hoặc DELETE LATER | 2026-11-03T19:58:35+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; có thể đổi runtime |
| `tmp_primary_root_login.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T20:23:47+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_shell_probe.txt` | D/F/H | MOVE hoặc DELETE LATER | 2026-11-03T20:23:47+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; rà đường xuất dữ liệu |
| `tmp_primary_shell_probe_csh.txt` | D/F/H | MOVE hoặc DELETE LATER | 2026-11-03T20:31:36+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; rà đường xuất dữ liệu |
| `tmp_primary_shell_verify.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T20:09:00+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_state.txt` | D/F | MOVE hoặc DELETE LATER | 2026-11-03T19:50:34+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng |
| `tmp_primary_vlan30_test.txt` | D/F/G | MOVE hoặc DELETE LATER | 2026-11-03T20:03:39+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; có thể đổi runtime |
| `tmp_primary_vlan_create.txt` | D/F/G | MOVE hoặc DELETE LATER | 2026-11-03T19:59:13+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; có thể đổi runtime |
| `tmp_secondary_carp_apply.txt` | D/F/G | MOVE hoặc DELETE LATER | 2026-11-03T19:32:58+07:00 | Lệnh thử ở root; lưu trace rồi mới dọn theo duyệt riêng; có thể đổi runtime |

### 8.3. Danh mục ảnh Nhóm2 và metadata

29 ảnh có sẵn:18 ảnh rời +9 Group2a +2 recovery/runtime. Hash MATCH chỉ chứng minh file khớp metadata lưu kèm; không xác thực độc lập kết quả kỹ thuật. REVIEW là chưa xem thủ công riêng từng ảnh.

| Tên/path | Nội dung/kết luận | Thời điểm thu kết thúc UTC+07:00 | Hash metadata | Vị trí báo cáo |
|---|---|---|---|---|
| `docs/evidence/M3/group2a-apply-20261103/console-hello-20261103T192904+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:29:11.658720+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-apply-20261103T193209+0700.png` | Primary lỗi redirect; Secondary chỉ dòng lệnh, chưa có kết quả thành công | 2026-11-03T19:32:27.888768+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-commands-20261103T192725+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:27:49.023199+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-probe-20261103T192450+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:25:12.149107+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/group2a-apply-20261103/primary-carp-verify-20261103T193403+0700.png` | Không có output CARP hợp lệ; Secondary lỗi redirect | 2026-11-03T19:34:23.247040+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/group2a-apply-20261103/primary-status-20261103T192325+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:23:33.968110+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/group2a-apply-20261103/primary-xml-shape-20261103T192547+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:26:07.925055+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/group2a-apply-20261103/secondary-carp-apply-20261103T193258+0700.png` | Primary lỗi redirect; Secondary chỉ dòng lệnh, chưa có kết quả thành công | 2026-11-03T19:33:16.235893+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/group2a-apply-20261103/secondary-carp-verify-20261103T193443+0700.png` | Không có output CARP hợp lệ; Secondary lỗi redirect | 2026-11-03T19:35:02.406276+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-absolute-probe-20261103T202600+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T20:26:28.994037+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-carp-runtime-setup-20261103T200121+0700.png` | Lỗi redirect hoặc chỉ đầu vào; không xác nhận thay runtime | 2026-11-03T20:01:38.231638+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-echo-test-20261103T200418+0700.png` | FAIL phép đọc: lệnh chữ HOA Command not found | 2026-11-03T20:04:28.535821+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-hostname-check-20261103T201034+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T20:10:41.478838+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-hostname-test-20261103T202734+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T20:27:43.002654+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-live-state-20261103T195034+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:50:57.177827+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-login-root-attempt-20261103T202219+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T20:22:27.533102+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-recovery-check-20261103T203042+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T20:30:52.431416+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-reload-abs-20261103T195757+0700.png` | FAIL đường dẫn lệnh chữ HOA, Command not found | 2026-11-03T19:58:07.961101+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-reload-check-20261103T195230+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:52:55.565325+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-reload-single-20261103T195455+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:55:11.608961+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-reload-single-20261103T195711+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T19:57:19.467359+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-shell-probe-20261103T202324+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T20:23:59.434102+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-shell-probe-csh-20261103T202447+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T20:25:17.666131+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-shell-verify-20261103T200832+0700.png` | REVIEW — chưa xác minh thủ công nội dung riêng ảnh này | 2026-11-03T20:09:04.163873+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-vlan30-create-20261103T195913+0700.png` | Lỗi redirect hoặc chỉ đầu vào; không xác nhận thay runtime | 2026-11-03T19:59:26.909158+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-vlan30-create-20261103T200255+0700.png` | Lỗi redirect hoặc chỉ đầu vào; không xác nhận thay runtime | 2026-11-03T20:03:07.303377+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/primary-vlan30-fileproof-20261103T200330+0700.png` | Lỗi redirect hoặc chỉ đầu vào; không xác nhận thay runtime | 2026-11-03T20:03:43.358209+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/recovery-check/primary-recovery-shell-20261103T210659+0700.png` | Lỗi redirect hoặc chỉ đầu vào; không xác nhận thay runtime | 2026-11-03T21:07:18.089553+07:00 | MATCH | Mục2.1 / phụ lục8.3 |
| `docs/evidence/M3/runtime-primary/primary-runtime-state-20261103T210805+0700.png` | FAIL phép đọc: lệnh chữ HOA Command not found | 2026-11-03T21:08:20.689440+07:00 | MATCH | Mục2.1 / phụ lục8.3 |

Kết quả: 29/29 PNG khớp capture.sha256. Không chỉnh sửa ảnh, không dùng tên file thay collector_time, không coi ảnh có lệnh là lệnh đã thực thi thành công.

### 8.4. Ignored sensitive files

| File/path | Trạng thái |
|---|---|
| `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/Primary-config.xml` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/Primary-config.xml.sha256` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/Primary-transport-pass.key` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/Secondary-config.xml` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/Secondary-config.xml.sha256` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/Secondary-transport-pass.key` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/transport-private.key` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1b-prerequisites-20261103/private-backups/Primary-before.xml` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1b-prerequisites-20261103/private-backups/Secondary-before.xml` | IGNORED — KEEP PRIVATE |
| `docs/evidence/M3/group1b-prerequisites-20261103/private-backups/carp-shared-secret.dpapi` | IGNORED — KEEP PRIVATE |
| `docs/evidence/eve-ng/ubuntu-image-test-config/node-config.json` | IGNORED — KEEP PRIVATE |
