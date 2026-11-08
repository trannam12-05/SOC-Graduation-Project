# 1. Đối chiếu bằng chứng — phần Nam (Network & OPNsense)

Chốt hồ sơ triển khai:07/11/2026, UTC+07:00; biên tập08/11/2026. Không có phép thử lab mới. Nguồn tiến độ: [SOC_TO_DO](../SOC_TO_DO.md). PASS dưới đây chỉ áp dụng đúng ca/thời điểm nghiệm thu, không xác nhận runtime tại ngày biên tập.

| Nội dung | Trạng thái | Nguồn đối chiếu | Cách dùng trong báo cáo |
|---|---|---|---|
| M1 thiết kế và topology nội bộ | PASS phạm vi | [M1 cuối](../M1/M1-final-acceptance-20261105.md) | Một Core OVS, hai firewall,5VLAN; cấu trúc12/12, không suy mọi dịch vụ đã chạy |
| VLAN30/40/50/60/99 | PASS | [M3.2 nghiệm thu](../evidence/M3/todo-completion-20261103/M3.2-acceptance.json) | DMZ60/.60.0/24, không DMZ10 trong lab; VIP .1, Primary .2, Secondary .3 |
| Core L2/access/trunk | PASS | [M2 tổng kết](../M2/M2-final-summary-20261103.md) | ens3–ens7 access; ens8/ens9 trunk; không IP ngoài loopback, forwarding0/0 |
| Routing/firewall chọn lọc | PASS | [M2 kết quả](../evidence/M2/final-acceptance-20261103/M2-results.json) | TCP8000 allow, hai ca deny có PCAP/counter; không nâng checklist TCP8080 thành đã thử |
| SPAN/OVS Mirror | PASS | M2 tổng kết mục2.6 | Ingress ens3–ens9, output ens10, select_dst_port rỗng; counter48frame/4278byte, có markerGET |
| pfsync persistent | PASS | [M3.1](../evidence/M3/todo-completion-20261103/M3.1-acceptance.json) | Hook tự áp sau reboot từng firewall; vtnet2/SYNC đúng; không gọi lại native để làm đạt |
| CARP failover/recovery | PASS | [M3.3](../evidence/M3/M3.3-failover-20261104/run-105204/M3.3-acceptance.json) | Shutdown Primary→Secondary MASTER5VLAN; recovery đúng hai vai |
| State/continuity TCP | PASS — một phiên | [M3.4B](../evidence/M3/M3.4B-pfsync-state-20261104/M3.4-acceptance.json) | .40.100:44341→.30.10:8000; ID/creator khớp, HTTP200/350byte; không reconnect |
| DHCP/DNS/firewall | PASS phạm vi | [M3.5](../M3/M3.5-network-services-steps-1-5-20261105.md) | Lease .40.110/.50.110, DNS/gateway VIP;7ca live; Management chỉ ICMP VIP |
| XMLRPC config/runtime | PASS phạm vi | [M3 runtime](../M3/M3-runtime-verification-20261106.md) |8rule/3pool khớp đầy đủ XML;8/8UUID rule mỗi máy; Kea running, không lease HA |
| WAN/SNAT HTTPS | PASS — một HEAD | [M3 NAT cuối](../M3/M3-WAN-NAT-final-acceptance-20261106.md) | WAN .220.144/.145, GW .2; .40.110→1.1.1.1 TCP443; HTTP301/TLSverify0/curlrc0 |
| Sensor/alert marker | PASS phạm vi | [Sensor sau marker](../evidence/M4/resume-20261102/sensor-public-after-marker.json) | Suricata7.0.3, capture0 không IP, SID1000001/rev1, ICMP, VLAN[30] |
| Manager EVE replay | PASS — replay | [Đối chiếu trường](../evidence/M5/continuation-20261102/decoded-field-validation.json) | Wazuh rule86601/level3; hash và flow/IP/VLAN/SID khớp; giữ xuất xứ hồ sơ M5 lịch sử |
| Toàn tuyến sensor→Manager live | PARTIAL | [Manager/replay](../M5-verification-and-demo-20261102.md) | Hai chặng đã đạt riêng, chưa có vận chuyển tự động với cùng event mới |
| M4.3 quản trị / M4.4 Syslog | PARTIAL/BLOCKED | [Checkpoint07/11](../evidence/M4/M4.3-M4.4-20261107/report.md) | Primary offline, Wazuh từ chối khóa; chưa nhận log firewall; TCP514 refused không kết luận UDP514 |
| Indexer/Dashboard/Filebeat node EVE | Chưa triển khai theo kiểm kê lịch sử | Manager/replay, checkpoint07/11 | Không dùng Kibana phiên khác làm bằng chứng Wazuh Dashboard node này; VMware chưa kiểm kê đủ |
| Hai Core, LACP, STP dự phòng | DESIGN ONLY / không áp dụng lab | M1/M2 | Giữ topology đầu vào đúng bối cảnh; không nhận là thiết bị/tính năng đã triển khai |
| WAN VIP/NAT HA, DHCP lease HA, zero loss/RTO | Chưa nghiệm thu | M3 NAT/M3.4B | Không suy từ một phiên nội bộ, rule trùng hoặc một HTTPS |
| API block/unblock tự động và automation HA | DESIGN ONLY / chưa có nghiệm thu live | M3/M4 và phần Mock của nhóm | OPNsense API là điểm tích hợp M5; decision/mock_applied không phải chặn traffic thật |

## 1.1. Những khác biệt đã xử lý

- Bảng/sơ đồ Nam cũ dùng VLAN10 và parent `vtnet1`: sửa thành VLAN60 và trunk `vtnet0` theo mapping nghiệm thu.
- Mục2.2.7 và2.2.18 cũ ghi chưa có failover: cập nhật M3.3/M3.4B, giữ giới hạn NAT/lease/automation/zero-loss.
- Bảng3.2.2 cũ trộn checklist T-01…T-19, TCP8080, LACP và ảnh ping: thay bằng bảng ca M2/M3 có nguồn, giữ ảnh phiên nhóm với chú thích đúng giới hạn.
- Truy vết Nam cũ gộp ACL/LACP và chỉ dẫn thiếu Bảng2.4a–c: tách mapping, policy và giới hạn HA/Mirror; không sửa kết quả AI/ELK/Mock của thành viên khác.
- Kết luận chung cũ xếp “duy trì state qua HA” vào phần chưa chứng minh: sửa riêng điểm mâu thuẫn với M3.4B; giữ các giới hạn AI và automation.

## 1.2. Ảnh và sơ đồ

Hình2.3–2.3e là sơ đồ biên tập lại theo hồ sơ, có nhãn rõ không phải ảnh chụp lab; nguồn SVG chỉnh sửa được và PNG nền trắng nằm trong `images/`. Hình3.17–3.25 và ảnh phiên nhóm được giữ là ảnh thực nghiệm gốc, không dùng sơ đồ dựng lại thay bằng chứng. Việc kiểm toàn vẹn ảnh và bảo toàn nội dung được ghi trong `images/validation.json` sau kiểm tra Word.
