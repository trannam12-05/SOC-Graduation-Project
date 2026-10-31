# Tiền kiểm tra lab xác minh Ubuntu Cloud Image

- **Thời gian:** 2026-10-31 14:24:42 +07:00 (Asia/Saigon)
- **Mục tiêu:** lab riêng `SOC-Ubuntu-Image-Test`, một node Linux QEMU Ubuntu 24.04, 1 vCPU, 2048 MiB RAM; giữ node tắt để chờ phê duyệt bước boot.
- **Trạng thái hiện tại:** tiền kiểm tra chỉ đọc đã hoàn tất; chưa tạo lab/node, chưa tạo cloud-init seed và chưa bật node.

## EVE-NG và quản lý lab

- Máy EVE xác nhận phiên bản Community `6.2.0-4`.
- Tài liệu EVE-NG chính thức cung cấp API được Web UI sử dụng để tạo lab (`POST /api/labs`) và node (`POST .../nodes`). API cần đăng nhập phiên.
- Hướng dẫn API cảnh báo mỗi tài khoản chỉ có một vị trí đăng nhập; phiên đăng nhập thứ hai có thể vô hiệu hóa phiên trước. Tôi chưa gọi API login để tránh ngắt phiên Web UI admin đang hoạt động nếu có.
- Đã kiểm tra chỉ đọc: chưa có `/opt/unetlab/labs/SOC-Ubuntu-Image-Test.unl`; chưa thấy lab hiện có tham chiếu image này.

## Firmware và khả năng boot

- Template `/opt/unetlab/html/templates/intel/linux.yml`: QEMU x86_64, `qemu_version: 2.12.0`, `qemu_nic: virtio-net-pci`, `qemu_options: -machine type=pc,accel=kvm ...`; không khai báo OVMF/pflash. Đây là template hiện có và tôi không thay đổi.
- Host có firmware files `/usr/share/OVMF/OVMF_CODE.fd` và `OVMF_VARS.fd`, nhưng template Linux không dùng chúng. EVE-NG hướng dẫn EFI riêng cho một số appliance bằng cách thêm OVMF files/cấu hình tương ứng; không áp dụng cấu hình đó vào template dùng chung.
- Canonical image manifest liệt kê `grub-pc` cùng `grub-efi-amd64`; tài liệu Ubuntu về cloud images có ví dụ SeaBIOS và UEFI. Điều này là cơ sở cho một phép thử BIOS mặc định mà không sửa firmware toàn hệ thống, nhưng không chứng minh image cụ thể đã boot trong EVE 6.2.0-4.
- Node dự kiến giữ firmware theo Linux template hiện tại (SeaBIOS/default QEMU). Không chèn OVMF hay sửa `qemu_options` dùng chung. Boot chưa được thử.

## Cloud-init / đăng nhập dự kiến

- Ubuntu cloud image có `cloud-init`; tài liệu Canonical yêu cầu datasource/seed cục bộ khi chạy cloud image ngoài cloud. `genisoimage` đã có trên host.
- Kế hoạch: NoCloud seed gồm `meta-data` với instance-id riêng và `user-data` tạo tài khoản `soc-test`, chèn **public key** SSH đã có, khóa mật khẩu cho user (`lock_passwd: true`) và giữ `ssh_pwauth: false`. Không đặt password plaintext.
- Seed sẽ là `cdrom.iso` riêng bên cạnh ổ `virtioa.qcow2` trong thư mục image đang dành cho Ubuntu này, theo quy ước EVE dùng `cdrom.iso` làm CD-ROM. Không sửa byte nào của QCOW2 gốc hoặc template; không gắn network cho node.
- Vì EVE API login chưa thực hiện, seed chưa được tạo/chuyển và lab/node chưa được tạo.

## Tài nguyên và cách ly

- Node sẽ có `cpu=1`, `ram=2048` (MiB), `ethernet=1`, `status=0`.
- Không thêm network object hoặc link; NIC để không kết nối, nên node không có đường tới mạng sản xuất hay Internet.
- Không tạo topology SOC, không cài Open vSwitch.

## Điểm chờ trước thao tác tạo lab/node

EVE API chính thức yêu cầu đăng nhập và cảnh báo login admin lần hai có thể vô hiệu hóa phiên cũ. Cần xác nhận có thể tạo phiên API admin (có thể làm phiên Web UI admin hiện tại phải đăng nhập lại) hoặc người dùng cần đóng/đăng xuất phiên Web UI trước. Chưa có thay đổi trên EVE trong bước tiền kiểm tra này.

## Nguồn chính thức

