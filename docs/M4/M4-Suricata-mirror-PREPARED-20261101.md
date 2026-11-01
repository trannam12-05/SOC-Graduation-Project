# CHƯƠNG 4. CHUẨN BỊ SURICATA NHẬN MIRROR VÀ TÍCH HỢP SOC

## 4.1. Phạm vi, trạng thái và nguyên lý

Ngày 01/11/2026, UTC+07:00. **Thiết kế/chưa triển khai:** chưa có sensor chạy, chưa cài Suricata, chưa cấu hình mirror, chưa có PCAP hoặc alert thử nghiệm thật. Giữ VM tắt trong lúc người dùng học Labtainer. Không dùng kết quả mock hoặc frame mẫu làm minh chứng phát hiện.

Suricata là tên chính thức của công cụ phân tích an ninh mạng. Sensor nhận bản sao Ethernet qua mirror nên là IDS (Intrusion Detection System, hệ thống phát hiện xâm nhập); chưa có IPS (Intrusion Prevention System, hệ thống ngăn chặn xâm nhập) inline. Core OVS chỉ Layer2, bản sao không thay đường chuyển tiếp gốc. SPAN/port mirroring chọn nguồn/hướng rồi đưa bản sao tới cổng quan sát; không tự quan sát được đường đi ngoài OVS.

## 4.2. Đường nhận lưu lượng và mapping cần chốt

```text
7 data ports Core -> OVS ingress Mirror -> ens10 (MAC 02:53:45:f2:19:07)
                   -> segment capture riêng -> SENSOR_CAPTURE (MAC/tên NIC chưa biết)
Sensor management -> NIC riêng -> VLAN99 Management, mapping/IP chưa chốt
eve.json -> Wazuh agent trên sensor -> Wazuh server/indexer/dashboard (dự kiến M5)
```

Không bridge NIC capture sang NIC quản trị hoặc WAN. Capture không IP/gateway; NIC quản trị có chính sách riêng, không đổi mapping Core. Mirror dự kiến chọn ingress ens3–ens9, VLAN30/40/50/60/99 và output ens10 chuyên dụng. Gói gửi ngược từ capture phải không chuyển sang data port. Khi firewall đưa một gói qua Core nhiều lần có thể có nhiều bản quan sát; ghi rõ vị trí/cả hai chiều, không suy mọi gói giống nhau là lỗi duplicate.

Phương án M4 tối thiểu sau M2: chưa cần sensor online, giữ PCAP thật từ TAP ens10 của phiên thử OVS rồi tắt Core, phân tích offline bằng Suricata trên một môi trường đủ RAM. Cách này chứng minh nhận/phân tích bản lưu khi có alert thật; không chứng minh pipeline live hoặc Wazuh thời gian thực.

## 4.3. Capture, tag và packet drop

