# 2. M2 — Nhóm 2B.2: kết quả đọc firewall OPNsense Primary

## 2.1. Kết luận và phạm vi

Ngày 03/11/2026, sau khi người dùng đăng nhập trực tiếp và mở Shell, đã đọc cấu hình firewall và ruleset PF đang nạp trên Primary. Bộ dữ liệu được thu xong lúc **16:47:08 UTC+07:00**; thời điểm thực thi collector sớm hơn, được kẹp giữa ảnh shell và ảnh `PUBLIC_RULES_READY`. Đồng hồ guest không được dùng thay thời điểm máy thu.

Có **7 rule cấu hình modern, 0 rule legacy**. Không có rule cấu hình gắn riêng `opt1`/VLAN30, không có interface group hoặc alias tùy chỉnh trong các nhánh đã đọc. Bảy UUID rule modern đều xuất hiện trong ruleset PF đang nạp. Không có rule floating tùy chỉnh trong bảy rule này. Danh sách đầy đủ rule tự động và rule do người dùng cấu hình được xuất riêng; không đánh đồng số rule cấu hình với số rule PF.

**Không có ngoại lệ DNS/NTP/cập nhật/log riêng cho VLAN30.** Có default deny IPv4 và IPv6 đang nạp, nhưng vẫn có ngoại lệ hệ thống, rule cho phép ở interface nguồn khác và state của phiên hợp lệ có thể ảnh hưởng kết quả. Đặc biệt, rule thử Employee → DC TCP8000 vẫn tồn tại. Vì vậy chưa thể nghiệm thu yêu cầu “mặc định chặn liên VLAN” cho toàn hệ thống.

Không thêm/sửa/xóa rule, không save cấu hình, reload firewall, xóa state hoặc thử lưu lượng. Không thay Core L2, Secondary, HA SYNC, CARP, NAT hoặc DHCP. Chỉ Primary được khởi động theo quyền đã cấp; không khởi động node khác. Việc người dùng mở shell không làm mở rộng quyền sang nhóm kế tiếp.

## 2.2. Phương pháp, tính toàn vẹn và giới hạn

Đã dùng SSH hiện có tới host EVE và framebuffer console QEMU; không mở SSH trên firewall, không nhập hoặc thu mật khẩu/API key. Từ shell đã được xác thực, collector chỉ đọc `/conf/config.xml`, lấy các trường rule/interface/alias được chọn và chạy các lệnh chỉ đọc:

- `/sbin/pfctl -vvsr`: rule PF và số liệu bộ đếm tại thời điểm đọc.
- `/sbin/pfctl -a '*' -sr`: phần rule filter được trả về với lựa chọn anchor đệ quy; không thấy mục anchor bổ sung trong đầu ra.
- `/sbin/pfctl -s Tables`: chỉ lấy tên bảng, không xuất tập dữ liệu bảng.
- `/usr/local/sbin/opnsense-version`: xác nhận OPNsense 26.7 (amd64).

Không xuất raw XML, thông tin người dùng, chứng thư hoặc khóa. Helper và dữ liệu công khai phục vụ truyền console được ghi tạm vào `/var/tmp/soc-2b2-reader.b64` và `/var/tmp/soc-2b2-public-rules.b64`; không ghi vào đường dẫn cấu hình. Không tự xóa tệp tạm hoặc dừng node sau thu thập.

SHA-256 `config.xml` trước/sau đọc giống nhau:

`2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2`

Hash này cũng khớp hash đã ghi trong Nhóm 2A. Đây là bằng chứng nội dung cấu hình không đổi tại các mốc đọc, không phải backup mới. Không tạo backup cấu hình ở nhóm chỉ đọc này. Ba lệnh PF đều trả về 0; `pfctl -vvsr` có thông báo thiếu ALTQ trong kernel, không làm mất đầu ra rule. ALTQ (Alternate Queuing — cơ chế xếp hàng lưu lượng) không phải chức năng được cấu hình hay kiểm thử trong nhóm này.

