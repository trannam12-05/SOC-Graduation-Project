# 1. Kịch bản video demo SOC tại nhà

## 1.1. Mục tiêu và nguyên tắc trình bày

Thời lượng mục tiêu 13 phút. SOC (Security Operations Center — trung tâm điều hành an ninh) trong đồ án sử dụng Core Layer 2 để phân vùng và sao chép lưu lượng, Suricata để phát hiện mẫu lưu lượng, Wazuh Manager để phân tích sự kiện và sinh cảnh báo. Gateway, firewall rules và NAT thuộc OPNsense. Không trình bày Core như thiết bị định tuyến.

Video tách ba loại đầu vào: **mô phỏng** là JSON do người kiểm thử tạo; **replay từ cảnh báo thật** là sự kiện đã được Suricata sinh trong kiểm thử trước rồi nạp lại; **truyền log trực tiếp** là sự kiện mới đi tự động từ sensor đang chạy tới Manager. Chỉ loại cuối mới chứng minh đường truyền log live. Không dùng màn hình `wazuh-logtest` để thay bằng chứng logcollector tự đọc tệp và ghi `alerts.json`.

Kết quả chẩn đoán ngày 02/11: JSON mô phỏng khớp rule tùy chỉnh 100101 level 8; sự kiện Suricata đầy đủ khớp rule tích hợp 86601 level 3 trong logtest. Không đọc nhầm Suricata SID 1000001 thành Wazuh rule ID; đây là hai trường thuộc hai bộ máy phát hiện khác nhau. Khi quay phải dùng đúng rule của từng sự kiện và đối chiếu tệp alert thực tế.

Đây là kịch bản chuẩn bị. Các thao tác chưa chạy trong lần quay phải nói ở thì dự kiến; cập nhật lời thoại theo báo cáo nghiệm thu tại thời điểm quay.

## 1.2. Nhóm tài nguyên và thứ tự quay

| Phân đoạn | Node cần chạy | RAM danh nghĩa | Điều kiện |
|---|---|---:|---|
| Giới thiệu topology/bằng chứng cũ | Không cần bật node | 0 | Mở sơ đồ và ảnh/log đã lưu |
| Kiểm thử Core–Suricata riêng | SOC-Core-L2 + Suricata-NIDS | Đọc RAM từ inventory hiện hành | Không bật Manager/cặp firewall; nguồn frame hiện có được bơm vào TAP Core, không cần bật Data-Center |
| HA SYNC và bằng chứng đã có | Không cần bật nếu trình bày ảnh/log | 0 | Nếu cần kiểm thử mới, xin quyền riêng bật cặp firewall; tổng cũ 6144 MiB, không bật Core/Manager |
| Wazuh mô phỏng/replay | Chỉ Wazuh-SOC | 4096 MiB | Đã được phép bật riêng ngày 02/11; đo lại RAM trước lần quay mới |
| Truyền log trực tiếp | Chưa chốt | Chưa chốt | Wazuh chưa nối mạng; cần phê duyệt thiết kế và ngân sách trước thay đổi |

Không tự dừng node để chuyển nhóm. Khi được phép, shutdown mềm qua guest rồi xác nhận tiến trình QEMU đã hết trước khi bật nhóm kế tiếp. Không sửa RAM/đĩa lúc node đang chạy. Chưa triển khai Docker. RAM danh nghĩa không thay cho đo MemAvailable, commit Windows, swap-in/out của EVE và tải ứng dụng quay video.

## 1.3. Timeline và lời thuyết minh

