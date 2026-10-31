# Đánh giá mức sẵn sàng image EVE-NG cho M2/M3

- **Ngày kiểm tra:** 2026-10-31 (Asia/Ho_Chi_Minh)
- **EVE-NG:** Community 6.2.0-4 (đã xác nhận qua kiểm tra SSH trước đó)
- **Phạm vi:** kiểm kê chỉ đọc file image, template, package và tài nguyên; không bật node, không tải/cài file, không sửa EVE-NG.
- **Log kiểm kê đầy đủ:** [eve-ng-image-inventory-20261031-132538.log](eve-ng-image-inventory-20261031-132538.log). Log chứa danh sách chính xác mọi file `.bin` IOL, QEMU, Dynamips và toàn bộ file template `.yml` ở cả `intel` và `amd`.

## Kết luận

Hiện có template cho IOSvL2, OPNsense, Linux và VPCS, nhưng template chỉ là định nghĩa node. Trong thư mục image không có file QEMU hoặc Dynamips. Các file IOL hiện có là các biến thể L3 theo metadata/tên file; không có file IOL L2 được liệt kê. Vì vậy chưa có image Core Layer 2 nào được xác nhận để triển khai M2 trong EVE-NG.

VPCS khác với các image trên: package và binary thực tế có mặt, binary ELF x86-64 có bit thực thi. Có thể dùng làm endpoint kiểm thử ở mức tĩnh; chưa chạy node nên chưa xác nhận runtime. Quyền binary hiện là `777 root:root` (mọi người dùng có quyền ghi); không thay đổi trong đợt kiểm tra, cần quản trị viên xem xét trước khi sử dụng.

## Danh sách image hiện có

### IOL

| File | Loại thiết bị theo metadata | Kích thước | Trạng thái |
|---|---|---:|---|
| `i86bi-linux-l3-jk9s-15.0.1.bin` | IOL L3 | 63,112,556 bytes | Có file, executable; chưa boot/test |
| `i86bi-linux-l3-p-15.0a.bin` | IOL L3 | 48,668,664 bytes | Có file, executable; chưa boot/test |
| `i86bi-linux-l3-p-15.0b.bin` | IOL L3 | 48,668,664 bytes | Có file, executable; chưa boot/test |
| `i86bi-linux-l3-tpgen-adventerprisek9-12.4.bin` | IOL L3 / biến thể có tên tpgen | 99,422,572 bytes | Có file, executable; chưa boot/test |
| `i86bi-linux-l3-tpgen-ipbase-12.4.bin` | IOL L3 / biến thể có tên tpgen | 50,091,604 bytes | Có file, executable; chưa boot/test |

Không có file IOL L2 trong danh sách. Không đọc nội dung `iourc`/file license. Dù file nằm trong thư mục IOL, khả năng khởi chạy còn phụ thuộc template, license hợp lệ và kiểm thử; đợt kiểm tra không xác thực license.

### QEMU và Dynamips

- **QEMU:** không tìm thấy file image trong `/opt/unetlab/addons/qemu` ở độ sâu kiểm kê đến 3 cấp.
- **Dynamips:** không tìm thấy file image trong `/opt/unetlab/addons/dynamips` ở độ sâu kiểm kê đến 3 cấp.

Do đó hiện không có file IOSvL2, OPNsense hoặc Ubuntu/Linux để ghép với các template tương ứng.

### VPCS

- Package: `eve-ng-vpcs 6.1-eve-ng`.
- Binary: `/opt/vpcsu/bin/vpcs`, ELF 64-bit x86-64, tồn tại và có bit executable.
- Quyền hiện tại: `777 root:root` — không được thay đổi trong phạm vi kiểm tra.
- Template `vpcs.yml` có ở cả `intel` và `amd`.
- **Đánh giá:** sẵn sàng tĩnh làm máy đầu cuối VPCS để thử IP/ping/kết nối cơ bản, nhưng chưa bật node để kiểm tra runtime. VPCS không thay thế switch, firewall hay máy Ubuntu đầy đủ.

## Template hiện có

| Template | Intel | AMD | Ý nghĩa | Image đi kèm |
|---|---:|---:|---|---|
| `viosl2.yml` | Có | Có | Định nghĩa node switch IOSvL2 | Không tìm thấy |
| `opnsense.yml` | Có | Có | Định nghĩa node OPNsense | Không tìm thấy |
| `linux.yml` | Có | Có | Định nghĩa Linux tổng quát | Không tìm thấy |
| `vpcs.yml` | Có | Có | Định nghĩa endpoint VPCS | Package/binary được tìm thấy; runtime chưa thử |
| `ubuntu.yml` | Không thấy | Không thấy | Template Ubuntu riêng | Không tìm thấy |

Các template khác được liệt kê đầy đủ trong log kiểm kê liên kết ở đầu tài liệu. Template có mặt không đồng nghĩa image cùng loại đã cài hoặc node có thể chạy.