Trang truyền đầu tiên từng bị chụp trước khi console cập nhật; bộ giải mã từ chối, ảnh và lỗi được giữ lại. Ảnh framebuffer chụp sau đó được dùng để đọc đúng trang. Toàn payload base64 đã khớp SHA-256 trước khi giải nén JSON; không sửa ảnh hoặc đoán ký tự. `readonly-collection-error.json` là lỗi truyền ảnh ban đầu đã được xử lý bằng đọc lại tệp công khai, không phải lỗi đăng nhập. Không chạy lại collector hoặc thay cơ chế xác thực.

## 2.3. Địa chỉ và interface hiện hành trong cấu hình

| Vùng | Assignment / thiết bị | Primary / subnet |
|---|---|---|
| LAN không gắn VLAN | lan / vtnet0 | 192.168.1.1/24 — mạng 192.168.1.0/24 |
| VLAN30 — Data Center | opt1 / vtnet0_vlan30 | 192.168.30.2/24 — mạng 192.168.30.0/24 |
| VLAN40 — Employee | opt2 / vtnet0_vlan40 | 192.168.40.2/24 — mạng 192.168.40.0/24 |
| VLAN50 — Guest | opt3 / vtnet0_vlan50 | 192.168.50.2/24 — mạng 192.168.50.0/24 |
| VLAN60 — DMZ | opt4 / vtnet0_vlan60 | 192.168.60.2/24 — mạng 192.168.60.0/24 |
| VLAN99 — Management | opt5 / vtnet0_vlan99 | 192.168.99.2/24 — mạng 192.168.99.0/24 |
| HA SYNC | opt6 / vtnet2 | 10.255.255.1/30, pfsync peer 10.255.255.2 |

Năm VLAN có trường enable=1; IPv6 address/prefix cấu hình của năm VLAN để trống. Không suy ra IPv6 đã bị vô hiệu hóa: ruleset vẫn có các ngoại lệ ICMPv6 hệ thống. Địa chỉ CARP VIP và nguồn máy quản trị không được suy ra từ các địa chỉ interface.

## 2.4. Toàn bộ bảy rule cấu hình và ánh xạ thứ tự PF

Tất cả bảy rule: enabled=1, action=pass, direction=in, quick=1, source_not=0, destination_not=0. Source port trống trong cấu hình, tức không giới hạn source port bằng trường này; với ICMP/pfsync không có khái niệm port TCP/UDP. Trong hai rule LAN protocol=any, destination port không giới hạn. Logging ở đây là trạng thái thật, không phải đề xuất.

| Thứ tự PF | Sequence | Interface | IPv4/IPv6 | Source | Destination | Protocol / port đích | Log | Mô tả |
|---|---:|---|---|---|---|---|---|---|
| @89 | 1 | lan / vtnet0 | IPv4 | LAN net: 192.168.1.0/24 | any | any / không giới hạn | Tắt | Default allow LAN to any rule |
| @90 | 10 | opt6 / vtnet2 | IPv4 | 10.255.255.2/32 | 10.255.255.1/32 | ICMP / không áp dụng port | Bật | SOC HA SYNC icmp |
| @91 | 11 | opt6 / vtnet2 | IPv4 | 10.255.255.2/32 | 10.255.255.1/32 | PFSYNC / không áp dụng port | Bật | SOC HA SYNC pfsync |
| @92, @93 | 11 | lan / vtnet0 | IPv6 | LAN net; rule sinh thêm fe80::/10 | any | any / không giới hạn | Tắt | Default allow LAN IPv6 to any rule |
| @94 | 12 | opt6 / vtnet2 | IPv4 | 10.255.255.2/32 | 10.255.255.1/32 | TCP / 443 | Bật | SOC HA SYNC tcp |
| @95 | 100 | opt2 / vtnet0_vlan40 | IPv4 | 192.168.40.100/32 | 192.168.40.2/32 | ICMP / không áp dụng port | Bật | SOC DIAG EMPLOYEE GATEWAY |
| @96 | 101 | opt2 / vtnet0_vlan40 | IPv4 | 192.168.40.100/32 | 192.168.30.10/32 | TCP / 8000 | Bật | SOC TEST EMPLOYEE TO DC HTTP |

