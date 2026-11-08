# 3.9. Phân tích pfsync và phương án NAT tối thiểu — chỉ đọc

## 3.9.1. Kết luận và giới hạn
Ngày 06/11/2026 (UTC+07:00), M3 giữ PARTIAL. Không cài đặt, đổi mạng, topology, hook hoặc vòng đời node; không reload/restart, packet injection, renew DHCP hoặc kiểm thử lại PASS. Tái sử dụng kết quả M3.5/M3.6 và mẫu HA ở mục 3.8. Dữ liệu mới chỉ gồm log, cấu hình có sẵn và bộ đếm tích lũy; tệp tạm phục vụ đọc console không thay cấu hình.

## 3.9.2. Tác nhân khởi phát bulk sync dài
Primary: bulk đầu hoàn tất tại 19:18:53. Hook start/96-soc-pfsync được gọi lúc 19:20:24; pluginctl -c pfsync chạy lúc 19:20:25, ngay sau đó pfsync bulk start và CARP demotion240. Đợt thứ hai hoàn tất 19:31:38, demotion0. Secondary cũng chạy cùng hook, nhưng đợt thứ hai hoàn tất trong khoảng hai giây. Mốc trên là giờ log guest nguyên bản offset +00:00 chưa xác minh đồng bộ, không trình bày như giờ Việt Nam; khoảng dài Primary khoảng 673 giây theo log.

Hook gọi lại cơ chế native sau khi sync ban đầu đã hoàn tất: đây là tác nhân tái khởi tạo đã được log xác nhận. Chưa xác định nguyên nhân sâu khiến đợt thứ hai chậm. Hai máy có interface opt6, peer đối ứng 10.255.255.1/2, compatibility1400; rule runtime cho phép pfsync đúng peer trên vtnet2. Không thấy cấu hình lệch version hoặc chặn tĩnh trong phần đã đọc; điều này không loại trừ sự cố runtime trước đó.

Counters Primary có 58 send errors/32 failed state lookup-inserts; Secondary 60/31. Các counter tích lũy không có mốc từng lỗi nên không quy kết là nguyên nhân khoảng chậm, cũng không chứng minh mất gói tại thời điểm đó. Cần log/PCAP lịch sử đúng cửa sổ hoặc quan sát thụ động có mốc đồng bộ ở lần khởi động đã được phê duyệt nếu muốn xác định sâu hơn; không tạo reboot/failover trong lượt này. Không tự xóa hook vì nó từng được dùng khắc phục tính persistent và đã PASS nghiệm thu.

Hai giá trị BACKUP cũ vẫn là bản thu tuần tự hai phía của lần chuyển vai trò, không chứng minh đồng thời cả hai BACKUP. Giữ nguyên toàn bộ dữ liệu gốc.

## 3.9.3. Điều kiện để WAN DHCP, gateway và NAT hoạt động
| Thành phần | Hiện trạng kiểm chứng | Điều kiện còn thiếu |
|---|---|---|
| Upstream | WAN-ISP-1/network4 và WAN-ISP-2/network5 là bridge; chỉ hai firewall tham gia, không node upstream; bridge WAN không nối pnet0 | Một upstream được phê duyệt có đường Internet và cùng miền L2 hoặc DHCP relay phù hợp |
| DHCP WAN | vtnet1 enabled, ipaddr=dhcp, nhưng chưa IPv4 ở mục3.8 | DHCP server có pool/lease hợp lệ và đường UDP67/68 hai chiều; địa chỉ, subnet không chồng LAN/SYNC; hai firewall có lease riêng |
| Gateway | Chưa IPv4 default route; không có gateway tĩnh trong phần cấu hình xuất | DHCP router option3 hợp lệ, gateway cùng subnet hoặc thiết kế định tuyến được hỗ trợ; OPNsense chấp nhận gateway động làm default. Trường gateway tĩnh rỗng tự nó không chứng minh lỗi DHCP gateway |
| Outbound NAT | Cả hai đã mode automatic, nhưng pfctl -sn chưa có rule dịch địa chỉ | IPv4 WAN/default route hợp lệ và SNAT được nạp khớp nguồn/egress/translation; thêm NAT không thay thế kết nối upstream |
| Luồng được phép | Giữ tám rule M3.5; chưa có quyền mở Internet rộng | Rule egress cụ thể cho nguồn/đích/cổng được duyệt; DNS hợp lệ nếu dùng tên miền, không bắt buộc DNS để NAT theo IP |
| NAT có HA | HA nội bộ đã PASS; chưa WAN VIP | Hai IP WAN riêng và một VIP ổn định trong cùng mạng upstream, không trùng DHCP pool; upstream hỗ trợ CARP/virtual MAC. Dịch nguồn sang WAN VIP, không sang IP riêng nếu yêu cầu giữ phiên |

