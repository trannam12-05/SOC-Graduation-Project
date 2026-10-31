# Báo cáo kiểm tra EVE-NG

- **Thời gian:** 2026-10-31 11:25 (Asia/Ho_Chi_Minh)
- **Phạm vi:** chỉ kiểm tra kết nối và khả năng công cụ tại máy Windows; không tạo lab/node, không thay đổi cấu hình VMware/EVE-NG.
- **URL được kiểm tra:** `http://192.168.220.143/`

## Phương pháp

- Mở kết nối TCP trực tiếp từ Windows tới `192.168.220.143` trên cổng 80 và 443.
- Gửi HTTP `HEAD` bằng `curl.exe`, chỉ thu mã HTTP, IP phản hồi và Content-Type; không lưu/hiển thị nội dung trang, cookie hay thông tin đăng nhập.
- Kiểm tra một số đường dẫn cài đặt phổ biến và module Python cho Edge, Chrome, Firefox, Playwright, Selenium, PyAutoGUI và Pillow.
- Kiểm tra sự hiện diện của Snipping Tool. Không mở trình duyệt hoặc giao diện đồ họa.

## Kết quả xác nhận

- TCP tới `192.168.220.143:80` **kết nối thành công**.
- `http://192.168.220.143/` phản hồi **HTTP 200**, Content-Type `text/html`.
- TCP 443 không được xác nhận là cần thiết; thiết kế được cung cấp sử dụng HTTP.
- Theo thông tin người dùng, trang đăng nhập web đang truy cập được. Kiểm tra tự động ở đây chỉ xác nhận endpoint HTTP phản hồi, không đọc nội dung để xác nhận trạng thái đăng nhập.
- Không tìm thấy Edge, Chrome hoặc Firefox trong các đường dẫn cài đặt phổ biến đã kiểm tra. Không tìm thấy các module Playwright, Selenium, PyAutoGUI hoặc Pillow.
- Snipping Tool có trên máy nhưng là công cụ giao diện; phiên làm việc này không có khả năng điều khiển giao diện hoặc chụp màn hình bằng nó.
- **Chưa kiểm tra danh sách image/template** Cisco IOSvL2, OPNsense, Linux/Ubuntu và VPCS. Chưa có ảnh minh chứng.

## Thao tác cần người dùng thực hiện

1. Mở `http://192.168.220.143/` trong trình duyệt trên máy Windows và tự đăng nhập; không gửi mật khẩu/token vào cuộc trò chuyện.
2. Trong giao diện EVE-NG, mở trang danh sách/kiểm tra image hoặc tạo lab mới ở trạng thái chưa lưu nếu cần truy cập template. Không bật node và không lưu/thay đổi lab.
3. Ghi lại sự hiện diện chính xác của Cisco IOSvL2, OPNsense, Linux/Ubuntu và VPCS; gửi kết quả bằng văn bản hoặc ảnh đã che dữ liệu nhạy cảm.
4. Nếu cần ảnh minh chứng, tự chụp dashboard và danh sách image sau khi đăng nhập, đảm bảo ảnh không chứa mật khẩu, token hoặc cookie, rồi lưu vào thư mục này với tên `eve-ng-dashboard.png` và `eve-ng-images.png`.

## Ảnh minh chứng

Hiện chưa có ảnh minh chứng. Không có đường dẫn ảnh nào được báo cáo là đã tồn tại.

## Bổ sung kiểm tra SSH từ Windows — 2026-10-31 11:29 (Asia/Ho_Chi_Minh)

### Công cụ

- OpenSSH client: `C:\Windows\System32\OpenSSH\ssh.exe` — OpenSSH 9.5p2 for Windows.
- PuTTY, Plink và Pageant: Release 0.85.
- WinSCP: 6.7.0.0.
- Không cài đặt thêm phần mềm.

### Kết nối

- `192.168.220.143:80`: TCP thành công; HTTP HEAD trả mã 200.
- `192.168.220.143:22`: TCP thành công.
- Thử SSH **chỉ bằng public key**, tắt xác thực mật khẩu/keyboard-interactive, không lưu host key: máy chủ không chấp nhận public-key authentication; client không gửi được public key. Không sử dụng mật khẩu.

