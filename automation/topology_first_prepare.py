"""Lập danh mục thiết kế và gap analysis từ minh chứng; không thay đổi EVE."""
from pathlib import Path
import json, datetime as dt, hashlib, shutil
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'docs/evidence/M2/topology-first-20261102'
EV.mkdir(exist_ok=True)
inventory=ROOT/'docs/evidence/M2/port-design-20261102T125730+0700/eve-inventory.json'
facts=json.loads(inventory.read_text(encoding='utf-8'))
lab=next(l for l in facts['labs'] if l['path'].endswith('/SOC-M2-Core-L2.unl'))
shutil.copyfile(inventory,EV/'inventory-before.json')
nodes=[
 ('OPNsense-Primary','Firewall',4,'M1 hình 2.1; M3 mapping vtnet0 LAN, vtnet1 WAN1, vtnet2 SYNC; NIC bổ sung dành WAN2'),
 ('OPNsense-Secondary','Firewall',4,'M1 hình 2.1 và bảng 2.1; cùng vai trò NIC Primary'),
 ('SOC-Core-L2','Core',8,'M2 mapping đã kiểm chứng; giữ nguyên tám MAC và cấu hình guest'),
 ('Data-Center','VLAN 30',1,'M1 hình 2.1 và bảng 3.2; đại diện vùng, chưa xác định ứng dụng máy chủ'),
 ('Employee','VLAN 40',1,'M1 hình 2.1 và bảng 3.3; endpoint đại diện'),
 ('Guest','VLAN 50',1,'M1 hình 2.1 và bảng 3.3; endpoint đại diện'),
 ('DMZ','VLAN 60',1,'M1 hình 2.1 và bảng 3.2; chưa chốt Web/DNS là bao nhiêu máy riêng'),
 ('Management','VLAN 99',1,'M1 hình 2.1 và bảng 3.3; endpoint quản trị đại diện'),
 ('Suricata-NIDS','SOC',2,'M1 hình 2.1; M4 mục 4.1/4.2: capture riêng, management riêng'),
 ('Wazuh-SOC','SOC',1,'M1 hình 2.1 và bảng 2.1; VLAN/NIC vật lý tới mạng SOC chưa được chỉ định'),
]
links=[
 ('SOC-Core-L2',5,'OPNsense-Primary',0,'Trunk Primary',True),
 ('SOC-Core-L2',6,'OPNsense-Secondary',0,'Trunk Secondary',True),
 ('OPNsense-Primary',2,'OPNsense-Secondary',2,'HA SYNC riêng',True),
 ('SOC-Core-L2',0,'Data-Center',0,'Access VLAN 30',False),
 ('SOC-Core-L2',1,'Employee',0,'Access VLAN 40',False),
 ('SOC-Core-L2',2,'Guest',0,'Access VLAN 50',False),
 ('SOC-Core-L2',3,'DMZ',0,'Access VLAN 60',False),
 ('SOC-Core-L2',4,'Management',0,'Access VLAN 99',False),
 ('SOC-Core-L2',7,'Suricata-NIDS',0,'SPAN capture không IP',False),
 ('Suricata-NIDS',1,'Management',0,'Cùng segment Management theo M4; không nối trực tiếp NIC đã dùng',False),
]
plan={'source':'docs/M1/M1_Thiet_ke_SOC_Core_L2_OPNsense_Giai_thich_thuat_ngu.docx',
 'source_sha256':hashlib.sha256((ROOT/'docs/M1/M1_Thiet_ke_SOC_Core_L2_OPNsense_Giai_thich_thuat_ngu.docx').read_bytes()).hexdigest(),
 'source_figure':'docs/evidence/M1/topology-source-review-20261102/image1.png',
 'lab':lab['path'],'expected_before_sha256':lab['sha256'],
 'nodes':[dict(zip(['name','zone','nic_count','source_and_limit'],n)) for n in nodes],
 'links':[dict(zip(['a','a_interface','b','b_interface','purpose','exists_before'],l)) for l in links],
 'wan_segments':['WAN-ISP-1','WAN-ISP-2'],
 'unresolved':['Internet/upstream chưa có node/image/interface chỉ định: giữ WAN bridge cô lập, không nối pnet/VMware',
 'Wazuh VLAN/IP và đường vật lý chưa chỉ định: tạo node giữ tắt, chưa nối NIC, chưa mô phỏng mũi tên log thành dây trực tiếp',
 'Automation có trong bảng 2.1 nhưng chưa xác định máy riêng: ghi thành phần logic, không tự tạo thêm node',
 'Số lượng máy chủ DC, Web/DNS DMZ, client mỗi vùng và máy SOC chưa có danh sách vật lý; mỗi vùng chỉ một endpoint đại diện',
 'Địa chỉ IP/VIP, policy, DHCP, WAN2/SYNC guest chưa xác nhận; không tự áp dụng IP dự kiến']}
