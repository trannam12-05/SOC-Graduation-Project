# 2. M2 — Nhóm 2C: chính sách liên VLAN theo cấu hình đã thu

## 2.1. Phạm vi và trạng thái

Rà soát cục bộ ngày 03/11/2026 (UTC+07:00), sử dụng bản thu Nhóm 2B.2 hoàn tất lúc 16:47:08 UTC+07:00. Không truy cập lại EVE-NG hoặc firewall; không chạy script bootstrap, script thử, kiểm tra thiết bị hay kiểm thử lưu lượng. Không sửa rule, Core L2, NAT, DHCP, CARP hoặc HA SYNC; không thêm allow-any. Kết luận phản ánh snapshot đã thu, không phải xác nhận runtime mới tại thời điểm viết.

Core L2 giữ nguyên kết quả 95/95 ca đã có. **M2 chưa nghiệm thu tích hợp PASS.** Bảy rule cấu hình đã có bằng chứng trong PF không đồng nghĩa các luồng mạng đã đi qua được.

## 2.2. Truy nguồn ngoại lệ Employee → Data Center TCP/8000

| Căn cứ | Nội dung xác minh được | Giới hạn |
|---|---|---|
| M1, Bảng 4.1; tài liệu M3 mục 3.3 | Employee → Data Center chỉ cho phép theo dịch vụ; M1 không chứa port 8000 | Là định hướng thiết kế; không phải phê duyệt TCP8000 làm dịch vụ nghiệp vụ |
| `automation/linux_role_bootstrap.py`, dòng 5 và phần service | Vai trò Data-Center dùng VLAN30, port 8000; tạo `soc-lab-http.service` với `/usr/bin/python3 -m http.server 8000 --bind 192.168.30.10 --directory /var/www/soc-lab`; trang index mô tả dịch vụ web tối thiểu trong EVE-NG | Xác định chức năng theo mã nguồn; không chứng minh service đang chạy hiện tại |
| `docs/evidence/M5/resume-20261102/data-center-bootstrap-public.json` | Mốc thu 02/11/2026 17:14:14 UTC+07:00: IP 192.168.30.10/24, service_port=8000, local_http_status=200, local_http_bytes=164; state=`CONFIGURED_LOCAL_SERVICE_VERIFIED_NOT_END_TO_END` | Có bằng chứng dịch vụ HTTP cục bộ từng hoạt động; không phải Employee truy cập DC thành công |
| `docs/evidence/M2/resume-20261102/vpcs-configured.json` | Employee đã được cấu hình 192.168.40.100/24, gateway 192.168.40.2; Guest 192.168.50.100/24, gateway 192.168.50.2 | Endpoint cấu hình lịch sử, chưa nghiệm thu end-to-end |
| `automation/vpcs_live_tests.py`, pha `dc-http` và `guest-deny` | Có lệnh dự kiến dùng VPCS TCP tới 192.168.30.10 port 8000 từ Employee và Guest | Mã có bài thử không có nghĩa bài thử đã chạy hoặc PASS; VPCS TCP probe không thay phép HTTP GET |
| `docs/evidence/M3/resume-20261102/primary-employee-diagnostic-rules-20261102T165019+0700.json` và ảnh cùng tên | Lệnh tạo rule thử `SOC TEST EMPLOYEE TO DC HTTP`, nguồn 192.168.40.100/32, đích 192.168.30.10/32, TCP8000, ingress opt2, sequence101, log=1 | Là nguồn gốc rule chẩn đoán; không thực thi lại lệnh lịch sử |
| JSON/CSV và PF Nhóm 2B.2 | UUID `684c6853-1caa-4a3c-9433-b48f01624c84` tồn tại trong cấu hình, PF @96 đang nạp | Chứng minh rule đã tồn tại, chưa chứng minh đường truyền hoặc dịch vụ hiện tại |

