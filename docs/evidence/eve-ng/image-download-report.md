# Báo cáo tải image Ubuntu cho M2

- **Thời gian kiểm tra/tải:** 2026-10-31 13:43:26 +07:00 (Asia/Saigon)
- **Mục đích:** chuẩn bị một Linux guest hợp pháp cho phương án Core Layer 2 dùng Open vSwitch trong M2.
- **Phạm vi:** chỉ tải và xác minh image trong staging. Chưa cài vào EVE-NG, chưa tạo lab/node, chưa thay đổi VMware hay EVE-NG.

## Nguồn và lựa chọn

Trang Linux image chính thức của EVE-NG có liên kết tới gói Linux dựng sẵn được tải qua Mega và hướng dẫn đưa image vào EVE. Ngay trên trang hướng dẫn không thấy danh sách phiên bản hoặc checksum cho từng image; ví dụ cài đặt tại đó dùng Ubuntu Desktop 16.04. Trang Supported Images nêu Ubuntu Desktop 16.04, 18.x, 20.x, không xác nhận Ubuntu Server 24.04. Do chưa xác minh được phiên bản, checksum và điều kiện phân phối của image cụ thể trong gói, chọn cloud image chính thức Canonical theo phương án dự phòng người dùng cho phép.

- **Image:** Ubuntu Server 24.04 LTS (Noble Numbat), amd64, cloud image.
- **Nguồn tải chính thức:** <https://cloud-images.ubuntu.com/releases/noble/release/ubuntu-24.04-server-cloudimg-amd64.img>
- **Trang thư mục / thông tin image:** <https://cloud-images.ubuntu.com/releases/noble/release/>
- **SHA-256 manifest:** <https://cloud-images.ubuntu.com/releases/noble/release/SHA256SUMS>
- **Ngày build đang được trang release công bố:** 2026-10-17.
- **Kích thước:** 621,284,352 bytes (592.5 MiB; trang Canonical hiển thị khoảng 593 MiB).
- **Định dạng:** trang Canonical mô tả đây là đĩa QCow2 bootable UEFI/GPT; 8 byte đầu file tải được là `51 46 49 FB 00 00 00 03` (magic QCOW2 `QFI\xFB`).
- **SHA-256 theo manifest Canonical:** `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`.
- **SHA-256 tính trên file tải:** `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94` — **khớp**.
- **Xác minh chữ ký manifest:** chưa thực hiện. Máy Windows không có `gpg.exe`; checksum được đối chiếu với SHA256SUMS tải qua HTTPS từ cùng tên miền Canonical.

## File đã tải

Thư mục staging mới, không ghi đè file có sẵn:

- `D:\SOC\staging\ubuntu-24.04-amd64-20261031\ubuntu-24.04-server-cloudimg-amd64.img`
- `D:\SOC\staging\ubuntu-24.04-amd64-20261031\SHA256SUMS`

## Tương thích với EVE-NG và giới hạn xác minh

- EVE-NG quy định image QEMU Linux dùng thư mục có tiền tố `linux-` và tên ổ đĩa như `virtioa.qcow2`. Khi được phê duyệt cài đặt, image này sẽ cần được đưa vào đúng cấu trúc/tên của EVE; chưa thực hiện thao tác đó.
- Ubuntu cloud image được Canonical công bố cho nền tảng KVM/QEMU và là QCOW2, nên phù hợp về định dạng với QEMU của EVE-NG. EVE-NG ghi nhận tiền tố `linux-` dành cho Linux nói chung.
- **Chưa xác minh boot trên EVE-NG 6.2.0-4.** Trang Canonical mô tả ảnh là UEFI/GPT; cấu hình BIOS/UEFI của node EVE cần được kiểm tra trong bước triển khai và phải thử boot trước khi coi là tương thích đã kiểm chứng.
- **Đăng nhập cần cloud-init seed ở lần khởi động đầu.** Theo tài liệu Ubuntu, user mặc định thường là `ubuntu`, cloud-init tạo user ban đầu; SSH password authentication mặc định tắt. Cần cung cấp `user-data`/`meta-data` (NoCloud seed) phù hợp, ưu tiên public key SSH. Chưa có user/password nào được đặt trong image này.
- `qemu-img` không có sẵn trên Windows nên chưa đọc được virtual capacity/metadata bằng công cụ QEMU. Kích thước trên báo cáo là kích thước file truyền tải, không phải dung lượng đĩa ảo sau khi guest chạy.
- Tải image không chứng minh đã cài hoặc thử được Open vSwitch. Cần ít nhất 2 NIC guest được EVE nối tới các cổng lab để kiểm thử bridge/switching; số NIC cụ thể sẽ chốt trong topology M2.

