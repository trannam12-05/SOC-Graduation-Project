"""Chỉ đọc trạng thái và cấu hình sensor không chứa bí mật để xuất minh chứng."""
from pathlib import Path
import subprocess,json
def cmd(args):
 p=subprocess.run(args,text=True,capture_output=True,timeout=15)
 return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
d={'result':json.loads(Path('/var/lib/soc/result.json').read_text()),
 'service':cmd(['systemctl','is-active','soc-suricata.service']),
 'packages':cmd(['dpkg-query','-W','suricata','tcpdump']),
 'interfaces':cmd(['ip','-j','address','show']),
 'unit':Path('/etc/systemd/system/soc-suricata.service').read_text(),
 'rules':Path('/etc/suricata/rules/soc-lab.rules').read_text(),
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'journal':cmd(['journalctl','-u','soc-suricata.service','--no-pager','-n','12']),
 'scope':'Configuration and live service state only; traffic detection and Wazuh delivery require separate tests'}
print(json.dumps(d))
