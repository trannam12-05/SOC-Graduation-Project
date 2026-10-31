"""Luu bao cao M2 v2 va danh muc moi; khong ghi de minh chung cu/khong SSH."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence/M2'
S=ROOT/'staging/soc-core-l2-20261031-stage1'

def new_text(path,text):
    with path.open('x',encoding='utf-8',newline='\n') as target:target.write(text)
def new_json(path,data):new_text(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def copy_new(source,dest):
    with source.open('rb') as src,dest.open('xb') as out:shutil.copyfileobj(src,out)

def main():
    final=json.loads((E/'M2-core-stage1-final-status-20261031.json').read_text(encoding='utf-8'))
    node=final['core-created-stopped.json'];seed=final['seed-ready.json'];bundle=final['bundle-ready.json']
    packages=json.loads((S/'package-manifest.json').read_text(encoding='utf-8'))
    memory=json.loads((E/'M2-core-stage1-windows-memory-20261031.json').read_text(encoding='utf-8-sig'))
    copy_new(S/'package-manifest.json',E/'M2-core-stage1-package-manifest-20261031.json')
    copy_new(S/'metadata-manifest.json',E/'M2-core-stage1-metadata-manifest-20261031.json')
    new_json(E/'M2-core-stage1-image-node-config-20261031.json',node)
    new_json(E/'M2-core-stage1-seed-status-20261031.json',seed)
    new_json(E/'M2-core-stage1-bundle-validation-20261031.json',final['bundle-validated.json'])
    new_text(E/'M2-core-stage1-lab-20261031.unl',final['core_lab_xml'])
    redacted=json.loads((E/'M2-core-stage1-seed-redacted-20261031.json').read_text(encoding='utf-8'))
    new_text(E/'M2-core-stage1-network-config-20261031.yaml',redacted['network_config'])
    new_text(E/'M2-core-stage1-meta-data-20261031.yaml',redacted['meta_data'])
    columns=['Package','Version','Architecture','origins','Size','SHA256','download_url']
    with (E/'M2-core-stage1-packages-20261031.csv').open('x',encoding='utf-8-sig',newline='') as target:
        writer=csv.DictWriter(target,fieldnames=columns);writer.writeheader()
        for package in packages['packages']:
            writer.writerow({k:(';'.join(o['suite']+'/'+o['component'] for o in package['origins']) if k=='origins' else package[k]) for k in columns})
    safe_log=f'''SOC M2 - CORE STAGE 1 - 31/10/2026 UTC+07:00
Nguồn: thao tác SSH có kiểm tra host key, các JSON/ảnh thật đính kèm.
Đã được duyệt: chuẩn bị bundle, image mới, đĩa riêng 8 GiB, seed, node tắt 8 NIC.
Không được duyệt và chưa làm: boot Core, cài OVS guest, VLAN/trunk/mirror, sửa mạng.

Core image: {node['disk_info']['filename']}
QCOW2 virtual-size: 8589934592 bytes; không có backing-file.
Disk SHA256: {node['disk_sha256']}
Base SHA256 trước/sau: {node['base_sha256']}
qemu-img check: returncode 0, check-errors 0.
qemu-img compare với base: returncode 0, Images are identical.
Cảnh báo Image size mismatch là do 3.5 -> 8 GiB; vùng tăng thêm zero, không chứng minh rootfs đã grow.
Lab: {node['lab_path']}; lab UUID {node['lab_id']}.
Node SOC-Core-L2 ID3 / UUID {node['uuid']} / status0 stopped / CPU1 RAM2048MiB Ethernet8.
8 interface EVE e0-e7, MAC 02:53:45:f2:19:00..07, network_id=0, 0 network object, 0 link.
Core process không tồn tại, runtime overlay chưa được tạo; guest NIC names chưa kiểm chứng.

Sự cố kiểm tra trạng thái: ID1 ban đầu trong lab mới bị EVE getStatus suy ra console port
trùng Ubuntu-Test ID1 đang chạy. Assertion dừng; kiểm tra UUID/runtime xác nhận Core chưa boot.
Chỉ node mới được đổi sang ID3 còn trống; native EVE status trả về 0; không stop/wipe node nào.

Seed: {seed['seed_path']}; owner root, mode 0600.
Seed SHA256: {seed['seed_sha256']}; bytes {seed['seed_bytes']}.
Instance-id: {seed['instance_id']}; account soc-core-admin; hostname soc-core-l2.
NoCloud cidata; user-data/meta-data/network-config đúng tên cả Rock Ridge và Joliet.
Console hash được người dùng nhập trực tiếp qua getpass TTY, không lưu plaintext/chat/repo/log.
SSH password authentication=false; root login disabled; password account unlocked trong seed.
Network-config match 8 MAC, DHCP4/DHCP6/RA off, không IP, optional=true; chưa áp dụng guest.
Kiểm tra cấu trúc YAML bằng PHP YAML; không khẳng định cloud-init schema/runtime đã đạt trên Core.

Bundle: {bundle['bundle']}
Bundle SHA256: {bundle['sha256']}; archive bytes 48619520.
70 .deb, tổng byte package 25963666; Ubuntu Noble/Noble Updates/Noble Security amd64/all.
OVS/openvswitch-common/python3-openvswitch: 3.3.9-0ubuntu0.24.04.1.
GPG signatures hợp lệ: Ubuntu Archive key F6ECB3762474EDA9D21B7022871920D1991BC93C.
Đối chiếu SHA256 indexes theo InRelease, SHA256 từng deb theo index, control Package/Version/Architecture.
APT sources/status/cache/Etc tách riêng; chỉ file repository Noble, không dùng host Jammy status/cache.
Kiểm tra APT --download-only --no-download: rc0, Download complete and in download only mode.
Thông báo 70 newly installed trong kế hoạch APT KHÔNG phải cài thật.
Host /var/lib/dpkg/status và /etc/apt không đổi; status APT cô lập vẫn rỗng.
Chưa kiểm tra tương thích kernel/installed-state bên trong Core vì Core chưa boot.

RAM Windows {memory['CollectedAt']}: free physical {memory['FreePhysicalMemoryKiB']} KiB,
khoảng {memory['FreePhysicalMemoryKiB']/1024:.1f} MiB; tổng {memory['TotalVisibleMemoryKiB']} KiB.
EVE snapshot 19:57: available5332MiB; lần free -m lúc20:00 available5352MiB, swap4095MiB/used0.
Không tự đóng ứng dụng/VM hoặc đổi cấu hình Windows/VMware. Chưa đạt ngưỡng Windows2GiB
đã đề xuất trong kế hoạch; chỉ đề nghị người dùng tự lưu công việc và đóng cửa sổ/tab không cần.

Đối chiếu cuối: 9 file template/image/seed/lab cũ đều giữ nguyên SHA256.
Hai QEMU cũ PID287703 và297601 vẫn chạy; không tác động overlay của chúng.
Ảnh thật: M2-core-seed-ready-real-terminal-20261031.png (19:55:46+07),
M2-core-stopped-eight-nics-real-terminal-20261031.png (19:57:58+07).
Ảnh lấy Win32 PrintWindow cửa sổ terminal thật, không sửa nội dung; không phải ảnh GUI topology.
Giới hạn GUI topology/settings: cần người dùng chụp thủ công nếu không có công cụ browser phù hợp.
'''
    new_text(E/'M2-core-stage1-execution-20261031.log',safe_log)
    extension=f'''

## 2.9. Chuẩn bị tài nguyên Core mới trong giai đoạn đầu M2

Phần 2.1–2.8 ở trên lưu kết quả kiểm chứng nền Ubuntu và thiết kế tại bước trước. Từ mục 2.9, báo cáo ghi nhận **tài nguyên mới đã được tạo theo phê duyệt**, phân biệt với các kiểm thử guest chưa được phép thực hiện. Hai node `Ubuntu-Test` và `Ubuntu-Console-Test` được giữ nguyên. Bản Word/Markdown cũ được bảo toàn; đây là phiên bản báo cáo M2 cập nhật.

### 2.9.1. Phạm vi phê duyệt và phương pháp

Được phép chuẩn bị bundle OVS offline từ Ubuntu 24.04 chính thức, image/đĩa riêng ít nhất 8 GiB, seed quản trị riêng và node mới 1 vCPU/2048 MiB/8 vNIC, để tắt và chưa nối mạng. Việc tạo lab/node sử dụng native PHP classes `Lab` và `Node` của EVE qua SSH quản trị, cùng cơ chế backend của EVE; không đăng nhập API Web, không tạo cookie hay thay phiên Web người dùng. Không gọi start/stop/wipe/fixpermissions toàn hệ thống.

Khởi động Core, cài OVS vào guest, tạo bridge/VLAN/trunk/mirror và nối mạng tiếp tục nằm ngoài phạm vi. Không sửa template chung, image gốc, lab cũ hoặc cấu hình Windows/VMware.

### 2.9.2. Kết quả image và đĩa Core

| Hạng mục | Kết quả đã xác minh |
|---|---|
| Image directory | `/opt/unetlab/addons/qemu/linux-ubuntu-24.04-soc-core-l2` |
| Disk | `virtioa.qcow2`, bản sao đầy đủ độc lập, không có backing-file |
| Virtual capacity | 8,589,934,592 byte, tương đương 8 GiB |
| File size | 621,346,944 byte; dung lượng file khác virtual capacity |
| Kiểm tra QCOW2 | `qemu-img check`: rc=0, `check-errors=0` |
| So nội dung với base | `qemu-img compare`: rc=0, `Images are identical` |
| Disk SHA-256 mới | `{node['disk_sha256']}` |
| Base SHA-256 bảo toàn | `{node['base_sha256']}` |

Quy trình sao chép kiểm tra checksum trước khi mở rộng, chỉ resize file mới, sau đó kiểm tra cấu trúc và so dữ liệu. Cảnh báo `Image size mismatch` trong compare là hệ quả đĩa mới 8 GiB lớn hơn base 3.5 GiB; công cụ vẫn trả về dữ liệu giống nhau, vùng đuôi tăng thêm bằng zero. Kết quả xác nhận tính toàn vẹn mức ảnh đĩa, **chưa xác nhận partition/root filesystem đã mở rộng**, vì Core chưa khởi động. [QEMU image utility](https://www.qemu.org/docs/master/tools/qemu-img.html).

### 2.9.3. Lab, node và tám interface đã khai báo

Lab mới là `/opt/unetlab/labs/SOC-M2-Core-L2.unl`, UUID `{node['lab_id']}`. Node `SOC-Core-L2` có ID **3**, UUID `{node['uuid']}`, CPU=1, RAM=2048 MiB, Ethernet=8, template Linux, VirtIO NIC, QEMU 2.12.0. Native EVE status đọc lại là **0 — stopped**; không có tiến trình QEMU mang UUID Core và chưa có runtime directory/overlay cho lab mới.

Trong lần tạo đầu, ID 1 của lab mới làm hàm EVE `getStatus()` nhìn thấy cổng console của node ID 1 đang chạy ở lab cũ và trả về 2. Không có Core process hoặc runtime, nên đây là kết quả trạng thái nhầm theo cổng, không phải Core đã boot. Chỉ ID của node mới được chuyển sang 3 chưa dùng; sau đó status=0 được đối chiếu lại với UUID/process/runtime. Không dừng VM cũ hoặc xóa/wipe dữ liệu để xử lý.

| EVE interface ID | Nhãn EVE đã đọc | MAC đã đọc | Network ID | NIC guest |
|---|---|---|---|---|
'''
    for interface in final['live_eve_node']['interfaces']:
        extension+=f"| {interface['id']} | {interface['eve_name']} | `{interface['mac']}` | 0, chưa nối | Chưa xác minh |\n"
    extension+=f'''
Node có 0 network object và 0 liên kết. Nhãn EVE `e0`–`e7` đã được xác minh ở cấp cấu hình; không coi đó là tên Linux và không giả định `ens3`, `ens4` cho Core chưa boot. Vai trò access/trunk/mirror vẫn theo thiết kế, chưa có cấu hình OVS áp dụng.

## 2.10. Seed NoCloud và tài khoản quản trị riêng

![Terminal thật hoàn tất seed](../evidence/M2/M2-core-seed-ready-real-terminal-20261031.png)

**Hình 2.3. Kết quả tạo seed NoCloud riêng cho node SOC-Core-L2 ở trạng thái tắt**

Mục đích của hình là chứng minh quy trình nhập mật khẩu qua terminal riêng đã kết thúc và seed đã được đóng gói, không phải chứng minh đăng nhập guest Core. Ảnh là cửa sổ PowerShell/SSH thực tế, chụp nguyên cửa sổ bằng Win32 PrintWindow lúc 19:55:46 ngày 31/10/2026, UTC+07:00. Input getpass không hiển thị mật khẩu; ảnh không chứa password/hash. Kết quả cho thấy seed sẵn sàng, Core vẫn tắt và chưa cài OVS.

| Trường seed | Kết quả kiểm tra tĩnh |
|---|---|
| Path | `{seed['seed_path']}` |
| Owner/mode | root, 0600; thư mục chứa input riêng 0700 |
| Volume label | `cidata`, có Rock Ridge và Joliet |
| File gốc ISO | `user-data`, `meta-data`, `network-config`, archive bundle OVS |
| Tài khoản / hostname đề nghị trong seed | `soc-core-admin` / `soc-core-l2` |
| Instance-id | `{seed['instance_id']}` |
| Console | Có hash SHA-512 crypt, `lock_passwd: false`; chưa thử login Core |
| SSH password/root login | `ssh_pwauth: false`, `disable_root: true`; hiệu lực runtime chưa kiểm tra |
| Quyền quản trị | Seed khai báo nhóm adm/sudo; chưa xác minh sudo trong guest |
| Network-config | Match 8 MAC, DHCP4/DHCP6/RA tắt, không địa chỉ IP, optional=true |
| Seed size / SHA-256 | {seed['seed_bytes']:,} byte / `{seed['seed_sha256']}` |

Mật khẩu do người dùng nhập trực tiếp hai lần qua getpass trên TTY SSH. Plaintext chỉ dùng trong bộ nhớ để đưa vào OpenSSL qua stdin; không đặt trên command line, chat, log hoặc repository. Hash chỉ nằm trong seed/input riêng bảo vệ trên EVE, không được sao chép vào bộ báo cáo. Public key quản trị chỉ được nhận khi fingerprint khớp khóa đã xác minh trước đây. File mô tả trong repository đã che hash/key material, không dùng thay seed thật.

Đã parse cấu trúc YAML và đối chiếu tên file trong cả hai namespace ISO, nhưng **chưa chạy cloud-init schema/runtime trên Core**. Việc guest nhận datasource, user/hostname, tám NIC và root filesystem là tiêu chí bước boot tiếp theo. Cấu hình NoCloud tĩnh không thay cho kết quả `cloud-init status --long` trong Core. [NoCloud chính thức](https://docs.cloud-init.io/en/latest/reference/datasources/nocloud.html).

## 2.11. Bundle Open vSwitch offline cho Ubuntu 24.04 amd64

### 2.11.1. Nguồn, phiên bản và toàn vẹn

Đã chuẩn bị **70 package** gồm root package `openvswitch-switch` và dependency/Pre-Depends do APT giải từ nguồn Ubuntu Noble chính thức; không bao gồm mọi Recommends/Suggests. `openvswitch-switch`, `openvswitch-common` và `python3-openvswitch` được chọn ở phiên bản **3.3.9-0ubuntu0.24.04.1**. Kiến trúc các gói chỉ có `amd64` hoặc `all`.

Metadata được tải bằng Windows qua HTTPS từ `archive.ubuntu.com` và `security.ubuntu.com`, gồm InRelease của noble/noble-updates/noble-security và sáu index main/universe amd64. Đã xác minh chữ ký với Ubuntu Archive Automatic Signing Key (2018), fingerprint `F6ECB3762474EDA9D21B7022871920D1991BC93C`. Hash index khớp InRelease; hash từng `.deb` khớp index; các trường Package/Version/Architecture trong control archive khớp manifest. Đây là chuỗi kiểm tra metadata → package, không chỉ so hai bản sao của cùng một file. [APT archive authentication](https://manpages.ubuntu.com/manpages/noble/man8/apt-secure.8.html).

| Artifact | Kết quả |
|---|---|
| Windows bundle | `staging/soc-core-l2-20261031-stage1/ovs-noble-amd64-offline-20261031.tar` |
| EVE bundle | `{bundle['bundle']}` |
| Archive size | 48,619,520 byte |
| Tổng dung lượng 70 `.deb` | 25,963,666 byte |
| Bundle SHA-256 | `{bundle['sha256']}` |
| OVS switch package SHA-256 | `7a9a359d6a3bc207b210ef2cf6b9f11244f89eb2a910b4ba863ebef08e85dd0a` |

### 2.11.2. Bộ giải APT tách riêng và giới hạn tương thích

APT executable sẵn có trên EVE chỉ được dùng làm bộ giải và kiểm tra cache: toàn bộ sources, Etc, status, state, cache và log được tách vào `/opt/unetlab/soc-core-preparation-20261031/apt-root`. Sources chỉ trỏ tới file repository Noble đã xác thực; status bắt đầu và kết thúc vẫn rỗng. Không dùng package status, sources hoặc cache Jammy của host để lựa chọn gói. Không cài phần mềm lên EVE để chuẩn bị bundle.

Kiểm tra cuối dùng `--download-only --no-download --no-install-recommends`; đã đủ byte trong cache, rc=0 và có dòng `Download complete and in download only mode`. Thông báo kế hoạch `70 newly installed` trong output APT **không phải 70 gói đã được cài**. Hash `/var/lib/dpkg/status` và các file `/etc/apt` của host không đổi. [APT configuration isolation](https://manpages.ubuntu.com/manpages/noble/man5/apt.conf.5.html).

Bundle phù hợp release/architecture và đã khép dependency theo trạng thái rỗng của bộ giải, nhưng chưa chứng minh tương thích kernel/datapath hoặc installed-state thực của Core. Sau boot phải kiểm tra `uname -r`, module openvswitch, kiến trúc và mô phỏng cài theo package state guest. Không cài mù toàn bộ 70 `.deb`: nhiều gói nền đã có trong guest và cần tránh nâng/gỡ thành phần ngoài phạm vi. Mọi cài OVS thực tế tiếp tục cần phê duyệt riêng.

## 2.12. Minh chứng kiểm tra cuối và tình trạng tài nguyên

![Terminal thật kiểm tra Core tắt và tám NIC](../evidence/M2/M2-core-stopped-eight-nics-real-terminal-20261031.png)

**Hình 2.4. Kiểm tra trạng thái tắt và tám giao diện mạng ảo đã khai báo của SOC-Core-L2**

Hình 2.4 ghi lại terminal thật chạy bộ kiểm tra chỉ đọc trên EVE, chụp lúc 19:57:58 UTC+07:00. Nội dung cho biết node status=0, cấu hình CPU/RAM/8 NIC, MAC của từng interface, network_id=0, không Core process/runtime, seed và bundle đã kiểm tra, checksum tài nguyên cũ bảo toàn. Đây là output kiểm tra từ EVE và Windows, **không phải console của guest Core đang boot hoặc ảnh GUI topology**. Ảnh nguyên cửa sổ, không cắt/ghép/sửa nội dung kỹ thuật.

Lần kiểm tra Windows lúc **{memory['CollectedAt']}** ghi FreePhysicalMemory **{memory['FreePhysicalMemoryKiB']:,} KiB, khoảng {memory['FreePhysicalMemoryKiB']/1024:.1f} MiB**; tổng RAM nhìn thấy khoảng 15.7 GiB. RAM Windows dao động trong phiên, không dùng số 899 MiB của ảnh chụp trước để thay mẫu mới hơn. EVE `free -m` ở lần đọc 20:00 cho available **5352 MiB**, swap dùng 0 MiB; việc EVE còn available không đồng nghĩa host Windows đã đủ RAM vật lý.

Theo ngưỡng vận hành đề xuất trong kế hoạch (Windows available ít nhất 2 GiB, EVE MemAvailable ít nhất 3 GiB trước boot), **Windows hiện chưa đạt điều kiện đề xuất để khởi động Core**. Không tự đóng ứng dụng/VM hoặc đổi RAM VMware. Người dùng có thể lưu công việc rồi tự đóng tab/ứng dụng không dùng và các cửa sổ terminal SOC đã hoàn tất; nếu muốn dừng VM khác thì phải xác định riêng, không dừng hai node kiểm chứng. Sau đó đo lại cả hai lớp tài nguyên. Ngưỡng này là lựa chọn cho lab, không phải bảo đảm của nhà cung cấp.

## 2.13. Giải thích thuật ngữ của bước chuẩn bị Core

| Tên tiếng Anh đầy đủ / viết tắt | Nghĩa tiếng Việt | Nguyên lý | Vai trò trong SOC và ví dụ của đồ án |
|---|---|---|---|
| Open vSwitch — OVS | Bộ chuyển mạch ảo | OVSDB lưu cấu hình, daemon/datapath chuyển frame theo chính sách L2 | Core SOC dự kiến thực hiện VLAN/trunk/mirror; hiện mới có bộ cài, chưa cài guest |
| Virtual Network Interface Card — vNIC | Giao diện mạng ảo | QEMU mô phỏng card với MAC và kết nối backend riêng | Đã khai báo 8 vNIC e0–e7 trên EVE; tên guest còn chưa xác minh |
| QCOW2 overlay — QEMU Copy-On-Write version 2 overlay | Lớp ảnh đĩa ghi thay đổi | Đọc dữ liệu chưa sửa từ backing, ghi thay đổi ở overlay; phụ thuộc chuỗi backing | Image Core mới là full copy độc lập; runtime overlay EVE chưa tạo vì Core chưa boot; overlay cũ giữ nguyên |
| cloud-init (tên sản phẩm, không tự tạo dạng khai triển) | Công cụ khởi tạo instance | Nhận datasource, đọc user-data/meta-data/network-config và chạy module theo boot/frequency | Seed Core khai báo tài khoản/hostname riêng; trạng thái done của node console không suy rộng cho Core |
| Offline package — Debian binary package `.deb` | Gói cài đặt dùng khi target không có Internet | Gói và dependency được tải trước, xác thực, chuyển qua phương tiện cục bộ rồi giải quyết theo trạng thái target | 70 gói Noble trong ISO riêng cho Core; chưa chạy cài đặt guest |
| Network bridge / Layer 2 bridge | Cầu nối chuyển mạch Layer 2 | Học MAC và chuyển frame trong miền được phép | Bridge OVS dự kiến tên br-soc, chưa tạo; khác bridge EVE dùng nối TAP |
| Access port | Cổng truy nhập một VLAN | Frame endpoint được gán vào VLAN của cổng | Vai trò access 30/40/50/60/99 thuộc thiết kế, chưa gán lên e0–e4 |
| VLAN trunk port | Cổng mang nhiều VLAN | Frame 802.1Q mang VLAN ID để dùng chung link | Hai cổng độc lập dự kiến tới hai OPNsense; chưa nối và không là bond LACP |
| Port mirroring | Sao chép lưu lượng sang cổng giám sát | Nhân bản frame được chọn tới capture port | Cổng thứ tám dự kiến gửi traffic cho Suricata; chưa cấu hình mirror, không phải IPS inline |

Các thuật ngữ đã có phần giải thích chi tiết hơn ở mục 2.5 và [kế hoạch triển khai Core](core-l2-implementation-plan.md). Ví dụ chưa được triển khai được đánh dấu rõ; không coi VLAN/IP hoặc port-to-port dự kiến là chính thức chỉ vì EVE đã có tám interface.

## 2.14. Đánh giá hoàn thành và bước tiếp theo

| Hạng mục | Kết quả ở cuối giai đoạn đầu |
|---|---|
| Bundle OVS chính thức | Đạt kiểm tra nguồn/chữ ký/hash/control và dependency/cache; chưa nghiệm thu runtime guest |
| Image/đĩa Core 8 GiB | Đạt kiểm tra QCOW2 và so dữ liệu; root filesystem guest chưa kiểm tra |
| Seed/tài khoản riêng | Đạt chuẩn bị tĩnh và bảo vệ bí mật; console login/cloud-init Core chưa thử |
| Node 1 CPU/2048 MiB/8 NIC | Đã tạo, status=0, 0 network/link, chưa có process/runtime overlay |
| Tài nguyên cũ | 9 file template/base/variant/seed/lab đều giữ SHA; hai QEMU cũ vẫn PID287703 và297601 |
| VLAN/trunk/mirror/bridge OVS | Chưa cấu hình, đúng giới hạn phê duyệt |
| Windows RAM | Chưa đạt ngưỡng vận hành đề xuất; cần người dùng xử lý rồi đo lại |

Sau khi người dùng giải phóng tài nguyên và phê duyệt **start duy nhất SOC-Core-L2**, mới boot, đăng nhập console bằng soc-core-admin và kiểm tra cloud-init, hostname, 8 NIC theo MAC, CPU/RAM, root partition/filesystem. Chưa cài OVS trong bước boot này. Khi các kiểm tra guest đạt, mới đề nghị phê duyệt mô phỏng/cài OVS offline và các bước cấu hình Layer 2 riêng.

Bộ báo cáo cập nhật gồm Word/Markdown mới, hai ảnh thật mới, snapshot trước/sau, cấu hình node/XML, metadata/network-config không chứa bí mật, log xác minh package, manifest và danh mục ảnh. Không sao chép seed ISO hoặc user-data chứa hash vào repository. Ảnh topology/settings EVE GUI chưa chụp trực tiếp: người dùng mở lab SOC-M2-Core-L2, hiển thị SOC-Core-L2 đang tắt và settings Ethernet=8, chụp PNG nguyên bản bằng Snipping Tool và lưu vào docs/evidence/M2 với thời điểm UTC+07:00. Ảnh terminal không được gán nhãn thành ảnh topology.
'''
    old=(ROOT/'docs/M2/M2-cloud-init-validation-20261031.md').read_text(encoding='utf-8')
    notice='> Bản cập nhật M2 ngày 31/10/2026: mục 2.1–2.8 lưu bước Ubuntu trước đây; mục 2.9–2.14 ghi nhận chuẩn bị Core mới. Bản Word/ảnh/log cũ được giữ nguyên.\n\n'
    report=ROOT/'docs/M2/M2-report-stage1-core-preparation-20261031.md'
    new_text(report,notice+old+extension)
    image_rows=[
      {'ten_anh':'M2-core-seed-ready-real-terminal-20261031.png','noi_dung':'Terminal thật hoàn tất seed, Core tắt; không phải guest login','thoi_diem':'2026-10-31T19:55:46.8688519+07:00','duong_dan':'docs/evidence/M2/M2-core-seed-ready-real-terminal-20261031.png','vi_tri_bao_cao':'Hình 2.3, mục 2.10'},
      {'ten_anh':'M2-core-stopped-eight-nics-real-terminal-20261031.png','noi_dung':'Terminal kiểm tra chỉ đọc: status0, 8 NIC/MAC không link, disk8GiB, bundle và seed','thoi_diem':'2026-10-31T19:57:58.1764632+07:00','duong_dan':'docs/evidence/M2/M2-core-stopped-eight-nics-real-terminal-20261031.png','vi_tri_bao_cao':'Hình 2.4, mục 2.12'}]
    for row in image_rows:row['sha256']=hashlib.sha256((ROOT/row['duong_dan']).read_bytes()).hexdigest()
    with (E/'M2-core-stage1-evidence-index-20261031.csv').open('x',encoding='utf-8-sig',newline='') as target:
        writer=csv.DictWriter(target,fieldnames=list(image_rows[0]));writer.writeheader();writer.writerows(image_rows)
    index=['# Danh mục minh chứng M2 — Chuẩn bị Core giai đoạn đầu','',
           '## 1. Ảnh thật đã thu','',
           '| Tên ảnh | Nội dung | Thời điểm UTC+07:00 | Đường dẫn | Vị trí báo cáo |','|---|---|---|---|---|']
    for row in image_rows:index.append(f"| [{row['ten_anh']}]({row['ten_anh']}) | {row['noi_dung']} | {row['thoi_diem']} | `{row['duong_dan']}` | {row['vi_tri_bao_cao']} |")
    index+=['','Ảnh nguyên cửa sổ Windows Terminal/PowerShell bằng Win32 PrintWindow; đã xem để kiểm tra nội dung. Không chỉnh sửa/ghép/cắt kết quả, không chứa password/hash/private key/token. Đây là ảnh terminal thật, không phải GUI EVE hoặc console guest Core đang chạy. CSV cùng tên chứa SHA-256 của ảnh.',
            '', '## 2. Log và cấu hình đã lưu','',
            '- [Snapshot trước thao tác](M2-core-stage1-baseline-20261031.json).',
            '- [Snapshot kiểm tra cuối](M2-core-stage1-final-status-20261031.json): status/process/runtime, interface/MAC, hash 9 file cũ và bộ nhớ.',
            '- [Log thực hiện](M2-core-stage1-execution-20261031.log).',
            '- [Cấu hình image/node](M2-core-stage1-image-node-config-20261031.json), [lab XML](M2-core-stage1-lab-20261031.unl).',
            '- [Seed status không chứa hash mật khẩu](M2-core-stage1-seed-status-20261031.json), [cấu hình đã che bí mật](M2-core-stage1-seed-redacted-20261031.json), [network-config](M2-core-stage1-network-config-20261031.yaml), [meta-data](M2-core-stage1-meta-data-20261031.yaml).',
            '- [Manifest package](M2-core-stage1-package-manifest-20261031.json), [bảng package CSV](M2-core-stage1-packages-20261031.csv), [metadata manifest](M2-core-stage1-metadata-manifest-20261031.json).',
            '- [Xác minh byte/closure](M2-core-stage1-bundle-validation-20261031.json), [log APT Noble](M2-core-stage1-apt-update-noble-20261031.log), [log APT download-only/no-download](M2-core-stage1-apt-offline-check-20261031.log).',
            '- [RAM Windows cuối](M2-core-stage1-windows-memory-20261031.json); EVE free -m ở 20:00 được chép trong log thực hiện.',
            '- `M2-core-stage1-SHA256SUMS-20261031.txt`: manifest riêng của bộ cập nhật; không cập nhật manifest cũ.',
            '', '## 3. Báo cáo cập nhật và giới hạn','',
            '- [Báo cáo Markdown v2](../../M2/M2-report-stage1-core-preparation-20261031.md).',
            '- [Báo cáo Word v2](../../M2/M2-report-stage1-core-preparation-20261031.docx).',
            '- Core chưa boot, chưa cài OVS; số NIC là cấu hình EVE, chưa là kết quả nhận NIC trong guest. Không có ảnh VLAN/trunk/mirror/runtime vì chưa triển khai.',
            '- Chưa có ảnh topology/settings EVE trực tiếp. Người dùng có thể mở lab SOC-M2-Core-L2, chụp topology và settings Ethernet=8 bằng Snipping Tool, giữ nguyên PNG, đặt tên M2-core-topology-stopped-<time>.png và M2-core-settings-eight-nics-<time>.png; bổ sung danh mục sau khi nhận ảnh. Không dùng ảnh giả.',
            '- Bộ ảnh/log cũ trong docs/evidence/eve-ng và các manifest M2 trước được giữ nguyên.','']
    new_text(E/'M2-core-stage1-evidence-index-20261031.md','\n'.join(index))
    print(json.dumps({'report':str(report),'new_images':len(image_rows),'packages':len(packages['packages']),'core_status':final['live_eve_node']['status'],'windows_free_MiB':memory['FreePhysicalMemoryKiB']/1024}))

if __name__=='__main__':main()