- EVE-NG, [API authentication, lab and node management](https://www.eve-ng.net/index.php/how-to-eve-ng-api/)
- EVE-NG, [QEMU image naming](https://www.eve-ng.net/index.php/documentation/qemu-image-namings/)
- EVE-NG, [EFI image example and OVMF files](https://www.eve-ng.net/index.php/xrv9000-efi/)
- Ubuntu, [Boot a cloud image with SeaBIOS or UEFI and create a local cloud-init seed](https://documentation.ubuntu.com/_/downloads/public-images/en/latest/pdf/)
- Canonical, [Ubuntu Server 24.04 cloud image manifest](https://cloud-images.ubuntu.com/releases/noble/release/ubuntu-24.04-server-cloudimg-amd64.manifest)
- Không có công cụ browser/screenshot khả dụng trong phiên này; chưa chụp ảnh minh chứng.

## Lab thử nghiệm đã chuẩn bị; chờ phê duyệt bật node (2026-10-31 14:31:42 +07:00)

- Sau khi người dùng xác nhận đã đăng xuất EVE Web, đăng nhập EVE API Community được thực hiện qua SSH tunnel tới loopback. Cookie phiên ở `/tmp` với quyền hạn chế, API logout được gọi trong cleanup và cookie đã bị xóa. Không ghi password/token/session cookie vào dự án hoặc log.
- API xác nhận image `linux-ubuntu-24.04-ovs` có trong danh sách của template `linux`.
- Tạo lab riêng `SOC-Ubuntu-Image-Test` tại `/SOC-Ubuntu-Image-Test.unl`, và một node `Ubuntu-Test` (node ID 1, UUID `b589f4b1-39d2-4f77-a6e9-96f6cdb004ab`). API đọc lại xác nhận `cpu=1`, `ram=2048 MiB`, `ethernet=1`, `status=0` (tắt). Phân tích file lab xác nhận 0 network object và 0 link.
- Tạo NoCloud seed `/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs/cdrom.iso`, volume label `cidata`. QCOW2 gốc không bị sửa. Seed owner `root:root`, mode `644`, SHA-256 `5f454921f7c183a0971a8694fe55c064713261fcfac418c94abc206a8f8dd1c1`.
- Tài khoản dự kiến `soc-test`, SSH Ed25519 public-key auth; `ssh_pwauth: false`, password account bị khóa, root login tắt. `sudo` NOPASSWD chỉ nằm trong guest thử nghiệm cô lập. Không có password plaintext trong cloud-init.
- Firmware node là firmware mặc định của template Linux (PC/SeaBIOS; không OVMF/pflash). Manifest Canonical liệt kê cả `grub-pc` và `grub-efi-amd64`, nhưng **chưa boot-test image Noble trong EVE**. Host có OVMF files nhưng template không gọi chúng. Không thay firmware/template dùng chung.
- NIC duy nhất chưa được kết nối; không có mạng production/Internet. Chưa cài OVS, không tạo topology SOC.
- **Chưa bật node.** Đăng nhập/SSH guest, cloud-init hoàn tất, firmware/boot và trạng thái console chưa thể xác nhận trước khi bật.
- Không có công cụ chụp màn hình/browser điều khiển trong phiên này; không tạo ảnh minh chứng.
## Kết quả boot thử sau khi được phê duyệt (2026-10-31 14:36:57 +07:00)

- Người dùng đã cho phép bật riêng node `Ubuntu-Test` trong lab `SOC-Ubuntu-Image-Test`.
- Kết nối SSH OpenSSH tới `root@192.168.220.143` thành công bằng cấu hình khóa sẵn có ở chế độ BatchMode; không dùng mật khẩu và không thay đổi EVE.
- Tiến trình QEMU khớp UUID lab/node còn hoạt động sau hơn 3 phút. Tham số được quan sát: `-smp 1`, `-m 2048`, `-machine type=pc,accel=kvm`, ổ `virtioa.qcow2` và CD-ROM `cdrom.iso`. Không có OVMF/pflash trong dòng lệnh; firmware là chế độ PC mặc định của template. Dung lượng filesystem `/`: 57G tổng, 42G còn trống.
- Ảnh console cho thấy kernel đã khởi chạy, systemd đã bắt đầu các dịch vụ và ext4 đã remount phân vùng gốc. Sau đó xuất hiện lặp lại lỗi đọc `fd0` (floppy); ảnh console sau khoảng hai phút vẫn chưa có màn hình đăng nhập hoặc dấu hiệu hoàn tất cloud-init.
- **Kết luận:** QEMU/node khởi chạy được và guest đã tiến vào kernel/systemd; chưa xác nhận Ubuntu boot hoàn chỉnh, cloud-init đã áp dụng seed, hoặc SSH guest đăng nhập được. Image chưa được xác nhận usable end-to-end.
- Minh chứng thực tế (ảnh console, không chứa thông tin xác thực): `docs/evidence/eve-ng/ubuntu-test-console.png` và `docs/evidence/eve-ng/ubuntu-test-console-after-boot.png`.
- Node có một NIC nhưng không được nối vào network object/link. Không cấu hình OVS/VLAN, không nối production/Internet, không cài phần mềm, không thay đổi image gốc/template/VMware.
- Cần bước xử lý tiếp theo để chẩn đoán trạng thái guest (chẳng hạn console tiếp tục chờ hoặc kiểm tra log guest). Nếu muốn kiểm tra SSH/cloud-init qua mạng thì cần phê duyệt riêng cho một mạng cô lập hoặc node kiểm thử bổ sung; chưa tạo các thành phần đó. Node hiện vẫn đang chạy theo yêu cầu bật thử; chưa gửi lệnh stop.
## Chẩn đoán console sau khi node đã chạy (2026-10-31 14:43 +07:00)

> Phần cập nhật này thay thế kết luận boot chưa hoàn tất ở các mục trước: lần chụp console mới hơn đã xác nhận TTY1 và login prompt. Trạng thái cloud-init vẫn chưa xác minh.

- Kiểm tra SSH chỉ đọc tới EVE thành công. Tiến trình QEMU đúng UUID `b589f4b1-39d2-4f77-a6e9-96f6cdb004ab` còn chạy; cấu hình thực tế gồm 1 vCPU, 2048 MiB, ổ VirtIO `virtioa.qcow2`, CD-ROM `cdrom.iso`, `-machine type=pc,accel=kvm`, `-vga std`, `-vnc :26869`. Không có `-serial`, `-nographic`, `-monitor`, `-fda`, `if=floppy` hoặc `-device floppy` được khai báo tường minh; không có OVMF/pflash. QEMU dùng VGA qua VNC; framebuffer 720x400, được xem qua SSH tunnel. Wrapper log tại thư mục runtime đúng node có kích thước 0 byte.
- Ảnh console trước Enter ghi `Ubuntu 24.04.5 LTS ubuntu tty1`. Đã gửi duy nhất một phím Enter (không gửi username/mật khẩu); ảnh sau đó hiển thị `ubuntu login:` trên `tty1`.
- **Kết luận boot:** Ubuntu đã khởi động tới TTY1 và xuất hiện login prompt. Không thấy kernel panic hoặc emergency mode trong phần console/log thu được. Lỗi `fd0` lặp trong ảnh cũ không ngăn guest tới login prompt; QEMU command line không yêu cầu floppy tường minh, nên đây có vẻ là probe thiết bị floppy legacy của PC machine, không phải lỗi ổ đĩa root. Đây là nhận định dựa trên console và cấu hình QEMU quan sát được.
- **Cloud-init:** tệp seed có cloud-config, metadata có `instance-id`, có cấu hình SSH authorized-keys, `ssh_pwauth: false` và khóa mật khẩu tài khoản; CD-ROM được gắn trong QEMU và kiểm tra ISO xác nhận volume label `cidata` (NoCloud). Điều này xác nhận seed được chuẩn bị và gắn đúng dạng nhận diện, nhưng không chứng minh guest đã xử lý seed. Chưa đăng nhập guest, không có serial log/cloud-init log/guest agent khả dụng; vì vậy trạng thái datasource đã được cloud-init nhận và cloud-init hoàn tất vẫn chưa xác minh. Không hiển thị hoặc ghi public/private key hay thông tin đăng nhập vào log.
- Ảnh minh chứng mới: `docs/evidence/eve-ng/ubuntu-test-console-diagnostic-before-enter.png`, `docs/evidence/eve-ng/ubuntu-test-console-diagnostic-after-enter.png`. Ảnh sau Enter chứng minh login prompt có mặt.
- Lab vẫn không có network object/link; không kết nối NIC ra mạng, không thêm node, không cài OVS. Không sửa image gốc, template, firmware, VMware hoặc cấu hình mạng. Node vẫn đang chạy.
## Kiểm tra tài khoản và cloud-init seed (2026-10-31 14:48 +07:00)

- Đã kiểm tra cục bộ các trường cấu hình của `user-data.yaml` và `meta-data.yaml` mà không in nội dung public key. `user-data` có tiêu đề cloud-config và khai báo duy nhất user `soc-test`; user có `lock_passwd: true`, một SSH public key loại Ed25519, `ssh_pwauth: false`, không khai báo `passwd`, `hashed_passwd`, `plain_text_passwd` hay `chpasswd`. Không có mục `default` trong danh sách users. Giá trị public key và bất kỳ bí mật nào không được đưa vào báo cáo/log.
- `meta-data` có `instance-id` và `local-hostname`. ISO hiện tại có SHA-256 `5f454921f7c183a0971a8694fe55c064713261fcfac418c94abc206a8f8dd1c1`; kiểm tra ISO xác nhận nhãn `cidata` và hai file ở root (`USER_DAT.YAM`, `META_DAT.YAM`). QEMU vẫn gắn ISO này. Điều đó xác nhận cấu hình seed được chuẩn bị/gắn, **không chứng minh cloud-init trong guest đã nhận hoặc áp dụng nó**.
- Console `tty1` có login prompt, nhưng dòng `ubuntu login:` là hostname `ubuntu` cộng với prompt đăng nhập, không chứng minh có tài khoản `ubuntu`. Theo tài liệu cloud-init, khi khai báo danh sách `users`, muốn tạo user mặc định của distro phải có mục `default`; seed hiện tại không yêu cầu user mặc định đó. User được khai báo là `soc-test`.
- Console login qua TTY có sẵn, nhưng seed không thiết lập mật khẩu cho `soc-test` và khóa password login cho tài khoản này. Vì vậy hiện **không có thông tin xác thực hợp lệ từ seed để đăng nhập console**; đừng thử mật khẩu đoán. Public key chỉ dùng cho SSH, không thay thế mật khẩu tại `login:`. `ssh_pwauth: false` chỉ tắt SSH password authentication; SSH key là đường đăng nhập dự kiến, nhưng NIC node đang không nối vào mạng nên chưa thể dùng đường đó.
- Chưa có bằng chứng guest chạy `cloud-init status --long`, chưa đọc được `/var/log/cloud-init.log` hoặc `/var/log/cloud-init-output.log` bên trong guest. `wrapper.txt` của QEMU rỗng; các log cloud-init trên EVE host là log của host, không dùng làm bằng chứng guest. Không có YAML parser cloud-init sẵn trên Windows trong phiên này, nên các trường được đối chiếu trực tiếp nhưng chưa có kiểm tra schema độc lập. Kết luận: **cloud-init hoàn tất/chưa hoàn tất đều chưa xác minh**.

### Phương án nếu cần đăng nhập/xác minh thêm (chưa thực hiện)

1. **Ưu tiên không đặt password:** tạo một đường SSH tạm thời, cô lập từ máy kiểm thử tới node và dùng private key tương ứng với public key đã có; giữ SSH password authentication tắt. Sau đăng nhập, đọc `cloud-init status --long` và log guest. Cần phê duyệt riêng trước khi nối NIC hoặc tạo thành phần mạng.
2. **Nếu cần console login:** dùng seed riêng cho node thử nghiệm với `hashed_passwd` và `lock_passwd: false` cho tài khoản kiểm thử; giữ `ssh_pwauth: false`. Sinh hash cục bộ, không lưu password plaintext. Do cloud-init áp dụng user-data theo instance/first boot, cách an toàn là tạo node kiểm thử mới dùng overlay mới và `instance-id` mới, giữ nguyên image gốc và template. Không sửa node đang chạy hay seed hiện tại trước khi có phê duyệt.

Nguồn chính thức: [cloud-init users/groups: default user, lock_passwd, hashed_passwd, ssh_authorized_keys](https://docs.cloud-init.io/en/latest/reference/modules.html); [cloud-init NoCloud: nhãn CIDATA, seed files, instance-id/first boot](https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html).
## Phương án mạng cô lập để kiểm tra SSH public-key (2026-10-31 14:52 +07:00; chỉ lập kế hoạch)

### Kiểm kê EVE chỉ đọc

- Đọc 3 file lab `.unl` trong `/opt/unetlab/labs`; không gọi API thay đổi.
  - `SOC-Ubuntu-Image-Test`: 1 node, 0 network object, 0 link.
  - `M2`: 5 network object loại `bridge`, 5 node, 0 link.
  - `M2_Core_L3`: 1 network object loại `pnet1`, 1 node, 0 link. Không dùng object này: tài liệu EVE mô tả pnet1/Cloud1 như đường bridge tới adapter thứ hai EVE, có thể nối tới mạng/thiết bị bên ngoài; chưa xác minh adapter thực tế đang nối vào VMware network nào.
- EVE hiện có duy nhất thư mục QEMU Linux `linux-ubuntu-24.04-ovs`. Template hiện tại gắn `cdrom.iso` dùng chung theo thư mục image; không nên tạo client node từ cùng image/seed y nguyên vì sẽ lặp cùng metadata/instance-id. Cần seed riêng/instance-id duy nhất nếu dùng node Ubuntu thứ hai.
- SSHD hiệu lực trên EVE báo `allowagentforwarding yes`; đây chỉ cho phép forwarding ở SSH server EVE, không tự tạo đường tới node trong bridge nội bộ và không chứng minh key đang được agent giữ.

### Địa chỉ mạng trong seed

- `user-data.yaml`, `meta-data.yaml` không khai báo network-config, địa chỉ tĩnh, gateway, DHCP hoặc subnet; không có file `network-config` riêng.
- Vì vậy không thể xác định IP hiện tại. Khi có NIC và network, cloud-init có thể dùng cấu hình mạng mặc định (thường DHCP), nhưng hiện node không nối network object/link và chưa có DHCP lease/IP xác nhận. Bridge EVE là Layer 2 thuần; nó không tự cấp DHCP.
- Không chọn hoặc ghi IP/subnet trong phương án này. Cần quyết định subnet riêng và DHCP hay cấu hình IP tĩnh per-node ở bước được phê duyệt.

### Topology đề xuất

```text
Ubuntu-Test NIC0 ─────┐
                      ├── SOC-SSH-Test-Isolated (EVE network type: bridge)
SSH-Test-Client NIC0 ─┘
```

- Tạo bridge object mới chỉ trong lab `SOC-Ubuntu-Image-Test`; không tái sử dụng bridge trong `M2`, không dùng `pnet*`, Cloud/NAT, VMware adapter, mạng quản trị, mạng vật lý hoặc lab SOC khác. Theo cookbook EVE, `bridge` là switch unmanaged nội bộ của topology.
- Client dự kiến là Linux QEMU node với SSH client. Tài nguyên ước tính: Ubuntu-Test đang dùng 1 vCPU/2048 MiB; client khoảng 1 vCPU/1024 MiB; tổng hai guest khoảng 2 vCPU/3 GiB RAM, chưa tính overhead EVE. Chưa có image Linux client riêng được xác nhận; image hiện có là Ubuntu đang thử nghiệm.
- Không tạo network/node và không nối NIC trong bước này.

### Điều kiện cần giải quyết trước khi có thể chạy SSH test

- Client node cần ký xác thực bằng private key tương ứng với public key trong seed. Không được chép private key vào EVE/node theo điều kiện hiện tại. Key chỉ có trên Windows/agent; agent forwarding tới SSH server EVE được phép ở mức cấu hình, nhưng EVE host không tự nằm trong bridge cô lập và không có đường đã xác minh để chuyển agent/socket tới client node.
- Vì vậy topology hai node + bridge tự nó chưa đủ để kiểm tra key theo đúng ràng buộc. Hai hướng cần phê duyệt/thiết kế riêng:
  1. Giữ key trên Windows và dùng Windows OpenSSH làm client qua một relay/port-forward chỉ nối tới bridge test. Cần thiết kế relay sao cho không mở guest ra NAT/Internet/VMware adapter; đây là đường host-side, không phải node client EVE.
  2. Dùng agent forwarding tới client node mà không sao chép private key. Cần một đường agent relay tới đúng node và xác minh kiểm soát truy cập; khả năng này chưa được kiểm thử, không nên coi là sẵn sàng.
- Không thể vừa yêu cầu một Linux client node dùng đúng private key, vừa cấm private key và chưa có agent relay/host path, nếu chỉ thêm bridge nội bộ. Nếu không chọn một trong hai hướng không chuyển private key, phải thay đổi điều kiện bảo vệ key; không đề xuất làm vậy.
- Nếu dùng cùng Ubuntu image làm client, cần image directory/seed riêng với instance-id riêng; đó là thao tác bổ sung image/seed và cần phê duyệt. Không dùng nguyên `cdrom.iso` hiện tại cho node thứ hai.

### Các thông số/quyết định cần phê duyệt trước triển khai

1. Chấp nhận client là Windows qua relay cô lập hay cần một Linux client node cùng bridge; nếu cần Linux node, phê duyệt thiết kế agent relay cụ thể sau khi kiểm tra tính khả thi.
2. Subnet riêng, static hay DHCP, và thành phần nào cấp DHCP. Hiện chưa có IP nào được gán hoặc xác nhận.
3. Nếu cần client node: image/seed riêng, `instance-id` mới, số vCPU/RAM và dung lượng disk.
4. Tạo bridge object mới trong lab test và gắn NIC0 của Ubuntu-Test; thao tác này có thể yêu cầu dừng/khởi động lại node để NIC được áp dụng, nên cần phê duyệt trạng thái vòng đời node riêng.
5. Có cho phép tạo/khởi chạy client node và/hoặc host-side relay hay không; không sửa SSHD, không chép private key, không dùng NAT/pnet.

Chưa tạo bridge, chưa nối NIC, chưa tạo client node, chưa cấp IP, chưa thay seed/image và chưa thay đổi EVE/VMware. Ubuntu-Test vẫn giữ trạng thái đang chạy.

Nguồn chính thức: [EVE-NG Cookbook: Bridge Network là switch unmanaged](https://www.eve-ng.net/wp-content/uploads/2023/02/EVE-COOK-BOOK-5.4-2023.pdf); [EVE-NG Cookbook: pnet/Cloud mapping tới adapter ngoài](https://www.eve-ng.net/wp-content/uploads/2024/01/EVE-PE-BOOK-5.11-2023.pdf); [cloud-init NoCloud và network defaults](https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html).
## Phương án console login bằng seed riêng cho node thử nghiệm (2026-10-31 15:00 +07:00; chưa áp dụng)

### Bằng chứng về overlay và seed hiện tại

- Node `Ubuntu-Test` vẫn chạy. QEMU overlay thực tế nằm dưới runtime path riêng của lab/node: `/opt/unetlab/tmp/0/459ae313-d464-454d-a219-b096bf8d2cfe/1/virtioa.qcow2`. `qemu-img info` chỉ đọc xác nhận overlay là QCOW2, virtual size 3,758,096,384 bytes, actual size khoảng 22.4 MB, backing file là image Ubuntu gốc. Image gốc là QCOW2 độc lập (không có backing file); kích thước thực khoảng 621 MB. Đây là bằng chứng node ghi vào overlay riêng thay vì ghi trực tiếp vào image gốc.
- QEMU hiện lấy CD-ROM từ đường dẫn dùng chung trong thư mục image: `/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs/cdrom.iso`. Không thay ISO này: thay seed tại đó có thể ảnh hưởng mọi node chọn cùng image.
- Còn khoảng 42 GB trên filesystem EVE. EVE có `qemu-img`, `genisoimage`, OpenSSL 3.0.2; `mkpasswd` không có. `openssl passwd -6` được hỗ trợ và có thể đọc password từ terminal khi không truyền password trên command line; password plaintext không cần vào script/log.
- EVE Cookbook mô tả Wipe node sẽ xóa temporary image snapshot để node boot lại từ base image. Thao tác wipe là phá hủy thay đổi trong overlay, nên cần sao lưu overlay và phê duyệt riêng trước khi dùng.

### Cách ly seed và overlay để chỉ thử trong lab này

- Giữ nguyên node/overlay `Ubuntu-Test`, image gốc `linux-ubuntu-24.04-ovs/virtioa.qcow2` và seed ISO hiện tại.
- Phương án đề xuất: tạo một image variant riêng, ví dụ `linux-ubuntu-24.04-soc-console-test`, trong thư viện QEMU của EVE; sao chép nguyên vẹn QCOW2 gốc vào đó (dự kiến khoảng 621 MB), tạo `cdrom.iso` riêng cho variant, rồi thêm node mới `Ubuntu-Console-Test` trong cùng lab và chọn variant này. EVE tạo overlay runtime riêng cho node mới khi start. Chỉ node mới trong `SOC-Ubuntu-Image-Test` sẽ tham chiếu variant; không sửa image/template dùng chung đang có.
- Lưu ý phạm vi: thư mục image mới nằm trong thư viện image EVE nên sẽ xuất hiện toàn hệ thống trong danh sách image, dù chỉ lab thử nghiệm dùng nó. Đây là giới hạn của cách EVE chọn `cdrom.iso` theo image directory. Không thấy/không xác nhận cơ chế gắn seed riêng theo node trong Community template/API hiện tại; không thêm QEMU custom option để thay `-cdrom` nếu chưa được kiểm chứng.
- Seed mới dùng `instance-id` duy nhất; tạo user `soc-test`, giữ nguyên SSH public key hiện tại, đặt `hashed_passwd` dạng SHA-512 crypt và `lock_passwd: false` để cho phép console login. Giữ `ssh_pwauth: false`, không dùng trường password plaintext. Password do người dùng tự nhập tại terminal tương tác khi sinh hash và tại console login; không gửi password hoặc hash vào chat/log/repository. Hash chỉ lưu trong seed ISO riêng của node thử nghiệm.
- Để bảo đảm cloud-init chạy trên first boot, dùng bản QCOW2 sạch vừa sao chép và `instance-id` mới. Không đổi seed dưới overlay đã boot rồi kỳ vọng module users chạy lại: cloud-init xác định first boot theo instance-id/cache.
- Tài nguyên dự kiến nếu giữ node cũ chạy: node cũ 1 vCPU/2 GiB + node console mới 1 vCPU/2 GiB = 2 vCPU/4 GiB RAM cho guest, cộng overhead EVE. EVE có 4 vCPU/8 GiB tổng; cần theo dõi áp lực bộ nhớ. Phần image copy 621 MB và seed nhỏ nằm trong 42 GB còn trống.

### Thứ tự kiểm chứng sau khi được duyệt

1. Ghi checksum/size image gốc và seed cũ; kiểm tra variant directory chưa tồn tại; sao chép image và so SHA-256; tạo user-data/meta-data mới rồi kiểm tra nội dung không chứa plaintext password.
2. Tạo seed ISO riêng nhãn `cidata`, xác nhận có `user-data`/`meta-data`, instance-id mới và SHA-256; kiểm tra quyền chỉ trên thư mục/file mới.
3. Thêm node mới trong lab này với 1 vCPU, 2048 MiB, 1 NIC không kết nối. Không dừng node cũ. Trước khi start, kiểm tra QEMU command line dự kiến trỏ tới variant image và variant CD-ROM, không trỏ seed cũ.
4. Chỉ sau phê duyệt riêng mới start node mới; đăng nhập `soc-test` qua VNC console, nhập password trực tiếp trong console. Không ghi input vào log/chụp ảnh khi nhập.
5. Sau login, chạy chỉ đọc: `cloud-init status --long`; kiểm tra datasource và instance-id; xem log cloud-init/journal tìm lỗi; `id soc-test`, `getent passwd soc-test`, `passwd -S soc-test`. Không đọc `/etc/shadow`. Xác nhận SSH password vẫn tắt bằng `sudo sshd -T`/cấu hình hiệu lực, không bật SSH password.

### Phục hồi nếu thử nghiệm thất bại

- Node hiện tại, image gốc và seed cũ vẫn giữ nguyên; thất bại ở node mới không đụng tới chúng.
- Không wipe ngay. Sau khi được duyệt dừng riêng node mới, giữ bản sao overlay runtime và log trước khi điều tra. EVE Wipe sẽ loại bỏ overlay node đó; chỉ dùng sau khi xác nhận backup và phê duyệt. Tạo lại một node/overlay mới từ bản variant sạch với `instance-id` mới để thử lại.
- Khi thử xong, node variant có thể được xóa khỏi lab theo phê duyệt. Image variant nằm trong thư viện EVE global, nên chỉ xóa thư mục sau khi xác nhận không lab/node nào tham chiếu; không xóa image gốc.

### Thao tác cần phê duyệt riêng trước khi thực hiện

- Tạo thư mục image variant toàn cục (dù chỉ lab thử nghiệm dùng), copy khoảng 621 MB image, tạo seed ISO mới và thêm một node trong lab `SOC-Ubuntu-Image-Test`.
- Sử dụng password hash `$6$` trong seed riêng; user tự nhập password trong terminal khi tạo hash/login, không cung cấp cho tôi.
- Start node mới (hiện node cũ vẫn chạy) và tài nguyên guest dự kiến tăng thêm 1 vCPU/2 GiB RAM.
- Mọi thao tác dừng/wipe/xóa node hoặc xóa image variant đều cần xác nhận riêng; chưa làm bất kỳ thao tác nào ở đây.

Nguồn chính thức: [EVE Community Cookbook: Wipe node xóa temporary image snapshot và boot từ base](https://www.eve-ng.net/wp-content/uploads/2020/03/EVE-Comm-BOOK-1.07-2020.pdf); [EVE API: quản lý node/lab và image](https://www.eve-ng.net/index.php/how-to-eve-ng-api/); [EVE naming cho QEMU image](https://www.eve-ng.net/index.php/documentation/qemu-image-namings/); [cloud-init user/hash fields và trạng thái](https://docs.cloud-init.io/en/latest/reference/modules.html); [cloud-init NoCloud, instance-id và first boot](https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html); [OpenSSL passwd](https://docs.openssl.org/3.3/man1/openssl-passwd/).
- Bổ sung kiểm tra tham chiếu image: trong 3 file lab `.unl` hiện có, `linux-ubuntu-24.04-ovs` chỉ được tham chiếu bởi node `Ubuntu-Test` của lab thử nghiệm. Đây không làm thay đổi giới hạn rằng thư mục image variant mới sẽ nằm trong thư viện toàn cục.
## Tiến độ triển khai seed console (2026-10-31 15:06 +07:00)

- Đã kiểm tra lại: variant path `/opt/unetlab/addons/qemu/linux-ubuntu-24.04-soc-console-test` chưa tồn tại trước khi tạo; disk EVE còn 42 GiB; image gốc có SHA-256 `04e8f2461a16a44e78a370284471f29616cdd9baf1893df25807b71f985b6c94`. Sau khi tạo variant, SHA-256 image gốc vẫn đúng giá trị này.
- Đã tạo thư mục image variant riêng và `virtioa.qcow2` dạng QCOW2 backing file bằng QEMU `qemu-img` 2.12.0. Overlay variant virtual-size 3.5 GiB, actual-size khoảng 196 KiB, backing trỏ tới QCOW2 gốc; `qemu-img check` báo không có lỗi. Thư mục mode 755 root:root, disk mode 644 root:root. Không ghi lên QCOW2 gốc.
- EVE có 7.7 GiB RAM tổng, khoảng 5.7 GiB available tại lần kiểm tra; chỉ node QEMU `Ubuntu-Test` đang chạy (RSS xấp xỉ 589 MiB, node cấu hình 2 GiB). Chưa dừng node này. Sẽ kiểm tra lại memory trước khi start node mới; nếu available không đủ sẽ dừng và báo.
- ISO seed mới chưa tạo; node `Ubuntu-Console-Test` chưa thêm/chưa chạy. Public key loại Ed25519 được kiểm tra trích xuất từ seed cũ thành công nhưng không hiển thị; source seed cũ không bị đổi.
- EVE không có `mkpasswd`; có OpenSSL 3.0.2 với `passwd -6`. Bước tiếp theo cần người dùng nhập mật khẩu console trực tiếp trong terminal PuTTY để tạo hash SHA-512 crypt. Hash sẽ được giữ trong biến shell và file seed bảo vệ, không được echo/log/báo cáo. Không gửi mật khẩu hoặc hash qua chat.
- Các thao tác đã thực hiện chỉ gồm tạo thư mục variant mới và QCOW2 overlay variant; không tạo node, không tạo ISO, không dừng/bật node, không nối mạng, không sửa template/VMware/lab khác.

## Xác nhận cloud-init thành công trên Ubuntu-Console-Test (2026-10-31; minh chứng M2)

> Cập nhật mới nhất này thay thế các kết luận **chưa xác minh cloud-init** đối với node `Ubuntu-Console-Test`. Các mục trước được giữ làm lịch sử; không suy rộng kết quả mới sang `Ubuntu-Test` cũ.

### Kết quả đã xác minh

- Người dùng xác nhận đã đăng nhập console thành công bằng `soc-test`. Trong phiên thu thập, console thật có shell `soc-test@soc-ubuntu-console-test`; `whoami` trả về `soc-test`.
- Đã chạy lại chỉ đọc `cloud-init status --long`: `status: done`, `extended_status: done`, `detail: DataSourceNoCloud [seed=/dev/sr0]`, `errors: []`, `recoverable_errors: {}`. **Cloud-init trên node console đã hoàn tất thành công theo báo cáo trạng thái guest.**
- Ảnh chính: [Hình 2.1](../M2/M2-cloud-init-success-20261031T184335+0700.png), thu lúc 18:43:35–18:43:42 ngày 31/10/2026, UTC+07:00 theo máy thu thập. Chú thích: **Hình 2.1. Kết quả kiểm tra trạng thái cloud-init trên Ubuntu Server 24.04**.
- [Hình 2.2](../M2/M2-ubuntu-system-info-20261031T184400+0700.png) xác nhận hostname `soc-ubuntu-console-test`, Ethernet `ens3` (MAC `00:50:00:00:02:00`) và loopback `lo`; `nproc=1`, RAM guest tổng 1967 MiB; `cloud-id=nocloud`. XML/QEMU xác nhận 1 vCPU, 2048 MiB RAM, 1 NIC VirtIO. NIC chưa nối mạng; `UP` không đồng nghĩa có kết nối ngoài.
- Node ID 2, UUID `09ac16f0-1614-48c5-8d01-ee1ab1b29582`, image variant `linux-ubuntu-24.04-soc-console-test`, CD-ROM riêng đã tồn tại và đang chạy khi kiểm tra. Không cần tạo lại node/seed. Phần 15:06 ghi chưa tạo node/ISO là snapshot lịch sử, không phải trạng thái hiện tại.

### Minh chứng, báo cáo và giới hạn

- Ảnh là framebuffer QEMU VNC thực tế toàn màn hình, không cắt/ghép/sửa nội dung; JSON cùng tên ghi nguồn, cấu hình quan sát, thời điểm và checksum. [Danh mục minh chứng](../M2/M2-evidence-index-20261031T1844+0700.md), [log chép từ ảnh](../M2/M2-cloud-init-validation-20261031T1844+0700.log).
- [Báo cáo M2 Markdown](../../M2/M2-cloud-init-validation-20261031.md) và [bản Word](../../M2/M2-cloud-init-validation-20261031.docx) gồm Hình 2.1–2.2, giải thích bảy thuật ngữ, kiểm tra tài nguyên và đề xuất NIC.
- `last_update` trong guest ghi năm 1970; EVE chưa đồng bộ NTP và lệch giờ máy thu thập. Không dùng các giá trị đó làm thời điểm ảnh, chưa chỉnh giờ. Chưa thu riêng mã thoát của lệnh hoặc toàn bộ log cloud-init trong guest.
- Kết quả xác nhận nền Ubuntu quản trị được, **chưa nghiệm thu OVS/VLAN/trunk/mirror hoặc toàn bộ M2**. Theo hồ sơ OVS chưa được cài; phiên này không cài và chưa kiểm kê package/runtime guest.
- Khuyến nghị Core **8 vNIC** (5 access cho VLAN 30/40/50/60/99 + 2 trunk tới hai OPNsense + 1 mirror). Đây là đề xuất; chưa đổi số NIC, chưa xác nhận tên NIC bổ sung, số cổng peer, subnet/IP hoặc khả năng template ở cấu hình 8 NIC. Hai trunk HA không phải một bond LACP xuyên hai firewall.
- Phiên này chỉ chạy lệnh chẩn đoán đọc và ghi tài liệu/minh chứng trên Windows. Không sửa seed/image/mạng, không cài OVS, không dừng/start/wipe/xóa node. Các ảnh/log cũ được giữ nguyên; các lần chụp trung gian có giới hạn được phân loại trong danh mục.

### Bước tiếp theo cần phê duyệt

Chốt phương án NIC và node Core đích; phê duyệt riêng việc tăng NIC/vòng đời node nếu cần, kế hoạch cấp gói để cài OVS và mạng kiểm thử. Chưa tự nối pnet/NAT/Internet. Core tiếp tục chỉ Layer 2; gateway, inter-VLAN routing, firewall rules và NAT xử lý trên OPNsense.