**Kết luận chức năng:** ngoại lệ phục vụ truy cập thử dịch vụ web HTTP tối thiểu của lab Data-Center bằng Python `http.server`. Không có bằng chứng được tìm thấy để gọi luồng này là AI/API. HTTP (Hypertext Transfer Protocol — giao thức truyền siêu văn bản) ở đây phục vụ trang tĩnh trong `/var/www/soc-lab`; mã không định nghĩa tuyến API hoặc chức năng suy luận AI cho dịch vụ này.

Rule được giữ nguyên. Chức năng kỹ thuật đã được truy nguồn; việc giữ nó làm ngoại lệ chính thức khi nghiệm thu vẫn cần người dùng chốt. Thông báo “giữ nguyên rule” trong Nhóm 2C không được tự nâng thành phê duyệt dịch vụ nghiệp vụ lâu dài.

Không tìm thấy tệp `vpcs-dc-http.json` hoặc `vpcs-guest-deny.json` trong hồ sơ đã tìm. Tệp `docs/evidence/M4/resume-20261102/vpcs-inventory.json` có output rỗng cho các lệnh; không dùng tệp này chứng minh gateway hoặc truy cập liên VLAN thành công. Giữ nguyên mọi minh chứng cũ, không chạy lại các script để lấp kết quả thiếu.

## 2.3. Cơ sở đọc bảng chính sách

Các subnet đã xác minh trong snapshot: VLAN30 `192.168.30.0/24`, VLAN40 `192.168.40.0/24`, VLAN50 `192.168.50.0/24`, VLAN60 `192.168.60.0/24`, VLAN99 `192.168.99.0/24`. Primary lần lượt `.2/24` trên opt1–opt5. Không suy CARP VIP `.1` đã được nghiệm thu.

Trong bảy rule cấu hình: hai rule LAN parent, ba rule HA SYNC và hai rule Employee; tất cả enabled/pass/in/quick. Không có rule riêng opt1/opt3/opt4/opt5, rule floating tùy chỉnh, interface group hoặc alias tùy chỉnh trong bản thu. PF có default block IPv4 @10 và IPv6 @11, logging bật, không quick; ngoại lệ phù hợp phía sau có thể thay quyết định. PF @12–@49 có ngoại lệ ICMPv6 tự động. Không kết luận mọi IPv6 bị chặn hoặc IPv6 đã tắt chỉ vì năm VLAN không khai báo địa chỉ IPv6.

VLAN (Virtual Local Area Network — mạng cục bộ ảo) tách miền Layer 2. Rule thường xét tại interface nhận luồng khởi tạo; vì vậy Employee → DC nằm trên opt2, không cần một rule pass phản chiếu trên opt1. Bộ lọc có trạng thái (stateful packet filter) lưu phiên được phép để nhận gói trả lời. Các kết luận “chặn” dưới đây áp dụng cho **kết nối IPv4 thông thường khởi tạo mới**, đi đúng đường định tuyến qua Primary và không khớp ngoại lệ khác; không thay kết quả kiểm thử, không xác nhận state hiện có, NAT liên kết hoặc đường vòng. Chuyển mạch cùng VLAN không được tự coi là chịu rule liên VLAN.

## 2.4. Bảng chính sách thực tế theo VLAN

