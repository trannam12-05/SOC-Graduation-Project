# Danh mục minh chứng tiền kiểm tra kế hoạch Core L2

## 1. Phạm vi

Ngày 31/10/2026, múi giờ báo cáo UTC+07:00. Đây là minh chứng **đọc trạng thái và mã nguồn để lập kế hoạch**, không phải kết quả triển khai `SOC-Core-L2`. Không tạo node, image, seed, tăng NIC, cài OVS, sửa mạng hoặc thay vòng đời VM.

| Tên tệp | Nội dung | Thời điểm và nguồn giờ | Đường dẫn từ gốc dự án | Vị trí báo cáo |
|---|---|---|---|---|
| [JSON tiền kiểm tra](M2-core-l2-plan-readonly-20261031T1856+0700.json) | Template, mã API/GUI/sinh NIC có số dòng, checksum base, CPU/RAM/đĩa, node đang chạy | Phiên đọc quanh mốc Windows 18:56:12 UTC+07:00; giờ EVE ghi riêng và chưa đồng bộ | `docs/evidence/M2/M2-core-l2-plan-readonly-20261031T1856+0700.json` | Mục 2 và phụ lục kế hoạch |
| [JSON kiểm tra cuối](M2-core-l2-plan-final-check-20261031.json) | So hash template/lab/seed, PID/UUID hai guest; xác nhận chưa có Core/image mới | Đọc cuối phiên, Windows ghi nhận trước 19:06:45 UTC+07:00; JSON chứa giờ EVE không dùng làm giờ chuẩn | `docs/evidence/M2/M2-core-l2-plan-final-check-20261031.json` | Mục 2.1 và phụ lục bảo toàn |
| [Log tóm tắt](M2-core-l2-plan-review-20261031.log) | Kết quả đã xác minh, giới hạn, đề xuất chưa làm | Tổng hợp sau lần đọc cuối, ngày 31/10/2026 UTC+07:00 | `docs/evidence/M2/M2-core-l2-plan-review-20261031.log` | Phụ lục thao tác chỉ đọc |
| [Kế hoạch triển khai](../../M2/core-l2-implementation-plan.md) | Port map, M2/M3, offline OVS, thuật ngữ, nghiệm thu, kế hoạch ảnh và quyền cần duyệt | Ngày lập 31/10/2026 UTC+07:00 | `docs/M2/core-l2-implementation-plan.md` | Phần thiết kế M2; chưa là kết quả thực nghiệm |

## 2. Ảnh đã có và ảnh chưa có

- Ảnh cloud-init, hostname/NIC/CPU/RAM của `Ubuntu-Console-Test` đã có ở [danh mục bước Ubuntu](M2-evidence-index-20261031T1844+0700.md). Giữ nguyên và chỉ dùng đúng node/ý nghĩa đã kiểm chứng.
- Chưa có ảnh `SOC-Core-L2`, 8 NIC runtime, cài OVS, bridge, VLAN/trunk/mirror vì chưa được triển khai. Mục 10 của kế hoạch liệt kê tên dự kiến, nội dung màn hình cần chụp, caption và số hình tương lai.
- Sơ đồ Mermaid là bản vẽ thiết kế, không phải screenshot EVE hoặc minh chứng nghiệm thu. Không tạo PNG giả lập để thay ảnh thật.
- Nếu không chụp GUI trực tiếp được, người dùng chụp topology/settings bằng công cụ Windows, giữ toàn bộ kết quả quan trọng và loại thông tin nhạy cảm khỏi màn hình trước chụp.

## 3. Kết quả và giới hạn

Đạt việc lập kế hoạch và xác minh tĩnh cơ chế đặt 8 NIC riêng node. Chưa nghiệm thu API tạo node, boot 8 NIC, package/dependency offline, datapath hoặc HA. Windows ít RAM vật lý khả dụng ở mẫu đo; phải kiểm tra lại trước boot. Hai node kiểm chứng và tài nguyên hiện hữu được giữ nguyên trong phiên này.

Checksum của bộ tài liệu tiền kiểm tra nằm trong `M2-core-l2-plan-SHA256SUMS-20261031.txt`; manifest cũ của bước cloud-init không được cập nhật hoặc ghi đè.
