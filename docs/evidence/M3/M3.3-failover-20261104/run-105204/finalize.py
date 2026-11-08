"""Báo cáo M3.3B từ evidence; chỉ DONE/PASS khi đủ ba acceptance."""
import datetime as dt,hashlib,json,sys
from pathlib import Path
OUT=Path(__file__).parent
BASE=OUT.parent
status=sys.argv[1]
assert status in ['DONE/PASS','FAIL/BLOCKED']
reason=sys.argv[2] if len(sys.argv)>2 else ''
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
def get(name):
    p=OUT/(name+'.json')
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None
accept={phase:get(phase+'-acceptance') for phase in ['before','failover','recovery']}
if status=='DONE/PASS':
    assert all(d and d['status']=='PASS' for d in accept.values())
    assert (OUT/'core-recovery-public-observation.json').exists()
    assert get('core-recovery-public-observation')['pass_verified']
    norm=lambda h:{n['name']:{k:v for k,v in n.items() if k not in ['left','top']} for n in h['nodes']}
    assert norm(get('host-before'))==norm(get('recovery-host'))
data={'todo':'M3.3 — CARP failover/recovery','status':status,'collector_time':now,'reason':reason,'phases':accept,'method':'Soft shutdown Primary bằng shutdown -p now; chỉ boot lại Primary sau failover PASS.','configuration_changed':False,'native_pfsync_reapply_during_recovery':False,'carp_parameters_changed':False,'session_preservation_tested':False,'scope':'Chỉ CARP failover/recovery năm VLAN và readiness; không NAT/DHCP, không M3.4/M4/M5.','evidence_directory':str(OUT)}
with (OUT/'M3.3-acceptance.json').open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
summary=('Failover PASS: Primary đã tắt, Secondary tự MASTER cả VLAN30/40/50/60/99, đủ VIP .1 và ARP qua Core; recovery PASS: Primary tự MASTER, Secondary BACKUP năm VLAN; pfsync UP/RUNNING, syncok1, demotion0 hai phía; Core/VLAN hoạt động. Không áp lại native pfsync hoặc sửa CARP để đạt kết quả.' if status=='DONE/PASS' else reason)
rel='evidence/M3/M3.3-failover-20261104/'+OUT.name
notice=f'''# CHECKPOINT MỚI NHẤT — M3.3 {status} — {now}

## 0.1. Kết quả M3.3B

**M3.3 — CARP failover/recovery: {status}.** {summary}

- Minh chứng BEFORE / FAILOVER / RECOVERY: [danh mục]({rel}/evidence-index.md), [kết quả]({rel}/M3.3-acceptance.json). Checkpoint này thay trạng thái READY_FOR_FAILOVER trước đó; các phần bên dưới giữ làm lịch sử.
- Backup config root-only trên mỗi firewall: `/root/soc-m33b-20261104/config.before.xml`; bản sao tài liệu và metadata lab được giữ trong đợt này. Không đổi VIP/VHID/advbase/advskew, topology, resource, Core, VLAN/IP hoặc NAT/DHCP.
- Không suy phép thử CARP thành nghiệm thu giữ phiên/kết nối liên tục, WAN/NAT/DHCP HA hoặc toàn bộ SOC. Không làm M3.4/M4/M5, không cleanup.
- **Dừng tại đây. NEXT TODO: chưa được giao; không tự tạo hoặc triển khai mục mới.**

---

'''
todo=Path('docs/SOC_TO_DO.md');lines=todo.read_text(encoding='utf-8').splitlines(keepends=True)
for i,line in enumerate(lines):
    if line.startswith('| M3.3 '):
        lines[i]=f'| M3.3 — CARP failover/recovery | {status} — {now} | `{rel}/M3.3-acceptance.json`; BEFORE/FAILOVER/RECOVERY |\n';break
