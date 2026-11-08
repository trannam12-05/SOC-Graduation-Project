"""Nghiệm thu baseline M3.4A; không thực thi state/failover hoặc sửa guest."""
import datetime as dt,hashlib,json
from pathlib import Path
OUT=Path(__file__).parent
def read(n):return json.loads((OUT/(n+'.json')).read_text(encoding='utf-8'))
now=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
host=read('host-final');before=read('host-before')
expected={'SOC-Core-L2':1024,'OPNsense-Primary':2048,'OPNsense-Secondary':2048,'Data-Center':1024}
assert {n['name']:int(n['ram']) for n in host['running']}==expected,'Node/RAM mismatch'
norm=lambda h:{n['name']:{k:v for k,v in n.items() if k not in ['left','top']} for n in h['nodes']}
assert norm(host)==norm(before),'Node/resource/interface mapping changed'
core=read('core-baseline')
for v in core.values():
    if isinstance(v,dict) and 'rc' in v:assert v['rc']==0,v
assert core['services']['out'].split()==['active']*3
assert core['bridge']['out'].strip()=='br-core-l2' and 'actions=NORMAL' in core['flow']['out']
assert core['ipv4_forwarding']['out'].strip()==core['ipv6_forwarding']['out'].strip()=='0'
addresses=json.loads(core['addresses']['out'])
assert not [a for n in addresses if n['ifname']!='lo' for a in n.get('addr_info',[])],'Non-loopback IP on Core'
ports=json.loads(core['ports']['out']);rows={r[0]:dict(zip(ports['headings'],r)) for r in ports['data']}
def values(v):return v[1] if isinstance(v,list) and v and v[0]=='set' else [v]
vlans=[30,40,50,60,99]
for i,vlan in enumerate(vlans,3):
    r=rows['ens'+str(i)];assert values(r['tag'])==[vlan] and r['vlan_mode']=='access'
for n in ['ens8','ens9']:
    assert set(values(rows[n]['trunks']))==set(vlans) and rows[n]['vlan_mode']=='trunk'
    assert any(a['ifname']==n and 'UP' in a['flags'] for a in addresses)
firewalls={}
for role,state,last,local,peer in [('primary','MASTER',2,'10.255.255.1','10.255.255.2'),('secondary','BACKUP',3,'10.255.255.2','10.255.255.1')]:
    d=read(role+'-baseline');assert d['role']==role and len(d['rows'])==5
    assert {r['vlan'] for r in d['rows']}==set(vlans)
    for row in d['rows']:
        assert row['state']==[state] and all(row[k] for k in ['physical_ip_ok','vip_ok','up','active']),row
        f=row['persistent'];assert f['mode']=='carp' and f['subnet']=='192.168.%d.1'%row['vlan'] and f['subnet_bits']=='24' and f['vhid']==str(row['vlan']) and f['advbase']=='1' and f['advskew']==('0' if role=='primary' else '100')
    pf=d['pfsync']['out'];assert d['pfsync']['rc']==0 and 'UP' in pf.splitlines()[0] and 'RUNNING' in pf.splitlines()[0]
    assert all(t in pf for t in ['syncdev: vtnet2','syncpeer: '+peer,'syncok: 1'])
    assert d['demotion']['out'].strip()=='0' and d['ping']['rc']==0 and '2 packets received' in d['ping']['out']
    assert ('inet '+local+' netmask 0xfffffffc') in d['sync']['out']
    assert d['hook_this_boot'] and d['hook_native_rc0'] and d['config_unchanged'] and d['config_sha256']==d['backup_sha256']
    previous=json.loads((Path('docs/evidence/M3/M3.4-pfsync-state-20261104')/(role+'-before.json')).read_text(encoding='utf-8'))
    assert d['config_sha256']==previous['config_sha256'],'Firewall config differs from previous checkpoint'
    firewalls[role]={'status':'PASS','carp':state,'vlans':vlans,'physical_ip_suffix':last,'vip_suffix':1,'pfsync_ready':True,'syncok':1,'demotion':0,'sync_ping':'2/2','hook_this_boot':True,'config_matches_previous_checkpoint':True,'backup':d['backup_path']}
arp=read('final-baseline-arp');assert len(arp['rows'])==5
for row in arp['rows']:
    assert row['primary_seen'] and row['secondary_seen'] and row['vip_conflict_seen']
    assert any(r['ip']=='192.168.%d.1'%row['vlan'] and r['mac']=='00:00:5e:00:01:%02x'%row['vlan'] for r in row['responses'])
