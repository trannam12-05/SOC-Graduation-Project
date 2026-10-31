"""Tạo phiên bản báo cáo M2 mới, giữ nguyên bản trước; chỉ dùng log/ảnh thực tế."""
import csv
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile
from export_m2_report_docx import build

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT/'docs/evidence/M2'
GUEST = EV/'ovs-offline-guest-20261101'
DOCS = ROOT/'docs/M2'
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    integrity = json.loads((GUEST/'transfer-integrity.json').read_text())
    assert integrity['verified_against_guest_console']
    audit = json.loads(sorted(EV.glob('M2-ovs-takeover-*-audit.json'))[-1].read_text())
    assert audit['all_passed']
    hashes = {}
    for line in (GUEST/'guest-sha256.txt').read_text().splitlines():
        digest,name = line.split(None,1)
        hashes[name.strip().removeprefix('/opt/ovs-offline/')] = digest
    assert len(hashes) == 70
    assert all(hashes[p['filename']] == p['sha256'] for p in audit['packages'])
    index_hashes = {}
    for line in (GUEST/'indexes-sha256.txt').read_text().splitlines():
        digest,name = line.split(None,1)
        index_hashes[name.strip().removeprefix('/opt/ovs-offline/')] = digest
    assert len(index_hashes) == 6
    assert all(index_hashes[p['path']] == p['sha256'] for p in audit['indexes'])
    signatures = (GUEST/'signatures.log').read_text()
    assert signatures.count('Good signature') == 3
    sim = (GUEST/'simulate2.log').read_text()
    assert '0 upgraded, 7 newly installed, 0 to remove' in sim
    assert '3.3.9-0ubuntu0.24.04.1' in sim
    assert not re.search(r'^Remv ',sim,re.M)
    allowed = {(p['package'],p['version']) for p in audit['packages']}
    actions = re.findall(r'^Inst (\S+)(?: \[[^\]]+\])? \((\S+)',sim,re.M)
    assert len(actions) == 7 and all((n,v) in allowed for n,v in actions)
    verify = (GUEST/'verification.log').read_text()
    assert 'Open vSwitch) 3.3.9' in verify and verify.count('active\n') == 3
    assert verify.count('3.3.9-0ubuntu0.24.04.1') == 3
    assert 'Bridge ' not in verify
    before = json.loads((EV/'M2-ovs-install-host-before-20261031.json').read_text(encoding='utf-8-sig'))
    after = json.loads((EV/'M2-ovs-install-host-after-20261101.json').read_text(encoding='utf-8-sig'))
    assert before['protected_sha256'] == after['protected_sha256']
    assert before['interfaces'] == after['interfaces'] and not after['networks']
    guest_links = json.loads((GUEST/'guest-links.json').read_text())
    mac_to_guest = {x['address']:x['ifname'] for x in guest_links if x.get('link_type') == 'ether'}
    capture = json.loads(sorted(EV.glob('M2-ovs-final-verification-*.json'))[-1].read_text())
    args = capture['qemu']['args']
    nic_rows = []
    for arg in args:
        if arg.startswith('virtio-net-pci,netdev='):
            values = dict(x.split('=',1) for x in arg.split(',')[1:])
            mac = values['mac']; backend = values['netdev']
            tap_arg = next(x for x in args if x.startswith('tap,id='+backend+','))
            tap = dict(x.split('=',1) for x in tap_arg.split(',')[1:])['ifname']
            assert mac in mac_to_guest
            assert not next(x for x in after['links'] if x['ifname']==tap).get('master')
            nic_rows.append([backend,tap,mac,mac_to_guest[mac],'Chưa nối peer; vai trò VLAN chưa gán'])
    assert len(nic_rows) == 8 and len({r[2] for r in nic_rows}) == 8
    mapping_stream = io.StringIO(newline='')
    mapping_writer = csv.writer(mapping_stream)
    mapping_writer.writerow(['qemu_backend','eve_host_tap','guest_mac','guest_interface','peer_and_role'])
    mapping_writer.writerows(nic_rows)
    with (EV/'M2-ovs-verified-runtime-nic-mapping-20261101.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        stream.write(mapping_stream.getvalue())
    validation = {'collected_at':NOW,'guest_packages_sha256_verified':70,'guest_indexes_sha256_verified':6,
                  'good_ubuntu_signatures':3,'simulated_actions':actions,
                  'guest_dependency_plan_matches_bundle':True,'protected_lab_image_seed_unchanged':True,
                  'ovs_version':'3.3.9','package_version':'3.3.9-0ubuntu0.24.04.1',
                  'services_active':['openvswitch-switch','ovsdb-server','ovs-vswitchd'],
                  'bridge_created':False,'vlan_trunk_mirror_tested':False,
                  'warning':'OVS_CTL_OPTS unset; startup succeeded; see warnings.log',
                  'guest_transport_sha256':integrity['sha256']}
    (EV/'M2-ovs-install-validation-20261101.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
    source = DOCS/'M2-report-stage2-preflight-20261031T2015+0700.md'
    old_word = source.with_suffix('.docx')
    backup = DOCS/'backups/M2-before-ovs-install-20261101'
    backup.mkdir(parents=True,exist_ok=False)
    for path in [source,old_word]:
        shutil.copy2(path,backup/path.name)
        assert sha(path) == sha(backup/path.name)
    prior = source.read_text(encoding='utf-8')
    result = DOCS/'M2-report-ovs-offline-installed-20261101.md'

    appendix = '''

## 2.17. Tiếp quản và hoàn tất cài Open vSwitch offline

### 2.17.1. Phạm vi và trạng thái cập nhật

Mục 2.1–2.16 giữ nguyên nội dung lịch sử của báo cáo trước; các nhận định Core chưa boot/chưa cài ở đó chỉ áp dụng tại thời điểm cũ. Kết quả hiện hành được cập nhật tại mục 2.17–2.20. Phiên triển khai diễn ra tối 31/10/2026 và hoàn thiện hồ sơ sang 01/11/2026, múi giờ UTC+07:00. Giờ thu thập lấy từ Windows, không dùng giờ guest hoặc EVE làm thời điểm đáng tin cậy.

Người dùng đã cho phép cài OVS offline trên SOC-Core-L2, ID 3, lab SOC-M2-Core-L2. Đã xác minh đúng tiến trình QEMU với UUID 2b295168-b72e-4de7-b364-37298252dd9f, 1 vCPU, 2048 MiB và 8 VirtIO NIC. Không wipe/reset node; không dừng hoặc bật thêm VM; không sửa VMware, NAT, Windows firewall, mạng, seed hoặc image. Hash lab, virtioa.qcow2 gốc và cdrom.iso gốc trước/sau giống nhau. Guest tự ghi filesystem trong quá trình cài; không có công cụ host ghi trực tiếp vào QCOW2 đang chạy.

Ảnh NIC, đĩa và trạng thái chưa cài do người dùng cung cấp đã được đọc trực tiếp, giữ nguyên byte. Thời điểm chụp gốc của ba ảnh chưa có log thu thập đi kèm; thời gian sửa tệp chỉ dùng tham khảo, không được thay thế thời điểm chụp.

![Tám NIC Core đã có](../evidence/M2/M2-core-l2-8-vnic-verified.png)

**Hình 2.10. Tám giao diện ens3–ens10 đã được Ubuntu nhận diện trước cài OVS**

Mục đích là xác định tập giao diện và MAC thực tế. Nội dung thể hiện tám NIC Ethernet, ngoài loopback; MAC lần lượt 02:53:45:f2:19:00 đến 02:53:45:f2:19:07. Kết quả xác nhận guest nhận đủ NIC; ý nghĩa là có cơ sở đối chiếu với EVE/QEMU. Chưa xác minh kết nối peer hoặc vai trò VLAN theo thứ tự NIC.

![Đĩa Core trước cài](../evidence/M2/M2-core-l2-disk-verified.png)

**Hình 2.11. Thiết bị đĩa vda 8 GiB và phân vùng Ubuntu Core trước cài đặt**

Mục đích là đối chiếu đĩa guest đang sử dụng. Nội dung lsblk thể hiện vda 8G, root vda1 và các phân vùng boot/EFI. Kết quả xác nhận dung lượng thiết bị, không phải dung lượng còn trống; ảnh không chứa df nên không dùng để chứng minh số trống 5,1 GiB mà người dùng đã mô tả. Ý nghĩa là xác định đúng phạm vi đĩa mà trình quản lý gói guest sử dụng.

![OVS chưa cài trước phiên](../evidence/M2/M2-core-l2-ovs-before-install.png)

**Hình 2.12. Trạng thái openvswitch-switch chưa cài ở mốc trước triển khai**

Mục đích là ghi nhận đường cơ sở. Nội dung dpkg thể hiện un và version none; kết quả cho thấy package chưa cài tại mốc ảnh. Ý nghĩa là phân biệt trạng thái trước và sau; ảnh này không thay cho kiểm tra phiên bản sau cài.

### 2.17.2. Bundle, chữ ký và giải phụ thuộc

Bộ audit mới trên Windows đối chiếu lại 70 tệp deb: SHA-256, kích thước, tên, phiên bản, kiến trúc và các trường Depends/Pre-Depends trong sáu chỉ mục Packages.xz đều khớp manifest. Trong guest đã tính lại 70 hash gói và sáu hash chỉ mục; dữ liệu xuất về Windows khớp hoàn toàn. gpgv xác nhận ba InRelease có chữ ký tốt từ Ubuntu Archive Automatic Signing Key (2018), fingerprint F6ECB3762474EDA9D21B7022871920D1991BC93C. Kiến trúc bundle là amd64/all. Phép kiểm tra status rỗng trước đây được giữ làm lịch sử; kế hoạch dependency trong lần này dựa trên trạng thái dpkg thực tế của guest.

Nguồn cũ chỉ ghi noble nên thiếu OVS 3.3.9 nằm trong noble-updates/main. Phiên này tạo offline.list riêng trong /tmp/m2-ovs-apt-2353, bao gồm noble, noble-updates và noble-security, chỉ URI file:/opt/ovs-offline, dùng signed-by với keyring Ubuntu. Không sửa nguồn APT online hiện hữu hoặc nguồn noble-only cũ; lần cài tiếp theo cần dùng nguồn riêng đã lưu, không chạy apt update chung rồi coi DNS đã được khắc phục.

### 2.17.3. Lệnh thực thi và xử lý lỗi

SSH tới EVE ban đầu bị chặn vì không có agent ký khóa; sau khi người dùng khởi động ssh-agent và nạp khóa, kết nối BatchMode đã thành công. Guest không có SSH trực tiếp; các lệnh được gửi qua VNC/RFB của đúng QEMU bên trong phiên SSH có kiểm tra host key. Lượt truyền payload dài bị sai ký tự, đã hủy dòng nhập dở; không coi các script payload chưa chạy là kết quả triển khai. Đã chuyển sang từng lệnh ngắn, giảm tốc độ và kiểm tra ảnh console; không chạy lại cloud-init hoặc chuyển lại kho gói.

Dùng sudo -n script -q -f /tmp/m2-ovs-install-20261031.log để ghi phiên root; không thu mật khẩu. Sao lưu trạng thái dpkg và source offline cũ vào thư mục làm việc trước cài. offline.list có ba dòng theo mẫu sau, thay suite tương ứng:

```text
deb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:/opt/ovs-offline noble main universe
deb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:/opt/ovs-offline noble-updates main universe
deb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:/opt/ovs-offline noble-security main universe
```

Các tùy chọn APT đã sử dụng, lưu nguyên bản trong apt-options.txt:

```text
-o Dir::Etc::sourcelist=/tmp/m2-ovs-apt-2353/offline.list
-o Dir::Etc::sourceparts=-
-o Dir::State::lists=/tmp/m2-ovs-apt-2353/lists
-o Acquire::Languages=none
-o Acquire::IndexTargets::deb::CNF::DefaultEnabled=false
-o Acquire::IndexTargets::deb::DEP-11::DefaultEnabled=false
```

Ba tùy chọn Dir giới hạn nguồn và chỉ mục vào phiên offline. Hai loại metadata CNF (gợi ý lệnh) và DEP-11 (mô tả ứng dụng) không có trong bundle; hai lần cập nhật đầu trả 100 vì thiếu chúng. Tắt việc lấy các loại phụ trợ trong phiên này cho phép lần update3 thành công với UPDATE_RC=0; vẫn giữ kiểm tra chữ ký và hash gói. Không cần Internet, không tắt xác thực kho và không đổi đồng hồ. Tùy chọn Languages tránh lấy bản dịch không cần thiết.

Trong shell thực tế, O là chuỗi tùy chọn trên và V=3.3.9-0ubuntu0.24.04.1. Các lệnh chính:

```sh
apt-get $O -o APT::Update::Error-Mode=any update
apt-get $O -s --no-install-recommends --no-remove install openvswitch-switch=$V
apt-get $O --yes --no-install-recommends --no-remove install openvswitch-switch=$V
```

Lệnh update cập nhật chỉ mục từ kho cục bộ; mô phỏng cho phép xem dependency; lệnh cuối cài đúng phiên bản, không cài gợi ý và không cho gỡ gói. APT tự chọn bảy gói cần thiết thay vì cài mù 70 tệp. Kế hoạch: libevent-2.1-7t64, libunbound8, libxdp1, python3-sortedcontainers, openvswitch-common, python3-openvswitch, openvswitch-switch; không nâng cấp hoặc gỡ gói, 18 gói hiện hữu không được nâng. Toàn bộ phiên bản trong bảy hành động Inst khớp manifest đã kiểm tra. INSTALL_RC=0. Cách dùng mô phỏng và pin phiên bản dựa trên [Ubuntu apt-get manual](https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html).

## 2.18. Kết quả kiểm chứng phần mềm và giới hạn nghiệm thu

### 2.18.1. Kết quả đạt và vấn đề còn tồn tại

| Hạng mục | Kết quả thực tế | Đánh giá và nguồn |
|---|---|---|
| Toàn vẹn gói/metadata guest | 70/70 gói và 6/6 chỉ mục khớp; 3 chữ ký tốt | Đạt; guest-sha256.txt, indexes-sha256.txt, signatures.log |
| Cập nhật offline | UPDATE_RC=0 sau khi tắt CNF/DEP-11 | Đạt; update3.log và ảnh Hình 2.13 |
| Dependency thực tế | 7 mới, 0 nâng cấp, 0 gỡ; đúng phiên bản bundle | Đạt; simulate2.log và Hình 2.14 |
| Cài phần mềm | INSTALL_RC=0 | Đạt; install.log, transcript và ảnh cài |
| Binary và schema | ovs-vsctl 3.3.9; DB Schema 8.5.1 | Đạt; verification.log và Hình 2.15 |
| Ba gói OVS | 3.3.9-0ubuntu0.24.04.1 | Đạt; verification.log |
| Dịch vụ | openvswitch-switch, ovsdb-server, ovs-vswitchd đều active | Đạt tại thời điểm kiểm tra; services.log |
| Cơ sở dữ liệu | UUID 36956952-09d5-4916-acf4-a3be3e891166; ovs_version 3.3.9; show RC=0; không bridge | Đạt khả năng truy cập DB; chưa kiểm thử chuyển tiếp |
| Module kernel | openvswitch có trong lsmod | Đạt nạp module; không chứng minh hiệu năng datapath |
| Tính nhất quán dpkg | dpkg --audit không xuất lỗi tại lần kiểm tra | Đạt trong phạm vi lệnh |
| Journal | OVS_CTL_OPTS unset, được đánh giá thành chuỗi rỗng; khởi động tiếp tục thành công | Cảnh báo còn tồn tại; warnings.log, journal.log; chưa sửa unit |
| VLAN, trunk, mirror | Chưa tạo/cấu hình/thử lưu lượng | Chưa nghiệm thu; chờ mapping peer |
| DNS/Internet guest | Không thay đổi mạng hoặc DNS | Chưa khắc phục kết nối online; không cản lần cài offline |

Đối tượng openvswitch-switch là unit điều phối nên cần đọc thêm ovsdb-server và ovs-vswitchd, không chỉ nhìn active của unit tổng. ovsdb-server quản lý cơ sở dữ liệu cấu hình; ovs-vswitchd hiện thực chuyển tiếp cùng datapath kernel; ovs-vsctl truy vấn và cập nhật cấu hình. Trong SOC, các thành phần này tạo nền cho phân tách VLAN và cung cấp bản sao lưu lượng giám sát. Kết quả hiện tại chỉ nghiệm thu cài đặt và khởi động phần mềm, chưa nghiệm thu chức năng chuyển mạch của M2. [Tài liệu OVS](https://docs.openvswitch.org/en/stable/intro/what-is-ovs/).

Việc lsmod hiển thị nf_nat hoặc nf_conntrack là thông tin module phụ thuộc của kernel; không phải minh chứng Core đã cấu hình NAT hoặc gateway. Không có lệnh cấu hình các chức năng Layer 3 trong phiên này.

### 2.18.2. Bảo toàn và lưu minh chứng

Log nguyên bản được lưu trong docs/evidence/M2/ovs-offline-guest-20261101/. Do không có đường mạng guest, dữ liệu được nén, mã hóa base64 và hiển thị từng trang trên console thật; bộ thu khôi phục ký tự bằng mẫu glyph chính xác, không đoán ký tự. SHA-256 của toàn bộ dữ liệu xuất khớp giá trị guest hiển thị trước khi giải nén. Ảnh truyền dữ liệu chỉ là phương tiện kiểm tra toàn vẹn, không được trình bày như ảnh kiểm thử chức năng mạng. Ảnh minh chứng kỹ thuật giữ nguyên nội dung; JSON đi kèm ghi thời điểm Windows, UUID, lệnh và hash ảnh.

Sao lưu báo cáo cũ nằm trong docs/M2/backups/M2-before-ovs-install-20261101/. Không xóa/di chuyển minh chứng cũ, kể cả docs/evidence/eve-ng/. Các bản gốc báo cáo vẫn giữ nguyên. Chưa kiểm tra bố cục bằng giao diện Word; đã kiểm tra cấu trúc DOCX, khổ A4, Times New Roman 12–13, lề trái 3 cm và các lề còn lại 2 cm.
'''
    figures = [
        ('M2-ovs-offline-update3-final-',13,'Cập nhật chỉ mục hoàn toàn offline thành công',
         'Mục đích là kiểm tra APT chỉ dùng nguồn cục bộ. Hình thể hiện UPDATE_RC=0 và các URI file:/opt/ovs-offline; kết quả xác nhận cập nhật thành công sau xử lý metadata phụ trợ. Ý nghĩa là dependency được giải từ bundle, không dựa Internet.'),
        ('M2-ovs-simulation-summary-hashes-',14,'Kế hoạch dependency thực tế và đủ 70 hash gói trong guest',
         'Mục đích là xác nhận phạm vi thay đổi trước cài. Hình thể hiện bảy gói mới, không nâng cấp/gỡ, HASH_RC=0 và 70 dòng hash. Kết quả đối chiếu hash về Windows được ghi trong JSON validation; riêng số dòng không thay kiểm tra hash. Ý nghĩa là tránh cài toàn bộ 70 dependency bất kể trạng thái guest.'),
        ('M2-ovs-installed-verification-',15,'Open vSwitch 3.3.9 hoạt động và cơ sở dữ liệu chưa có bridge',
         'Mục đích là kiểm tra binary, dịch vụ và DB sau cài. Hình thể hiện phiên bản 3.3.9, schema 8.5.1, ba active, UUID DB và SHOW_RC=0. Kết quả xác nhận nền OVS sẵn sàng; không có bridge nên chưa kết luận chuyển mạch/VLAN/mirror đạt.'),
        ('M2-ovs-service-journal-',16,'Journal khởi động Open vSwitch và cảnh báo biến tùy chọn chưa đặt',
         'Mục đích là đối chiếu trạng thái active với nhật ký khởi động. Nội dung thể hiện nạp module và khởi động daemon thành công, đồng thời có OVS_CTL_OPTS unset. Kết quả cho thấy cảnh báo không ngăn lần khởi động này; ý nghĩa là báo cáo minh bạch vấn đề còn tồn tại, không kết luận không có cảnh báo.'),
        ('M2-ovs-repository-signatures-',17,'Xác minh ba chữ ký InRelease của kho Ubuntu ngay trong guest',
         'Mục đích là xác thực nguồn metadata. Hình thể hiện ba Good signature cùng khóa Ubuntu Archive; kết quả phù hợp log signatures.log. Ý nghĩa là phân biệt kiểm tra chữ ký với chỉ kiểm tra số lượng tệp trong thư mục kho.')]
    for prefix,num,title,explain in figures:
        path = sorted(EV.glob(prefix+'*.png'))[-1]
        appendix += f'\n![{title}](../evidence/M2/{path.name})\n\n**Hình 2.{num}. {title}**\n\n{explain}\n'
    appendix += '\n### 2.18.3. Đối chiếu runtime và ảnh topology còn thiếu\n\n'
    appendix += '| QEMU backend | TAP trên EVE | MAC guest/QEMU | NIC Ubuntu | Peer/vai trò |\n|---|---|---|---|---|\n'
    appendix += '\n'.join('| '+' | '.join(row)+' |' for row in nic_rows)
    appendix += '\n\nBảng xác nhận backend QEMU, TAP và NIC Ubuntu theo MAC; tám TAP đều không có bridge master trên EVE tại snapshot. XML lab không có interface nối network; nhãn cổng giao diện Web và peer hai đầu vẫn cần đọc khi thiết kế kết nối. Không suy từ net0 thành nhãn EVE đã nhìn thấy trên GUI. Vai trò access/trunk/mirror vẫn là dự kiến.\n\n'
    appendix += 'Chưa chụp được topology GUI EVE bằng công cụ hiện có; các ảnh mới là console QEMU thật. Để bổ sung thủ công: mở lab SOC-M2-Core-L2 trên giao diện Web EVE, giữ nguyên trạng thái node, hiển thị toàn bộ canvas và tên node SOC-Core-L2; dùng Win+Shift+S chụp rõ trạng thái node và các liên kết hiện có, không cắt mất nhãn. Lưu docs/evidence/M2/M2-core-topology-after-ovs-<thoi-diem-UTC+0700>.png, ghi giờ chụp kèm múi giờ và bổ sung vào danh mục. Ảnh này hiện chưa tồn tại trong bộ minh chứng.\n'
    appendix += '\n'+(DOCS/'M2-ovs-cau-hinh-du-kien.md').read_text(encoding='utf-8')
    appendix += '\n## 2.20. Giải thích thuật ngữ và nguồn tham khảo\n\n'+(DOCS/'M2-ovs-thuat-ngu-bo-sung.md').read_text(encoding='utf-8')
    with result.open('x',encoding='utf-8') as stream:
        stream.write('> Bản cập nhật hiện hành: OVS 3.3.9 đã cài và kiểm tra dịch vụ; các mốc chưa cài ở phần lịch sử được giữ nguyên. Xem mục 2.17–2.20.\n\n'+prior+appendix)
    build(result)
    docx = result.with_suffix('.docx')
    with zipfile.ZipFile(docx) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            if name.endswith('.xml'):
                ET.fromstring(archive.read(name))
        main_xml = archive.read('word/document.xml').decode()
        styles = archive.read('word/styles.xml').decode()
        assert '11906' in main_xml and '16838' in main_xml and '1701' in main_xml
        assert 'Times New Roman' in styles
        embedded = [archive.read(n) for n in archive.namelist() if n.startswith('word/media/')]
        assert len(embedded) >= 12
        assert all(any(blob == p.read_bytes() for p in EV.glob('*.png')) for blob in embedded)
    # Danh mục có thời gian đi kèm múi giờ, đường dẫn và vị trí báo cáo.
    rows = []
    candidates = [p for p in EV.rglob('*') if p.is_file() and (
        p.name.startswith(('M2-ovs-','M2-core-takeover','M2-console-')) or
        GUEST in p.parents or 'console-transfer-20261101' in p.parts)]
    candidates += [EV/n for n in ['M2-core-l2-8-vnic-verified.png','M2-core-l2-disk-verified.png','M2-core-l2-ovs-before-install.png']]
    for path in sorted(set(candidates)):
        clock = NOW
        note = 'Thời điểm lập danh mục; thời điểm thu cụ thể xem log đi kèm'
        if path.suffix == '.png' and path.with_suffix('.json').exists():
            meta = json.loads(path.with_suffix('.json').read_text())
            clock = meta.get('collector_time_end',NOW)
            note = 'Console QEMU thật; lệnh, UUID, SHA256 trong JSON cùng tên'
        if path.name.startswith('M2-core-l2-'):
            clock = 'Chưa xác định (múi giờ chụp chưa xác nhận)'
            note = 'Ảnh người dùng đã có; không suy ra giờ chụp từ mtime'
        if GUEST in path.parents:
            clock = integrity['collector_time_start']+' → '+integrity['collector_time_end']+' (UTC+07:00)'
            note = 'Log guest nguyên byte; giờ xuất/nhận theo JSON console-transfer; giờ trong log guest chỉ tham khảo'
        rows.append([path.name,note,clock,str(path.relative_to(ROOT)),'2.17–2.18; dữ liệu truyền console không làm hình chức năng',sha(path)])
    out = io.StringIO(newline=''); writer = csv.writer(out)
    writer.writerow(['ten_tep','noi_dung','thoi_diem_va_mui_gio','duong_dan','vi_tri_bao_cao','sha256'])
    writer.writerows(rows)
    with (EV/'M2-ovs-evidence-index-20261101.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        stream.write(out.getvalue())
    index = '# Danh mục minh chứng cài OVS offline M2\n\nLập lúc '+NOW+' (UTC+07:00).\n\n'
    index += '| Tệp | Nội dung | Thời điểm/múi giờ | Đường dẫn | Vị trí báo cáo |\n|---|---|---|---|---|\n'
    index += '\n'.join('| '+' | '.join(row[:5])+' |' for row in rows)
    index += '\n\nAudit 23:43:58 trả false do bộ so sánh coi trường dependency rỗng khác trường không có; không có hash lỗi. Audit 23:44:09 đã sửa cách chuẩn hóa trường và đạt. Các ảnh thử truyền payload/đợi lệnh chỉ ghi diễn biến, không chứng minh cài thành công.\n'
    (EV/'M2-ovs-evidence-index-20261101.md').write_text(index,encoding='utf-8')
    hashes = [f'{sha(p)}  {p.relative_to(ROOT).as_posix()}' for p in [result,docx,EV/'M2-ovs-install-validation-20261101.json',EV/'M2-ovs-evidence-index-20261101.csv']]
    (EV/'M2-ovs-deliverables-SHA256SUMS-20261101.txt').write_text('\n'.join(hashes)+'\n',encoding='utf-8')
    print(json.dumps({'report':str(docx),'evidence_entries':len(rows),'embedded_images':len(embedded),'checks':'ZIP/XML, image bytes, font, A4/margins, hashes, dependencies, protected files all passed'},ensure_ascii=False))

if __name__ == '__main__':
    main()
