# CHƯƠNG 2. CHUẨN BỊ MÔI TRƯỜNG CORE LAYER 2

## 2.1. Mục tiêu và phạm vi kiểm chứng

Giai đoạn này kiểm tra khả năng khởi tạo và quản trị Ubuntu Server 24.04 trên EVE-NG trước khi triển khai Core Layer 2 bằng Open vSwitch (OVS). Đối tượng kiểm tra là node `Ubuntu-Console-Test`, ID 2, trong lab `SOC-Ubuntu-Image-Test`. EVE-NG được truy cập tại `192.168.220.143`; đây là địa chỉ quản trị EVE đã sử dụng thực tế, không phải địa chỉ gateway của các VLAN trong đồ án.

Người quản trị đã xác nhận đăng nhập console bằng tài khoản `soc-test`. Trong phiên thu thập minh chứng, các lệnh chỉ đọc được thực hiện tại shell đã đăng nhập của chính node này. Hoạt động chỉ gồm đọc trạng thái, chụp framebuffer console thật và ghi tài liệu trên Windows; không cài OVS, sửa mạng, thay seed/image, dừng hoặc khởi động node. Tài liệu này là phần báo cáo M2 về chuẩn bị hệ điều hành, chưa phải biên bản nghiệm thu Core chuyển mạch.

Ảnh được thu trực tiếp từ framebuffer VNC của QEMU qua phiên SSH có kiểm tra host key. Mỗi ảnh giữ toàn bộ màn hình 720 × 400 pixel, không ghép, không cắt, không sửa nội dung. Thao tác Ctrl+L trước ảnh chính chỉ làm mới màn hình terminal thật rồi chạy lại lệnh kiểm tra; không sửa ảnh sau khi chụp. Log JSON cùng tên ảnh ghi node UUID, tiến trình QEMU, lệnh đã gửi, thời điểm và SHA-256 của ảnh.

## 2.2. Kết quả kiểm tra cloud-init

Lệnh `cloud-init status --long` được sử dụng để kiểm tra trạng thái khởi tạo trong guest. Ảnh được chọn cho báo cáo được thu từ 18:43:35 đến 18:43:42 ngày 31/10/2026, UTC+07:00, theo đồng hồ máy thu thập Windows.

![Kết quả cloud-init thực tế](../evidence/M2/M2-cloud-init-success-20261031T184335+0700.png)

**Hình 2.1. Kết quả kiểm tra trạng thái cloud-init trên Ubuntu Server 24.04**

Mục đích của Hình 2.1 là xác định cloud-init đã hoàn tất trong máy Ubuntu, thay vì chỉ suy luận từ việc CD-ROM đã được gắn trên EVE-NG. Nội dung hình thể hiện lệnh thực tế, các trường trạng thái và dấu nhắc shell của `soc-test` trên hostname `soc-ubuntu-console-test`.

| Nội dung kiểm tra | Kết quả thực tế | Đánh giá |
|---|---|---|
| `status` | `done` | Đã hoàn tất |
| `extended_status` | `done` | Đã hoàn tất |
| `boot_status_code` | `enabled-by-generator` | Trường trạng thái quan sát được |
| `detail` | `DataSourceNoCloud [seed=/dev/sr0]` | Đã nhận nguồn NoCloud từ CD-ROM |
| `errors` | `[]` | Không liệt kê lỗi |
| `recoverable_errors` | `{}` | Không liệt kê lỗi có thể phục hồi |
| Tài khoản sử dụng | Shell `soc-test`; lệnh `whoami` ở Hình 2.2 trả về `soc-test` | Đăng nhập được xác nhận |

