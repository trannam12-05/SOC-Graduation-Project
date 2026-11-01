# CHƯƠNG 2. ĐIỀU PHỐI KIỂM THỬ CORE THEO NHÓM CÔNG VIỆC

## 2.1. Trạng thái và chốt quyền

Ngày 01/11/2026, UTC+07:00; chuẩn bị trước 10 giờ, hạn nộp 05/11. **Chưa chạy trên VM.** Đồng hồ đến 10:00 không tự mở quyền. Giữ Core và mọi VM SOC tắt cho đến thông báo người dùng rằng Labtainer đã xong và tài nguyên sẵn sàng. Không thay mạng, image, QCOW2, sudoers hoặc tài nguyên host.

Không làm lại cài OVS, tạo bridge hoặc mapping đã có bằng chứng. Baseline cần đọc sau boot vì trạng thái runtime đã thay đổi; ảnh/log trước không thay việc xác nhận sau khởi động. Dùng bảng L00–L13 hiện có, không tạo một bộ test trùng lặp.

## 2.2. Một quy trình, ba điểm dừng có lý do

automation/m2_run_queue.py mặc định chỉ tạo queue.json và results.csv với NOT_RUN, không gọi SSH hay khởi động tiến trình con. Khi thực thi ở đợt sau, bộ điều phối chạy tuần tự: tài nguyên → yêu cầu bật đúng Core ID3 nếu đang tắt → baseline → backup mới → 31 case VLAN/trunk → mirror ens10 → 32 case với mirror → cài mẫu persistence không IP → reboot mềm có checkpoint → baseline/boot_id → thử frame sau boot → lưu kết quả.

Ba điểm dừng cần giữ: (1) đăng nhập console và xác thực sudo tại guest sau boot đầu; (2) xem console, bảo đảm không có tác vụ ghi trước reboot; (3) đăng nhập/xác thực lại sau reboot. Đây là xác thực và điều kiện kỹ thuật, không xin duyệt lại từng lệnh. Không nhận mật khẩu từ tham số, file hay chat; không sửa sudoers. Nếu không có shell đã xác minh, bộ điều phối ghi WAIT_CONSOLE thay vì đoán prompt.

## 2.3. Lệnh chuẩn bị đã được phép chạy cục bộ

```text
py -3.12 -X utf8 automation/m2_run_queue.py --run-dir staging/m2-offline-plan-20261101
py -3.12 -X utf8 -m unittest discover -s tests -p test_m2_preparation.py
py -3.12 -X utf8 automation/validate_m3_plan.py configs/M3/address-proposal.json
```

Các lệnh này không truy cập VM. Unit test dùng mock/fixture và chỉ đánh giá luồng điều khiển. Kết quả OK không được điền PASS cho VLAN, trunk, mirror, persistence hoặc HA.

## 2.4. Lệnh thực thi để trong hàng đợi, chưa được chạy

Sau thông báo tài nguyên sẵn sàng, chọn thư mục phiên mới. Ví dụ dưới đây không phải lệnh đã thực hiện:

```text
py -3.12 -X utf8 automation/m2_run_queue.py --execute --resources-ready --run-dir staging/m2-live-20261101
# Khi đã thấy đúng console Core, đăng nhập và sudo -v tại guest, tự nhập bí mật.
py -3.12 -X utf8 automation/m2_run_queue.py --execute --resources-ready --console-shell-ready --run-dir staging/m2-live-20261101
# Tại checkpoint reboot: xem console và bảo đảm không có tác vụ guest đang ghi.
py -3.12 -X utf8 automation/m2_run_queue.py --execute --resources-ready --console-shell-ready --reboot-ready --run-dir staging/m2-live-20261101
# Sau boot, đăng nhập/sudo lại rồi tiếp tục cùng thư mục.
py -3.12 -X utf8 automation/m2_run_queue.py --execute --resources-ready --console-shell-ready --run-dir staging/m2-live-20261101
```

--resources-ready là lời xác nhận người dùng đã thông báo sẵn sàng, không phải cách bỏ qua kiểm tra RAM. Trước bật Core, chốt bảo thủ Windows RAM/virtual available ≥3 GiB, EVE MemAvailable ≥3 GiB; khi Core đã chạy giữ ít nhất 1 GiB theo các ngưỡng script. Đây là điều kiện cần, không bảo đảm hiệu năng; nếu swap tăng, host giật hoặc đang có VM EVE khác thì dừng riêng nhóm triển khai. Không tự tắt Labtainer hoặc ứng dụng Windows.

