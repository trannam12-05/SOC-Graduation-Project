# Tiến độ dự án SOC

## Mốc tiếp quản khẩn cấp — 01/11/2026, 12:57 UTC+07:00

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
