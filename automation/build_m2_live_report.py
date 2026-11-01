"""Build M2 delivery only from completed real frame suites and changed boot ID."""
import collections
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
from export_m2_report_docx import build

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'docs/evidence/M2/live-tests-20261101'
DATA=EV/'final-collection'
DOC=ROOT/'docs/M2/M2-report-functional-tests-verified-20261101.md'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    q=json.loads((DATA/'queue-receipt.json').read_text())
    assert q['stages']['collect']['status']=='DONE' and q['stages']['reboot']['status']=='DONE'
    stages=['vlan-trunk','mirror-traffic','postboot-traffic']
    suites={s:json.loads((DATA/s/'result.json').read_text()) for s in stages}
    assert [len(suites[s]['cases']) for s in stages]==[31,32,32]
    assert all(d['completed'] and d['all_cases_passed'] and not d['final_guard_error'] for d in suites.values())
    states=[]
    for p in (DATA/'guest-public-replies').glob('*-verified-reply.json'):
        r=json.loads(p.read_text())
        if r['rc']==0:
            o=json.loads(r['stdout']);states.append(o['state'])
    final=next(s for s in reversed(states) if s['boot_id']!=q['initial_boot_id'])
    assert final['forward4']==final['forward6']=='0' and len(final['ports'])==9 and len(final['mirrors'])==1
    assert all(not a['addr_info'] for a in final['addresses'] if a['ifname']!='lo')
    old_reports={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'docs/M2').glob('*.docx')}
    counts={s:dict(collections.Counter(str(e['vlan']) for e in suites[s]['events'] if e['tap']=='vunl0_3_7')) for s in stages}
    doc='''# CHƯƠNG 2. TRIỂN KHAI VÀ KIỂM THỬ CORE LAYER 2 BẰNG OPEN vSWITCH

## 2.1. Kết quả thực tế ngày 01/11/2026

Đã hoàn thành bộ kiểm thử Core Layer 2 trong lab M2 cô lập: **95/95 ca frame thực tế đạt, 0 ca frame thất bại**; gồm31 ca trước mirror,32 ca sau mirror và32 ca sau reboot. OVS3.3.9 giữ đúng năm access, hai trunk và cổng ens10 mirror chuyên dụng. Persistence đã được kiểm tra bằng boot_id thay đổi, đọc lại cấu hình/dịch vụ và chạy lại frame, không chỉ dựa vào OVSDB còn dữ liệu.

Kết luận chỉ áp dụng mẫu frame Ethernet phát128byte, các VLAN30/40/50/60/99, unicast/broadcast và phép đo hữu hạn trong lab. Chưa kiểm tải cao, IPv6 payload, ứng dụng TCP/IP qua firewall, OPNsense HA, Suricata IDS hoặc Wazuh. Không lấy PASS của kiểm tra tĩnh/mock làm kết quả mạng;95 ca trên được thu từ socket nhận frame thật ở TAP phía EVE sau khi frame đi qua guest.

Thời gian trong báo cáo dựa collector Windows UTC+07:00. Đồng hồ EVE/guest được ghi nhưng chưa coi là đồng bộ; timestamp PCAP cần đọc cùng metadata collector. Báo cáo mới không ghi đè các báo cáo cài đặt, mapping hoặc chuẩn bị trước đó.

## 2.2. Phạm vi và môi trường đã xác minh

EVE-NG192.168.220.143, lab SOC-M2-Core-L2, Core ID3/UUID2b295168-b72e-4de7-b364-37298252dd9f, Ubuntu24.04,1vCPU,2048MiB RAM,8vNIC. Chỉ bật Core; không bật OPNsense/Suricata hoặc endpoint VM. Lab vẫn không có EVE network/link và TAP không có bridge master, nên không có segment ngoài Core để frame đi tắt.

OVS3.3.9 đã cài offline từ đợt trước, schema8.5.1. Không cài lại gói hoặc tạo lại bridge. Không sửa image gốc, seed NoCloud, mạng VMware/Windows/Labtainer hoặc firewall/NAT. Các thay đổi cấu hình và ghi log diễn ra trong filesystem guest/OVSDB; không ghi trực tiếp QCOW2 từ host khi VM chạy.

Hồ sơ cài đặt trước đó đã kiểm bộ70 gói .deb, sáu chỉ mục và ba chữ ký InRelease Ubuntu; dependency thực tế cần bảy gói mới. Phiên bản gói3.3.9-0ubuntu0.24.04.1, kho file:/opt/ovs-offline với noble/noble-updates/noble-security. Không đồng nghĩa đã cài cả70 gói. Các lỗi nguồn thiếu noble-updates/metadata phụ CNF-DEP11 đã xử lý ở mốc cũ; không sửa DNS/Internet để cài lại trong đợt thử này. Ubuntu là Ubuntu24.04 dùng vai trò Core, không gọi nhầm thành sản phẩm Ubuntu Core dạng immutable.

## 2.3. Mapping và cấu hình cuối

| QEMU | TAP EVE | NIC Ubuntu / MAC | Cấu hình đã kiểm chứng | Vai trò |
|---|---|---|---|---|
'''
    roles=['Data Center','Employee','Guest','DMZ','Management','OPNsense Primary — peer chưa triển khai','OPNsense Secondary — peer chưa triển khai','Output mirror — chưa có sensor VM']
    for i in range(8):
        config='Access VLAN '+str([30,40,50,60,99][i]) if i<5 else ('Trunk30,40,50,60,99' if i<7 else 'Mirror output, trunk30,40,50,60,99')
        doc+=f'| net{i} | vunl0_3_{i} | ens{i+3} / 02:53:45:f2:19:{i:02x} | {config} | {roles[i]} |\n'
    doc+='''
br-core-l2 dùng system datapath, standalone, local internal Port access99 không IP. Không controller, bond hoặc LACP. Hai trunk không native VLAN. Mirror span-suricata chọn ingress ens3–ens9, select_vlan30/40/50/60/99, select_dst_port rỗng và output_port ens10; không select_all. ens10 không phải NIC quản trị và phép thử gửi ngược đã bị bỏ. Số OpenFlow ofport cấp động, không suy từ tên ens.

Output ovs-vsctl show được đọc từ guest sau reboot:

```text
'''+final['show'].rstrip()+'''
```

## 2.4. Phương pháp phát/thu lưu lượng thật

AF_PACKET là giao diện socket Ethernet của Linux. Bộ thử bind riêng tám TAP có sẵn trên EVE: phát ra TAP vào QEMU/vNIC tương ứng, chỉ thu frame guest trả ra từ các TAP khác. Script kiểm đúng QEMU netdev→TAP→MAC, không có master bridge, không thêm link/VM hoặc IP. Loại PACKET_OUTGOING để không dùng bản phát làm chứng cứ chuyển tiếp. Chỉ marker ngẫu nhiên của đúng phiên được lưu.

Frame dùng EtherType0x88b5, dài128byte tại điểm phát và chứa payload đánh dấu; đây là Ethernet kiểm thử thật, không phải ping hoặc mô phỏng ofproto/trace. Điểm thu thực tế có124/128/132byte do bỏ/giữ/thêm thẻ802.1Q. PACKET_AUXDATA được dùng khi kernel đưa VLAN tag vào metadata, phục hồi TPID/TCI cho PCAP. Capture được phân tích lại khi tải về, kiểm cấu trúc, marker và SHA-256; không tạo PCAP từ kết quả mong đợi.

Mỗi ca chờ0,5giây; ca âm có đối chứng dương và ca dương cuối suite. Không nhận frame trong cửa sổ này chỉ được kết luận trong phạm vi phép thử, không khẳng định an toàn với mọi tải/kiểu frame. Các suite phải đủ31/32 ca và final guard hợp lệ; phiên bị ngắt không được coi là đạt.

## 2.5. Bảng kết quả lưu lượng

| Nhóm thực tế | Số ca | PASS | FAIL | Frame guest trả ra | Chứng cứ |
|---|---|---|---|---|---|
'''
    labels={'vlan-trunk':'Access/trunk/isolation trước mirror','mirror-traffic':'Sau cấu hình mirror','postboot-traffic':'Sau reboot/persistence'}
    for s in stages:
        d=suites[s];doc+=f'| {labels[s]} | {len(d["cases"])} | {sum(c["status"]=="PASS" for c in d["cases"])} | 0 | {len(d["events"])} | final-collection/{s}/result.json và8 PCAP TAP |\n'
    doc+='''
Chi tiết95 dòng ở final-collection/frame-cases.csv; mỗi ca có ingress, VLAN phát, tập cổng/VLAN mong đợi, tập nhận thực tế và số bản sao mirror. Access5 ca, trunk10 ca, negative trunk4 ca, wrong-tag access1 ca, learned-unicast10 ca và đối chứng cuối1 ca; suite mirror thêm1 ca ingress trên ens10. Không đếm14 mock/static test vào bảng này.

Các access nhận untagged; trunk nhận đúng VID được phép. Không rò sang access VLAN khác trong các ca quan sát; VID100/untagged trên trunk và tagged40 vào access30 bị bỏ. Các ca unicast sau học MAC chỉ đi tới đúng đích, không flood trunk còn lại. Không thử trực tiếp hai access cùng VLAN vì thiết kế cuối mỗi VLAN chỉ có một access; phép cùng VLAN dùng access↔trunk độc lập.

## 2.6. SPAN/Mirror thực tế

Suite sau mirror có26 bản sao trên TAP ens10, phân bố VID30:6, VID40/50/60/99:5 mỗi VLAN. Counter Mirror trước reboot tx_packets26/tx_bytes3328 đọc bằng console thật. PCAP mirror thực tế gồm11 frame132byte và15 frame128byte, tổng3372byte: chênh44byte tương ứng11 thẻ802.1Q bổ sung. Đây là đối chiếu vị trí đếm dựa trên capture, không đồng nhất byte counter với byte PCAP hoặc coi chênh lệch này là packet drop. Sau reboot suite32 ca lặp lại phải có quan sát tương ứng, không suy từ cấu hình Mirror còn tồn tại.

'''
    doc+='Bảng VLAN trên bản sao thu thực tế: '+json.dumps(counts,ensure_ascii=False)+'.\n\n'
    doc+='''Mirror ingress-only tránh nhân bản do chọn cả nguồn và đích trong cùng lần đi qua bridge; phép thử nhỏ không quan sát trùng bản sao ngoài dự kiến. Luồng qua firewall rồi quay lại Core có thể tạo một lần ingress khác; chưa có firewall trong đợt này. Có bản sao không đồng nghĩa đã có alert IDS hoặc chặn gói IPS.

## 2.7. Persistence, lỗi và sao lưu

Lần boot đầu cho thấy OVSDB giữ cấu hình nhưng br-core-l2 admin DOWN. Guard đã chặn trước frame. Helper khôi phục đầu tiên so sánh cả cờ link trong ip -j addr khi chủ đích đổi cờ UP, gây rollback không cần thiết; sau đó bật lại IPv6 đã sinh link-local trên bridge. Lần thử tiếp bị guard không IP chặn. Không che các lần lỗi này hoặc tính chúng thành PASS; chúng không phải ca frame thất bại.

Đã giữ snapshot/log các lần thử, sao lưu OVSDB lần nữa tại /root/m2-runtime-final-20261101/ovsdb.before và đọc/compact bản sao để xác nhận hợp lệ, rồi chỉ đặt addrgenmode none, disable_ipv61 trên interface nội bộ và bật br-core-l2. Không đổi forwarding, NIC cũ, VLAN hoặc tạo bridge. Ảnh runtime-diagnosis/runtime-backup/runtime-restored-up ghi diễn biến. Rollback runtime lần lỗi không khớp hoàn toàn địa chỉ do link-local tự sinh; không gọi lần đó là khôi phục đầy đủ đã đạt.

Snapshot chính trước mirror ở '''+q['backup']['path']+''', schema8.5.1, SHA-256 '''+q['backup']['sha256']+'''. Raw DB chỉ trong guest root-only; backup OVSDB đọc được không thay một phép restore mới nếu chưa thực hiện. Khi rollback có lỗi phải dừng và giữ log, không Wipe/Reset. Snapshot OVS rỗng từ đợt tạo bridge đầu không dùng cho giai đoạn này.

Journal sau reboot vẫn có cảnh báo OVS_CTL_OPTS chưa đặt, được systemd coi là chuỗi rỗng. Các dịch vụ OVS và unit không IP vẫn active,95 ca frame đạt. Chưa chỉnh unit OVS để bỏ cảnh báo; không coi đây là lỗi chuyển mạch.

Persistence dùng soc-core-l2-noip.service và helper tại /usr/local/sbin, sau OVS, chỉ tác động interface nội bộ br-core-l2, không đổi forwarding. Lưu registry/hash tệp để rollback giữ tệp thay vì xóa. Đã reboot mềm guest qua systemd-run/systemctl, không reboot EVE/Windows, không Reset node. Sau boot đọc lại đúng MAC, version, VLAN/Mirror, không IP/gateway và forwarding0/0 rồi chạy32 ca frame.

Sau reboot, /tmp không còn bundle cũ; lần truyền helper lớn tiếp theo bị lỗi giải nén. Guard checksum đã chặn thực thi. Console có dòng nhập dở; đã dừng đúng tiến trình điều phối/client của phiên và gửi Ctrl+C, không dừng VM. Adapter được sửa dùng literal JSON để giảm chuỗi escape, hash từng phần lẫn toàn bộ và thư mục /var/tmp. Lần xuất chỉ đọc nhỏ dùng thư viện đã giữ tại /root/m2-isolated-20261101T0035/guest.py với SHA-256 được xác minh, trả trạng thái thực qua console. Bộ guard hiện hành kiểm dữ liệu đó rồi chính hàm frame_test của bộ điều phối chạy32 ca cuối. Đây là thay đường vận chuyển dữ liệu kiểm chứng, không giả lập kết quả mạng. Log lỗi truyền được giữ cùng kết quả đạt.

'''
    doc+=f'boot_id trước: {q["initial_boot_id"]}; sau: {final["boot_id"]}. Hai giá trị khác nhau là bằng chứng kernel guest đã khởi động lại.\n\n'
    doc+='''## 2.8. Nguyên lý và vai trò trong SOC

OVS (Open vSwitch) gồm ovsdb-server lưu cấu hình, ovs-vswitchd điều khiển datapath và datapath kernel xử lý frame. Bridge học MAC (Media Access Control) theo VLAN trong FDB (Forwarding Database); NORMAL switching chọn cổng đích đã học hoặc flood trong VLAN. Core cung cấp hạ tầng Layer2 cho các vùng SOC, không làm gateway.

VLAN (Virtual Local Area Network) chia miền quảng bá. Access phân loại frame endpoint vào một VLAN và xuất không thẻ; trunk mang nhiều VLAN theo IEEE802.1Q. IEEE là Institute of Electrical and Electronics Engineers; thẻ gồm TPID (Tag Protocol Identifier), TCI (Tag Control Information), trong đó VID (VLAN Identifier) nhận dạng VLAN. Thử frame xác nhận tác dụng phân loại, thêm/bỏ tag và cách ly trong mẫu, thay vì chỉ nhìn tag/trunks của Port.

SPAN (Switched Port Analyzer) là tên chức năng giám sát cổng thường dùng; OVS dùng đối tượng Mirror để sao chép lưu lượng. ens10 nay đã là output chuyên dụng có capture thật, hỗ trợ Suricata quan sát sau này. Gateway liên VLAN dự kiến là CARP VIP trên OPNsense HA; firewall chịu routing/rules/NAT. Các chức năng M3/M4 này chưa triển khai trong đợt M2.

Các thuật ngữ nền tảng và giám sát còn lại được giữ ở mục2.8 của M2-report-consolidated-review-20261101.md và phần M3/M4: QEMU, QCOW2, cloud-init, NoCloud, SSH, LACP, OPNsense, CARP, pfsync, HA, NAT, DHCP, IDS/IPS, Suricata, Wazuh. Chúng là tên chính thức hoặc dạng đầy đủ đã giải thích; ví dụ firewall/sensor vẫn dự kiến. Tài liệu nguyên lý: [OVS](https://docs.openvswitch.org/en/stable/intro/what-is-ovs/), [VLAN](https://docs.openvswitch.org/en/stable/faq/vlan/), [Mirror](https://docs.openvswitch.org/en/stable/faq/configuration/), [OPNsense HA](https://docs.opnsense.org/manual/hacarp.html).

## 2.9. Minh chứng hình ảnh thật

'''
    old_text=(ROOT/'docs/M2/M2-report-consolidated-review-20261101.md').read_text(encoding='utf-8')
    glossary=old_text.split('## 2.8. Thuật ngữ')[1].split('## 2.9.')[0]
    glossary=glossary[glossary.index('| Thuật ngữ'):].split('Các dẫn số')[0]
    updates={
        '| OVS —':'ovsdb-server giữ cấu hình, ovs-vswitchd điều khiển datapath. br-core-l2 đã thử frame thật; Core chỉ Layer2. [1]',
        '| Bridge;':'Học MAC và chuyển frame theo VLAN. br-core-l2 đã có năm access, hai trunk và cổng mirror; bộ95 ca thực tế đạt.',
        '| VLAN —':'Chia miền quảng bá; VLAN30/40/50/60/99 đã kiểm classification/cách ly trong bộ frame hữu hạn, chưa có gateway firewall.',
        '| IEEE 802.1Q;':'Thẻ Ethernet phân biệt VLAN trên trunk. Mẫu thu124/128/132byte đã thể hiện bỏ/giữ/thêm thẻ4byte; TPID/TCI/VID được giải thích ở trên.',
        '| Trunk;':'Mang nhiều VLAN có tag. ens8/ens9 đã thử năm VID được phép và VID100/untagged bị bỏ; chưa có hai firewall peer. [2]',
        '| Access port;':'Phân loại endpoint vào một VLAN, egress không thẻ. ens3 tag30 và ens4–ens7 tag40/50/60/99 đã thử frame thật. [2]',
        '| SPAN —':'OVS dùng Mirror sao chép ingress bảy data port theo năm VLAN tới ens10. Đã có capture bản sao thật; chưa có Suricata sensor. [2]',
        '| Port mirroring;':'Tạo bản sao ngoài đường chuyển tiếp chính. ens10 chuyên dụng, frame gửi ngược không chuyển ra data port; không coi đây là IPS. [2]',
        '| QEMU;':'Cung cấp phần cứng ảo, có thể tăng tốc KVM. Core dùng tám VirtIO NIC, chỉ một QEMU được bật; reboot guest được xác minh bằng boot_id khác nhau.'}
    rows=[]
    for line in glossary.splitlines():
        for prefix,value in updates.items():
            if line.startswith(prefix):line='| '+line.split('|')[1].strip()+' | '+value+' |';break
        rows.append(line)
    doc=doc.replace('## 2.9. Minh chứng hình ảnh thật','\n'.join(rows)+'\n\n## 2.9. Minh chứng hình ảnh thật')
    figures=[('runtime-backup','Backup OVSDB trước khôi phục runtime','Snapshot đã tạo và compact bản sao thành công; giữ raw trong guest, chưa phải phép restore mới.'),
             ('runtime-restored-up','Khôi phục bridge không IP và forwarding0/0','Ảnh sau sửa riêng bridge, không đổi VLAN hoặc địa chỉ/gateway trên Core.'),
             ('preboot-ports','Bảng access/trunk sau thêm cổng mirror','Bảy cổng dữ liệu và ens10 đều đọc từ OVS; trunk ens10 chỉ phục vụ output mirror.'),
             ('preboot-mirror','Mirror trước reboot và26 bản sao','Counter26/3328 tương ứng mẫu frame128byte, không phải thông lượng production.'),
             ('postboot-ports','Port/VLAN sau reboot','Đối chiếu cấu hình cuối với cùng mapping tám NIC; kết hợp suite32 ca sau boot.'),
             ('postboot-l2','Core sau reboot không IP/gateway','Bridge admin UP, không IP, forwarding0/0; loopback giữ địa chỉ cục bộ như trước.'),
             ('postboot-services','Dịch vụ OVS và unit persistence sau boot','Output active/enabled/boot_id dùng cùng JSON để xác nhận persistence thực tế.'),
             ('postboot-datapath','Datapath và MAC đã học sau thử frame','Minh chứng bổ sung runtime/counter; PCAP và ca nguồn–đích mới là bằng chứng chuyển tiếp.')]
    used=[]
    for number,(label,title,explanation) in enumerate(figures,1):
        image=sorted(EV.glob(label+'-*.png'))[-1];used.append(image)
        doc+=f'![{title}](../evidence/M2/live-tests-20261101/{image.name})\n\n**Hình 2.{number}. {title}**\n\nMục đích là đối chiếu trạng thái thực tế với tiêu chí M2. Nội dung và kết quả: {explanation} Ý nghĩa là kiểm chứng có giới hạn đúng mốc thu, không dựng lại màn hình.\n\n'
    doc+='''## 2.10. Bàn giao, giới hạn và điều kiện bắt đầu M3

Đạt bộ thử Core Layer2/mirror/persistence được giao, với95 ca frame và24 PCAP theo TAP được giữ cục bộ; một số PCAP có0 gói ở cổng không nhận trong cửa sổ đo, không phải24 capture đều có dữ liệu. Tất cả ảnh/log cũ giữ nguyên. PCAP là dữ liệu capture thật có marker; .gitignore vẫn loại raw capture/OVSDB/image/token khỏi Git. CSV/JSON/hash và ảnh sạch phục vụ đối chiếu trên repository PRIVATE. Chưa có ảnh topology GUI mới; log XML/QEMU xác nhận một node/không link. Chưa kiểm phân trang bằng Word GUI.

Chưa thực hiện: tải cao/throughput, IPv6 payload, end-to-end TCP/IP qua các peer thật, gateway/rules/NAT/CARP/pfsync/XMLRPC/DHCP trên OPNsense hoặc phát hiện Suricata/Wazuh. Đây là giới hạn, không ghi thành FAIL của95 ca Ethernet. Không bật firewall/sensor trong đợt này.

Để bắt đầu M3 Primary: phê duyệt phạm vi mới; image amd64 chính thức đã xác thực checksum/chữ ký; đo lại Windows RAM/commit và EVE RAM/swap/đĩa; chốt MAC/interface LAN-WAN-SYNC, địa chỉ/subnet/DNS/WAN upstream. Dùng kế hoạch tuần tự, chỉ một firewall trước; cần ngân sách3–4GiB cho firewall và dự phòng host. Cặp HA cùng Core vượt phân bổ EVE hiện có, không nghiệm thu HA bằng hai máy chạy lần lượt. Xem M3-deployment-matrix-and-tests-PREPARED-20261101.md và SOC-execution-resource-plan-20261101.md.
'''
    doc+='\n## 2.11. Nguồn chính thức và hồ sơ trước\n\n'+old_text.split('## 2.12. Nguồn chính thức và đối chiếu hồ sơ')[1]
    doc=re.sub(r'\b(OVS|VLAN|VID|schema|Ubuntu|Core|Ethernet|Layer|ID)(?=\d)',r'\1 ',doc)
    doc=re.sub(r'(\d)(MiB|GiB|GB|byte|vCPU|PCAP)\b',r'\1 \2',doc)
    with DOC.open('x',encoding='utf-8',newline='\n') as f:f.write(doc)
    build(DOC)
    target=DOC.with_suffix('.docx')
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        hashes=[hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')]
        assert hashes==[sha(p) for p in used]
        xml=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        w='{'+ns['w']+'}';pg=xml.find('.//w:pgSz',ns);m=xml.find('.//w:pgMar',ns)
        assert pg.get(w+'w')=='11906' and pg.get(w+'h')=='16838' and m.get(w+'left')=='1701'
        assert all(m.get(w+x)=='1134' for x in ['top','right','bottom']) and b'Times New Roman' in z.read('word/styles.xml')
    assert all(sha(ROOT/p)==h for p,h in old_reports.items())
    index=[]
    for p in used:
        meta=json.loads(p.with_suffix('.json').read_text())
        index.append({'name':p.name,'content':'Actual console screenshot','collector_time':meta['collector_time_start'],
                      'path':str(p.relative_to(ROOT)),'report_position':'2.9','sha256':sha(p)})
    (EV/'report-evidence-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    validation={'collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),
                'frame_tests':95,'pass':95,'fail':0,'real_frame_tests':True,'boot_id_before':q['initial_boot_id'],
                'boot_id_after':final['boot_id'],'postboot_suite_passed':True,'old_reports_unchanged':True,
                'images_embedded_exact_bytes':len(used),'report_sha256':sha(target),'word_gui_pagination_reviewed':False}
    (EV/'delivery-validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(validation))


if __name__=='__main__':main()
