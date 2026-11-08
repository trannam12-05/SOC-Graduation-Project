"""Chuẩn bị payload CARP; không thực thi guest. Chỉ được chạy apply sau M3.1 PASS."""
from m3_todo_console import OUT,pycmd
php=(OUT/'apply-carp.php').read_text(encoding='utf-8')
source='''import pathlib,subprocess,json,os
os.umask(0o077)
p=pathlib.Path('/var/tmp/soc-m3-todo-carp.php');p.write_text(__PHP__,encoding='utf-8');p.chmod(0o600)
syntax=subprocess.run(['php','-l',str(p)],capture_output=True,text=True,timeout=10)
assert syntax.returncode==0,'PHP syntax check failed'
q=subprocess.run(['php',str(p)],capture_output=True,text=True,timeout=30)
assert q.returncode==0,'Save failed; inspect checkpoint before retry'
saved=json.loads(q.stdout);assert saved['status']=='SAVED' and saved['protected_sections_unchanged']
native=subprocess.run(['/usr/local/sbin/configctl','interface','vip','configure'],capture_output=True,text=True,timeout=60)
filter_reload=subprocess.run(['/usr/local/sbin/configctl','filter','reload'],capture_output=True,text=True,timeout=60)
d={'model_save':saved,'vip_native':{'rc':native.returncode,'stdout':native.stdout,'stderr':native.stderr},'filter_reload':{'rc':filter_reload.returncode,'stdout':filter_reload.stdout,'stderr':filter_reload.stderr},'config_sha256_after':__import__('hashlib').sha256(pathlib.Path('/conf/config.xml').read_bytes()).hexdigest()}
'''.replace('__PHP__',repr(php))
(OUT/'apply-carp-guest.py').write_text(source,encoding='utf-8')
print('Prepared only; compressed command characters:',len(pycmd(source)))
