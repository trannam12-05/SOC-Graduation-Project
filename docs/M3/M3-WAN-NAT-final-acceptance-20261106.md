# 3.16. Nghiệm thu WAN và NAT Internet tối thiểu M3

## 3.16.1. Kết luận và phạm vi
Ngày06/11/2026 (UTC+07:00), hạng mục WAN/NAT được phê duyệt đạt **DONE/PASS**. Các mục M3 độc lập đã giao được đóng theo phạm vi nghiệm thu hiện có, tái sử dụng PASS lịch sử, không chạy lại. Không suy thành nghiệm thu NAT HA giữ phiên, toàn bộ SOC, M4/M5 hoặc mọi đích Internet.

Đã chuyển đúng hai WAN sang pnet0 có guard/watchdog, giữ DHCP; áp một rule egress và một Hybrid SNAT giới hạn trên mỗi firewall; gửi đúng một HTTPS HEAD từ Employee-Linux tới1.1.1.1:443. Không sửa HA/CARP/pfsync/hook, Core, VLAN/IP nội bộ, VPCS hoặc WAN2. Không dừng/khởi động lại node hoặc cài phần mềm.

## 3.16.2. Sao lưu, guard và chuyển WAN
Cấu hình mỗi firewall được sao lưu root-only quyền0600 vào /root/soc-m3-wan-nat-20261106/config.before.xml; trước thêm rule có config.before-nat.xml riêng. Hash before/after và UUID rule trong kết quả apply từng máy. Topology và bridge membership nằm trong giao dịch /root/soc-m3-wan-live-20261106T212212Z/, gồm lab-before.unl và state.json. Hash topology trước/sau lưu tại M3-WAN-NAT-acceptance.json. Không xuất config thô chứa bí mật vào docs.

Guard xác minh tên/UUID/PID QEMU và đúng TAP, pnet0 IP/route, năm vai trò CARP, syncok/demotion, hash interfaces/virtualip/hasync và hook. Đã thử đọc guard không đổi mạng trước mutation. Watchdog độc lập được arm180giây trước chuyển link để trả TAP về bridge cũ và phục hồi XML nếu hash vẫn thuộc giao dịch; không ghi đè thay đổi cạnh tranh. Runtime đổi đúng vunl0_1_1 và vunl0_2_1 sang pnet0, metadata chuyển hai vtnet1 sang network12 WAN1-UPSTREAM-PNET0; giữ bridge network4 cũ. Không nối toàn bridge cũ hoặc chuyển eth0 quản trị. Các TAP khác được kiểm tra giữ master cũ.

| Thành phần | Cấu hình thực tế đã kiểm chứng |
|---|---|
| Primary WAN | vtnet1,192.168.220.144/24 do DHCP cấp |
| Secondary WAN | vtnet1,192.168.220.145/24 do DHCP cấp |
| Gateway hai máy | 192.168.220.2, IPv4 default route tồn tại |
| Quản trị EVE | pnet0 vẫn192.168.220.143/24, route qua192.168.220.2; SSH thu kết quả thành công |
| Topology cuối | 11node/12network, hash khớp bản commit |
| Employee-Linux | 192.168.40.110/24 DHCP trên employee0, gateway192.168.40.1; đọc lại trước NAT |

Không tự gán IP/VIP. Watchdog được disarm sau khi cả hai lease/gateway, runtime/metadata, HA và quản trị đạt; kiểm tra cuối không còn tiến trình watchdog. Không có lỗi mạng yêu cầu rollback. Backup và manifest được giữ để rollback có kiểm soát nếu sau này được giao.

## 3.16.3. Firewall và Hybrid SNAT
Đã áp Secondary trước, đọc guard rồi mới áp Primary. Mỗi máy có một firewall rule mới: pass/in/quick trên opt2 VLAN40, IPv4/TCP, source192.168.40.110/32, destination1.1.1.1/32, port443, log bật và keep state. Không mở Guest/DC/DMZ/Management hoặc any-any.

Outbound mode Hybrid; một rule SNAT ưu tiên trên WAN/vtnet1 với cùng nguồn/đích/TCP443, translation là địa chỉ interface WAN động, static-port tắt. Schema Filter.xml của phiên bản đang cài được đọc trước khi áp; mode dùng nat/outbound/mode=hybrid. Target model để trống theo cơ chế địa chỉ interface; đã xác minh rule PF thực nạp:

