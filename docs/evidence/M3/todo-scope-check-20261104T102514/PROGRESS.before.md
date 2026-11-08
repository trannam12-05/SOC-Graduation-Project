# CHECKPOINT MỚI NHẤT — M3 tới M3.2 DONE/PASS — 03/11/2026, UTC+07:00

## 0.1. Điểm tiếp quản — 2026-11-03T23:44:19+07:00

**Đọc mục này và [SOC_TO_DO.md](SOC_TO_DO.md) trước. Các checkpoint bên dưới là lịch sử, không dùng các dòng “không chuyển M3”, “Core chưa nối”, “CARP chưa apply” cũ làm trạng thái hiện tại.**

| TODO | STATUS | EVIDENCE |
|---|---|---|
| M3.1 — pfsync persistent, tự hoạt động sau reboot từng firewall | DONE/PASS lúc23:22:49+07:00 | `evidence/M3/todo-completion-20261103/M3.1-acceptance.json`; `primary-pfsync-postboot.json`, `secondary-pfsync-postboot.json` |
| M3.2 — CARP năm VLAN; Primary MASTER / Secondary BACKUP | DONE/PASS lúc23:35:30+07:00 | `evidence/M3/todo-completion-20261103/M3.2-acceptance.json`; hai JSON carp-verified, ảnh carp-proof, packet/ARP evidence |

**Đã hoàn thành tới M3.2. TODO tiếp theo: không có mục M3 chưa DONE trong tệp hiện hành.** Không tự tạo thêm mục hoặc chuyển M4/M5. Không có công việc triển khai còn lại được liệt kê cho M3. Failover/giữ phiên, CARP sau reboot riêng và WAN/NAT/DHCP HA chưa nghiệm thu; đây là giới hạn kết quả, không phải TODO mới được tự giao.

## 0.2. Trạng thái runtime vừa kiểm tra

- Core `SOC-Core-L2`: ON,1024MiB/1vCPU; giữ Layer2, gateway/inter-VLAN ở OPNsense. Lượt checkpoint mới xác nhận tiến trình QEMU, không chạy lại toàn bộ OVS audit; bằng chứng L2/VLAN có tại báo cáo M2 và M3 resource optimization.
- Primary: ON,2048MiB/2vCPU; **MASTER trên VLAN30/40/50/60/99**, advbase1/advskew0. IP vật lý192.168.VLAN.2/24; SYNC10.255.255.1/30.
- Secondary: ON,2048MiB/2vCPU; **BACKUP trên VLAN30/40/50/60/99**, advbase1/advskew100. IP vật lý192.168.VLAN.3/24; SYNC10.255.255.2/30.
- VIP đã lưu và nghiệm thu:192.168.30.1/24→VHID30;192.168.40.1/24→40;192.168.50.1/24→50;192.168.60.1/24→60;192.168.99.1/24→99. Chỉ năm VLAN, không WAN/LAN parent.
- Pfsync hai phía: UP/RUNNING, syncdev vtnet2, peer đối ứng đúng, version1400, syncok1; CARP demotion0. Ảnh console thật lúc23:44:11+07:00 xác nhận lại CARP/pfsync; host-readonly.json lúc23:44:19+07:00 xác nhận ba QEMU/tài nguyên. Không suy thành kiểm tải dài hạn hoặc failover PASS.

## 0.3. Thay đổi cuối, backup và cách tiếp quản an toàn

1. Đã sửa persistence pfsync bằng hook native `/usr/local/etc/rc.syshook.d/start/96-soc-pfsync` (0700), gọi `pluginctl -c pfsync` sau network startup; log `/var/log/soc-pfsync-start.log`. Đã reboot riêng từng firewall, đối chiếu kern.boottime mới và log cùng boot; reader nghiệm thu không apply lại sau boot. Không vá mã core OPNsense.
2. **Thay đổi hệ thống cuối:** tạo năm VIP CARP trên Secondary sau Primary; dùng model native, validation/backup trước save và native VIP/filter reload. Các phần XML ngoài virtualip/revision được kiểm giữ nguyên. Sau đó chỉ đọc, kiểm thử và ghi báo cáo. Lượt checkpoint23:44 không áp/reload/reboot hoặc thay đổi cấu hình.
3. Backup root-only trên **mỗi firewall**: `/root/soc-m3-todo-pfsync-20261103/config.before.xml` và `/root/soc-m3-todo-carp-20261103/config.before.xml`. Shared secret đã có trong guest, không in/chép vào chat hoặc evidence công khai. Không tự rollback/reapply các payload vì checkpoint/đối tượng đã tồn tại.
4. Lab trên EVE: `/opt/unetlab/labs/SOC-M2-Core-L2.unl`; node IDs Primary1, Secondary2, Core3. Kết nối SSH host đã cấu hình trong `automation/topology_remote.py`; công cụ console `automation/m3_resource_console.py` hỗ trợ `--output-dir`. Trước gửi lệnh, chụp và xem đúng console/shell; hai firewall đang ở root shell ở lần thu mới nhất. Nếu phiên đăng nhập hết hạn, cần đăng nhập trực tiếp, không đổi authentication/seed để vượt qua.
5. Không còn TODO M3 được liệt kê để tự thực thi. Nếu phiên sau cần kiểm tra lại trạng thái, chỉ đọc `ifconfig`, pfsync/demotion và host trước; không cài lại OVS, tạo lại bridge/VIP, đổi RAM hay chạy lại bootstrap. Không cleanup, xóa evidence/backup, commit/push hoặc triển khai M4/M5.

## 0.4. Evidence và báo cáo cần đọc

