# Ánh xạ cổng Core Layer 2 (M1)

## Trạng thái và nguyên tắc

Các cổng dưới đây được chép từ bảng 3.3 của Word. Báo cáo gọi tên interface IOSvL2 là **ví dụ**, yêu cầu xác nhận theo image/node thực tế; đây không phải mapping đã được xác nhận trên EVE-NG. Cột cổng phía thiết bị đích không được Word nêu nên để **chưa nêu**, không tự gán số cổng.

Core Switch chỉ làm Layer 2: VLAN, access/trunk, switching frame và SPAN. OPNsense xử lý gateway, inter-VLAN routing, firewall rules và NAT.

| Thiết bị nguồn | Cổng nguồn | Thiết bị/vùng đích trong Word | Cổng đích | Chế độ | VLAN được phép / VLAN access | SPAN | Trạng thái |
|---|---|---|---|---|---|---|---|
| Cisco IOSvL2 Core (ví dụ) | `Gi0/0` | OPNsense Primary LAN | Chưa nêu | Trunk 802.1Q | 30, 40, 50, 60, 99 | Không nêu là nguồn mirror | Mapping và tên cổng là đề xuất M1 |
| Cisco IOSvL2 Core (ví dụ) | `Gi0/1` | OPNsense Secondary LAN | Chưa nêu | Trunk 802.1Q | 30, 40, 50, 60, 99 | Không nêu là nguồn mirror | Mapping và tên cổng là đề xuất M1 |
| Cisco IOSvL2 Core (ví dụ) | `Gi0/2` | Data Center / thiết bị đầu cuối | Chưa nêu | Access | VLAN 30 | Không | Mapping đề xuất M1 |
| Cisco IOSvL2 Core (ví dụ) | `Gi0/3` | Employee / thiết bị đầu cuối | Chưa nêu | Access | VLAN 40 | Không | Mapping đề xuất M1 |
| Cisco IOSvL2 Core (ví dụ) | `Gi1/0` | Guest / thiết bị đầu cuối | Chưa nêu | Access | VLAN 50 | Không | Mapping đề xuất M1 |
| Cisco IOSvL2 Core (ví dụ) | `Gi1/1` | Management / thiết bị đầu cuối | Chưa nêu | Access | VLAN 99 | Không | Mapping đề xuất M1 |
| Cisco IOSvL2 Core (ví dụ) | `Gi1/2` | Suricata capture interface | Chưa nêu | SPAN destination | Không áp dụng | Cổng đích SPAN được đề xuất; **nguồn mirror chưa xác định** | Mapping đề xuất M1 |

## SPAN

M1 chỉ chỉ ra `Gi1/2` làm cổng đích cho Suricata; không xác định cổng/VLAN nguồn, hướng ingress/egress, hay cách bảo đảm quan sát lưu lượng khi HA failover. Cần chốt các điểm này theo khả năng của switch image và topology EVE-NG. Không cấu hình SPAN trong giai đoạn tài liệu này.

## Cần xác nhận

- Image/model switch, danh sách interface thực tế và cổng đích ở mỗi node.
- Cổng OPNsense WAN, LAN và SYNC tương ứng; mapping cổng vật lý/ảo tới node.
- VLAN tag, native VLAN nếu có, danh sách allowed VLAN cuối cùng.
- Thiết bị đầu cuối và cổng đích cụ thể cho từng access port.
- SPAN source port/VLAN, hướng mirror, băng thông và bao phủ khi Primary/Secondary đổi vai.
- Có một Core L2 trong M1; khả năng Core đơn là điểm lỗi đơn đã được Word lưu ý.
