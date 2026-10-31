# Danh mục minh chứng chốt giai đoạn đầu Core M2

## 1. Tài liệu hiện hành

- [Báo cáo Word chốt](../../M2/M2-report-stage1-core-preparation-20261031-final.docx).
- [Báo cáo Markdown chốt](../../M2/M2-report-stage1-core-preparation-20261031-final.md).
- [Danh mục ảnh và log ban đầu của giai đoạn](M2-core-stage1-evidence-index-20261031.md), [CSV ảnh](M2-core-stage1-evidence-index-20261031.csv).
- [Snapshot v2 chốt](M2-core-stage1-final-status-v2-20261031.json): trạng thái node, 8 NIC, không process/runtime, checksum cũ và RAM mới nhất.
- [Payload v2](M2-core-stage1-payload-v2-20261031.json): bundle/seed mới, hash và mục tạm 0 byte đã loại khỏi phát hành; v1 vẫn giữ.
- [Seed status v2](M2-core-stage1-seed-status-v2-20261031.json), [bundle validation v2](M2-core-stage1-bundle-validation-v2-20261031.json), [APT log v2](M2-core-stage1-apt-offline-check-v2-20261031.log).
- [Manifest 70 package không đổi giữa v1/v2](M2-core-stage1-package-manifest-20261031.json), [CSV package](M2-core-stage1-packages-20261031.csv), [metadata manifest](M2-core-stage1-metadata-manifest-20261031.json).
- `M2-core-stage1-SHA256SUMS-20261031.txt`: checksum bộ tài liệu/minh chứng giai đoạn, gồm các bản được bảo toàn.

## 2. Danh mục ảnh thật

| Tên ảnh | Nội dung | Thời điểm UTC+07:00 | Đường dẫn | Vị trí báo cáo |
|---|---|---|---|---|
| [M2-core-seed-ready-real-terminal-20261031.png](M2-core-seed-ready-real-terminal-20261031.png) | Terminal thật hoàn tất seed trước khi làm sạch payload v2; không chứa mật khẩu/hash | 31/10/2026 19:55:46 | docs/evidence/M2/M2-core-seed-ready-real-terminal-20261031.png | Hình 2.3, mục 2.10 |
| [M2-core-stopped-eight-nics-real-terminal-20261031.png](M2-core-stopped-eight-nics-real-terminal-20261031.png) | Terminal kiểm tra live: status0, 8 MAC không link, disk8GiB, bundle/seed chuẩn bị; không là guest console | 31/10/2026 19:57:58 | docs/evidence/M2/M2-core-stopped-eight-nics-real-terminal-20261031.png | Hình 2.4, mục 2.12 |

Ảnh chụp nguyên cửa sổ bằng Win32 PrintWindow, đã xem kiểm tra, không sửa nội dung kỹ thuật. Ảnh không chứa checksum v2; dùng snapshot v2 và manifest để xác nhận media hiện hành. Hai ảnh và CSV cũ được giữ nguyên, không ghi đè bằng ảnh giả.

## 3. Trạng thái nghiệm thu

Đã hoàn tất chuẩn bị image QCOW2 độc lập 8 GiB, seed quản trị riêng và node Core tắt 1CPU/2048MiB/8vNIC không link; bundle OVS 3.3.9 gồm 70 gói Noble amd64/all đã xác thực. Chưa boot Core, chưa thử cloud-init/login/NIC/kernel/filesystem trong guest, chưa cài OVS, chưa bridge/VLAN/trunk/mirror. Windows RAM ở snapshot v2 dưới ngưỡng đề xuất; chờ người dùng xử lý và duyệt boot.

Chưa có ảnh topology/settings GUI EVE trực tiếp. Người dùng có thể mở lab SOC-M2-Core-L2, chụp topology node tắt và settings Ethernet=8 bằng Snipping Tool, lưu PNG nguyên bản kèm thời điểm vào docs/evidence/M2 để bổ sung. Ảnh terminal không được đổi nhãn thành ảnh topology.