- Minh chứng checkpoint mới: [evidence-index](evidence/M3/checkpoint-20261103T2343/evidence-index.md), `host-readonly.json`, hai ảnh checkpoint và JSON cùng tên. Chỉ là ảnh/output thật; timestamp collector UTC+07:00, không dùng giờ guest lệch làm giờ thu.
- Nghiệm thu chính: [báo cáo M3](M3/M3-todo-completion-20261103.md), [danh mục đầy đủ](evidence/M3/todo-completion-20261103/evidence-index.md), hai acceptance JSON nêu trên; đủ config/runtime/packet/ARP/backup metadata.
- Lưu ý đã ghi trong báo cáo: byte hash lab có chênh lệch ở một text object; toàn bộ cây node/network và interface mapping giữ nguyên. Không tự sửa/revert text object hoặc kết luận toàn tệp nguyên byte.
- Evidence và báo cáo cũ giữ nguyên. Không tạo thêm demo plan hoặc tài liệu triển khai ngoài TODO.

---

# LỊCH SỬ — M2 hoàn thành — 03/11/2026, UTC+07:00

Core L2 PASS; Inter-VLAN PASS bằng HTTP200 .40.100 → .30.10:8000 và PCAP tag40→30/TTL64→63/MAC Primary; firewall PASS một ca dương/hai ca âm đối chiếu PCAP/counter; access/trunk PASS; SPAN PASS; LACP N/A. Không sửa rule hoặc Core/NAT/DHCP/CARP/HA. Client namespace có NIC tạm VLAN40 trong DC, giữ đúng IP ngoại lệ; sau thử DC tắt mềm, NIC tạm gỡ, lab phục hồi nguyên byte. Core + Primary giữ chạy. [Báo cáo cuối](M2/M2-final-summary-20261103.md), [SOC TO DO](SOC_TO_DO.md), [evidence index](evidence/M2/final-acceptance-20261103/evidence-index.csv). Không chuyển M3.

Các checkpoint bên dưới giữ làm lịch sử; kết quả NOT_RUN/chưa PASS trước đó đã được cập nhật bằng mốc này, không xóa minh chứng.

# M2 Nhóm 2A — kết quả mới nhất 02/11/2026, UTC+07:00

Đã shutdown mềm Wazuh theo quyền riêng, xác nhận dừng rồi bật Primary; chỉ Core + Primary chạy, tổng RAM khai báo 5120 MiB. Sau khi người dùng mở shell, đã backup root-only `/root/soc-group2a-20261102-215617/config.xml` trên ổ cứng Primary (0700/0600); raw backup giữ trong guest, Windows chỉ lưu JSON công khai và ảnh/log. Cả năm VLAN đều enabled/UP, parent vtnet0, tag 30/40/50/60/99, IP tương ứng 192.168.VLAN.2/24; khớp cấu hình đã quan sát trước đây. Không có cấu hình cần sửa. Hash config hiện hành/backup đọc lại khớp `2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2`. IPv4 forwarding 1, có route trực tiếp, không thêm static route/VIP/gateway. Không thay Core, WAN, SYNC, NAT, DHCP, rules hoặc Secondary; không kiểm thử lưu lượng. **Dừng sau Nhóm 2A, chờ “TIẾP TỤC”.** [Báo cáo trước/sau và ảnh](M2/M2-group2a-primary-vlans-20261102.md), [JSON công khai](evidence/M2/group2a-20261102T215617+0700/primary-audit-before.json), [danh mục](evidence/M2/group2a-20261102T215617+0700/evidence-index-final.csv).

# M2 Nhóm 1B — kết quả trước đó 02/11/2026, 21:46 UTC+07:00

Đã bật riêng SOC-Core-L2 theo phê duyệt và chờ người dùng đăng nhập trực tiếp. Sau đăng nhập, đã sao lưu OVSDB/cấu hình vào `docs/evidence/M2/group1b-20261102T212014+0700/private-backups/`, kiểm schema 8.5.1 và xác minh SHA-256 khi chuyển về Windows. Runtime khớp mapping đã xác nhận: access ens3–ens7 lần lượt VLAN 30/40/50/60/99; trunk ens8/ens9 đủ năm VLAN; SPAN giữ nguyên; Core không IP/gateway, forwarding 0/0. Không cần sửa cấu hình, không LACP, không thử lưu lượng hoặc thay OPNsense. Wazuh đã chạy trước đó được giữ nguyên; chỉ Core được start trong lượt này. **Dừng sau Nhóm 1B, chờ xác nhận chuyển nhóm.** [Báo cáo và ảnh](M2/M2-group1b-runtime-20261102.md), [manifest backup](evidence/M2/group1b-20261102T212014+0700/backup-manifest.json), [danh mục minh chứng](evidence/M2/group1b-20261102T212014+0700/evidence-index-final.csv).

# Tiếp quản trước đó — 02/11/2026, UTC+07:00

