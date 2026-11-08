"""Ghi kết quả bị gián đoạn; không ép PASS hoặc đổi hệ thống để che thiếu evidence."""
import datetime as dt,hashlib,json,shutil
from pathlib import Path

OUT=Path(__file__).parent
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
sync=read('state-sync-acceptance.json');host=read('host-resume-check.json');analysis=read('interrupted-analysis.json')
assert sync['status']=='PASS' and host['running']==[]
assert analysis['acked_steps_after_primary_off']==11 and analysis['syn_transmissions_observed']==1
assert analysis['tcp_retransmissions_observed']==1
assert not analysis['client_final_result_exists']
carp=read('failover-confirmed-carp.json')
vhids=sorted({p['vhid'] for p in carp['packets'] if p['source']=='192.168.%d.3'%p['vhid'] and p['advskew']==100})
assert vhids==[30,40,50,60,99]
off=read('failover-off-host.json');assert 'OPNsense-Primary' not in {p['name'] for p in off['running']}
reason='Gián đoạn/restart môi trường EVE: khi tiếp tục, host uptime khoảng 3 phút, không có QEMU hoặc client test chạy. Chưa thu đủ native state sau failover, chưa hoàn tất HTTP và chưa kiểm chứng recovery. Tác nhân gây restart chưa xác minh.'
result={'todo':'M3.4 — Kiểm thử pfsync state synchronization khi CARP failover','status':'FAIL/BLOCKED','collector_time':now,'state_before':'PASS — hai entry ESTABLISHED:ESTABLISHED của cùng flow trên Primary','state_sync':sync,'failover':{'status':'OBSERVED_IN_PACKET_EVIDENCE','primary_off_confirmed':True,'secondary_advertised_vhids':vhids,'all_five_vips_arp_observed':all(r['vip_conflict_seen'] for r in read('failover-confirmed-arp.json')['rows']),'native_after_state_fully_retrieved':False},'connection':{'status':'CONTINUED_DURING_OBSERVED_INTERVAL_THEN_TEST_INTERRUPTED','acked_markers_after_primary_off':11,'syn_transmissions':1,'tcp_retransmissions':1,'no_reconnect_observed':True,'http_completed':False,'zero_packet_loss_claimed':False,'evidence':'interrupted-analysis.json and intact raw log/PCAP prefixes'},'recovery':{'status':'NOT_RUN','qemu_running_at_resume':[],'current_carp_pfsync':'NOT_VERIFIED'},'reason':reason,'configuration_changes':{'firewall_rules':False,'NAT_DHCP':False,'VIP_VHID_advskew':False,'Core':False,'topology':False,'endpoint_runtime_route':'Data-Center: 192.168.40.100/32 via 192.168.30.1 dev lan0; original IP/default route/netplan preserved when checked; route after restart not checked'},'checkpoint':'Keep M3.1/M3.2/M3.3 historical PASS. M3.4 not complete. Need restore lab baseline and rerun M3.4 as a new TCP session; do not replay native apply or old TCP sequence numbers. No next TODO.'}
(OUT/'M3.4-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')

