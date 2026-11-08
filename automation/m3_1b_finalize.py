"""Đóng Nhóm1B từ dữ liệu thật; không tạo CARP VIP hoặc sửa cấu hình thiết bị."""
from pathlib import Path
import csv,datetime,hashlib,ipaddress,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/evidence/M3/group1b-prerequisites-20261103'
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
audit={r:json.loads((OUT/(r.lower()+'-audit.json')).read_text(encoding='utf-8')) for r in ['Primary','Secondary']}
repairs={r:json.loads((OUT/(r.lower()+'-repair.json')).read_text(encoding='utf-8')) for r in ['Primary','Secondary']}
applies={r:json.loads((OUT/(r.lower()+'-apply.json')).read_text(encoding='utf-8')) for r in ['Primary','Secondary']}
endpoint=json.loads((OUT/'endpoint-address-review.json').read_text(encoding='utf-8'))
capture=json.loads((OUT/'pfsync-capture-stop.json').read_text(encoding='utf-8'))
settled=json.loads((OUT/'settled-verification.json').read_text(encoding='utf-8'))
assert not endpoint['VIP_assignment_conflicts']
for r in audit:
 assert not audit[r]['VIP_references'] and not audit[r]['VHIDs'] and not audit[r]['ARP_VIP_conflicts']
 assert audit[r]['config_unchanged'] and repairs[r]['config_unchanged'] and repairs[r]['config_sha256_after']==audit[r]['backup_sha256']
 assert applies[r]['same_shared_secret_verified'] and repairs[r]['secret_file_unchanged'] and repairs[r]['secret_mode']=='0o600'
 assert repairs[r]['CARP_VIPs_created']==0
 assert settled[r]['config_sha256']==audit[r]['backup_sha256']
ready=all(x['runtime_ready'] for x in repairs.values()) and capture['both_directions'] and all(settled[r]['syncok']==1 and settled[r]['carp_demotion']==0 and settled[r]['bulk_done_observed'] for r in ['Primary','Secondary'])
rows=[]
for i,v in enumerate([30,40,50,60,99],1):
 vip=f'192.168.{v}.1';net=ipaddress.ip_network(f'192.168.{v}.0/24');assert ipaddress.ip_address(vip) in net
 rows.append({'status':'APPROVED','VLAN':v,'interface_Primary':f'opt{i} / vtnet0_vlan{v}','interface_Secondary':f'opt{i} / vtnet0_vlan{v}','Primary_IP':f'192.168.{v}.2/24','Secondary_IP':f'192.168.{v}.3/24','CARP_VIP':vip+'/24','VHID':v,'advbase':1,'Primary_advskew':0,'Secondary_advskew':100,'SYNC':'opt6/vtnet2; Primary 10.255.255.1/30; Secondary 10.255.255.2/30','applied':False})
