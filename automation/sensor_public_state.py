"""Xuất service, NIC và alert lab từ sensor qua serial thật, không dùng IP guest."""
import json,datetime as dt,subprocess,sys
from pathlib import Path
from topology_remote import remote,ROOT

if __name__=='__main__':
 label=sys.argv[1]
 code='import json,pathlib,subprocess; p=pathlib.Path("/var/log/suricata/eve.json"); a=[json.loads(l) for l in p.open() if "\\\"alert\\\"" in l] if p.exists() else []; a=[x for x in a if x.get("event_type")=="alert" and x.get("alert",{}).get("signature_id") in [1000001,1000002]]; d={"service":subprocess.run(["systemctl","is-active","soc-suricata.service"],capture_output=True,text=True).stdout.strip(),"capture_interface":json.loads(subprocess.run(["ip","-j","address","show","capture0"],capture_output=True,text=True).stdout),"alerts":a,"boot_id":pathlib.Path("/proc/sys/kernel/random/boot_id").read_text().strip()}; print("SOC_SENSOR_PUBLIC "+json.dumps(d),file=open("/dev/ttyS0","w")); print("PUBLIC_STATE_EXPORTED")'
 file=ROOT/'staging/topology-first'/('sensor-export-'+label+'.txt');file.write_text("sudo -n python3 -c '"+code+"'")
 p=subprocess.run([sys.executable,str(ROOT/'automation/topology_console.py'),'--node','Suricata-NIDS','--output-dir','docs/evidence/M4/resume-20261102','--label','sensor-export-'+label,'--command-file',str(file)],text=True,capture_output=True,encoding='utf-8',timeout=65)
 assert p.returncode==0,p.stderr
 print(p.stdout.strip())
 out=remote("import pathlib,json\np=pathlib.Path('/opt/unetlab/tmp/0/f39cfc8c-5eaf-461e-bb0c-60b5fde848b7/9/serial.log')\nrows=[line.split('SOC_SENSOR_PUBLIC ',1)[1] for line in p.read_text(errors='replace').splitlines() if 'SOC_SENSOR_PUBLIC ' in line]\nassert rows,'No public result in actual serial log'\nprint(rows[-1])")
 d=json.loads(out);d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat();d['scope']='Actual live sensor state; guest timestamps untrusted, correlate marker and addresses'
 target=ROOT/'docs/evidence/M4/resume-20261102'/('sensor-public-'+label+'.json');target.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'state':d['service'],'alerts':len(d['alerts']),'evidence':str(target)}))