rel='evidence/M3/M3.4-pfsync-state-20261104'
notice=f'''# CHECKPOINT MỚI NHẤT — M3.4 FAIL/BLOCKED — {now}

## 0.1. Kết quả và nguyên nhân

**M3.4 chưa hoàn thành.** {reason}

- STATE BEFORE/SYNC: đã kiểm chứng hai entry ESTABLISHED của flow TCP `192.168.40.100:44340 → 192.168.30.10:8000`; state ID `bf10eb6a00000000`, `c010eb6a00000000` và creator ID `c70da713` khớp trên Primary/Secondary. Secondary BACKUP có counter0:0 trước tiếp quản; có pfsync protocol240 hai chiều.
- FAILOVER: đã soft shutdown riêng Primary, host xác nhận Primary tắt và Core/Secondary/DC còn chạy; Secondary .3 quảng bá đủ VHID30/40/50/60/99, năm VIP .1 trả lời ARP. Bản native state sau failover đã tạo header checksum nhưng chưa nhận đủ payload; không coi là evidence đã giải mã.
- CONNECTION: 11 marker của cùng TCP session được ACK sau khi Primary tắt; một SYN, không reconnect, một retransmission được ghi nhận. Chưa hoàn tất HTTP; không kết luận zero packet loss hoặc kết nối hoạt động ở thời điểm hiện tại.
- RECOVERY: **NOT_RUN**. Kiểm tra tiếp quản thấy EVE uptime khoảng3 phút, không có QEMU và không còn process client; file live.json là snapshot cũ. Không tự bật lại node hoặc tạo kết nối khác để che mất session gốc.
- [Báo cáo/danh mục minh chứng]({rel}/evidence-index.md), [kết quả]({rel}/M3.4-result.json). Raw log/PCAP đã được bảo toàn byte gốc, các đuôi NUL/truncated được ghi rõ; chưa có client-result.json/wire-result.json.
- Backup: trên mỗi firewall `/root/soc-m34-20261104/config.before.xml`; trên DC `/root/soc-m34-20261104/routes.before.json` (0600). Chỉ thêm host route runtime `.40.100/32 via .30.1` để chiều về dùng CARP; IP/default route/netplan không đổi khi kiểm tra. Sau restart chưa đọc lại route trong guest. Không sửa rule, NAT/DHCP, CARP parameters, Core hoặc topology.
- Điểm tiếp tục: khôi phục đúng baseline rồi thử lại **duy nhất M3.4 với session mới**; không thể tiếp tục session TCP cũ. Nếu lấy lại payload state cũ để lưu trữ phải khớp hash trong staged-result-checkpoint.json; đó không phải runtime mới. M3.1–M3.3 giữ PASS lịch sử. **Không làm TODO khác; dừng tại đây.**

---

'''
todo=Path('docs/SOC_TO_DO.md');lines=todo.read_text(encoding='utf-8').splitlines(keepends=True)
for i,l in enumerate(lines):
    if l.startswith('| M3.4 '):
        lines[i]=f'| M3.4 — Kiểm thử pfsync state synchronization khi CARP failover | FAIL/BLOCKED — {now}; state sync PASS, test bị gián đoạn trước hoàn tất/recovery | `{rel}/M3.4-result.json`; `interrupted-analysis.json` |\n';break
else:raise RuntimeError('Missing M3.4 TODO')
shutil.copy2(todo,OUT/'SOC_TO_DO.before-final.md')
todo.write_text(notice+''.join(lines),encoding='utf-8')
progress=Path('docs/PROGRESS.md');shutil.copy2(progress,OUT/'PROGRESS.before-final.md');progress.write_text(notice+progress.read_text(encoding='utf-8'),encoding='utf-8')

