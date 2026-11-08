# CHECKPOINT M1 — KẾT NỐI WAZUH ĐÃ BỔ SUNG — 05/11/2026, UTC+07:00

Theo quyền người dùng, đã kiểm kê, sao lưu topology rồi nối Wazuh-SOC e0 vào VLAN99-Management/network10. Thao tác thành công lúc 09:15:50; đọc lại độc lập lúc 09:16:43 xác nhận đủ 12/12 kiểm tra cấu trúc, chỉ thêm đúng interface, giữ 10 node/11 segment. Không bật/tắt node hoặc cấu hình IP; mọi node tiếp tục tắt.

[Báo cáo bổ sung M1](M1/M1-wazuh-link-verified-20261105.md), bản Word cùng tên; [danh mục minh chứng](evidence/M1/wazuh-link-20261105/evidence-index.csv). Backup trên EVE: /root/soc-m1-wazuh-link-20261105T091550Z. Chi tiết hash và phạm vi tại connection-result.json và independent-verification.json.

**M1: hồ sơ thiết kế và cấu trúc kết nối cơ sở đã hoàn thiện; còn ảnh topology GUI để đóng nghiệm thu.** Không có cửa sổ trình duyệt EVE đang mở; chưa thu ảnh thật mới. Hướng dẫn chụp nằm trong mục 1.5 báo cáo bổ sung. Chưa nghiệm thu IP Wazuh, đường log live hoặc chức năng mạng từ lần nối này. Internet là phần mở rộng, không phải điều kiện lab cơ sở. Các đoạn dưới đây về Wazuh chưa nối là lịch sử trước thay đổi.

---

