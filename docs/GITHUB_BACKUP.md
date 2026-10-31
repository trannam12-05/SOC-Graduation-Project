# Bàn giao GitHub của dự án SOC

## 1. Repository và phạm vi

- Repository: https://github.com/trannam12-05/SOC-Graduation-Project .
- Chủ sở hữu: `trannam12-05`; nhánh `main`; chế độ **PRIVATE** đã được đọc lại từ GitHub API với quyền push.
- Đây là lưu mã nguồn, tài liệu, mapping và minh chứng phù hợp; không phải bản sao đĩa VM/EVE. Image, ISO, kho gói offline và OVSDB raw vẫn ở máy/guest.
- Checkpoint kỹ thuật hiện hành và công việc tiếp theo: [PROGRESS.md](PROGRESS.md).

## 2. Kiểm tra trước phát hành

Workspace `D:\SOC` ban đầu chưa có `.git`; không có repository lồng nhau hoặc lịch sử commit cũ. Đã khởi tạo Git mới trên nhánh main. Kiểm tra lịch sử bằng `rev-list --all` và rà mọi blob bằng `cat-file --batch-all-objects`, gồm đối tượng chưa được tham chiếu nếu có. Không có lịch sử cũ cần viết lại; không force-push hoặc xóa tệp.

Quét toàn bộ danh sách tệp dự kiến commit, nội dung ZIP/XML/metadata và ảnh nhúng của DOCX, metadata PNG, mẫu private key/token/JWT, giá trị xác thực literal/hash và giá trị nhạy cảm đã biết trong phiên. Kết quả chỉ ghi tên tệp/quy tắc/dòng khi phát hiện; không in giá trị bí mật. Sau stage đối chiếu byte của từng blob với SHA-256 tệp gốc và quét lại cả index/object store trước commit.

Đã dùng Windows OCR en-US tích hợp để đọc **78 ảnh duy nhất theo SHA-256**, gồm ảnh được tham chiếu hoặc nhúng trong các báo cáo; không sửa ảnh hoặc cài công cụ mới. OCR không báo lỗi xử lý; kết quả OCR thô chỉ lưu trong staging đã bị ignore. OCR và dò mẫu là các lớp rà soát có giới hạn, không phải chứng minh toán học rằng mọi chuỗi bí mật đều có thể nhận diện.

Không phát hiện bí mật thật trong tập tệp đủ điều kiện công bố sau rà soát. Một giá trị redaction notice trong manifest seed được xác nhận là lời mô tả đã che, không phải password hash; scanner chỉ bỏ qua đúng SHA-256 của lời mô tả đó. Tệp kiểm kê cũ `docs/evidence/eve-ng/ubuntu-image-test-config/node-config.json` có trường accountPassword chưa đủ rõ để đưa lên Git nên loại khỏi publication, giữ nguyên bản cục bộ; không kết luận đó là mật khẩu thật.

## 3. Dữ liệu được loại khỏi Git

`.gitignore` loại private key, token/config xác thực theo tên, `.env`, DB/pcap raw, QCOW2 và các image VM, ISO, `.deb`, archive, staging, cache, bản sao trùng trong docs/M2/backups và dữ liệu truyền console trung gian. Không dùng blanket ignore cho log/JSON vì đây là minh chứng kỹ thuật cần giữ khi đã rà soát.

Không xóa hoặc di chuyển các tệp bị ignore. Giữ các báo cáo M2 theo từng phiên bản, CSV mapping, script, ảnh console phù hợp và log kết quả thực tế trong các thư mục guest. Các danh mục minh chứng lịch sử mô tả bộ hồ sơ cục bộ ban đầu và có thể tham chiếu tệp chỉ giữ tại D:\SOC; không đồng nghĩa mọi tệp trong danh mục đã được upload.

`.gitattributes` tắt chuyển đổi newline để giữ nguyên byte của tài liệu/log/ảnh và checksum đã công bố. Đối chiếu nội dung staged với tệp hiện hành trước commit; không dùng Git LFS hoặc filter làm thay byte minh chứng.

## 4. Kiểm tra sau push và tiếp tục trên máy khác

Commit SHA thực tế và kết quả push được báo khi thực hiện xong; để đọc lại tại máy:

```powershell
git status --short --branch
git log -1 --format=fuller
git remote -v
git ls-remote origin refs/heads/main
```

HEAD phải khớp SHA của refs/heads/main. Repository cần tiếp tục là PRIVATE; script `automation/github_private_backup.py verify` chỉ đọc xác nhận owner/visibility/quyền trước thao tác. Script lấy thông tin xác thực từ Git Credential Manager trong bộ nhớ, không ghi token vào source, remote URL, tệp hoặc output.

Trên máy khác, đăng nhập GitHub bằng cơ chế riêng của người quản trị, clone repository private rồi đọc AGENTS.md và PROGRESS.md. Không nhập secret vào file dự án. Không tự suy ra quyền bật VM, nối EVE link, sửa image/seed, firewall/NAT hoặc chạy lại apply từ việc clone/checkpoint GitHub.

Nhật ký rà soát đầy đủ, manifest toàn bộ tệp và kết quả OCR thô nằm tại `staging/github-backup/` trên máy này, không đưa lên Git để tránh xuất bản nội dung rà soát thô có thể nhạy cảm. Báo cáo này chỉ chứa kết luận và phương pháp đã thực hiện.