- Kiểm kê 20:33: tất cả QEMU tắt, khác checkpoint ba node chạy. Người dùng đã duyệt bật riêng Wazuh-SOC 4096 MiB; không bật node khác.
- Audit sau boot: Manager 4.14.9-1 failed do timeout 45 giây; không có drop-in. Đã backup unit và tạo mới `/etc/systemd/system/wazuh-manager.service.d/soc-timeout.conf` với TimeoutStartSec=300; sau sửa service active, enabled và các thành phần chính chạy. Chưa kiểm tra reboot sau sửa.
- JSON mô phỏng tự thu thập thành alert mới 100101 level 8. Replay đúng sự kiện M4 thật thành alert mới 86601 level 3; đã đối chiếu nguồn SHA-256, timestamp sự kiện, IP, ICMP, VLAN 30, SID và flow ID. Rule tích hợp không có full_log; các phép kiểm ban đầu thiếu khớp được giữ nguyên, không xóa.
- Chỉ đạt thu thập replay cục bộ. Chưa có đường mạng Wazuh hoặc truyền log trực tiếp; không kết luận end-to-end live PASS. Indexer/Dashboard/Filebeat chưa có gói trên Wazuh-SOC. Pfsync chỉ xác minh gói hai chiều, chưa nghiệm thu giữ phiên/state replication; CARP failover chưa đạt nghiệm thu.
- Báo cáo: [M5](M5-verification-and-demo-20261102.md). [Kịch bản demo 13 phút](SOC-video-demo-20261102.md). [Đề xuất live chưa triển khai](M5-live-pipeline-proposal-20261102.md). [Danh mục ảnh/log mới](evidence/M5/continuation-20261102/evidence-index-final.md).
- Không cài lại Core/OPNsense/Manager, không sửa RAM/đĩa/image/seed/dây mạng. Minh chứng cũ giữ nguyên. Chỉ Wazuh-SOC được giữ chạy; chưa có quyền shutdown/reboot hoặc bật các nhóm khác trong lượt này.

Phần bên dưới là checkpoint lịch sử, giữ nguyên nội dung gốc; trạng thái runtime phải dùng mốc mới nhất và minh chứng tương ứng.

# Tiến độ dự án SOC

## Mốc tiếp quản khẩn cấp — 01/11/2026, 12:57 UTC+07:00

**Mới nhất 22:09 UTC+07:00:** Primary đã start riêng thành công với `-boot order=c`; ảnh thật ghi `Booting from Hard Disk...`, tiếp đó `/dev/gpt/rootfs`, filesystem clean và đang khởi tạo dịch vụ. ISO giữ nguyên; Core tắt. Guard swap đã sửa đánh giá: 268 KiB swap cũ không phải áp lực swap đang xảy ra; EVE còn khoảng 6,3 GiB available và vmstat si/so=0. Windows hồi lên 0,54 GiB available/3,09 GiB commit trước start. Đang chờ boot hoàn tất và người dùng đăng nhập root/chọn Shell để kiểm tra mount/phiên bản/NIC; chưa tuyên bố gateway hoặc firewall PASS.

**Sau thông báo cài xong của người dùng:** đã xác minh không QEMU chạy, sao lưu overlay đã cài 2491482112 byte vào `/root/m3-primary-installed-backup-20261101/virtioa.qcow2`, SHA-256 nguồn/bản sao khớp `81d0dba0063d918581f0cfc8717fe81472c3398cd82e9381fd8b904f68e0a5df`. Lab XML đã backup; chỉ đổi boot riêng Primary từ `order=dc` sang `order=c`. ISO vẫn giữ/gắn, không nằm trong thứ tự boot; không sửa image gốc. **Chưa boot lại thành công:** guard start chặn vì swap EVE có 268 KiB (free -m làm tròn thành 0); vmstat không có swap-in/out hiện thời. EVE available 6348 MiB, Windows available vừa đo 0,17 GiB/commit 3,10 GiB sau sao lưu. Chưa coi cài đặt/boot là PASS từ thông báo người dùng hoặc metadata đĩa; cần console/root filesystem từ ổ.

**Mới nhất 13:26 UTC+07:00: installer đã bắt đầu ghi đúng vtbd0.** Đã xem màn hình xác nhận duy nhất vtbd0 rồi chọn YES trong phạm vi cài đặt được duyệt; ảnh thật cho thấy partition tables và vtbd0p1 Completed, vtbd0p3 In Progress. Chưa gọi là cài xong. Backup offline trước cài vẫn giữ. Đánh giá lại ngưỡng Windows 1 GiB: đó là dự phòng tạm, không phải yêu cầu cứng installer; tiếp tục chỉ Primary đang chạy vì EVE available 4988 MiB, swap 0, Windows commit available 4,24 GiB (physical available 0,61 GiB). Không tăng RAM/VM, không bật Core, không chạy tác vụ song song; theo dõi tài nguyên. Các mốc chờ RAM/chưa ghi bên dưới là lịch sử trước bước này.

**Mới nhất 13:18 UTC+07:00:** người dùng đã đăng nhập installer; đã qua Keymap, chọn Install (UFS), đang ở màn hình chọn ổ `vtbd0 (16GB)`; `cd0` là DVD, không chọn. **Chưa xác nhận ghi/phân vùng, chưa cài hệ điều hành.** Ảnh thật `installer-keymap`, `installer-options`, `installer-ufs-target` trong evidence M3. Windows available 0,37 GiB/commit available 3,01 GiB; EVE available 5035 MiB, swap 0. Tạm dừng trước thao tác ghi/tăng tải, chờ Windows có khoảng 1 GiB available. Giữ Primary tại installer, Core tắt; không shutdown hoặc yêu cầu đăng nhập lại.

**Cập nhật sau sao lưu:** đã bật lại duy nhất Primary qua wrapper EVE, Core giữ tắt. Điều chỉnh ngưỡng 4 GiB Windows trước đó vì quá bảo thủ cho QEMU lồng trong EVE đã cấp 8 GiB: guard thực thi Windows available ≥1 GiB, commit available ≥2 GiB; EVE available ≥4 GiB, swap chưa dùng, không QEMU khác. Số đo trước start: Windows 1,128 GiB/commit 3,421 GiB, EVE 6354 MiB. Receipt `evidence/M3/primary-live-20261101/start-primary-after-backup.json`. Không đổi RAM VMware; vẫn chưa chạy installer. Đây là trạng thái mới hơn dòng cả hai VM tắt phía dưới.