Sequence là trường thứ tự cấu hình; vị trí phần tử XML không phải thứ tự xử lý cuối cùng. Hai rule cùng sequence 11 được trình bày theo thứ tự PF thật. Số @ là chỉ số tại thời điểm thu, có thể đổi sau reload; dùng UUID trong CSV/JSON để tương quan bền hơn. Rule IPv6 LAN tạo hai rule PF nên bảy rule cấu hình không tương ứng đúng bảy dòng PF. Rule pfsync dùng no state; các rule còn lại dùng keep state. Năm rule SYNC/Employee có nosync=1; hai rule LAN nosync=0. Không kiểm thử hoạt động đồng bộ XMLRPC trong nhóm này.

CSV `configured-firewall-rules.csv` có đầy đủ source port, destination port, action, logging, sequence, UUID và chỉ số PF. `pf-filter-rules-current.txt` giữ thứ tự và toàn bộ dòng rule đang nạp; `pf-filter-verbose-current.txt` giữ cả bộ đếm.

## 2.5. Rule chặn/tự động và ảnh hưởng VLAN30

| Chỉ số PF | Hành vi đang nạp | Ý nghĩa và giới hạn |
|---|---|---|
| @0–@9 | Block các điều kiện nguồn/interface, gồm @2: nguồn 192.168.30.0/24 đi vào interface khác vtnet0_vlan30 | Chống giả nguồn; @2 không phải “chặn mọi lưu lượng VLAN30”. @1 dùng bảng tự động, chỉ thu tên/số lượng, chưa xuất thành viên. |
| @10, @11 | block drop in log inet all; block drop in log inet6 all | Default deny IPv4/IPv6. Không quick: rule pass phù hợp phía sau có thể thay quyết định. Không thêm block-any trùng cơ chế này. |
| @12–@49 | Pass quick một số ICMPv6, với phạm vi nguồn/đích/type thể hiện trong tệp đầy đủ | Ngoại lệ hệ thống; không tuyên bố “mọi IPv6 đều bị chặn”. Không thay hoặc tắt IPv6. |
| @50–@57 | Block quick TCP/UDP source/destination port 0 | Bảo vệ hệ thống, không phải ngoại lệ dịch vụ DC. |
| @58, @59 | Block quick từ bảng sshlockout tới self trên ssh/https | Có thể tác động quản trị. Đầu ra lúc thu hiển thị bảng 0 phần tử; không thay bảng. |
| @60 | Block quick từ bảng virusprot tới any | Có thể tác động nhiều vùng; đầu ra lúc thu hiển thị bảng 0 phần tử. |
| @61–@74 | Pass DHCP/DHCPv6 hệ thống trên WAN hoặc LAN vtnet0 | Không phải rule DHCP VLAN30. Không đổi cấu hình DHCP. |
| @75–@85 | Block bogon/private/link-local trên WAN | Không phải chặn liên VLAN ở opt1. |
| @86 | Pass out log không quick | Hướng out; không tự cho phép một kết nối mới chưa qua lọc in từ VLAN30. Không suy thành DC allow-any. |
| @87, @88 | Pass in log quick trên vtnet0, any → self TCP http/https | Bảo vệ truy cập quản trị trên LAN parent; không phải rule trên VLAN30/VLAN99. |
| @89–@96 | Bảy rule cấu hình ở mục 2.4 | Có rule nguồn interface khác cho phép đích DC; không thể chỉ xem tab VLAN30 để kết luận chính sách toàn vùng. |

