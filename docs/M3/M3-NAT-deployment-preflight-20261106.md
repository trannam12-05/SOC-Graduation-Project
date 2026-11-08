# 3.12. Triển khai NAT — dừng ở preflight và sao lưu

## 3.12.1. Kết quả thực tế
Ngày06/11/2026 UTC+07:00, M3 tổng thể PARTIAL; đợt NAT BLOCKED_BEFORE_NETWORK_CHANGES. Đã thực hiện phần sao lưu và kiểm tra an toàn được duyệt. Chưa chuyển WAN, chưa thêm firewall/Hybrid SNAT, chưa gửi HTTPS hoặc khởi động node. Không báo cáo NAT PASS. Mọi PASS M3.5/M3.6 được giữ nguyên, không kiểm thử lại.

## 3.12.2. Sao lưu và upstream
Topology backup trên EVE: /root/soc-m3-nat-20261106T202914Z/lab-before.unl, SHA-256 b08522f6f47879a41a0896eff0c8704f5922f1786b2ea1d85af88113afc46224 khớp bản gốc. Cấu hình Primary: /root/soc-m3-nat-prechange-20261106T203235Z/config.before.xml. Secondary: /root/soc-m3-nat-prechange-20261106T203421Z/config.before.xml. Hai bản quyền0600, hash khớp config tại thời điểm sao lưu; hash chi tiết trong deployment-result.json. Chỉ lưu cấu hình chứa bí mật trên guest root-only, không xuất config thô vào docs.

pnet0 vẫn192.168.220.143/24, gateway mặc định192.168.220.2; đọc lại cuối xác nhận topology không đổi, địa chỉ/route quản trị giữ nguyên. Đây là xác minh đường route quản trị, không chứng minh Internet, DHCP guest hoặc không có sự kiện mạng ngoài cửa sổ quan sát. WAN hai firewall chưa có default route IPv4; không renew hoặc tự cấp IP.

## 3.12.3. Điều kiện dừng
Mã API connectNode→linkInterface→Interfc.edit được kiểm tra chỉ gán network_id vào đối tượng rồi lưu; phần này không cập nhật TAP/bridge runtime. Chưa xác minh cơ chế chuyển link nóng an toàn trong bản EVE hiện tại. Không thử thay metadata rồi báo đã chuyển WAN, không tự stop/restart node và không tự thao tác bridge mạng quản trị thay cho cơ chế chưa được đánh giá. Điều này KHÔNG chứng minh chắc chắn cần dừng VM; đó là giới hạn xác minh của lượt này.

Employee là VPCS node5, tại thời điểm kiểm tra không có tiến trình VPCS nào trên EVE. Vì vậy chưa có IP Employee hiện hành được xác minh; lease .40.110 lịch sử không được tự coi còn hiệu lực. Chưa có client HTTPS được xác nhận trên đúng endpoint. Không dùng curl trên firewall/EVE để thay cho Employee hoặc giả địa chỉ nguồn. Theo giới hạn quyền dự án, không suy quyền thay/khởi động node từ yêu cầu kiểm chứng.

Các điều kiện triển khai trong phương án đã duyệt có điều kiện chưa đủ. Dừng trước thay đổi mạng để tránh rủi ro HA và không thay đổi lab rồi mới phát hiện không thể nghiệm thu đúng nguồn.

## 3.12.4. Rollback và việc còn lại
Không cần rollback mạng/cấu hình: chưa có thay đổi nào thuộc phạm vi đó. Backup, tệp tạm thu console và minh chứng được giữ; không xóa dữ liệu cũ. Không đổi HA/CARP/pfsync/hook, Core hoặc VLAN/IP đã nghiệm thu.

Để tiếp tục: xác minh phương pháp chuyển đúng hai WAN TAP sang pnet0 và cập nhật topology đồng nhất khi node đang chạy, có kiểm tra/rollback được duyệt; nếu cần dừng/restart hoặc bảo trì thì phải xin duyệt riêng. Cần duyệt chuẩn bị endpoint Employee có HTTPS và xác minh IP thực tế; không tự thêm image/node hoặc cài công cụ. Khi các điều kiện đủ mới chuyển WAN, yêu cầu lease/gateway hợp lệ trên cả hai; sau đó áp dụng đúng nguồn /32→1.1.1.1/32 TCP443, Hybrid SNAT WAN address và thử một HTTPS theo phê duyệt. Nếu bước đó lỗi mới rollback đúng thay đổi đã thực hiện, không đụng cấu hình PASS.

## 3.12.5. Minh chứng và hình
Thư mục docs/evidence/M3/M3-NAT-deployment-20261106/. deployment-result.json ghi trạng thái từng bước; preflight-topology-backup.json và final-host-unchanged.json xác nhận backup/topology/upstream. runtime-prerequisites.json, employee-runtime-preflight.json và các tệp link-*-*.json lưu căn cứ chỉ đọc. results-20261106T203932+0700.json ghi backup hai guest và hash; evidence-index.csv có tệp, nội dung, thời điểm lưu kèm múi giờ, hash và vị trí báo cáo.

Hình 3.13/3.14: ảnh console Primary/Secondary trong bộ before/execute/header/page của đợt này. Mục đích ghi nhận console thật và quá trình sao lưu; nội dung trang header/page là dữ liệu truyền kết quả được kiểm tra checksum, đọc kèm JSON giải mã. Kết quả chứng minh thu backup, không thay thế minh chứng WAN/NAT/HTTPS chưa chạy. Ảnh không chỉnh nội dung; thời gian tên file là thời điểm lưu batch UTC+07:00, không phải thời điểm chính xác từng lệnh. Chưa có ảnh topology sau thay đổi vì không thực hiện đổi topology.
