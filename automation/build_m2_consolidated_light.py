"""Build a new M2 report from existing verified evidence; no VM or OCR process."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
from export_m2_report_docx import build

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT/'docs/M2'
EV = ROOT/'docs/evidence/M2'
OUT = EV/'light-documentation-20261101'
SOURCE = DOCS/'M2-report-consolidated-review-20261101.md'
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    old_reports = {str(p.relative_to(ROOT)):sha(p) for p in DOCS.glob('*.docx')}
    prior = (DOCS/'M2-report-isolated-bridge-configured-20261101.md').read_text(encoding='utf-8')
    runtime = json.loads((EV/'isolated-bridge-20261101/guest/after.json').read_text())
    result = json.loads((EV/'isolated-bridge-20261101/guest/result.json').read_text())
    backup = json.loads((EV/'accelerated-20261101/stopped-backup.json').read_text(encoding='utf-8-sig'))
    assert result['configuration_verified'] and not result['traffic_tested'] and not result['mirror_created']
    assert backup['overlay_sha256_before'] == backup['overlay_sha256_after'] == backup['backup_sha256']
    mapping = list(csv.DictReader((EV/'isolated-bridge-20261101/configured-port-mapping.csv').open(encoding='utf-8-sig')))
    doc = '''# CHƯƠNG 2. CORE LAYER 2 BẰNG UBUNTU VÀ OPEN vSWITCH

## 2.1. Mục tiêu, phạm vi và trạng thái mới nhất

Bản hợp nhất phục vụ rà soát trước hạn nộp 05/11/2026, lập ngày 01/11/2026 (UTC+07:00). Báo cáo này tổ chức lại các kết quả quan trọng từ ba mốc cài OVS, xác minh mapping và cấu hình bridge cô lập; giữ nguyên báo cáo cũ làm lịch sử. Không trình bày đề xuất như kết quả triển khai.

Đã kiểm chứng khi Core chạy lúc 01:03–01:13: cài offline OVS 3.3.9, br-core-l2, năm access và hai trunk, không IP/gateway, forwarding 0/0. Chưa thử lưu lượng, SPAN, persistence hoặc HA. Kiểm kê mới lúc 07:57–07:58: không QEMU chạy, lab Core vẫn một node/không network/link. Vì vậy các bảng runtime là kết quả của mốc đã thu, không khẳng định daemon đang active khi node tắt.

Người dùng hiện học Labtainer và yêu cầu chế độ nhẹ: giữ VM SOC tắt, không thay EVE/VMware/Windows/Labtainer, không tải OPNsense, không chạy bài thử. Chỉ tiếp tục máy ảo sau khi người dùng xác nhận tài nguyên sẵn sàng. Đã hoàn thành tài liệu và chuẩn bị script không đồng nghĩa hoàn tất nghiệm thu chuyển mạch M2.

## 2.2. Kiến trúc và vai trò trong SOC

Core Ubuntu cung cấp chuyển mạch Ethernet Layer 2, phân chia vùng bằng VLAN và dự kiến sao chép lưu lượng cho cảm biến. OPNsense đảm nhiệm gateway, định tuyến liên VLAN, firewall rules và NAT; client dùng CARP VIP khi cặp HA thực sự triển khai. Core không được gán IP quản trị hay địa chỉ gateway. Suricata nhận mirror là IDS thụ động; Wazuh là thành phần phân tích/thu thập an ninh dự kiến, chưa có bằng chứng tích hợp.

```text
THIẾT KẾ KẾT NỐI — CÁC PEER VÀ LINK CHƯA ĐƯỢC TẠO
Data Center VLAN30 ------- ens3 --+
Employee    VLAN40 ------- ens4 --+
Guest       VLAN50 ------- ens5 --+
DMZ         VLAN60 ------- ens6 --+-- br-core-l2 (đã cấu hình ở mốc trước)
Management  VLAN99 ------- ens7 --+
OPNsense Primary LAN ----- ens8 --+   trunk 30,40,50,60,99
OPNsense Secondary LAN --- ens9 --+   trunk 30,40,50,60,99
Suricata capture <-------- ens10 -+   mirror dự kiến; hiện ngoài OVS

Primary SYNC <------ segment riêng ------> Secondary SYNC
WAN hai firewall: thiết kế riêng, chưa nối mạng host hoặc mạng thật.
```

Hai trunk phải ở hai segment độc lập, không bond/LACP xuyên hai firewall. Cổng capture không bridge sang mạng khác. Khi chưa có gateway, Core không tự chuyển frame giữa VLAN 30 và VLAN 40. Một Core đơn vẫn là điểm lỗi đơn; thiết kế hai firewall không tự giải quyết lỗi Core.

## 2.3. Môi trường và cài Open vSwitch hoàn toàn offline

EVE-NG Community 6.2.0-4 tại 192.168.220.143, VMware Workstation trên Windows 11. Lab SOC-M2-Core-L2, node SOC-Core-L2 ID 3, UUID 2b295168-b72e-4de7-b364-37298252dd9f. Guest Ubuntu 24.04, một vCPU, 2048 MiB RAM, đĩa 8 GiB và tám vNIC VirtIO. Cloud-init đã hoàn tất; không chạy lại hoặc sửa seed NoCloud.

Bundle offline gồm 70 gói .deb, sáu chỉ mục được đối chiếu hash; ba chữ ký InRelease Ubuntu được xác minh. Gói openvswitch-switch/openvswitch-common/python3-openvswitch thuộc phiên bản 3.3.9-0ubuntu0.24.04.1. Bộ giải thực tế chỉ cần bảy gói mới, không đồng nghĩa đã cài toàn bộ 70 gói. Kho /opt/ovs-offline có dists/pool và các suite noble/noble-updates/noble-security; thao tác cài dùng nguồn file riêng, không dựa DNS/Internet guest.

Lỗi cũ gồm nguồn thiếu noble-updates, metadata phụ CNF/DEP-11 không có trong bundle và console nhập sai dấu sao. Đã sửa nguồn dành riêng cho lệnh offline, tắt lấy chỉ mục phụ không có và cài theo tên gói thay wildcard. Không sửa NAT/DNS/firewall để che lỗi. Lệnh và exit code chi tiết giữ trong minh chứng cài đặt cũ; không chạy lại cài phần mềm trong đợt tài liệu.

## 2.4. Mapping tám cổng theo MAC và trạng thái cấu hình

Mapping dưới đây được đối chiếu QEMU netdev/device, TAP EVE và MAC trong Ubuntu ở mốc runtime trước. TAP không có bridge master, lab không có peer/link; chưa có mapping cổng firewall/sensor. Số OpenFlow ofport cấp động không được suy ra từ ens hoặc net0; cần đọc lại sau boot.

| QEMU | TAP EVE | Ubuntu / MAC | Cấu hình đã kiểm chứng | Peer dự kiến / trạng thái hiện nay |
|---|---|---|---|---|
'''
    roles = ['Data Center','Employee','Guest','DMZ','Management','OPNsense Primary','OPNsense Secondary','Suricata capture']
    for i in range(8):
        config = 'Access VLAN '+str([30,40,50,60,99][i]) if i < 5 else ('Trunk 30,40,50,60,99' if i < 7 else 'Ngoài OVS, chưa Mirror')
        doc += f'| net{i} | vunl0_3_{i} | ens{i+3} / 02:53:45:f2:19:{i:02x} | {config} | {roles[i]}; chưa nối |\n'
    doc += '''
Local Port br-core-l2 là interface nội bộ thuộc access VLAN99, không phải vNIC thứ chín, không IP. Tám MAC không đổi trong lần cấu hình. Chưa tuyên bố peer, network_id hoặc carrier end-to-end khi chưa có kết nối.

## 2.5. Cấu hình bridge thực tế, sao lưu và xử lý lỗi

OVSDB schema 8.5.1 được backup online bằng ovsdb-client vào thư mục root-only trước giao dịch, kiểm tra schema và đọc/compact sang bản sao riêng. Không compact DB đang chạy và không ghi QCOW2. Snapshot đầu tiên /root/m2-isolated-20261101T0035/ovsdb.before dùng để trở về OVS rỗng; không dùng lại cho rollback giai đoạn mới đã có bridge.

Lần áp dụng đầu bị guard chặn vì kernel tạo route multicast IPv6 ff00::/8 trên bridge mới. Restore snapshot trả mã 0; link/address/route về baseline được đối chiếu. Sau đó chỉ tắt IPv6 host stack trên interface nội bộ mới, đặt addrgenmode none và bật bridge; không đổi forwarding hay IPv6 trên tám NIC cũ. Lần áp dụng thứ hai đạt kiểm tra tĩnh. Đây là lỗi và rollback thực tế, không xóa khỏi báo cáo. File failure.json còn trong minh chứng là lịch sử lần đầu, không phải kết quả cuối.

Giao dịch cấu hình năm access và hai trunk được giữ ở guest/applied-transaction.json cùng commands.jsonl. Không chạy lại mẫu cũ có cả mirror. Đọc lại ovs-vsctl show sau cấu hình cho kết quả nguyên văn:

```text
'''+runtime['show'].rstrip()+'''
```

Bridge dùng system datapath, standalone và NORMAL switching, không controller/bond/LACP. Interface.error rỗng, ofport hợp lệ. Bridge admin UP; operstate UNKNOWN của interface nội bộ và dòng ovs-system DOWN không tự chứng minh bridge lỗi. Datapath có đủ bảy cổng vật lý và local port. Counter frame ở mốc đó bằng 0, vì chưa có phát lưu lượng thử.

Trong đợt tăng tốc trước khi chuyển sang chế độ nhẹ, Core đã tắt nên sao lưu thêm overlay nguyên byte tại /root/m2-stopped-backup-20261101T075852Z/core-overlay.qcow2, 712310784 byte. Hash nguồn trước/sau và bản sao đều bằng:

```text
'''+backup['backup_sha256']+'''
```

Không ghi đè image gốc, không sửa nguồn QCOW2, không khởi động guestfs/helper VM. Chưa thử restore overlay. Script backup ban đầu gặp tương thích hashlib.file_digest của Python trên EVE; đã đổi sang SHA-256 đọc từng khối và chạy lại thành công. Thư mục của lần dừng sớm được giữ nguyên, không xóa dữ liệu. Sau yêu cầu chế độ nhẹ không tiếp tục backup nặng hoặc thao tác EVE.

## 2.6. Nguyên lý chuyển mạch, VLAN và mirror

OVS là Open vSwitch, tên chính thức của bộ chuyển mạch phần mềm. ovsdb-server giữ cấu hình Bridge/Port/Interface/Mirror, ovs-vswitchd điều khiển datapath; datapath kernel chuyển frame. NORMAL switching học nguồn MAC theo VLAN để chọn cổng đích, flood broadcast/đích chưa biết trong cùng VLAN và áp dụng chính sách VLAN. FDB (Forwarding Database, cơ sở dữ liệu chuyển tiếp) và counter hỗ trợ giải thích đường gói nhưng phải kết hợp capture thật. [Giới thiệu OVS](https://docs.openvswitch.org/en/stable/intro/what-is-ovs/).

VLAN (Virtual Local Area Network, mạng cục bộ ảo) chia miền quảng bá. Access port phân loại frame endpoint không thẻ vào tag của port; egress access thường không mang thẻ. IEEE 802.1Q cung cấp thẻ bốn byte trong Ethernet, gồm TPID và TCI; phần VID nhận dạng VLAN. Trong thiết kế Core, trunk ens8/ens9 mang đúng 30/40/50/60/99, không native VLAN. Kiểm tra cột tag/trunks chỉ chứng minh cấu hình; cần phát/thu frame để xác minh thêm/bỏ thẻ và cách ly. [OVS VLAN FAQ](https://docs.openvswitch.org/en/stable/faq/vlan/).

SPAN (Switched Port Analyzer) là tên chức năng giám sát cổng thường gặp; OVS thực hiện port mirroring qua đối tượng Mirror. Thiết kế chọn ingress bảy port dữ liệu, giới hạn năm VLAN, select_dst_port rỗng và output_port ens10 dành riêng. Cổng mirror không làm NIC quản trị và không chuyển tiếp lưu lượng sensor gửi ngược như port dữ liệu thông thường. Chưa cấu hình hoặc capture ens10; tag trên bản sao, số bản sao và mất gói phải đo, không giả định. [OVS Basic Configuration](https://docs.openvswitch.org/en/stable/faq/configuration/).

Core vận chuyển và phân vùng lưu lượng của SOC; firewall quyết định quyền liên vùng. Mirror giúp sensor quan sát bản sao phục vụ phát hiện, nhưng không tạo quyền chặn gói gốc hoặc giải mã mọi lưu lượng. Chưa chạy Suricata, chưa có cảnh báo IDS/IPS hoặc tích hợp Wazuh được nghiệm thu.

## 2.7. Bảng kết quả thực tế và giới hạn nghiệm thu

| Hạng mục | Kết quả | Bằng chứng / giới hạn |
|---|---|---|
| OVS 3.3.9 và ba dịch vụ | PASS tại mốc chạy trước | Ảnh version/services và log cài; node hiện tắt |
| Mapping tám NIC | PASS ở runtime trước | CSV MAC QEMU/TAP/ens; cần đọc lại sau bật |
| Bridge, năm access, hai trunk | PASS cấu hình tĩnh/runtime trước | after.json, show, Port/Interface; không thay lưu lượng thật |
| Core không IP/gateway, forwarding 0/0 | PASS ở mốc cấu hình | ip/route/sysctl và ảnh; chưa kiểm tra sau reboot |
| Rollback lần tạo bridge đầu | PASS thực tế | attempt1-restored.json, rollback RC0, đối chiếu baseline |
| Backup overlay khi tắt | PASS toàn vẹn bản sao | stopped-backup.json; chưa kiểm thử restore |
| VLAN isolation/access/trunk/802.1Q bằng frame | NOT RUN | Chưa có PCAP hoặc kết quả truyền frame |
| Mirror ens10 | NOT CONFIGURED / NOT RUN | ens10 ngoài OVS ở mốc trước |
| Persistence và thử lại sau boot | NOT RUN | Không dùng trạng thái DB trước shutdown để kết luận |
| Gateway/CARP/pfsync/XMLRPC/firewall/NAT | NOT IMPLEMENTED | M3 còn thiết kế, chưa có image firewall trong kho đã kiểm kê |
| Topology GUI mới | MISSING | Có log lab một node/không link; không thay bằng sơ đồ thiết kế |

Không nghiệm thu chức năng chuyển mạch M2 toàn bộ khi chưa có frame thật. Không biến cảnh báo tài nguyên thành FAIL chức năng của OVS; ca bị chặn ghi NOT RUN/BLOCKED. Không khẳng định có ảnh topology hoặc capture chưa thu.

## 2.8. Thuật ngữ phục vụ giải thích hệ thống

'''
    glossary = prior.split('### 2.20.1.')[1].split('### 2.20.2.')[0]
    glossary = glossary[glossary.index('| Thuật ngữ'):]
    replacements = {
        'dự kiến tạo bridge br-core-l2 để nối các vùng SOC.':'đã tạo br-core-l2 ở mốc runtime trước; chưa nối peer hoặc thử frame.',
        'Dự kiến br-core-l2 chứa các port access/trunk; bridge chưa tạo trong bước cài phần mềm.':'br-core-l2 đã chứa năm access và hai trunk; chưa thử chuyển tiếp thực tế.',
        'cấu hình thực tế còn chờ.':'tag access đã kiểm chứng; chuyển tiếp frame còn chờ.',
        'Ví dụ dự kiến tag=30 cho cổng Data Center; chưa gán ens3 hoặc cổng cụ thể.':'ens3 tag=30 cho Data Center đã xác minh tĩnh; chưa thử frame.',
        'Tiến trình QEMU thực tế đang phục vụ SOC-Core-L2 với 8 thiết bị VirtIO; không khởi động QEMU phụ.':'QEMU từng chạy Core với tám VirtIO NIC; ở kiểm kê mới QEMU đã tắt.',
    }
    for old, new in replacements.items():
        assert old in glossary
        glossary = glossary.replace(old,new)
    doc += glossary
    doc += '''
Các dẫn số [1]–[11] trong bảng thuật ngữ đối chiếu tài liệu chính thức ở mục 2.12. Những ví dụ firewall/sensor là dự kiến. Khái niệm đã được giải thích theo tên đầy đủ khi có viết tắt; các tên riêng QEMU, OPNsense, cloud-init, NoCloud, Suricata và Wazuh giữ đúng tên sản phẩm/cơ chế.

## 2.9. Minh chứng hình ảnh đã thu

Ảnh dưới đây là tệp thật đã lưu từ các phiên trước, nhúng nguyên byte và chú thích lại cho bản hợp nhất. Không phải ảnh mới của đợt chế độ nhẹ. Thời điểm dựa metadata collector UTC+07:00 khi có; đồng hồ guest/EVE chỉ tham khảo. Danh mục có hash/đường dẫn/thời điểm ở docs/evidence/M2/light-documentation-20261101/evidence-index.csv.

'''
    figures = [
        ('M2-core-l2-8-vnic-verified.png','Tám NIC Ubuntu trước cài OVS','Kiểm tra guest nhận đủ ens3–ens10. Nội dung hiển thị giao diện thật; kết quả đủ tám NIC tại mốc chụp. Ý nghĩa là nền tảng đối chiếu MAC, chưa xác nhận peer.'),
        ('M2-core-l2-disk-verified.png','Đĩa và phân vùng của Core','Kiểm tra dung lượng đĩa. Nội dung lsblk/df thể hiện vda 8 GiB; kết quả phản ánh mốc trước cài đặt. Ý nghĩa là đánh giá chỗ cho bộ gói, không thay số đo hiện tại.'),
        ('M2-ovs-offline-update3-final-20261031T235646+0700.png','Cập nhật chỉ mục APT offline','Kiểm tra nguồn cục bộ dùng được. Nội dung là kết quả apt update với kho file; đạt ở lệnh này. Ý nghĩa là cài OVS không cần Internet guest.'),
        ('M2-ovs-simulation-summary-hashes-20261031T235739+0700.png','Dependency và checksum bộ gói offline','Kiểm tra kế hoạch dependency và hash gói. Kết quả ở màn hình thật phục vụ đối chiếu bundle 70 gói; không nói rằng đã cài cả 70. Ý nghĩa là giảm rủi ro cài thiếu phụ thuộc.'),
        ('M2-ovs-installed-verification-20261031T235923+0700.png','OVS 3.3.9 sau cài đặt, chưa có bridge ở mốc cũ','Kiểm tra version và dịch vụ sau cài. Kết quả 3.3.9/schema 8.5.1 và active; OVSDB lúc này chưa có bridge. Ý nghĩa là mốc lịch sử trước bước cấu hình, không mâu thuẫn với bridge tạo sau đó.'),
        ('M2-ovs-repository-signatures-20261031T235957+0700.png','Chữ ký chỉ mục Ubuntu','Kiểm tra nguồn metadata. Nội dung xác minh ba chữ ký; kết quả dùng cho bước offline. Ý nghĩa là tách kiểm tra nguồn gói với kiểm tra runtime OVS.'),
        ('isolated-bridge-20261101/backup-ready-20261101T005559+0700.png','Metadata bản sao OVSDB trước cấu hình','Kiểm tra snapshot và schema. Kết quả cho thấy metadata root-only và checksum. Ý nghĩa là sẵn đường phục hồi; ảnh này riêng lẻ không chứng minh restore.'),
        ('isolated-bridge-20261101/configured-show-1-20261101T010433+0700.png','Cấu hình br-core-l2, phần 1','Đối chiếu output ovs-vsctl show thật. Kết quả hiển thị một phần bridge/port sau cấu hình. Ý nghĩa là bằng chứng DB; xem tiếp hình sau để đủ output.'),
        ('isolated-bridge-20261101/configured-show-2-20261101T010444+0700.png','Cấu hình br-core-l2, phần 2','Hoàn thiện đối chiếu show. Kết quả bổ sung các cổng và phiên bản của bridge. Ý nghĩa là xác minh cấu hình đầy đủ, chưa phải thử frame.'),
        ('isolated-bridge-20261101/configured-ports-20261101T010523+0700.png','Bảng access và trunk đọc từ OVS','Kiểm tra tag/vlan_mode/trunks. Kết quả năm access và hai trunk đúng danh sách VLAN; local Port access99. Ý nghĩa là tránh nhầm port trước thử lưu lượng.'),
        ('isolated-bridge-20261101/configured-datapath-20261101T010534+0700.png','Datapath và Interface sau cấu hình','Kiểm tra port được datapath nhận và lỗi interface. Kết quả runtime ở mốc cô lập, chưa có frame thử. Ý nghĩa là điều kiện cần trước nghiệm thu forwarding.'),
        ('isolated-bridge-20261101/configured-l2-20261101T010544+0700.png','Không IP/gateway, forwarding 0/0, ens10 ngoài OVS','Kiểm tra vai trò Layer 2. Nội dung ip -br addr và kết quả forwarding/Mirror; chỉ loopback có địa chỉ, forwarding0/0, không mirror/ens10. Ý nghĩa là Core không đóng vai gateway.'),
    ]
    evidence_rows = []
    image_hashes = []
    for number, (rel, title, explanation) in enumerate(figures,1):
        image = EV/rel
        assert image.is_file()
        image_hashes.append(sha(image))
        doc += f'![{title}](../evidence/M2/{rel})\n\n**Hình 2.{number}. {title}**\n\nMục đích: {explanation}\n\n'
        meta = image.with_suffix('.json')
        time = 'Không có timestamp collector độc lập; giữ nguyên tên tệp nguồn, không suy từ giờ sửa tệp'
        if meta.is_file():
            record = json.loads(meta.read_text(encoding='utf-8-sig'))
            time = record.get('collector_time_start',record.get('collector_time_end',time))
        elif re.search(r'\d{8}T\d{6}\+0700',image.name):
            time = 'Theo tên tệp nguồn: '+re.search(r'\d{8}T\d{6}\+0700',image.name).group()
        evidence_rows.append([image.name,title,time,str(image.relative_to(ROOT)),f'2.9 / Hình 2.{number}',sha(image)])
    doc += '''
## 2.10. Kiểm thử đã chuẩn bị và điều kiện chạy tiếp

Kịch bản chi tiết và bảng điều kiện/thao tác/kết quả/bằng chứng nằm trong M2-test-and-rollback-PREPARED-20261101.md và .csv. Bộ frame có 31 case trước mirror, 32 khi mirror; bao gồm broadcast, learned unicast, hai trunk/năm VLAN, sai VID/untagged, đối chứng dương và kiểm tra mirror không chuyển tiếp ngược. Mọi ca frame đều NOT RUN.

Phương án ưu tiên dùng AF_PACKET trên tám TAP riêng của Core, không nối bridge ngoài EVE, không thêm endpoint VM. Chỉ frame mang marker phiên được ghi; loại bản PACKET_OUTGOING để không nhầm gói phát với kết quả qua guest. Bản PCAP mới chỉ được coi là minh chứng khi phát/thu thành công và có counter/FDB, thời gian và đối chứng tương ứng. Không dùng mô phỏng trace làm thay capture thật.

Đã chuẩn bị script m2_tap_frame_test.py, m2_mirror_guest_prepared.py và mẫu unit/helper soc-core-l2-noip; chưa chạy trên runtime Linux/OVS. Snapshot mới trước mirror phải giữ cấu hình bảy port hiện hữu, không khôi phục nhầm snapshot OVS rỗng. Persistence thử boot trước sửa để biết trạng thái thật; nếu cần triển khai unit thì kiểm tra xung đột tệp, backup và không đổi forwarding. Sau reboot phải thử lại frame, không chỉ đọc DB.

## 2.11. Tài nguyên, việc còn thiếu và kế hoạch trước hạn nộp

Windows 16 GiB đang chạy Labtainer và chỉ còn khoảng 0,5 GiB available ở tiền kiểm tra, sau đó có mẫu thấp hơn 0,1 GiB. EVE 7897 MiB tổng/6531 MiB available khi chưa có QEMU không bảo đảm Windows còn headroom. Không bật Core hoặc VM khác trong chế độ nhẹ. Việc xác nhận tài nguyên sẵn sàng phải do người dùng thông báo, rồi mới đo lại.

Ưu tiên sau khi đủ RAM: bật duy nhất Core theo cách EVE chuẩn, thu baseline sau boot, backup mới, thử frame trước mirror, thêm mirror đúng mapping, thử lại/capture, triển khai persistence có rollback nếu cần và thử sau reboot. Khi đó mới cập nhật bảng PASS/FAIL lưu lượng. Ảnh topology GUI và kiểm tra phân trang Word vẫn còn thiếu; không có ảnh mới khi Core tắt.

M3: kiểm kê chưa có OPNsense. Kế hoạch Primary/Secondary, CARP VIP, pfsync, XMLRPC, VLAN gateway, ma trận firewall và triển khai tuần tự nằm trong ../M3/M3-OPNsense-HA-PROPOSED-20261101.md. Một firewall có thể là bản trình diễn tối thiểu sau khi đủ tài nguyên; chạy tuần tự hai firewall không được nghiệm thu HA. Core2048 + hai firewall3072 mỗi máy đã là8192 MiB, vượt tổng EVE7897 trước overhead. Chưa tải image hoặc sửa NAT/firewall/đường WAN.

Mốc dự kiến để ưu tiên trước 05/11/2026: hoàn thiện bộ chứng cứ M2 ngay khi tài nguyên sẵn sàng; sau đó demo một OPNsense và rule/gateway thực tế; HA chỉ triển khai nếu có ngân sách được xác nhận. Các ngày là kế hoạch, không bảo đảm kết quả chưa thử. Git chỉ lưu script/tài liệu/minh chứng sạch, không raw backup, PCAP, QCOW2, ISO hoặc bí mật.

## 2.12. Nguồn chính thức và đối chiếu hồ sơ

'''
    sources = prior.split('### 2.20.2. Tài liệu chính thức')[1].split('## 2.21.')[0]
    doc += sources
    doc += '''
Hồ sơ nguồn: M2-report-ovs-offline-installed-20261101.docx; M2-report-port-mapping-and-ovs-design-20261101.docx; M2-report-isolated-bridge-configured-20261101.docx. Tất cả giữ nguyên. Dữ liệu chính: isolated-bridge-20261101/guest/commands.jsonl, after.json, result.json, attempt1-restored.json và configured-port-mapping.csv; kiểm kê mới port-design-20261101T075757+0700/eve-inventory.json; backup mới accelerated-20261101/stopped-backup.json. Danh mục và checksum của bản hợp nhất được lưu riêng.
'''
    with SOURCE.open('x',encoding='utf-8',newline='\n') as f:
        f.write(doc)
    build(SOURCE)
    target = SOURCE.with_suffix('.docx')
    ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.endswith('.xml'):
                ET.fromstring(z.read(name))
        embedded = [hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')]
        assert embedded == image_hashes
        document = ET.fromstring(z.read('word/document.xml'))
        pg = document.find('.//w:pgSz',ns)
        margins = document.find('.//w:pgMar',ns)
        w = '{'+ns['w']+'}'
        assert pg.get(w+'w') == '11906' and pg.get(w+'h') == '16838'
        assert margins.get(w+'left') == '1701' and all(margins.get(w+x) == '1134' for x in ['right','top','bottom'])
        assert b'Times New Roman' in z.read('word/styles.xml')
        assert len(document.findall('.//w:drawing',ns)) == len(figures)
    assert all(sha(ROOT/path)==digest for path,digest in old_reports.items())
    # Master table export for review, not an execution result.
    test_source = (DOCS/'M2-test-and-rollback-PREPARED-20261101.md').read_text(encoding='utf-8')
    rows = [line for line in test_source.splitlines() if line.startswith('| L')]
    with (DOCS/'M2-test-cases-PREPARED-20261101.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID_nhom','muc_tieu','dieu_kien','thao_tac','ket_qua_mong_doi','bang_chung_can_thu','trang_thai'])
        for line in rows:
            writer.writerow([cell.strip() for cell in line.strip('|').split('|')])
    for path, description, section in [
        (EV/'accelerated-20261101/stopped-backup.json','Metadata backup overlay khi node tắt','2.5'),
        (EV/'port-design-20261101T075757+0700/eve-inventory.json','Kiểm kê EVE: không QEMU, không image firewall','2.1/2.11'),
        (EV/'port-design-20261101T075757+0700/windows-memory.json','RAM Windows ở tiền kiểm tra','2.11')]:
        timestamp = 'Thời điểm thu có trong nội dung; EVE UTC không tin cậy nếu chưa đồng bộ'
        if path.name == 'eve-inventory.json':
            timestamp = json.loads(path.read_text())['collector_time_end']
        if path.name == 'windows-memory.json':
            timestamp = json.loads(path.read_text(encoding='utf-8-sig'))['CollectedAt']
        evidence_rows.append([path.name,description,timestamp,str(path.relative_to(ROOT)),section,sha(path)])
    with (OUT/'evidence-index.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ten_tep','noi_dung','thoi_diem_va_mui_gio','duong_dan','vi_tri_bao_cao','sha256'])
        writer.writerows(evidence_rows)
    receipt = {'collector_time':NOW,'report':str(target.relative_to(ROOT)),'sha256':sha(target),
               'embedded_images':len(figures),'exact_image_bytes':True,'previous_reports_unchanged':old_reports,
               'validation':'ZIP/XML/A4/TNR 13pt body/12pt tables, required margins; GUI pagination not inspected',
               'frame_tests_executed':False,'new_mirror_applied':False,'persistence_tested':False,
               'vm_started':False,'new_evidence_images_created':False,'mode':'Light documentation only after user instruction'}
    (OUT/'validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+str(p.relative_to(ROOT)).replace('\\','/') for p in [SOURCE,target,DOCS/'M2-test-and-rollback-PREPARED-20261101.md',DOCS/'M2-test-cases-PREPARED-20261101.csv',ROOT/'docs/M3/M3-OPNsense-HA-PROPOSED-20261101.md'])+'\n',encoding='utf-8')
    print(json.dumps({'report':str(target),'images':len(figures),'previous_reports_unchanged':True,'frame_tests_executed':False},ensure_ascii=False))


if __name__ == '__main__':
    main()
