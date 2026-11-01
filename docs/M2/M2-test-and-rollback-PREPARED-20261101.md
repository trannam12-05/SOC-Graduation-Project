# CHƯƠNG 2. KỊCH BẢN KIỂM THỬ VÀ KHÔI PHỤC ĐÃ CHUẨN BỊ

## 2.1. Trạng thái và điều kiện thực thi

Ngày 01/11/2026, UTC+07:00. **Chưa chạy các script/ca kiểm thử trong tài liệu này.** Người dùng đang học Labtainer, yêu cầu mọi VM SOC giữ tắt. Chỉ thực thi sau khi người dùng thông báo tài nguyên sẵn sàng; không suy phê duyệt cũ thành quyền khởi động trong thời gian này.

Baseline cấu hình được kiểm chứng lúc 01:03–01:13: OVS 3.3.9, br-core-l2, ens3–ens7 access 30/40/50/60/99, ens8/ens9 trunk đúng năm VLAN, ens10 ngoài OVS, không mirror/IP/gateway, forwarding 0/0. Đến 07:58 không còn QEMU chạy; chưa xác nhận cấu hình runtime sau bật lại. Bản sao overlay lúc node tắt đã có checksum khớp, không thay nguồn.

## 2.2. Phương pháp thử nhẹ, không tạo đường đi tắt

Ưu tiên AF_PACKET (Linux packet socket, giao diện gửi/nhận frame Ethernet trực tiếp) trên EVE, bind riêng từng TAP đã có của đúng Core. TAP là giao diện Ethernet ảo nối kernel host với QEMU; frame gửi ra TAP đi tới vNIC guest, frame guest phát ra được thu tại TAP tương ứng. Không tạo Linux bridge, không gán IP cho EVE hoặc Core, không nối thêm EVE network/link, không khởi động helper VM.

Script chỉ nhận frame mang marker ngẫu nhiên của phiên, bỏ PACKET_OUTGOING để không nhầm bản phát với frame Core đã chuyển tiếp. PACKET_AUXDATA phục hồi VLAN khi kernel chuyển thông tin tag sang metadata. Bản ghi tx_hex lưu frame phát; PCAP mỗi TAP chỉ chứa frame thử được thu từ guest, không capture đại trà. Test phải thất bại nếu không có đối chứng dương; không coi không nhận được gói là VLAN isolation đã đạt khi đường phát/thu chưa được chứng minh.

Đây là kiểm thử chuyển tiếp qua QEMU/vNIC/datapath thật khi thực hiện thành công, không phải ovs-appctl ofproto/trace mô phỏng. Tuy nhiên không thay phép thử IP, gateway, lưu lượng ứng dụng, hiệu năng hay Suricata. Mỗi TAP phải không có master, lab không link; guard từ chối nếu topology thay đổi. Hai endpoint cùng EVE bridge ngoài Core không được dùng làm bằng chứng OVS.

## 2.3. Bảng ca kiểm thử dự kiến