report=f'''# CHƯƠNG 3. KIỂM THỬ ĐỒNG BỘ STATE PFSYNC KHI CARP FAILOVER — M3.4

## 3.4.1. Kết luận và phạm vi

**FAIL/BLOCKED**, tổng hợp lúc {now} (UTC+07:00). Đồng bộ state trước failover có bằng chứng PASS; đã quan sát dữ liệu tiếp tục qua Secondary sau khi Primary tắt. {reason} Không biến phần kết quả đạt thành nghiệm thu toàn M3.4.

Thời gian thu dựa trên collector chuyển sang UTC+07:00. Giờ EVE/guest được ghi là untrusted. Khoảng thời gian tương đối trong client/wire dùng monotonic của lần chạy cũ; không dùng snapshot cũ để suy uptime hoặc kết nối hiện tại. Đợt gốc thu khoảng11:10–11:24; lượt tiếp quản thu lại khoảng16:14 trở đi cùng ngày04/11/2026.

## 3.4.2. Thiết kế phép thử và thuật ngữ

TCP (Transmission Control Protocol — giao thức điều khiển truyền vận) theo dõi sequence/acknowledgement để truyền dữ liệu tin cậy. State của Packet Filter (PF — tên bộ lọc gói) lưu flow và trạng thái hai chiều. pfsync là tên chính thức của cơ chế/giao diện đồng bộ state, không tự tạo dạng khai triển. Trong SOC, state đồng bộ cho phép firewall dự phòng xử lý flow đang có thay vì chỉ nhận kết nối mới. Ví dụ đã kiểm chứng: hai state ID của flow bên dưới hiện diện trên Secondary lúc BACKUP, có cùng creator ID và sequence window như Primary.

CARP (Common Address Redundancy Protocol — giao thức dự phòng địa chỉ chung) điều phối firewall phục vụ Virtual IP address (VIP — địa chỉ IP ảo). VIP VLAN40 .40.1 được client dùng làm gateway; chiều về dùng VIP VLAN30 .30.1. HTTP (Hypertext Transfer Protocol — giao thức truyền siêu văn bản) là lưu lượng ứng dụng lành tính trên dịch vụ DC đã có TCP8000. Lượt này mở đúng một TCP session và giữ một HTTP request chưa kết thúc header để đọc state; không tạo nhiều kết nối hoặc tấn công dịch vụ.

Client là script TCP qua AF_PACKET trên host EVE hiện có, gắn vào access TAP `vunl0_3_1` có sẵn, không thêm interface/link hoặc gán IP vào network stack host. Không báo đây là VPCS hay TCP socket kernel Linux. Employee VPCS không chạy; client kiểm tra ARP trùng IP trước khi dùng IP theo plan `.40.100`, MAC `02:53:4f:43:04:34`. Server là VM Data-Center thật `.30.10:8000` (đã boot node có sẵn). RAM Core/Primary/Secondary/DC lần lượt1024/2048/2048/1024 MiB.

Rule Primary hiện có cho phép `.40.100 → .30.10:8000`; Secondary không có rule tạo flow mới tương ứng. Không thêm allow-any hoặc sửa rule. Default route DC vẫn `.30.2`; chỉ thêm route runtime `.40.100/32 via .30.1` sau backup để flow thử quay về qua CARP. Ảnh xác nhận IP/default route giữ nguyên và backup route0600. Không sửa netplan; không cleanup route hoặc node sau thử. Sau gián đoạn, guest đều OFF và route chưa được xác minh lại.

## 3.4.3. Bảng kết quả và cách diễn giải

| Hạng mục | Kết quả | Minh chứng |
|---|---|---|
| BEFORE: Primary MASTER, Secondary BACKUP năm VLAN, syncok1/demotion0 | PASS | before-acceptance.json; hai before.json |
| State ESTABLISHED trên Primary | PASS | primary-state-before.json; ảnh state-readable-before |
| Đồng bộ hai state ID/creator ID sang Secondary BACKUP | PASS | state-sync-acceptance.json; secondary-state-before.json, counter0:0 |
| Primary tắt; Secondary quảng bá đủ năm VHID và VIP trả lời ARP | Đã quan sát qua gói và host | failover-off-host.json; failover-confirmed-carp/arp.json |
| Native state cũ còn tồn tại trên Secondary sau tiếp quản | CHƯA THU ĐỦ | mới có header checksum và một phần transport; không có JSON đã giải mã |
| Cùng session tiếp tục gửi/ACK sau khi Primary tắt | Đã quan sát11 marker ACK | interrupted-analysis.json; client-events-valid-records.json; wire-valid-records.json |
| HTTP request hoàn tất | CHƯA ĐẠT NGHIỆM THU | không có HTTP200 và không có client-result.json |
| Recovery Primary MASTER / Secondary BACKUP / pfsync READY | NOT_RUN | host-resume-check.json: không QEMU; resume-process-check.json |
| Tổng M3.4 | FAIL/BLOCKED | M3.4-result.json |

Hai state ID là `bf10eb6a00000000`, `c010eb6a00000000`; cùng creator ID `c70da713`. Primary có counter và origif tương ứng ingress VLAN40/egress VLAN30; Secondary BACKUP có counter0:0. Không coi hai entry là hai TCP session: chúng thuộc cùng4-tuple. Log client ghi một SYN và giữ nguyên client/server initial sequence numbers; không tự reconnect. Wire capture cho thấy trước chuyển vai, gói đi qua trunk Primary với MAC `50:00:00:01:00:00`; sau khi Primary OFF, gói hai chiều xuất hiện trên trunk Secondary với MAC `50:00:00:02:00:00`, VLAN40↔30 và TTL qua router. Bằng chứng này hỗ trợ kết luận dữ liệu đã tiếp tục trong khoảng quan sát, không thay thế native state sau failover đang thiếu.

Có một TCP retransmission được ghi nhận quanh chuyển vai; đây không phải phép đo toàn bộ mất gói. Không tuyên bố zero packet loss, gián đoạn bằng0 hoặc hoàn tất HTTP. Nguyên nhân kết thúc phép thử là môi trường bị gián đoạn/restart theo host uptime/process mất; chưa xác định tác nhân, không quy kết CARP làm đứt kết nối.

## 3.4.4. Minh họa thực tế

'''
figs=[('dc-before-public','Data-Center trước test.','Xác nhận IP .30.10, HTTP8000 active và default route .30.2; chọn đúng endpoint đã có.'),('dc-backup-proof','Backup route và chiều về qua CARP.','Ảnh đọc tệp route gốc mode0600 và route get .40.100 qua .30.1; minh chứng backup trước đổi runtime.'),('primary-state-readable-before','State trên Primary.','Hai entry ESTABLISHED cùng4-tuple; đọc ID/creator, counter, origif để thiết lập baseline.'),('secondary-state-readable-before','State đồng bộ trên Secondary BACKUP.','Đọc cùng ID/creator và window; counter0:0 hỗ trợ việc state được đồng bộ trước khi mang traffic.'),('primary-soft-shutdown','Controlled failover bằng tắt mềm Primary.','Lệnh shutdown -p now trên đúng console; kết hợp host xác nhận Primary OFF.')]
num=1
for prefix,title,explain in figs:
    pics=sorted(OUT.glob(prefix+'-2026*.png'))
    if not pics:continue
    pic=pics[-1];cap=f'Hình 3.{num}. {title}'
    report+=f'![{cap}]({pic.name})\n\n{cap}\n\nMục đích, nội dung, kết quả và ý nghĩa: {explain}\n\n';num+=1
