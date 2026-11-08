"""Đối chiếu backup đã xác minh, lập bảng CARP; không kết nối/sửa firewall."""
from pathlib import Path
import csv,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/evidence/M3/group1-carp-readiness-20261103'
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
audits={};trees={};allvips={}
for role in ['Primary','Secondary']:
 a=json.loads((OUT/(role.lower()+'-audit.json')).read_text(encoding='utf-8'))
 p=OUT/'private-backups'/(role+'-config.xml');raw=p.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==a['backup_sha256']==a['local_sha256']==a['config_sha256_before']==a['config_sha256_after']
 assert a['config_unchanged'] and a['local_decryption_and_hash_verified']
 assert subprocess.run(['git','check-ignore','--',str(p.relative_to(ROOT))],cwd=ROOT,capture_output=True).returncode==0
 trees[role]=E.fromstring(raw);audits[role]=a
 # Đọc tất cả node mode/type CARP, chỉ xuất trường allowlist; không đọc password ra báo cáo.
 entries=[]
 for n in trees[role].iter():
  if (n.findtext('mode') or n.findtext('type') or '').lower()=='carp':
   entries.append({k:n.findtext(k) for k in ['interface','subnet','subnet_bits','address','prefix','vhid','advbase','advskew','descr'] if n.find(k) is not None})
 allvips[role]=entries
 a['CARP_entries_public_all_branches']=entries
 block=re.search(r'(?ms)^pfsync0:.*?(?=^[A-Za-z0-9_]+:|\Z)',a['runtime_ifconfig']['stdout'])
 a['pfsync_runtime_observation']={'raw_interface_block':block.group(0) if block else None,'UP_flag_present':bool(block and re.search(r'<[^>]*\bUP\b',block.group(0))),'syncdev_present':bool(block and 'syncdev:' in block.group(0)),'syncpeer_present':bool(block and 'syncpeer:' in block.group(0)),'interpretation':'Read-only runtime observation; prior packet evidence retained; no reconfiguration in group1'}
 a['protected_section_hashes_local_read']={name:hashlib.sha256(E.tostring(trees[role].find(name))).hexdigest() if trees[role].find(name) is not None else None for name in ['interfaces','filter','nat','dhcpd','hasync','virtualip','OPNsense']}
 (OUT/(role.lower()+'-audit.json')).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
assert audits['Primary']['version']['stdout'].strip()==audits['Secondary']['version']['stdout'].strip()
baseline=json.loads((ROOT/'docs/evidence/M2/group2b2-20261103/firewall-current-public.json').read_text(encoding='utf-8'))
assert audits['Primary']['backup_sha256']==baseline['config_sha256_after'],'Primary changed since M2; review before calling M2 intact'
def iface(role,name):return next(x for x in audits[role]['interfaces'] if x['assignment']==name)
rows=[]
for i,vid in enumerate([30,40,50,60,99],1):
 p=iface('Primary','opt'+str(i));s=iface('Secondary','opt'+str(i))
 assert p['if']==s['if']=='vtnet0_vlan'+str(vid)
 assert p['ipaddr']==f'192.168.{vid}.2' and s['ipaddr']==f'192.168.{vid}.3' and p['subnet']==s['subnet']=='24'
 rows.append({'interface_Primary':p['assignment']+' / '+p['if'],'interface_Secondary':s['assignment']+' / '+s['if'],'VLAN':vid,'Primary_IP':p['ipaddr'],'Secondary_IP':s['ipaddr'],'CARP_VIP_candidate_M1':f'192.168.{vid}.1','subnet_prefix':f'192.168.{vid}.0/24','VIP_approval':'Ví dụ M1, chưa xác nhận, không áp dụng','VHID':'Chưa được chốt','advskew_Primary':'Chưa được chốt','advskew_Secondary':'Chưa được chốt','advbase':'Chưa được chốt','SYNC':'opt6 / vtnet2; Primary 10.255.255.1/30; Secondary 10.255.255.2/30'})
for role,address in [('Primary','10.255.255.1'),('Secondary','10.255.255.2')]:
 s=iface(role,'opt6');assert s['if']=='vtnet2' and s['ipaddr']==address and s['subnet']=='30'
