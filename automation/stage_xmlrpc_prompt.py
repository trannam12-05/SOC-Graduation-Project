"""Chuẩn bị prompt xác thực không ghi bí mật trên Primary."""
import json
from topology_console_job import TopologyConsoleJob
from topology_remote import ROOT
a=TopologyConsoleJob(ROOT/'docs/evidence/M3/resume-20261102/xmlrpc-stage','xmlrpc-private-20261102','OPNsense-Primary')
a.stage({'private.php':(ROOT/'automation/xmlrpc_config_private.php').read_bytes(),'prompt.py':(ROOT/'automation/xmlrpc_prompt_private.py').read_bytes()})
p=a.command('python3 '+a.remote+'/prompt.py')
print(json.dumps({'prompt_image':str(p),'script':a.remote+'/prompt.py','scope':'Await user input directly in console; never ask for password in chat'}))
