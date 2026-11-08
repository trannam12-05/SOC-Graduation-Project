"""Tổng hợp minh chứng thật và báo cáo M2; không thao tác thiết bị."""
from pathlib import Path
import csv,datetime,hashlib,json,struct,xml.etree.ElementTree as E,zipfile
from export_m2_report_docx import build
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/evidence/M2/final-acceptance-20261103'
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat()
analysis=json.loads((OUT/'packet-analysis.json').read_text(encoding='utf-8'))
cleanup=json.loads((OUT/'cleanup-receipt.json').read_text(encoding='utf-8'))
guest=json.loads((OUT/'packet-collect-result.json').read_text(encoding='utf-8'))['results'][-1]
old=ROOT/'docs/evidence/M2/live-tests-20261101/final-collection/frame-cases.csv'
history=list(csv.DictReader(old.open(encoding='utf-8-sig')))
assert len(history)==95 and all(x['status']=='PASS' for x in history)
assert all(analysis[k] for k in ['Inter_VLAN_PASS','ACL_negative_PASS','SPAN_PASS','access_trunk_live_PASS'])
assert cleanup['lab_restored_byte_exact'] and cleanup['DC_stopped_verified']
assert {r['name'] for r in cleanup['running']}=={'SOC-Core-L2','OPNsense-Primary'}
assert cleanup['eve_memory']['SwapFree']==cleanup['eve_memory']['SwapTotal']

observations={'recorded_at':NOW,'method':'Trích đọc có đối chiếu từ ảnh console gốc, không phải JSON native pfctl/OVS',
 'config_sha256_before':'2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2',
 'config_sha256_after':'2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2',
 'before_image':'primary-rule-before-tests-20261103T171719+0700.png','after_image':'primary-rule-after-tests-20261103T171843+0700.png',
 'default_deny_ipv4':{'PF_index':10,'before_packets':0,'after_packets':12,'after_bytes':720},
 'HTTP_allow':{'PF_index':96,'UUID':'684c6853-1caa-4a3c-9433-b48f01624c84','before_packets':0,'after_packets':10,'after_bytes':1005,'state_creations':1},
 'mirror':{'before_image':'core-mirror-runtime-20261103T171747+0700.png','after_image':'core-mirror-after-tests-20261103T171916+0700.png','before_packets':0,'after_packets':48,'after_bytes':4278},
 'core':{'source_image':'core-runtime-root-20261103T171628+0700.png','ipv4_forwarding':0,'ipv6_forwarding':0,'non_loopback_IPs':[]}}
