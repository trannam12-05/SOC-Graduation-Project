# 2. M2 — Nghiệm thu Nhóm 1/2: điều kiện đầu vào luồng Employee → Data Center

## 2.1. Kết quả

**NOT_RUN_BLOCKED — chưa chạy phép thử HTTP, chưa nghiệm thu PASS.** Không có kết quả FAIL của lưu lượng vì chưa phát yêu cầu HTTP. Báo cáo lập ngày 03/11/2026, UTC+07:00, từ kiểm kê chỉ đọc tại `docs/evidence/M2/acceptance-group1-20261103/inventory-before.json` và các hồ sơ đã có.

Luồng mục tiêu: IPv4 `192.168.40.100 → 192.168.30.10`, TCP đích 8000, phải có phản hồi HTTP hợp lệ qua OPNsense. Không dùng phản hồi HTTP cục bộ lịch sử hoặc TCP probe để thay tiêu chí này.

## 2.2. Kiểm kê mới và điều kiện chưa đáp ứng

| Hạng mục | Kết quả mới | Ý nghĩa |
|---|---|---|
| OPNsense Primary | Có một QEMU, RAM khai báo 3072 MiB | Giữ chạy, không thay cấu hình |
| Core L2 | Không có QEMU khớp node Core trong danh sách tiến trình | Core thực tế đang tắt; điều kiện “giữ Core đang chạy” chưa đáp ứng. Không kết luận cấu hình Core hỏng hoặc phủ nhận 95/95 ca lịch sử |
| Data-Center | Node QEMU 1024 MiB, đang tắt | Chưa bật do bài thử chưa đủ điều kiện |
| Employee | Node loại VPCS, đang tắt | Hồ sơ thử hiện có dùng TCP probe, chưa xác nhận công cụ gửi HTTP GET từ endpoint này |
| Secondary, Wazuh, Suricata và endpoint khác | Không có tiến trình tương ứng trong kiểm kê | Không khởi động |
| EVE-NG | MemAvailable khoảng 4874 MiB ở mốc kiểm kê | Chỉ là số đo trước tải, chưa xác nhận tài nguyên khi chạy đủ nhóm |
| Windows | FreePhysicalMemory 867096 KiB, FreeVirtualMemory 5025504 KiB | RAM vật lý dự phòng khoảng 847 MiB; không tự tăng RAM hoặc dừng ứng dụng/VM |

Primary 3072 + Core 2048 + DC 1024 = **6144 MiB RAM khai báo**, chưa tính chi phí host và VPCS. Script start hiện có đặt giới hạn 5120 MiB cho tổ hợp này, vì nhánh 6144 MiB chỉ áp dụng một số tổ hợp tên khác. Đây là guard trong script của dự án, không phải yêu cầu tối thiểu chính thức của EVE-NG; chưa gọi wrapper start, không tự sửa hoặc bỏ guard. Cần đánh giá cửa sổ tài nguyên phù hợp trước khi bật đủ nhóm, không coi chỉ số MemAvailable lúc này là xác nhận an toàn cho toàn bài.

Yêu cầu hiện tại chỉ cho phép khởi động endpoint VLAN30/VLAN40, còn Core được mô tả là đã chạy. Do thực tế Core đang tắt, không tự mở rộng quyền sang khởi động Core. Quy tắc giới hạn quyền trong `AGENTS.md` yêu cầu thao tác vòng đời node tuân theo phê duyệt riêng; không khởi động Core chỉ vì cần thu minh chứng.

## 2.3. Khả năng HTTP và bằng chứng endpoint

Đã đọc metadata node và tĩnh chuỗi trợ giúp trong binary VPCS hiện có; không chạy thêm VPCS, không tạo client phụ hoặc thay endpoint. Việc không thấy chuỗi HTTP không được dùng để chứng minh chắc chắn VPCS không có chức năng đó. Kết luận chính xác là **chưa có cơ chế HTTP client được xác nhận cho Employee hiện tại**. `automation/vpcs_live_tests.py` chỉ có `ping ... -P 6 -p 8000`; đây là TCP probe, không chứng minh HTTP GET hoặc phản hồi HTTP hợp lệ.

