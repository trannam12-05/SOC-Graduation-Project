# 3.11. Phương án cuối trình duyệt WAN và NAT M3

## 3.11.1. Kết quả kiểm tra chỉ đọc — 06/11/2026, UTC+07:00
EVE package6.2.0-4. Hàm listNetworkTypes() trong /opt/unetlab/html/includes/functions.php:621–634 chỉ trả bridge, ovs và pnet hiện có; không trả nat. Không có nat0; dnsmasq inactive; iptables NAT không có rule dịch địa chỉ. Vì vậy không chọn NAT Cloud tích hợp trên bản đang cài; không cài, nâng cấp hoặc tự tạo NAT trên host.

Upstream thực tế của HOST: pnet0 có lease192.168.220.143/24, router192.168.220.2, DHCP server192.168.220.254, DNS192.168.220.2. Route lookup đến1.1.1.1 dùng gateway192.168.220.2; đây chỉ tra bảng định tuyến, chưa phát gói hoặc chứng minh kết nối Internet. Không dùng IP .143 của host cho firewall; địa chỉ DHCP server .254 không phải gateway. Chưa xác minh pool còn trống, khả năng DHCP cấp lease cho MAC guest, hỗ trợ WAN VIP hoặc hành vi mạng VMware phía ngoài.

Đích được người dùng duyệt trong phiên chat:1.1.1.1 TCP443. Nguồn phải là một Employee được xác minh IP; chỉ thử HTTPS tối thiểu sau khi WAN/upstream được duyệt và cấu hình riêng. Không có quyền thử trong lượt lập phương án.

## 3.11.2. Phương án chọn để phê duyệt
Dùng Cloud0/pnet0 làm đường ra upstream có sẵn thay NAT Cloud không được hỗ trợ. Đây là mạng quản trị EVE có DHCP/router đã quan sát, không phải NAT Cloud EVE; việc nó thuộc mạng có NAT phía hypervisor cần xác minh riêng, chưa khẳng định từ địa chỉ .2/.254. Phải duyệt việc đưa WAN guest vào cùng miền L2 với mạng quản trị này.

Dự kiến thêm network loại pnet0, tên WAN1-UPSTREAM-PNET0, rồi chuyển CHỈ hai link vtnet1 của Primary/Secondary từ bridge WAN-ISP-1 sang network mới. Giữ bridge WAN-ISP-1 cũ để rollback; không nối network-to-network bằng link giả định. WAN-ISP-2, Core L2, VLAN/IP/VIP nội bộ, SYNC và hook giữ nguyên. Nếu không cho phép chung mạng quản trị, dừng phương án này; cần pnet riêng hoặc router upstream riêng được duyệt, không tự thay thế.

| Tham số | Giá trị đề xuất có căn cứ |
|---|---|
| WAN IPv4 | Giữ DHCP hiện có trên mỗi OPNsense; IP do server192.168.220.254 cấp, mỗi máy một lease riêng, chưa biết giá trị |
| Subnet/gateway dự kiến | 192.168.220.0/24, gateway192.168.220.2, lấy theo lease WAN thực nhận và chỉ tiếp tục khi khớp mạng được duyệt |
| IP không được dùng | 192.168.220.143 của host; không tự chọn .x hoặc reuse IP thấy trong tài liệu |
| WAN VIP | Không tạo trong phương án NAT tối thiểu; chưa có pool/exclusion/reservation để đề xuất số VIP hợp lệ |
| Source Employee | EMPLOYEE_VERIFIED_IP/32; .40.110 chỉ là lease đã PASS trước đây, không coi còn đúng ở thời điểm triển khai |

Không đổi subnet/VLAN nội bộ. WAN blockpriv hiện bật: không mặc định tắt khi WAN nhận RFC1918. Sau phê duyệt, nếu DHCP/gateway bị rule này cản thì dừng, lưu log và trình ngoại lệ chính xác; không tự mở private/bogon hoặc GUI/SSH WAN. Kết nối WAN vào mạng quản trị là tác động an ninh cần duyệt dù không mở port vào.

## 3.11.3. Cấu hình dự thảo — chưa áp dụng
Tệp M3-NAT-approval-draft-20261106.json mô tả rule đề xuất, có placeholder nguồn buộc xác minh trước thi hành; không phải script có thể tự chạy.

Firewall rule mới: enabled; action pass; quick; interface VLAN40/opt2; direction in; IPv4; protocol TCP; source EMPLOYEE_VERIFIED_IP/32, source port any; destination1.1.1.1/32; destination port443; log bật; stateful mặc định; không policy-route riêng nếu default route hợp lệ. Không mở DNS Internet, Guest hoặc đích khác; không thay tám rule PASS.