| VLAN nguồn | Luồng đã có rule cho phép | Luồng bị chặn theo logic snapshot | Ngoại lệ/chưa xác nhận | Cấu hình còn thiếu hoặc cần quyết định | Kiểm thử tích hợp còn thiếu |
|---|---|---|---|---|---|
| 30 — Data Center | Không có pass dịch vụ riêng cho kết nối mới ingress opt1. Gói trả lời của phiên hợp lệ có thể qua state | IPv4 mới DC → VLAN40/50/60/99 hoặc đích khác không khớp pass: chịu default deny | Có đường vào DC từ Employee TCP8000 và từ LAN parent theo rule nguồn khác; chưa xác nhận thử liên VLAN. Có ngoại lệ ICMPv6 hệ thống | Không thiếu rule deny bắt buộc. DNS/NTP/cập nhật/log chỉ cần ngoại lệ nếu dịch vụ thực sự cần và được chốt nguồn, đích, giao thức/cổng | DC khởi tạo sang vùng khác bị chặn; chiều trả lời TCP8000 nếu ngoại lệ được duyệt; tương quan log/rule ID |
| 40 — Employee | @95: 192.168.40.100 → 192.168.40.2, IPv4 ICMP, sequence100, log bật. @96: 192.168.40.100 → 192.168.30.10, IPv4 TCP đích8000, source port không giới hạn, sequence101, log bật | Máy Employee khác tới DC8000; cùng máy tới cổng khác; Employee khởi tạo IPv4 tới các VLAN khác hoặc đích khác không khớp pass: default deny | TCP8000 là web lab, chưa chốt ngoại lệ nghiệm thu chính thức; không mở rộng thành toàn VLAN40. ICMP tới gateway là chẩn đoán | Chốt giữ TCP8000 và ICMP như ngoại lệ chính thức hay xử lý sau theo phê duyệt. Chỉ bổ sung dịch vụ khác nếu có nhu cầu được xác nhận | Ca dương đúng máy/cổng; ca âm sai nguồn/sai cổng; phản hồi dịch vụ thật; không coi TCP probe là HTTP GET |
| 50 — Guest | Không có pass dịch vụ riêng ingress opt3 | IPv4 mới Guest → VLAN30/40/60/99 và Internet không khớp pass: default deny | Không được mô tả “Guest đã ra Internet”; ngoại lệ ICMPv6 tự động vẫn phải xét | Không thiếu rule block nội bộ. DNS/DHCP/WAN chỉ cần thiết nếu phạm vi M2 yêu cầu Guest sử dụng các dịch vụ này; phải chốt riêng, không tự cấu hình | Guest → DC8000 và các vùng nội bộ bị chặn; ca Internet/DNS chỉ thêm sau khi được duyệt |
| 60 — DMZ | Không có pass backend/log riêng ingress opt4 | IPv4 mới DMZ → VLAN30/40/50/99 hoặc đích khác không khớp pass: default deny | Dịch vụ cục bộ của DMZ không đồng nghĩa có quyền truy cập backend hoặc được công bố từ WAN | Không thiếu rule deny mặc định. Backend/log/cập nhật chỉ mở khi có luồng được duyệt. NAT công bố dịch vụ ngoài nhóm | DMZ khởi tạo sang nội bộ bị chặn; ca backend chỉ kiểm khi có ngoại lệ chính thức |
| 99 — Management | Không có pass quản trị riêng ingress opt5 | IPv4 mới VLAN99 → các vùng khác và GUI firewall không khớp pass: default deny | Nhãn Management không tự cấp quyền quản trị. Anti-lockout hiện có ở LAN parent, không phải VLAN99; chưa có IP máy quản trị được chốt | Nếu mục tiêu quản trị qua VLAN99 là bắt buộc: cần IP admin, đích và dịch vụ quản trị được duyệt rồi mới bổ sung rule hẹp. Giữ đường quản trị LAN/console hiện có | Kiểm đường quản trị đang dùng không bị mất; kiểm allow đúng admin và deny sai nguồn chỉ khi chính sách VLAN99 đã được phê duyệt |

Các dòng “default deny” là suy luận từ cấu hình và ruleset đã thu, **chưa phải kết quả kiểm thử chặn**. Không tạo thêm rule block-any hoặc block liên VLAN trùng cơ chế mặc định. Luồng nguồn LAN parent không thuộc năm VLAN trên vẫn có thể được cho phép tới các đích này, nên không được suy từ bảng rằng mọi truy cập vào DC đều bị chặn.

## 2.5. Rule ngoài năm VLAN cần ghi nhận và giữ nguyên

