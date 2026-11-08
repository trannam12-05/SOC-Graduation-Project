# 2. M2 — Nhóm 1B: backup và đối chiếu Core Layer 2

## 2.1. Phạm vi và kết quả

Thời điểm thu backup theo máy Windows: 2026-11-02T21:44:54.159398+07:00. Trạng thái đối chiếu: **MATCH_CONFIRMED_CONFIGURATION**. Đây là kiểm tra cấu hình runtime; không kiểm thử lưu lượng, không chạy lại bộ 95 ca M2 đã đạt trước đây.

Ba thao tác được giao: khởi động riêng SOC-Core-L2; sao lưu OVSDB/cấu hình hiện tại về Windows; đối chiếu runtime trước khi quyết định sửa. Wazuh-SOC đã chạy từ trước, được giữ nguyên. Không bật node khác, không thay OPNsense hoặc kiến trúc Core.

## 2.2. Backup đã thu

- Backup OVSDB tại Windows: `D:\SOC\docs\evidence\M2\group1b-20261102T212014+0700\private-backups\ovsdb.snapshot`.
- Kích thước: 25764 byte; SHA-256: `7214fd7d9b55d4f4a0d949283963a1e26744b7e6936243ca76f4e95764541645`.
- Thư mục backup trong guest: `/root/m2-group1b-20261102-212014`.
- Tên database: `Open_vSwitch`; schema: `8.5.1`.
- Đã kiểm tra db-name/schema và compact bản sao bằng ovsdb-tool; không compact hoặc restore database đang chạy.
- Toàn bộ reply console và từng tệp được đối chiếu SHA-256 sau truyền. Không ghi đè backup cũ.

Cùng thư mục private-backups có `runtime.json`, `ovs-show.txt`, `systemd-units.txt` và `commands.jsonl`. Raw backup và dữ liệu console trung gian thuộc các đường dẫn được Git bỏ qua; không thực hiện commit/push. File manifest ghi tên, kích thước, đường dẫn và hash. Chưa thử restore backup trong lượt này.

## 2.3. Cấu hình runtime đã đọc

| Port | VLAN mode | Access tag | Trunk VLAN |
|---|---|---|---|
| ens3 | access | 30 | [] |
| ens4 | access | 40 | [] |
| ens5 | access | 50 | [] |
| ens6 | access | 60 | [] |
| ens7 | access | 99 | [] |
| ens8 | trunk | [] | [30, 40, 50, 60, 99] |
| ens9 | trunk | [] | [30, 40, 50, 60, 99] |
| ens10 | trunk | [] | [30, 40, 50, 60, 99] |
| br-core-l2 | access | 99 | [] |

NIC/MAC được đối chiếu với mapping đã xác nhận, không suy ofport từ tên ens. ens10 là cổng mirror output đã có, không chuyển thành cổng dữ liệu. Local port br-core-l2 thuộc VLAN 99, không phải NIC EVE bổ sung.

Boot ID hiện tại: `889ac878-8218-4e58-80b5-ae790802380e`. IPv4/IPv6 forwarding: `0/0`. Dịch vụ giữ Core không IP: `active`, trạng thái enable: `enabled`. Chi tiết dịch vụ OVS, MAC, địa chỉ, route, interface error và mirror nằm trong runtime.json; kết quả guard ở comparison.json.

## 2.4. Thay đổi và mục giữ nguyên

Không áp dụng thay đổi cấu hình trong lượt này. Không tạo VLAN/port/bond mới, không sửa SPAN. LACP (Link Aggregation Control Protocol — giao thức điều khiển gộp liên kết) không áp dụng: hai trunk đi tới hai firewall riêng, không có nhóm đường và peer phù hợp được xác nhận. Không cấu hình LACP.

SPAN/port mirroring: mirror span-suricata chọn ingress ens3–ens9 của VLAN 30/40/50/60/99, output ens10; không chọn chiều đích. Đối chiếu theo tên port/VLAN, không nhầm UUID hoặc ofport với định danh cố định qua boot.

## 2.5. Sai lệch và giới hạn

Runtime khớp guard cấu hình đã xác nhận: VLAN/access/trunk, ánh xạ MAC, mirror, Core không IP/gateway, forwarding tắt, interface không báo lỗi và các dịch vụ liên quan. Không có mục VLAN/trunk cần sửa theo dữ liệu thu được. Cấu hình Nhóm 1B đạt đối chiếu; không suy từ đó rằng kiểm thử lưu lượng tổng thể mới đã đạt.

## 2.6. Ảnh minh chứng

![Bảng VLAN access và trunk trên Core đang chạy](../evidence/M2/group1b-20261102T212014+0700/runtime-ports-20261102T214541+0700.png)

Hình 2.1. Bảng VLAN access và trunk trên Core đang chạy.

Mục đích: kiểm tra từng port. Nội dung/kết quả: mode, tag và trunk đọc từ OVS runtime. Ý nghĩa: đối chiếu cấu hình, không phải phép thử frame.

![Mirror hiện hành của Core](../evidence/M2/group1b-20261102T212014+0700/runtime-mirror-20261102T214552+0700.png)

Hình 2.2. Mirror hiện hành của Core.

Mục đích: xác nhận SPAN giữ nguyên. Nội dung/kết quả: bảng Mirror lấy trực tiếp từ console, thể hiện UUID cổng nguồn/đích và các VLAN; tên cổng được đối chiếu qua runtime.json và comparison.json. Ý nghĩa: trạng thái cấu hình quan sát được; không thay kiểm thử lưu lượng.

![Backup OVSDB và trạng thái dịch vụ](../evidence/M2/group1b-20261102T212014+0700/backup-proof-20261102T214603+0700.png)

Hình 2.3. Backup OVSDB và trạng thái dịch vụ.

Mục đích: xác nhận backup hiện hữu. Nội dung/kết quả: hash/schema backup và dịch vụ được đọc từ guest. Ý nghĩa: backup đã tạo và có thể đối chiếu hash với Windows, chưa thử restore.

## 2.7. Điểm dừng

Dừng sau Nhóm 1B và chờ người dùng xác nhận mới chuyển nhóm. Không triển khai OPNsense HA, không thử traffic, không tự tắt Core hoặc Wazuh. Checkpoint chờ đăng nhập trước đó được giữ làm lịch sử; báo cáo này phản ánh kết quả sau khi người dùng đăng nhập.

Danh mục ảnh/log/backup: `docs/evidence/M2/group1b-20261102T212014+0700/evidence-index-final.csv`. Bảng danh mục chỉ liệt kê tệp thực có, ghi thời điểm UTC+07:00 và vị trí báo cáo.
