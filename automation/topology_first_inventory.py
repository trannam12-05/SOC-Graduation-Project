"""Xuất lab thật, danh sách NIC/segment và kiểm tra cấu trúc; không thử lại VLAN."""
import base64,datetime as dt,json,csv,hashlib
from topology_remote import remote,ROOT
EV=ROOT/'docs/evidence/M2/topology-first-20261102'
CODE=r'''
import pathlib,json,base64,xml.etree.ElementTree as E,subprocess,os
p=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');r=E.parse(p).getroot()
nodes=[{'attributes':dict(n.attrib),'interfaces':[dict(i.attrib) for i in n.findall('interface')]} for n in r.findall('.//node')]
processes=[]
for p2 in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[s.decode(errors='replace') for s in p2.read_bytes().split(b'\0') if s]
  if a and 'qemu-system-' in os.path.basename(a[0]):processes.append({'pid':p2.parent.name,'name':a[a.index('-name')+1],'uuid':a[a.index('-uuid')+1],'ram_mib':a[a.index('-m')+1]})
 except (FileNotFoundError,ValueError,ProcessLookupError):pass
print(json.dumps({'lab_path':str(p),'lab_id':r.get('id'),'nodes':nodes,'networks':[dict(n.attrib) for n in r.findall('.//network')],
 'textobjects':len(r.findall('.//textobject')),'running_qemu':processes,
 'memory':subprocess.run(['free','-m'],text=True,capture_output=True).stdout,
 'lab_xml_base64':base64.b64encode(p.read_bytes()).decode(),
 'images':[{'name':p.name,'files':[{'name':f.name,'bytes':f.stat().st_size} for f in p.iterdir() if f.is_file()]} for p in pathlib.Path('/opt/unetlab/addons/qemu').iterdir() if p.is_dir()]}))
'''

def collect(label='after'):
 d=json.loads(remote(CODE));raw=base64.b64decode(d.pop('lab_xml_base64'))
 d['collector_time']=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
 d['time_basis']='Windows collector UTC+07:00; EVE clock is untrusted'
 (EV/f'lab-{label}.unl').write_bytes(raw)
 (EV/f'inventory-{label}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 ns={n['attributes']['name']:n for n in d['nodes']}; nets={n['name']:n for n in d['networks']}
 def net(name,port):return next((x['network_id'] for x in ns[name]['interfaces'] if int(x['id'])==port),None)
 tests={
  'node_count_10':len(ns)==10,'segments_11':len(nets)==11,
  'firewalls_4_nics':all(ns[n]['attributes']['ethernet']=='4' for n in ['OPNsense-Primary','OPNsense-Secondary']),
  'core_eight_nics':ns['SOC-Core-L2']['attributes']['ethernet']=='8',
  'original_primary_trunk':net('SOC-Core-L2',5)==net('OPNsense-Primary',0)=='1',
  'original_secondary_trunk':net('SOC-Core-L2',6)==net('OPNsense-Secondary',0)=='2',
  'original_sync':net('OPNsense-Primary',2)==net('OPNsense-Secondary',2)=='3',
  'wan_segments_isolated':all(nets[n]['type']=='bridge' for n in ['WAN-ISP-1','WAN-ISP-2']),
  'capture_separate_management':net('Suricata-NIDS',0)!=net('Suricata-NIDS',1),
  'capture_core_only':net('Suricata-NIDS',0)==net('SOC-Core-L2',7),
  'sensor_management':net('Suricata-NIDS',1)==net('Management',0)==net('SOC-Core-L2',4),
  'wazuh_no_invented_connection':not ns['Wazuh-SOC']['interfaces'],
 }
 for port,name in enumerate(['Data-Center','Employee','Guest','DMZ','Management']):tests['core_access_'+name]=net('SOC-Core-L2',port)==net(name,0)
 for port,name in [(1,'WAN-ISP-1'),(3,'WAN-ISP-2')]:tests['both_firewalls_'+name]=net('OPNsense-Primary',port)==net('OPNsense-Secondary',port)==nets[name]['id']
 validation={'collected_at':d['collector_time'],'structural_checks':tests,'all_structural_checks_passed':all(tests.values()),'scope':'XML structure only; not guest configuration, traffic, gateway, HA, IDS or SOC verification','global_TOPOLOGY_READY':False,'unresolved':'Wazuh physical attachment, WAN upstream and exact endpoint multiplicity are not specified'}
 (EV/f'validation-{label}.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
 with (EV/f'nodes-{label}.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['node_id','name','template','image','nic_count','ram_MiB','power','implementation_state','collector_time'])
  running={p['name'] for p in d['running_qemu']}
  for n in d['nodes']:
   a=n['attributes'];name=a['name']
   state='CONFIGURED; VERIFIED_M2_ONLY_HISTORICAL' if name=='SOC-Core-L2' else 'OS_INSTALLED_VERIFIED_HISTORICAL; GATEWAY_NOT_VERIFIED' if name=='OPNsense-Primary' else 'CONFIGURED_ON_DISK; HA_PARTIAL_ONLY' if name=='OPNsense-Secondary' else 'CONFIGURED_SERVICE; MIRROR_NOT_YET_VERIFIED' if name=='Suricata-NIDS' else 'CREATED_NOT_CONFIGURED; VPCS_BINARY_AVAILABLE' if name in ['Employee','Guest','Management'] else 'CREATED_NOT_INSTALLED'
   w.writerow([a['id'],name,a['template'],a.get('image',''),a['ethernet'],a.get('ram',''), 'RUNNING' if name in running else 'STOPPED',state,d['collector_time']])
 with (EV/f'interfaces-{label}.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f);w.writerow(['node','interface_id','eve_label','network_id','segment','collector_time'])
  ids={n['id']:n['name'] for n in d['networks']}
  for n in d['nodes']:
   for i in n['interfaces']:w.writerow([n['attributes']['name'],i['id'],i['name'],i['network_id'],ids[i['network_id']],d['collector_time']])
 print(json.dumps({'nodes':len(ns),'segments':len(nets),'nic_attachments':sum(len(n['interfaces']) for n in d['nodes']),'structural_checks_passed':all(tests.values()),'running':list(running),'evidence':str(EV)},ensure_ascii=True))
 return d

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--label',default='after');a=p.parse_args();collect(a.label)