### Tình trạng phương thức xác thực an toàn sẵn có

- Windows `ssh-agent`: Stopped, StartupType Disabled.
- Không thấy tiến trình Pageant đang chạy.
- Thư mục người dùng `.ssh` có `known_hosts` và `known_hosts.old`; không thấy file khóa trong thư mục này.
- Chưa xác nhận có khóa an toàn được cấu hình trong PuTTY/WinSCP; không đọc session, secret hoặc nội dung file khóa.
- Chưa đăng nhập SSH thành công. Vì vậy phiên bản EVE-NG, tài nguyên, dung lượng đĩa, image QEMU/IOL/Dynamips và template **chưa được kiểm tra**. Không thể kết luận image nào có hoặc dùng được.

### Cần người quản trị thực hiện

Dùng PuTTY/WinSCP để đăng nhập thủ công trong giao diện máy của bạn, không chia sẻ mật khẩu ở đây; hoặc cấu hình public key theo quy trình quản trị an toàn. Sau khi xác nhận phương thức truy cập chỉ đọc đã sẵn sàng, có thể tiếp tục kiểm tra. Không cần gửi private key, mật khẩu, token hay cookie.

### Ảnh minh chứng

Chưa chụp ảnh. Không có ảnh mới được tạo. Ảnh duy nhất cần chụp sau này là các màn hình thông tin không chứa dữ liệu nhạy cảm.

## Ghi nhận tiếp theo — 2026-10-31 (Asia/Ho_Chi_Minh)

Người dùng báo đã hoàn tất thao tác trong cửa sổ PuTTY root. Phiên PuTTY là cửa sổ tương tác riêng; tôi không thể đọc terminal đó hoặc dùng phiên đã xác thực làm kênh SSH cho các lệnh của mình. Vì vậy chưa có kết quả kiểm tra từ bên trong EVE-NG được xác minh độc lập.

Để tiếp tục mà không đưa mật khẩu vào lệnh/log, hãy chạy khối lệnh chỉ đọc bên dưới trong terminal PuTTY root và gửi lại phần output. Các lệnh chỉ đọc phiên bản, CPU/RAM/đĩa và metadata file/template; không bật node, sửa file, tải/cài image hoặc chạy fixpermissions.

```sh
printf '\n=== EVE version ===\n'
cat /opt/unetlab/version 2>/dev/null || dpkg-query -W -f='${binary:Package} ${Version}\n' 'eve-ng*' 2>/dev/null
printf '\n=== Host / CPU / RAM / disk ===\n'
hostname
uname -r
lscpu | grep -E '^(Architecture|CPU\(s\)|Model name|Virtualization):'
free -h
df -hT / /opt/unetlab
printf '\n=== QEMU directories and disk files ===\n'
find /opt/unetlab/addons/qemu -mindepth 1 -maxdepth 2 -type f \
  \( -iname '*.qcow2' -o -iname '*.qcow' -o -iname '*.img' \) \
  -printf '%M %u:%g %s %p\n' 2>/dev/null
printf '\n=== IOL files ===\n'
find /opt/unetlab/addons/iol/bin -maxdepth 1 -type f \
  -printf '%M %u:%g %s %f\n' 2>/dev/null
printf '\n=== Dynamips files ===\n'
find /opt/unetlab/addons/dynamips -maxdepth 2 -type f \
  -printf '%M %u:%g %s %p\n' 2>/dev/null
printf '\n=== Relevant templates ===\n'
find /opt/unetlab/html/templates -type f \
  \( -iname '*viosl2*.yml' -o -iname '*opnsense*.yml' -o -iname '*linux*.yml' \
     -o -iname '*ubuntu*.yml' -o -iname '*vpcs*.yml' \) \
  -printf '%p\n' 2>/dev/null
printf '\n=== VPCS executable ===\n'
if test -x /opt/unetlab/addons/bin/vpcs; then ls -l /opt/unetlab/addons/bin/vpcs; else echo 'VPCS executable not found at standard path'; fi
```