```text
nat log on vtnet1 inet proto tcp from 192.168.40.110 to 1.1.1.1 port = https -> (vtnet1:0) port 1024:65535
```

NAT (Network Address Translation) là dịch địa chỉ mạng; SNAT (Source Network Address Translation) dịch địa chỉ nguồn khi gói rời WAN, cho phép phản hồi quay về endpoint nội bộ. Trong SOC, chỉ nguồn/dịch vụ được firewall cho phép mới được sử dụng luồng này. Hybrid giữ các rule tự động đồng thời thêm rule thủ công ưu tiên; không tuyên bố bảng NAT chỉ chứa một nguồn. NAT không thay thế chính sách firewall. Cặp firewall được áp rule tương đương riêng từng máy; không đổi nhóm XMLRPC/hasync hoặc chạy đồng bộ toàn cấu hình.

Mỗi bước dùng model validation, xác nhận rule PF nạp bằng UUID và đối chiếu canonical toàn bộ rule cũ; interfaces/virtualip/hasync được so sánh giữ nguyên. Chỉ filter reload, không flush state/restart HA. UUID FW/SNAT và hash cấu hình của từng máy nằm trong results-20261106T213614+0700.json (Secondary), results-20261106T214203+0700.json (Primary).

## 3.16.4. HTTPS và bằng chứng dịch nguồn
Một curl HEAD duy nhất, buộc IPv4/employee0, destinationhttps://1.1.1.1/, không proxy, retry hoặc theo redirect, timeout12giây; giữ kiểm chứng chứng chỉ TLS, không dùng insecure. Script có sentinel chống chạy lại. Không thử đích khác hoặc các ca PASS trước.

| Nội dung | Kết quả |
|---|---|
| Nguồn/đích curl | 192.168.40.110 →1.1.1.1:443 |
| curl exit/TLS verify | 0/0 |
| HTTP | 301, không theo Location; chứng minh HTTPS response, không đòi HTTP200 |
| Số request | 1 |
| Thời gian curl báo | 0.439285giây, không dùng làm benchmark hoặc SLA |
| SYN phía Employee | 192.168.40.110:52552→1.1.1.1:443 |
| SYN phía WAN | 192.168.220.144:58206→1.1.1.1:443 |
| Đối chiếu | Cùng TCP sequence240639040; NAT translation proved=true |

PCAP thụ động đồng thời trên TAP Employee và WAN Primary, filter chỉ host1.1.1.1/TCP443, snaplen128; không phát gói riêng để đo. Employee24packet, WAN25packet; không suy số lượng này thành zero loss. SHA-256 PCAP và cặp SYN nằm trong nat-pcap-analysis.json. HTTPS-acceptance.json chứa argv/metrics/return code thật đã kiểm checksum qua console. TLS là Transport Layer Security, bảo vệ phiên HTTPS; ở đây chỉ kiểm chứng chứng chỉ trong phiên được duyệt, không kiểm thử IDS/IPS hoặc tấn công.

## 3.16.5. Bảo toàn HA, chẩn đoán công cụ và giới hạn
Guard cuối PASS: Primary MASTER/Secondary BACKUP cả VLAN30/40/50/60/99, syncok1/demotion0 hai phía. Hash cấu hình interfaces/virtualip/hasync và hook khớp baseline. PID Primary4985, Secondary4075, Core4665, Employee55311 không đổi. Không đo tính liên tục SLA hoặc chạy failover.

Một lượt guard sau áp Secondary báo GUARD_FAILED vì công cụ so sánh tuple với list khi đọc lại JSON. Các giá trị HA/quản trị thực tế khớp; đã chuẩn hóa cấu trúc dữ liệu, giữ nguyên log lỗi và đọc guard lại PASS trước chạm Primary. Đây là lỗi công cụ đã sửa, không báo thành lỗi HA hoặc xóa lịch sử. Không cần rollback mạng vì không quan sát thấy điều kiện HA/quản trị sai lệch theo guard.

