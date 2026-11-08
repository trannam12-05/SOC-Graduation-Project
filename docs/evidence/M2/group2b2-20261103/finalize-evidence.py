"""Tạo bảng và kiểm tra cục bộ từ dữ liệu đã thu, không thao tác thiết bị."""
from pathlib import Path
import csv, datetime, hashlib, json, re
out=Path(__file__).resolve().parent
root=Path('D:/SOC')
d=json.loads((out/'firewall-current-public.json').read_text(encoding='utf-8'))
lines=[s for s in d['pf_rules_verbose']['stdout'].splitlines() if s.startswith('@')]
assert d['config_unchanged'] and d['config_sha256_before']==d['config_sha256_after']
assert len(d['modern_rules'])==7 and not d['legacy_rules']
assert all(x['interface']!='opt1' for x in d['modern_rules'])
for x in d['modern_rules']:
    x['pf_positions']=', '.join(re.match(r'@\d+',s).group() for s in lines if x['uuid'] in s)
    assert x['pf_positions']
keys=['pf_positions','sequence','uuid','enabled','interface','direction','ipprotocol','protocol','source_net','source_not','source_port','destination_net','destination_not','destination_port','action','log','quick','statetype','nosync','description']
with (out/'configured-firewall-rules.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader()
    w.writerows(sorted(d['modern_rules'],key=lambda x:int(x['pf_positions'].split(',')[0][1:])))
with (out/'running-pf-rules.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Thứ tự xuất','Chỉ số PF','Loại','Dòng rule đầy đủ'])
    for i,line in enumerate(lines,1):w.writerow([i,re.match(r'@\d+',line).group(),'scrub' if ' scrub ' in line else 'filter',line])
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
checks={'checked_at':now,'config_hash_equal':True,'modern_count':7,'legacy_count':0,'configured_vlan30_count':0,'all_configured_UUIDs_present_in_PF':True,'PF_command_rcs':{k:d[k]['rc'] for k in ['pf_rules_verbose','pf_anchor_filter_rules','pf_tables_names_only']},'traffic_tested':False,'rules_changed':0,'authentication_changed':False,'PF_filter_count':sum(' scrub ' not in x for x in lines),'PF_scrub_count':sum(' scrub ' in x for x in lines),'source_public_sha256':hashlib.sha256((out/'firewall-current-public.json').read_bytes()).hexdigest()}
assert all(v==0 for v in checks['PF_command_rcs'].values())
assert not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',json.dumps(d))
(out/'delivery-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
old=out/'M2-group2b2-report.md'
notice='> Checkpoint lịch sử trước khi mở Shell. Kết quả cuối đã thu thành công: [M2-group2b2-firewall-results.md](M2-group2b2-firewall-results.md). Nội dung cũ được giữ nguyên bên dưới.\n\n'
if not old.read_text(encoding='utf-8').startswith('> Checkpoint'):
    old.write_text(notice+old.read_text(encoding='utf-8'),encoding='utf-8')
with (out/'evidence-index-final.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Tên tệp','Nội dung','Thời điểm thu thập/tạo UTC+07:00','Đường dẫn','Vị trí dự kiến trong báo cáo','SHA256'])
    for p in sorted(out.rglob('*')):
        if not p.is_file() or p.name=='evidence-index-final.csv' or '__pycache__' in p.parts:continue
        ts=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone(datetime.timedelta(hours=7))).isoformat()
        if p.suffix=='.json':
            j=json.loads(p.read_text(encoding='utf-8'));ts=j.get('collector_time_end',j.get('collector_time',j.get('collected_at',j.get('checked_at',ts))))
        elif p.suffix=='.png' and p.with_suffix('.json').exists():
            j=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'));ts=j.get('collector_time_end',ts)
        desc='Ảnh console thật, nguyên bản' if p.suffix=='.png' else 'Dữ liệu công khai đã xác minh' if p.name=='firewall-current-public.json' else 'Báo cáo/bảng/log/mã thu; đọc kèm giới hạn trong báo cáo kết quả'
        w.writerow([p.name,desc,ts,str(p.relative_to(root)).replace('\\','/'),'Chương 2 / M2 Nhóm 2B.2',hashlib.sha256(p.read_bytes()).hexdigest()])
print(json.dumps(checks,ensure_ascii=False))