| Thời gian | Màn hình/thao tác | Lời thuyết minh tiếng Việt |
|---|---|---|
| 00:00–01:15 | Topology EVE, chú thích VLAN và đường mirror | “Mô hình phân vùng VLAN 30 Data Center, 40 Employee, 50 Guest, 60 DMZ và 99 Management. Core chỉ chuyển mạch Layer 2. OPNsense đảm nhiệm gateway và chính sách giữa các vùng.” |
| 01:15–02:30 | Mở mapping M2, bảng 95 ca và ảnh console cũ | “Bộ kiểm thử M2 đã ghi nhận 95 trên 95 ca frame trong phạm vi VLAN, trunk, mirror và sau khởi động lại. Đây là kết quả lịch sử có tệp minh chứng; không đồng nghĩa gateway hoặc HA đã đạt.” |
| 02:30–04:30 | Ảnh sensor trước/sau marker, `live-mirror-frames.json`, JSON cảnh báo thật | “Frame ICMP vô hại được đưa vào TAP nối cổng access VLAN 30 của Core và quan sát tại sensor. Suricata tạo SID 1000001. Đây là kiểm thử đường Core–sensor bằng frame thật; không phải ping từ máy Data-Center hoặc kiểm thử định tuyến.” |
| 04:30–05:30 | Wazuh `systemctl show`, override timeout, trạng thái thành phần | “Manager đã từng gặp giới hạn khởi động 45 giây. Cấu hình override 300 giây cần được xác nhận từ tệp trên đĩa và giá trị systemd đang dùng. Trạng thái sau lần boot hiện tại được ghi ở màn hình này.” |
| 05:30–07:30 | Trạng thái replay trước thử, sự kiện JSON mô phỏng, alert mới | “Tôi ghi một sự kiện mô phỏng có định danh riêng vào tệp đã được logcollector theo dõi. Điều kiện đạt là xuất hiện cảnh báo Rule 100101 mới trong alerts.json, đúng nội dung và vị trí tệp; logtest chỉ là bước kiểm tra giải mã riêng.” |
| 07:30–09:30 | Hash nguồn thật, backup, append một dòng, kết quả alert mới | “Đầu vào tiếp theo lấy từ cảnh báo Suricata thật đã lưu. Hash đối chiếu giúp bảo đảm nguồn replay không bị thay bằng dữ liệu khác. Đường xử lý từ tệp replay tới Manager được kiểm tra tự động. Phân đoạn này vẫn là replay, chưa chứng minh truyền log trực tiếp.” |
| 09:30–11:00 | Ảnh SYNC, pfsync hai chiều, XMLRPC alias | “Bằng chứng SYNC cho thấy kết nối giữa hai firewall. Pfsync đã có gói giao thức 240 hai chiều, nhưng chưa đủ chứng minh phiên được giữ qua failover. XMLRPC Aliases có minh chứng riêng. CARP failover chưa nghiệm thu.” |
| 11:00–12:00 | Bảng chức năng đạt/chưa đạt | “Wazuh Manager và giao diện SOC hoàn chỉnh là hai phạm vi khác nhau. Indexer và Dashboard chưa triển khai đầy đủ. Chúng tôi chỉ kết luận trong giới hạn từng bằng chứng.” |
| 12:00–13:00 | Sơ đồ đường log dự kiến và phương án dự phòng | “Do giới hạn RAM, các khối được quay theo nhóm. Video ghép các phân đoạn có thời điểm và loại thử rõ ràng. Đường truyền log trực tiếp sẽ được nghiệm thu khi hoàn thành kết nối và kiểm thử sự kiện mới.” |

Nếu kiểm thử mô phỏng hoặc replay chưa đạt, thay câu “được kiểm tra tự động” bằng “đang kiểm tra; chưa có cảnh báo mới đáp ứng tiêu chí”. Giữ lại màn hình lỗi phù hợp, không dựng lại kết quả đạt.

## 1.4. Lệnh trình diễn chỉ đọc

Chạy trên console Wazuh sau đăng nhập, không đưa mật khẩu vào lệnh hoặc video:

```sh
systemctl is-active wazuh-manager
systemctl show wazuh-manager -p TimeoutStartUSec -p DropInPaths -p ActiveState
sudo /var/ossec/bin/wazuh-control status
sudo wc -l /var/log/soc-suricata-replay.json
```

Lệnh đầu phản ánh trạng thái systemd. Lệnh thứ hai kiểm tra timeout hiệu lực và đường dẫn override. Lệnh thứ ba phản ánh tiến trình thành phần, cần đối chiếu với log lỗi. Lệnh cuối chỉ đếm dòng; số dòng tăng không chứng minh đã có cảnh báo.

Không dùng `cat ossec.conf`, `env`, lịch sử shell hoặc cấu hình firewall đầy đủ khi quay vì có thể lộ thông tin xác thực. Chỉ mở các trường công khai đã chọn.

## 1.5. Ảnh và log sử dụng