WAN VIP chưa được tạo; source NAT dùng WAN IP riêng nên chưa nghiệm thu giữ phiên Internet khi failover. Tình trạng bulk sync dài trước đây chỉ được giải thích về tác nhân tái khởi tạo hook; nguyên nhân sâu của thời gian chờ chưa tuyên bố đã khắc phục. Không sửa hook theo giới hạn người dùng. Các nội dung này là giới hạn ngoài đợt NAT tối thiểu được duyệt, không được tự sửa hoặc tự kiểm thử thêm.

## 3.16.6. Bảng đóng phạm vi M3
| Tiêu chí | Trạng thái | Minh chứng, không kiểm thử lại |
|---|---|---|
| pfsync persistent | PASS lịch sử | todo-completion-20261103/M3.1-acceptance.json |
| CARP5VLAN | PASS lịch sử | todo-completion-20261103/M3.2-acceptance.json |
| CARP failover/recovery | PASS lịch sử | M3.3-failover-20261104/run-105204/M3.3-acceptance.json |
| pfsync state/continuity | PASS lịch sử | M3.4B-pfsync-state-20261104/M3.4-acceptance.json |
| DHCP/DNS/firewall cơ bản | PASS lịch sử | M3.5-network-services-20261105/M3.5-acceptance.json |
| XMLRPC8rule/3pool đầy đủ | PASS phạm vi đã kiểm chứng | M3-runtime-review-20261106/acceptance.json, trường xmlrpc_configuration; overall PARTIAL cũ do NAT được giữ làm lịch sử |
| WAN/NAT Internet một Employee | DONE/PASS mới | M3-WAN-NAT-live-20261106/M3-WAN-NAT-acceptance.json |

Các đường dẫn bảng thuộc docs/evidence/M3/. Không sửa kết quả cũ thành kết quả mới. M3 DONE/PASS trong phạm vi các hạng mục độc lập đã được giao/nghiệm thu; không phải nghiệm thu NAT HA hoặc tích hợp SOC. Không chuyển M4/M5.

## 3.16.7. Hình và lưu trữ minh chứng
Thư mục docs/evidence/M3/M3-WAN-NAT-live-20261106/. evidence-index.csv ghi tên/nội dung/thời điểm lưu kèm múi giờ/đường dẫn/vị trí/hash; các thư mục transaction-* giữ ảnh framebuffer/log/state/PCAP được tải từ EVE. Tên batch dùng đồng hồ máy thu UTC+07:00; giờ guest/EVE nguyên bản chưa xác minh đồng bộ, không tự đổi thành thời gian Việt Nam. Không chỉnh nội dung ảnh.

Hình 3.16. OPNsense-Primary-status-20261106T214654+0700.png. Mục đích xác nhận WAN, rule SNAT và HA Primary; nội dung IP.144/gateway.2, rule giới hạn và năm MASTER/syncok1. Ý nghĩa cấu hình đã nạp và vai trò cuối phù hợp, không chứng minh failover NAT.

Hình 3.17. OPNsense-Secondary-status-20261106T214654+0700.png. Mục đích kiểm chứng phía dự phòng; nội dung IP.145/gateway.2, rule SNAT tương đương, năm BACKUP/syncok1. Ý nghĩa bảo toàn HA trong cửa sổ kiểm tra.

Hình 3.18. Employee-Linux-status-20261106T214535+0700.png. Mục đích kiểm chứng đúng endpoint/đích; nội dung source.40.110, destination1.1.1.1:443, HTTP301, TLSverify0, curlrc0, request1. Ý nghĩa nghiệm thu HTTPS tối thiểu qua NAT; bằng chứng gói bổ sung trong PCAP.

Công cụ hiện có thu console VNC và log SSH, chưa thu ảnh topology GUI mới. Để bổ sung thủ công: mở EVE lab SOC-M2-Core-L2, hiển thị đủ Employee-Linux, hai WANvtnet1 vào WAN1-UPSTREAM-PNET0/Cloud0 và các link nội bộ; chụp toàn màn hình rõ tên/link, không thông tin đăng nhập, lưu cùng thư mục dạng topology-WAN-final-YYYYMMDDTHHMMSS+0700.png. Không coi hình chưa chụp là minh chứng có sẵn.

Tham khảo chính thức về nghĩa mode NAT: [OPNsense Source NAT](https://docs.opnsense.org/manual/nat.html#source-nat-outbound); field/model áp dụng được đối chiếu schema cài trên chính guest. Tài liệu không thay thế bằng chứng runtime nêu trên.
