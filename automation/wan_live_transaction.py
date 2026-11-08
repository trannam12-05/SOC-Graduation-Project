"""Giao dịch chỉ hai TAP WAN, rollback tự động; không sửa cấu hình HA."""
import pathlib,json,subprocess,os,fcntl,hashlib,datetime,time,xml.etree.ElementTree as E,io,contextlib,base64,zlib,struct,tempfile,signal
bundle=json.loads(base64.b64decode(BUNDLE));mode=bundle['mode']
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl')
def sha(b):return hashlib.sha256(b).hexdigest()
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=12)
 if p.returncode:raise RuntimeError(str(a)+': '+p.stderr)
 return p.stdout
def master(tap):return pathlib.Path('/sys/class/net',tap,'master').resolve().name
def hoststate():
 a=json.loads(run(['ip','-j','-4','addr','show','pnet0']))
 addresses=[[x['local'],x['prefixlen']] for n in a for x in n.get('addr_info',[])]
 routes=json.loads(run(['ip','-j','-4','route','show','default']))
 return {'addresses':addresses,'routes':[[n.get('gateway'),n.get('dev')] for n in routes]}
def pids():
 out={}
 for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
  try:
   a=[s.decode(errors='replace') for s in p.read_bytes().split(b'\0') if s]
   if a and 'qemu-system-' in a[0]:out[a[a.index('-name')+1]]={'pid':p.parent.name,'args':a}
  except (OSError,ValueError):pass
 return out
def save(p,d):
 tmp=p.with_suffix('.new');tmp.write_text(json.dumps(d,indent=2));tmp.chmod(0o600);os.replace(tmp,p)
def rollback(work):
 state=json.loads((work/'state.json').read_text());events=[]
 for tap,old in state['masters'].items():
  current=master(tap)
  if current=='pnet0':run(['ip','link','set','dev',tap,'master',old]);events.append('restored '+tap)
  elif current!=old:events.append('CONFLICT '+tap+' current='+current)
 current=lab.read_bytes()
 if sha(current)==state['after_sha256']:
  tmp=lab.with_suffix('.rollback');tmp.write_bytes((work/'lab-before.unl').read_bytes());os.chown(tmp,*state['owner']);os.chmod(tmp,state['mode']);os.replace(tmp,lab);events.append('restored topology')
 elif sha(current)!=state['before_sha256']:events.append('CONFLICT topology; not overwritten')
 state['status']='ROLLED_BACK' if not any('CONFLICT' in s for s in events) else 'ROLLBACK_CONFLICT';state['rollback_events']=events;state['host_after']=hoststate();save(work/'state.json',state)
 return state
if mode=='watchdog':
 work=pathlib.Path(bundle['work'])
 while True:
  state=json.loads((work/'state.json').read_text())
  if state['status']!='ARMED':break
  if time.monotonic()>state['deadline']:
   rollback(work);break
  time.sleep(2)
 raise SystemExit()
cap=bundle['capture'].split("REMOTE = r'''",1)[1].split("'''",1)[0]
cap=cap.replace('key = ord(char)',"key = ord(shifted.get(char, char.lower() if char.isupper() else char))")
decoder={'__name__':'decoder'};exec(bundle['decoder'],decoder)
frames=[]
def frame(node,command,label,work,wait=3):
 code=cap.replace("n.get('name') == 'SOC-Core-L2'","n.get('name') == "+repr(node)).replace('__CHECK__','None').replace('__CUSTOM_COMMAND__',repr(command))
 code=code.replace('time.sleep(3)','time.sleep('+str(wait)+')')
 buf=io.StringIO()
 with contextlib.redirect_stdout(buf):exec(code,{})
 facts=json.loads(buf.getvalue());png=base64.b64decode(facts['capture'].pop('png_base64'))
 stem=label+'-'+str(len(frames));(work/(stem+'.png')).write_bytes(png);facts['capture']['sha256']=sha(png);save(work/(stem+'.json'),facts);frames.append(stem)
 return work/(stem+'.png')
def guard(node,label,work):
 image=frame(node,'python3 /var/tmp/soc-wan-guard.py',label,work)
 packet=base64.b64decode(decoder['decode'](image,1280),validate=True)
 length,digest=struct.unpack('>I32s',packet[:36]);assert 0<length<=924
 b=packet[36:36+length];assert sha(b)==digest.hex();return json.loads(zlib.decompress(b))
def valid(g):
 expected='MASTER' if g['role']=='Primary' else 'BACKUP'
 return g['syncok'] and g['demotion']=='0' and sorted(g['carp'])==sorted([[expected,str(v)] for v in [30,40,50,60,99]])
