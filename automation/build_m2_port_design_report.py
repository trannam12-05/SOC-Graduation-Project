"""Tạo báo cáo phiên bản mới và danh mục từ kiểm kê chỉ đọc; không tác động mạng."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from export_m2_report_docx import build

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT/'docs/M2'
EV = ROOT/'docs/evidence/M2/port-design-20261101T001402+0700'
OLD = DOCS/'M2-report-ovs-offline-installed-20261101.docx'
PRIOR_MAPPING = ROOT/'docs/evidence/M2/M2-ovs-verified-runtime-nic-mapping-20261101.csv'
NOW = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write_new(path,text):
    with path.open('x',encoding='utf-8',newline='\n') as f:f.write(text)

def main():
    inventory = json.loads((EV/'eve-inventory.json').read_text(encoding='utf-8'))
    windows = json.loads((EV/'windows-memory.json').read_text(encoding='utf-8'))
    lab = next(l for l in inventory['labs'] if l['path'].endswith('/SOC-M2-Core-L2.unl'))
    assert len(lab['nodes']) == 1 and not lab['networks']
    node = lab['nodes'][0]
    assert node['attributes']['id']=='3' and not node['interfaces']
    qemu = next(p for p in inventory['qemu_processes'] if node['attributes']['uuid'] in p['args'])
    assert len(inventory['qemu_processes'])==1
    links = json.loads(inventory['host_links']['stdout'])
    with PRIOR_MAPPING.open(encoding='utf-8-sig',newline='') as f:
        old_mapping = list(csv.DictReader(f))
    roles = ['Access Data Center VLAN 30','Access Employee VLAN 40','Access Guest VLAN 50',
             'Access DMZ VLAN 60','Access Management VLAN 99','Trunk OPNsense Primary LAN',
             'Trunk OPNsense Secondary LAN','Mirror output Suricata capture']
    rows = []
    for old,role in zip(old_mapping,roles):
        device = next(a for a in qemu['args'] if a.startswith('virtio-net-pci,netdev='+old['qemu_backend']+','))
        assert 'mac='+old['guest_mac'] in device
        backend = next(a for a in qemu['args'] if a.startswith('tap,id='+old['qemu_backend']+','))
        assert 'ifname='+old['eve_host_tap'] in backend
        assert not next(l for l in links if l['ifname']==old['eve_host_tap']).get('master')
        rows.append({**old,'peer_and_role':'Chưa nối peer','runtime_mapping_status':'Đã đối chiếu QEMU/TAP và ảnh guest mới theo MAC',
                     'proposed_role':role,'role_status':'Dự kiến; chưa cấu hình',
                     'eve_gui_port_label':'Chưa đọc nhãn GUI; không suy thành e0–e7',
                     'evidence':'eve-inventory.json; M2-port-guest-nics-20261101T001443+0700.png',
                     'collected_at':inventory['collector_time_end']})
    assert len(rows)==8 and len({r['guest_mac'] for r in rows})==8
    for dest in [EV/'M2-port-mapping-verified-and-proposed-20261101.csv',DOCS/'M2-port-mapping-verified-and-proposed-20261101.csv']:
        with dest.open('x',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    # Kiểm tra cuối chỉ đọc: lab và quan hệ bridge master của TAP vẫn giữ nguyên.
    remote = "import hashlib,json,subprocess; p='/opt/unetlab/labs/SOC-M2-Core-L2.unl'; print(json.dumps({'lab_sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'links':json.loads(subprocess.check_output(['ip','-j','link','show']))}))"
    ssh=['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-i',str(Path.home()/'.ssh/eve-ng-root-ed25519'),'root@192.168.220.143','python3','-']
    result=subprocess.run(ssh,input=remote,capture_output=True,text=True,timeout=25)
    assert result.returncode==0,result.stderr
    after=json.loads(result.stdout)
    assert after['lab_sha256']==lab['sha256']
    assert all(not next(l for l in after['links'] if l['ifname']==r['eve_host_tap']).get('master') for r in rows)
    after['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    write_new(EV/'final-readonly-check.json',json.dumps(after,ensure_ascii=False,indent=2))
    # Bảo toàn nguồn DOCX/Markdown, sau đó xuất phiên bản báo cáo khác tên.
    original_hash=sha(OLD)
    prior_md=OLD.with_suffix('.md')
    backup=DOCS/'backups/M2-before-port-design-20261101'
    backup.mkdir(parents=True,exist_ok=False)
    for p in [OLD,prior_md]:
        shutil.copy2(p,backup/p.name)
        assert sha(p)==sha(backup/p.name)
    appendix=(DOCS/'M2-port-design-appendix-20261101.md').read_text(encoding='utf-8')
    target=DOCS/'M2-report-port-mapping-and-ovs-design-20261101.md'
    write_new(target,'> Cập nhật thiết kế cổng M2 ngày 01/11/2026: mục 2.21–2.27 chứa mapping xác minh mới và cấu hình dự kiến CHƯA THỰC THI. Các phần trước giữ nguyên lịch sử.\n\n'+prior_md.read_text(encoding='utf-8')+'\n\n'+appendix)
    build(target)
    docx=target.with_suffix('.docx')
    with zipfile.ZipFile(docx) as archive:
        assert archive.testzip() is None
        for name in archive.namelist():
            if name.endswith('.xml'):ET.fromstring(archive.read(name))
        document=archive.read('word/document.xml').decode()
        styles=archive.read('word/styles.xml').decode()
        assert all(v in document for v in ['11906','16838','1701','1134'])
        assert 'Times New Roman' in styles and 'w:val="26"' in styles and 'w:val="24"' in styles
        embedded=[archive.read(n) for n in archive.namelist() if n.startswith('word/media/')]
        assert len(embedded)==14
        for p in EV.glob('M2-port-guest-nics*.png'):
            assert p.read_bytes() in embedded
        for p in EV.glob('M2-port-l2-baseline*.png'):
            assert p.read_bytes() in embedded
    assert sha(OLD)==original_hash
    validation={'collected_at':NOW,'old_docx_unchanged_sha256':original_hash,'new_docx_sha256':sha(docx),
        'verified_nic_rows':8,'duplicate_macs':0,'core_lab_node_count':1,'core_lab_network_count':0,
        'tap_master_count':0,'core_running_qemu_pid':qemu['pid'],
        'guest_console_observation':{'ipv4_forwarding':0,'ipv6_forwarding':0,'physical_nics_have_addresses':False,
          'ovs_bridges_listed':0,'ovs_mirrors_listed':0,
          'basis':'Actual framebuffer M2-port-l2-baseline; manually read, not shell output inferred from proposal'},
        'windows_free_GiB':windows['FreePhysicalMemoryKiB']/1024/1024,
        'eve_memavailable_MiB':int(re.search(r'^MemAvailable:\s+(\d+)',inventory['meminfo'],re.M).group(1))/1024,
        'network_changes_executed':False,'bridge_or_vlan_created':False,'additional_vm_started':False,
        'docx_checks':'ZIP/XML, 14 embedded image bytes, A4, 3/2/2/2 cm, TNR 12–13; no GUI pagination review',
        'guest_mac_verification':'Eight MACs manually matched current console to old CSV and current QEMU device/netdev arguments',
        'proposed_config_executed':False,'tests':'T00 baseline observed; T01–T15 not executed'}
    write_new(EV/'design-validation.json',json.dumps(validation,ensure_ascii=False,indent=2))
    # Inventory còn ghi cả trạng thái Linux host; không nhầm TAP MAC với guest MAC.
    note='''# Nhật ký xác minh thiết kế cổng M2

Phạm vi: chỉ đọc EVE/QEMU/TAP/tài nguyên và console guest; chỉ ghi tài liệu trên Windows.
Lệnh host: đọc XML lab, /proc/*/cmdline, /proc/meminfo/status/loadavg; ip -j link;
free -m; lscpu; vmstat 1 3; df -h; timedatectl; stat binary VPCS; liệt kê tên/kích thước image.
Lệnh guest đã gửi: ip -br link; ip -br addr; sysctl net.ipv4.ip_forward
net.ipv6.conf.all.forwarding; sudo -n ovs-vsctl list-br; sudo -n ovs-vsctl list Mirror.
Không có lệnh add-br/add-port/set Port/create Mirror/ip link set/sysctl -w hoặc start/stop.
Kết quả: tám MAC khớp; tám TAP chưa bridge master; lab một node/không network;
guest forwarding=0/0, chưa IP trên vNIC, chưa bridge/mirror. Số liệu RAM đọc tại thời điểm inventory.
Cấu hình 8 vai trò và giao dịch OVS chỉ là dự kiến trong docs/M2; T01–T15 chưa chạy.
Ảnh topology GUI chưa có; hướng dẫn chụp thủ công nằm ở mục 2.27.
'''
    write_new(EV/'execution-readonly.log','Collector: '+NOW+' UTC+07:00\n'+note)
    items=[]
    for path in sorted(EV.iterdir()):
        if not path.is_file():continue
        clock=inventory['collector_time_start']+' → '+inventory['collector_time_end']
        content='Kiểm kê chỉ đọc và dữ liệu thô'
        if path.suffix=='.png':
            meta=json.loads(path.with_suffix('.json').read_text())
            clock=meta['collector_time_start']+' → '+meta['collector_time_end']
            content='Ảnh console QEMU thật, nguyên byte; không sửa nội dung'
        if path.name=='windows-memory.json':clock=windows['CollectedAt'];content='RAM Windows và CPU logic tại thời điểm đo'
        if 'mapping' in path.name:content='Mapping đã xác minh, cột vai trò dự kiến và peer chưa nối'
        if path.name in ['design-validation.json','execution-readonly.log']:clock=NOW
        items.append([path.name,content,clock,str(path.relative_to(ROOT)),'2.21, 2.24, 2.27',sha(path)])
    for path in [docx,target,DOCS/'M2-port-design-appendix-20261101.md',DOCS/'M2-ovs-config-PROPOSED-20261101.txt',DOCS/'M2-port-topology-PROPOSED-20261101.mmd']:
        items.append([path.name,'Tài liệu thiết kế; không phải cấu hình thực tế',NOW,str(path.relative_to(ROOT)),'2.21–2.27',sha(path)])
    index=EV/'evidence-index.csv'
    with index.open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['ten_tep','noi_dung','thoi_diem_UTC+0700','duong_dan','vi_tri_bao_cao','sha256']);writer.writerows(items)
    text='# Danh mục minh chứng xác minh cổng và thiết kế M2\n\nThời điểm lập: '+NOW+' (UTC+07:00).\n\n'
    text+='| Tệp | Nội dung | Thời điểm/múi giờ | Đường dẫn | Vị trí báo cáo |\n|---|---|---|---|---|\n'
    text+='\n'.join('| '+' | '.join(row[:5])+' |' for row in items)
    text+='\n\nĐạt: mapping runtime tám MAC và kiểm kê topology hiện tại. Chưa triển khai/kiểm thử: mọi vai trò VLAN, trunk, bridge, mirror, peer và HA. Ảnh GUI topology chưa chụp; không có kết quả giả.\n'
    write_new(EV/'evidence-index.md',text)
    write_new(EV/'SHA256SUMS.txt','\n'.join(sha(p)+'  '+str(p.relative_to(ROOT)).replace('\\','/') for p in sorted(EV.iterdir()) if p.is_file())+'\n')
    assert all(sha(ROOT/row[3])==row[5] for row in items)
    print(json.dumps({'report':str(docx),'mapping':str(DOCS/'M2-port-mapping-verified-and-proposed-20261101.csv'),
       'evidence':str(EV/'evidence-index.md'),'nic_rows':8,'embedded_images':len(embedded),
       'old_report_preserved':True,'network_changes':False},ensure_ascii=False))

if __name__=='__main__':main()