## Kiểm chứng tính năng L2

| Image/candidate | L2 switching | VLAN / 802.1Q trunk | SPAN | LACP | Kết luận cho Core M2 |
|---|---|---|---|---|---|
| Các IOL hiện có | Chưa xác nhận; metadata nhận diện chúng là biến thể L3, không có IOL L2 được cài | Chưa thử; không suy ra từ tên file | Chưa thử | Chưa thử | Không chọn làm Core L2 khi chưa có bằng chứng runtime/feature |
| IOSvL2 của Cisco (chưa cài) | Cisco mô tả là switch L2 | Cisco liệt kê VLAN và 802.1Q trunk được hỗ trợ | Cisco nêu SPAN không được hỗ trợ | Cisco liệt kê Port-Channel với LACP/PAgP được hỗ trợ | Có thể dùng cho VLAN/trunk/LACP nếu có license hợp lệ, nhưng không đáp ứng SPAN của thiết kế M1 |
| Open vSwitch trên Linux (phương án thay thế, chưa có image) | Software switch L2 | Có access/trunk 802.1Q | Có mirroring | Có bonding LACP | Phù hợp mô phỏng chức năng VLAN/trunk/LACP/SPAN; không tái tạo Cisco CLI/hành vi IOS |
| VPCS | Không phải switch | Không phải trunk switch | Không | Không | Chỉ làm endpoint kiểm thử |

