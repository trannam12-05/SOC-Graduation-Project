"""Ghi checkpoint từ minh chứng thực tế; không chạy failover hay sửa guest."""
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, 'automation')
from topology_remote import remote
from m3_resource_optimization import CODE

OUT = Path('docs/evidence/M3/M3.3-restore-20261104')
now = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
host = json.loads(remote(CODE, timeout=50))
host['collector_time'] = now
(OUT/'host-final.json').write_text(json.dumps(host, ensure_ascii=False, indent=2), encoding='utf-8')
assert {(n['name'], int(n['ram'])) for n in host['running']} == {('SOC-Core-L2',1024), ('OPNsense-Primary',2048), ('OPNsense-Secondary',2048)}
checks = {}
for role, state, last, peer in [('primary','MASTER',2,'10.255.255.2'), ('secondary','BACKUP',3,'10.255.255.1')]:
    d = json.loads((OUT/(role+'-runtime-restored.json')).read_text(encoding='utf-8'))
    old = json.loads((Path('docs/evidence/M3/todo-completion-20261103')/(role+'-carp-verified.json')).read_text(encoding='utf-8'))
    assert d['role'] == role and len(d['rows']) == 5
    assert {r['vlan'] for r in d['rows']} == {30,40,50,60,99}
    for row in d['rows']:
        assert row['state'] == [state] and row['physical_ip_ok'] and row['vip_ok'] and row['up'] and row['active'], row
        assert row['persistent'] == next(r['persistent'] for r in old['rows'] if r['vlan']==row['vlan'])
        assert ('advbase 1 advskew '+('0' if last==2 else '100')) in row['carp'][0]
    pf = d['pfsync']['out']
    assert d['pfsync']['rc']==0 and 'UP' in pf.splitlines()[0] and 'RUNNING' in pf.splitlines()[0]
    assert all(s in pf for s in ['syncdev: vtnet2','syncpeer: '+peer,'syncok: 1'])
    assert d['demotion']['rc']==0 and d['demotion']['out'].strip()=='0'
    assert d['ping']['rc']==0 and '0.0% packet loss' in d['ping']['out']
    assert d['hook_this_boot'] and d['hook_native_rc0'] and d['config_unchanged']
    assert d['config_sha256'] == d['backup_sha256'] == old['config_sha256']
    assert ('inet 10.255.255.'+str(last-1)+' netmask 0xfffffffc') in d['sync']['out']
    checks[role] = {'state':state,'vlans':[30,40,50,60,99],'pfsync_ready':True,'syncok':1,'demotion':0,'hook_this_boot':True,'config_matches_M3_2':True,'backup_path':d['backup_path']}

arp=json.loads((OUT/'arp-restored.json').read_text())
assert len(arp['rows'])==5 and all(r['primary_seen'] and r['secondary_seen'] and r['vip_conflict_seen'] for r in arp['rows'])
pack=json.loads((OUT/'pfsync-restored.json').read_text())
assert pack['both_directions']
carp=json.loads((OUT/'carp-restored.json').read_text())
assert {(p['vhid'],p['source']) for p in carp['packets']} == {(v,'192.168.%d.2'%v) for v in [30,40,50,60,99]}

core_public=next(OUT.glob('core-public-proof-*.png'))
core_ovs=next(OUT.glob('core-ovs-compact-*.png'))
result={'todo':'M3.3','status':'READY_FOR_FAILOVER','collector_time':now,'core':{'status':'PASS','basis':'Ảnh console thật đã đọc: OVS services active; port access/trunk đúng năm VLAN; flow NORMAL; không IP ngoài loopback; forwarding IPv4/IPv6=0; ARP .2/.3/.1 qua năm access port.','evidence':[core_public.name,core_ovs.name,'arp-restored.json']},'firewalls':checks,'failover_tested':False,'recovery_tested':False,'runtime_native_restore_primary':True,'automatic_simultaneous_boot_readiness':False,'guest_configuration_changed':False,'changes':'Boot ba node, tạo backup/checkpoint; gọi lại /usr/local/sbin/pluginctl -c pfsync trên Primary để khôi phục runtime M3.1. Không sửa config hoặc CARP parameters.','pfsync_packet_both_directions':True,'limitations':['READY_FOR_FAILOVER chỉ xác nhận điều kiện đầu; M3.3 failover/recovery chưa DONE/PASS.','Trường vip_conflict_seen trong collector ARP cũ chỉ nghĩa có trả lời VIP; ở đây VIP đã được cấu hình, không phải kết luận xung đột.','Hash toàn lab có thể khác do tọa độ giao diện; đối chiếu riêng node/network/mapping bên dưới.']}
before=json.loads((OUT/'host-before.json').read_text())
def mapping(h):
    return {n['name']:{k:v for k,v in n.items() if k not in ['left','top']} for n in h['nodes']}
assert mapping(before)==mapping(host), 'Unexpected node/resource/interface change'
result['node_resource_interface_mapping_unchanged']=True
result['lab_sha256_before']=before['lab_sha256']
result['lab_sha256_after']=host['lab_sha256']
(OUT/'M3.3-readiness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')

