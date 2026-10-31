# Tiến độ dự án SOC

Checkpoint ngày **01/11/2026, UTC+07:00 (Asia/Saigon)**. Dự kiến tiếp tục ngày 02/11/2026. Đọc `AGENTS.md` trước mọi thao tác; các giới hạn quyền trong phiên trước vẫn có hiệu lực.

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

Sau đó chuẩn bị và trình phạm vi riêng cho các bước chưa được duyệt:

1. Chọn endpoint VLAN-aware/capture, image hợp lệ, MAC/cổng hai đầu, số NIC và ngân sách RAM; xác minh node/peer thực tế.
2. Chốt mapping GUI EVE/network_id và kế hoạch nối từng link. Hai trunk firewall phải là hai segment riêng, không LACP xuyên cặp HA; WAN/SYNC thiết kế riêng.
3. Khi được duyệt, thử T02–T09 với hai peer độc lập, capture nguồn/đích, FDB/counter và đối chứng dương. Endpoint chung EVE bridge có thể đi tắt ngoài OVS nên không đủ để chứng minh switching/mirror.
4. Duyệt SPAN riêng trước khi đưa ens10 vào OVS/Mirror và chuẩn bị Suricata capture + NIC quản trị riêng.
5. Duyệt đợt restart/persistence riêng; chưa dừng hoặc restart node trong checkpoint này.

Ở lần kiểm kê 00:14 ngày 01/11/2026, Windows còn khoảng 2,22 GiB và EVE khoảng 5,47 GiB available, chỉ Core đang chạy; không thấy image/node OPNsense/Suricata trong kho EVE đã khảo sát. Đây là số đo lịch sử, phải đo lại trước khi bật VM. Chưa có ngân sách chạy đồng thời cặp firewall, sensor và endpoint.

Core chỉ Layer 2; gateway liên VLAN dự kiến là CARP VIP trên OPNsense HA. IP/subnet/VIP trong M1 vẫn là đề xuất, không tự áp dụng. Không mở rộng quyền từ nhiệm vụ lưu GitHub sang thay đổi hệ thống.

## 6. Lưu GitHub và dữ liệu chỉ giữ cục bộ

Repository đích đã được tạo và xác minh **PRIVATE**: https://github.com/trannam12-05/SOC-Graduation-Project . Chủ sở hữu `trannam12-05`; nhánh `main`. Workspace ban đầu chưa có `.git`, không có lịch sử commit cũ; không có repository lồng nhau. SHA checkpoint và trạng thái remote cần đọc bằng `git log -1`, `git status -sb` và `git ls-remote origin refs/heads/main`.

`.gitignore` loại staging, private key/token/.env, image VM/ISO/gói offline/archive, DB raw/pcap, cache và dữ liệu truyền console trung gian. Giữ nguyên mọi tệp đó trên máy; không xóa hoặc di chuyển minh chứng cũ. Tệp `docs/evidence/eve-ng/ubuntu-image-test-config/node-config.json` có trường accountPassword chưa đủ rõ để đưa lên Git nên chỉ giữ cục bộ. Không khẳng định trường này là mật khẩu thật; bản gốc không bị sửa.

Giữ byte gốc bằng `.gitattributes` để không đổi checksum log/ảnh khi commit. Các báo cáo cũ vẫn giữ nguyên; bản sao trùng trong `docs/M2/backups/` chỉ lưu cục bộ. Một số danh mục lịch sử có thể trỏ tới tệp trung gian hoặc bản gốc chỉ có tại D:\SOC; không diễn giải danh mục đó thành cam kết mọi tệp đã lên GitHub. Xem [kiểm tra bàn giao GitHub](GITHUB_BACKUP.md).