**Mới nhất 13:03: cả Primary và Core đều TẮT.** Sau khi RAM tạm lên 1,27 GiB, đã shutdown mềm Primary để sao lưu ổ runtime trước installer; guard xác minh QEMU dừng, backup overlay và lab XML thành công, checksum khớp. Backup `/root/m3-primary-preinstall-20261101T1302/`; chưa cài, chưa phân vùng hoặc đổi mạng. Sau dừng Windows vẫn chỉ 1,13 GiB available/3,41 GiB commit available, chưa bật lại VM 3 GiB. Chờ khoảng 4 GiB available rồi start riêng Primary. Các dòng dưới là diễn biến trước mốc mới nhất này.

Người dùng giao ưu tiên OPNsense Primary với thời gian còn 9 giờ 30 phút. **Trạng thái runtime mới thay dòng Core đang chạy ở checkpoint M2 phía dưới:** Core hiện tắt; duy nhất Primary ID 1 đang chạy Live ISO OPNsense 26.7, chưa xác minh cài ổ. SSH đã khôi phục; EVE available 5114 MiB, swap 0. Windows chỉ khoảng 0,40 GiB available, chưa đủ dự phòng tăng tải/bật Core. Không có link EVE. Đang chờ shell Live đã xác thực để đọc partition và MAC trước installer, đồng thời người dùng giải phóng RAM. [Nhật ký và ảnh thật M3](M3/M3-primary-live-status-20261101.md).

M2 vẫn giữ **95/95 ca frame thật PASS**, mirror và persistence đã có bằng chứng; không chạy lại hoặc phủ nhận kết quả cũ do mô tả đầu vào chưa cập nhật. Chưa có nghiệm thu gateway/firewall/HA/IDS. Bộ công cụ `capture_m3_primary_readonly.py` đã chụp đúng Primary; không gửi phím hoặc thay VM.

Cập nhật 13:00: shell Primary đã xác thực; kiểm tra nhẹ xác nhận vtbd0 16 GiB, chưa có bảng phân vùng được gpart nhận diện, root vẫn Live ISO. MAC net0/net1/net2 lần lượt khớp vtnet0/vtnet1/vtnet2; hiện LAN=vtnet0, WAN=vtnet1, vtnet2 chưa gán. Chưa chạy installer vì Windows vẫn chỉ 0,49 GiB RAM available sau lần giải phóng, dưới dự phòng 1 GiB; chờ thêm RAM. M2 và ảnh Live ban đầu đã push PRIVATE commit `3eae637fbfeba2d9b56647364292938091a50cf6`, remote/local khớp. Ảnh/lệnh kiểm tra shell bổ sung nằm trong thư mục minh chứng M3, chưa phải PASS cài đặt.

Checkpoint ngày **01/11/2026, UTC+07:00 (Asia/Saigon)**; hạn nộp **05/11/2026**. Đọc `AGENTS.md` trước mọi thao tác.

## 0. Trạng thái hiện hành và các mốc bàn giao

### 0.0. Kết quả M2 thực tế đã hoàn thành ngày 01/11

**Core đang chạy; bộ kiểm thử M2 cô lập đạt95/95 ca frame thật,0 FAIL.** Đây là trạng thái hiện hành thay cho các mốc NOT_RUN/giữ VM tắt ở dưới. Không cần cài lại OVS/tạo bridge hoặc chạy lại suite đã đạt nếu trạng thái chưa đổi. Chỉ một QEMU Core2048MiB được bật, không thêm VM/link, không sửa image/seed/mạng host.

- [Báo cáo Word M2 thực tế](M2/M2-report-functional-tests-verified-20261101.docx), [Markdown](M2/M2-report-functional-tests-verified-20261101.md): mapping, nguyên lý, kết quả và8 ảnh console thật; các báo cáo cũ giữ nguyên. [Kiểm tra bàn giao](evidence/M2/live-tests-20261101/delivery-checks-final.json).
- [Bảng95 ca](evidence/M2/live-tests-20261101/final-collection/frame-cases.csv): trước mirror31/31, sau mirror32/32, sau reboot32/32. Có178 frame guest trả ra,24 PCAP cuối lưu cục bộ trong ba thư mục stage; capture chỉ marker thử, không lấy PACKET_OUTGOING làm kết quả. Bản pre-reboot-collection là snapshot trùng của63 ca đầu, không cộng thêm vào95.
- [Mapping sau reboot](evidence/M2/live-tests-20261101/configured-port-mapping-after-reboot.csv): ens3/30,ens4/40,ens5/50,ens6/60,ens7/99; ens8/ens9 trunk30,40,50,60,99; ens10 output Mirror span-suricata chọn ingress7 data ports/năm VLAN, không select_dst_port. Cổng mirror gửi ngược không chuyển tiếp. Mỗi suite mirror có26 bản sao: VID30=6, còn lại5 mỗi VLAN; chưa có Suricata VM.
- **Persistence đạt:** soc-core-l2-noip.service enabled/active; boot_id3060cddc-e143-4e13-b739-76f4f2b96deb đổi thành6b7326c8-146a-45f7-b373-1a014d0021e2; cấu hình/VLAN/mirror, không IP/gateway và forwarding0/0 đều kiểm lại, rồi32 ca frame sau boot đạt.
- Backup chính trước SPAN: `/root/m2-traffic-m2-live-20261101a/ovsdb.before`, schema8.5.1; metadata/hash trong queue-receipt.json và guest-public-replies của final-collection. Raw DB chỉ trong guest root-only. Registry tệp unit/helper và log lệnh đầy đủ vẫn trong cùng workdir guest; các JSON/ảnh/events/PCAP đã thu ở Windows được chỉ rõ trong danh mục. Không dùng snapshot OVS rỗng từ đợt đầu để rollback hiện tại.
- Lỗi đã xử lý: ssh-agent bị dừng; bridge admin DOWN sau boot đầu; guard so nhầm cờ link và IPv6 link-local tự sinh khi rollback runtime; bundle/tmp bị dọn sau reboot và lỗi truyền/chuỗi console. Các lần lỗi giữ trong evidence, không tính thành FAIL của95 ca frame. Đã dừng đúng client điều phối của phiên và Ctrl+C dòng nhập dở, không Reset/dừng VM hoặc sửa sudoers.
- Adapter hiện dùng literal JSON, hash từng chunk/toàn bộ và `/var/tmp`. Sau lỗi bundle lớn, `m2_postboot_readonly_export.py` dùng thư viện đã giữ trong/root với hash263c27f2… để lấy trạng thái thực; `m2_resume_verified_postboot.py` kiểm cùng guard rồi dùng chính controller/frame_test chạy32 ca cuối. `m2_recover_bridge_runtime.py` chỉ giữ lịch sử các lần thử lỗi, không tái chạy. Không coi mock/static hoặc dữ liệu xuất chỉ đọc là PASS lưu lượng.
- Còn cảnh báo **OVS_CTL_OPTS chưa đặt** trong journal, dịch vụ vẫn active; chưa sửa unit OVS để bỏ cảnh báo. Chưa có ảnh GUI topology mới và chưa rà phân trang Word bằng GUI. Chưa thử tải cao, IPv6 payload, endpoint TCP/IP/firewall/HA hoặc IDS/Wazuh.
- Tài nguyên cuối đợt: Windows khoảng2,13GiB available, EVE5922MiB available, một QEMU. Đây là số đo lịch sử, đo lại trước M3. Core tiếp tục chạy nhàn, không bật thêm VM trong đợt này.

