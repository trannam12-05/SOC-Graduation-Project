# CHƯƠNG 1. NGHIỆM THU CUỐI M1 — THIẾT KẾ VÀ TOPOLOGY LAB NỘI BỘ

## 1.1. Kết quả

Ngày 05/11/2026, M1 đạt yêu cầu trong phạm vi lab nội bộ: thiết kế Core Layer 2, năm VLAN, cặp OPNsense, hai đường WAN cô lập, mạng SYNC, SPAN/Suricata, endpoint đại diện và Wazuh trên VLAN 99 đã được thể hiện trong hồ sơ và topology EVE-NG. Internet/upstream là phần mở rộng dự kiến theo lựa chọn của người dùng.

Kết nối Wazuh e0 vào `VLAN99-Management` đã được bổ sung lúc 09:15:50 UTC+07:00. Kiểm tra XML độc lập lúc 09:16:43 xác nhận 12/12 điều kiện cấu trúc đạt, giữ nguyên 10 node và 11 segment. Không node nào được bật/tắt và không cấu hình IP trong thao tác này.

![Topology EVE-NG sau khi nối Wazuh vào VLAN 99](../evidence/M1/wazuh-link-20261105/topology-overview-20261105T091848+0700.png)

**Hình 1.2. Topology EVE-NG của lab SOC nội bộ sau khi bổ sung kết nối Wazuh.**

Mục đích của hình là đối chiếu thiết kế M1 với topology thực tế trên EVE-NG. Ảnh chụp thật lúc 09:18:48 UTC+07:00 hiển thị 10 node, hai firewall OPNsense, Core L2, năm vùng VLAN, đường SPAN tới Suricata, hai WAN cô lập và đường Wazuh e0 tới segment `VLAN99-Management`. Kết quả xác nhận liên kết được hiển thị trên GUI và phù hợp với XML đã đọc độc lập. Ý nghĩa của hình là hoàn tất minh chứng cấu trúc topology M1; ảnh không chứng minh IP Wazuh, truyền log live hoặc dịch vụ trong guest.

Nhãn đỏ “NIC chưa nối: cần xác nhận VLAN” cạnh Wazuh là textobject lịch sử trên canvas, chưa được cập nhật sau thao tác. Đường màu xanh từ `VLAN99-Management` tới Wazuh e0 đã hiện rõ; kết quả kỹ thuật được đối chiếu thêm bằng `connection-result.json` và `independent-verification.json`. Không chỉnh sửa nội dung ảnh để che nhãn cũ.

## 1.2. Bảng nghiệm thu

| Hạng mục | Kết quả | Minh chứng và giới hạn |
|---|---|---|
| Sơ đồ topology EVE-NG hoàn chỉnh trong phạm vi lab nội bộ | PASS | Hình 1.2; 10 node, 11 segment |
| Bảng VLAN, subnet, gateway | PASS | Bản thiết kế hợp nhất; VIP `.1`, Primary `.2`, Secondary `.3` đã được kiểm chứng M3 |
| VLAN 30/40/50/60/99 | PASS về thiết kế và cấu trúc | M2 kiểm chứng access/trunk; không suy mọi endpoint đã cấu hình IP |
| Core chỉ hoạt động Layer 2 | PASS | M2 đã nghiệm thu; đợt chụp M1 không boot lại Core |
| Wazuh nối mạng Management | PASS về cấu trúc | GUI và XML; chưa kiểm tra guest/IP/log live |
| Internet/upstream | Không thuộc phạm vi cơ sở | Hai WAN giữ cô lập, là phần mở rộng dự kiến |
| Ảnh topology thật, rõ và không chứa bí mật | PASS | Ảnh PNG nguyên bản, không chỉnh sửa nội dung kỹ thuật |

Kết luận: **M1 hoàn thành trong phạm vi thiết kế và topology lab nội bộ.** Các giá trị IP Wazuh/Suricata mới, DHCP, NAT Internet, pipeline log live và automation block IP thuộc các đầu việc M3–M5; không được xem là đã nghiệm thu từ M1.

## 1.3. Tài liệu liên quan

- Báo cáo thiết kế: `docs/M1/M1-design-consolidated-20261105.md` và bản Word cùng tên.
- Báo cáo kết nối Wazuh: `docs/M1/M1-wazuh-link-verified-20261105.md` và bản Word cùng tên.
- Minh chứng: `docs/evidence/M1/wazuh-link-20261105/evidence-index.csv`.
- Sơ đồ nguồn: `network/topology/M1-internal-lab-20261105.mmd`.