Không khởi động image nào để thử CLI/traffic. Tài liệu Cisco ghi rõ IOSvL2 có L2 forwarding, VLAN/802.1Q và LACP, nhưng không hỗ trợ SPAN; đây là thông tin về tính năng của image, không phải bằng chứng rằng image đã có trên EVE-NG. [Tài liệu Cisco IOSvL2](https://developer.cisco.com/docs/modeling-labs/iosvl2/)

## Image còn thiếu và nguồn hợp pháp

### Ưu tiên 1: Core Layer 2

- Hiện thiếu image IOSvL2 hoặc một image switch L2 khác có entitlement rõ ràng.
- IOSvL2 có trong các image Cisco Modeling Labs; Cisco quy định image được cấp kèm CML chỉ được cấp phép sử dụng **bên trong CML**. Không lấy image từ mirror/diễn đàn hoặc trích xuất từ CML để đưa vào EVE-NG nếu không có quyền riêng cho cách sử dụng đó. [Cisco – giấy phép reference platform images](https://developer.cisco.com/docs/modeling-labs/vm-images-for-cml-labs/)
- Nếu bắt buộc dùng IOSvL2 cho đúng CLI Cisco, lựa chọn sạch nhất là chạy phần kiểm thử IOSvL2 trong CML với license phù hợp; hoặc chỉ dùng image từ Cisco Software Download khi entitlement của nhóm cho phép triển khai trên EVE-NG.
- Nếu toàn bộ lab phải nằm trong EVE-NG mà chưa có license phù hợp, dùng Ubuntu Server hợp pháp với Open vSwitch làm Core L2 thay thế. OVS hỗ trợ VLAN access/trunk, LACP và port mirroring theo tài liệu dự án; khác biệt là không có Cisco IOS CLI. [OVS features](https://docs.openvswitch.org/en/latest/intro/what-is-ovs/), [OVS VLAN/SPAN configuration](https://docs.openvswitch.org/en/stable/faq/configuration/)
- Lưu ý: ngay cả khi có IOSvL2, SPAN vẫn không có trong feature set theo tài liệu Cisco. Có thể dùng OVS cho mirror traffic, hoặc một switch thật/virtual image khác có SPAN và license hợp lệ.

### Ưu tiên 2: OPNsense HA

- Template `opnsense.yml` có sẵn nhưng QEMU disk image chưa có.
- Dùng OPNsense Community Edition từ trang tải chính thức; chọn `dvd` ISO amd64 để cài vào QEMU disk theo template EVE, rồi xác minh checksum/chữ ký theo tài liệu OPNsense. Không tải image đóng gói lại từ nguồn không rõ. [OPNsense Download](https://opnsense.org/download/), [hướng dẫn xác minh image](https://docs.opnsense.org/manual/install.html).
- Virtual disk tối thiểu khuyến nghị là 8 GB; OPNsense yêu cầu tối thiểu 3 GB RAM cho cài đặt ảo. [OPNsense virtual install](https://docs.opnsense.org/manual/virtuals.html)

### Ưu tiên 3: Linux/Ubuntu

- Có `linux.yml` generic nhưng không có QEMU image và không có template `ubuntu.yml` riêng.
- Có thể lấy Ubuntu Server/Cloud image từ Ubuntu/Canonical chính thức; dùng `linux.yml` hiện có sau khi xác nhận định dạng và yêu cầu disk của template. Ubuntu Cloud Images là image chính thức cho KVM/OpenStack và nền tảng ảo hóa. [Ubuntu Cloud Images](https://cloud-images.ubuntu.com/), [Ubuntu download](https://ubuntu.com/download).
- Không cần tải Linux riêng nếu chỉ dùng VPCS làm máy ping cơ bản; cần Ubuntu khi muốn cài Open vSwitch, Suricata agent, công cụ mạng hoặc ứng dụng đầy đủ.

## Ước tính tài nguyên cho lab

EVE-NG hiện có 4 vCPU và 7.7 GiB RAM khả dụng trong VM. Lần kiểm tra thấy khoảng 6.0 GiB RAM available, 41 GiB trống trên phân vùng 57 GiB. Đây là tải nền tại thời điểm kiểm tra; các node đang tắt.

| Giai đoạn | Sizing node tham khảo | Ước tính tổng node | Đánh giá trên EVE 4 vCPU / 8 GB |
|---|---|---:|---|
| M2: Core L2 + 2–4 VPCS | 1 switch khoảng 1 vCPU/1 GB; 2–4 VPCS khoảng 32–64 MB mỗi node | Khoảng 1.1–1.3 GB RAM, 1 vCPU | Khả thi về tài nguyên. Hiện thiếu image switch L2 hợp pháp trong EVE; có thể dùng OVS/Linux sau khi có Ubuntu image. |
| M3: một OPNsense + Core L2 + VPCS | OPNsense 3 GB RAM, 2 vCPU; switch 1 GB/1 vCPU; vài VPCS | Khoảng 4.1–4.3 GB RAM, 3 vCPU | Có thể chạy lab nhỏ nhưng sát giới hạn tài nguyên; cần tắt các node không dùng và theo dõi RAM. |
| M3: hai OPNsense HA + Core L2 + VPCS | Mỗi OPNsense tối thiểu 3 GB RAM; switch khoảng 1 GB; VPCS 0.1–0.3 GB | Khoảng 7.1–7.3 GB RAM node, 5 vCPU nếu cấp 2 vCPU/firewall | Không phù hợp với VM 8 GB: tổng node gần hết RAM trước overhead EVE/Linux; CPU cũng bị overcommit. |
| M3 HA thoải mái hơn | Hai OPNsense 3–4 GB mỗi node, switch 1 GB, clients | 7.2–9.3 GB RAM node | Nâng EVE VM lên **ít nhất 12 GB RAM và 6 vCPU**; **16 GB / 8 vCPU** thoải mái hơn nếu chạy thêm Suricata/Wazuh. |

OPNsense công bố 3 GB RAM/dual-core là mức tối thiểu cho full standard features, 4 GB là mức hợp lý và 8 GB là mức khuyến nghị cho một instance. Ước tính này dùng mức 3 GB tối thiểu mỗi firewall; không đại diện benchmark tải thật. [OPNsense hardware sizing](https://docs.opnsense.org/manual/hardware.html)

## Đề xuất chuẩn bị theo giai đoạn

1. **Trước M2:** quyết định có entitlement Cisco cho IOSvL2 dùng trong EVE-NG hay không. Nếu không, chốt OVS/Linux làm giải pháp L2 trong EVE và ghi rõ khác biệt so với Cisco. SPAN nên triển khai trên OVS hoặc switch khác có hỗ trợ.
2. **M2:** ưu tiên Core L2 và VPCS; chưa cần chạy OPNsense HA cùng lúc. Giữ Core không routing; VLAN/access/trunk thuộc switch, gateway vẫn dự kiến do OPNsense đảm nhiệm ở giai đoạn M3.
3. **Trước M3:** lấy OPNsense từ nguồn chính thức, xác minh checksum/chữ ký, dùng template đã có, bắt đầu với một firewall để kiểm tra interface/VLAN/DHCP/NAT. Đây là phương án chuẩn bị, chưa thực hiện trong lần kiểm tra này.
4. **HA:** trước khi bật hai OPNsense cùng lúc, nâng tài nguyên EVE hoặc chạy topology HA riêng. Không dựa vào cấp 2 GB cho mỗi firewall như phương án mặc định vì thấp hơn mức tối thiểu OPNsense công bố.
5. **VPCS:** binary có mặt nhưng mode `777` cần được quản trị viên đánh giá. Không sửa permission trong phạm vi kiểm kê này.

## Giới hạn kiểm tra

- Không bật node, vì vậy chưa xác nhận runtime/CLI, 802.1Q, LACP, SPAN, DHCP, HA hay hiệu năng.
- Không đọc file license IOL hoặc nội dung bí mật.
- Không tải/cài file, không sửa quyền, không chạy `fixpermissions`, không tạo lab.
- Phiên bản EVE-NG được đối chiếu từ log kiểm tra SSH trước đó; mục phiên bản ở log inventory mới bị trống do định dạng lệnh truy vấn package, không phải kết quả cho thấy thiếu phiên bản.
