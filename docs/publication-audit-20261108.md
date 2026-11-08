# 1. Rà soát xuất bản tiến độ SOC M1–M4

Thời điểm:08/11/2026, UTC+07:00. Repository đích: `https://github.com/trannam12-05/SOC-Graduation-Project.git`, nhánh `main`. Sau fetch, local và origin/main cùng commit `7ab1652`; không cần merge/rebase tại bước kiểm tra đầu. Không force push; không thay hệ thống lab.

## 1.1. Phạm vi đưa vào commit

- Thiết kế/mapping/VLAN và mã nguồn liên quan đã qua rà soát chuỗi thông tin xác thực.
- Báo cáo M1–M4, SOC_TO_DO, báo cáo Word `SOC_M1-M4_BaoCaoCaNhan.docx` và PowerPoint hiện tại `Thuyết trình nhóm 1.pptx`.
- Minh chứng public, JSON/CSV/log kết quả và ảnh chọn lọc đã đối chiếu trong báo cáo/thuyết trình; giữ đúng trạng thái PASS/PARTIAL/BLOCKED/DESIGN ONLY.
- Nội dung Office XML đã được quét mẫu private key/token/credential; topology XML được kiểm tra thuộc tính xác thực khác rỗng. Thông tin định danh học thuật có chủ đích trong tài liệu được giữ theo phạm vi xuất bản báo cáo/thuyết trình người dùng yêu cầu.

## 1.2. Phạm vi giữ cục bộ

Không đưa image VM/ISO/đĩa, archive, PCAP, raw config, private backup, seed/khóa, cache, thư mục temp và bản tài liệu cũ trùng nội dung vào commit. Các quy tắc có sẵn được bổ sung trong `.gitignore`, không xóa dữ liệu trên máy.

Ảnh raw chưa được xem riêng, màn hình đăng nhập/xác thực, payload mã hóa/trang truyền console và kết quả trung gian chưa đủ điều kiện kiểm tra bị giữ lại. Danh sách tệp chưa theo dõi được loại khỏi đợt này: `docs/publication-exclusions-20261108.csv`. Các tệp đã bị ignore trước đó không nằm trong danh sách quét Git untracked.

Phát hiện rà soát: seed `docs/evidence/eve-ng/ubuntu-image-test-config/user-data.yaml` có public SSH key và được bỏ khỏi index hiện tại nhưng giữ nguyên tệp cục bộ. Đây là khóa công khai đã có trong lịch sử; không viết lại lịch sử và không coi là private key/token bị phát hiện. Tệp `M2-core-stage1-seed-redacted-20261031.json` được kiểm tra riêng: giá trị khớp mẫu credential thực chất đã REDACTED nên được giữ.

Tên script có chữ private/secret không tự bị coi là chứa bí mật: chỉ giữ khi cơ chế lấy dữ liệu từ nguồn cục bộ/stdin và không có giá trị xác thực thật trong mã. Không chạy các script triển khai trong quá trình xuất bản.

## 1.3. Giới hạn và kiểm chứng

Quét mẫu không là chứng nhận mọi dữ liệu tùy ý đều an toàn; bởi vậy các ảnh/console chưa rà soát bị loại bảo thủ. Không thay ảnh/log gốc để xóa dấu vết hoặc sửa kết quả. Các liên kết đến tệp bị loại có thể chỉ sử dụng được ở workspace đầy đủ; danh mục loại trừ giải thích phạm vi bản GitHub.

Commit sử dụng thông điệp `docs: update SOC M1-M4 reports, evidence and presentation`. Kết quả push chỉ được xác nhận sau khi GitHub trả SHA trên `refs/heads/main` khớp HEAD local; SHA và số tệp thực tế được thông báo sau thao tác, không ghi trước thành công.
