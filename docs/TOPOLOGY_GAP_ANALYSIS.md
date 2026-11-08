# 1. Phân tích chênh lệch topology SOC

## 1.1. Nguồn và phạm vi

Ngày 02/11/2026, UTC+07:00. Nguồn chính do người dùng xác nhận: Word M1 trong workspace, hình 2.1 nhúng và các tài liệu M2–M4. Không tìm thấy bản .drawio/.vsdx/.unl/.pdf trong workspace; danh mục toàn bộ ảnh/Word/sơ đồ ở `evidence/M1/topology-source-review-20261102/design-file-inventory.json`. Các Word M2/M3 là báo cáo triển khai từng phần, không thay thế sơ đồ kiến trúc M1.

Hình M1 được trích nguyên byte tại `evidence/M1/topology-source-review-20261102/image1.png`; đây là sơ đồ thiết kế, không phải screenshot EVE. M1 mục 2.2 nói rõ hình logic không thể hiện đầy đủ số lượng node/cổng vật lý.

## 1.2. Kiểm kê hiện hành trước thay đổi

SSH đã xác thực; kiểm kê 2026-11-02T12:57:30.721516+07:00. Lab `/opt/unetlab/labs/SOC-M2-Core-L2.unl`, UUID `f39cfc8c-5eaf-461e-bb0c-60b5fde848b7`, có 3 node, 3 segment/link; không QEMU đang chạy. Cả hai firewall có 3 NIC; Core có 8 NIC. Không chạy lại suite VLAN đã đạt. Bằng chứng: `evidence/M2/topology-first-20261102/inventory-before.json`.

| Thành phần theo thiết kế | Đã tồn tại | NIC cần | Gap / trạng thái thực tế |
|---|---|---|---|
| OPNsense-Primary (Firewall) | Có | 4 | Primary đã cài/boot theo minh chứng M3 ngày 01/11; guest hiện tắt, gateway/HA chưa VERIFIED; M1 hình 2.1; M3 mapping vtnet0 LAN, vtnet1 WAN1, vtnet2 SYNC; NIC bổ sung dành WAN2 |
| OPNsense-Secondary (Firewall) | Có | 4 | Node hiện có; cài đặt guest chưa xác minh; M1 hình 2.1 và bảng 2.1; cùng vai trò NIC Primary |
| SOC-Core-L2 (Core) | Có | 8 | Core đã CONFIGURED và VERIFIED trong phạm vi 95 ca M2 ngày 01/11; không suy thành E2E VERIFIED; M2 mapping đã kiểm chứng; giữ nguyên tám MAC và cấu hình guest |
| Data-Center (VLAN 30) | Chưa có | 1 | Thiếu node; sẽ CREATED_NOT_INSTALLED khi tạo, không đồng nghĩa đã cài dịch vụ; M1 hình 2.1 và bảng 3.2; đại diện vùng, chưa xác định ứng dụng máy chủ |
| Employee (VLAN 40) | Chưa có | 1 | Thiếu node; sẽ CREATED_NOT_INSTALLED khi tạo, không đồng nghĩa đã cài dịch vụ; M1 hình 2.1 và bảng 3.3; endpoint đại diện |
| Guest (VLAN 50) | Chưa có | 1 | Thiếu node; sẽ CREATED_NOT_INSTALLED khi tạo, không đồng nghĩa đã cài dịch vụ; M1 hình 2.1 và bảng 3.3; endpoint đại diện |
| DMZ (VLAN 60) | Chưa có | 1 | Thiếu node; sẽ CREATED_NOT_INSTALLED khi tạo, không đồng nghĩa đã cài dịch vụ; M1 hình 2.1 và bảng 3.2; chưa chốt Web/DNS là bao nhiêu máy riêng |
| Management (VLAN 99) | Chưa có | 1 | Thiếu node; sẽ CREATED_NOT_INSTALLED khi tạo, không đồng nghĩa đã cài dịch vụ; M1 hình 2.1 và bảng 3.3; endpoint quản trị đại diện |
| Suricata-NIDS (SOC) | Chưa có | 2 | Thiếu node; sẽ CREATED_NOT_INSTALLED khi tạo, không đồng nghĩa đã cài dịch vụ; M1 hình 2.1; M4 mục 4.1/4.2: capture riêng, management riêng |
| Wazuh-SOC (SOC) | Chưa có | 1 | Thiếu node; sẽ CREATED_NOT_INSTALLED khi tạo, không đồng nghĩa đã cài dịch vụ; M1 hình 2.1 và bảng 2.1; VLAN/NIC vật lý tới mạng SOC chưa được chỉ định |

## 1.3. Đối chiếu dây và interface

