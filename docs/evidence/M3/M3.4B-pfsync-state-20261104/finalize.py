"""Chỉ nghiệm thu khi các pha và continuity độc lập đều có evidence PASS."""
import datetime as dt,hashlib,json
from pathlib import Path
P=Path(__file__).parent
def read(n):return json.loads((P/(n+'.json')).read_text(encoding='utf-8'))
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
phases={n:read(n+'-acceptance') for n in ['before','state-sync','failover','continuity','recovery']}
assert all(d['status']=='PASS' for d in phases.values())
packet=read('packet-analysis');assert packet['status']=='PASS' and packet['http_requests_observed']==1 and packet['client_syn_packets']==1
assert read('endpoint-test-route')['default_route_unchanged']
native_hash=hashlib.sha256((P/'native.py').read_bytes()).hexdigest()
assert all(read(role+'-native-stage')['sha256']==native_hash for role in ['primary','secondary'])
preserved=[]
for folder in ['M3.4-pfsync-state-20261104','M3.4A-baseline-20261104']:
 old=P.parent/folder;m=json.loads((old/'sha256-manifest.json').read_text(encoding='utf-8'))
 for n,h in m['sha256'].items():assert hashlib.sha256((old/n).read_bytes()).hexdigest()==h,(folder,n)
 preserved.append({'folder':str(old),'files_checked':len(m['sha256']),'unchanged':True})
(P/'previous-evidence-integrity.json').write_text(json.dumps({'collector_time':now,'manifests':preserved},ensure_ascii=False,indent=2),encoding='utf-8')
for item in read('artifact-manifest'):
 assert hashlib.sha256((P/'artifacts'/item['name']).read_bytes()).hexdigest()==item['sha256']
