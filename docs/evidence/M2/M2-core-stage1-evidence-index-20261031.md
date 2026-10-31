# Danh mục minh chứng M2 — Chuẩn bị Core giai đoạn đầu

## 1. Ảnh thật đã thu

| Tên ảnh | Nội dung | Thời điểm UTC+07:00 | Đường dẫn | Vị trí báo cáo |
|---|---|---|---|---|
| [M2-core-seed-ready-real-terminal-20261031.png](M2-core-seed-ready-real-terminal-20261031.png) | Terminal thật hoàn tất seed, Core tắt; không phải guest login | 2026-10-31T19:55:46.8688519+07:00 | `docs/evidence/M2/M2-core-seed-ready-real-terminal-20261031.png` | Hình 2.3, mục 2.10 |
| [M2-core-stopped-eight-nics-real-terminal-20261031.png](M2-core-stopped-eight-nics-real-terminal-20261031.png) | Terminal kiểm tra chỉ đọc: status0, 8 NIC/MAC không link, disk8GiB, bundle và seed | 2026-10-31T19:57:58.1764632+07:00 | `docs/evidence/M2/M2-core-stopped-eight-nics-real-terminal-20261031.png` | Hình 2.4, mục 2.12 |

Ảnh nguyên cửa sổ Windows Terminal/PowerShell bằng Win32 PrintWindow; đã xem để kiểm tra nội dung. Không chỉnh sửa/ghép/cắt kết quả, không chứa password/hash/private key/token. Đây là ảnh terminal thật, không phải GUI EVE hoặc console guest Core đang chạy. CSV cùng tên chứa SHA-256 của ảnh.

## 2. Log và cấu hình đã lưu

- [Snapshot trước thao tác](M2-core-stage1-baseline-20261031.json).
- [Snapshot kiểm tra cuối](M2-core-stage1-final-status-20261031.json): status/process/runtime, interface/MAC, hash 9 file cũ và bộ nhớ.
- [Log thực hiện](M2-core-stage1-execution-20261031.log).
- [Cấu hình image/node](M2-core-stage1-image-node-config-20261031.json), [lab XML](M2-core-stage1-lab-20261031.unl).
- [Seed status không chứa hash mật khẩu](M2-core-stage1-seed-status-20261031.json), [cấu hình đã che bí mật](M2-core-stage1-seed-redacted-20261031.json), [network-config](M2-core-stage1-network-config-20261031.yaml), [meta-data](M2-core-stage1-meta-data-20261031.yaml).
- [Manifest package](M2-core-stage1-package-manifest-20261031.json), [bảng package CSV](M2-core-stage1-packages-20261031.csv), [metadata manifest](M2-core-stage1-metadata-manifest-20261031.json).
- [Xác minh byte/closure](M2-core-stage1-bundle-validation-20261031.json), [log APT Noble](M2-core-stage1-apt-update-noble-20261031.log), [log APT download-only/no-download](M2-core-stage1-apt-offline-check-20261031.log).
- [RAM Windows cuối](M2-core-stage1-windows-memory-20261031.json); EVE free -m ở 20:00 được chép trong log thực hiện.
- `M2-core-stage1-SHA256SUMS-20261031.txt`: manifest riêng của bộ cập nhật; không cập nhật manifest cũ.

## 3. Báo cáo cập nhật và giới hạn

- [Báo cáo Markdown v2](../../M2/M2-report-stage1-core-preparation-20261031.md).
- [Báo cáo Word v2](../../M2/M2-report-stage1-core-preparation-20261031.docx).
- Core chưa boot, chưa cài OVS; số NIC là cấu hình EVE, chưa là kết quả nhận NIC trong guest. Không có ảnh VLAN/trunk/mirror/runtime vì chưa triển khai.
- Chưa có ảnh topology/settings EVE trực tiếp. Người dùng có thể mở lab SOC-M2-Core-L2, chụp topology và settings Ethernet=8 bằng Snipping Tool, giữ nguyên PNG, đặt tên M2-core-topology-stopped-<time>.png và M2-core-settings-eight-nics-<time>.png; bổ sung danh mục sau khi nhận ảnh. Không dùng ảnh giả.
- Bộ ảnh/log cũ trong docs/evidence/eve-ng và các manifest M2 trước được giữ nguyên.