carp=read('final-baseline-carp')
assert {p['vhid'] for p in carp['packets'] if p['source']=='192.168.%d.2'%p['vhid'] and p['advbase']==1 and p['advskew']==0 and p['ttl']==255}==set(vlans)
assert read('final-baseline-pfsync-packets')['both_directions']
endpoint=read('endpoint-baseline');ips=json.loads(endpoint['addresses']['out'])
assert any(a['local']=='192.168.30.10' and a['prefixlen']==24 for n in ips for a in n['addr_info'])
assert endpoint['http_service']['out'].strip()=='active' and '192.168.30.10:8000' in endpoint['listening']['out']
assert int(endpoint['http_main_pid']['out'].strip())>0
integrity=read('previous-evidence-integrity');assert integrity['unchanged']
result={'phase':'M3.4A — Khôi phục baseline','M3.4_status':'READY_FOR_RETEST','collector_time':now,'core':{'status':'PASS','ovs_active':True,'layer2':True,'no_nonloopback_ip':True,'ipv4_forwarding':0,'ipv6_forwarding':0,'access_trunk_five_vlans':True},'firewalls':firewalls,'endpoint':{'status':'PASS','node':'Data-Center','ip':'192.168.30.10/24','service':'soc-lab-http active; 192.168.30.10:8000 LISTEN','default_gateway':'192.168.30.2','old_test_runtime_route_restored':False,'http_request_tested':False},'running_resources_mib':expected,'node_resource_interface_mapping_unchanged':True,'lab_byte_hash_unchanged':host['lab_sha256']==before['lab_sha256'],'state_test_run_this_phase':False,'failover_test_run_this_phase':False,'native_pfsync_reapplied':False,'guest_configuration_changed':False,'previous_M3_4_evidence_unchanged':True,'M3_4_experiment_complete':False,'checkpoint':'Baseline đã đạt; chờ chỉ thị M3.4B với session mới. Không chạy retest hoặc cleanup.'}
(OUT/'M3.4A-readiness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
rel='evidence/M3/M3.4A-baseline-20261104'
notice=f'''# CHECKPOINT MỚI NHẤT — M3.4 READY_FOR_RETEST — {now}

## 0.1. M3.4A — Baseline đã khôi phục

**M3.4 = READY_FOR_RETEST.** Chỉ nghiệm thu baseline M3.4A; chưa chạy M3.4B, chưa kết luận toàn bộ state/failover M3.4 DONE/PASS. Kết quả lần thử bị gián đoạn trước đây được giữ nguyên, không chuyển thành pfsync FAIL.

- Core1024 MiB: OVS active, đúng access/trunk năm VLAN, flow NORMAL; không IP ngoài loopback, forwarding IPv4/IPv6=0, giữ Layer2. ARP qua năm access port nhận đủ Primary .2, Secondary .3 và VIP .1.
- Primary2048 MiB: IP .2/24 và MASTER trên VLAN30/40/50/60/99. Secondary2048 MiB: IP .3/24 và BACKUP cả năm VLAN. VIP .1/24, VHID30/40/50/60/99, advbase1/skew0/100 đúng checkpoint.
- SYNC10.255.255.1/30 ↔ .2/30 ping2/2 hai chiều; pfsync UP/RUNNING, đúng vtnet2/peer, syncok1 và demotion0 hai phía. Hook chạy cùng boot; không phải gọi lại native pfsync hoặc đặt demotion thủ công.
- Endpoint duy nhất: Data-Center1024 MiB, `.30.10/24`, HTTP8000 active/LISTEN. Chỉ đọc dịch vụ, không HTTP request. Default route gốc vẫn `.30.2`; host route runtime riêng `.40.100/32 via .30.1` của lần test cũ không được dựng lại trong M3.4A; chuẩn bị đường client/return qua CARP thuộc bước setup của retest khi được giao.
- Config firewall khớp hash checkpoint trước; backup root-only mỗi firewall: `/root/soc-m34a-baseline-20261104/config.before.xml`. Không đổi topology/resource/IP/VIP/VHID/advskew, không Core/NAT/DHCP hoặc cleanup. Giữ đúng bốn node chạy.
- [Evidence mới]({rel}/evidence-index.md), [kết quả baseline]({rel}/M3.4A-readiness.json). Đã kiểm tra137 tệp minh chứng M3.4 cũ giữ nguyên SHA-256; không xóa/di chuyển.
- **Dừng tại READY_FOR_RETEST; chưa chạy M3.4B, chưa làm TODO khác.**

---

'''
todo=Path('docs/SOC_TO_DO.md');lines=todo.read_text(encoding='utf-8').splitlines(keepends=True)
for i,line in enumerate(lines):
    if line.startswith('| M3.4 '):
        lines[i]=f'| M3.4 — Kiểm thử pfsync state synchronization khi CARP failover | READY_FOR_RETEST — {now}; baseline M3.4A PASS, M3.4B chưa chạy | `{rel}/M3.4A-readiness.json`; evidence test cũ giữ nguyên |\n';break
else:raise RuntimeError('Missing M3.4 TODO row')
todo.write_text(notice+''.join(lines),encoding='utf-8')
progress=Path('docs/PROGRESS.md');progress.write_text(notice+progress.read_text(encoding='utf-8'),encoding='utf-8')
report=f'''# CHƯƠNG 3. KHÔI PHỤC BASELINE M3.4A

## 3.4.1. Kết luận và phạm vi

**READY_FOR_RETEST**, tổng hợp lúc {now} (UTC+07:00). Chỉ boot và xác minh Core, hai OPNsense và Data-Center có sẵn; không state/failover test, không HTTP request, không M3.4B. Chưa kết luận toàn M3.4 DONE/PASS. Không sửa cấu hình guest; pfsync/CARP tự trở lại trạng thái yêu cầu sau boot.

Thời gian thu dùng collector chuyển sang UTC+07:00; giờ bên trong EVE/guest được lưu riêng, không thay giờ collector. Các banner/MOTD cũ trong console Linux không phải địa chỉ runtime; nghiệm thu dùng ip address, service/listener, OVS và ifconfig thực tế trong JSON có transport SHA-256.

## 3.4.2. Bảng kết quả

| Thành phần | Kết quả | Minh chứng |
|---|---|---|
| Đúng bốn node, RAM1024/2048/2048/1024 MiB | PASS | host-final.json; bốn start receipts |
| Core OVS active, Layer2, không IP ngoài loopback, forwarding0/0 | PASS | core-baseline.json; core-public-proof |
| Access ens3–ens7 và trunk ens8/ens9 đúng VLAN30/40/50/60/99 | PASS | core-baseline.json; core-ovs-proof; final-baseline-arp.json |
| Primary .2 và Secondary .3 đúng năm VLAN | PASS | primary/secondary-baseline.json |
| SYNC ping2/2 và pfsync READY, syncok1, demotion0 hai phía | PASS | hai baseline JSON; pfsync-proof; final-baseline-pfsync-packets.json |
| Primary MASTER / Secondary BACKUP năm VLAN, năm VIP .1 đúng | PASS | hai baseline JSON; carp-proof; final-baseline-carp.json |
| Data-Center .30.10/24, HTTP8000 active/LISTEN | PASS mức baseline | endpoint-baseline.json; endpoint-proof; không kiểm thử HTTP request |
| Evidence M3.4 cũ giữ nguyên | PASS | previous-evidence-integrity.json:137 tệp |
| State/failover/recovery test mới | NOT_RUN | Ngoài phạm vi M3.4A |

## 3.4.3. Giải thích và ý nghĩa

Open vSwitch (OVS — tên sản phẩm) làm switch Layer2: flow NORMAL và bảng port access/trunk phân phối frame theo Virtual Local Area Network (VLAN — mạng LAN ảo). Access port mang frame của một VLAN tới endpoint; trunk dùng cơ chế gắn thẻ IEEE802.1Q để mang nhiều VLAN giữa Core và firewall. Đã kiểm chứng mapping access30/40/50/60/99 và trunk năm VLAN, cùng ARP từ các access port tới .2/.3/.1. Core không làm gateway hoặc inter-VLAN routing.

OPNsense là tên sản phẩm firewall. Common Address Redundancy Protocol (CARP — giao thức dự phòng địa chỉ chung) dùng quảng bá để điều phối MASTER/BACKUP phục vụ Virtual IP address (VIP — địa chỉ IP ảo). Trong SOC, các VIP .1 của năm VLAN là gateway dự phòng trên OPNsense; lượt này chỉ xác nhận vai trò ban đầu, không chuyển vai.

pfsync là tên chính thức của giao diện/giao thức đồng bộ state Packet Filter, không tự tạo dạng khai triển. Baseline xác nhận UP/RUNNING, syncdev vtnet2, peer đối ứng đúng, syncok1 và demotion0; có gói protocol240 hai chiều. Không dùng readiness để thay kết luận giữ phiên hoặc state synchronization dưới failover. Kết quả lần test cũ vẫn là bằng chứng một phần của lần thử bị gián đoạn.

Endpoint Data-Center đã tự phục hồi IP và listener nhưng default route gốc là .30.2, host route runtime riêng qua .30.1 của phép thử trước không còn sau reboot. Không thay route trong lượt này. Khi M3.4B được giao, cần setup lại client và chiều về CARP cho session mới theo phương án đã duyệt; đó là chuẩn bị retest, không phải lỗi IP/OVS/pfsync baseline.

## 3.4.4. Ảnh console thực tế

'''
figs=[('core-public-proof','Core chỉ Layer2 và dịch vụ OVS active.','Xem địa chỉ và forwarding0/0; xác nhận không chuyển routing lên Core.'),('core-ovs-proof','Bảng access/trunk và flow NORMAL.','Đọc tag/trunks cùng flow chuyển mạch; đối chiếu ARP năm VLAN.'),('primary-carp-proof','Primary MASTER cả năm CARP.','Đọc IP .2, VIP .1 và VHID30/40/50/60/99; xác nhận vai trò chính.'),('secondary-carp-proof','Secondary BACKUP cả năm CARP.','Đọc IP .3, VIP .1 và skew100; xác nhận dự phòng.'),('primary-pfsync-proof','Pfsync và SYNC trên Primary.','Đọc syncok1/demotion0 và ping đối ứng; xác nhận readiness phía chính.'),('secondary-pfsync-proof','Pfsync và SYNC trên Secondary.','Đọc syncok1/demotion0 và ping đối ứng; đối chiếu hai phía.'),('endpoint-proof','Data-Center đã boot và listener hoạt động.','Đọc địa chỉ/route/service/ss; chỉ xác minh baseline, chưa HTTP request.')]
for i,(prefix,title,explanation) in enumerate(figs,1):
    matches=sorted(OUT.glob(prefix+'-2026*.png'));assert matches,'Missing figure '+prefix
    p=matches[-1];caption=f'Hình 3.{i}. {title}'
    report+=f'![{caption}]({p.name})\n\n{caption}\n\nMục đích, nội dung, kết quả và ý nghĩa: {explanation}\n\n'
report+='''## 3.4.5. Checkpoint và giới hạn

Giữ bốn node đang chạy; không có node không liên quan được bật. Không chạy lại client cũ, không phục hồi session đã mất, không thu state-table của bài test hoặc thực hiện failover. M3.4 chỉ READY_FOR_RETEST, M3.4B chưa chạy. Config hai firewall khớp hash trước gián đoạn; không áp lại native pfsync để đạt kết quả. VIP/VHID/advbase/advskew, Core, topology và IP plan giữ nguyên.

Các capture baseline-* đầu được thu trong lúc guest hoàn tất boot; đối chiếu nghiệm thu dùng final-baseline-* sau boot, kết hợp JSON runtime. Trường vip_conflict_seen trong collector ARP tái sử dụng chỉ nghĩa có trả lời VIP, không có nghĩa phát hiện xung đột trong lượt này. Ảnh cũ và bằng chứng lần test trước không bị chỉnh hoặc xóa; previous-evidence-integrity.json xác nhận checksum.

## 3.4.6. Danh mục minh chứng

| Tệp | Nội dung | Thời điểm thu (múi giờ) | Đường dẫn | Vị trí dự kiến trong báo cáo |
|---|---|---|---|---|
'''
for p in sorted(OUT.iterdir()):
    if not p.is_file() or p.suffix in ['.py','.txt'] or p.name in ['evidence-index.md','sha256-manifest.json']:continue
    when=dt.datetime.fromtimestamp(p.stat().st_mtime,dt.timezone(dt.timedelta(hours=7))).isoformat()
    desc='Ảnh console thật, nguyên nội dung' if p.suffix=='.png' else 'Runtime/metadata hoặc bản sao tài liệu; xem tên thành phần'
    if p.suffix=='.json':
        d=json.loads(p.read_text(encoding='utf-8'))
        if isinstance(d,dict):when=d.get('collector_time',d.get('collector_time_end',when))
    report+=f'| {p.name} | {desc} | {when} | docs/{rel}/{p.name} | M3.4A — thành phần tương ứng/phụ lục truy vết |\n'
(OUT/'evidence-index.md').write_text(report,encoding='utf-8')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='sha256-manifest.json'}
(OUT/'sha256-manifest.json').write_text(json.dumps({'collector_time':now,'sha256':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'M3.4':'READY_FOR_RETEST','core':'PASS','primary':'PASS','secondary':'PASS','carp':'MASTER/BACKUP 5 VLAN','pfsync':'READY both; syncok1/demotion0','endpoint':'PASS; no HTTP request','evidence':str(OUT)},ensure_ascii=True))