| ID / nhóm | Mục tiêu | Điều kiện | Thao tác | Kết quả mong đợi | Bằng chứng cần thu | Trạng thái |
|---|---|---|---|---|---|---|
| L00 / tài nguyên | Không ảnh hưởng Labtainer/host | Người dùng xác nhận sẵn sàng | Đo RAM available/commit Windows, MemAvailable/swap EVE; chỉ bật Core nếu đủ | Có dự phòng thực tế, không thêm VM ngoài ngân sách | JSON tài nguyên có giờ UTC+07:00 | CHƯA CHẠY |
| L01 / baseline | Đúng node, MAC, phần mềm | Core đã bật an toàn | Đối chiếu UUID, QEMU/TAP, ens3–ens10, OVS version/show/Port/Interface/Mirror | Đúng mapping tám NIC, bảy cổng dữ liệu, không lỗi | QEMU args, MAC, OVS JSON, ảnh console | CHƯA CHẠY LẠI SAU BOOT |
| L02 / backup | Có đường khôi phục trước thay đổi | Root guest, đúng baseline | ovsdb-client backup, kiểm tra schema/hash/compact bản sao; lưu link/IP/route/unit | Snapshot root-only đọc được, không ghi DB/QCOW2 từ host | Metadata và log; raw DB chỉ trong guest | CHƯA CHẠY CHO ĐỢT MỚI |
| L03 / access, 5 frame case | Gán VLAN và cách ly broadcast | L01/L02 đạt; không mirror | Phát untagged vào lần lượt ens3–ens7 | Chỉ hai trunk nhận đúng VID; bốn access khác không nhận | result.json, tx_hex, PCAP riêng từng TAP, counter/FDB | CHƯA CHẠY |
| L04 / trunk, 10 frame case | Tag ingress/egress hai trunk | L03 đối chứng dương đạt | Phát tagged từng VID trên ens8 rồi ens9 | Access tương ứng nhận untagged; trunk kia nhận đúng VID, không rò VLAN | PCAP 802.1Q, log từng nguồn/đích | CHƯA CHẠY |
| L05 / negative trunk, 4 frame case | Chặn VID ngoài danh sách và untagged | Bộ thu đã có đối chứng dương | Mỗi trunk nhận VID100 rồi frame untagged | Không chuyển ra cổng dữ liệu khác | tx_hex + PCAP nguồn/đích + đối chứng trước/sau | CHƯA CHẠY |
| L06 / negative access, 1 frame case | Không chấp nhận VLAN khác trên access30 | Access30 hoạt động với untagged | Đưa tagged VID40 vào ens3 | Không chuyển sang VLAN40 hay trunk | Capture và log frame nhận dạng | CHƯA CHẠY |
| L07 / learned unicast, 10 frame case | Học MAC và chuyển đúng một đích | Broadcast đã học MAC thử trong mỗi VLAN | Năm VID: trunk tới MAC access, access tới MAC trunk | Chỉ đích đã học nhận, đúng bỏ/thêm tag; không flood trunk còn lại | FDB trước/sau, PCAP, counter | CHƯA CHẠY |
| L08 / đối chứng cuối, 1 frame case | Xác nhận đường đo còn hoạt động | Sau ca âm | Phát untagged access30 tới broadcast | Hai trunk nhận VID30 | PCAP và result.json | CHƯA CHẠY |
| L09 / mirror static | Đúng nguồn/hướng/đích mirror | Mapping ens10 đã xác nhận, snapshot mới | Thêm ens10 + Mirror trong một giao dịch; ingress bảy data port, năm VLAN | output_port chỉ ens10, không select_dst_port, không IP | OVS Mirror/Port/Interface JSON, ảnh | CHƯA CẤU HÌNH |
| L10 / mirror traffic | Quan sát bản sao, không phá forwarding | L09 đạt | Chạy lại bộ L03–L08 với --mirror, thêm frame ingress ens10 | Các ca dương có bản sao ens10; frame từ ens10 không chuyển tới data port | PCAP ens10 và đích chính; kiểm tra tag thực tế, không giả định | CHƯA CHẠY |
| L11 / persistence | Cấu hình và L2 duy trì sau khởi động lại | Snapshot mới, console và RAM ổn, không tác vụ guest đang ghi | Lưu boot_id/config/IP/route; shutdown/reboot mềm; chờ boot rồi đọc lại | boot_id đổi; OVS đúng; không IP/gateway; forwarding 0/0, dịch vụ active | Log hai boot, show/Mirror, unit/journal, ảnh thật | CHƯA CHẠY |
| L12 / lặp sau boot | Không chỉ DB persist mà frame vẫn đi đúng | L11 đạt | Chạy lại L03–L10 phù hợp cấu hình cuối | Bộ frame đạt trước/sau; không thêm VLAN hoặc route | Hai bộ result/PCAP và bảng so sánh | CHƯA CHẠY |
| L13 / lỗi & rollback | Hoàn nguyên có kiểm soát | Có snapshot đúng đợt và console root | Khi thất bại: dừng phát frame, lưu lỗi, khôi phục snapshot; đối chiếu baseline | Không mất log; access/trunk cũ trở lại; không chạy rollback rỗng từ đợt đầu | restore RC, snapshot hash và state trước/sau | CHƯA CHẠY CHO ĐỢT MỚI |

Bộ tự động có 31 case frame trước mirror và 32 case khi bật mirror. L03/L04 cũng quan sát không rò sang access khác; không phải thử trực tiếp hai access cùng VLAN vì thiết kế cuối mỗi VLAN chỉ có một access. Nếu cần hai access cùng VLAN phải có kế hoạch riêng, không thay tag access hiện tại để làm đẹp kết quả. Không dùng một PASS tổng để che ca FAIL; điều kiện thiếu được ghi BLOCKED/NOT RUN, không đổi thành PASS.

## 2.4. Script và trình tự chạy sau khi đủ điều kiện

- automation/m2_tap_frame_test.py: chạy trên EVE root, không sửa topology. --guest-ready là xác nhận điều kiện kỹ thuật đã kiểm tra, không phải công cụ tự bật VM. Guard kiểm tra lab/UUID/MAC/TAP không master; output phải mới, không ghi đè.
- automation/m2_mirror_guest_prepared.py: chạy trong guest root, các action backup/mirror/verify/rollback; không thay sudoers, không lưu bí mật. Backup yêu cầu chưa mirror và giữ nguyên bảy data port. Thay mirror có auto-rollback nếu kiểm tra tĩnh thất bại. Script này chưa có kết quả thực thi.
- configs/M2/soc-core-l2-noip.service và .sh: mẫu persistence cho interface nội bộ br-core-l2, chưa cài/enable. Chỉ tắt IPv6 host stack trên bridge, không đổi sysctl forwarding hoặc NIC cũ. Script dừng nếu đã có IP ngoài dự kiến, không tự flush địa chỉ.