def export(work,result):
 files=[]
 for p in sorted(work.iterdir()):
  if p.suffix in ['.png','.json','.pcap','.txt','.log'] and p.name!='state.json':files.append({'name':p.name,'data':base64.b64encode(p.read_bytes()).decode()})
 files.append({'name':'state.json','data':base64.b64encode((work/'state.json').read_bytes()).decode()})
 print(json.dumps({'work':str(work),'result':result,'files':files}))
if mode=='https':
 work=pathlib.Path(bundle['work']);state=json.loads((work/'state.json').read_text());assert state['status']=='WAN_READY'
 assert not (work/'https-result.json').exists(),'HTTPS already attempted; do not repeat'
 checks={name:guard(name,name+'-pre-https',work) for name in state['baseline']}
 assert all(valid(g) and g['protected']==state['baseline'][name]['protected'] and g['hook']==state['baseline'][name]['hook'] and g['gateway']=='192.168.220.2' for name,g in checks.items())
 assert hoststate()==state['host_before'] and sha(lab.read_bytes())==state['after_sha256']
 root=E.fromstring(lab.read_bytes());primary=next(n for n in root.findall('.//node') if n.get('name')=='OPNsense-Primary');employee=next(n for n in root.findall('.//node') if n.get('name')=='Employee-Linux')
 captures=[]
 try:
  for label,tap in [('employee','vunl0_'+employee.get('id')+'_0'),('wan','vunl0_'+primary.get('id')+'_1')]:
   path=work/(label+'.pcap');log=open(work/(label+'-capture.log'),'w')
   p=subprocess.Popen(['tcpdump','-p','-U','-n','-i',tap,'-s','128','-c','80','-w',str(path),'tcp and host 1.1.1.1 and port 443'],stdout=log,stderr=log)
   captures.append((label,p,log,path))
  time.sleep(1)
  assert all(p.poll() is None for _,p,_,_ in captures),'Passive capture failed'
  picture=frame('Employee-Linux','python3 /var/tmp/soc-https-once.py','Employee-HTTPS-once',work,15)
  packet=base64.b64decode(decoder['decode'](picture,1280),validate=True);length,digest=struct.unpack('>I32s',packet[:36]);assert 0<length<=924
  b=packet[36:36+length];assert hashlib.sha256(b).digest()==digest;result=json.loads(zlib.decompress(b))
 except Exception as error:result={'status':'FAILED','error':str(error),'scope':'Do not repeat HTTPS; collect existing guest result'}
 finally:
  for label,p,log,path in captures:
   if p.poll() is None:p.send_signal(signal.SIGINT)
   try:p.wait(timeout=6)
   except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=3)
   log.close()
   if path.exists():
    text=run(['tcpdump','-nn','-tttt','-r',str(path)]);(work/(label+'-packets.txt')).write_text(text)
  save(work/'https-result.json',result)
 export(work,result);raise SystemExit()
if mode in ['inspect','rollback','guard']:
 work=pathlib.Path(bundle['work'])
 state=json.loads((work/'state.json').read_text())
 if mode=='guard':
  checks={name:guard(name,name+'-guard-'+str(int(time.time())),work) for name in state['baseline']}
  healthy=all(valid(g) and g['protected']==state['baseline'][name]['protected'] and g['hook']==state['baseline'][name]['hook'] for name,g in checks.items())
  healthy=healthy and hoststate()==state['host_before'] and sha(lab.read_bytes())==state['after_sha256']
  result={'status':'GUARD_PASS' if healthy else 'GUARD_FAILED','guards':checks,'host':hoststate(),'work':str(work)}
  save(work/('guard-result-'+str(int(time.time()))+'.json'),result)
 else:result=rollback(work) if mode=='rollback' else state
 export(work,result);raise SystemExit()