Trước thu: xác minh MAC sensor, interface capture/management, MTU, trạng thái link, capture không IP, tool/version. Thu counter Core, TAP, NIC sensor và Suricata trước/sau; xem offload/VLAN metadata và queue. Chỉ sửa offload trên sensor sau backup và có phạm vi thực thi, không thay host Windows/VMware hoặc NIC EVE quản trị. GRO/LRO có thể làm biến dạng cách nhìn gói; tham khảo theo phiên bản thực tế, không chép tùy chọn kernel một cách mù quáng. [Suricata packet capture](https://docs.suricata.io/en/latest/performance/packet-capture.html).

Capture thử hữu hạn trên mạng lab riêng, chỉ nguồn/đích/marker đã chốt. Ví dụ tương lai: tcpdump -i SENSOR_CAPTURE -nn -e -s 0 -c 20 -w m4-marker.pcap, kèm BPF giới hạn ICMP thử; dùng timeout để không chờ vô hạn, exit124 không phải PASS. Với VLAN tag, đối chiếu bytes Ethernet/TPID/TCI và metadata capture; không chỉ nhìn cột VLAN trên GUI. So sánh frame nguồn, trunk và ens10; giữ nguyên PCAP gốc, ghi SHA-256 và collector time UTC+07:00.

Đo packet drop bằng chênh counter trước/sau của đúng phiên: gói phát đánh số/marker, gói ở mirror, kernel capture drop, Suricata capture/drop và decoder errors. Tránh công thức lấy tổng counter từ lúc boot rồi gọi là tỷ lệ phiên. Nếu mẫu nhỏ không có drop thì chỉ kết luận không quan sát drop trong mẫu, không bảo đảm thông lượng. Không chạy stress trong ngân sách RAM thấp.

## 4.4. Kiểm thử phát hiện vô hại đã chuẩn bị

suricata/soc-lab.rules có một rule ICMP nhận chuỗi SOC-M4-TEST-20261101, SID1000001 (mã nhận dạng rule cục bộ, phải kiểm tra trùng). automation/m4_benign_frame.py tạo một Ethernet/IPv4/ICMP frame đúng checksum; mặc định chỉ PREPARED_NOT_SENT, không gửi. Chỉ future --execute --resources-ready trên EVE mới phát một frame vào TAP ens3 đã kiểm tra. Địa chỉ 192.168.30.101/.102 là đề xuất thử cần xác nhận; không gán IP cho Core/host và không đòi có ping reply. Đây là traffic đánh dấu nội bộ, không scan/khai thác hay truy cập Internet.

Các frame EtherType88b5 của bộ M2 chỉ chứng minh chuyển mạch; rule ICMP không được coi là sẽ phát hiện chúng. M4 cần frame IPv4/ICMP riêng hoặc client thử thật. Chạy suricata -T với cấu hình/rule của sensor trước; sau đó phân tích bản PCAP thật bằng -r vào thư mục log mới. Không dùng tùy chọn xóa PCAP, không chạy song song service live với tiến trình offline cùng interface/logdir. Chốt command theo phiên bản đã cài. [Suricata CLI](https://docs.suricata.io/en/latest/command-line-options.html).

## 4.5. Checklist thực thi, chưa chạy

| ID | Điều kiện và thao tác | Kết quả mong đợi / bằng chứng |
|---|---|---|
| M4-01 | M2 mirror đã đạt, mapping capture hai đầu xác minh | OVS Mirror JSON, MAC/port, ảnh topology thật |
| M4-02 | Kiểm interface sensor không IP, management tách riêng | ip/link/route, MAC, không bridge vòng lặp |
| M4-03 | Phát frame marker hữu hạn, capture nguồn/ens10/sensor | Marker có ở mirror và sensor; tag thực tế được ghi, không giả định |
| M4-04 | Đưa frame từ capture ngược vào Core | Data port không nhận; có đối chứng dương nguồn khác |
| M4-05 | suricata -T rồi -r PCAP thật với rule lab | Cấu hình hợp lệ; eve.json có event_type alert, SID1000001 và thời gian/địa chỉ đúng |
| M4-06 | Lặp bằng marker khác không khớp rule | Không alert SID1000001 cho marker không khớp, engine vẫn nhận gói |
| M4-07 | Đọc capture/drop/decoder counters trước/sau | Số liệu phiên, giới hạn mẫu và mất gói được trình bày chính xác |
| M4-08 | Nếu đủ RAM: sensor live trên NIC capture | Alert live gắn capture và marker; không gọi offline là live |
| M4-09 | Wazuh agent đọc EVE rồi server nhận | Alert/event gắn sensor, SID, timestamp và địa chỉ; ảnh dashboard hoặc log thật |

## 4.6. Log và kiến trúc tích hợp dự kiến

EVE của Suricata (Extensible Event Format) là log JSON, **khác sản phẩm EVE-NG**. eve.json có thể chứa alert và dữ liệu giao thức; thu các trường timestamp, event_type, flow_id, alert.signature_id/signature, địa chỉ và VLAN khi bản thực tế cung cấp. Không mặc định mọi phiên bản/event đều có trường VLAN. [EVE JSON](https://docs.suricata.io/en/latest/output/eve/eve-json-output.html).

Wazuh là nền tảng giám sát an ninh: agent trên sensor dự kiến đọc JSON và gửi tới server; indexer lưu/tìm kiếm, dashboard hiển thị. Fragment suricata/wazuh-localfile-PROPOSED.xml chỉ là đoạn localfile cần merge sau backup, chưa cài vào ossec.conf. Không ghi đè cấu hình agent đầy đủ. Phải kiểm đường log, quyền đọc, agent kết nối và server decoder/rule trước khi nói tích hợp đạt. Chứng minh event ở sensor rồi ở server bằng SID/thời gian/marker, không chỉ ảnh service active. [Wazuh Suricata integration](https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html).

Không bật đồng thời toàn bộ Wazuh/Suricata/HA trên EVE8GiB. Nếu chưa đủ RAM cho server, hoàn tất log Suricata thật và chuẩn bị chuyển log có kiểm soát; ghi M5 chưa triển khai, không tạo screenshot dashboard giả. Bằng chứng mới lưu docs/evidence/M4/<phiên>; PCAP giữ riêng theo .gitignore và rà dữ liệu trước công bố.