Với lưu lượng IPv4 thông thường khởi tạo từ VLAN30, không thấy pass in riêng hoặc pass in toàn cục cho dịch vụ ứng dụng DC trong ruleset thu được. Đây là kết quả rà cấu hình/ruleset, chưa phải kết quả thử chặn thực tế. Không thu riêng bảng state hoặc NAT rules; không kết luận về state còn sống, dịch vụ NAT được liên kết, đường đi thay thế hoặc kết nối nội bộ cùng VLAN. Lưu lượng cùng VLAN có thể được Core L2 chuyển trực tiếp nên không tự chịu rule định tuyến trên OPNsense.

## 2.6. Quyền quản trị và HA SYNC cần giữ

Anti-lockout không bị disable trong trường cấu hình đã đọc; PF @87/@88 cho phép TCP http/https từ nguồn any **đi vào vtnet0** tới self. WebGUI cấu hình protocol=https; trường port không ghi rõ trong XML. Báo cáo giữ tên service PF ở các rule tự động, không tự gán port cấu hình khi chưa đọc mapping. Đích self là địa chỉ của chính firewall; điều kiện ingress LAN vẫn bắt buộc. Không suy rằng mọi VLAN có quyền quản trị hoặc dịch vụ SSH đang lắng nghe chỉ vì có tên ssh trong rule chặn tự động.

Hai rule LAN rộng @89 và @92/@93 có thể cho phép các máy thuộc nguồn LAN truy cập DC hoặc quản trị theo điều kiện của chúng; đây là rule hiện có, không phải nguồn quản trị đã được nhóm phê duyệt. IP máy quản trị vẫn cần xác nhận. Giữ nguyên các rule này trong nhóm chỉ đọc; nếu sau này cần thu hẹp phải có phương án quản trị/console được duyệt riêng.

Ba rule SYNC @90/@91/@94 chỉ từ peer 10.255.255.2 tới Primary 10.255.255.1 trên vtnet2; TCP443 được xác nhận trong cấu hình rule và được PF hiển thị bằng service https. Rule có mặt không chứng minh peer hiện đang chạy hoặc HA đạt; Secondary không được bật, không phát ping/TCP/pfsync thử.

## 2.7. Đối chiếu bảng Nhóm 2B.1

| Mục đề xuất | Đã tồn tại trên opt1? | Kết luận hiện tại |
|---|---|---|
| P10 — DNS | Không có rule cấu hình riêng | Chưa chốt source host, resolver IP/alias, IPv4/IPv6 và giao thức/cổng. Không tự dùng địa chỉ DNS ví dụ M1. |
| P20 — NTP | Không có rule cấu hình riêng | Chưa chốt server IP, source host, giao thức/cổng. Không coi thời gian guest là xác nhận NTP server cho DC. |
| P30 — Cập nhật | Không có rule cấu hình riêng | Chưa chốt máy nguồn, repository/proxy/đích và giao thức/cổng. Không thay bằng Internet any. |
| P40 — Log/SOC | Không có rule cấu hình riêng | Chưa chốt IP collector, máy phát log và cơ chế truyền/giao thức/cổng. Wazuh replay không xác nhận endpoint mạng live. |
| D0 — implicit deny | Có default block IPv4/IPv6 @10/@11 | Không tạo rule trùng. Phải xét ngoại lệ tự động, rule LAN và Employee, state và chiều vào interface. |

Rule `SOC TEST EMPLOYEE TO DC HTTP` là ngoại lệ thử đã tồn tại: `192.168.40.100 → 192.168.30.10 TCP8000`, khác P10–P40. Không suy tên HTTP thành dịch vụ nghiệp vụ được duyệt hoặc xác nhận có server đang nghe TCP8000. Nếu cần loại ngoại lệ này để thực thi chính sách liên vùng mới, phải phê duyệt riêng thay đổi VLAN40; không sửa bằng rule trên VLAN30 và không tự vô hiệu hóa nó ở nhóm này.