**Điều kiện M3 Primary:** giao phạm vi M3 riêng, image chính thức đã xác thực, đủ RAM/commit/đĩa và dự phòng, xác minh MAC/interface LAN-WAN-SYNC, subnet/VIP/DNS/WAN/upstream. Ưu tiên cài một firewall tuần tự; cặp HA + Core vượt RAM EVE hiện có. Không triển khai OPNsense/Suricata trong checkpoint này. Kế hoạch đến05/11 vẫn ở SOC-execution-resource-plan-20261101.md; M2 chức năng được giao đã đạt, chuyển ưu tiên sang Primary khi đủ điều kiện.

### 0.0.1. Lịch sử tiếp tục sau Labtainer — 01/11, 10:36 UTC+07:00

Người dùng xác nhận đã hoàn thành Labtainer và phê duyệt bật duy nhất Core2GiB, kiểm thử M2/mirror/persistence có backup và rollback. Không bật firewall/sensor, không sửa mạng host/image/seed. Giới hạn giữ VM tắt ở các mục lịch sử dưới đây đã được thay bằng phạm vi mới này khi đủ tài nguyên.

Lần chạy bộ điều phối `staging/m2-live-20261101a` chưa tới bước start: SSH EVE bị `Permission denied (publickey,password)`, ssh-agent Windows Stopped và không kết nối agent. RAM đo10:36 là2,88GiB available, virtual available6,45GiB; cần đo lại và đạt ngưỡng bật Core3GiB. Đã yêu cầu người dùng tự khôi phục agent/khóa và giải phóng thêm ít RAM, không thay dịch vụ Windows. [Tiền kiểm tra thực tế](evidence/M2/live-tests-20261101/preflight-agent-blocked.json). Chưa phát lệnh start, chưa chạy ca frame hoặc thay cấu hình; không có PASS mới. Tiếp tục cùng queue sau khi khôi phục điều kiện, không cài lại OVS/tạo lại bridge.

### 0.1. Chuẩn bị tăng tốc trước 10 giờ ngày 01/11

**Không có lịch tự khởi động VM lúc 10:00. Chờ thông báo tài nguyên sẵn sàng từ người dùng.** Đợt này không SSH tới EVE, không bật VM, không chạm QCOW2 hoặc Labtainer.

- [Runbook tuần tự](M2/M2-sequential-runbook-PREPARED-20261101.md): bộ điều phối `automation/m2_run_queue.py` mặc định chỉ lập kế hoạch; future execution gom tài nguyên/start/baseline/backup/frame/mirror/persistence/thu kết quả. Chỉ giữ điểm dừng đăng nhập/sudo sau boot và kiểm tra trước reboot, không hỏi từng lệnh. Queue và nhật ký append-only cho phép tiếp tục mà không chạy lại nhóm đã DONE; phiên đã rollback yêu cầu review và phiên mới.
- Adapter `automation/m2_console_job.py`: chuẩn bị truyền script/nhận JSON bằng console, kiểm payload/reply SHA-256, không SSH trực tiếp guest hoặc nhận bí mật. **Chưa chạy trên console thật.** Sửa guard đường dẫn backup, stale baseline, lưu lỗi/rollback, final case count, resume sau reboot và bảo toàn log console khi tiếp tục.
- [Báo cáo M2 mới có phụ lục điều phối](M2/M2-report-execution-ready-PREPARED-20261101.docx), [Markdown](M2/M2-report-execution-ready-PREPARED-20261101.md): giữ12 ảnh cũ nguyên byte, không ghi đè báo cáo trước. [Rà DOCX/static](preparation/pre10-20261101/) ghi rõ không nghiệm thu mạng, chưa kiểm GUI phân trang.
- [M3 địa chỉ/chính sách/checklist](M3/M3-deployment-matrix-and-tests-PREPARED-20261101.md), `configs/M3/address-proposal.json`: IP Primary/Secondary/VIP từ ví dụ M1, đề xuất mới SYNC /30 và DHCP40/50 ghi riêng, mọi giá trị chưa xác nhận. `validate_m3_plan.py` chỉ kiểm nhất quán; `m3_collect_readonly.sh` chưa chạy trên firewall.
- [M4 Suricata](M4/M4-Suricata-mirror-PREPARED-20261101.md): mapping capture/management tách biệt, capture tag/drop, rule ICMP marker, offline PCAP rồi live khi đủ RAM, log EVE→Wazuh. `automation/m4_benign_frame.py`, `suricata/soc-lab.rules` và fragment Wazuh chỉ chuẩn bị; chưa gửi frame/cài sensor/tích hợp.
- [Kế hoạch tài nguyên và hạn05/11](SOC-execution-resource-plan-20261101.md), [mẫu kết quả](templates/SOC-test-result-template.csv), [mẫu danh mục ảnh/log](templates/SOC-evidence-template.csv). NOT_RUN là mặc định; một firewall không thay nghiệm thu HA, Suricata offline không thay live IDS.