Outbound NAT đề xuất: Hybrid, một rule thủ công ưu tiên; interface WAN/vtnet1; IPv4/TCP; source EMPLOYEE_VERIFIED_IP/32; destination1.1.1.1/32 TCP443; translation WAN address động của mỗi firewall; static-port tắt. Hybrid vẫn sinh automatic rules cho nguồn khác: quyền egress hiệu lực phải kiểm tra theo toàn bộ firewall hiện có; không tuyên bố chỉ một rule NAT trong bảng hoặc tự siết policy đã PASS. Nếu yêu cầu NAT duy nhất một nguồn toàn hệ thống thì cần phê duyệt Manual riêng sau kiểm kê; không nằm mặc định trong phương án này.

Giữ nguyên cấu hình HA/XMLRPC, không bổ sung syncitems. Cần duyệt áp dụng rule NAT tương đương trên từng máy vì nhóm sync hiện chưa bao gồm NAT; mọi giá trị nguồn/đích như nhau, translation dùng WAN address tương ứng. Rule firewall được chuẩn bị trên Primary và chỉ sync nhóm rules đã có sau khi duyệt thao tác; không gọi ha_reconfigure_backup nếu tác động dịch vụ chưa được đánh giá. Không tự mở rộng phạm vi sync.

## 3.11.4. Tác động HA và rollback
Phương án này chỉ phục vụ NAT Internet tối thiểu, không nghiệm thu NAT HA giữ phiên. Dịch qua WAN address riêng làm source IP thay đổi khi đổi chủ; pfsync không giải quyết được sự thay đổi địa chỉ dịch. Không kiểm thử failover, đổi advskew/demotion/VIP hoặc sửa hook. NAT HA liền phiên cần phương án riêng: hai WAN IP ổn định, một VIP được upstream dành riêng và cho phép CARP/virtual MAC, translation sang VIP; hiện chưa đủ bằng chứng chọn số VIP hợp lệ.

Chuyển link hoặc apply rule có thể gây reload và thay đổi runtime HA; EVE Community không được mặc định hỗ trợ chuyển link nóng không gián đoạn. Trước triển khai phải xác minh thao tác được hỗ trợ, sao lưu topology/config riêng từng máy và ghi tình trạng HA. Nếu cần stop/reboot node, đổi interface assignment hoặc rủi ro mất dịch vụ thì dừng xin duyệt riêng; không suy quyền từ phê duyệt bản nháp NAT.

Rollback đề xuất theo thứ tự thay đổi thực tế: gỡ đúng firewall/NAT rule mới, phục hồi mode Automatic nếu đã chuyển, đưa hai vtnet1 về network4 WAN-ISP-1; chỉ gỡ network pnet0 mới khi hết liên kết. Dùng bản backup tương ứng nếu restore phần riêng không bảo đảm; restore toàn config có thể reload dịch vụ nên cũng phải được duyệt khi cần. Không khôi phục chồng các thay đổi hợp lệ của người khác. Không reset demotion/restart pfsync, không xóa evidence. Ghi log trước/sau và chỉ đọc lại vai trò HA; không lặp các ca PASS.

## 3.11.5. Phê duyệt cần thiết và điều kiện dừng
Xin duyệt có điều kiện: dùng Cloud0/pnet0 chung mạng quản trị, chuyển đúng hai WANvtnet1, giữ DHCP và nhận lease hợp lệ từ upstream đã quan sát; thêm rule egress TCP443 nguồn Employee đã xác minh đến1.1.1.1 và rule Hybrid SNAT như trên; sao lưu và rollback đúng phạm vi. Không duyệt IP tĩnh/VIP hoặc thay HA/hook.

Điều kiện trước apply: đọc lease Employee đang dùng và điền nguồn; xác minh DHCP WAN nhận IP riêng không trùng host, mask/gateway đúng; route WAN hợp lệ; không phát hiện thao tác bắt buộc dừng node hoặc làm gián đoạn HA. Nếu điều kiện chưa đạt, dừng ở bước đó và báo, không tự chọn IP hoặc mở thêm quyền. Chỉ sau khi cấu hình WAN/upstream được duyệt và triển khai mới gửi một kết nối HTTPS tối thiểu tới1.1.1.1:443, lưu ảnh/log và bằng chứng NAT; không dùng SYN flood, scan hoặc chạy lại kiểm thử PASS.

## 3.11.6. Minh chứng và trạng thái
Thư mục docs/evidence/M3/M3-upstream-final-plan-20261106/ gồm host-readonly.json, network-support.json, network-types-source.json, upstream-host-lease.json và evidence-index.csv. Đó là log SSH thật chỉ đọc; chưa chụp ảnh mới, chưa có lease WAN guest hoặc Internet PASS. Ảnh và PASS cũ giữ nguyên. M3 PARTIAL; NAT Internet BLOCKED/PENDING_APPROVAL. Báo cáo này thay lựa chọn NAT Cloud có điều kiện bằng kết quả khả năng thực tế, không sửa lịch sử.
