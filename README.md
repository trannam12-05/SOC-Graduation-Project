# M2 đã hoàn thành — 03/11/2026, UTC+07:00

Core L2, Inter-VLAN HTTP200 qua Primary, firewall ca dương/hai ca âm, access/trunk và SPAN đều PASS; LACP N/A theo kiến trúc hai trunk tới hai firewall riêng. [Tổng kết M2](docs/M2/M2-final-summary-20261103.md), [Word](docs/M2/M2-final-summary-20261103.docx), [SOC TO DO](docs/SOC_TO_DO.md), [evidence index](docs/evidence/M2/final-acceptance-20261103/evidence-index.csv). Core/Primary giữ chạy, DC tắt mềm, client/NIC tạm đã gỡ và lab phục hồi nguyên byte. Không chuyển M3. Các mốc cũ bên dưới giữ làm lịch sử.

# Đồ án SOC trên EVE-NG

## Cập nhật mới nhất — 02/11/2026

M2 Nhóm 2A: Primary đã có đủ năm VLAN đúng parent vtnet0/tag/IP .2/24, enabled/UP; đã backup root-only và kiểm hash cấu hình trước/sau, không cần sửa. Core giữ Layer 2. Hiện Core + Primary chạy; Wazuh đã shutdown mềm theo quyền riêng để nhường RAM. Chưa thử lưu lượng hoặc cấu hình rules trong nhóm này; đang dừng chờ xác nhận. Xem [báo cáo Nhóm 2A](docs/M2/M2-group2a-primary-vlans-20261102.md).

Mốc M5 trước đó: đã kiểm tra Wazuh-SOC theo phê duyệt. Manager 4.14.9-1 hoạt động sau khi khôi phục override timeout 300 giây vào `/etc`; chưa thử reboot sau sửa. Thu thập tự động đã sinh alert từ JSON mô phỏng (rule 100101 level 8) và replay cảnh báo Suricata thật VLAN 30 (rule 86601 level 3). **Chưa nghiệm thu toàn chuỗi live**; Wazuh chưa nối segment, Indexer/Dashboard/Filebeat chưa cài trên node này.

Xem [báo cáo kiểm chứng M5](docs/M5-verification-and-demo-20261102.md), [kịch bản quay video 13 phút](docs/SOC-video-demo-20261102.md), [đề xuất đường log live chưa triển khai](docs/M5-live-pipeline-proposal-20261102.md) và [danh mục minh chứng mới](docs/evidence/M5/continuation-20261102/evidence-index-final.md). Các mốc ngày 01/11 và mô tả chuẩn bị bên dưới được giữ làm lịch sử.

## Mục tiêu

Xây dựng và mô phỏng một kiến trúc Security Operations Center (SOC) trong EVE-NG, sử dụng Ubuntu/Open vSwitch cho Core Layer 2, OPNsense HA theo thiết kế và các thành phần giám sát/an ninh mạng. Tài liệu và cấu hình được tổ chức theo từng giai đoạn để có thể kiểm chứng thiết kế trước khi triển khai.

## Trạng thái hiện hành

Ngày 01/11/2026: **M2 đạt 95/95 ca frame thật**, mirror ens10 và persistence sau reboot đã kiểm chứng; Core đang chạy, không IP/gateway và forwarding 0/0. Xem [báo cáo kết quả mới](docs/M2/M2-report-functional-tests-verified-20261101.docx), [bảng ca thực tế](docs/evidence/M2/live-tests-20261101/final-collection/frame-cases.csv) và [PROGRESS](docs/PROGRESS.md). Chưa triển khai gateway/HA/Suricata; các đoạn checkpoint chuẩn bị dưới đây giữ làm lịch sử.

M2 đã cài OVS 3.3.9 và cấu hình bridge cô lập với năm access, hai trunk; ens10 chưa mirror. Chưa nối peer/link và chưa nghiệm thu chuyển mạch bằng lưu lượng thực tế. Đọc [docs/PROGRESS.md](docs/PROGRESS.md) để tiếp quản và [docs/GITHUB_BACKUP.md](docs/GITHUB_BACKUP.md) để hiểu phạm vi lưu GitHub; không chạy lại cấu hình đã hoàn thành.

Checkpoint 01/11/2026: Core đang tắt, chỉ làm tài liệu/script trong khi người dùng học Labtainer. Chỉ bật VM sau thông báo tài nguyên sẵn sàng. Xem [báo cáo M2 hợp nhất](docs/M2/M2-report-consolidated-review-20261101.docx), [kịch bản thử và rollback chưa chạy](docs/M2/M2-test-and-rollback-PREPARED-20261101.md) và [thiết kế OPNsense HA dự kiến](docs/M3/M3-OPNsense-HA-PROPOSED-20261101.md).

Để triển khai tiếp theo nhóm: [runbook bộ điều phối M2](docs/M2/M2-sequential-runbook-PREPARED-20261101.md), [M3 địa chỉ và checklist](docs/M3/M3-deployment-matrix-and-tests-PREPARED-20261101.md), [M4 sensor/mirror/log](docs/M4/M4-Suricata-mirror-PREPARED-20261101.md), [kế hoạch đến05/11](docs/SOC-execution-resource-plan-20261101.md). Script mặc định không thực thi; không có tự khởi động lúc10 giờ.

## Nhiệm vụ của Nam

Nam phụ trách phối hợp xây dựng và hoàn thiện đồ án: rà soát yêu cầu, chuẩn bị sơ đồ và kế hoạch địa chỉ mạng, ghi lại quyết định thiết kế, triển khai các thành phần theo kế hoạch được thống nhất, kiểm thử kết nối và chức năng an ninh, đồng thời cập nhật tài liệu tiếng Việt để nhóm có thể tái hiện và đánh giá kết quả.

## Cấu trúc dự án

- `docs/M1`, `docs/M2`: tài liệu theo các giai đoạn của đồ án.
- `network`: thiết kế Core Layer 2 và kế hoạch địa chỉ IP.
- `opnsense`: tài liệu HA và firewall.
- `eve-ng`, `suricata`, `wazuh`, `automation`, `tests`: khu vực dành cho mô hình, giám sát, tự động hóa và kiểm thử.

Thiết kế M1 là cơ sở đề xuất. Các thông số cần được xác nhận trên mô hình EVE-NG trước khi xem là cấu hình chính thức.

## Hồ sơ tổng hợp M1–M4 — 08/11/2026

- [Báo cáo cá nhân Word M1–M4](docs/SOC_M1-M4_BaoCaoCaNhan.docx): 76 trang, 6 chương, 23 vị trí hình và 17 bảng.
- [PowerPoint hiện tại](Thuyết%20trình%20nhóm%201.pptx): cập nhật topology/VLAN/HA/Suricata và ảnh minh chứng thật, ảnh terminal nền sáng.
- [Tiến độ và phạm vi nghiệm thu](docs/SOC_TO_DO.md): M1–M3 PASS theo hạng mục; M4 còn PARTIAL/BLOCKED, chưa nghiệm thu truyền log live/Syslog.
- [Phạm vi xuất bản an toàn](docs/publication-audit-20261108.md): loại trừ dữ liệu xác thực, VM và minh chứng thô chưa rà soát; các bản gốc giữ tại workspace.