Đường dẫn image và template ở trên dựa theo tài liệu EVE-NG; việc thấy file chỉ xác nhận file tồn tại. Chưa khởi chạy node nên chưa kiểm chứng runtime. Tài liệu tham khảo chính thức: [EVE-NG Cookbook – vị trí image và template](https://www.eve-ng.net/wp-content/uploads/2021/04/EVE-COOK-BOOK-4.10-2021.pdf), [EVE-NG hướng dẫn thư mục template](https://www.eve-ng.net/index.php/documentation/howtos/template-icons-and-config-scripts-update-from-git/).


## Kiểm tra xác thực SSH trên Windows — 2026-10-31 (Asia/Ho_Chi_Minh)

- `Get-Command ssh` xác nhận OpenSSH tại `C:\Windows\System32\OpenSSH\ssh.exe`.
- `ssh -V`: OpenSSH_for_Windows_9.5p2, LibreSSL 3.8.2.
- Thư mục `%USERPROFILE%\.ssh` chỉ có `known_hosts` và `known_hosts.old`; không thấy private/public key file. Không đọc nội dung hai file host key.
- Không có file cấu hình OpenSSH `~/.ssh/config`.
- Dịch vụ `ssh-agent` đang Stopped/Disabled; không có identity nào được xác nhận trong agent.
- Không tìm thấy PuTTY saved session cho `192.168.220.143` với trường key file; không đọc session WinSCP hay dữ liệu xác thực.
- Kết nối public-key-only tới `root@192.168.220.143` thất bại vì client không gửi public key nào; không thử mật khẩu.
- Do đó chưa có kênh SSH tự động an toàn để chạy lệnh kiểm tra chỉ đọc. Phiên PuTTY người dùng mở riêng không được OpenSSH/VS Code kế thừa.

### Bước dự kiến cần phê duyệt

Tạo một cặp khóa Ed25519 riêng trên Windows (private key ở lại máy Windows, có passphrase), sau đó thêm duy nhất public key tương ứng vào `/root/.ssh/authorized_keys` qua phiên PuTTY root. Thao tác này thay đổi quyền đăng nhập SSH trên EVE-NG. Chưa tạo khóa, chưa sửa `authorized_keys` hoặc cấu hình SSH và chưa đổi quyền file. Cần kiểm tra quyền hiện có trước; không chạy `chmod`/`fixpermissions`.

## Chuẩn bị tạo SSH key riêng — 2026-10-31

Người dùng đã cho phép tạo cặp Ed25519 riêng cho EVE-NG và thêm public key vào `/root/.ssh/authorized_keys`, với điều kiện kiểm tra trước và bảo toàn key cũ.

Kiểm tra cục bộ trước khi tạo:

- OpenSSH và `ssh-keygen` có sẵn.
- Thư mục `%USERPROFILE%\.ssh` tồn tại.
- Tên đích dự kiến `eve-ng-root-ed25519` và `eve-ng-root-ed25519.pub` hiện chưa tồn tại, nên chưa có nguy cơ ghi đè các file cùng tên.
- SSH agent vẫn Stopped/Disabled.
- Chưa tạo private/public key; chưa đọc/hiển thị private key; chưa sửa file trên Windows hoặc EVE-NG.

Đang chờ người quản trị đọc metadata/quyền hiện tại của `/root`, `/root/.ssh`, `/root/.ssh/authorized_keys`, loại key công khai hiện có và cấu hình SSH hiệu lực (`PubkeyAuthentication`, `AuthorizedKeysFile`, `StrictModes`, `PermitRootLogin`, `PasswordAuthentication`) qua PuTTY. Chưa có thay đổi từ bước này.

## EVE-NG SSH preflight — 2026-10-31

Kết quả do người quản trị chạy và cung cấp từ phiên PuTTY root:

- `/root` thuộc `root:root`, mode `700`.
- `/root/.ssh` và `/root/.ssh/authorized_keys` chưa tồn tại; không có public key cũ trong file đích và không cần tạo bản sao lưu file chưa tồn tại.
- `sshd -T`: `PubkeyAuthentication yes`, `AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys2`, `StrictModes yes`, `PermitRootLogin yes`, `PasswordAuthentication yes`.
- Chưa sửa `sshd_config`; không bật/tắt phương thức xác thực nào.

Đã mở một PowerShell terminal tương tác để tạo cặp Ed25519 cục bộ tại `%USERPROFILE%\.ssh\eve-ng-root-ed25519` và file `.pub` tương ứng. Người dùng cần nhập passphrase trực tiếp trong terminal đó. Chưa xác nhận keygen đã hoàn tất; chưa có thay đổi nào trên EVE-NG.

## Kiểm tra cặp SSH key cục bộ — 2026-10-31

- Private key C:\Users\ACER\.ssh\eve-ng-root-ed25519 tồn tại; metadata ghi nhận kích thước 464 byte. Nội dung không được mở/hiển thị.
- ACL private key chỉ cấp Allow cho: NT AUTHORITY\SYSTEM:FullControl; BUILTIN\Administrators:FullControl; LAPTOP-490FGEI5\ACER:Modify, Synchronize. Owner: LAPTOP-490FGEI5\ACER.
- Public key C:\Users\ACER\.ssh\eve-ng-root-ed25519.pub tồn tại và được ssh-keygen -lf xác nhận hợp lệ. Fingerprint công khai: SHA256:NmKKtOy8jUJd/x2Zg9xzrdGLCRAHCFfdNejRnrJ+ne4.
- Chưa sao chép public key vào EVE-NG; chưa tạo /root/.ssh, chưa tạo/backup/sửa uthorized_keys. Bước tiếp theo yêu cầu người dùng dán public key vào PuTTY; sau đó xác minh SSH qua Plink/Pageant.

## Cập nhật cài đặt public key — 2026-10-31

Người quản trị đã tạo `/root/.ssh` mode 700 (`root:root`) và `/root/.ssh/authorized_keys` mode 600 (`root:root`) trong phiên PuTTY. `authorized_keys` chưa tồn tại trước đó nên không cần sao lưu file cũ. Theo transcript được cung cấp, heredoc kết thúc mà không có public-key line ở phần thân; `ssh-keygen -lf` trả về “is not a public key file”. Do đó public key chưa được cài đặt/xác nhận và chưa thực hiện thử SSH bằng khóa. Cần nối thêm đúng dòng từ file Windows `.pub`, rồi xác nhận fingerprint trước khi thử kết nối.

## Xác minh public key cục bộ trước kết nối — 2026-10-31

- Public key cục bộ hợp lệ, loại ED25519; fingerprint: `SHA256:NmKKtOy8jUJd/x2Zg9xzrdGLCRAHCFfdNejRnrJ+ne4`.
- Private key tồn tại; nội dung không được đọc/hiển thị. ACL chỉ cho phép `LAPTOP-490FGEI5\ACER`, `SYSTEM` và `Administrators`.
- Pageant chưa chạy trước thao tác này. Đã mở Pageant với đường dẫn private key để người dùng nhập passphrase trực tiếp trong hộp thoại. Chưa xác minh key đã được nạp, chưa thử kết nối và chưa chạy lệnh kiểm tra trên EVE-NG.

# Kết quả hoàn tất kiểm tra SSH và inventory chỉ đọc — 2026-10-31

## Xác thực SSH

- Windows OpenSSH đã đăng nhập thành công đến `root@192.168.220.143` bằng khóa `eve-ng-root-ed25519`; output có marker `SSH_PUBLIC_KEY_AUTHENTICATED`.
- Fingerprint remote trong `/root/.ssh/authorized_keys`: `SHA256:NmKKtOy8jUJd/x2Zg9xzrdGLCRAHCFfdNejRnrJ+ne4` (ED25519), khớp public key trên Windows.
- Quyền remote: `/root/.ssh` là `700 root:root`; `/root/.ssh/authorized_keys` là `600 root:root`. File có 2 dòng tổng cộng; ssh-keygen xác nhận key hợp lệ. Trước khi thêm key file chưa tồn tại, nên không có key cũ để sao lưu.
- Private key nằm ngoài dự án tại `%USERPROFILE%\.ssh\eve-ng-root-ed25519`, được bảo vệ bằng passphrase. Không đọc/hiển thị/lưu private key hoặc passphrase.
- Thay đổi EVE-NG duy nhất được thực hiện theo phê duyệt: tạo `/root/.ssh` và thêm public key vào `/root/.ssh/authorized_keys`. Không đổi `sshd_config`, không đổi thiết lập mật khẩu, không đổi VMware, image hoặc cấu hình mạng.

## Hệ thống EVE-NG

- Phiên bản: `eve-ng 6.2.0-4`.
- Hostname: `eve-ng`; kernel `6.7.5-eveng-6-ksm+`.
- CPU nhìn thấy từ EVE: 4 vCPU, x86_64, Intel 13th Gen Core i5-13420H; hai socket, hai core/socket theo `lscpu`.
- RAM: tổng 7.7 GiB; 1.4 GiB dùng, 6.0 GiB khả dụng; swap 4.0 GiB, chưa dùng.
- Phân vùng `/` và `/opt/unetlab`: 57 GiB tổng, 14 GiB dùng, 41 GiB trống (25% sử dụng).

## Image và template

| Thành phần | Bằng chứng | Đánh giá |
|---|---|---|
| Cisco IOSvL2 | Template `viosl2.yml` có ở `templates/intel` và `templates/amd`; không có file image QEMU trong `/opt/unetlab/addons/qemu`; IOL hiện liệt kê các image `i86bi-linux-l3-...`, không có image L2 trong truy vấn | Template có, image IOSvL2 không tìm thấy; chưa dùng được theo file hiện có |
| OPNsense | Template `opnsense.yml` có ở cả Intel và AMD; không tìm thấy file image QEMU | Template có, image không tìm thấy; chưa dùng được theo file hiện có |
| Ubuntu/Linux | Template generic `linux.yml` có ở cả Intel và AMD; không tìm thấy file image QEMU và không thấy template tên Ubuntu | Template Linux có, image Ubuntu/Linux không tìm thấy; chưa xác nhận có thể dùng |
| VPCS | Template `vpcs.yml` có ở cả Intel và AMD; package `eve-ng-vpcs` được cài và danh sách file package khai báo `/opt/vpcsu/bin/vpcs`. Không tìm thấy binary ở đường dẫn mặc định `/opt/unetlab/addons/bin/vpcs`; chưa xác minh trực tiếp file `/opt/vpcsu/bin/vpcs` có tồn tại và executable hay không | Template/package có; khả năng chạy chưa xác nhận |
| Dynamips | Không tìm thấy image file dưới `/opt/unetlab/addons/dynamips` trong truy vấn | Chưa có image được xác nhận |

Chưa bật node nên mọi đánh giá khả năng sử dụng là kiểm tra tĩnh dựa trên package, template, tên file và đường dẫn. Không thử runtime bằng cách khởi động node.

## Log minh chứng

- `eve-ng-readonly-ssh-20261031-130710.log`: xác thực thành công, phiên bản, RAM, đĩa, QEMU/IOL/Dynamips và danh sách template.
- `eve-ng-readonly-ssh-final-20261031-131039.log`: xác thực thành công, fingerprint/quyền `authorized_keys`, CPU và đường dẫn file VPCS theo package.
- `eve-ng-readonly-ssh-details-20261031-130940.log`: lần truy vấn bổ sung lỗi quoting từ Windows trước khi lệnh kiểm tra chạy; không có thông tin bí mật trong log. Kết quả hợp lệ được lấy ở log `final`.

Không có ảnh màn hình. Không tạo lab, không bật node, không tải/cài image, không chạy `fixpermissions`, không sửa cấu hình SSH ngoài việc thêm public key đã được phê duyệt.