### 0.2. Checkpoint triển khai trước và phần chưa thực hiện

**Giữ tất cả VM SOC tắt. Chỉ tiếp tục triển khai VM sau khi người dùng xác nhận đã học xong Labtainer và tài nguyên sẵn sàng.** Không reboot, không tải image OPNsense, không đổi EVE/VMware/Windows/Labtainer, không chạy kiểm thử frame hoặc mirror trong thời gian này. Phê duyệt tăng tốc trước đó không thay thế giới hạn mới.

- SSH đã được người dùng khôi phục bằng ssh-agent; Codex kết nối lại thành công. Không đổi sudoers hoặc yêu cầu bí mật.
- Kiểm kê 07:57–07:58: không có QEMU chạy; lab Core vẫn một node/không network/link. Windows khoảng 0,5 GiB available, có mẫu tiếp theo dưới 0,1 GiB; EVE available 6531/7897 MiB. Đây là số đo lịch sử, phải đo lại sau thông báo sẵn sàng. Không coi dịch vụ OVS đang active khi Core tắt.
- Trước chuyển sang chế độ nhẹ, đã backup overlay khi Core tắt: `/root/m2-stopped-backup-20261101T075852Z/core-overlay.qcow2`, 712310784 byte; ba hash nguồn trước/sau và bản sao khớp `7a31bfb3a08d2c64bd8397b00290e419c277fb2a2359593df7a307a2f991df17`. Không ghi QCOW2 nguồn; raw backup giữ trên EVE, chưa thử restore. [Metadata](evidence/M2/accelerated-20261101/stopped-backup.json).
- [Báo cáo M2 hợp nhất mới](M2/M2-report-consolidated-review-20261101.docx), [bản Markdown](M2/M2-report-consolidated-review-20261101.md): 12 ảnh thật nhúng nguyên byte, bảng trạng thái và giải thích kỹ thuật; các báo cáo cũ giữ nguyên. Chưa kiểm tra phân trang qua GUI Word.
- [Kịch bản kiểm thử và rollback](M2/M2-test-and-rollback-PREPARED-20261101.md), [bảng CSV](M2/M2-test-cases-PREPARED-20261101.csv): 31 case frame trước mirror/32 khi mirror, tất cả chưa chạy; bảng L00–L13 bao gồm tài nguyên, baseline, capture, persistence và rollback.
- Script mới: `automation/m2_tap_frame_test.py` (phát/thu frame trên TAP riêng, không thêm VM hoặc host bridge), `automation/m2_mirror_guest_prepared.py` (backup/mirror/rollback trong guest), mẫu `configs/M2/soc-core-l2-noip.service` và `.sh`. **Chỉ chuẩn bị, chưa triển khai/thử runtime.** Đã kiểm tra cú pháp Python cục bộ; không coi là PASS chuyển mạch.
- [Thiết kế M3 OPNsense HA](M3/M3-OPNsense-HA-PROPOSED-20261101.md): Primary/Secondary, CARP VIP, pfsync/XMLRPC, VLAN gateway, chính sách firewall và kế hoạch tuần tự. Chưa tải image/chạy OPNsense. Core + hai firewall tối thiểu 8192 MiB vượt tổng EVE 7897 MiB trước overhead; một firewall là phương án demo tối thiểu sau khi đủ RAM, không nghiệm thu HA bằng hai máy chạy lần lượt.
- [Danh mục ảnh/log bản hợp nhất](evidence/M2/light-documentation-20261101/evidence-index.csv), [kiểm tra DOCX](evidence/M2/light-documentation-20261101/validation.json). Không có ảnh console mới hoặc PCAP thử nghiệm trong đợt nhẹ.

Sau thông báo tài nguyên sẵn sàng: đo lại RAM/commit Windows và RAM/swap EVE; bật duy nhất Core nếu an toàn; đọc baseline sau boot trước sửa; tạo snapshot OVSDB mới có bridge hiện hữu; thử frame không mirror, cấu hình mirror ens10 rồi thử/capture; xử lý persistence có rollback và thử lại sau reboot. Không chạy lại prepare/apply tạo bridge từ baseline rỗng. Chốt địa chỉ/WAN/MAC firewall trước M3. Mọi nghiệm thu lưu lượng, mirror, persistence và HA vẫn chờ bằng chứng thực tế.

Các mục 1–6 dưới đây giữ chi tiết checkpoint triển khai trước đó; phát biểu active/runtime áp dụng tại mốc thu cũ, phải đọc cùng cập nhật mục 0.

## 1. Trạng thái đã triển khai và kiểm chứng