# Không có CARP sẵn trong đợt này; nếu có phải báo hiện trạng riêng, không ghi đè bằng đề xuất.
assert not allvips['Primary'] and not allvips['Secondary'],'Existing CARP found; require report handling actual values'
with (OUT/'carp-planning-table.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'carp-planning-table.json').write_text(json.dumps({'reviewed_at':NOW,'status':'DRAFT_NOT_APPROVED_NOT_APPLIED','rows':rows,'actual_CARP_entries':allvips},ensure_ascii=False,indent=2),encoding='utf-8')
checksums=''.join(audits[r]['backup_sha256']+'  private-backups/'+r+'-config.xml\n' for r in ['Primary','Secondary'])
(OUT/'backup-SHA256SUMS.txt').write_text(checksums,encoding='ascii')
manifest={'collected_at':NOW,'scope':'New full backups, protected locally; public metadata only','encryption':'RSA-OAEP-SHA256 + AES-256-CBC/PBKDF2; decrypted XML SHA256 verified',
 'backups':[{'role':r,'local':audits[r]['backup_local'],'guest':audits[r]['backup_path_guest'],'bytes':audits[r]['backup_bytes'],'sha256':audits[r]['backup_sha256'],'git_ignored':True,'config_unchanged':True} for r in ['Primary','Secondary']],
 'Primary_matches_M2_baseline':True,'both_versions':audits['Primary']['version']['stdout'].strip(),'actual_CARP_VIP_count':0}
(OUT/'backup-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
table='| Interface hai phía | VLAN | Primary IP | Secondary IP | VIP ví dụ M1 — chưa duyệt | Subnet/prefix | VHID | Advskew P/S | SYNC |\n|---|---|---|---|---|---|---|---|---|\n'
for row in rows:table+='| '+' | '.join([row['interface_Primary'],str(row['VLAN']),row['Primary_IP'],row['Secondary_IP'],row['CARP_VIP_candidate_M1'],row['subnet_prefix'],row['VHID'],'Chưa chốt / Chưa chốt','opt6/vtnet2 (*)'])+' |\n'
imageP=sorted((OUT/'console-backup-primary-v2').glob('backup-execute-*.png'))[-1]
imageS=sorted((OUT/'console-backup-secondary-v2').glob('backup-execute-*.png'))[-1]
report='''# CHƯƠNG 3. M3 — NHÓM 1: BACKUP VÀ ĐỐI CHIẾU KẾ HOẠCH CARP

## 3.1. Kết quả và giới hạn

Thời điểm tổng hợp: TIME, UTC+07:00. Primary và Secondary cùng chạy VERSION, boot từ ổ cứng và có shell hợp lệ để đọc cấu hình. Đã tạo backup mới của cả hai trong guest, truyền dưới dạng mã hóa, giải mã tại thư mục riêng trên Windows và đối chiếu nguyên byte bằng SHA-256. Không áp dụng CARP, không failover, không sửa firewall/NAT/DHCP, Core hoặc các rule HA SYNC.

**Cả hai sẵn sàng cho việc đọc/đối chiếu và đã có backup; chưa sẵn sàng áp dụng hoặc nghiệm thu CARP.** Chưa có CARP VIP nào trong các nhánh cấu hình đã duyệt bằng bản backup đầy đủ và runtime chưa được dùng để chứng minh vai trò MASTER/BACKUP. VIP/VHID/advskew chưa được phê duyệt. Không coi net.inet.carp.allow bật hoặc dòng “CARP event system: OK” lúc boot là VIP đã hoạt động.

## 3.2. Quản lý RAM và trạng thái node

Trước đợt: Primary3072 MiB + Core2048 MiB chạy. Nếu bật Secondary3072 MiB sẽ thành8192 MiB, vượt tổng EVE khoảng7898 MiB. Người dùng đã cấp riêng quyền tắt mềm Core trong câu trả lời cho câu hỏi tài nguyên; đã gửi poweroff từ root shell và kiểm tra Core QEMU dừng trước khi start Secondary. Không sửa OVS, VLAN, trunk hoặc nội dung cấu hình M2.

Chỉ hai firewall chạy, tổng6144 MiB. `start-secondary.json` ghi guard RAM/start receipt; `inventory-both-running.json` ghi EVE còn khoảng3339 MiB available, swap0 tại mốc thu. Các endpoint M2 đã tắt từ trước; không bật Wazuh, Suricata hoặc node khác. Primary giữ hoạt động, không reboot. Kiểm kê cuối nằm trong `inventory-final.json`.

Core đang tắt để bảo đảm RAM, nên đường L2 giữa trunk Primary/Secondary qua Core chưa vận hành trong nhóm này. SYNC vtnet2 vẫn là segment riêng giữa hai firewall. Không suy boot hai firewall thành CARP đã có kênh bầu chọn trên năm VLAN; trước một đợt CARP tương lai cần phương án RAM/Layer2 phù hợp được duyệt, không tự thay Core hoặc hạ RAM firewall trong nhóm này.

## 3.3. Bảng CARP dự kiến đối chiếu thực tế

TABLE

(*) SYNC chung cho mọi dòng: Primary **opt6/vtnet2 10.255.255.1/30**, Secondary **opt6/vtnet2 10.255.255.2/30**. Đây là địa chỉ riêng đồng bộ, không đề xuất thêm CARP VIP lên đường SYNC. Tên assignment/device của hai phía khớp nhau trong bản đọc mới.

IP riêng Primary .2/24 và Secondary .3/24 là cấu hình thực tế đã đọc lại. Các VIP .1 được lấy nguyên từ tài liệu M1 và `configs/M3/address-proposal.json` (status PROPOSED_NOT_CONFIRMED_NOT_APPLIED, confirmed=false); **không phải VIP được người dùng phê duyệt hoặc đã kiểm tra không trùng**. Không tự tạo VIP/VHID hay nhập advskew mặc định/giá trị trong ví dụ tài liệu bên ngoài. Advbase cũng chưa được chốt; CSV lưu đầy đủ từng trường advskew hai phía, advbase và SYNC.

## 3.4. Mạng/interface ngoài năm VLAN cần làm rõ phạm vi HA

| Mạng/interface | Hiện trạng đã đọc | Kế hoạch CARP |
|---|---|---|
| LAN parent / vtnet0 | Primary192.168.1.1/24, Secondary192.168.1.2/24 trong hồ sơ và bản đọc mới | Chưa xác nhận có yêu cầu HA cho LAN parent; chưa có VIP/VHID/advskew được chốt. Không dùng lại .1 làm VIP vì Primary đang sở hữu địa chỉ đó |
| WAN / vtnet1 | Cấu hình DHCP; địa chỉ/gateway upstream và VIP WAN chưa được tài liệu chốt | Không đề xuất VIP/VHID số cụ thể, không thay NAT/DHCP |
| NIC WAN bổ sung vtnet3 | Có trong topology nhưng không tự suy thành interface HA đã được gán | Phạm vi/interface/IP/VIP cần xác nhận nếu muốn sử dụng |
| SYNC / opt6/vtnet2 | .1/.2 của mạng10.255.255.0/30 | Đường đồng bộ riêng; không đưa vào danh sách tạo CARP VIP |

Đợt này không có lease/gateway WAN nào được nâng thành quy hoạch được phê duyệt. Runtime ifconfig đầy đủ không nhạy cảm được lưu trong hai audit JSON, không phát DHCP renew hoặc phép thử mạng riêng.

## 3.5. Thông số đã xác nhận và phần còn thiếu

Đã xác nhận bằng dữ liệu mới: phiên bản hai firewall giống nhau, assignment opt1–opt5 và device VLAN khớp, năm subnet/prefix24, các IP riêng .2/.3, SYNC opt6/vtnet2 với .1/.2 /30. Tài liệu xác nhận **kiến trúc** CARP dùng VIP gateway, SYNC riêng, Core chỉ Layer2; không đồng nghĩa xác nhận các VIP ví dụ. Cấu hình pfsync/XMLRPC được đọc chọn lọc, không xuất thông tin xác thực hoặc thay cấu hình.

Các mục thiếu trước khi có thể áp dụng CARP trong nhóm sau:

1. Duyệt VIP cụ thể của từng VLAN, và xác nhận không trùng với thiết bị khác; .1 hiện chỉ là ví dụ M1.
2. Chốt VHID cho từng nhóm VIP, bảo đảm phù hợp miền L2 và không xung đột; chưa tìm thấy VHID số được duyệt trong tài liệu M1/M3.
3. Chốt advskew Primary/Secondary, advbase và ý định ưu tiên/khôi phục vai trò. Không lấy giá trị ví dụ trong hướng dẫn làm cấu hình đồ án.
4. Cách thiết lập secret CARP chung qua kênh riêng nếu cần khi cấu hình; không yêu cầu gửi password vào chat hoặc ghi vào báo cáo/Git.
5. Chốt có HA trên LAN parent/WAN không; WAN còn thiếu upstream/subnet/IP/gateway/VIP. Không tự mở rộng phạm vi sang NAT/DHCP.
6. Bảo đảm Layer2 giữa interface chứa VIP và phương án tài nguyên khi cần Core cùng hai firewall. Khả năng trao đổi CARP protocol112 và xung đột VIP/VHID chưa được thử trong nhóm chỉ đọc; không tự thêm rule hoặc phát packet để xác minh.

**Vấn đề runtime mới cần ghi nhận:** `ifconfig -a` trên cả hai firewall sau boot ghi `pfsync0: flags=0`, không có cờ UP, không có syncdev/syncpeer. Trong cấu hình, Primary vẫn chọn opt6/peer10.255.255.2 và Secondary chọn opt6/peer10.255.255.1. Không dùng `syncok: 1` đứng riêng để kết luận đồng bộ state đang hoạt động. Chưa xác định nguyên nhân khác biệt cấu hình/runtime; không sửa, restart pfsync hoặc bổ sung trường cấu hình trong Nhóm1. Điều này cần được xem xét trước nghiệm thu đồng bộ phiên HA; không tự kết luận CARP bầu chọn phụ thuộc pfsync.

Pfsync từng có bằng chứng gói hai chiều; chưa đánh đồng bằng chứng đó với nghiệm thu giữ phiên hoặc khẳng định nó đang chạy ở mốc mới. XMLRPC từng có bằng chứng thêm/xóa alias thử trên Secondary. Không cấu hình hoặc kiểm thử lại hai chức năng trong nhóm này; các audit mới chỉ phản ánh cấu hình hiện có, không tạo thêm một kết luận HA runtime PASS.

## 3.6. Backup đầy đủ và checksum

Thư mục riêng trên Windows: `docs/evidence/M3/group1-carp-readiness-20261103/private-backups/`, NTFS bỏ quyền kế thừa và chỉ cấp quyền cho owner hiện hành; toàn bộ thư mục bị Git ignore. Không chỉ đổi tên tệp để che secret. Khi truyền console chỉ có mã reader không chứa xác thực, public key và ciphertext; trước khi chấp nhận backup đã kiểm hash payload, giải mã, giải nén, kiểm kích thước/hash plaintext và parse XML.

| Firewall | Backup tại Windows | SHA-256 |
|---|---|---|
| Primary | private-backups/Primary-config.xml | HASH_PRIMARY |
| Secondary | private-backups/Secondary-config.xml | HASH_SECONDARY |

Checksum công khai: `backup-SHA256SUMS.txt`; manifest: `backup-manifest.json`. Bản backup tương ứng trong guest: `/root/soc-m3-group1-primary-20261103/config.xml` và `/root/soc-m3-group1-secondary-20261103/config.xml`, root-only thư mục0700/tệp0600. Public audit chỉ chứa metadata, IP/interface và thông số HA cho phép xuất, không có mật khẩu/hash đăng nhập/private key/API key/CARP secret.

Mỗi firewall có hash config trước/sau đọc bằng hash backup tại guest và Windows. Primary còn khớp nguyên hash snapshot M2; không thay các cấu hình M2. File private vận chuyển như key hoặc dữ liệu nén vẫn nằm trong thư mục riêng; không đưa chúng vào báo cáo hoặc Git. Không commit/push. Bản XML đầy đủ chỉ dùng phục hồi riêng, không công khai nội dung.

## 3.7. Thuật ngữ áp dụng

CARP — Common Address Redundancy Protocol, giao thức dự phòng địa chỉ chung — giúp hai firewall chia sẻ VIP (Virtual IP Address, địa chỉ IP ảo). VHID — Virtual Host Identifier, định danh nhóm host ảo — nhận diện nhóm bầu chọn. Advskew là tham số lệch thời gian quảng bá; mức thấp hơn có ưu tiên cao hơn theo cơ chế CARP. Advbase là thời gian cơ sở của chu kỳ quảng bá. CARP dùng IP protocol112, khác TCP/UDP port112. Trong SOC, các cơ chế này dự kiến duy trì gateway khi một firewall lỗi; trong topology này năm VLAN mới có IP riêng, VIP/VHID/advskew còn chưa chốt, chưa nghiệm thu dự phòng.

HA — High Availability, tính sẵn sàng cao — là mục tiêu dự phòng, không phải trạng thái chỉ vì hai VM chạy. Pfsync là tên giao thức đồng bộ trạng thái PF; XMLRPC là cơ chế đồng bộ cấu hình hiện có của OPNsense. OPNsense là tên sản phẩm, không tự khai triển. SYNC là tên đường đồng bộ của dự án, không tự coi là VIP. Vai trò và các thuật ngữ SOC/VLAN/802.1Q/trunk/OVS/QEMU/SSH/NAT/DHCP dùng `docs/TOPOLOGY_TERMS.md` cùng trạng thái của báo cáo này; nhóm này không thay cấu hình các thành phần đó.

Cơ sở nguyên lý: [OPNsense — Configure CARP](https://docs.opnsense.org/manual/how-tos/carp.html), đối chiếu ngày03/11/2026. Hướng dẫn chính thức yêu cầu assignment phù hợp và khả năng nhận CARP trên interface; các ví dụ địa chỉ/VHID/skew của hướng dẫn không phải dữ liệu được chốt cho đồ án. Không làm theo các bước NAT/DHCP/reboot trong hướng dẫn vì ngoài quyền Nhóm1.

## 3.8. Hình và giới hạn thu thập

![Backup Primary](IMAGE_PRIMARY)

**Hình 3.1. Tạo backup mới trên Primary trước kế hoạch CARP.**

Mục đích: xác nhận snapshot mới. Nội dung: M3_BACKUP_READY, hash, config unchanged và VIP_count. Kết quả: backup guest có trước khi chuyển mã hóa; checksum Windows được kiểm riêng trong audit. Ý nghĩa: không dùng backup M2 cũ thay snapshot mới. Ảnh toàn màn hình, không sửa nội dung kỹ thuật; thời điểm thu có trong JSON cùng tên.

![Backup Secondary](IMAGE_SECONDARY)

**Hình 3.2. Tạo backup mới trên Secondary.**

Mục đích: xác nhận snapshot phía dự phòng. Nội dung: cùng bộ metadata không nhạy cảm cho Secondary. Kết quả: có backup mới, cấu hình không đổi. Ý nghĩa: hai phía có mốc phục hồi trước mọi thay đổi CARP tương lai; không phải ảnh MASTER/BACKUP.

Mốc thu dùng máy thu UTC+07:00; giờ guest có thể lệch. Các ảnh boot/shell và trang mã hóa được giữ trong thư mục minh chứng. Lần thử truyền bàn phím nhanh đầu tiên bị mất ký tự; kiểm hash/chạy reader bị chặn trước khi tạo backup, giữ ảnh lỗi, sau đó dùng nhịp console đã kiểm chứng. Primary stdout QEMU là pipe, không phải serial.log đọc được; vì vậy chuyển backup bằng trang glyph đã xác minh, không đổi xác thực/console/serial config hoặc tạo kết nối mạng mới. Không sửa ảnh để che lỗi truyền.

## 3.9. Trạng thái bàn giao

Ba việc Nhóm1 hoàn tất khi hai backup đã được xác minh và bảng đối chiếu được lưu. Primary + Secondary giữ chạy; Core tắt mềm theo quyền riêng; endpoint khác giữ tắt. **Không cấu hình CARP, không failover, không sửa rule HA SYNC, NAT/DHCP hoặc M2.** VIP/VHID/advskew vẫn chờ xác nhận. Không tự chuyển Nhóm2.

Danh mục `evidence-index.csv` có tên tệp, nội dung, thời điểm kèm múi giờ, đường dẫn, vị trí báo cáo và checksum. Private backup chỉ được liệt kê metadata/hash; không nhúng nội dung vào ảnh/báo cáo. Báo cáo này chuẩn bị nội dung học thuật cho Word; nếu xuất cần A4, Times New Roman12–13, lề trái3 cm/còn lại2 cm và chú thích dưới hình.
'''
report=report.replace('TIME',NOW).replace('VERSION',audits['Primary']['version']['stdout'].strip()).replace('TABLE',table)
report=report.replace('HASH_PRIMARY',audits['Primary']['backup_sha256']).replace('HASH_SECONDARY',audits['Secondary']['backup_sha256'])
target=ROOT/'docs/M3/M3-group1-CARP-readiness-20261103.md'
report=report.replace('IMAGE_PRIMARY','../evidence/M3/group1-carp-readiness-20261103/'+str(imageP.relative_to(OUT)).replace('\\','/')).replace('IMAGE_SECONDARY','../evidence/M3/group1-carp-readiness-20261103/'+str(imageS.relative_to(OUT)).replace('\\','/'))
target.write_text(report,encoding='utf-8')
sources=[ROOT/'opnsense/ha/ha-design.md',ROOT/'configs/M3/address-proposal.json',ROOT/'docs/M1/M1_Thiet_ke_SOC_Core_L2_OPNsense_Giai_thich_thuat_ngu.docx',ROOT/'docs/M3/M3-OPNsense-HA-PROPOSED-20261101.md']
(OUT/'source-manifest.json').write_text(json.dumps({'reviewed_at':NOW,'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]},indent=2),encoding='utf-8')
checks={'checked_at':NOW,'both_firewalls_booted':True,'same_version':True,'both_backups_new_and_plaintext_hash_verified':True,'both_backups_Git_ignored':True,'Primary_matches_M2_snapshot':True,'VLAN_assignments_and_prefix_match':True,'CARP_VIP_count':0,'CARP_applied':False,'failover_tested':False,'firewall_NAT_DHCP_HA_modified':False,'ready_for_CARP_application':False,'pfsync_runtime_issue':[{'role':r,'UP':audits[r]['pfsync_runtime_observation']['UP_flag_present'],'syncdev_present':audits[r]['pfsync_runtime_observation']['syncdev_present'],'syncpeer_present':audits[r]['pfsync_runtime_observation']['syncpeer_present']} for r in ['Primary','Secondary']],'missing':['VIP approval','VHID','advskew both sides','advbase','CARP secret via private channel','scope WAN/LAN parent','Layer2 and RAM plan for CARP test','Review pfsync runtime versus saved configuration']}
(OUT/'delivery-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
paths=[p for p in OUT.rglob('*') if p.is_file() and 'private-backups' not in p.parts and p.name!='evidence-index.csv']+[target]+sources+[OUT/'private-backups'/(r+'-config.xml') for r in ['Primary','Secondary']]
with (OUT/'evidence-index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Tên tệp','Nội dung','Thời điểm thu/tạo UTC+07:00','Đường dẫn','Vị trí báo cáo','SHA256'])
 for p in sorted(set(paths)):
  ts=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone(datetime.timedelta(hours=7))).isoformat()
  if p.suffix=='.json':
   j=json.loads(p.read_text(encoding='utf-8-sig'));ts=j.get('collector_time_end',j.get('collector_time',j.get('collected_at',j.get('checked_at',ts))))
  elif p.suffix=='.png' and p.with_suffix('.json').exists():ts=json.loads(p.with_suffix('.json').read_text())['collector_time_end']
  desc='Backup đầy đủ riêng tư; không Git/không công khai nội dung' if 'private-backups' in p.parts else 'Ảnh console thật nguyên bản; trang mã hóa là dữ liệu truyền' if p.suffix=='.png' else 'Báo cáo/cấu hình công khai/checksum/metadata; đọc giới hạn trong báo cáo Nhóm1'
  w.writerow([p.name,desc,ts,str(p.relative_to(ROOT)).replace('\\','/'),'Chương 3 / Nhóm 1',hashlib.sha256(p.read_bytes()).hexdigest()])
print(json.dumps({'report':str(target),'backups_verified':2,'CARP_configured':False,'same_version':True,'VIPs_confirmed':False,'rows':len(rows),'stop_before_group2':True},ensure_ascii=False))
