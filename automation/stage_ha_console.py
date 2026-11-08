"""Đưa script HA không chứa bí mật vào đúng firewall qua console có checksum."""
import argparse,json
from pathlib import Path
from topology_console_job import TopologyConsoleJob
from topology_remote import ROOT

p=argparse.ArgumentParser();p.add_argument('role',choices=['Primary','Secondary']);a=p.parse_args()
directory=ROOT/'docs/evidence/M3/resume-20261102'/('ha-stage-'+a.role)
adapter=TopologyConsoleJob(directory,'ha-rules-'+a.role.lower()+'-20261102','OPNsense-'+a.role)
adapter.stage({'ha.php':(ROOT/'automation/ha_sync_rules.php').read_bytes()})
image=adapter.command('php '+adapter.remote+'/ha.php '+a.role+' check')
print(json.dumps({'role':a.role,'path':adapter.remote+'/ha.php','validation_image':str(image)}))
