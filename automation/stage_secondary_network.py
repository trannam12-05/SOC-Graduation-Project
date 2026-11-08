"""Truyền script bảo toàn mạng Secondary; chỉ chạy pha kiểm tra."""
import json
from topology_console_job import TopologyConsoleJob
from topology_remote import ROOT
directory=ROOT/'docs/evidence/M3/resume-20261102/secondary-network-stage'
adapter=TopologyConsoleJob(directory,'secondary-network-v2-20261102','OPNsense-Secondary')
adapter.stage({'secondary.py':(ROOT/'automation/secondary_preserve_network.py').read_bytes()})
image=adapter.command('python3 '+adapter.remote+'/secondary.py')
print(json.dumps({'path':adapter.remote+'/secondary.py','check_image':str(image)}))
