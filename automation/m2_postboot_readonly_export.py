"""Small read-only guest export using the previously retained verified M2 library.

Avoid re-transferring a large runtime helper when /tmp was cleaned. Does not
change OVS, links, addresses, units or forwarding; only writes a new public log.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys

SOURCE=Path('/root/m2-isolated-20261101T0035/guest.py')
EXPECTED='263c27f2b85f742fd15e8f9eef0c44831e52ae1bbf4a18234e7b7387985c9123'


def main():
    assert os.geteuid()==0 and __debug__
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED, 'Unexpected retained library; no fallback used'
    work=Path(sys.argv[-1]);assert work.parent==Path('/root') and work.name.startswith('m2-postboot-export-')
    work.mkdir(mode=0o700,exist_ok=False)
    spec=importlib.util.spec_from_file_location('retained_m2',SOURCE)
    g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);g.WORK=work
    with contextlib.redirect_stdout(io.StringIO()):
        state=g.state('postboot')
        state['mirrors']=g.table('Mirror','name,select_all,select_src_port,select_dst_port,select_vlan,output_port')
        state['noip_unit']=g.run(['systemctl','is-active','soc-core-l2-noip']).strip()
        state['noip_unit_enabled']=g.run(['systemctl','is-enabled','soc-core-l2-noip']).strip()
    state['boot_id']=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    (work/'postboot-complete.json').write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps({'action':'postboot-readonly-export','state':state,'commands_log':str(work/'commands.jsonl'),'traffic_tested_by_this_export':False}))


if __name__=='__main__':main()
