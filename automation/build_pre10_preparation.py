"""Sequential local document/static review only; never uses SSH, VM or packet sockets."""
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile
from export_m2_report_docx import build

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/preparation/pre10-20261101'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def review(p):
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None
        d=ET.fromstring(z.read('word/document.xml'))
        styles=z.read('word/styles.xml')
        pg=d.find('.//w:pgSz',NS);mar=d.find('.//w:pgMar',NS)
        w='{'+NS['w']+'}'
        return {'file':str(p.relative_to(ROOT)),'sha256':sha(p),'zip_xml_readable':True,
                'a4':pg is not None and pg.get(w+'w')=='11906' and pg.get(w+'h')=='16838',
                'margins_3_2_2_2_cm':mar is not None and mar.get(w+'left')=='1701' and all(mar.get(w+x)=='1134' for x in ['top','right','bottom']),
                'times_new_roman_in_styles':b'Times New Roman' in styles,
                'embedded_images':len([n for n in z.namelist() if n.startswith('word/media/')]),
                'gui_pagination_reviewed':False}


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    before={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'docs/M2').glob('*.docx')}
    sys.path.insert(0,str(ROOT/'tests'))
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_m2_preparation.py')
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (OUT/'static-tests.log').write_text(stream.getvalue(),encoding='utf-8')
    assert result.wasSuccessful()
    old=ROOT/'docs/M2/M2-report-consolidated-review-20261101.md'
    target=ROOT/'docs/M2/M2-report-execution-ready-PREPARED-20261101.md'
    supplement=(ROOT/'docs/M2/M2-sequential-runbook-PREPARED-20261101.md').read_text(encoding='utf-8')
    supplement=supplement[supplement.index('## 2.1.'):]
    for n in range(7,0,-1):supplement=supplement.replace('## 2.'+str(n)+'.','## 2.'+str(n+12)+'.')
    content=old.read_text(encoding='utf-8')+'\n\n'+supplement
    content=content.replace('TPID và TCI; phần VID nhận dạng VLAN','TPID (Tag Protocol Identifier) và TCI (Tag Control Information); phần VID (VLAN Identifier) nhận dạng VLAN')
    content+='\n\nKiểm tra cục bộ mới: '+str(result.testsRun)+' mock/static test đạt trong phiên soạn; không SSH, không VM và không xác nhận PASS chức năng mạng. Xem docs/preparation/pre10-20261101/static-review.json.\n'
    with target.open('x',encoding='utf-8',newline='\n') as f:f.write(content)
    build(target)
    reviews=[review(p) for p in (ROOT/'docs/M2').glob('*.docx')]
    latest=next(r for r in reviews if r['file']==str(target.with_suffix('.docx').relative_to(ROOT)))
    assert latest['a4'] and latest['margins_3_2_2_2_cm'] and latest['times_new_roman_in_styles'] and latest['embedded_images']==12
    with zipfile.ZipFile(old.with_suffix('.docx')) as a,zipfile.ZipFile(target.with_suffix('.docx')) as b:
        ha=sorted(hashlib.sha256(a.read(n)).hexdigest() for n in a.namelist() if n.startswith('word/media/'))
        hb=sorted(hashlib.sha256(b.read(n)).hexdigest() for n in b.namelist() if n.startswith('word/media/'))
        assert ha==hb
    assert all(sha(ROOT/p)==h for p,h in before.items())
    (OUT/'docx-review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    receipt={'collector_time':dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(),
             'scope':'LOCAL_STATIC_AND_MOCK_ONLY_NOT_NETWORK_ACCEPTANCE','tests_run':result.testsRun,
             'errors':len(result.errors),'failures':len(result.failures),'vm_started':False,'network_frame_sent':False,
             'ssh_to_eve_used':False,'qcow2_accessed':False,'new_screenshots_or_pcap_created':False,
             'old_reports_unchanged':True,'new_docx_images_exactly_match_prior':True,
             'runtime_limitations':['New console/queue/persistence paths not yet tested on running guest','Requires actual console login and sudo access','VLAN/mirror/reboot/HA/IDS NOT RUN']}
    (OUT/'static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    files=[target,target.with_suffix('.docx'),OUT/'static-tests.log',OUT/'docx-review.json',OUT/'static-review.json']
    (OUT/'SHA256SUMS.txt').write_text('\n'.join(sha(p)+'  '+p.relative_to(ROOT).as_posix() for p in files)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':main()