## Đề xuất đăng nhập và cài Open vSwitch (chỉ hướng dẫn, chưa chạy)

1. Ở bước chuẩn bị node, tạo cloud-init NoCloud seed với user quản trị riêng hoặc user mặc định `ubuntu`, kèm **public SSH key** của người quản trị. Không ghi mật khẩu plaintext vào seed; giữ tắt đăng nhập SSH bằng mật khẩu. Xác nhận user có quyền `sudo`.
2. Gắn seed vào node trước lần boot đầu; kiểm tra đăng nhập bằng SSH key hoặc console và kiểm tra `cloud-init status --wait`. Việc tạo/gắn seed và boot node cần phê duyệt/triển khai riêng.
3. Sau khi guest có mạng và truy cập được kho Ubuntu, cài OVS bên trong guest bằng:

   ```sh
   sudo apt update
   sudo apt install openvswitch-switch
   sudo systemctl enable --now openvswitch-switch
   sudo ovs-vsctl show
   ```

4. Tiếp đó mới cấu hình OVS bridge, gắn các NIC lab vào bridge, rồi xác nhận VLAN/trunk/LACP/SPAN theo yêu cầu M2. Các lệnh trên là kế hoạch cho guest trong lab, không phải lệnh đã chạy.

## Trạng thái

Image đã tải và SHA-256 khớp manifest Canonical. File chỉ nằm trong staging của dự án. **Chưa cài image lên EVE-NG, chưa tạo node/lab, chưa boot VM, chưa cài OVS và chưa sửa bất kỳ cấu hình EVE-NG/VMware nào.** Chờ người dùng phê duyệt riêng bước cài đặt/chuẩn bị node.

## Nguồn tham khảo chính thức

