# Đồ án SOC trên EVE-NG

## Mục tiêu

Xây dựng và mô phỏng một kiến trúc Security Operations Center (SOC) trong EVE-NG, sử dụng Ubuntu/Open vSwitch cho Core Layer 2, OPNsense HA theo thiết kế và các thành phần giám sát/an ninh mạng. Tài liệu và cấu hình được tổ chức theo từng giai đoạn để có thể kiểm chứng thiết kế trước khi triển khai.

## Trạng thái hiện hành

M2 đã cài OVS 3.3.9 và cấu hình bridge cô lập với năm access, hai trunk; ens10 chưa mirror. Chưa nối peer/link và chưa nghiệm thu chuyển mạch bằng lưu lượng thực tế. Đọc [docs/PROGRESS.md](docs/PROGRESS.md) để tiếp quản và [docs/GITHUB_BACKUP.md](docs/GITHUB_BACKUP.md) để hiểu phạm vi lưu GitHub; không chạy lại cấu hình đã hoàn thành.

Checkpoint 01/11/2026: Core đang tắt, chỉ làm tài liệu/script trong khi người dùng học Labtainer. Chỉ bật VM sau thông báo tài nguyên sẵn sàng. Xem [báo cáo M2 hợp nhất](docs/M2/M2-report-consolidated-review-20261101.docx), [kịch bản thử và rollback chưa chạy](docs/M2/M2-test-and-rollback-PREPARED-20261101.md) và [thiết kế OPNsense HA dự kiến](docs/M3/M3-OPNsense-HA-PROPOSED-20261101.md).

## Nhiệm vụ của Nam

Nam phụ trách phối hợp xây dựng và hoàn thiện đồ án: rà soát yêu cầu, chuẩn bị sơ đồ và kế hoạch địa chỉ mạng, ghi lại quyết định thiết kế, triển khai các thành phần theo kế hoạch được thống nhất, kiểm thử kết nối và chức năng an ninh, đồng thời cập nhật tài liệu tiếng Việt để nhóm có thể tái hiện và đánh giá kết quả.

## Cấu trúc dự án

- `docs/M1`, `docs/M2`: tài liệu theo các giai đoạn của đồ án.
- `network`: thiết kế Core Layer 2 và kế hoạch địa chỉ IP.
- `opnsense`: tài liệu HA và firewall.
- `eve-ng`, `suricata`, `wazuh`, `automation`, `tests`: khu vực dành cho mô hình, giám sát, tự động hóa và kiểm thử.

Thiết kế M1 là cơ sở đề xuất. Các thông số cần được xác nhận trên mô hình EVE-NG trước khi xem là cấu hình chính thức.
