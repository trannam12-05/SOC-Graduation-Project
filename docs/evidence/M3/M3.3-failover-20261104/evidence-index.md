# Checkpoint M3.3B — DONE/PASS — 2026-11-04T11:07:14.319327+07:00

[Danh mục BEFORE/FAILOVER/RECOVERY mới](run-105204/evidence-index.md). [Kết quả](run-105204/M3.3-acceptance.json). Failover PASS: Primary đã tắt, Secondary tự MASTER cả VLAN30/40/50/60/99, đủ VIP .1 và ARP qua Core; recovery PASS: Primary tự MASTER, Secondary BACKUP năm VLAN; pfsync UP/RUNNING, syncok1, demotion0 hai phía; Core/VLAN hoạt động. Không áp lại native pfsync hoặc sửa CARP để đạt kết quả.

Các mục bên dưới là lịch sử, giữ nguyên để truy vết.

---

# 1. M3.3 — Minh chứng trước kiểm thử

## 1.1. Kết quả

**BLOCKED** lúc 2026-11-04T10:27:35.821104+07:00 (UTC+07:00). Kiểm kê `/proc` trên EVE-NG không có QEMU chạy; điều kiện đầu không đúng. Chưa kiểm tra runtime trong guest, chưa failover/recovery, chưa xác minh pfsync hoặc VIP. M3.1/M3.2 giữ PASS lịch sử. Không thay đổi cấu hình hoặc vòng đời node. Điểm tiếp tục: khôi phục điều kiện đầu theo quyền riêng rồi thử lại M3.3; không làm mục khác.

## 1.2. Danh mục

| Tệp | Nội dung | Thời điểm thu (múi giờ) | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
| host-before.json | Kiểm kê QEMU rỗng, hash lab và backup metadata | 2026-11-04T10:27:35.821104+07:00 | docs/evidence/M3/M3.3-failover-20261104/host-before.json | M3.3 — điều kiện đầu và phụ lục truy vết |
| M3.3-result.json | BLOCKED, nguyên nhân và checkpoint | 2026-11-04T10:27:35.821104+07:00 | docs/evidence/M3/M3.3-failover-20261104/M3.3-result.json | M3.3 — điều kiện đầu và phụ lục truy vết |
| SOC_TO_DO.before.md | Bản sao TODO trước cập nhật | 2026-11-04T10:27:35.821104+07:00 | docs/evidence/M3/M3.3-failover-20261104/SOC_TO_DO.before.md | M3.3 — điều kiện đầu và phụ lục truy vết |
| PROGRESS.before.md | Bản sao tiến độ trước cập nhật | 2026-11-04T10:27:35.821104+07:00 | docs/evidence/M3/M3.3-failover-20261104/PROGRESS.before.md | M3.3 — điều kiện đầu và phụ lục truy vết |

Backup metadata lab root-only trên EVE: `/root/soc-resource-checkpoint-20261104T102737`. SHA-256 lab: `885368801d8bb7b8093f71fe8dca095f01ff7ad8339684963be0a3aed6bb7723`. Không có backup guest mới vì firewall không chạy; không truy cập/chỉnh QCOW2.

## 1.3. Giới hạn ảnh

Công cụ chụp console Primary không tìm thấy tiến trình QEMU nên không thu được ảnh. Không có ảnh runtime mới. Nếu bổ sung ảnh thủ công: mở lab SOC-M2-Core-L2 trên EVE-NG, giữ nguyên node, chụp toàn topology với tên/trạng thái node rõ ràng và lưu `topology-before-manual.png` tại thư mục này. Ảnh đó chưa được thu; không dùng ảnh cũ làm trạng thái hiện tại.