notice=f'''# CHECKPOINT MỚI NHẤT — M3.3 READY_FOR_FAILOVER — {now}

## 0.1. Phạm vi và trạng thái

Đã khôi phục đúng điều kiện đầu theo quyền người dùng: chỉ boot Core L2 1024 MiB, OPNsense Primary 2048 MiB và Secondary 2048 MiB. **M3.3: READY_FOR_FAILOVER; chưa chạy failover/recovery, chưa DONE/PASS M3.3.** Checkpoint này thay trạng thái BLOCKED trước đó; các phần phía dưới giữ làm lịch sử.

- Core: OVS active; access VLAN30/40/50/60/99 và trunk đúng; flow NORMAL; không IP ngoài loopback; forwarding IPv4/IPv6=0. ARP qua cả năm access port nhận đủ .2/.3/.1.
- Primary: IP 192.168.VLAN.2/24, CARP MASTER cả năm VLAN; Secondary: IP 192.168.VLAN.3/24, BACKUP cả năm VLAN. VIP 192.168.30.1, .40.1, .50.1, .60.1, .99.1/24 đúng VHID30/40/50/60/99; advbase1, skew0/100 giữ nguyên.
- SYNC 10.255.255.1/30 ↔ 10.255.255.2/30 ping được; pfsync UP/RUNNING, đúng peer/vtnet2, syncok1, demotion0 hai phía; hook chạy trong boot hiện tại; có gói protocol240 hai chiều.
- Config hai firewall khớp SHA-256 đã nghiệm thu M3.2; đã cần gọi lại native pfsync trên Primary để khôi phục runtime M3.1 (syncok0/demotion240 → syncok1/demotion0); không sửa cấu hình lưu, VIP/VHID/skew hoặc hook. Backup root-only trên mỗi firewall: `/root/soc-m33-restore-20261104/config.before.xml`; bản sao tài liệu và checkpoint metadata lab đã lưu.
- [Danh mục minh chứng](evidence/M3/M3.3-restore-20261104/evidence-index.md), [kết quả kiểm chứng](evidence/M3/M3.3-restore-20261104/M3.3-readiness.json). Giữ ba node chạy; không NAT/DHCP, không đổi topology/Core/VLAN/IP, không cleanup, không M4/M5. **Dừng trước failover.**

---

'''
todo=Path('docs/SOC_TO_DO.md');lines=todo.read_text(encoding='utf-8').splitlines(keepends=True)
for i,line in enumerate(lines):
    if line.startswith('| M3.3 '):
        lines[i]=f'| M3.3 — CARP failover và recovery thực tế trên năm VLAN | READY_FOR_FAILOVER — {now}; failover/recovery chưa chạy | `evidence/M3/M3.3-restore-20261104/M3.3-readiness.json` |\n'
        break
else: raise RuntimeError('Missing M3.3 TODO')
todo.write_text(notice+''.join(lines),encoding='utf-8')
progress=Path('docs/PROGRESS.md');progress.write_text(notice+progress.read_text(encoding='utf-8'),encoding='utf-8')

index=f'''# 1. M3.3 — Khôi phục điều kiện đầu

## 1.1. Kết luận

**READY_FOR_FAILOVER** lúc {now} (UTC+07:00). Chỉ khôi phục điều kiện đầu; chưa chạy failover/recovery và chưa kết luận M3.3 DONE/PASS. Các kiểm tra bắt buộc đã đạt từ runtime guest, ARP qua Core và gói thật trên SYNC/trunk. Không sửa cấu hình guest; có gọi lại native pfsync trên Primary theo quyền khôi phục M3.1.

## 1.2. Bảng kết quả

| Hạng mục | Kết quả | Minh chứng |
|---|---|---|
| Đúng ba QEMU, RAM 1024/2048/2048 MiB | PASS | host-final.json |
| OVS, Core chỉ L2, access/trunk năm VLAN, flow NORMAL | PASS | core-public-proof, core-ovs-compact; arp-restored.json |
| Primary .2, Secondary .3 và VIP .1 cả năm VLAN | PASS | hai runtime-restored.json; arp-restored.json |
| SYNC ping; pfsync UP/RUNNING, đúng peer, syncok1 | PASS | hai runtime-restored.json; pfsync-restored.json |
| Demotion0; hook đúng boot | PASS | hai runtime-restored.json |
| Primary MASTER / Secondary BACKUP cả năm VLAN | PASS | hai runtime-restored.json; carp-restored.json |
| Cấu hình giữ nguyên từ M3.2 | PASS | hash trong runtime-restored.json đối chiếu carp-verified cũ |
| Failover/recovery | NOT_RUN | Ngoài phạm vi lượt này |

## 1.3. Ảnh minh họa

'''
pics=[(core_public,'Hình 3.1. Core sau boot: dịch vụ OVS, địa chỉ và forwarding.','Xác nhận Core chỉ chuyển mạch Layer 2; OVS active, không IP ngoài loopback và forwarding0/0.'),(core_ovs,'Hình 3.2. Bảng port VLAN/trunk và flow NORMAL.','Xác nhận mapping access/trunk và flow chuyển mạch đã tự phục hồi; ARP năm VLAN kiểm chứng đường dữ liệu.')]
pics += [(next(OUT.glob('primary-carp-readable-*.png')), 'Hình 3.3. Primary MASTER trên năm VLAN.', 'Đọc IP .2, VIP .1 và MASTER/VHID30/40/50/60/99, advbase1/skew0; khẳng định vai trò ban đầu đã khôi phục.'), (next(OUT.glob('secondary-carp-readable-*.png')), 'Hình 3.4. Secondary BACKUP trên năm VLAN.', 'Đọc IP .3, VIP .1 và BACKUP cả năm VHID, skew100; xác nhận thiết kế dự phòng.'), (next(OUT.glob('primary-pfsync-readable-*.png')), 'Hình 3.5. Pfsync và SYNC Primary sau khôi phục.', 'Pfsync UP/RUNNING, syncok1, demotion0 và ping SYNC thành công; chứng minh readiness hiện tại sau native restore.'), (next(OUT.glob('secondary-pfsync-readable-*.png')), 'Hình 3.6. Pfsync và SYNC Secondary.', 'Pfsync UP/RUNNING, syncok1, demotion0 và ping SYNC thành công; đối chiếu hai phía.')]
for path,caption,explain in pics:
    index+=f'![{caption}]({path.name})\n\n{caption}\n\nMục đích, nội dung, kết quả và ý nghĩa: {explain}\n\n'