- EVE-NG, [Linux images](https://www.eve-ng.net/index.php/documentation/howtos/howto-create-own-linux-host-image/)
- EVE-NG, [Supported Images](https://www.eve-ng.net/index.php/documentation/supported-images/)
- EVE-NG, [QEMU image namings](https://www.eve-ng.net/index.php/documentation/qemu-image-namings/)
- Canonical, [Ubuntu 24.04 LTS cloud image release](https://cloud-images.ubuntu.com/releases/noble/release/)
- Canonical, [SHA256SUMS](https://cloud-images.ubuntu.com/releases/noble/release/SHA256SUMS)
- Ubuntu documentation, [Configure preinstalled images and SSH authentication](https://ubuntu.com/hardware/docs/boards/how-to/special_hardware/headless-usage/)
## Kiểm tra trước cài đặt EVE-NG (2026-10-31 13:57:24 +07:00)

- File staging tồn tại (621,284,352 bytes); SHA-256 tính lại khớp giá trị Canonical đã ghi ở trên.
- Windows OpenSSH `ssh.exe` và `scp.exe` có sẵn; private-key path tồn tại. Không đọc nội dung private key.
- Dịch vụ `ssh-agent` trên Windows đang dừng. Thử `ssh` bằng key với `BatchMode=yes` thất bại: `Permission denied (publickey,password)`. Không thử mật khẩu.
- Vì chưa xác thực SSH được, chưa kiểm tra dung lượng đĩa, template/quy ước trên host, sự tồn tại của thư mục image đích, và chưa tạo thư mục/chuyển image.
- **Trạng thái cài:** đang chờ người quản trị nạp key bằng Windows OpenSSH Agent. Không có thay đổi nào trên EVE-NG.
### Cập nhật xác thực Windows (2026-10-31 14:10:47 +07:00)

- Người dùng cho phép chạy `Start-Service ssh-agent` dưới quyền Administrator. Lệnh đã được gọi nâng quyền nhưng tiến trình thoát mã 1; kiểm tra lại cho thấy dịch vụ vẫn `Stopped`, `StartType: Disabled`.
- Theo điều kiện người dùng, không thay đổi Startup Type. Vì vậy chưa thể nạp khóa bằng `ssh-add`; chưa thử SSH lại, chưa kiểm tra host EVE và chưa chuyển image.
- Fingerprint public key đã xác nhận ở bước trước: `SHA256:NmKKtOy8jUJd/x2Zg9xzrdGLCRAHCFfdNejRnrJ+ne4`.
### Cập nhật Windows OpenSSH Agent (2026-10-31 14:12:46 +07:00)

- Theo chấp thuận của người dùng, chỉ dịch vụ `ssh-agent` được đổi Startup Type từ Disabled sang Manual và khởi động bằng quyền Administrator.
- Xác nhận sau thao tác: `ssh-agent` = `Running`, Startup Type = `Manual`.
- Đã mở cửa sổ PowerShell tương tác để chạy `ssh-add` với private key trong `%USERPROFILE%\.ssh\eve-ng-root-ed25519`. Chưa xác nhận người dùng nhập passphrase hoặc key được nạp; không có passphrase trong báo cáo/log.
- Chưa kiểm tra lại SSH hoặc thao tác trên EVE-NG.
### Kết quả kiểm tra/cài đặt qua SSH (2026-10-31 14:14:41 +07:00)

- `ssh-agent`: Running, Startup Type Manual; không thay đổi dịch vụ Windows nào khác.
- `ssh-add -l`: fingerprint khớp `SHA256:NmKKtOy8jUJd/x2Zg9xzrdGLCRAHCFfdNejRnrJ+ne4`.
- SSH tới `root@192.168.220.143` thành công với public-key only, `StrictHostKeyChecking=yes`; không dùng mật khẩu và không bỏ qua xác minh host key.
- Host xác nhận EVE-NG `6.2.0-4`; `/opt/unetlab/addons/qemu` còn 44,127,700 KiB khả dụng theo `df -Pk`.
- Template `/opt/unetlab/html/templates/intel/linux.yml` và `amd/linux.yml` dùng Linux QEMU x86_64, NIC `virtio-net-pci`, tên ổ phù hợp `virtioa.qcow2`; khai báo mặc định 1 Ethernet, RAM 4096 MiB. Cấu hình `-machine type=pc,accel=kvm`; chưa chứng minh cloud image UEFI/GPT khởi động được với cấu hình mặc định.
- Sau khi xác nhận đích vắng mặt, đã tạo riêng `/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs` (root:root, 0755). Lệnh xác nhận bằng `stat` lỗi do quoting định dạng qua SSH sau khi `mkdir` thành công. Kiểm tra chỉ đọc sau đó xác nhận thư mục tồn tại và `virtioa.qcow2` chưa có.
- Theo yêu cầu dừng khi có lỗi, SCP **chưa chạy**. Image chưa có trên EVE-NG và chưa được EVE nhận diện. Không chỉnh quyền image, không dùng fixpermissions, không tạo lab/node, không khởi động node, không cài OVS.
- Image staging vẫn ở `D:\SOC\staging\ubuntu-24.04-amd64-20261031\ubuntu-24.04-server-cloudimg-amd64.img`; SHA-256 đã kiểm tra khớp trước lần SSH.
## Cập nhật hoàn tất cài image vào EVE-NG (2026-10-31 14:18:21 +07:00)

- Đích: `/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs/virtioa.qcow2`.
- SCP qua SSH public key hoàn tất; trước khi chuyển đã xác nhận `virtioa.qcow2` chưa tồn tại. Host key verification bật, không dùng mật khẩu.
- SHA-256 staging Windows trước SCP và SHA-256 tính trên EVE-NG sau SCP đều là `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`.
- Kích thước sau chuyển: 621,284,352 byte. File `root:root`, mode `644`; thư mục `root:root`, mode `755`. Quyền phù hợp, không cần điều chỉnh quyền và không chạy `fixpermissions`.
- **Nhận diện theo filesystem/template: đạt.** Thư mục có tiền tố `linux-`, image tên `virtioa.qcow2`, và template `/opt/unetlab/html/templates/intel/linux.yml` tồn tại. Đây là cấu trúc EVE Linux QEMU đã xác minh. Không mở/tạo lab để kiểm tra dropdown giao diện, nên hiển thị GUI chưa được quan sát trực tiếp.
- **Boot/tính năng chưa kiểm chứng:** không tạo lab hoặc bật node theo phạm vi. Template mặc định dùng `-machine type=pc,accel=kvm`, x86_64, `virtio-net-pci`, RAM 4096 MiB, 1 Ethernet. Image Canonical được mô tả UEFI/GPT; cần bước kiểm thử có phê duyệt để xác nhận boot. Template hiện tại cũng mặc định chỉ một NIC, chưa đủ cơ sở kết luận cấu hình OVS nhiều cổng.
- Một lệnh đọc hậu kiểm ban đầu gặp lỗi quoting ở `cut`/`grep`; đã thay bằng lệnh đọc đơn giản và xác minh thành công trong giới hạn retry được cho phép. Không có thao tác sửa dữ liệu do lỗi đó.
- Không tạo lab, không khởi động node, không cài Open vSwitch, không thay đổi mạng hoặc image khác.