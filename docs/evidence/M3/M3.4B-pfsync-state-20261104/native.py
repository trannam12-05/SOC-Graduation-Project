"""Read-only PF/CARP snapshots; watcher hữu hạn, không sửa state/rule/CARP."""
import os,pathlib,subprocess,json,re,time,sys,xml.etree.ElementTree as E
P=pathlib.Path('/root/soc-m34b-20261104')
def cmd(a):
 q=subprocess.run(a,text=True,capture_output=True,timeout=10);return dict(rc=q.returncode,out=q.stdout,err=q.stderr)
def carp():
 rows=[]
 for v in [30,40,50,60,99]:
  q=cmd(['ifconfig','vtnet0_vlan'+str(v)]);s=q['out'];rows.append(dict(vlan=v,rc=q['rc'],state=re.findall(r'carp: (\w+)',s),vip_ok=('inet 192.168.%d.1 netmask 0xffffff00'%v) in s,carp=[l.strip() for l in s.splitlines() if 'carp:' in l]))
 return rows
def capture(rows=None):
 begin=time.monotonic();q=cmd(['pfctl','-ss','-vv']);lines=q['out'].splitlines();blocks=[]
 for i,line in enumerate(lines):
  if '192.168.40.100:44341' not in line or '192.168.30.10:8000' not in line:continue
  b=[line]
  for following in lines[i+1:]:
   if following and not following[0].isspace():break
   b.append(following)
  text='\n'.join(b);m=re.search(r'id:\s*(\S+)\s+creatorid:\s*(\S+)',text)
  blocks.append(dict(text=text,id=m.group(1) if m else None,creatorid=m.group(2) if m else None,established='ESTABLISHED:ESTABLISHED' in text))
 return dict(flow='192.168.40.100:44341 -> 192.168.30.10:8000',pfctl_rc=q['rc'],blocks=blocks,carp_all=carp() if rows is None else rows,native_capture_started_monotonic=begin,native_capture_finished_monotonic=time.monotonic(),guest_wall_clock_untrusted=time.time(),local_sync_ip=E.parse('/conf/config.xml').getroot().findtext('interfaces/opt6/ipaddr'))
def save(name,d):
 os.umask(0o077)
 tmp=P/(name+'.pending')
 with tmp.open('x') as f:json.dump(d,f,separators=(',',':'));f.flush();os.fsync(f.fileno())
 assert not (P/name).exists();os.replace(tmp,P/name)
 fd=os.open(str(P),os.O_RDONLY);os.fsync(fd);os.close(fd)
def watch():
 started=time.monotonic();initial=carp()
 assert E.parse('/conf/config.xml').getroot().findtext('interfaces/opt6/ipaddr')=='10.255.255.2'
 assert all(r['state']==['BACKUP'] for r in initial),'Secondary must start BACKUP'
 save('watcher-ready.json',dict(pid=os.getpid(),armed_monotonic=started,guest_wall_clock_untrusted=time.time(),initial_carp=initial,deadline_seconds=300))
 while time.monotonic()-started<300:
  rows=carp()
  if all(r['state']==['MASTER'] for r in rows):
   observed=time.monotonic();d=capture(rows);d.update(trigger='all five CARP MASTER',master_observed_monotonic=observed,trigger_to_state_capture_seconds=d['native_capture_started_monotonic']-observed,elapsed_since_armed_seconds=observed-started)
   save('secondary-after-immediate.json',d);print('native_after_saved',flush=True);return
  time.sleep(0.25)
 save('watcher-timeout.json',dict(status='TIMEOUT',last_carp=rows,elapsed=time.monotonic()-started))
if __name__=='__main__' and sys.argv[-1]=='watch':watch()
