"""Ghi trích đọc từ ảnh nguyên bản; phân biệt với dữ liệu native từ guest."""
from pathlib import Path
import datetime,json
OUT=Path('D:/SOC/docs/evidence/M3/group1b-prerequisites-20261103')
d={'recorded_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
 'method':'Manual transcription verified against unmodified real console screenshots; not native JSON output',
 'Primary':{'UP':True,'syncdev':'vtnet2','syncpeer':'10.255.255.2','syncok':1,'carp_demotion':0,'state_image':'primary-pfsync-retry-stable-20261103T182701+0700.png','bulk_log_image':'primary-pfsync-bulk-log-20261103T182737+0700.png','bulk_done_observed':True,'bulk_fail_in_displayed_log':False,'kernel_bulk_start_uptime':8799,'kernel_bulk_done_uptime':9229},
 'Secondary':{'UP':True,'syncdev':'vtnet2','syncpeer':'10.255.255.1','syncok':1,'carp_demotion':0,'state_image':'secondary-pfsync-final-20261103T182701+0700.png','bulk_log_image':'secondary-pfsync-bulk-log-20261103T182737+0700.png','bulk_done_observed':True,'bulk_fail_in_displayed_log':False,'kernel_bulk_start_uptime':2414,'kernel_bulk_done_uptime':2419},
 'note':'Initial apply/readiness observations retained; Primary native reapply sequentially after peer stable; no manual syncok or demotion override; initial PCAP does not cover later retry'}
d['Primary']['config_sha256']='2a8dff44d86ee2971237c05fc94cec5e99ceccb642893f12474de6d8f54028a2'
d['Secondary']['config_sha256']='fd0482546117a18254e05114dc1b101012b95c1388e4ba9ea4eaafce115c69bd'
(OUT/'settled-verification.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'both_syncok_1':True,'both_demotion_0':True,'both_bulk_done':True}))
