# 1. Checkpoint xác định phạm vi M3

Thời điểm: 2026-11-04T10:25:14+07:00 (UTC+07:00). Kết quả: BLOCKED vì không có TODO M3 chưa DONE trong danh sách hiện hành. Đây là minh chứng rà soát tài liệu, không phải nghiệm thu runtime. Không thực hiện bước kỹ thuật trên EVE-NG; không thu ảnh runtime mới.

| Tệp | Nội dung | Thời điểm thu thập | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
| scope-check.json | Nguyên nhân BLOCKED, checkpoint và SHA-256 tài liệu nguồn | 2026-11-04T10:25:14+07:00 | docs/evidence/M3/todo-scope-check-20261104T102514/scope-check.json | M3 — giới hạn phạm vi và công việc còn lại |
| SOC_TO_DO.before.md | Bản sao TODO trước cập nhật | 2026-11-04T10:25:14+07:00 | docs/evidence/M3/todo-scope-check-20261104T102514/SOC_TO_DO.before.md | Phụ lục truy vết |
| PROGRESS.before.md | Bản sao tiến độ trước cập nhật | 2026-11-04T10:25:14+07:00 | docs/evidence/M3/todo-scope-check-20261104T102514/PROGRESS.before.md | Phụ lục truy vết |

M3.1 và M3.2 giữ kết quả lịch sử DONE/PASS. Failover/giữ phiên, CARP sau reboot riêng và WAN/NAT/DHCP HA chưa được nghiệm thu; không tự chuyển thành TODO mới. Không thay đổi cấu hình, topology, Core L2, VLAN/IP plan, node hoặc evidence cũ. Điểm tiếp tục: cần xác định rõ một TODO M3 mới trước khi triển khai hoặc kiểm thử phụ thuộc vào TODO đó.