index+='''## 1.4. Giới hạn và checkpoint tiếp tục

CARP (Common Address Redundancy Protocol — giao thức dự phòng địa chỉ chung) cho phép một firewall MASTER phục vụ VIP và firewall BACKUP tiếp quản khi mất quảng bá. Trong SOC, VIP là gateway dự phòng của năm VLAN. Lượt này đã xác minh vai trò ban đầu; việc tiếp quản và phục hồi chưa được kiểm thử. pfsync là tên giao diện/giao thức đồng bộ trạng thái của Packet Filter; gói hai chiều và syncok1 chứng minh readiness, không tự chứng minh giữ phiên khi failover. M3.1/M3.2 giữ PASS; bước tiếp tục duy nhất là phép thử M3.3 khi được yêu cầu.

Collector ARP tái sử dụng tên `vip_conflict_seen`; ở lượt này trường đó chỉ là quan sát trả lời VIP, không có nghĩa phát hiện xung đột. Collector đầu trên Primary có lỗi cú pháp và chưa chạy phần thân; giữ ảnh lỗi để truy vết, nghiệm thu dùng `runtime-restored.json` đã truyền và xác minh SHA-256. Không dùng ảnh boot hoặc ảnh lỗi để thay kết quả guest. Hai ảnh `carp-final-proof` không có output do tùy chọn grep qua keyboard bị đổi chữ hoa/thường; không dùng để nghiệm thu. Ảnh `carp-readable` là lần thu thay thế có đầy đủ nội dung, vẫn giữ nguyên ảnh lỗi.

Sau boot đồng thời, Primary từng BACKUP năm VLAN, syncok0/demotion240; Secondary MASTER, syncok1/demotion0. Đã backup config và gọi đúng `/usr/local/sbin/pluginctl -c pfsync` trên Primary, native_rc0; sau đó Primary syncok1/demotion0/MASTER, Secondary về BACKUP. Không đặt demotion thủ công, không đổi CARP parameters. Vì đã cần can thiệp runtime, lượt này không chứng minh hai firewall tự đạt readiness khi boot đồng thời; nguyên nhân bulk-sync ban đầu chưa được kết luận. Minh chứng trước/sau giữ nguyên.

Hai firewall tự khôi phục journal khi boot và báo hệ thống tệp sạch; không can thiệp thủ công. Node/resource/interface mapping trước/sau giữ nguyên khi bỏ qua tọa độ left/top của giao diện; không kết luận toàn tệp lab nguyên byte nếu hash khác.

## 1.5. Danh mục tệp và thời điểm

| Tệp | Nội dung | Thời điểm thu (UTC+07:00) | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
'''
for p in sorted(OUT.iterdir()):
    if p.name in ['evidence-index.md','finalize-readiness.py'] or p.suffix in ['.txt','.py']: continue
    when=dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone(dt.timedelta(hours=7))).isoformat()
    desc='Ảnh console thực tế, nguyên nội dung' if p.suffix=='.png' else 'Log/JSON runtime hoặc metadata; xem tên và nội dung tệp'
    if p.suffix=='.json':
        obj=json.loads(p.read_text(encoding='utf-8'));when=obj.get('collector_time',obj.get('collector_time_end',when))
    index+=f'| {p.name} | {desc} | {when} | docs/evidence/M3/M3.3-restore-20261104/{p.name} | M3.3 — điều kiện đầu/phụ lục truy vết |\n'
(OUT/'evidence-index.md').write_text(index,encoding='utf-8')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='sha256-manifest.json'}
(OUT/'sha256-manifest.json').write_text(json.dumps({'collected_at':now,'sha256':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':result['status'],'roles':checks,'evidence':str(OUT)},ensure_ascii=False))