## 2.5. Kiến trúc tự động và nơi lưu kết quả

m2_console_job.py chuyển bundle qua RFB/console hiện có, kiểm SHA-256 payload trước khi thực thi, dùng sudo -n không chờ mật khẩu, trả JSON qua framebuffer thật bằng bảng glyph khớp chính xác. Mỗi reply có chiều dài/hash/mã thoát; dữ liệu sai hash hoặc console khác độ phân giải/font sẽ bị từ chối. Không giả định có SSH guest hoặc nối NIC tạm. Adapter mới chỉ được mock-test, cần quan sát ảnh thật ở lần chạy đầu; nếu bàn phím/console lỗi thì không chạy lại giao dịch thay đổi một cách mù quáng.

Log chuẩn bị và queue ở staging, được .gitignore loại trừ. Khi có kết quả thật, sao chép **chọn lọc** JSON/ảnh sạch sang docs/evidence/M2/<phiên>, giữ raw backup root-only trong guest. PCAP theo TAP giữ trên EVE; không đưa raw capture lên Git mặc định. Queue ghi DONE là bước đã được kiểm tra tương ứng, không phải nghiệm thu toàn bộ M2; REQUESTED cho start/reboot chưa có chứng minh hoàn thành. Sau reboot phải thấy boot_id đổi và suite frame hoàn tất, không suy từ lệnh reboot trả về.

Nguồn log trong guest: /root/m2-traffic-<phiên>/commands.jsonl, before/baseline/after/verify JSON, backup-metadata, log lỗi và rollback. Kết quả truyền console có hash và screenshot thật; raw OVSDB không được xuất qua stdout. Gói public dùng ở báo cáo không bao gồm DB, khóa, token hay cấu hình tài khoản.

## 2.6. Lỗi, rollback và resume

Frame test phải đủ 31/32 case và final guard đạt; phiên ngắt được đánh incomplete, không chỉ kiểm các ca đã chạy. Nếu guest baseline khác thiết kế, dừng trước backup/thay đổi. Nếu không có sudo cache, nhận mã lỗi xác thực; người dùng tự xác thực tại console, không dùng sudoers NOPASSWD.

Mirror có rollback trong guest; bộ điều phối cũng giữ bước rollback khi lỗi sau thay đổi. Hai lớp có thể restore lại cùng snapshot, nhưng chỉ kết luận khôi phục khi đọc lại đạt; bản đầu là OVS rỗng không được dùng. Unit/helper mới được giữ lại trong workdir khi rollback, không xóa dữ liệu. Nếu phát hiện port/bridge ngoài dự kiến hoặc unit đã bị sửa, dừng rollback tự động, giữ log và dùng console điều tra.

Phiên đã rollback bị khóa khỏi resume triển khai, cần review baseline rồi tạo phiên mới; các bước mirror/persistence/traffic phía sau được invalidated. Nếu restore không kiểm chứng được, trạng thái UNVERIFIED_MANUAL_CONSOLE_REQUIRED, không ghi PASS. Không xử lý rollback bằng Wipe/Reset hoặc sửa QCOW2 đang chạy.

## 2.7. Rà soát báo cáo và thuật ngữ

Đã rà OOXML các DOCX M2: kích thước giấy, lề, font, hình nhúng, thứ tự caption và hash của các bản cũ. Kiểm tra cấu trúc không thay kiểm tra phân trang bằng Word. Không chạy Word/LibreOffice trong chế độ thiếu RAM. Nếu không thấy lỗi hình thức có căn cứ thì giữ nguyên bản đã tạo, dùng phụ lục điều phối này để bổ sung phần mới.

Trong nội dung kỹ thuật: MAC là Media Access Control (địa chỉ lớp liên kết); FDB là Forwarding Database (bảng học MAC); IEEE là Institute of Electrical and Electronics Engineers; thẻ 802.1Q gồm TPID (Tag Protocol Identifier) và TCI (Tag Control Information), trong đó VID (VLAN Identifier) nhận dạng VLAN. Đây là giải thích nguyên lý; chưa có capture để kết luận tag trên mirror thực tế. Các thuật ngữ SOC/OVS/VLAN/trunk/access/SPAN và vai trò firewall/sensor đã có ở báo cáo hợp nhất, không đổi tên riêng thành dạng khai triển tự tạo.
