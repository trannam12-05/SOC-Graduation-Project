# 2. Nhóm 1B — checkpoint chờ đăng nhập Core

Checkpoint lịch sử. Sau khi người dùng xác nhận đăng nhập, thao tác 2 và 3 đã hoàn tất; xem [báo cáo runtime và backup](M2-group1b-runtime-20261102.md). Nội dung bên dưới giữ nguyên trạng thái lúc chờ đăng nhập.

## 2.1. Trạng thái ba thao tác được giao

| Thao tác | Kết quả tại checkpoint |
|---|---|
| Khởi động riêng SOC-Core-L2 | Đã gửi lệnh start đúng ID 3/UUID đã xác nhận; ảnh thật xác nhận Ubuntu soc-core-l2 đã boot tới login prompt |
| Sao lưu OVSDB và cấu hình về Windows | Chưa thực hiện; cần shell đăng nhập và sudo được xác thực |
| Đối chiếu runtime và chỉ sửa VLAN/trunk nếu cần | Chưa thực hiện; phải hoàn tất backup trước, không suy trạng thái hiện tại từ minh chứng cũ |

Chưa hoàn tất Nhóm 1B. Không sửa VLAN, trunk, SPAN, LACP, IP hoặc OPNsense; không thử lưu lượng. Wazuh-SOC đã chạy trước khi bắt đầu và được giữ nguyên. Chỉ SOC-Core-L2 được khởi động trong lượt này.

## 2.2. Minh chứng khởi động và tài nguyên

Thư mục mới: `docs/evidence/M2/group1b-20261102T212014+0700/`. `start-core.json` lưu quyền thực thi, node đích, RAM/tiến trình trước start và kết quả wrapper. Trước start, EVE MemAvailable khoảng 5579,5 MiB, mẫu vmstat không có swap-in/out; Windows available 844320 KiB, commit available 5984216 KiB. Đây là số đo trước start, không phải số đo hiện tại sau boot.

![Console Core chờ đăng nhập](../evidence/M2/group1b-20261102T212014+0700/core-console-ready-20261102T212206+0700.png)

Hình 2.1. SOC-Core-L2 đã boot và đang chờ đăng nhập console.

Mục đích là xác minh node đã khởi động thật. Màn hình hiển thị Ubuntu 24.04.5 LTS, hostname soc-core-l2 và login prompt. Kết quả xác nhận boot tới màn hình đăng nhập; không chứng minh OVS đang hoạt động hoặc cấu hình VLAN chính xác. Ảnh kiểm tra lại lúc 21:24:22 UTC+07:00 vẫn hiển thị cùng login prompt.

Danh mục ảnh/log: `evidence-index.csv` trong cùng thư mục, gồm thời điểm máy thu UTC+07:00, đường dẫn, vị trí báo cáo và SHA-256.

## 2.3. Điều kiện tiếp tục thao tác 2 và 3

Người dùng mở console SOC-Core-L2, đăng nhập trực tiếp bằng tài khoản hiện có, chạy `sudo -v` và tự nhập mật khẩu trong console; không gửi mật khẩu vào chat. Sau đó báo “ĐÃ ĐĂNG NHẬP”. Không thay sudoers, không thay chế độ đăng nhập hoặc mạng để bỏ qua xác thực.

Đã chuẩn bị mã backup/đối chiếu trên Windows nhưng chưa chạy vào guest: `automation/m2_group1b_backup_guest.py`, `automation/m2_group1b_backup_host.py`, `automation/m2_group1b_compare.py`. Backup dự kiến lấy snapshot nhất quán qua ovsdb-client, kiểm tra schema và checksum, rồi chuyển về thư mục mới trong M2. Chưa có backup OVSDB mới tại checkpoint này; không trình bày đường dẫn dự kiến như tệp đã tồn tại.

Sau khi có shell xác thực, tiếp tục đúng thao tác 2 và 3 của cùng Nhóm 1B, không khởi động lại Core và không chuyển nhóm. Nếu gặp sai lệch chưa rõ, dừng trước khi sửa theo yêu cầu người dùng.
