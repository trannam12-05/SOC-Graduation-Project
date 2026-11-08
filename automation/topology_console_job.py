"""Tái dùng truyền console có checksum cho Linux mới, không đụng adapter Core."""
from pathlib import Path
import json,subprocess,sys
from m2_console_job import ConsoleJob,ConsoleTransportError,ROOT

class TopologyConsoleJob(ConsoleJob):
 def __init__(self,directory,session,node):
  super().__init__(directory,session,shell_ready=True);self.node=node
 def command(self,text):
  self.counter+=1
  path=self.directory/('command-'+str(self.counter).zfill(4)+'.txt');path.write_text(text,encoding='utf-8')
  p=subprocess.run([sys.executable,str(ROOT/'automation/topology_console.py'),'--node',self.node,'--output-dir',str(self.directory),'--label','job'+str(self.counter),'--command-file',str(path)],capture_output=True,text=True,encoding='utf-8',timeout=75)
  if p.returncode:raise ConsoleTransportError('Không xác định kết quả console; kiểm tra ảnh trước khi tiếp tục')
  return Path(json.loads(p.stdout)['image'])

if __name__=='__main__':
 directory=ROOT/'docs/evidence/M4/topology-first-20261102/console-export'
 adapter=TopologyConsoleJob(directory,'sensor-export-20261102','Suricata-NIDS')
 files={'guest.py':(ROOT/'automation/sensor_export_guest.py').read_bytes()}
 adapter.stage(files)
 reply=adapter.run('collect','/var/lib/soc')
 data=json.loads(reply['stdout'])
 out=ROOT/'docs/evidence/M4/topology-first-20261102'
 (out/'sensor-configuration-public.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'state':data['result']['state'],'transport':'Exact glyph match and SHA256 verified','output':str(out/'sensor-configuration-public.json')}))