lock=open('/root/.soc-m3-wan.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
work=pathlib.Path('/root/soc-m3-wan-live-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));work.mkdir(mode=0o700)
raw=lab.read_bytes();root=E.fromstring(raw);beforehost=hoststate();assert ['192.168.220.143',24] in json.loads(json.dumps(beforehost['addresses']))
assert ['192.168.220.2','pnet0'] in beforehost['routes']
process=pids();masters={};nodes=[]
for name in ['OPNsense-Primary','OPNsense-Secondary']:
 n=next(n for n in root.findall('.//node') if n.get('name')==name);i=n.find("interface[@id='1']");assert i.get('name')=='vtnet1' and i.get('network_id')=='4'
 tap='vunl0_'+n.get('id')+'_1';assert tap in ' '.join(process[name]['args']);assert n.get('uuid') in process[name]['args'];assert master(tap)=='vnet0_4';masters[tap]=master(tap);nodes.append((name,n,i))
allmasters={p.name:master(p.name) for p in pathlib.Path('/sys/class/net').iterdir() if (p/'master').exists()}
baseline={name:guard(name,name+'-before',work) for name,_,_ in nodes};assert all(valid(g) for g in baseline.values()),'Baseline HA not ready; no mutation'
(work/'lab-before.unl').write_bytes(raw);(work/'lab-before.unl').chmod(0o600)
if mode=='preflight':
 state={'status':'BASELINE_READY','work':str(work),'before_sha256':sha(raw),'masters':masters,'host_before':beforehost,'baseline':baseline}
 save(work/'state.json',state);export(work,state);raise SystemExit()
networkid=str(max(int(n.get('id')) for n in root.findall('.//network'))+1)
E.SubElement(root.find('.//networks'),'network',{'id':networkid,'type':'pnet0','name':'WAN1-UPSTREAM-PNET0','left':'250','top':'40','visibility':'1','icon':'lan.png'})
for _,_,i in nodes:i.set('network_id',networkid)
new=E.tostring(root,encoding='utf-8',xml_declaration=True)
check=E.fromstring(new)
for name,_,_ in nodes:
 next(n for n in check.findall('.//node') if n.get('name')==name).find("interface[@id='1']").set('network_id','4')
check.find('.//networks').remove(next(n for n in check.findall('.//network') if n.get('id')==networkid))
assert E.tostring(check)==E.tostring(E.fromstring(raw)),'Unexpected topology change'
state={'status':'PREPARED','work':str(work),'before_sha256':sha(raw),'after_sha256':sha(new),'owner':[lab.stat().st_uid,lab.stat().st_gid],'mode':lab.stat().st_mode&0o777,'masters':masters,'host_before':beforehost,'baseline':baseline,'network_id':networkid,'history':[]}
save(work/'state.json',state)
assert lab.read_bytes()==raw and hoststate()==beforehost
state['status']='ARMED';state['deadline']=time.monotonic()+180;save(work/'state.json',state)
wd={'mode':'watchdog','work':str(work)}
program='BUNDLE='+repr(base64.b64encode(json.dumps(wd).encode()).decode())+'\n'+bundle['self']
watchdog=work/'watchdog.py';watchdog.write_text(program);watchdog.chmod(0o700)
with open(work/'watchdog.log','w') as log:subprocess.Popen(['python3',str(watchdog)],stdout=log,stderr=log,start_new_session=True)
try:
 for tap in masters:run(['ip','link','set','dev',tap,'master','pnet0'])
 assert lab.read_bytes()==raw
 temp=lab.with_suffix('.wan-new');temp.write_bytes(new);os.chown(temp,*state['owner']);os.chmod(temp,state['mode']);os.replace(temp,lab)
 while time.monotonic()<state['deadline']-15:
  assert json.loads((work/'state.json').read_text())['status']=='ARMED','Watchdog already acted'
  assert hoststate()==beforehost,'Management IP/route changed'
  for name,x in process.items():assert pids()[name]['pid']==x['pid'],'Existing QEMU changed'
  for tap,old in allmasters.items():assert master(tap)==('pnet0' if tap in masters else old),'Unexpected bridge change'
  guards={name:guard(name,name+'-after',work) for name,_,_ in nodes}
  assert json.loads((work/'state.json').read_text())['status']=='ARMED' and time.monotonic()<state['deadline']-2,'Watchdog window elapsed'
  state['history'].append({'monotonic':time.monotonic(),'guards':guards});save(work/'state.json',state)
  assert all(valid(g) and g['protected']==baseline[name]['protected'] and g['hook']==baseline[name]['hook'] for name,g in guards.items()),'HA/protected config changed'
  ips=[g['wan'][0][0] if g['wan'] else None for g in guards.values()]
  if all(ip and ip.startswith('192.168.220.') for ip in ips) and len(set(ips))==2 and all(g['gateway']=='192.168.220.2' and g['wan'][0][1]=='0xffffff00' for g in guards.values()):
   assert sha(lab.read_bytes())==state['after_sha256']
   state['status']='WAN_READY';state['host_after']=hoststate();save(work/'state.json',state);break
  time.sleep(4)
 else:raise RuntimeError('No two valid DHCP leases/default gateways within watchdog window')
except Exception as error:
 state['error']=str(error);save(work/'state.json',state);result=rollback(work)
else:result=state
export(work,result)
