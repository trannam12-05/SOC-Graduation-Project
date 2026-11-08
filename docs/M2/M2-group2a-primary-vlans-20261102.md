# 2. M2 — Nhóm 2A: VLAN interface trên OPNsense Primary

## 2.1. Kết quả và phạm vi

Đã hoàn tất kiểm tra cấu hình năm VLAN interface trên Primary. Cấu hình đã có đủ, đúng và đang UP; **không áp dụng thay đổi cấu hình**. Core tiếp tục Layer 2; không sửa OVS/SPAN. OPNsense Primary có IPv4 forwarding bằng 1 và route trực tiếp tới năm mạng VLAN. Chưa kiểm thử lưu lượng liên VLAN, chưa nghiệm thu firewall rules hoặc quyền truy cập giữa các vùng.

Ba thao tác của Nhóm 2A: chuẩn bị tài nguyên và bật Primary; backup cấu hình trước mọi thay đổi; đối chiếu VLAN/parent/tag/IP và giữ nguyên phần đúng. Không thêm static route, CARP VIP, gateway hoặc rule. Không thay WAN, SYNC, NAT, DHCP hay OPNsense Secondary.

## 2.2. Nhóm tài nguyên đã sử dụng

Trước nhóm này, Wazuh-SOC 4096 MiB và Core 2048 MiB đang chạy, Primary 3072 MiB tắt. Bật cả ba sẽ cần tổng RAM khai báo 9216 MiB, lớn hơn RAM EVE nhìn thấy 7897 MiB. Sau khi người dùng phê duyệt riêng, đã gửi `systemctl poweroff` trong Wazuh, xác nhận QEMU Wazuh dừng rồi mới start Primary. Core giữ nguyên và không khởi động lại.

Nhóm thực hiện gồm Core + Primary, tổng 5120 MiB. Kiểm kê sau start xác nhận đúng hai node này; EVE MemAvailable khoảng 4505 MiB, swap dùng 0 tại mốc thu. Wazuh giữ tắt sau nhóm; Secondary không bật. Không đổi RAM/đĩa, image, seed hoặc dây mạng.

Minh chứng tài nguyên: `inventory-before.json`, `inventory-after-wazuh-shutdown.json`, `inventory-primary-running.json` trong `docs/evidence/M2/group2a-20261102T215617+0700/`. Receipt start Primary ở `docs/evidence/M2/topology-first-20261102/start-OPNsense-Primary-220531.json`. Các thời điểm máy thu dùng UTC+07:00; không suy đồng hồ guest là chính xác.

## 2.3. Cơ sở địa chỉ và định danh cổng

`network/ip-plan/vlan-ip-plan.md` vẫn là đề xuất M1. Đối chiếu trong nhóm này dùng các địa chỉ **đã được quan sát triển khai trước đây** trong `configs/M3/deployment-observed-20261102.json`, kết hợp XML/runtime hiện tại; không nâng các VIP đề xuất thành địa chỉ được phép gán mới.

Primary vtnet0 có MAC `50:00:00:01:00:00`, khớp mapping đã xác minh trước đây; NIC 0 nối segment trunk 1 tới Core. Cả năm định nghĩa VLAN trong cấu hình và kết quả ifconfig đều chỉ ra parent vtnet0 và tag tương ứng. Không suy tên interface từ riêng tên VLAN; đã đối chiếu assignment, định nghĩa VLAN và runtime.

VLAN (Virtual Local Area Network — mạng LAN ảo) phân vùng mạng ở Layer 2. Inter-VLAN Routing — định tuyến giữa các VLAN — sử dụng các interface Layer 3 của OPNsense để chuyển gói giữa các mạng trực tiếp kết nối, chịu điều khiển của chính sách firewall. Trong topology này, Core mang các tag trên trunk còn Primary sở hữu các địa chỉ .2/24 bên dưới. Bằng chứng hiện tại xác nhận cấu hình interface và route; chưa xác nhận lưu lượng xuyên vùng được cho phép. Không đặt gateway hoặc IP định tuyến lên Core.