report+='''## 3.4.5. Tính toàn vẹn và checkpoint

Đã sao chép byte gốc log/PCAP còn trên EVE vào `interrupted-artifacts/`, đối chiếu SHA-256 trong interrupted-artifact-manifest.json; không sửa bản gốc. Client JSONL có263 byte NUL cuối, wire JSONL có714 byte NUL cuối. Các bản derived chỉ phân tích143 client records và133 wire records nguyên vẹn; vị trí/độ dài/hash phần hỏng được ghi rõ. Không nội suy hoặc tái tạo dữ liệu mất. PCAP có thể kết thúc giữa record do gián đoạn; chỉ các frame đầy đủ mới được dùng khi phân tích sau này. Không có kết quả đóng bình thường client-result.json hoặc wire-result.json.

Bản native after-failover nằm dự kiến tại `/var/tmp/soc-m3-todo-secondary-state-after-failover.b64` trong Secondary. Header đã nhận khai báo1748 byte encoded, SHA-256 `1d85e1fba1077f1d1da92d2723605423f7c8213f4355b3c39dde4998e5285448`; chưa nhận đủ payload. Có thể lấy lại để lưu trữ nếu file còn và hash khớp, nhưng không trình bày nó như runtime mới. Không boot node chỉ để lấy ảnh hoặc ghi log trong lượt kết thúc này.

Checkpoint: M3.1–M3.3 giữ PASS lịch sử; M3.4 chưa DONE. Hiện không QEMU chạy, client cũ đã mất. Cần khôi phục baseline rồi thực hiện lại duy nhất M3.4 bằng session mới; không thể tiếp tục sequence cũ hoặc dùng snapshot live.json làm kết nối hiện tại. Không chạy lại payload native apply đã nghiệm thu để ép kết quả, không NAT/DHCP, không M4/M5 hoặc cleanup.

## 3.4.6. Danh mục minh chứng

| Tệp | Nội dung | Thời điểm thu (múi giờ) | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
'''
for p in sorted(OUT.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.py','.txt'] or p.name in ['evidence-index.md','sha256-manifest.json']:continue
    relfile=p.relative_to(OUT).as_posix();when=dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone(dt.timedelta(hours=7))).isoformat();desc='Log/JSON hoặc bản sao tài liệu; xem pha trong tên tệp'
    if p.suffix=='.png':desc='Ảnh console thực tế, nguyên nội dung'
    if 'interrupted-artifacts' in p.parts:desc='Bản sao byte gốc sau gián đoạn; thời điểm này là lúc sao chép, không phải runtime mới'
    elif p.suffix=='.json':
        d=json.loads(p.read_text(encoding='utf-8'))
        if isinstance(d,dict):when=d.get('collector_time',d.get('collector_time_end',when))
    report+=f'| {relfile} | {desc} | {when} | docs/{rel}/{relfile} | M3.4 — pha tương ứng/phụ lục truy vết |\n'
(OUT/'evidence-index.md').write_text(report,encoding='utf-8')
manifest={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='sha256-manifest.json'}
(OUT/'sha256-manifest.json').write_text(json.dumps({'collector_time':now,'sha256':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':result['status'],'state_sync':'PASS','acked_after_off':11,'retransmissions':1,'recovery':'NOT_RUN','evidence':str(OUT)},ensure_ascii=True))
