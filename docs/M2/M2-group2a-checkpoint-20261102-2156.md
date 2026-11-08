# 2. M2 Nhóm 2A — checkpoint tài nguyên trước khi bật Primary

Checkpoint lịch sử. Sau khi người dùng cho phép shutdown mềm Wazuh và mở shell Primary, Nhóm 2A đã hoàn tất; xem [báo cáo VLAN interface và backup](M2-group2a-primary-vlans-20261102.md). Nội dung dưới đây giữ nguyên trạng thái trước phê duyệt.

## 2.1. Trạng thái quan sát

Kiểm kê lúc 21:56:17 ngày 02/11/2026 (UTC+07:00) xác nhận OPNsense Primary đang tắt; Wazuh-SOC 4096 MiB và SOC-Core-L2 2048 MiB đang chạy. Primary khai báo 3072 MiB. Tổng nếu bật cả ba là 9216 MiB, vượt 7897 MiB RAM EVE nhìn thấy. MemAvailable thực tế tại thời điểm kiểm kê là khoảng 5101 MiB, swap đang dùng 0; không lấy mẫu bộ nhớ đang dùng thấp làm bảo đảm ba node sẽ không vượt tài nguyên khi tăng tải.

Chưa start Primary, chưa shutdown node nào, chưa đọc cấu hình hiện tại trong guest Primary, chưa tạo backup mới và chưa sửa cấu hình. Core Nhóm 1B giữ nguyên. Không thay OPNsense Secondary, WAN, SYNC, NAT, DHCP hoặc firewall rules; không thử lưu lượng.

Minh chứng: `docs/evidence/M2/group2a-20261102T215617+0700/inventory-before.json`.

## 2.2. Phương án tài nguyên chờ phê duyệt

Shutdown mềm riêng Wazuh-SOC, xác nhận tiến trình đã dừng rồi bật Primary; giữ Core chạy. Core + Primary dùng tổng RAM khai báo 5120 MiB. Không đổi RAM hoặc đĩa và không tự bật lại Wazuh sau nhóm này.

Đã hỏi người dùng cho phép shutdown mềm Wazuh. AGENTS.md mục 6 yêu cầu quyền riêng cho dừng VM/node; quyền bật Primary chưa được suy rộng thành quyền dừng Wazuh. Chờ câu trả lời trước khi thực hiện các bước phụ thuộc.

## 2.3. Dữ liệu địa chỉ tham chiếu và giới hạn

`network/ip-plan/vlan-ip-plan.md` là đề xuất M1, chưa phải toàn bộ quy hoạch đã xác nhận. `configs/M3/deployment-observed-20261102.json` ghi các địa chỉ Primary đã quan sát trên EVE:

| VLAN | Primary đã quan sát trước đây | Parent theo mapping lịch sử |
|---|---|---|
| 30 | 192.168.30.2/24 | vtnet0, cần đối chiếu cấu hình/runtime hiện tại |
| 40 | 192.168.40.2/24 | vtnet0, cần đối chiếu cấu hình/runtime hiện tại |
| 50 | 192.168.50.2/24 | vtnet0, cần đối chiếu cấu hình/runtime hiện tại |
| 60 | 192.168.60.2/24 | vtnet0, cần đối chiếu cấu hình/runtime hiện tại |
| 99 | 192.168.99.2/24 | vtnet0, cần đối chiếu cấu hình/runtime hiện tại |

Topology XML hiện tại nối Primary NIC 0/vtnet0 với Core trunk qua segment 1. Đây là dây theo XML; phải đối chiếu MAC trong guest trước khi sửa. Không dùng đề xuất CARP VIP .1 để tự gán gateway/VIP; không thêm static route cho mạng trực tiếp kết nối.

Sau khi được phép thực hiện phương án tài nguyên, tiếp tục đúng ba thao tác của Nhóm 2A: kiểm kê interface; backup root-only cấu hình Primary trước mọi thay đổi; chỉ hoàn thiện VLAN interface thực sự thiếu/sai theo dữ liệu đã xác nhận. Nếu địa chỉ/parent có sai lệch chưa rõ hoặc thiếu xác nhận, dừng trước khi sửa. Không đưa raw config.xml chứa mật khẩu hash, private key hoặc bí mật lên Git hoặc vào ảnh/log công khai.

## 2.4. Danh mục minh chứng hiện có

| Tệp | Nội dung | Thời điểm thu | Đường dẫn | Vị trí báo cáo |
|---|---|---|---|---|
| inventory-before.json | XML node/interface, tiến trình QEMU và RAM EVE trước mọi thay đổi | 2026-11-02T21:56:17+07:00 | docs/evidence/M2/group2a-20261102T215617+0700/inventory-before.json | Chương 2, Nhóm 2A, tiền kiểm tài nguyên |

Chưa có ảnh console Primary mới vì node chưa bật; không báo cáo ảnh chưa chụp hoặc backup chưa tạo là minh chứng đã có. Đây là checkpoint chờ quyền thao tác cần thiết, không phải nghiệm thu hoàn tất Nhóm 2A.
