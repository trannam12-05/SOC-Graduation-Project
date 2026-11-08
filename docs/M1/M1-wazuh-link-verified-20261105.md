# CHƯƠNG 1. BỔ SUNG TRIỂN KHAI KẾT NỐI WAZUH TRONG LAB NỘI BỘ

## 1.1. Phạm vi được phê duyệt

Ngày 05/11/2026, người dùng cho phép kiểm kê chỉ đọc EVE-NG, sao lưu topology và nối Wazuh e0 vào segment Management hiện hữu. Không bật/tắt node, không đặt IP, không cài phần mềm, không sửa seed/image hoặc WAN. Đây là phụ lục bổ sung bản thiết kế M1 hợp nhất cùng ngày; các bản Word trước giữ nguyên.

## 1.2. Hiện trạng và thay đổi

Kiểm kê thu lúc 09:15:03 UTC+07:00 xác nhận lab SOC-M2-Core-L2 có 10 node, 11 segment; không có tiến trình QEMU. Wazuh-SOC ID10 có một NIC khai báo nhưng chưa có interface gắn mạng. Segment VLAN99-Management ID10 là bridge nội bộ, đã nối Core e4, Management e0 và Suricata e1.

Đã dùng hàm connectNode của EVE-NG để nối Wazuh-SOC ID10, interface0/e0 vào network10. Kết quả thu lúc 09:15:50 UTC+07:00, mã trả về 0. Không thêm node hoặc segment. Kiểm tra ngữ nghĩa XML trước/sau xác nhận chỉ có một interface mới; mọi thuộc tính node, network, liên kết khác và nội dung cấu trúc giữ nguyên. Không có tiến trình QEMU/VPCS sau thao tác.

| Đầu nối | Segment | Kết quả |
|---|---|---|
| Core e4 / ens7 | VLAN99-Management, ID10 | Giữ nguyên |
| Management interface0 | VLAN99-Management, ID10 | Giữ nguyên |
| Suricata e1 | VLAN99-Management, ID10 | Giữ nguyên |
| Wazuh e0 | VLAN99-Management, ID10 | Đã bổ sung vào XML lab |

Việc nối cùng segment cho phép thiết kế đường quản trị và đường log tách khỏi capture. Nó không chứng minh guest có IP, agent đã đăng ký, kết nối TCP thông hay log được vận chuyển. Core vẫn giữ vai trò Layer 2 theo kiến trúc; đợt này không boot Core để đọc lại runtime OVS.

## 1.3. Sao lưu và tính toàn vẹn

Thư mục sao lưu trên EVE: /root/soc-m1-wazuh-link-20261105T091550Z, quyền0700; hai tệp lab-before.unl và lab-after.unl quyền0600. Không tải raw XML về máy Windows; metadata công khai lưu trong danh mục minh chứng.

| Đối tượng | SHA-256 |
|---|---|
| Lab trước thay đổi | 3a228544ae38c43703b495c6f4022a83112578936cd1d90f5b72c895a9fd53b2 |
| Lab sau thay đổi | 94e4c6380f776ca9b154c5c068a3b2ee20f1f90c03005e9790e94543300e7a6f |

Nếu cần phục hồi, trước hết đối chiếu hash hiện tại và bảo đảm không có chỉnh sửa mới; bản backup trước thay đổi là nguồn phục hồi. Không tự chép đè backup khi trạng thái đã khác hoặc có node chạy. Đợt này không thực hiện rollback, không kết luận đã thử khôi phục.

## 1.4. Kết quả nghiệm thu M1

| Hạng mục | Trạng thái | Minh chứng |
|---|---|---|
| Thiết kế lab nội bộ, VLAN/subnet/VIP và mapping | Hoàn thiện hồ sơ | Bản M1 hợp nhất ngày 05/11 và nghiệm thu M2–M3 được dẫn trong đó |
| Wazuh e0 nối VLAN99 | Đạt cấu trúc XML | connection-result.json; independent-verification.json |
| Số lượng 10 node, 11 segment và liên kết khác | Giữ nguyên | So sánh ngữ nghĩa trước/sau và đọc lại độc lập |
| Node không bị bật/tắt, guest không cấu hình lại | Đạt phạm vi thao tác | Không phát lệnh vòng đời; kiểm kê không có QEMU/VPCS |
| Ảnh topology thật sau thay đổi | Chưa thu | Không có cửa sổ trình duyệt EVE để chụp bằng công cụ hiện có |
| IP Wazuh và đường log live | Chưa kiểm chứng | Ngoài phạm vi được giao; không boot node |

Phần thiết kế và kết nối topology cơ sở đã được hoàn thiện ở mức hồ sơ và cấu trúc XML. Chưa đóng toàn bộ đầu việc M1 “topology EVE-NG hoàn chỉnh” do chưa có ảnh GUI sau thay đổi. Kết nối Internet là mở rộng theo lựa chọn người dùng, không còn là điều kiện bắt buộc của lab nội bộ.

## 1.5. Hướng dẫn ảnh và nội dung báo cáo

Mở EVE-NG tại 192.168.220.143, lab SOC-M2-Core-L2, tải lại trang và xem toàn topology; không cần bật node. Cần thấy đủ 10 node, hai WAN cô lập, hai trunk, đường SYNC, năm vùng VLAN, capture riêng và Wazuh nối segment Management. Sau đó mở chi tiết kết nối Wazuh e0 để thấy VLAN99-Management/network10. Chụp hai ảnh rõ chữ, không có thông tin đăng nhập; lưu tại docs/evidence/M1/wazuh-link-20261105/ với tên topology-overview-YYYYMMDDTHHMMSS+0700.png và wazuh-link-YYYYMMDDTHHMMSS+0700.png. Ghi thời điểm thực tế kèm múi giờ vào danh mục; chưa có ảnh thì không ghi là đã thu.

Chú thích dự kiến Hình 1.2: “Topology SOC trong lab nội bộ sau khi bổ sung kết nối Wazuh”. Mục đích: đối chiếu bản thiết kế với GUI thực tế. Nội dung cần thấy: các vùng mạng và Wazuh cùng segment Management. Kết quả chỉ điền sau khi xem ảnh. Ý nghĩa: xác nhận kết nối được hiển thị, không thay cho kiểm thử guest hoặc pipeline.

Chú thích dự kiến Hình 1.3: “Interface e0 của Wazuh-SOC thuộc segment VLAN99-Management”. Mục đích: kiểm tra đúng đầu nối. Nội dung cần thấy: tên node/interface/segment. Kết quả và thời điểm chỉ điền sau khi chụp. Ý nghĩa: minh chứng kết nối quản trị tách khỏi đường SPAN.