## 2.4. Cấu hình VLAN interface trước/sau

| VLAN | Assignment / thiết bị | Parent | Tag | IPv4 trước | IPv4 sau | Trạng thái / xử lý |
|---|---|---|---|---|---|---|
| 30 | OPT1 / vtnet0_vlan30 | vtnet0 | 30 | 192.168.30.2/24 | 192.168.30.2/24 | Enabled, UP; giữ nguyên |
| 40 | OPT2 / vtnet0_vlan40 | vtnet0 | 40 | 192.168.40.2/24 | 192.168.40.2/24 | Enabled, UP; giữ nguyên |
| 50 | OPT3 / vtnet0_vlan50 | vtnet0 | 50 | 192.168.50.2/24 | 192.168.50.2/24 | Enabled, UP; giữ nguyên |
| 60 | OPT4 / vtnet0_vlan60 | vtnet0 | 60 | 192.168.60.2/24 | 192.168.60.2/24 | Enabled, UP; giữ nguyên |
| 99 | OPT5 / vtnet0_vlan99 | vtnet0 | 99 | 192.168.99.2/24 | 192.168.99.2/24 | Enabled, UP; giữ nguyên |

Kết quả máy đối chiếu: `MATCH_EXISTING_VLAN_CONFIGURATION`, không có mục sai lệch. Đã đối chiếu MAC parent, assignment duy nhất, tag/parent trong ifconfig, địa chỉ và netmask 0xffffff00, cờ UP và enable. `primary-comparison.json` ghi từng điều kiện. Bảng trước/sau giống nhau vì không có lệnh ghi cấu hình; hash toàn bộ config hiện hành được đọc lại sau backup và bằng đúng bản backup.

IPv4 forwarding hiện hành bằng 1. `netstat -rn -f inet` có các route trực tiếp 192.168.30.0/24, 192.168.40.0/24, 192.168.50.0/24, 192.168.60.0/24 và 192.168.99.0/24 tới các VLAN interface tương ứng. Không thêm static route cho các mạng này. Việc có route không thay cho kiểm thử firewall hoặc lưu lượng.

## 2.5. Backup cấu hình và kiểm tra tính toàn vẹn

Backup đầy đủ thực tế nằm **bên trong guest Primary**, trên filesystem ổ cứng `/dev/gpt/rootfs`, không phải Live ISO:

`/root/soc-group2a-20261102-215617/config.xml`

Thư mục có mode 0700, tệp mode 0600; tạo bằng cơ chế không ghi đè tệp có sẵn. Nội dung được sao chép nguyên byte từ `/conf/config.xml`, flush/fsync rồi kiểm hash. SHA-256:

`2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2`

Đọc lại độc lập lúc 22:22:35 UTC+07:00 xác nhận hash `/conf/config.xml` bằng hash backup và bằng hash tại thời điểm tạo. Vì vậy toàn bộ cấu hình giữ nguyên giữa hai mốc, bao gồm các phần WAN, SYNC, NAT, DHCP, firewall model, VIP và gateway. Không restore hoặc reload/apply cấu hình trong nhóm này.

Windows chỉ lưu `primary-audit-before.json`, `primary-comparison.json`, `final-integrity.json` và ảnh/log công khai trong `docs/evidence/M2/group2a-20261102T215617+0700/`. Không truyền raw config.xml qua ảnh console, không đưa mật khẩu hash, chứng thư, private key hoặc API key vào dữ liệu công khai/Git. Chưa tạo bản backup đầy đủ ngoài VM và chưa thử restore; không trình bày các việc này là đã hoàn thành.

## 2.6. Phương pháp và giới hạn công cụ

Sau khi người dùng đăng nhập root và mở Shell, đã chuyển script chỉ đọc/backup có checksum. Các lần gọi background đầu gặp lỗi cú pháp chuyển hướng output/cú pháp dòng nhập trên shell csh; ảnh lỗi được giữ nguyên. Đã hủy dòng nhập, kiểm tra thư mục backup chưa có rồi gọi trực tiếp bằng lệnh ngắn. Script này tạo backup và xuất duy nhất các trường interface/VLAN, runtime và hash cần thiết. Không có sửa cấu hình từ các lệnh lỗi hoặc lần chạy thành công.