(ROOT/'configs/topology-first-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 1. Phân tích chênh lệch topology SOC','',
 '## 1.1. Nguồn và phạm vi', '',
 'Ngày 02/11/2026, UTC+07:00. Nguồn chính do người dùng xác nhận: Word M1 trong workspace, hình 2.1 nhúng và các tài liệu M2–M4. Không tìm thấy bản .drawio/.vsdx/.unl/.pdf trong workspace; danh mục toàn bộ ảnh/Word/sơ đồ ở `evidence/M1/topology-source-review-20261102/design-file-inventory.json`. Các Word M2/M3 là báo cáo triển khai từng phần, không thay thế sơ đồ kiến trúc M1.', '',
 'Hình M1 được trích nguyên byte tại `evidence/M1/topology-source-review-20261102/image1.png`; đây là sơ đồ thiết kế, không phải screenshot EVE. M1 mục 2.2 nói rõ hình logic không thể hiện đầy đủ số lượng node/cổng vật lý.', '',
 '## 1.2. Kiểm kê hiện hành trước thay đổi','',
 f"SSH đã xác thực; kiểm kê {facts['collector_time_start']}. Lab `{lab['path']}`, UUID `{lab['lab_id']}`, có 3 node, 3 segment/link; không QEMU đang chạy. Cả hai firewall có 3 NIC; Core có 8 NIC. Không chạy lại suite VLAN đã đạt. Bằng chứng: `evidence/M2/topology-first-20261102/inventory-before.json`.", '',
 '| Thành phần theo thiết kế | Đã tồn tại | NIC cần | Gap / trạng thái thực tế |','|---|---|---|---|']
existing={n['attributes']['name']:n for n in lab['nodes']}
for name,zone,nic,source in nodes:
 n=existing.get(name)
 status=('Primary đã cài/boot theo minh chứng M3 ngày 01/11; guest hiện tắt, gateway/HA chưa VERIFIED' if name=='OPNsense-Primary' else 'Core đã CONFIGURED và VERIFIED trong phạm vi 95 ca M2 ngày 01/11; không suy thành E2E VERIFIED' if name=='SOC-Core-L2' else 'Node hiện có; cài đặt guest chưa xác minh') if n else 'Thiếu node; sẽ CREATED_NOT_INSTALLED khi tạo, không đồng nghĩa đã cài dịch vụ'
 lines.append(f'| {name} ({zone}) | {"Có" if n else "Chưa có"} | {nic} | {status}; {source} |')
lines+=['','## 1.3. Đối chiếu dây và interface','','| Nguồn/interface EVE | Đích/interface EVE | Chức năng | Trước thay đổi |','|---|---|---|---|']
for a,ai,b,bi,present,exists in links:
 lines.append(f'| {a}/{ai} | {b}/{bi} | {present} | {"Đúng theo XML hiện hành" if exists else "Thiếu"} |')
lines+=['| WAN-ISP-1 | vtnet1 mỗi firewall | Shared L2 WAN1 | Thiếu |','| WAN-ISP-2 | NIC thứ 4 mỗi firewall | Shared L2 WAN2 | Thiếu NIC và segment |','',
 'Core EVE e0–e7 đã kiểm kê; tương ứng ens3–ens10 theo MAC M2. Firewall vtnet0 LAN, vtnet1 WAN1, vtnet2 SYNC giữ nguyên. NIC thứ tư dự kiến WAN2; tên vtnet3 cần xác minh sau boot, chưa gán interface guest. Không thấy link sai trong ba link hiện có; chưa kiểm thử lưu lượng qua các link đó.', '',
 '## 1.4. Image và cài đặt','',
 'Kho EVE hiện có `opnsense-26.7-soc` (đĩa nền trống và ISO cài), `linux-ubuntu-24.04-ovs` (Ubuntu cloud image), image Core và console-test. Không có image chứa Suricata/Wazuh đã cài. Dùng Ubuntu nền cho các node dịch vụ là hệ điều hành dự kiến; tuyệt đối không báo dịch vụ đã cài chỉ từ tên node. VPCS binary đã kiểm kê cho endpoint đơn giản. Không dùng image/seed Core để nhân bản các máy dịch vụ.', '',
 '## 1.5. Điểm chưa thống nhất và chưa xác định','']
lines += [f'- {s}' for s in plan['unresolved']]
lines += ['- M1 đề xuất IP quản trị Core; M2 đã kiểm chứng Core không IP. Giữ Core không IP, không áp dụng lại đề xuất M1.',
 '- M1 bảng 3.3 thiếu dòng DMZ trong khi hình 2.1 có DMZ; dùng ens6/access60 đã cấu hình và kiểm chứng M2, không thêm Core thứ hai.', '',
 '## 1.6. Tiêu chí trạng thái','',
 '`TOPOLOGY_READY`: đối chiếu đủ node/link vật lý được xác định. `CONFIGURED`: có cấu hình thực tế trên guest. `VERIFIED`: có kiểm thử và minh chứng đúng phạm vi. `CREATED_NOT_INSTALLED`: node tồn tại nhưng chưa cài hoặc chưa xác minh hệ điều hành/dịch vụ. Không đánh dấu toàn mô hình TOPOLOGY_READY khi Wazuh/upstream và số lượng máy chưa đủ đặc tả; có thể đánh dấu từng link/nhóm đã đủ.', '',
 '## 1.7. Kết quả sau dựng','', 'Chưa thực thi tại thời điểm tạo gap analysis; kết quả sau thay đổi phải đối chiếu `TOPOLOGY_FIRST_HANDOFF.md` và inventory-after, không suy từ kế hoạch.']
(ROOT/'docs/TOPOLOGY_GAP_ANALYSIS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Wrote design plan and gap analysis before EVE changes')