(OUT/'firewall-counter-observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2),encoding='utf-8')
pos=guest['cases'][0]['observed']
(OUT/'http-response-body.html').write_text(pos['body_text'],encoding='utf-8')
(OUT/'http-response-headers.txt').write_text('HTTP 200 OK\n'+'\n'.join(k+': '+v for k,v in pos['headers'])+'\n',encoding='utf-8')
assert hashlib.sha256((OUT/'http-response-body.html').read_bytes()).hexdigest()==pos['body_sha256']
cases=[{'id':'M2-P01','status':'PASS','scope':'HTTP đúng nguồn .40.100 → .30.10 TCP8000'},
       {'id':'M2-N01','status':'PASS','scope':'Sai nguồn .40.101 bị default deny'},
       {'id':'M2-N02','status':'PASS','scope':'Kết nối mới .30.10 → .40.100 TCP8001 bị default deny; có dịch vụ đối chứng'}]
items=[('Core L2','PASS','95/95 ca lịch sử + ảnh runtime L2 mới'),('Inter-VLAN Routing','PASS','HTTP200 + VLAN40→30, TTL64→63, MAC Primary'),('ACL/firewall giữa VLAN','PASS','Một ca dương/hai ca âm + PCAP + counter'),('Access/trunk','PASS','Suite năm VLAN lịch sử + PCAP mới access/trunk'),('LACP','N/A','Hai trunk tới hai firewall riêng, không LAG chung'),('SPAN/Port Mirroring','PASS','PCAP mirror có marker GET + counter tăng')]
result={'collected_at':NOW,'milestone':'M2','state':'COMPLETE','items':[{'item':a,'status':b,'evidence':c} for a,b,c in items],
 'application_cases':cases,'historical_frame_tests':{'total':95,'PASS':95,'FAIL':0,'source':str(old.relative_to(ROOT))},
 'new_application_tests':{'total':3,'PASS':3,'FAIL':0},'scope_limit':'Không nghiệm thu mọi cặp VLAN/port/IPv6, HA/CARP/NAT/DHCP hoặc SOC pipeline từ ba ca HTTP',
 'firewall_rules_changed':0,'core_configuration_changed':False,'temporary_client':'Linux namespace m2-client40 in DC, second NIC on existing VLAN40; removed after tests',
 'final_nodes':cleanup['running'],'temporary_topology_restored':True,'moved_to_M3':False,'git_commit_or_push':False}
(OUT/'M2-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'M2-results.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Hạng mục','Trạng thái','Căn cứ']);w.writerows(items)

def prepend(path,text):
 old=path.read_text(encoding='utf-8-sig')
 if not old.startswith(text.splitlines()[0]):path.write_text(text+'\n\n'+old,encoding='utf-8')
prepend(ROOT/'README.md','''# M2 đã hoàn thành — 03/11/2026, UTC+07:00

Core L2, Inter-VLAN HTTP200 qua Primary, firewall ca dương/hai ca âm, access/trunk và SPAN đều PASS; LACP N/A theo kiến trúc hai trunk tới hai firewall riêng. [Tổng kết M2](docs/M2/M2-final-summary-20261103.md), [Word](docs/M2/M2-final-summary-20261103.docx), [SOC TO DO](docs/SOC_TO_DO.md), [evidence index](docs/evidence/M2/final-acceptance-20261103/evidence-index.csv). Core/Primary giữ chạy, DC tắt mềm, client/NIC tạm đã gỡ và lab phục hồi nguyên byte. Không chuyển M3. Các mốc cũ bên dưới giữ làm lịch sử.''')
prepend(ROOT/'docs/PROGRESS.md','''# M2 hoàn thành — 03/11/2026, UTC+07:00

Core L2 PASS; Inter-VLAN PASS bằng HTTP200 .40.100 → .30.10:8000 và PCAP tag40→30/TTL64→63/MAC Primary; firewall PASS một ca dương/hai ca âm đối chiếu PCAP/counter; access/trunk PASS; SPAN PASS; LACP N/A. Không sửa rule hoặc Core/NAT/DHCP/CARP/HA. Client namespace có NIC tạm VLAN40 trong DC, giữ đúng IP ngoại lệ; sau thử DC tắt mềm, NIC tạm gỡ, lab phục hồi nguyên byte. Core + Primary giữ chạy. [Báo cáo cuối](M2/M2-final-summary-20261103.md), [SOC TO DO](SOC_TO_DO.md), [evidence index](evidence/M2/final-acceptance-20261103/evidence-index.csv). Không chuyển M3.

Các checkpoint bên dưới giữ làm lịch sử; kết quả NOT_RUN/chưa PASS trước đó đã được cập nhật bằng mốc này, không xóa minh chứng.''')
prepend(ROOT/'docs/AUTONOMOUS_PROGRESS.md','''# M2 đã nghiệm thu — 03/11/2026, UTC+07:00

Mốc mới nhất: [tổng kết M2](M2/M2-final-summary-20261103.md), [SOC TO DO](SOC_TO_DO.md). Sáu hạng mục có bảng PASS/N/A; ba ca HTTP dương/âm có PCAP/counter. Core + Primary giữ chạy; DC tắt mềm; NIC/namespace client tạm đã gỡ. Không chuyển M3. Phần dưới là nhật ký lịch sử, giữ nguyên nội dung cũ.''')

report=ROOT/'docs/M2/M2-final-summary-20261103.md'
target=report.with_suffix('.docx')
if not target.exists():build(report)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 doc=E.fromstring(z.read('word/document.xml'));sty=E.fromstring(z.read('word/styles.xml'))
 page=doc.find('.//w:pgSz',ns);marg=doc.find('.//w:pgMar',ns)
 W='{'+ns['w']+'}'
 assert page.get(W+'w')=='11906' and page.get(W+'h')=='16838'
 assert marg.get(W+'left')=='1701' and all(marg.get(W+k)=='1134' for k in ['right','top','bottom'])
 assert sty.find('.//w:rFonts',ns).get(W+'ascii')=='Times New Roman'
 imgs=[x for x in z.namelist() if x.startswith('word/media/')]
 assert len(imgs)==6
 source_images=['core-runtime-root-20261103T171628+0700.png','endpoint-ip-mask-gateway-20261103T172108+0700.png','dc-http-results-summary-20261103T171916+0700.png','primary-rule-before-tests-20261103T171719+0700.png','primary-rule-after-tests-20261103T171843+0700.png','core-mirror-after-tests-20261103T171916+0700.png']
 for embedded,src in zip(imgs,source_images):assert z.read(embedded)==(OUT/src).read_bytes()
references=[old,ROOT/'docs/evidence/M2/group2b2-20261103/firewall-current-public.json',ROOT/'docs/evidence/M2/group2b2-20261103/configured-firewall-rules.csv']
(OUT/'source-manifest.json').write_text(json.dumps({'reviewed_at':NOW,'sources':[{'path':str(x.relative_to(ROOT)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in references]},indent=2),encoding='utf-8')
checks={'checked_at':NOW,'required_items':{a:b for a,b,c in items},'application_cases_PASS':3,'historical_frame_PASS':95,
 'pcap_routing_negative_and_mirror_checks':True,'HTTP_body_hash_matches':True,'temporary_topology_restored_byte_exact':True,'only_Core_and_Primary_running':True,
 'DOCX_package_valid':True,'DOCX_A4_TimesNewRoman_margins_valid':True,'DOCX_six_embedded_images_byte_equal_originals':True,'DOCX_visual_pagination_reviewed':False,
 'firewall_config_hash_equal_from_screenshots':True,'no_M3_work':True}
(OUT/'delivery-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')

extras=[report,target,ROOT/'docs/SOC_TO_DO.md',ROOT/'README.md',ROOT/'docs/PROGRESS.md',ROOT/'docs/AUTONOMOUS_PROGRESS.md']+references
for name in ['m2_acceptance_prepare.py','m2_dc_acceptance_guest.py','m2_guest_console_stage.py','m2_packet_capture.py','m2_analyze_packets.py','m2_acceptance_cleanup.py','m2_finalize_delivery.py']:extras.append(ROOT/'automation'/name)
files=sorted(set([p for p in OUT.rglob('*') if p.is_file() and p.name!='evidence-index.csv' and '__pycache__' not in p.parts]+extras))
with (OUT/'evidence-index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Tên ảnh/tệp','Nội dung','Thời điểm thu thập/tạo kèm múi giờ','Đường dẫn','Vị trí dự kiến trong báo cáo','SHA-256'])
 for p in files:
  ts=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone(datetime.timedelta(hours=7))).isoformat()
  if p.suffix=='.json':
   j=json.loads(p.read_text(encoding='utf-8-sig'));ts=j.get('collector_time_end',j.get('collector_time',j.get('collected_at',j.get('checked_at',ts))))
  elif p.suffix=='.png' and p.with_suffix('.json').exists():ts=json.loads(p.with_suffix('.json').read_text(encoding='utf-8'))['collector_time_end']
  if p.suffix=='.pcap':
   ts=json.loads((OUT/'packet-stop.json').read_text())['collector_time'];desc='PCAP thật TCP lab; timestamp packet theo host chưa đồng bộ, dùng mốc thu UTC+07:00'
  elif p.suffix=='.png':desc='Framebuffer console thật, không chỉnh nội dung'
  elif p==old:desc='Suite lịch sử 95/95 frame PASS; tái sử dụng, không chạy lại'
  elif p.suffix=='.py':desc='Mã thu/phân tích/tổng hợp; không tự xem mã là kết quả PASS'
  elif p.suffix=='.unl':desc='Topology đợt test với NIC client tạm, đã được phục hồi sau thử'
  else:desc='Kết quả/cấu hình công khai/báo cáo; đọc giới hạn và phương pháp trong báo cáo M2'
  section='Chương 2 / phụ lục minh chứng'
  if p.name in source_images:section='Chương 2 / Hình 2.'+str(source_images.index(p.name)+1)
  w.writerow([p.name,desc,ts,str(p.relative_to(ROOT)).replace('\\','/'),section,hashlib.sha256(p.read_bytes()).hexdigest()])
print(json.dumps({'state':'M2_COMPLETE','items':result['items'],'evidence_entries':len(files),'report':str(report),'word':str(target),'checks':checks},ensure_ascii=False))
