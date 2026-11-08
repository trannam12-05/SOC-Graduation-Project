import subprocess,json,pathlib
def run(args):
    q=subprocess.run(args,text=True,capture_output=True,timeout=15);return dict(rc=q.returncode,out=q.stdout,err=q.stderr)
d={'hostname':run(['hostname']),'addresses':run(['ip','-j','address','show','lan0']),'routes':run(['ip','-j','route']),'route_to_client':run(['ip','-j','route','get','192.168.40.100']),'http_service':run(['systemctl','is-active','soc-lab-http']),'http_main_pid':run(['systemctl','show','soc-lab-http','-p','MainPID','--value']),'listening':run(['ss','-lnt']),'boot_id':pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'scope':'Chỉ đọc dịch vụ/địa chỉ/route; không GET, không TCP client, không state/failover test.'}
