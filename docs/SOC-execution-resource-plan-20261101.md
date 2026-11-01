# Kế hoạch vận hành tuần tự đến hạn 05/11/2026

## 1. Giới hạn hiện hành

Trước 10 giờ ngày 01/11 và cho đến khi người dùng thông báo tài nguyên sẵn sàng: chỉ tài liệu/script/kiểm tra tĩnh, không bật VM SOC, không can thiệp Labtainer. Không có lịch tự khởi động lúc 10 giờ. Mọi số liệu tài nguyên đã thu là lịch sử, phải đo lại trước đợt chạy thật.

Windows vật lý16GiB, EVE tổng đo được7897MiB, Core2048MiB. Không đồng nhất RAM trống trong EVE với RAM available trên Windows. Ước lượng overhead EVE1GiB dưới đây là dự phòng lập kế hoạch, không phải số đo cam kết. Không tăng RAM/CPU hoặc sửa VMware/Windows/EVE trong đợt chuẩn bị.

## 2. Nhóm máy có thể cân nhắc chạy cùng nhau

| Nhóm tương lai | RAM guest dự kiến | Tính cả EVE dự phòng1GiB | Khả năng và giới hạn |
|---|---|---|---|
| Chỉ Core, endpoint bằng TAP | 2GiB | Khoảng3GiB | Ưu tiên M2; không cần helper VM. Vẫn chờ Windows đủ RAM và người dùng xác nhận |
| Chỉ Primary trong lúc cài | 3–4GiB | Khoảng4–5GiB | Core/sensor/Secondary giữ tắt; image chính thức và đĩa phải sẵn sàng |
| Core + Primary | 5–6GiB | Khoảng6–7GiB | Có thể demo gateway/rule khi số đo host cho phép; không HA; client nhẹ phải cộng thêm ngân sách |
| Core + sensor nhỏ | Khoảng4GiB nếu sensor dự trù2GiB | Khoảng5GiB | Chỉ vài rule, lưu lượng nhỏ, không coi2GiB là yêu cầu chính thức/đủ cho ruleset lớn; cần đo sensor thật |
| Chỉ sensor phân tích PCAP offline | Sensor dự trù2GiB | Khoảng3GiB | Tắt Core/firewall, dùng PCAP đã thu thật; không chứng minh live IDS |
| Core + Primary3GiB + sensor2GiB | 7GiB | Khoảng8GiB | Không chọn với EVE7897MiB vì thiếu dự phòng |
| Core + hai OPNsense3GiB | 8GiB | Khoảng9GiB | Vượt EVE hiện có; HA đầy đủ bị chặn tài nguyên |
| Core + cặp HA + sensor/Wazuh | Lớn hơn mức trên | Còn tăng theo dịch vụ | Cần môi trường/tài nguyên được duyệt riêng; không ép bằng swap |

Một VM Wazuh tập trung cũng cần ngân sách riêng cho server/indexer/dashboard; không thêm vào EVE chỉ vì “còn vài GiB”. M5 có thể chuẩn bị log và cấu hình agent, còn nghiệm thu dashboard/tích hợp chỉ thực hiện ở môi trường đủ tài nguyên. [Yêu cầu Wazuh theo quy mô](https://documentation.wazuh.com/current/quickstart.html).

## 3. Phân biệt trình diễn tối thiểu và nghiệm thu đầy đủ

M2 tối thiểu có giá trị: một Core thật và frame qua các TAP riêng, VLAN/trunk/mirror/persistence có capture/log và đối chứng. Không cần nhiều endpoint VM; không lấy gói đi tắt trên EVE bridge làm bằng chứng OVS.

M3 tối thiểu: một firewall thật, VLAN gateway, một luồng rule cho phép và một luồng bị chặn, NAT chỉ khi WAN lab đã chốt. M3 HA đầy đủ bắt buộc cặp chạy đồng thời, VIP tiếp quản, state sync và số đo gián đoạn; cài lần lượt hai máy không thay được điều đó.

M4 tối thiểu: PCAP mirror thật và Suricata phát hiện marker từ PCAP khi chạy sau đó; ghi offline. M4 live/tích hợp M5 cần sensor/collector thật, có alert ở cả hai đầu. Nếu chưa đủ tài nguyên, ghi phần chưa làm thay vì ghép ảnh hoặc tuyên bố đạt.

## 4. Lịch ưu tiên dự kiến

| Thời điểm | Đầu ra ưu tiên | Điều kiện / phương án nếu bị chặn |
|---|---|---|
| 01/11 trước thông báo sẵn sàng | Queue M2, mock-test, IP/policy M3, checklist M4, mẫu minh chứng, Git checkpoint | Không VM, không tải image |
| 01/11 sau thông báo sẵn sàng | M2: baseline sau boot,31/32 case frame, mirror, persistence, capture và báo cáo kết quả | Nếu RAM chưa đủ: tiếp tục phần offline, không tự tắt Labtainer |
| 02/11 | Primary: cài chính thức, mapping, gateway/rule theo nhóm VLAN | Nếu thiếu image/WAN: chốt đầu vào trước, không mở NAT host |
| 03/11 | M4: capture thật, Suricata offline hoặc live nhỏ; chuẩn bị log Wazuh | Nếu thiếu sensor: thu PCAP mirror và giữ nguyên để phân tích sau |
| 04/11 | Kiểm lại bằng chứng, thử lại lỗi; HA chỉ nếu có ngân sách mới phù hợp | Nếu không đủ cặp: báo cáo single-firewall và giới hạn HA rõ ràng |
| 05/11 | Chốt Word, bảng đạt/chưa đạt, checksum và Git; dành thời gian rà trình bày | Không thêm tính năng rủi ro sát giờ nộp |

Đây là kế hoạch, chưa phải kết quả hoặc cam kết các ca đã chạy. Khi một bước bị chặn, tiếp tục tài liệu/phân tích log có sẵn thay vì dừng cả dự án.

## 5. Mẫu kết quả và ảnh cần chụp

Mẫu chung: docs/templates/SOC-test-result-template.csv và SOC-evidence-template.csv. Trạng thái mặc định NOT_RUN; chỉ ghi PASS/FAIL khi có log/capture, thời gian và tiêu chí tương ứng. BLOCKED ghi lý do thiếu điều kiện; mock/static có scope riêng, không dùng PASS mạng.

Ảnh cần thu khi chạy thật: topology EVE hiện hành; console version/Port/Mirror/khôngIP; bảng VLAN trên trunk bằng capture; frame marker nguồn–đích–mirror; unit/boot_id sau reboot; GUI interface/VIP/rules OPNsense; state/sync/CARP timeline; cấu hình/counter/alert Suricata; event Wazuh đối chiếu SID và thời gian. Ảnh caption tiếng Việt, đánh số theo chương, dưới hình và có giải thích mục đích/nội dung/kết quả/ý nghĩa. Khi không có công cụ chụp GUI, người dùng mở đúng màn hình, chụp toàn phần kết quả và lưu docs/evidence/M2/M3/M4 tương ứng, không có credential; chưa chụp phải ghi MISSING.