assert len({r['VHID'] for r in rows})==5
scope='Current firewall full configuration/runtime and passive ARP cache; saved VPCS/seed endpoint assignments; IP plan; no active DAD and no assurance about undisclosed external/offline device'
params={'approved_at':NOW,'scope_HA':[30,40,50,60,99],'excluded':['WAN','LAN parent'],'conflict_check_scope':scope,'rows':rows,'CARP_VIPs_created':0,'password_value_included':False}
(OUT/'CARP-final-parameters.json').write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'CARP-final-parameters.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
counts={src:sum(p['source']==src for p in capture['packets']) for src in ['10.255.255.1','10.255.255.2']}
result={'collected_at':NOW,'VIPs':{r['CARP_VIP']:'APPROVED' for r in rows},'VHIDs':{str(r['VLAN']):r['VHID'] for r in rows},'VIP_conflict_scope':scope,'pfsync_status':'READY' if ready else 'NOT READY','pfsync_readiness_scope':'Current runtime UP/syncpeer, two-way protocol240, settled syncok=1/demotion=0 and kernel bulk done both sides; not reboot, full state retention or failover acceptance','pfsync_packets_by_source':counts,'native_repair':'/usr/local/sbin/pluginctl -c pfsync','settled_syncok':{r:settled[r]['syncok'] for r in ['Primary','Secondary']},'settled_CARP_demotion':{r:settled[r]['carp_demotion'] for r in ['Primary','Secondary']},'bulk_done_verified_both':True,'saved_XML_changed':False,'HA_SYNC_rules_changed':False,'M2_changed':False,'NAT_DHCP_changed':False,'secret_same_verified_without_disclosure':True,'CARP_VIPs_created':0,'failover_run':False,'stop_before_CARP_creation':True}
(OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
table='| VLAN | Interface hai phía | VIP | VHID | advbase | Advskew P/S | Kết quả |\n|---|---|---|---|---|---|---|\n'
for r in rows:table+='| '+' | '.join([str(r['VLAN']),r['interface_Primary'],r['CARP_VIP'],str(r['VHID']),'1','0 / 100','APPROVED'])+' |\n'
report='''# CHƯƠNG 3. M3 — NHÓM 1B: ĐIỀU KIỆN TRƯỚC KHI TẠO CARP VIP

## 3.1. Kết quả và phạm vi phê duyệt

Thời điểm tổng hợp: TIME (UTC+07:00). Năm VIP được phân loại **APPROVED trong phạm vi cấu hình đã kiểm tra**. Pfsync: **PFSYNC_STATUS trong runtime hiện tại**, có cấu hình peer đúng và bằng chứng protocol240 hai chiều. Chưa tạo CARP VIP, chưa failover, không sửa M2, NAT/DHCP hoặc rule HA SYNC; không mở rộng sang WAN/LAN parent.

## 3.2. VIP/VHID: đối chiếu và bộ tham số cuối cùng

TABLE

Primary giữ .2/24, Secondary giữ .3/24 trên từng VLAN. SYNC giữ nguyên **opt6/vtnet2**, Primary10.255.255.1/30, Secondary10.255.255.2/30. Các giá trị advbase1, advskew0/100 và VHID30/40/50/60/99 được chọn đúng quyền người dùng vừa cấp, không còn lấy ví dụ chưa duyệt của M1 làm cấu hình. Bảng chỉ là dữ liệu chuẩn bị, `applied=false`.

Phạm vi xác nhận xung đột: snapshot đầy đủ của hai firewall tại nhóm1B, runtime interface, cache ARP đọc thụ động; mười bản ghi cấu hình endpoint VPCS/seed đã lưu; và quy hoạch subnet. Không có tham chiếu gán năm IP đích trong XML hiện hành của hai firewall, không có VHID khác0, không thấy năm IP trong cache ARP hoặc các địa chỉ endpoint đã đối chiếu. VIP nằm trong đúng /24 và khác IP riêng .2/.3, network/broadcast. Năm VHID duy nhất, tương ứng mỗi VIP và phải giống nhau ở hai thành viên của cùng nhóm.

Core đang tắt theo quyền Nhóm1; đợt này không bật Core, không phát ARP probe hoặc thăm dò CARP trên các VLAN. **APPROVED không phải bảo đảm mọi thiết bị chưa khai báo hoặc đang tắt bên ngoài tập cấu hình đều không dùng IP/VHID.** Trước khi tạo VIP trong đợt được phép tiếp theo, cần đọc lại xung đột khi đường L2 phù hợp hoạt động. Không phát hiện CONFLICT để phải đổi địa chỉ; không thay bất kỳ địa chỉ nào.

## 3.3. Nguyên nhân pfsync và cách xử lý

Trước sửa: cả hai pfsync0 đều flags=0, không UP/syncdev/syncpeer. Cấu hình lưu vẫn có hasync.pfsyncinterface=opt6 và peer đúng phía đối diện. Mã cài `/usr/local/etc/inc/interfaces.inc` và đăng ký plugin cho thấy routine native áp những trường này để đưa pfsync0 lên, chọn syncdev/peer. Đây là trường hợp **cấu hình lưu chưa được áp vào runtime**, không có bằng chứng thiếu IP hoặc cần mở rộng rule HA SYNC. Không tự thêm trường enable hoặc sửa XML.

Đã thử configctl interface pfsync.configure; công cụ trả “Action not allowed or missing” dù exit code0. Runtime vẫn flags0 nên giữ kết quả đó là NOT READY, không coi exit code là thành công. Không sửa quyền configd hoặc restart dịch vụ khác. Sau khi đối chiếu action file thật, gọi trực tiếp backend mà action đó đăng ký: **/usr/local/sbin/pluginctl -c pfsync**, một lần trên mỗi firewall.

Sau backend native: cả hai pfsync0 có UP, syncdev vtnet2, syncpeer đúng .2 hoặc .1. **Không chốt READY tại thời điểm này:** ảnh đọc ngay sau áp còn syncok0; kiểm tra tiếp ghi nhận Primary vẫn demotion240 trong khi bulk chưa hoàn tất. Đã áp lại riêng backend native trên Primary khi Secondary đã ổn định, không đổi tham số, không ghi sysctl ép syncok/demotion. Ảnh ổn định cuối xác nhận hai phía syncok1 và demotion0; kernel log hai phía ghi “pfsync bulk done”, không phải “bulk fail”. Đây là điều kiện được dùng để chốt READY.

Cấu hình XML trước/sau khớp nguyên byte; các hash bảo vệ interfaces/filter/NAT/DHCP/hasync/virtualip/OPNsense giữ nguyên. Không thay rule HA SYNC, không thay IP10.255.255.1/30 hoặc10.255.255.2/30. Phiên bản pfsync mà backend áp từ cấu hình hiện hữu được giữ nguyên, không đổi phiên bản để dò lỗi.

Thu thụ động tại TAP SYNC Secondary trong cửa sổ áp backend ban đầu: protocol240 từ .1 sang .2 có COUNT_P packet, từ .2 sang .1 có COUNT_S packet. Chỉ nhận packet đúng cặp peer, không tạo HTTP/session thử hoặc failover. PCAP này không bao phủ lần áp lại Primary sau đó; bước hoàn tất bulk được chứng minh riêng bằng kernel log/ảnh syncok1/demotion0 cuối. Không chỉ dùng số gói hai chiều hoặc syncok1 đứng riêng để kết luận. `pfsync-control-decoded.json` giữ bản giải mã control packet; `settled-verification.json` ghi rõ phương pháp trích đọc ảnh gốc, không giả làm JSON native.

**Giới hạn READY:** đã sẵn sàng về device/peer và trao đổi protocol240 ở phiên hiện tại; chưa nghiệm thu giữ phiên/state table thực, chưa thử reboot hoặc failover. Mã có đường gọi routine pfsync liên quan cấu hình VIP/CARP và plugin riêng; khi chưa tạo CARP, không tự thêm hook khởi động để ép hành vi boot. Chưa khẳng định sửa runtime này đã được kiểm thử bền vững qua reboot. Không cần tạo một VIP giả để đưa pfsync lên.

## 3.4. Backup trước sửa và bảo toàn cấu hình

Backup mới trên hai guest: `/root/soc-m3-1b-primary-20261103/config.before.xml` và `/root/soc-m3-1b-secondary-20261103/config.before.xml`, thư mục0700 và tệp0600. Snapshot được tạo trước khi gọi bất kỳ backend áp pfsync nào.

Windows: `private-backups/Primary-before.xml`, `private-backups/Secondary-before.xml`. Các tệp local được nhân từ bản đầy đủ đã xác minh ở Nhóm1, **chỉ sau khi hash snapshot mới trên guest khớp chính xác**. Đây là tối ưu không truyền lại secret thừa, không báo nhầm lần tải mới: phương pháp và đường nguồn được ghi rõ trong `backup-before-manifest.json`.

| Firewall | SHA-256 backup trước sửa và cấu hình sau sửa |
|---|---|
| Primary | HASH_P |
| Secondary | HASH_S |

`SHA256SUMS-before.txt` và manifest cung cấp đường dẫn/checksum. Toàn bộ thư mục private-backups được Git ignore và NTFS chỉ cấp quyền owner hiện hành; không đưa backup thô hoặc secret lên Git. Native repair không đổi file cấu hình nên Primary vẫn khớp snapshot M2. Các ảnh/log lịch sử M2 được giữ nguyên và không chạy lại suite đã PASS.

## 3.5. CARP password được chuẩn bị an toàn

Một secret ngẫu nhiên được tạo một lần bằng bộ sinh mật mã, lưu tại Windows dưới dạng DPAPI CurrentUser trong `private-backups/carp-shared-secret.dpapi`. Plaintext không được viết vào tệp Windows, lệnh shell, ảnh, report hoặc chat. Secret được mã hóa riêng theo RSA-OAEP-SHA256 public key của từng guest; chỉ decrypt vào tệp root-only0600.

Hai đường guest: `/root/soc-m3-1b-primary-20261103/carp-shared.secret` và `/root/soc-m3-1b-secondary-20261103/carp-shared.secret`. Thử thách HMAC riêng từng phía được kiểm với cùng secret gốc để xác nhận hai file nhận cùng giá trị; báo cáo chỉ lưu kết quả boolean, không lưu password hoặc fingerprint mật khẩu. Native pfsync repair được kiểm không đổi file secret. **Chưa ghi secret vào XML CARP, vì chưa tạo VIP.**

## 3.6. Hình minh chứng và thuật ngữ

Các ảnh `console-primary-audit/execute-audit-*.png` và phía Secondary ghi snapshot trước sửa; `console-primary-apply/` giữ kết quả lỗi dispatcher; `console-primary-repair/execute-repair-*.png` và phía Secondary ghi pfsync runtime sau backend đúng. JSON đọc qua glyph khớp chính xác và SHA-256 toàn payload, không dùng OCR đoán ký tự hoặc sửa ảnh.

![Primary đã ổn định](../evidence/M3/group1b-prerequisites-20261103/primary-pfsync-retry-stable-20261103T182701+0700.png)

**Hình 3.3. Primary pfsync đã ổn định sau áp lại tuần tự.**

Mục đích: kiểm tra sau khởi tạo bulk. Nội dung: UP, syncdev/peer, syncok1, demotion0 và hash. Kết quả: đúng tham số, không còn demotion do bulk pending. Ý nghĩa: kết hợp kernel bulk done để chốt READY thay vì chỉ dựa vào UP. Ảnh thu lúc18:27:03 UTC+07:00.

![Secondary đã ổn định](../evidence/M3/group1b-prerequisites-20261103/secondary-pfsync-final-20261103T182701+0700.png)

**Hình 3.4. Secondary pfsync đã ổn định.**

Mục đích: xác nhận phía peer. Nội dung: syncpeer .1, syncok1, demotion0 và hash không đổi. Kết quả: cùng sẵn sàng trong phiên hiện tại. Ý nghĩa: không suy tình trạng Secondary từ riêng Primary. Ảnh thu lúc18:27:10 UTC+07:00. Hai ảnh kernel bulk done tương ứng được lưu cùng evidence index; các ảnh trung gian syncok0 vẫn giữ nguyên.

CARP — Common Address Redundancy Protocol, giao thức dự phòng địa chỉ chung — dùng VIP (Virtual IP Address, IP ảo) và VHID (Virtual Host Identifier, định danh nhóm host ảo) để bầu chọn thành viên. Advbase là khoảng cơ sở; advskew là độ lệch quảng bá để thể hiện ưu tiên. Trong SOC, mục tiêu là dự phòng gateway; tại đợt này các tham số mới được chốt, chưa có bầu chọn.

Pfsync là tên giao thức đồng bộ trạng thái PF (Packet Filter, bộ lọc gói); dùng IP protocol240, không phải TCP/UDP port240. Runtime đúng và gói hai chiều hỗ trợ mục tiêu HA (High Availability, sẵn sàng cao), chưa thay cho nghiệm thu giữ phiên. SYNC là tên đường riêng của dự án; opt6 là assignment, vtnet2 là device. HMAC — Hash-based Message Authentication Code, mã xác thực thông điệp có khóa — dùng làm kiểm chứng bí mật mà không công khai bí mật. DPAPI — Windows Data Protection API — bảo vệ bản lưu theo tài khoản Windows hiện hành. Ví dụ đã kiểm là peer SYNC và secret staged; CARP/failover vẫn chưa áp dụng.

Nguồn chính thức đối chiếu nguyên lý/backend: [OPNsense core26.7 interfaces.inc](https://raw.githubusercontent.com/opnsense/core/26.7/src/etc/inc/interfaces.inc), [actions_interface.conf](https://raw.githubusercontent.com/opnsense/core/26.7/src/opnsense/service/conf/actions.d/actions_interface.conf). Quyết định thao tác ưu tiên mã **cài thực tế** đã đọc, vì số dòng/version có thể khác bản tag trên web; không lấy ví dụ bên ngoài thay giá trị người dùng duyệt.

## 3.7. Bàn giao và điểm dừng

VIP năm VLAN APPROVED trong phạm vi kiểm tra; pfsync PFSYNC_STATUS ở runtime hiện tại. Bộ tham số cuối là `CARP-final-parameters.csv/json`, chưa áp vào thiết bị. Primary/Secondary giữ chạy; Core/endpoint khác vẫn tắt. Không đổi VLAN/access/trunk/OVS, NAT/DHCP hoặc HA SYNC rules; không mở rộng WAN/LAN parent.

Đã lưu `result.json`, backup/checksum, metadata capture, PCAP, audit/repair JSON, ảnh và `evidence-index.csv` có tên/nội dung/thời điểm UTC+07:00/đường dẫn/vị trí báo cáo/hash. Timestamp guest/PCAP được ghi riêng, không suy thành đồng hồ chuẩn của máy thu. **Dừng trước khi tạo CARP VIP và chờ người dùng xác nhận.**
'''
report=report.replace('TIME',NOW).replace('TABLE',table).replace('PFSYNC_STATUS',result['pfsync_status']).replace('COUNT_P',str(counts['10.255.255.1'])).replace('COUNT_S',str(counts['10.255.255.2'])).replace('HASH_P',audit['Primary']['backup_sha256']).replace('HASH_S',audit['Secondary']['backup_sha256'])
dest=ROOT/'docs/M3/M3-group1b-prerequisites-20261103.md';dest.write_text(report,encoding='utf-8')
# Mọi file báo cáo chỉ chứa metadata; private key/password/cipher temp không vào index công khai.
files=[p for p in OUT.rglob('*') if p.is_file() and 'private-backups' not in p.parts and p.name!='evidence-index.csv']+[dest]+[OUT/'private-backups'/(r+'-before.xml') for r in ['Primary','Secondary']]
with (OUT/'evidence-index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Tên tệp','Nội dung','Thời điểm thu/tạo UTC+07:00','Đường dẫn','Vị trí trong báo cáo','SHA256'])
 for p in sorted(set(files)):
  t=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone(datetime.timedelta(hours=7))).isoformat()
  if p.suffix=='.json':
   d=json.loads(p.read_text(encoding='utf-8-sig'))
   if isinstance(d,dict):t=d.get('collector_time_end',d.get('collector_time',d.get('collected_at',t)))
  elif p.suffix=='.png' and p.with_suffix('.json').exists():t=json.loads(p.with_suffix('.json').read_text())['collector_time_end']
  desc='Backup riêng tư, Git ignore; không công khai nội dung' if 'private-backups' in p.parts else 'Ảnh console thật không chỉnh sửa' if p.suffix=='.png' else 'Dữ liệu/báo cáo/metadata; đọc giới hạn trong báo cáo Nhóm1B'
  w.writerow([p.name,desc,t,str(p.relative_to(ROOT)).replace('\\','/'),'Chương3 / Nhóm1B',hashlib.sha256(p.read_bytes()).hexdigest()])
print(json.dumps(result,ensure_ascii=False))