JSON công khai được nén và truyền qua console theo từng trang; khôi phục chỉ khi glyph khớp chính xác và SHA-256 toàn payload khớp. So khớp lại toàn bộ hash cấu hình hiện hành/backup sau bước thu thập. Không suy PASS từ riêng ảnh menu console hoặc trạng thái dịch vụ.

## 2.7. Thông số còn thiếu và điểm dừng

Không thiếu parent/tag/IP/mask/enable của năm VLAN hiện có để hoàn tất phạm vi gán interface Nhóm 2A. Quy hoạch M1 vẫn cần được cập nhật hành chính để phản ánh trạng thái triển khai đã thu. Các giá trị CARP VIP, gateway client, WAN/upstream và chính sách firewall chưa được chốt/nghiệm thu bởi nhóm này; không tự bổ sung hoặc xác nhận thay người dùng.

**Dừng sau Nhóm 2A, chờ người dùng xác nhận “TIẾP TỤC”.** Giữ Core và Primary chạy, Wazuh tắt theo quyền đã duyệt; không tự chuyển sang rules, DHCP, NAT, HA hoặc kiểm thử lưu lượng.

Danh mục minh chứng hiện có được lưu tại `docs/evidence/M2/group2a-20261102T215617+0700/evidence-index-final.csv`, gồm tên tệp, nội dung, thời điểm/múi giờ, đường dẫn, vị trí báo cáo và SHA-256.

## 2.8. Ảnh console thực tế

![Parent, tag và địa chỉ VLAN trên Primary](../evidence/M2/group2a-20261102T215617+0700/vlan-config-table-20261102T222255+0700.png)

Hình 2.1. Bảng cấu hình VLAN interface hiện hành của Primary.

Mục đích là kiểm tra parent, VLAN tag, thiết bị được gán và địa chỉ IPv4. Lệnh chỉ đọc các trường đã chọn từ cấu hình thực tế và hiển thị đủ năm dòng VLAN. Kết quả xác nhận vtnet0 là parent, tag 30/40/50/60/99 và các địa chỉ .2/24 giữ nguyên. Ý nghĩa là xác nhận cấu hình có sẵn; trạng thái enable/UP và địa chỉ trên hệ điều hành được kiểm riêng trong JSON runtime, không suy chỉ từ XML.

![Route trực tiếp và IPv4 forwarding](../evidence/M2/group2a-20261102T215617+0700/connected-routes-20261102T222320+0700.png)

Hình 2.2. Route trực tiếp của các mạng VLAN và trạng thái IPv4 forwarding.

Mục đích là quan sát bảng định tuyến sẵn có. Các mạng VLAN có route link trực tiếp; sysctl trả net.inet.ip.forwarding: 1. Netstat hiển thị tên Netif theo độ rộng cột, nên tên đầy đủ được đối chiếu từ ifconfig trong JSON runtime. Kết quả không yêu cầu bổ sung static route; ý nghĩa giới hạn ở trạng thái định tuyến, không chứng minh traffic đã qua firewall.

![Backup root-only và SHA-256](../evidence/M2/group2a-20261102T215617+0700/backup-permissions-20261102T222329+0700.png)

Hình 2.3. Quyền truy cập và checksum bản sao cấu hình Primary.

Mục đích là xác nhận backup thực sự hiện hữu và được bảo vệ. Ảnh hiển thị thư mục root:wheel chỉ chủ sở hữu truy cập, tệp chỉ root đọc/ghi và SHA-256 khớp manifest. Kết quả xác nhận backup root-only trên guest; không hiển thị nội dung config.xml. Thời gian sửa tệp trong ls theo đồng hồ guest, không thay thời điểm máy thu trong danh mục. Ý nghĩa không bao gồm kiểm thử restore hoặc bản sao ngoài VM.