after=read('secondary-state-after-immediate');continuity=phases['continuity'];recovery=phases['recovery']
d={'todo':'M3.4 — Kiểm thử pfsync state synchronization khi CARP failover','status':'DONE/PASS','collector_time':now,'session':continuity['flow'],'A_state_synchronization':'PASS','B_connection_continuity':'PASS','state_ids_creator_ids':phases['state-sync']['native_state_ids_creator_ids'],'native_after_captured_on_all_five_MASTER':True,'watcher_observation_to_read_start_seconds':after['trigger_to_state_capture_seconds'],'watcher_native_capture_duration_seconds':after['native_capture_finished_monotonic']-after['native_capture_started_monotonic'],'continuity':continuity,'recovery':recovery,'phases':{n:v['status'] for n,v in phases.items()},'native_helper_sha256_verified':True,'previous_evidence_unchanged':True,'configuration_changes':{'firewall_rules':False,'NAT_DHCP':False,'CARP_VIP_VHID_advskew':False,'Core':False,'topology_IP_VLAN_plan':False,'endpoint':'Only scoped runtime host route 192.168.40.100/32 via existing VIP 192.168.30.1; original default route/IP/netplan preserved; no cleanup'},'limitations':['One new IPv4 TCP/HTTP session under current policy; not all protocols/flows/load.','Client retry counter0 and no duplicate TCP payload at client capture; packet loss not measured, no zero-packet-loss claim.','Watcher read-start delay is relative to observing five MASTER roles, not network downtime or failover convergence time.','HTTP request completed through Secondary before Primary recovery; no claim that this already-closed session stayed active across recovery.'],'next_todo':'Not assigned; stop after M3.4.'}
(P/'M3.4-acceptance.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
rel='evidence/M3/M3.4B-pfsync-state-20261104'
notice=f'''# CHECKPOINT MỚI NHẤT — M3.4 DONE/PASS — {now}

## 0.1. Nghiệm thu M3.4B

**M3.4 — pfsync state synchronization khi CARP failover: DONE/PASS.** A. State synchronization PASS. B. Connection continuity PASS cho một session mới; recovery hoàn tất. Checkpoint này thay READY_FOR_RETEST của M3.4A; kết quả/evidence các lần trước giữ nguyên lịch sử, không sửa thành PASS.

- SESSION: `192.168.40.100:44341 → 192.168.30.10:8000/TCP`, client host EVE qua access VLAN40 sẵn có, Data-Center thật; một SYN, một HTTP request, không reconnect.
- Native Primary/Secondary BEFORE cùng hai ID `075deb6a00000000`, `085deb6a00000000`, creator ID `d57c33f6`, ESTABLISHED:ESTABLISHED; Secondary BACKUP có counter0:0. Có pfsync protocol240 hai chiều.
- FAILOVER: chỉ soft shutdown Primary; Core/Secondary/DC giữ PID. Watcher chỉ đọc đã lưu native snapshot ngay khi thấy đủ năm MASTER, giữ nguyên hai ID/creator và ESTABLISHED, VIP đúng. Ảnh native sau đó ghi counter tăng trên cùng state; không đổi VIP/VHID/advskew hoặc rule.
- CONTINUITY: cùng session nhận11 marker ACK sau Primary OFF rồi hoàn tất `HTTP/1.0 200 OK`,350 byte; PCAP tái lắp response khớp SHA-256. Retry counter client0, không thấy duplicate payload tại capture client; **không kết luận zero packet loss**. Request đã hoàn tất trước khi boot Primary.
- RECOVERY: Primary tự MASTER / Secondary BACKUP cả VLAN30/40/50/60/99, năm VIP .1 đúng; pfsync READY hai phía, syncok1/demotion0, SYNC ping2/2; Core OVS/VLAN hoạt động, Core giữ Layer2. Không gọi lại native pfsync hoặc đặt demotion thủ công.
- Backup mỗi firewall `/root/soc-m34b-20261104/config.before.xml`; DC `/root/soc-m34b-20261104/routes.before.json`. Chỉ thêm host route runtime `.40.100/32 via .30.1` để chiều về qua CARP; IP/default route/netplan không đổi. Route và helper/evidence được giữ lại theo yêu cầu không cleanup. Bốn node vẫn chạy, Primary đã boot mới; không node khác được bật.
- [Báo cáo/danh mục minh chứng]({rel}/evidence-index.md), [nghiệm thu]({rel}/M3.4-acceptance.json). M3.4 cũ137 tệp và M3.4A119 tệp giữ nguyên checksum.
- **NEXT TODO: chưa được giao. Dừng sau M3.4; không M3.5, NAT/DHCP, M4/M5 hoặc cleanup.**

---

'''
todo=Path('docs/SOC_TO_DO.md');lines=todo.read_text(encoding='utf-8').splitlines(keepends=True)
for i,line in enumerate(lines):
 if line.startswith('| M3.4 '):
  lines[i]=f'| M3.4 — Kiểm thử pfsync state synchronization khi CARP failover | DONE/PASS — {now}; state sync, continuity của một session mới và recovery PASS | `{rel}/M3.4-acceptance.json`; native state trước/sau, PCAP và recovery |\n';break
else:raise RuntimeError('Missing TODO M3.4')
todo.write_text(notice+''.join(lines),encoding='utf-8')
progress=Path('docs/PROGRESS.md');progress.write_text(notice+progress.read_text(encoding='utf-8'),encoding='utf-8')
report=f'''# CHƯƠNG 3. KIỂM THỬ PFSYNC STATE FAILOVER — M3.4B

## 3.4.1. Kết luận và phạm vi

**DONE/PASS**, tổng hợp lúc {now} (UTC+07:00). Phân biệt A. State synchronization PASS và B. Connection continuity PASS. Primary đã được boot và tự trở lại MASTER, Secondary BACKUP đủ năm VLAN, pfsync READY hai phía; Core Layer2/VLAN và endpoint hoạt động.

Phạm vi là một IPv4 TCP/HTTP session lành tính dưới policy có sẵn, không suy thành nghiệm thu mọi flow, UDP/IPv6, tải dài hạn hoặc zero packet loss. HTTP đã hoàn tất qua Secondary trước recovery; không tuyên bố session đã đóng vẫn giữ qua recovery.

## 3.4.2. Phương pháp, thuật ngữ và nhận diện session

Trong SOC (Security Operations Center — trung tâm giám sát/vận hành an toàn thông tin), tính sẵn sàng của gateway cần được kiểm chứng ở cả vai trò firewall và state của lưu lượng. CARP (Common Address Redundancy Protocol — giao thức dự phòng địa chỉ chung) điều phối MASTER/BACKUP của Virtual IP address (VIP — địa chỉ IP ảo). pfsync là tên cơ chế/giao diện đồng bộ state của Packet Filter (PF), không tự tạo dạng khai triển; hai firewall dùng SYNC10.255.255.1/30 ↔ .2/30.

TCP (Transmission Control Protocol — giao thức điều khiển truyền vận) theo dõi sequence/acknowledgement. HTTP (Hypertext Transfer Protocol — giao thức truyền siêu văn bản) được dùng trên dịch vụ DC hiện có. Một request được giữ mở ở phần header để đọc state; sau failover mới gửi dòng trống kết thúc chính request đó và nhận response. Không tạo HTTP request mới làm bằng chứng continuity.

| Thuộc tính | Giá trị thực tế |
|---|---|
| Client | Host EVE hiện có, TCP client AF_PACKET; access TAP vunl0_3_1, không thêm NIC/link hoặc gán IP vào network stack host |
| Client IP/MAC | 192.168.40.100, 02:53:4f:43:04:35; VPCS Employee không chạy, có ARP conflict probe |
| Server | VM Data-Center có sẵn,192.168.30.10:8000 |
| TCP tuple | 192.168.40.100:44341 → 192.168.30.10:8000 |
| Initial sequence numbers | Client69072772; server45026641 |
| Request | GET /?soc_m34=state-retest-b HTTP/1.0; một request trên một session |
| Gateway | Client VIP192.168.40.1, chiều về qua VIP192.168.30.1 |

Default route DC vẫn192.168.30.2; sau backup0600 chỉ thêm host route `.40.100/32 via .30.1`. Không sửa IP/default route/netplan, Core, topology, NAT/DHCP hoặc firewall rule. Rule Primary hiện có cho phép đúng nguồn .40.100 tới .30.10 TCP8000; Secondary không có rule tạo flow mới tương ứng. Client là bộ thực thi TCP qua raw socket, không báo đây là VPCS hoặc TCP socket kernel Linux.

Core là Open vSwitch (OVS — tên sản phẩm), chỉ Layer2, chuyển frame theo Virtual Local Area Network (VLAN — mạng LAN ảo) và trunk IEEE802.1Q. Gói thực tế trước/sau đều đi VLAN40↔30 và TTL64→63 tại firewall, không có đường tắt inter-VLAN trên Core.

## 3.4.3. A — State synchronization và native failover

| Pha | Native state | CARP | Minh chứng |
|---|---|---|---|
| Primary BEFORE | Hai entry ESTABLISHED, ID075deb6a00000000/085deb6a00000000, creator d57c33f6; counter có traffic | MASTER năm VLAN | primary-state-before.json; ảnh native trước |
| Secondary BEFORE | Cùng hai ID/creator, sequence window khớp; counter0:0 | BACKUP năm VLAN | secondary-state-before.json; state-sync-acceptance.json |
| Secondary ngay khi tiếp quản | Hai ID/creator không đổi, ESTABLISHED; snapshot sớm có counter0:0 | MASTER năm VLAN, VIP đúng | secondary-state-after-immediate.json; failover-acceptance.json |
| Secondary sau khi chuyển dữ liệu | Cùng ID/creator; counter đã tăng, ví dụ5:5 tại ảnh đọc native | MASTER năm VLAN | secondary-after-native-readable; wire/client logs |

Hai entry thuộc cùng TCP tuple (ingress VLAN40/egress VLAN30), không phải hai session. Creator ID và state ID được đối chiếu trực tiếp từ `pfctl -ss -vv`. pfsync protocol240 có gói hai chiều; không tuyên bố đã giải mã state ID từ payload pfsync khi chỉ thu metadata.

Watcher có hạn300 giây chỉ đọc CARP và PF; không tạo/xóa state hoặc đổi vai. Khi quan sát đủ năm MASTER, nó gọi native PF ngay và lưu snapshot atomically kèm fsync trước khi console truyền dữ liệu. Khoảng observer→read-start là {after['trigger_to_state_capture_seconds']:.8f} giây; đây không phải thời gian gián đoạn hoặc CARP convergence. Thời điểm snapshot trong guest và thời điểm collector nhận JSON là hai mốc khác nhau. Counter0 trong snapshot đầu không bị diễn giải thành state không hoạt động: marker tiếp theo và ảnh native sau đó chứng minh state được sử dụng.

## 3.4.4. B — Connection continuity

| Kiểm tra | Kết quả |
|---|---|
| Một SYN, không reconnect, ISN/tuple giữ nguyên | PASS |
| Marker ACK sau host xác nhận Primary OFF | 11 marker |
| Hoàn tất request đã mở từ BEFORE qua Secondary | HTTP/1.0 200 OK,350 byte |
| Tái lắp response từ PCAP | Khớp SHA-256 {continuity['response_sha256']} |
| TCP RST quan sát tại client | 0 |
| Retry counter của client | 0 |
| Duplicate TCP payload tại điểm capture client | 0 |
| Mất gói toàn hệ thống | Không đo; không tuyên bố zero packet loss |

`packet-analysis.json` đối chiếu tuple/sequence/payload length, VLAN40→30, TTL64→63 và MAC forwarding: trước qua trunk Primary (`50:00:00:01:00:00`), sau Primary OFF qua trunk Secondary (`50:00:00:02:00:00`). PCAP được giữ nguyên byte, không dựng lại packet. Client PCAP có106 TCP packet records, một GET, không TCP RST; response tái lắp khớp kết quả client. Capture có phạm vi/điểm quan sát hữu hạn nên0 retry/duplicate không chứng minh0 loss.

## 3.4.5. Recovery và điểm dừng

Primary được soft shutdown rồi boot lại đúng node1; Core/Secondary/DC giữ PID, không stop/reboot. Recovery native xác nhận Primary MASTER, Secondary BACKUP trên VLAN30/40/50/60/99; VIP .1, VHID/advbase/skew và config SHA-256 giữ nguyên. Pfsync hai phía UP/RUNNING, đúng vtnet2/peer, syncok1, demotion0; SYNC ping2/2. Hook cùng boot hoạt động, không gọi lại native pfsync hoặc đặt demotion thủ công. Core OVS active, đúng access/trunk, flow NORMAL, không IP ngoài loopback và forwarding0/0; ARP năm VLAN nhận đủ .2/.3/.1.

Giữ bốn node chạy và các helper/backup/evidence; không cleanup host route runtime. Client/capture và watcher kết thúc bình thường theo vòng đời phép thử, không tái khởi động session cũ. M3.4B hoàn tất, không làm M3.5/M4/M5. Evidence M3.4 cũ137 tệp và M3.4A119 tệp được kiểm tra lại SHA-256 và giữ nguyên; kết quả cũ bị gián đoạn vẫn là lịch sử riêng.

Thời điểm thu dùng collector chuyển sang UTC+07:00. Giờ EVE/guest được ghi là untrusted; các delta watcher dùng monotonic cùng guest, không dùng thay downtime. Tệp artifacts được chép sau phép thử, mtime lúc sao chép không phải timestamp phát packet.

## 3.4.6. Ảnh minh chứng thực tế

'''
figs=[('primary-state-before-readable','Native state Primary trước failover.','Đọc tuple, hai ID/creator, ESTABLISHED và counter để thiết lập nguồn state.'),('secondary-state-before-readable','Native state Secondary BACKUP trước failover.','Cùng ID/creator/window, counter0:0; đối chiếu JSON native và vai trò BACKUP.'),('primary-soft-shutdown','Soft shutdown riêng Primary.','Xác nhận lệnh shutdown -p now; host xác nhận Primary OFF trước marker continuity.'),('secondary-after-native-readable','Secondary MASTER và state cũ sau tiếp quản.','Đọc năm MASTER và ID/creator giữ nguyên, counter tăng; đối chiếu snapshot watcher sớm hơn.'),('dc-http-success-journal','Server ghi request retest trả HTTP200.','Chỉ dòng URI state-retest-b là request hiện tại; journal có boot lịch sử. Kết hợp một SYN/một GET trong PCAP để chứng minh không reconnect.'),('primary-recovery-carp-readable','Primary MASTER sau boot mới.','Đọc năm VIP .1 và MASTER/VHID; xác nhận tự recovery.'),('secondary-recovery-carp-readable','Secondary BACKUP sau recovery.','Đọc năm VIP .1, BACKUP và skew100; không ép tham số.'),('primary-recovery-pfsync-readable','Pfsync và SYNC Primary sau recovery.','Đọc syncok1/demotion0, đúng peer và ping thành công.'),('secondary-recovery-pfsync-readable','Pfsync và SYNC Secondary sau recovery.','Đối chiếu UP/RUNNING, syncok1/demotion0 và peer ngược.'),('core-recovery-readable','Core vẫn Layer2 sau recovery.','OVS active, không IP ngoài loopback và forwarding0/0; port/flow/ARP xem core-recovery.json và recovery-arp.json.')]
for i,(prefix,title,why) in enumerate(figs,1):
 pics=sorted(P.glob(prefix+'-2026*.png'));assert pics,'Missing figure '+prefix
 pic=pics[-1];cap=f'Hình 3.{i}. {title}'
 report+=f'![{cap}]({pic.name})\n\n{cap}\n\nMục đích, nội dung, kết quả và ý nghĩa: {why}\n\n'
report+='''## 3.4.7. Danh mục minh chứng

| Tệp | Nội dung | Thời điểm thu (múi giờ) | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
'''
for p in sorted(P.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.py','.txt'] or p.name in ['evidence-index.md','sha256-manifest.json']:continue
 local=p.relative_to(P).as_posix();when=dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone(dt.timedelta(hours=7))).isoformat();desc='Runtime/metadata hoặc backup tài liệu; xem pha trong tên tệp'
 if p.suffix=='.png':desc='Ảnh console thực tế, nguyên nội dung'
 if 'artifacts' in p.parts:desc='Log/PCAP byte gốc sao chép sau test; thời điểm này là lúc sao chép'
 elif p.suffix=='.json':
  obj=json.loads(p.read_text(encoding='utf-8'))
  if isinstance(obj,dict):when=obj.get('collector_time',obj.get('collector_time_end',when))
 report+=f'| {local} | {desc} | {when} | docs/{rel}/{local} | M3.4B — pha tương ứng/phụ lục truy vết |\n'
(P/'evidence-index.md').write_text(report,encoding='utf-8')
manifest={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='sha256-manifest.json'}
(P/'sha256-manifest.json').write_text(json.dumps({'collector_time':now,'sha256':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'DONE/PASS','A_state_sync':'PASS','B_continuity':'PASS','recovery':'PASS','retry_counter':continuity['tcp_retransmissions_observed'],'evidence':str(P)},ensure_ascii=True))
