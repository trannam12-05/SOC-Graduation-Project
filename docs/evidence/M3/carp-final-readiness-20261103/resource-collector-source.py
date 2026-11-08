
import pathlib,json,os,subprocess,xml.etree.ElementTree as e,time
r=e.parse('/opt/unetlab/labs/SOC-M2-Core-L2.unl').getroot();wanted=['SOC-Core-L2','OPNsense-Primary','OPNsense-Secondary'];nodes=[dict(n.attrib) for n in r.findall('.//node') if n.get('name') in wanted];running=[]
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[x.decode(errors='replace') for x in p.read_bytes().split(bytes([0])) if x]
  if a and 'qemu-system-' in os.path.basename(a[0]):
   stat={x.split(':')[0]:x.split(':',1)[1].strip() for x in (p.parent/'status').read_text().splitlines() if ':' in x}
   running.append({'pid':p.parent.name,'name':a[a.index('-name')+1],'ram_mib':int(a[a.index('-m')+1]),'smp':a[a.index('-smp')+1],'vmrss':stat.get('VmRSS'),'vmswap':stat.get('VmSwap')})
 except (OSError,ValueError):pass
mem={x.split(':')[0]:int(x.split()[1]) for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if len(x.split())>1 and x.split()[1].isdigit()}
commands={}
for label,args in [('free',['free','-m']),('vmstat',['vmstat','1','3']),('cpu',['lscpu']),('uptime',['uptime']),('process_usage',['ps','-eo','pid,comm,pcpu,pmem,rss','--sort=-pcpu'])]:
 p=subprocess.run(args,capture_output=True,text=True,timeout=10);commands[label]={'rc':p.returncode,'stdout':p.stdout if label!='process_usage' else '\n'.join(p.stdout.splitlines()[:16]),'stderr':p.stderr}
print(json.dumps({'nodes':nodes,'running_qemu':running,'meminfo_kib':mem,'cpu_count':os.cpu_count(),'loadavg':os.getloadavg(),'commands':commands}))