Ví dụ lệnh tương lai, **chưa chạy**, cần chuyển script qua đường console đã kiểm chứng và đối chiếu SHA-256 trước:

```text
# Trong guest; dùng thư mục mới cho mỗi đợt
python3 m2_mirror_guest_prepared.py backup --work /root/m2-traffic-<timestamp>
# Trên EVE; xác minh guest sẵn sàng trước
python3 m2_tap_frame_test.py --guest-ready --output /root/m2-frame-before-<timestamp>
# Trong guest; thêm mirror sau khi bộ trước mirror đạt
python3 m2_mirror_guest_prepared.py mirror --work /root/m2-traffic-<timestamp>
# Trên EVE
python3 m2_tap_frame_test.py --guest-ready --mirror --output /root/m2-frame-mirror-<timestamp>
# Trong guest, chỉ khi cần khôi phục snapshot của chính đợt này
python3 m2_mirror_guest_prepared.py rollback --work /root/m2-traffic-<timestamp>
```

Lệnh ví dụ dùng placeholder timestamp, không dán nguyên dấu < > vào shell. Mỗi phiên frame tạo tối đa vài chục frame và chờ thu khoảng nửa giây/case; không đo stress. Thu thêm ovs-appctl fdb/show br-core-l2, ovs-ofctl dump-ports/dump-flows và journal chọn lọc trước/sau. PCAP chứa frame đánh dấu thử giữ cục bộ theo .gitignore; JSON/ảnh sạch dùng cho báo cáo và Git.

## 2.5. Persistence và rollback dự kiến

Sau bật lại lần đầu, đọc cấu hình **trước khi sửa** để biết OVSDB thực sự persist đến đâu. OVSDB lưu cấu hình bền vững không đồng nghĩa cờ admin UP/IPv6 runtime của bridge tự persist. Nếu bridge tự sinh IP/route, ghi lỗi và bản chụp; không tuyên bố PASS. Khi baseline hợp lệ và đã sao lưu, kiểm tra không có tệp cùng tên trước khi đặt helper ở /usr/local/sbin và unit ở /etc/systemd/system. Không ghi đè unit/helper cũ. Chạy kiểm tra cú pháp, daemon-reload, enable/start đúng unit mới rồi thu log. Không thay networkd/netplan/seed/NIC cũ.

Rollback unit: trước tiên lưu trạng thái enabled/active và nội dung tệp nếu có; chỉ disable unit do chính đợt này tạo, giữ lại unit/helper trong thư mục backup có timestamp thay vì xóa dữ liệu, daemon-reload. Khôi phục cờ bridge/IPv6 theo snapshot; không ghi forwarding. Nếu reboot không lên, giữ log và dùng console; không Wipe/Reset. Rollback OVS dùng snapshot mới đã có br-core-l2 và bảy port, không dùng bản /root/m2-isolated-20261101T0035/ovsdb.before vốn khôi phục OVS rỗng.

Backup overlay đã thu lúc node tắt tại /root/m2-stopped-backup-20261101T075852Z/core-overlay.qcow2 là dự phòng cuối. Metadata ở docs/evidence/M2/accelerated-20261101/stopped-backup.json. Không phục hồi overlay trong lúc VM chạy; trước phục hồi phải xác minh đúng backing chain và giữ thêm bản trạng thái lỗi. Chưa kiểm thử restore overlay hoặc restore của script mới; rollback thực tế đã đạt trước đây chỉ là lần tạo bridge đầu tiên được ghi trong báo cáo cấu hình.

## 2.6. Minh chứng, thời gian và giới hạn

Ghi collector_time với UTC+07:00 cho mỗi lần nhận log; đồng hồ EVE/guest không được coi là chuẩn khi chưa đồng bộ. PCAP timestamp của EVE phải đi cùng metadata collector. Danh mục cần có tên tệp, nội dung, thời điểm/múi giờ, đường dẫn, vị trí báo cáo và hash. Ảnh console lấy framebuffer thật, không vẽ lại kết quả; chưa thể chụp runtime khi Core tắt. Khi có thể, chụp topology GUI sau khi đúng trạng thái; ảnh chưa chụp phải ghi thiếu.

Script mới chỉ kiểm tra cú pháp tại máy soạn; chưa kiểm chứng runtime Linux/OVS, nên cần thử có giám sát ở đợt M2 thật. Mọi kết quả PASS/FAIL của lưu lượng, mirror, persistence và HA hiện vẫn chưa có. Kế hoạch M3 riêng: ../M3/M3-OPNsense-HA-PROPOSED-20261101.md.