else:raise RuntimeError('M3.3 row missing')
todo.write_text(notice+''.join(lines),encoding='utf-8')
progress=Path('docs/PROGRESS.md');progress.write_text(notice+progress.read_text(encoding='utf-8'),encoding='utf-8')
index=f'''# CHƯƠNG 3. KIỂM THỬ CARP FAILOVER VÀ RECOVERY — M3.3B

## 3.3.1. Phạm vi, phương pháp và kết quả

Thời điểm tổng hợp: {now} (UTC+07:00). **{status}**. {summary}

Core chỉ thực hiện Layer 2; gateway dự phòng vẫn ở OPNsense. CARP (Common Address Redundancy Protocol — giao thức dự phòng địa chỉ chung) cho phép một firewall MASTER phục vụ địa chỉ ảo (VIP — Virtual IP address), firewall BACKUP tiếp quản khi không còn nhận quảng bá của MASTER. Trong topology SOC này, năm VIP 192.168.30.1/40.1/50.1/60.1/99.1 ứng với VLAN30/40/50/60/99. Phép thử sử dụng tắt mềm Primary, giữ Core và Secondary hoạt động, rồi boot lại Primary sau khi nghiệm thu failover.

pfsync là tên chính thức của giao diện/giao thức đồng bộ trạng thái Packet Filter, không tự tạo dạng khai triển. Vai trò trong SOC là đồng bộ trạng thái giữa hai firewall qua SYNC 10.255.255.1/30 ↔ 10.255.255.2/30. Kiểm tra syncok1 và gói protocol240 hai chiều trong lượt này xác nhận readiness trước/sau, chưa chứng minh giữ phiên ứng dụng.

## 3.3.2. Bảng kết quả

| Pha | Trạng thái | Minh chứng chính |
|---|---|---|
'''
for phase,d in accept.items():index+=f'| {phase.upper()} | {d["status"] if d else "CHƯA NGHIỆM THU"} | {phase}-acceptance.json, runtime/host/ARP/CARP tương ứng |\n'
index+='''
Config hai firewall được kiểm tra SHA-256 với backup trước phép thử; persistent VIP/VHID/advbase/advskew được đối chiếu trước/sau. Core và Secondary không bị stop/reboot: PID host được đối chiếu qua các pha. Primary phải có boottime mới ở recovery. Không dùng ảnh cũ để kết luận runtime mới. Thời điểm thu dựa trên đồng hồ collector chuyển sang UTC+07:00; giờ bên trong EVE/guest được giữ riêng và không dùng thay giờ thu.

Các bản `failover-*` đầu tiên được thu trong quá trình shutdown; nghiệm thu pha failover sử dụng bộ `failover-confirmed-*` sau khi host xác nhận Primary đã tắt. Trường ARP `vip_conflict_seen` trong collector tái sử dụng chỉ mang nghĩa quan sát trả lời VIP; trong phép thử này VIP đã cấu hình, trường đó không phải kết luận xung đột.

Lệnh đọc OVSDB trước test bằng sudo -n không chạy vì sudo cache đã hết hạn; giữ ảnh lỗi, không thay đổi xác thực. Core được kiểm tra qua systemctl, địa chỉ/forwarding, PID liên tục và ARP trên năm access port; không tuyên bố đã audit lại đầy đủ OVSDB nếu không có output.

## 3.3.3. Ảnh minh họa thực tế

'''
images=[('primary-before-readable','Primary MASTER và VIP trước failover.','Đọc năm vai trò MASTER và các VIP .1; thiết lập baseline thực tế.'),('secondary-before-readable','Secondary BACKUP trước failover.','Đọc năm vai trò BACKUP và các VIP .1; xác nhận dự phòng trước test.'),('primary-soft-shutdown','Lệnh shutdown mềm Primary.','Xác nhận đúng node nhận shutdown -p now; host sau đó kiểm tra QEMU đã kết thúc.'),('secondary-failover-readable','Secondary MASTER sau khi Primary tắt.','Đọc MASTER/VHID của năm VLAN và VIP .1; kết hợp ARP và quảng bá từ .3 chứng minh tiếp quản.'),('primary-recovery-readable','Primary sau recovery.','Đọc vai trò và VIP sau boot mới; nghiệm thu dựa trên recovery-acceptance.json.'),('secondary-recovery-readable','Secondary sau recovery.','Đọc vai trò và VIP tương ứng; xác minh trở về BACKUP khi Primary phục hồi.'),('core-recovery-public','Core và dịch vụ OVS sau recovery.','Kiểm tra OVS active, không IP ngoài loopback, forwarding0/0; kết hợp ARP năm VLAN chứng minh Core/VLAN tiếp tục hoạt động.')]
images += [('primary-recovery-pfsync','Pfsync và SYNC Primary sau recovery.','Đọc syncok1, demotion0, đúng peer và ping SYNC thành công; xác nhận Primary tự phục hồi pfsync.'),('secondary-recovery-pfsync','Pfsync và SYNC Secondary sau recovery.','Đọc syncok1, demotion0 và ping thành công phía đối ứng; đối chiếu readiness hai firewall.')]
fig=1
for prefix,title,purpose in images:
    matches=sorted(OUT.glob(prefix+'-*.png'))
    if not matches:continue
    p=matches[-1];caption=f'Hình 3.{fig}. {title}'
    index+=f'![{caption}]({p.name})\n\n{caption}\n\nMục đích, nội dung và ý nghĩa: {purpose} Kết quả xem bảng và JSON nghiệm thu tương ứng; không suy rộng ngoài phạm vi.\n\n';fig+=1