**Số rule mới đủ điều kiện áp dụng ngay vẫn là 0** vì chưa có luồng dịch vụ cụ thể được duyệt. Mục tiêu nhóm đọc đã đạt; mục tiêu hoàn thiện chính sách và kiểm thử lưu lượng chưa đạt/chưa thực hiện.

## 2.8. Thuật ngữ và cơ sở giải thích

Firewall rule là quy tắc tường lửa, đối chiếu địa chỉ, giao thức, port, interface và hướng để cho phép/chặn. PF (Packet Filter — bộ lọc gói) là backend ruleset đang nạp được đọc bằng pfctl. Stateful filtering là lọc có trạng thái: phiên đã được phép có thể cho gói trả lời qua state; quick dừng xét khi khớp, còn rule không quick có thể bị rule phù hợp sau thay quyết định. Trong SOC, cơ chế này thực thi phân vùng và ghi log để giám sát. Ví dụ đã xác minh: UUID Employee TCP8000 có cả trong XML và PF @96; chưa kiểm chứng lưu lượng.

OPNsense là tên sản phẩm, không tự khai triển. HA (High Availability — tính sẵn sàng cao) là mô hình dự phòng; pfsync là tên giao thức đồng bộ trạng thái của PF, không tự tạo dạng khai triển. Trong topology, vtnet2 là đường SYNC đã xác nhận; ba rule của đường này có mặt nhưng không phải bằng chứng failover. VLAN (Virtual Local Area Network — mạng cục bộ ảo) tách miền Layer 2; Core vận chuyển frame còn firewall lọc lưu lượng định tuyến qua các interface VLAN. Các thuật ngữ còn lại dùng hồ sơ thuật ngữ chung và đọc kèm trạng thái kiểm chứng mới này.

Nguồn chính thức về nguyên lý: [OPNsense Rules](https://docs.opnsense.org/manual/firewall.html), đã đối chiếu trong phiên rà soát chính sách trước. Tài liệu hiện hành không thay thế đầu ra thực tế của phiên bản lab 26.7. Các kết luận cấu hình trong báo cáo dựa trên JSON và PF đã thu, không dựa vào ví dụ tài liệu ngoài.

## 2.9. Hình, danh mục minh chứng và bàn giao

`evidence-index-final.csv` có tên tệp, nội dung, thời điểm kèm UTC+07:00, đường dẫn, vị trí dự kiến trong báo cáo và SHA-256. Ảnh nguồn được giữ nguyên, không thay bằng ảnh dựng.

- Hình 2.3 (số dự kiến): `primary-shell-confirm-20261103T163911+0700.png`. Mục đích xác minh shell; nội dung menu chuyển vào root shell; kết quả có dấu nhắc; ý nghĩa đủ điều kiện gửi lệnh chỉ đọc.
- Hình 2.4 (số dự kiến): `readonly-console/job6-20261103T164342+0700.png`. Mục đích chứng minh collector hoàn tất; nội dung PUBLIC_RULES_READY, số rule và config_unchanged; kết quả 7 modern/0 legacy; ý nghĩa xác nhận mốc thu, được đối chiếu bằng JSON và hash payload.
- Hình 2.5 (số dự kiến): `current-rules-tail-20261103T164800+0700.png` hoặc ảnh quan sát sau cùng tên phần mô tả. Mục đích minh họa rule đang nạp; nội dung phần cuối pfctl gồm quản trị, SYNC và Employee; kết quả đối chiếu JSON; ý nghĩa cho thấy rule Employee tới DC vẫn tồn tại. Tệp text đầy đủ bổ sung các dòng ngoài màn hình.

Khi xuất Word: A4, Times New Roman 12–13, lề trái 3 cm, các lề còn lại 2 cm; chú thích dưới hình, điều chỉnh số hình theo chương thực tế. Chưa xuất Word ở nhóm này.

Primary giữ chạy; không tự shutdown/reboot hoặc chuyển nhóm. Không commit/push Git. Dừng chờ người dùng xác nhận trước mọi bước tiếp theo.