| Endpoint | Thông số hồ sơ lịch sử | Trạng thái trong lượt này |
|---|---|---|
| Employee | `192.168.40.100/24`, gateway `192.168.40.2`, đã được ghi trong `docs/evidence/M2/resume-20261102/vpcs-configured.json` | Chưa bật, chưa xác minh IP/mask/gateway runtime |
| Data-Center | `192.168.30.10/24` trong log bootstrap; seed mạng ghi default route qua `192.168.30.2` trong `docs/evidence/M5/resume-20261102/service-seed-preparation.json` | Chưa bật, gateway runtime chưa được đọc; không trình bày seed như cấu hình runtime đã kiểm chứng |
| HTTP server DC | Mã `automation/linux_role_bootstrap.py` dùng Python `http.server` TCP8000; log cũ `data-center-bootstrap-public.json` từng ghi HTTP200 cục bộ | Chưa khởi chạy lại hoặc kiểm tra dịch vụ trong lượt này |

Không giả nguồn `.40.100` trên EVE/Core hoặc gán trùng IP để tạo PASS. Nếu cần client Linux có HTTP, phải chốt phương án endpoint VLAN40 và IP đó trước; không tự đổi image, seed, dây mạng hoặc cài phần mềm.

## 2.4. Kết quả theo tiêu chí nghiệm thu

| Tiêu chí | Kết quả | Bằng chứng/giới hạn |
|---|---|---|
| Đúng IP/mask/gateway hai endpoint ở runtime | NOT_RUN | Chỉ có hồ sơ lịch sử, chưa boot endpoint |
| `.40.100` truy cập `.30.10:8000` | NOT_RUN | Không gửi TCP probe hoặc HTTP |
| Phản hồi HTTP hợp lệ | NOT_RUN | Không lấy HTTP200 cục bộ cũ thay kết quả liên VLAN |
| Đi qua OPNsense giữa hai VLAN | NOT_RUN | Core đang tắt, chưa thu PCAP/state/log của phiên thử mới |
| Không sửa cấu hình hoặc bật node ngoài quyền | Đã tuân thủ trong lượt này | Chỉ đọc host inventory, metadata, chuỗi binary và chụp console Primary; không gọi start wrapper |

Không xác định lỗi firewall/routing/service từ kết quả chưa chạy. Nguyên nhân chặn là điều kiện hạ tầng và công cụ client chưa đủ, không phải bằng chứng luồng bị firewall chặn.

## 2.5. Minh chứng và hình

- `inventory-before.json`: node, interface/segment, tiến trình QEMU/VPCS, RAM EVE và Windows; thời điểm thu UTC+07:00 trong tệp.
- `employee-client-capability-review.json`: đọc tĩnh chuỗi binary hiện có; ghi rõ chưa xác nhận HTTP client, không thực thi endpoint mới.
- `primary-preflight-observe-20261103T170340+0700.png` và JSON: framebuffer thật của Primary lúc 17:03:43 UTC+07:00, không gửi lệnh guest. Console còn hiển thị đầu ra `pfctl -sr | tail -10` từ lần đọc trước; ảnh này chỉ chứng minh console đang có và nội dung màn hình ở mốc chụp, **không phải lệnh firewall vừa chạy lại hay minh chứng HTTP mới**.
- `result.json`, `evidence-index.csv`: kết quả và danh mục tên tệp/nội dung/thời điểm/đường dẫn/vị trí báo cáo/hash.

Hình 2.6 (số dự kiến khi ghép báo cáo): Console Primary tại bước kiểm kê trước nghiệm thu. Mục đích xác nhận trạng thái console; nội dung là ruleset cũ còn trên màn hình; kết quả chưa có HTTP; ý nghĩa không được suy thành nghiệm thu kết nối. Chú thích đặt dưới ảnh khi xuất Word, không chỉnh nội dung kỹ thuật ảnh.

Chưa có ảnh console endpoint hoặc HTTP vì endpoint chưa được bật. Khi đủ điều kiện và được duyệt: chụp IP/mask/default route hai endpoint, yêu cầu HTTP từ đúng `.40.100`, status/header/body đáp ứng và log/state/capture đúng phiên tại Primary. Lưu PNG nguyên bản trong thư mục nghiệm thu M2, không lộ xác thực; hình phải ghi rõ thời điểm UTC+07:00. Đây là hướng dẫn chụp tương lai, không phải ảnh đã có.

## 2.6. Điểm dừng

Cần chốt quyền bật Core nếu đang tắt, cửa sổ RAM cho nhóm Primary/Core/DC và phương án HTTP client tại `.40.100` trong VLAN40. Chưa được phép tự thay endpoint hoặc cơ chế mạng để đạt tiêu chí. Không chạy thử bài khác hoặc sửa cấu hình hàng loạt.

M2 giữ kết quả Core 95/95 lịch sử, **nghiệm thu Inter-VLAN tích hợp chưa PASS**. Đã dừng trước khi bật endpoint hoặc gửi lưu lượng. Chờ người dùng xác nhận phương án tiếp tục.
