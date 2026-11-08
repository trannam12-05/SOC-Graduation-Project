# Giới hạn ảnh và hướng dẫn chụp thủ công

## 1. Minh chứng đã có

resources-before.json và eve-free/vmstat/cpu/uptime/process_usage.txt là output thực tế thu qua SSH, không phải dữ liệu mô phỏng. Lượt này không có ảnh màn hình tài nguyên đã chụp. Công cụ hiện tại lấy được stdout SSH nhưng không có công cụ chụp chính cửa sổ terminal Windows đang hiển thị stdout đó; không dựng PNG từ text để thay ảnh thật.

## 2. Cách chụp thủ công ở lượt được phép đọc tiếp

Mở Windows PowerShell và phiên SSH EVE-NG hiện có. Trên EVE chỉ chạy `date -Is`, `free -m`, `vmstat 1 3`, `nproc`, `uptime`; hiển thị kết quả đầy đủ. Trên Windows có thể mở Task Manager > Performance > Memory để chụp Available/Committed. Không boot Core hoặc đổi RAM để chụp ảnh.

Chụp toàn màn hình console bằng Snipping Tool/Print Screen, gồm lệnh/kết quả/thời điểm; không để hiện password/private key/token. Lưu dưới docs/evidence/M3/carp-final-readiness-20261103/manual-capture-<timestamp+0700>.png và bổ sung index thời điểm mới. Ảnh chụp sau này là số đo mới, không được gắn giờ thu cũ22:16. Không có ảnh nào ở hướng dẫn này được báo cáo là đã chụp.