1. Core: `docs/evidence/M2/live-tests-20261101/final-collection/frame-cases.csv` cùng báo cáo M2 đã có.
2. Suricata: `docs/evidence/M4/resume-20261102/sensor-export-after-marker-20261102T170219+0700.png`, `sensor-public-after-marker.json`, `live-mirror-frames.json`, `suricata-real-alert-replay.jsonl` trong cùng thư mục.
3. HA: `docs/evidence/M3/resume-20261102/pfsync-packets.json` và ảnh `xmlrpc-target-probe-check-20261102T163938+0700.png`, `xmlrpc-target-cleanup-verified-20261102T164809+0700.png`.
4. Wazuh mới: `docs/evidence/M5/continuation-20261102/`; chỉ sử dụng ảnh/log có thực trong danh mục minh chứng cuối.

Chú thích báo cáo dự kiến: “Hình 4.1. Cảnh báo Suricata SID 1000001 trong kiểm thử frame VLAN 30”; “Hình 5.1. Trạng thái Manager và timeout sau boot”; “Hình 5.2. Cảnh báo từ JSON mô phỏng”; “Hình 5.3. Cảnh báo Wazuh từ replay sự kiện Suricata thật”. Đánh số lại theo chương khi ghép báo cáo tổng.

Mỗi hình cần giải thích: mục đích kiểm tra; trường/kết quả xuất hiện; điều kiện đạt; và phạm vi ý nghĩa. Hình 4.1 chứng minh sensor phát hiện marker; hình 5.2/5.3 chỉ chứng minh thu thập cục bộ nếu chưa có vận chuyển log trực tiếp.

## 1.6. Phương án dự phòng

Nếu không đủ RAM để chạy Core và Suricata, dùng ảnh/log M4 cũ có nhãn “kết quả thu lúc 17:01–17:02 ngày 02/11/2026 UTC+07:00 theo đồng hồ máy thu”. Không suy giờ sự kiện guest thành giờ máy thu vì đồng hồ guest chưa được tin cậy. Chạy riêng Manager để trình diễn replay nếu đủ tài nguyên và có quyền bật.

Nếu Manager không khởi động, quay phần kiểm tra lỗi và minh chứng cũ; không tuyên bố alerts.json mới đã có. Nếu hoàn toàn không bật được VM, dùng video giải thích topology, minh chứng cũ và danh sách phần chưa nghiệm thu; tiêu đề phải ghi “trình bày bằng chứng kiểm thử đã lưu”.

Không bật thêm node chỉ để có topology trông đầy đủ. Các đoạn ghép phải có nhãn thời gian, nhóm node và loại thử, không tạo cảm giác toàn hệ thống hoạt động đồng thời.

## 1.7. Tiền kiểm trước quay và tiêu chí lưu kết quả

Kiểm tra dung lượng lưu video, khung hình và âm thanh; tắt hiển thị thông báo có thông tin riêng tư. Mở sẵn tệp công khai cần trình chiếu. Đo tài nguyên khi phần mềm quay đang chạy; nếu thiếu dự phòng thì quay bằng chứng đã lưu. Không tự cài thêm phần mềm quay.

Sau mỗi đoạn, lưu ảnh đầy đủ khung console và log JSON, ghi tên tệp, nội dung, thời điểm kèm múi giờ, đường dẫn và chương dự kiến vào danh mục. Khi công cụ không chụp được GUI topology: mở lab `SOC-M2-Core-L2`, hiển thị đủ tên node/VLAN/link, chụp toàn cửa sổ bằng công cụ Windows hiện có và lưu `docs/evidence/M5/continuation-20261102/topology-manual-<thoi-diem>.png`. Đây là ảnh cần chụp thủ công, chưa phải minh chứng đã có.

## 1.8. Nguồn tham khảo chính thức

Wazuh mô tả thu thập `eve.json` bằng cấu hình localfile JSON trong [Network IDS integration](https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html). Cơ chế đọc tệp tham chiếu [localfile](https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/localfile.html); nơi ghi cảnh báo tham chiếu [Data analysis](https://documentation.wazuh.com/current/user-manual/ruleset/). Tài liệu trực tuyến được tra cứu ngày 02/11/2026; kết quả cài đặt 4.14.9 cần dựa vào kiểm tra guest thực tế.