index+='''## 3.3.4. Danh mục minh chứng

| Tệp | Nội dung | Thời điểm thu, múi giờ | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
'''
for p in sorted(OUT.iterdir()):
    if not p.is_file() or p.suffix in ['.py','.txt'] or p.name in ['evidence-index.md','sha256-manifest.json']:continue
    when=dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone(dt.timedelta(hours=7))).isoformat()
    desc='Ảnh console thật, nguyên nội dung' if p.suffix=='.png' else 'Log/runtime/metadata hoặc bản sao tài liệu; xem tên pha'
    if p.suffix=='.json':
        d=json.loads(p.read_text(encoding='utf-8'));when=d.get('collector_time',d.get('collector_time_end',when))
    index+=f'| {p.name} | {desc} | {when} | docs/{rel}/{p.name} | M3.3 — pha tương ứng/phụ lục truy vết |\n'
for p in sorted(BASE.glob('m33b-*-shell-*')):
    when=dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone(dt.timedelta(hours=7))).isoformat()
    if p.suffix=='.json':when=json.loads(p.read_text(encoding='utf-8')).get('collector_time_end',when)
    index+=f'| {p.name} | Kiểm tra console/shell trước gửi lệnh; ảnh thật và metadata | {when} | docs/evidence/M3/M3.3-failover-20261104/{p.name} | M3.3 — kiểm tra transport ban đầu |\n'
index+=f'\n## 3.3.5. Giới hạn và điểm dừng\n\n{summary} Không kiểm thử giữ phiên TCP/UDP, thời gian gián đoạn ứng dụng, NAT/DHCP hoặc M4/M5. Dừng sau M3.3; chưa có NEXT TODO được giao.\n'
(OUT/'evidence-index.md').write_text(index,encoding='utf-8')
oldindex=BASE/'evidence-index.md'
if oldindex.exists():
    backup=OUT/'evidence-index-parent.before.md'
    if not backup.exists():backup.write_bytes(oldindex.read_bytes())
    old=oldindex.read_text(encoding='utf-8')
else:old=''
oldindex.write_text(f'# Checkpoint M3.3B — {status} — {now}\n\n[Danh mục BEFORE/FAILOVER/RECOVERY mới]({OUT.name}/evidence-index.md). [Kết quả]({OUT.name}/M3.3-acceptance.json). {summary}\n\nCác mục bên dưới là lịch sử, giữ nguyên để truy vết.\n\n---\n\n'+old,encoding='utf-8')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='sha256-manifest.json'}
(OUT/'sha256-manifest.json').write_text(json.dumps({'collector_time':now,'sha256':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':status,'evidence':str(OUT),'reason':reason},ensure_ascii=True))