| Rule/đường truy cập | Chính sách trong snapshot | Ý nghĩa |
|---|---|---|
| LAN parent vtnet0, mạng 192.168.1.0/24 | @89 cho LAN net → any IPv4; @92/@93 cho nguồn LAN IPv6/link-local → any; log tắt | Là allow rộng đang có, không phải rule mới hoặc ngoại lệ quản trị đã duyệt. Có thể ảnh hưởng chính sách truy cập vào các VLAN khi đi vào vtnet0. Không chỉnh trong Nhóm 2C |
| Anti-lockout LAN | @87/@88, ingress vtnet0, TCP từ any → self trên service http/https, log bật | Đường bảo vệ quản trị hiện hành; không chứng minh truy cập được từ VLAN99, cũng không phải xác nhận IP admin |
| HA SYNC opt6/vtnet2 | @90/@91/@94: peer 10.255.255.2 → Primary 10.255.255.1, IPv4 ICMP/pfsync/TCP443, log bật | Giữ nguyên; rule tồn tại không thay bằng chứng failover/state replication. Không kiểm thử HA ở nhóm này |

Nếu phạm vi nghiệm thu đòi giới hạn mọi nguồn liên vùng, hai rule LAN rộng phải được chủ dự án quyết định giữ vì mục đích quản trị/lab hay thu hẹp ở nhóm riêng có đường phục hồi. Không thể đánh dấu toàn hệ thống “chỉ cho dịch vụ cần thiết” chỉ dựa vào default deny trên VLAN.

## 2.6. M2 thực sự còn thiếu gì?

### 2.6.1. Không cần cấu hình bổ sung chỉ để có default deny

Core và các VLAN interface đã có bằng chứng; default deny đã hiện diện. Không có căn cứ bắt buộc thêm DNS/NTP/Internet/log hoặc rule deny mới chỉ để kết thúc M2. Trạng thái không có pass dịch vụ không tự là lỗi cấu hình nếu chính sách yêu cầu vùng đó chưa được phép khởi tạo kết nối.

### 2.6.2. Quyết định chính sách cần chốt

1. Xác nhận TCP8000 là ngoại lệ web lab dùng để nghiệm thu, hay chỉ giữ tạm rồi xử lý ở nhóm riêng; tương tự với ICMP chẩn đoán Employee → gateway. Nhóm này giữ nguyên cả hai.
2. Chốt vai trò LAN parent và phạm vi hai allow rộng hiện có. Nếu yêu cầu cô lập bao gồm cả nguồn LAN parent, đây là vấn đề chính sách cần xử lý có phê duyệt, không phải thiếu thêm một rule chặn VLAN30.
3. Nếu bắt buộc quản trị qua VLAN99: chốt IP máy quản trị, thiết bị đích, giao thức/cổng và logging để chuẩn bị rule hẹp. Nếu tiếp tục quản trị qua LAN/console thì ghi rõ đó là phương án hiện tại, không báo VLAN99 quản trị đã hoàn tất.
4. Chỉ chốt DNS/NTP/cập nhật/log hoặc dịch vụ nghiệp vụ khác khi thực sự nằm trong phạm vi M2; chưa đủ nguồn/đích/giao thức/cổng thì không mở. DHCP/NAT/CARP/HA không bị thay đổi để lấp các mục chưa chốt này.

**Chưa xác định có rule dịch vụ mới nào bắt buộc phải thêm ngay.** Những thiếu hụt rõ nhất hiện tại là phê duyệt ngoại lệ/phạm vi quản trị và kiểm thử tích hợp; cấu hình bổ sung chỉ phát sinh từ các yêu cầu được chốt ở trên.

## 2.7. Checklist nghiệm thu tích hợp M2 — chưa thực hiện