DHCP option3 cung cấp router; option6 cung cấp DNS nếu cần phân giải. DHCP riêng từng firewall không tự tạo một WAN VIP ổn định. Nếu upstream dùng RFC1918/NAT kép, phải duyệt chính sách WAN phù hợp thực tế; không tự tắt block private/bogon hoặc mở any-any.

## 3.9.4. Đề xuất chưa triển khai và phạm vi cần phê duyệt
Ưu tiên một upstream duy nhất cho WAN-ISP-1; chưa dùng WAN-ISP-2 hoặc multi-WAN. Chọn EVE Cloud/pnet có upstream đang hoạt động hoặc router upstream phù hợp; không mặc định pnet0 an toàn hoặc có DHCP. Cần duyệt interface/bridge cụ thể, dải địa chỉ/subnet, gateway, DHCP server và đường Internet trước khi nối.

Phạm vi nghiệm thu NAT nhỏ nhất: nguồn Employee 192.168.40.110/32 theo lease đã PASS, đích một máy Internet được chọn và TCP443; không thêm Guest, Data Center, DMZ hay Management vào rule egress mới. Nếu lease thay đổi, phải xác nhận lại nguồn trước triển khai. Dùng đích IP cụ thể để tránh phụ thuộc DNS trong phép thử ban đầu, được thực hiện sau phê duyệt riêng; không chạy lúc này.

Phương án HA phù hợp: upstream dành hai lease/reservation ổn định cho WAN riêng Primary/Secondary, và địa chỉ WAN VIP thứ ba ngoài pool cấp động. Đề xuất Hybrid outbound NAT, một rule ưu tiên cho nguồn/đích/cổng nêu trên, egress WAN, translation WAN VIP, static-port mặc định tắt nếu ứng dụng không yêu cầu. Rule firewall egress cùng phạm vi trên VLAN40, giữ deny liên VLAN. Hybrid vẫn sinh rule automatic; nếu cần giới hạn bản thân tập NAT tuyệt đối chỉ nguồn thử, phải duyệt Manual và rà soát toàn bộ rule trước chuyển mode. Không chọn mode hoặc VIP thực tế ở lượt này.

Cần duyệt đồng bộ nhóm NAT Primary sang Secondary hoặc phương án cấu hình tương đương: syncitems hiện có aliases,rules,kea,dnsforwarder chưa bao gồm NAT. Không tự thêm nhóm sync. NAT với translation WAN address ở mode Automatic có thể phục vụ kiểm thử một máy khi WAN hợp lệ, nhưng không thay thế nghiệm thu giữ phiên NAT qua WAN VIP; không đánh dấu NAT HA PASS theo phương án đơn lẻ đó.

Việc cần phê duyệt: upstream/Cloud và kết nối L2; dải WAN/gateway/leases/VIP; đích Internet và phạm vi egress; mode/rule NAT và nhóm XMLRPC sync; kế hoạch sao lưu, triển khai và kiểm chứng riêng. Đề xuất không cấp quyền áp dụng. M3 vẫn PARTIAL, NAT Internet BLOCKED đến khi các điều kiện được cấp và nghiệm thu thực tế.

## 3.9.5. Minh chứng và nguồn
Thư mục docs/evidence/M3/M3-cause-nat-plan-20261106/: results-20261106T201450+0700.json chứa hook, log và cấu hình đã lọc; topology-readonly.json và wan-members-host.json xác nhận mapping/bridge; pfsync-timeline.csv và assessment.json ghi đối chiếu. evidence-index.csv có thời điểm lưu, múi giờ, hash và vị trí báo cáo. Ảnh là framebuffer thật, không chỉnh nội dung; giờ tên file là lúc lưu batch UTC+07:00, không phải lúc từng lệnh.

Hình 3.11. Ảnh console hook Primary (OPNsense-Primary-status-*.png): mục đích đối chiếu lệnh native với log; nội dung hook gọi pluginctl -c pfsync; kết quả xác nhận cơ chế tái khởi tạo, không chứng minh nguyên nhân truyền chậm.

Hình 3.12. Ảnh console hook Secondary (OPNsense-Secondary-status-*.png): mục đích so sánh hai phía; nội dung cùng hook; ý nghĩa không quy kết hook giống nhau luôn gây cùng thời lượng. Giữ ảnh trạng thái và các trang truyền dữ liệu làm phụ lục, đọc kèm JSON kiểm checksum.

Nguồn chính thức tham khảo cho đề xuất, không thay thế minh chứng lab: [OPNsense — High Availability](https://docs.opnsense.org/manual/hacarp.html) về peer compatibility và đồng bộ; [Source NAT](https://docs.opnsense.org/manual/nat.html#source-nat-outbound) về Automatic/Hybrid/Manual; [Configure CARP — Setup Source NAT](https://docs.opnsense.org/manual/how-tos/carp.html#setup-source-nat) về translation WAN VIP và phạm vi nguồn. Truy cập 06/11/2026. Các thông số upstream/VIP còn là thiết kế đề xuất, chưa áp dụng.