Kết quả cho phép xác nhận cloud-init đã hoàn tất thành công theo báo cáo trạng thái của guest, nguồn dữ liệu NoCloud được nhận từ `/dev/sr0` và tài khoản quản trị thử nghiệm có thể sử dụng console. Ý nghĩa đối với Core Layer 2 là nền hệ điều hành có thể được quản trị và tiếp tục chuẩn bị cho OVS. Kết quả này chưa chứng minh OVS đã được cài, chuyển mạch VLAN/trunk hoạt động, mirror hoạt động hoặc firewall HA đã được kiểm thử. Cách diễn giải trạng thái dựa trên tài liệu chính thức về [CLI cloud-init](https://docs.cloud-init.io/en/latest/reference/cli.html) và [reported status](https://docs.cloud-init.io/en/latest/howto/status.html).

Trường `last_update` trong ảnh ghi `Thu, 01 Jan 1970 00:03:33 +0000`; không sử dụng trường này làm thời điểm thu thập minh chứng. Đồng hồ EVE cũng báo `NTPSynchronized=no` và lệch so với máy thu thập. Thời điểm ảnh được ghi riêng theo Windows, chuyển sang UTC+07:00; chưa hiệu chỉnh đồng hồ của bất kỳ hệ thống nào. Mã thoát của lệnh chưa được thu riêng; kết luận dựa trên các trường trạng thái và ảnh, không suy diễn đã đo mã thoát bằng 0.

## 2.3. Kiểm tra hostname, NIC, CPU và RAM

![Thông tin hệ thống Ubuntu thực tế](../evidence/M2/M2-ubuntu-system-info-20261031T184400+0700.png)

**Hình 2.2. Kết quả kiểm tra hostname, giao diện mạng và tài nguyên của node Ubuntu**

Mục đích của Hình 2.2 là đối chiếu cấu hình máy ảo do EVE/QEMU cấp với tài nguyên và tên giao diện mà Ubuntu nhận diện. Hình ghi lại lần lượt các lệnh `hostname`, `ip -br link`, `nproc`, `free -m`, `whoami` và `cloud-id`. Kết quả xác nhận khả năng quản trị guest, nhận diện cổng thử nghiệm và thiết lập đường cơ sở tài nguyên; chưa xác nhận khả năng chịu tải khi chuyển tiếp lưu lượng SOC.

| Thông số | Kết quả xác minh | Nguồn và giới hạn |
|---|---|---|
| Hostname | `soc-ubuntu-console-test` | `hostname`; ảnh ban đầu còn có `hostnamectl` |
| Hệ điều hành | Ubuntu 24.04.5 LTS, x86-64 | `hostnamectl` trên ảnh `M2-console-initial-20261031T184136+0700.png` |
| NIC Ethernet trong guest | `ens3`, MAC `00:50:00:00:02:00`, trạng thái `UP` | `ip -br link`; ngoài ra có `lo` là loopback, không phải NIC nối topology |
| Liên kết ra topology | Chưa kết nối | XML lab không có network object/interface nối mạng; TAP `vunl0_2_0` không có bridge master |
| CPU cấu hình | 1 vCPU | XML `cpu=1` và QEMU `-smp 1` |
| CPU khả dụng cho tiến trình kiểm tra | `nproc` trả về `1` | Phù hợp CPU cấu hình; không phải phép đo hiệu năng |
| RAM cấu hình | 2048 MiB | XML `ram=2048` và QEMU `-m 2048` |
| RAM guest nhìn thấy | Tổng 1967 MiB; available 1664 MiB tại lúc chụp | `free -m`; nhỏ hơn RAM cấu hình do phần bộ nhớ dành riêng cho hệ thống; số available biến đổi theo thời điểm |
| Swap | Tổng 0 MiB trong guest | `free -m`; không nhầm với swap của EVE host |
| Datasource | `cloud-id` trả về `nocloud` | Kiểm tra bổ sung trong guest |

NIC là Network Interface Card, tức giao diện mạng; vNIC là giao diện mạng ảo do QEMU cung cấp. CPU là Central Processing Unit, tức bộ xử lý trung tâm; vCPU là bộ xử lý ảo cấp cho guest. RAM là Random Access Memory, tức bộ nhớ truy cập ngẫu nhiên. Các thành phần này lần lượt cung cấp cổng chuyển tiếp, năng lực xử lý và bộ nhớ làm việc cho Core dự kiến; phép kiểm tra hiện tại xác nhận tài nguyên được nhận diện, chưa đánh giá thông lượng hoặc độ trễ.

Trạng thái `UP` của `ens3` không chứng minh có đường tới Internet, gateway hoặc một VLAN đã triển khai. Trong EVE, NIC hiện vẫn chưa nối vào topology. Tên `ens3` chỉ được xác nhận cho một NIC hiện tại; không tự gán `ens4`, `eth0` hoặc tên tiếp theo cho các NIC chưa được thêm.

Có thể tái kiểm tra bằng các lệnh chỉ đọc dưới đây. `hostnamectl` cho biết nhận dạng hệ thống; `ip -br link` liệt kê giao diện; `nproc` và `lscpu` kiểm tra CPU; `free -m` kiểm tra RAM; hai lệnh cuối kiểm tra người dùng và datasource. `lscpu` là hướng dẫn bổ sung, chưa được thực hiện trong lần chụp này.

```sh
hostnamectl
ip -br link
nproc
lscpu
free -m
whoami
cloud-id
```

## 2.4. Đề xuất số lượng NIC cho Core Open vSwitch

### 2.4.1. Cơ sở tính toán

OVS, tên đầy đủ Open vSwitch, là bộ chuyển mạch ảo mã nguồn mở. Trong thiết kế này, OVS dự kiến chuyển tiếp frame theo địa chỉ MAC và phân tách các miền Layer 2 bằng VLAN; toàn bộ gateway, định tuyến liên VLAN, firewall rules và NAT do OPNsense đảm nhiệm. SOC là Security Operations Center, tức trung tâm điều hành an ninh mạng; Core cung cấp đường truyền giữa các vùng và bản sao lưu lượng cho bộ phận giám sát của SOC, không thay firewall.

VLAN là Virtual Local Area Network, tức mạng cục bộ ảo, tạo các miền quảng bá riêng trên hạ tầng chuyển mạch. Cổng access nối thiết bị đầu cuối vào một VLAN; trunk mang lưu lượng của nhiều VLAN bằng thẻ IEEE 802.1Q. Trong topology đồ án, một trunk đến OPNsense có thể mang VLAN 30/40/50/60/99, không cần năm NIC trunk riêng cho năm VLAN. Việc bố trí năm NIC access dưới đây xuất phát từ năm kết nối endpoint dự kiến, không phải quy tắc bắt buộc một NIC cho mỗi VLAN. [Tài liệu cấu hình OVS](https://docs.openvswitch.org/en/stable/faq/configuration/).

Đối chiếu [port map M1](../../network/core-l2/port-mapping.md), [kế hoạch địa chỉ](../../network/ip-plan/vlan-ip-plan.md), [phương án M2](deployment-options.md) và AGENTS hiện hành: M1 có hai trunk tới firewall, bốn access và một mirror; AGENTS xác định thêm vùng DMZ VLAN 60, nên đề xuất dưới đây bổ sung một access DMZ. Những mô tả cũ gọi DMZ là tùy chọn không thay thế quy định VLAN hiện hành.

### 2.4.2. Phương án khuyến nghị: 8 vNIC

| Nhãn logic đề xuất | Số vNIC | Vai trò | Trạng thái |
|---|---|---|---|
| Access Data Center | 1 | Endpoint VLAN 30 | Chưa triển khai |
| Access Employee | 1 | Endpoint VLAN 40 | Chưa triển khai |
| Access Guest | 1 | Endpoint VLAN 50 | Chưa triển khai |
| Access DMZ | 1 | Endpoint VLAN 60 | Chưa triển khai |
| Access Management | 1 | Endpoint/mạng quản trị VLAN 99 | Chưa triển khai |
| Trunk OPNsense Primary LAN | 1 | Dự kiến mang VLAN 30/40/50/60/99 | Dự trữ cho M3; chưa xác minh cổng peer |
| Trunk OPNsense Secondary LAN | 1 | Dự kiến mang VLAN 30/40/50/60/99 | Dự trữ cho M3; chưa xác minh cổng peer |
| Mirror output | 1 | Xuất bản sao lưu lượng tới NIC capture của Suricata | Chưa chốt nguồn/hướng mirror hoặc peer |
| **Tổng** | **8** | **5 access + 2 trunk + 1 mirror** | **Đề xuất, chưa đổi NIC** |

Port mirroring là cơ chế sao chép frame được chọn sang cổng giám sát; SPAN là Switched Port Analyzer, tên thường dùng trong hệ sinh thái Cisco cho chức năng giám sát tương tự. Trong đồ án, cổng mirror dự kiến đưa bản sao tới Suricata, công cụ phân tích lưu lượng để phát hiện xâm nhập. Cổng mirror không thay cổng quản trị của cảm biến và không được tính như đường chuyển tiếp endpoint bình thường. Phạm vi nguồn, hướng ingress/egress và khả năng quan sát khi firewall chuyển vai trò cần chốt ở bước thiết kế tiếp theo. [OVS mirroring](https://docs.openvswitch.org/en/stable/faq/configuration/).

Phương án 8 vNIC giữ sẵn hai đường firewall cho HA (High Availability, tính sẵn sàng cao), tức khả năng tiếp tục cung cấp dịch vụ khi một thành phần gặp sự cố. Hai trunk tới Primary và Secondary là hai kết nối riêng, **không gộp thành LACP xuyên qua hai firewall**. LACP (Link Aggregation Control Protocol, giao thức điều khiển gộp liên kết) cần peer hỗ trợ và các link cùng nhóm được thiết kế phù hợp; LACP chưa thuộc kết quả kiểm chứng này.

### 2.4.3. Phương án tối giản và khả năng mở rộng

- M2 tạm chỉ giữ một trunk, năm access và một mirror thì cần 7 vNIC; phương án này chưa có kết nối riêng tới firewall thứ hai như M1. Khuyến nghị chọn 8 để chuẩn bị cho M3.
- Quản trị Core có thể thiết kế qua OVS internal interface thuộc VLAN 99, không nhất thiết thêm một vNIC. Đây là đề xuất, chưa gán IP. Nếu chọn NIC quản trị riêng thì tổng tăng lên 9 và cần xác định segment quản trị trước khi nối.
- Kiểm thử dương hai endpoint cùng VLAN phải đi qua hai cổng OVS khác nhau. Có thể xin thêm một cổng test (tổng 9 nếu giữ tám vai trò trên), hoặc xin tạm bố trí lại một cổng access chưa dùng. Không nối cả hai endpoint vào cùng bridge EVE rồi coi ping thành công là bằng chứng đã đi qua Core.
- Nếu giữ nguyên tám vai trò và bổ sung riêng một bài thử LACP hai link thì cần thêm hai vNIC, tổng 10. Số lượng có thể khác nếu tái sử dụng cổng; chưa chốt peer hoặc triển khai.
- Trước khi tăng NIC, cần kiểm tra khả năng template, số cổng GUI/API cho phép, PCI/QEMU và tên NIC thực tế sau khi thay đổi được phê duyệt. Chưa khẳng định template đã chạy thành công với 8, 9 hoặc 10 NIC.

Không có số cổng Ethernet mới, địa chỉ IP, subnet, VIP hoặc native VLAN nào được xác nhận chính thức bởi đề xuất này. Chưa thay đổi NIC của `Ubuntu-Console-Test` hoặc quyết định chuyển node kiểm thử thành Core. WAN và đường đồng bộ HA của OPNsense không tự động nối qua Core VLAN người dùng trong đề xuất tính NIC này.

## 2.5. Giải thích các thuật ngữ nền tảng

### 2.5.1. cloud-init

**Tên và nghĩa:** `cloud-init` là tên chính thức của công cụ khởi tạo tự động instance; không phải từ viết tắt cần tự tạo một tên khai triển. Có thể diễn giải tiếng Việt là công cụ thiết lập ban đầu máy chủ/máy ảo.

**Nguyên lý:** trong quá trình boot, công cụ nhận diện datasource, đọc dữ liệu khởi tạo và chạy các module tương ứng, chẳng hạn tạo user hoặc đặt hostname. Cấu hình phụ thuộc dữ liệu cung cấp và tần suất module; không giả định mọi module chạy lại ở mọi lần reboot. [Giới thiệu cloud-init](https://docs.cloud-init.io/en/latest/explanation/introduction.html).

**Vai trò và ví dụ:** trong SOC, công cụ giúp chuẩn hóa nền Ubuntu để người quản trị có thể tiếp tục chuẩn bị Core. Tại node đang kiểm tra, trạng thái `done` cùng tài khoản `soc-test` sử dụng được là kết quả đã xác minh. Việc cài OVS thông qua cloud-init là khả năng kỹ thuật, chưa được cấu hình hoặc cho phép thực hiện ở đây.

### 2.5.2. NoCloud

**Tên và nghĩa:** `NoCloud` là tên một datasource của cloud-init, không phải tên viết tắt. Trong trường hợp này có thể diễn giải là phương thức cung cấp dữ liệu khởi tạo cục bộ không cần dịch vụ cloud metadata qua mạng.

**Nguyên lý:** với đĩa seed cục bộ, cloud-init nhận diện filesystem có nhãn `CIDATA`/`cidata` và đọc đúng các tệp `user-data`, `meta-data` ở thư mục gốc. Metadata có `instance-id` để nhận dạng instance. NoCloud còn có các cách cấp dữ liệu khác; kết quả hiện tại chỉ xác nhận cách dùng CD-ROM. [NoCloud](https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html).

**Vai trò và ví dụ:** phương thức này phù hợp bootstrap node SOC đang cô lập, chưa có mạng. `DataSourceNoCloud [seed=/dev/sr0]` và `cloud-id` trả về `nocloud` xác nhận guest hiện tại đã nhận nguồn đó; không suy rộng kết quả sang seed/node cũ.

### 2.5.3. Datasource

**Tên và nghĩa:** Data Source, thường viết liền là `datasource`, nghĩa là nguồn dữ liệu cấu hình; không có chữ viết tắt bắt buộc trong ngữ cảnh này.

**Nguyên lý:** datasource là lớp cung cấp dữ liệu mà cloud-init sử dụng để nhận metadata và user-data, có thể từ nền tảng cloud hoặc nguồn cục bộ. Nó xác định nơi và cách lấy dữ liệu, không đồng nghĩa với file cấu hình cụ thể. [Datasources](https://docs.cloud-init.io/en/latest/reference/datasources.html).

**Vai trò và ví dụ:** trong quá trình chuẩn bị SOC, nhận đúng datasource giúp tránh trường hợp Ubuntu boot được nhưng thiếu user hoặc hostname mong muốn. Ở node hiện tại, datasource là NoCloud, thiết bị seed là `/dev/sr0`, còn hostname và tài khoản là các giá trị được kiểm tra riêng trong guest.

### 2.5.4. Seed ISO

**Tên và nghĩa:** Seed ISO, tức ảnh đĩa mồi khởi tạo dạng ISO 9660. Đây là cụm mô tả phương tiện chứa cấu hình, không phải tên một giao thức mạng.

**Nguyên lý:** QEMU gắn tệp ISO như CD-ROM; guest nhìn thấy thiết bị quang ảo. Dữ liệu bên trong cung cấp chỉ dẫn khởi tạo cho datasource. Với NoCloud, cần bảo đảm nhãn đĩa và tên file mà guest đọc được; tên file nguồn có đuôi `.yaml` trên host không thay thế yêu cầu tên trong ISO. [Ubuntu: dùng datasource cục bộ](https://ubuntu.com/docs/public-images/public-images-how-to/use-local-cloud-init-ds/).

**Vai trò và ví dụ:** seed riêng giúp bootstrap tài khoản quản trị cho node thử nghiệm mà không sửa image Ubuntu gốc hoặc seed của node khác. QEMU đang gắn `linux-ubuntu-24.04-soc-console-test/cdrom.iso`; kết quả `/dev/sr0` xác nhận guest dùng đĩa seed. Không công bố nội dung hash mật khẩu hoặc các dữ liệu nhạy cảm trong báo cáo.

### 2.5.5. QEMU

**Tên và nghĩa:** QEMU thường được diễn giải là Quick Emulator, bộ giả lập/ảo hóa máy tính. Tên chính thức của dự án là QEMU. [Thuật ngữ NIST](https://csrc.nist.gov/glossary/term/QEMU).

**Nguyên lý:** QEMU tạo mô hình máy gồm CPU, RAM, thiết bị mạng và ổ đĩa để chạy hệ điều hành khách. Khi kết hợp KVM (Kernel-based Virtual Machine, cơ chế ảo hóa trong nhân Linux), nó có thể sử dụng hỗ trợ ảo hóa phần cứng. [QEMU system emulation](https://www.qemu.org/docs/master/system/introduction.html).

**Vai trò và ví dụ:** QEMU là lớp chạy máy Ubuntu làm nền cho Core SOC dự kiến. Tiến trình được quan sát là `/opt/qemu-2.12.0/bin/qemu-system-x86_64`, cấp `-smp 1`, `-m 2048`, NIC VirtIO và `accel=kvm`. Đây là tham số chạy đã đọc, không phải lệnh khởi tạo mới hoặc bằng chứng OVS đã tồn tại.

### 2.5.6. QCOW2

**Tên và nghĩa:** QEMU Copy-On-Write version 2, tức định dạng ảnh đĩa QEMU dùng cơ chế sao chép khi ghi thuộc họ QCOW2. Tên định dạng không được dùng để suy luận rằng header luôn mang version 2. [QEMU glossary](https://www.qemu.org/docs/master/glossary.html), [đặc tả QCOW2](https://www.qemu.org/docs/master/interop/qcow2.html).

**Nguyên lý:** khi dùng backing file, dữ liệu chưa thay đổi được đọc từ lớp nền; dữ liệu mới được ghi vào overlay. Overlay vẫn phụ thuộc backing file, nên không phải bản sao đầy đủ độc lập. Các lớp phải được giữ nguyên hoặc xử lý bằng quy trình được phê duyệt. [QEMU disk images](https://www.qemu.org/docs/master/system/images.html).

**Vai trò và ví dụ:** QCOW2 cho phép thử nghiệm nền Ubuntu mà giữ base của đồ án. Chuỗi đã được kiểm tra ở phiên khôi phục là runtime overlay của node 2 → variant `linux-ubuntu-24.04-soc-console-test/virtioa.qcow2` → base `linux-ubuntu-24.04-ovs/virtioa.qcow2`. Phiên này chỉ đọc đường runtime từ tiến trình, không chạy kiểm tra sửa chữa ổ đĩa hoặc thay backing chain.

### 2.5.7. Console

**Tên và nghĩa:** System Console, tức giao diện điều khiển trực tiếp hệ thống; không có từ viết tắt bắt buộc. Trong node này, Ubuntu sử dụng virtual console/TTY, được hiển thị qua VGA ảo của QEMU và truy cập bằng VNC (Virtual Network Computing).

**Nguyên lý:** bàn phím và màn hình ảo cho phép tương tác với guest mà không cần NIC guest có địa chỉ IP. Đường console khác với SSH (Secure Shell, giao thức quản trị từ xa có mã hóa), vốn cần một đường mạng tới hệ thống đích. Linux phân biệt virtual console với serial console; không gọi VGA/VNC hiện tại là serial console. [Linux console](https://docs.kernel.org/admin-guide/serial-console.html), [QEMU invocation](https://www.qemu.org/docs/master/system/invocation.html).

**Vai trò và ví dụ:** console cung cấp đường bootstrap và kiểm tra Core khi mạng chưa được cấu hình. Tại đây, `soc-test` đăng nhập và chạy `cloud-init status --long` trên console thật. SSH chỉ dùng để vào EVE và vận chuyển dữ liệu chụp, không chứng minh đã SSH vào Ubuntu.

## 2.6. Phân loại kết quả và vấn đề còn tồn tại

| Hạng mục | Phân loại | Kết luận |
|---|---|---|
| Guest boot, console và user `soc-test` | Đạt, đã xác minh | Có shell thực tế và kết quả `whoami` |
| Cloud-init/NoCloud | Đạt, đã xác minh | `done`, không liệt kê lỗi, seed `/dev/sr0` |
| Hostname/NIC/CPU/RAM hiện tại | Đạt về nhận diện | Có ảnh và đối chiếu XML/QEMU |
| Tăng lên 8 vNIC | Đề xuất | Chưa thay node, chưa xác minh giới hạn hoặc tên NIC bổ sung |
| Cài đặt và dịch vụ OVS | Chưa nghiệm thu | Không cài trong phiên này; chưa chạy kiểm kê package/dịch vụ guest |
| VLAN access/trunk, mirror | Chưa kiểm thử | Chưa có cấu hình hoặc lưu lượng thử nghiệm |
| IP, subnet, số cổng hai đầu | Chưa xác nhận | Các giá trị M1 tiếp tục là đề xuất |
| SSH vào guest | Chưa kiểm thử | Console thành công không thay cho SSH thành công |
| Đồng hồ hệ thống | Còn tồn tại | `last_update` năm 1970 và EVE NTP chưa đồng bộ; chưa sửa |
| Hoàn tất toàn bộ M2 | Chưa đạt | Mới hoàn thành bước chuẩn bị hệ điều hành |

Trong lần thu thập đầu, chuỗi phím cho biến `_NPROCESSORS_ONLN` bị console nhận sai thành dấu gạch ngang nên `getconf` báo lỗi; không dùng lần đó để kết luận CPU. Lần kiểm tra sau dùng `nproc`, trả về `1` và được đối chiếu với QEMU. Một ảnh ban đầu chụp trước khi output cloud-init được vẽ xong nên chưa đủ minh chứng dù tên file chứa `success`. Các ảnh và JSON này được giữ nguyên, phân loại rõ trong danh mục; Hình 2.1 và 2.2 chỉ dùng hai ảnh chính đã đọc kiểm tra.

## 2.7. Bước tiếp theo cần phê duyệt

1. Chốt phương án 8 vNIC, mục đích từng cổng, peer kiểm thử trunk/mirror, cách kiểm thử hai endpoint cùng VLAN và lựa chọn node sẽ làm Core. Giữ nguyên các node cũ và không mặc định biến node kiểm thử thành Core.
2. Nếu cần tăng NIC hoặc chuẩn bị node Core, phê duyệt rõ thao tác trên node đích và việc dừng/khởi động lại nếu EVE yêu cầu. Chỉ sau thay đổi được duyệt mới đối chiếu NIC theo MAC, tên guest và cổng EVE.
3. Phê duyệt riêng kế hoạch cài `openvswitch-switch` trong guest, gồm đường cung cấp package. Guest đang cô lập, chưa có đường tải gói được xác nhận; không tự nối pnet/NAT/Internet hoặc sửa seed để cài gói.
4. Phê duyệt cấu hình chuyển mạch Layer 2 và mạng kiểm thử trước khi triển khai VLAN/trunk/mirror. Core không tạo gateway liên VLAN, firewall/NAT; các chức năng đó ở OPNsense.

## 2.8. Tài liệu và khả năng đưa vào Word

Tài liệu Markdown này là bản nội dung báo cáo có thể tái sử dụng. Bản `.docx` cùng tên chứa ảnh thật, chú thích phía dưới và bảng kết quả, dùng A4, Times New Roman 13, lề trái 3 cm, các lề khác 2 cm. Số chương/mục và Hình 2.1–2.2 được ghi rõ; khi ghép vào luận văn đầy đủ cần đối chiếu mục lục và số hình chung. Danh mục minh chứng, log chép kết quả và JSON gốc của bộ thu thập nằm trong `docs/evidence/M2/`; minh chứng cũ tại `docs/evidence/eve-ng/` được giữ nguyên.

Các nguồn chính thức được dẫn ngay tại nội dung liên quan; ngày truy cập 31/10/2026. Tài liệu online giải thích nguyên lý, không xác nhận phiên bản cloud-init hoặc tính năng OVS của guest hiện tại. Ảnh và JSON mới là căn cứ cho các kết quả thực nghiệm.