| Nguồn/interface EVE | Đích/interface EVE | Chức năng | Trước thay đổi |
|---|---|---|---|
| SOC-Core-L2/5 | OPNsense-Primary/0 | Trunk Primary | Đúng theo XML hiện hành |
| SOC-Core-L2/6 | OPNsense-Secondary/0 | Trunk Secondary | Đúng theo XML hiện hành |
| OPNsense-Primary/2 | OPNsense-Secondary/2 | HA SYNC riêng | Đúng theo XML hiện hành |
| SOC-Core-L2/0 | Data-Center/0 | Access VLAN 30 | Thiếu |
| SOC-Core-L2/1 | Employee/0 | Access VLAN 40 | Thiếu |
| SOC-Core-L2/2 | Guest/0 | Access VLAN 50 | Thiếu |
| SOC-Core-L2/3 | DMZ/0 | Access VLAN 60 | Thiếu |
| SOC-Core-L2/4 | Management/0 | Access VLAN 99 | Thiếu |
| SOC-Core-L2/7 | Suricata-NIDS/0 | SPAN capture không IP | Thiếu |
| Suricata-NIDS/1 | Management/0 | Cùng segment Management theo M4; không nối trực tiếp NIC đã dùng | Thiếu |
| WAN-ISP-1 | vtnet1 mỗi firewall | Shared L2 WAN1 | Thiếu |
| WAN-ISP-2 | NIC thứ 4 mỗi firewall | Shared L2 WAN2 | Thiếu NIC và segment |

Core EVE e0–e7 đã kiểm kê; tương ứng ens3–ens10 theo MAC M2. Firewall vtnet0 LAN, vtnet1 WAN1, vtnet2 SYNC giữ nguyên. NIC thứ tư dự kiến WAN2; tên vtnet3 cần xác minh sau boot, chưa gán interface guest. Không thấy link sai trong ba link hiện có; chưa kiểm thử lưu lượng qua các link đó.

## 1.4. Image và cài đặt

Kho EVE hiện có `opnsense-26.7-soc` (đĩa nền trống và ISO cài), `linux-ubuntu-24.04-ovs` (Ubuntu cloud image), image Core và console-test. Không có image chứa Suricata/Wazuh đã cài. Dùng Ubuntu nền cho các node dịch vụ là hệ điều hành dự kiến; tuyệt đối không báo dịch vụ đã cài chỉ từ tên node. VPCS binary đã kiểm kê cho endpoint đơn giản. Không dùng image/seed Core để nhân bản các máy dịch vụ.

## 1.5. Điểm chưa thống nhất và chưa xác định

- Internet/upstream chưa có node/image/interface chỉ định: giữ WAN bridge cô lập, không nối pnet/VMware
- Wazuh VLAN/IP và đường vật lý chưa chỉ định: tạo node giữ tắt, chưa nối NIC, chưa mô phỏng mũi tên log thành dây trực tiếp
- Automation có trong bảng 2.1 nhưng chưa xác định máy riêng: ghi thành phần logic, không tự tạo thêm node
- Số lượng máy chủ DC, Web/DNS DMZ, client mỗi vùng và máy SOC chưa có danh sách vật lý; mỗi vùng chỉ một endpoint đại diện
- Địa chỉ IP/VIP, policy, DHCP, WAN2/SYNC guest chưa xác nhận; không tự áp dụng IP dự kiến
- M1 đề xuất IP quản trị Core; M2 đã kiểm chứng Core không IP. Giữ Core không IP, không áp dụng lại đề xuất M1.
- M1 bảng 3.3 thiếu dòng DMZ trong khi hình 2.1 có DMZ; dùng ens6/access60 đã cấu hình và kiểm chứng M2, không thêm Core thứ hai.

## 1.6. Tiêu chí trạng thái

`TOPOLOGY_READY`: đối chiếu đủ node/link vật lý được xác định. `CONFIGURED`: có cấu hình thực tế trên guest. `VERIFIED`: có kiểm thử và minh chứng đúng phạm vi. `CREATED_NOT_INSTALLED`: node tồn tại nhưng chưa cài hoặc chưa xác minh hệ điều hành/dịch vụ. Không đánh dấu toàn mô hình TOPOLOGY_READY khi Wazuh/upstream và số lượng máy chưa đủ đặc tả; có thể đánh dấu từng link/nhóm đã đủ.

## 1.7. Kết quả sau dựng

Chưa thực thi tại thời điểm tạo gap analysis; kết quả sau thay đổi phải đối chiếu `TOPOLOGY_FIRST_HANDOFF.md` và inventory-after, không suy từ kế hoạch.