| Mã | Hạng mục cần thực hiện sau phê duyệt | Minh chứng cần có | Trạng thái |
|---|---|---|---|
| C-I01 | Xác nhận các endpoint thật dùng đúng subnet, gateway và đường VLAN đã chốt; không chạy lại suite Core 95/95 nếu không có thay đổi liên quan | Cấu hình endpoint và topology đã có; chỉ bổ sung phần thiếu khi tổ chức kiểm thử tích hợp | Chưa nghiệm thu tích hợp |
| C-I02 | Employee .40.100 → DC .30.10 TCP8000, nếu được duyệt làm ngoại lệ | Phản hồi TCP và HTTP từ client phù hợp; rule UUID/log/state chọn lọc; không dùng HTTP200 cục bộ thay đường liên VLAN | Chưa kiểm thử |
| C-I03 | Đúng đích nhưng sai nguồn, hoặc đúng nguồn nhưng sai cổng, từ Employee | Kết quả client cộng log/rule phù hợp; không lấy timeout đơn lẻ làm bằng chứng đủ | Chưa kiểm thử |
| C-I04 | Guest → DC8000 và các ca âm đại diện VLAN30/50/60/99 khởi tạo sang vùng khác | Có lưu lượng thử tới dịch vụ đối chứng hợp lệ, capture/log tại firewall, kết quả deny tương ứng; không coi server tắt là firewall chặn | Chưa kiểm thử |
| C-I05 | Gói trả lời của phiên được phép; không mở mới chiều ngược ngoài chính sách | State và log/capture chọn lọc của cùng phiên | Chưa kiểm thử |
| C-I06 | Quyền quản trị hiện có; VLAN99 nếu được chốt thêm yêu cầu | Đúng nguồn admin/đích/cổng được duyệt, đường phục hồi console; nguồn không hợp lệ bị từ chối | Chưa kiểm thử |
| C-I07 | Phạm vi IPv6 và các ngoại lệ ICMPv6 hệ thống | Chính sách IPv6 được chốt trước; kết quả ca kiểm tương ứng, không tự tắt IPv6 hoặc tuyên bố block-all | Chưa kiểm thử |

Không bật node hoặc phát lưu lượng trong nhóm này. Trước đợt tích hợp phải có quyền bật đúng nhóm node và đủ RAM; không mặc định bật toàn topology. Các ca trên là kế hoạch, không phải kết quả đã đạt. Không yêu cầu kiểm thử lại Core 95/95 hoặc HA đã có chứng cứ nếu không thuộc mục tiêu mới; nghiệm thu HA còn thiếu thuộc phạm vi riêng, không gộp thành M2 PASS.

## 2.8. Nguồn và minh chứng bàn giao

- Cấu hình/ruleset thực tế: [JSON Nhóm 2B.2](../evidence/M2/group2b2-20261103/firewall-current-public.json), [bảng bảy rule](../evidence/M2/group2b2-20261103/configured-firewall-rules.csv), [PF đầy đủ](../evidence/M2/group2b2-20261103/pf-filter-rules-current.txt).
- Báo cáo đọc trước: [Nhóm 2B.2](../evidence/M2/group2b2-20261103/M2-group2b2-firewall-results.md). Ảnh console thật và log nguồn vẫn ở thư mục cũ; không di chuyển hoặc sửa ảnh.
- Nguồn chức năng dịch vụ và kiểm chứng cục bộ được liệt kê ở mục 2.2. Báo cáo thiết kế M1: `docs/M1/M1_Thiet_ke_SOC_Core_L2_OPNsense_Giai_thich_thuat_ngu.docx`; chính sách M3: `docs/M3/M3-deployment-matrix-and-tests-PREPARED-20261101.md`.
- Cơ sở nguyên lý đã dùng ở Nhóm 2B.2: [OPNsense Rules](https://docs.opnsense.org/manual/firewall.html). Nhóm 2C không truy cập lại thiết bị hoặc website để lặp các bước đã có bằng chứng.
- Danh mục/hash nguồn và thời điểm rà soát: `docs/evidence/M2/group2c-20261103/source-manifest.json`, `evidence-index.csv`. Đây là minh chứng rà soát tài liệu, không phải ảnh hoặc test live mới.

Nhóm này không có bước kỹ thuật trên thiết bị nên không phát sinh ảnh cấu hình mới. Khi tích hợp được phê duyệt, chụp topology/console client, rule/log hiển thị đúng UUID và kết quả ca; ẩn xác thực, lưu ảnh gốc vào thư mục M2 của đợt kiểm thử. Đánh số hình theo Chương 2, chú thích dưới hình và giải thích mục đích, nội dung, kết quả, ý nghĩa; không ghi ảnh tương lai là minh chứng đã có.

Đã hoàn tất rà soát chính sách theo snapshot; **chưa nghiệm thu M2 PASS**. Không thay đổi hệ thống, không chạy thử và không commit/push. Dừng chờ người dùng xác nhận.