- EVE-NG `192.168.220.143`; lab `SOC-M2-Core-L2`; node `SOC-Core-L2`, ID 3, UUID `2b295168-b72e-4de7-b364-37298252dd9f`.
- Ubuntu 24.04, user `soc-core-admin`, 1 vCPU, 2048 MiB RAM, đĩa 8 GiB, tám VirtIO NIC. Không ghi thông tin đăng nhập vào Git.
- Open vSwitch **3.3.9**, gói `3.3.9-0ubuntu0.24.04.1`, DB schema **8.5.1** đã cài hoàn toàn offline. Bộ 70 gói và sáu chỉ mục đã đối chiếu checksum; kho gói/ISO vẫn giữ trên máy và guest, không đưa lên Git.
- `openvswitch-switch`, `ovsdb-server`, `ovs-vswitchd` đã xác minh active ở lần thu minh chứng.
- `br-core-l2`: `datapath_type=system`, `fail_mode=standalone`, cờ quản trị UP; datapath nhận đủ bảy port vật lý và một local port, Interface.error rỗng, flow NORMAL tồn tại.
- Không có controller, bond/LACP hoặc Mirror. `ens10` vẫn ngoài OVS, không SPAN và trạng thái không đổi.
- Core không có IP/gateway trên các cổng/bridge; route giữ nguyên; IPv4/IPv6 forwarding đều **0**. Local Port `br-core-l2` thuộc VLAN 99, không phải vNIC thứ chín.
- Riêng interface mới `br-core-l2` đặt `addrgenmode none` và `net.ipv6.conf.br-core-l2.disable_ipv6=1` để tránh địa chỉ/route IPv6 tự sinh. Không đổi forwarding hoặc IPv6 của tám NIC cũ. Chưa chứng minh các thiết lập runtime này duy trì qua reboot.
- Lab chưa có network/link hoặc peer; tám TAP trên EVE chưa có bridge master. Không bật thêm VM, không sửa VMware/Windows/firewall/NAT/OPNsense, image gốc hoặc seed.

## 2. Mapping hiện hành

| QEMU | TAP trên EVE | NIC guest | MAC | Cấu hình OVS đã kiểm chứng | Peer thực tế |
|---|---|---|---|---|---|
| net0 | vunl0_3_0 | ens3 | 02:53:45:f2:19:00 | Access VLAN 30 — Data Center | Chưa nối |
| net1 | vunl0_3_1 | ens4 | 02:53:45:f2:19:01 | Access VLAN 40 — Employee | Chưa nối |
| net2 | vunl0_3_2 | ens5 | 02:53:45:f2:19:02 | Access VLAN 50 — Guest | Chưa nối |
| net3 | vunl0_3_3 | ens6 | 02:53:45:f2:19:03 | Access VLAN 60 — DMZ | Chưa nối |
| net4 | vunl0_3_4 | ens7 | 02:53:45:f2:19:04 | Access VLAN 99 — Management | Chưa nối |
| net5 | vunl0_3_5 | ens8 | 02:53:45:f2:19:05 | Trunk 30,40,50,60,99 — dành cho Primary | Chưa nối |
| net6 | vunl0_3_6 | ens9 | 02:53:45:f2:19:06 | Trunk 30,40,50,60,99 — dành cho Secondary | Chưa nối |
| net7 | vunl0_3_7 | ens10 | 02:53:45:f2:19:07 | Ngoài OVS, chưa mirror | Chưa nối |

Tên cổng GUI EVE và MAC/cổng peer chưa được xác minh. Không suy số OpenFlow `ofport` từ thứ tự ens/QEMU; đọc cột `ovs_ofport` trong CSV và kiểm tra lại khi bắt đầu phiên tiếp theo.

## 3. Tài liệu và minh chứng cần đọc khi tiếp quản

1. [Báo cáo cấu hình cô lập hiện hành](M2/M2-report-isolated-bridge-configured-20261101.docx) và [bản Markdown](M2/M2-report-isolated-bridge-configured-20261101.md), đặc biệt mục 2.28–2.33. Các mốc và đề xuất ở phần trước là lịch sử.
2. [Mapping đã cấu hình](evidence/M2/isolated-bridge-20261101/configured-port-mapping.csv), [kết quả guest](evidence/M2/isolated-bridge-20261101/guest/result.json), [xác minh bàn giao](evidence/M2/isolated-bridge-20261101/delivery-validation.json).
3. [Danh mục minh chứng](evidence/M2/isolated-bridge-20261101/evidence-index.md), [log lệnh thực tế](evidence/M2/isolated-bridge-20261101/guest/commands.jsonl), [log lần áp dụng cuối](evidence/M2/isolated-bridge-20261101/guest/apply.log).
4. [Thiết kế và kế hoạch kiểm thử T00–T15](M2/M2-report-port-mapping-and-ovs-design-20261101.docx). Phạm vi SPAN trong thiết kế cũ **chưa được thực hiện**; phê duyệt mới yêu cầu giữ ens10 ngoài OVS.
5. [Kết quả cài OVS offline](M2/M2-report-ovs-offline-installed-20261101.docx).

## 4. Lỗi đã xử lý, sao lưu và giới hạn

- Nguồn APT ban đầu thiếu `noble-updates`; đã dùng nguồn file offline riêng, xác thực chữ ký Ubuntu, tắt lấy metadata phụ trợ CNF/DEP-11 không có trong bundle. Không sửa DNS/Internet của guest.
- Lần tạo bridge đầu tiên bị chặn bởi kiểm tra route vì kernel thêm route multicast IPv6 `ff00::/8` trên bridge mới. Snapshot OVSDB đã restore thành công, link/address/route trở về đường cơ sở; sau đó chỉnh riêng IPv6 cục bộ bridge mới và áp dụng lại thành công. Log `attempt1-*` và `failure.json` là lịch sử lần đầu, không phải trạng thái thất bại hiện hành.
- Backup raw và script rollback nằm **chỉ trong guest**, thư mục `/root/m2-isolated-20261101T0035/` mode 0700. `ovsdb.before` mode 0600, SHA-256 `09afc9da76c632f14c24e4754f499b620c8c3042f235b02144198a8f50a99081`; schema 8.5.1. Metadata đã lưu trong [backup-metadata.json](evidence/M2/isolated-bridge-20261101/guest/backup-metadata.json).
- `rollback.sh` phục hồi snapshot về cấu hình OVS rỗng trước bridge; không tự chạy khi tiếp quản. Cần đánh giá quyền/phạm vi trước mọi rollback mới vì thao tác sẽ bỏ cấu hình hiện tại. UUID hàng DB có thể đổi sau restore.
- Cảnh báo `OVS_CTL_OPTS` chưa đặt từ đợt cài đã được ghi nhận; không sửa unit trong phạm vi cấu hình cô lập.
- Chưa có ảnh GUI topology mới; ảnh console thật và log đã thu, hướng dẫn chụp thủ công nằm trong báo cáo. Chưa kiểm tra phân trang bằng giao diện Word.

## 5. Chưa nghiệm thu và công việc tiếp theo

**Chưa kiểm thử lưu lượng thực tế; chưa nghiệm thu chức năng chuyển mạch M2.** Chưa thử VLAN isolation, tag 802.1Q, allowed/denied trunk, SPAN, gateway/HA hoặc persistence sau reboot.

Phiên tiếp theo bắt đầu bằng kiểm tra chỉ đọc: đúng node/UUID, MAC, `ovs-vsctl show`, Port/Interface/Mirror, địa chỉ/route/forwarding, trạng thái dịch vụ, kết nối EVE và RAM Windows/EVE. Không chạy lại cài OVS, seed/cloud-init hoặc tạo bridge đã có. Script `m2_isolated_bridge_guest.py prepare/apply` dành cho baseline rỗng, **không chạy lại** trên cấu hình hiện hành.

Các bước dưới đây là kế hoạch của checkpoint cũ. Đợt tăng tốc đã phê duyệt kiểm thử/mirror/persistence trong M2 cô lập có rollback, nhưng **hiện tạm giữ theo yêu cầu Labtainer ở mục 0**. Sau xác nhận tài nguyên sẵn sàng, tiếp tục thao tác an toàn đã được giao; chỉ xin quyền mới cho phần vượt phạm vi hoặc ảnh hưởng host:

1. Chọn endpoint VLAN-aware/capture, image hợp lệ, MAC/cổng hai đầu, số NIC và ngân sách RAM; xác minh node/peer thực tế.
2. Chốt mapping GUI EVE/network_id và kế hoạch nối từng link. Hai trunk firewall phải là hai segment riêng, không LACP xuyên cặp HA; WAN/SYNC thiết kế riêng.
3. Khi được duyệt, thử T02–T09 với hai peer độc lập, capture nguồn/đích, FDB/counter và đối chứng dương. Endpoint chung EVE bridge có thể đi tắt ngoài OVS nên không đủ để chứng minh switching/mirror.
4. Kiểm thử SPAN ens10 theo thiết kế trong M2 sau khi sẵn sàng, có snapshot mới; không cần chạy Suricata đầy đủ. Triển khai sensor thật và mạng quản trị riêng cần chốt tài nguyên/topology.
5. Kiểm tra boot/persistence có backup và rollback khi tài nguyên sẵn sàng; chưa thực hiện trong checkpoint này.

Ở lần kiểm kê 00:14 ngày 01/11/2026, Windows còn khoảng 2,22 GiB và EVE khoảng 5,47 GiB available, chỉ Core đang chạy; không thấy image/node OPNsense/Suricata trong kho EVE đã khảo sát. Đây là số đo lịch sử, phải đo lại trước khi bật VM. Chưa có ngân sách chạy đồng thời cặp firewall, sensor và endpoint.

Core chỉ Layer 2; gateway liên VLAN dự kiến là CARP VIP trên OPNsense HA. IP/subnet/VIP trong M1 vẫn là đề xuất, không tự áp dụng. Không mở rộng quyền từ nhiệm vụ lưu GitHub sang thay đổi hệ thống.

## 6. Lưu GitHub và dữ liệu chỉ giữ cục bộ

Repository đích đã được tạo và xác minh **PRIVATE**: https://github.com/trannam12-05/SOC-Graduation-Project . Chủ sở hữu `trannam12-05`; nhánh `main`. Workspace ban đầu chưa có `.git`, không có lịch sử commit cũ; không có repository lồng nhau. SHA checkpoint và trạng thái remote cần đọc bằng `git log -1`, `git status -sb` và `git ls-remote origin refs/heads/main`.

`.gitignore` loại staging, private key/token/.env, image VM/ISO/gói offline/archive, DB raw/pcap, cache và dữ liệu truyền console trung gian. Giữ nguyên mọi tệp đó trên máy; không xóa hoặc di chuyển minh chứng cũ. Tệp `docs/evidence/eve-ng/ubuntu-image-test-config/node-config.json` có trường accountPassword chưa đủ rõ để đưa lên Git nên chỉ giữ cục bộ. Không khẳng định trường này là mật khẩu thật; bản gốc không bị sửa.

Giữ byte gốc bằng `.gitattributes` để không đổi checksum log/ảnh khi commit. Các báo cáo cũ vẫn giữ nguyên; bản sao trùng trong `docs/M2/backups/` chỉ lưu cục bộ. Một số danh mục lịch sử có thể trỏ tới tệp trung gian hoặc bản gốc chỉ có tại D:\SOC; không diễn giải danh mục đó thành cam kết mọi tệp đã lên GitHub. Xem [kiểm tra bàn giao GitHub](GITHUB_BACKUP.md).
