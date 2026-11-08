import json,re,hashlib,datetime
from pathlib import Path
out=Path(__file__).parent
vlans=[30,40,50,60,99]
def blocks(text):
 matches=list(re.finditer(r'(?m)^([^\s:]+): flags=',text));return {m.group(1):text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)] for i,m in enumerate(matches)}
def analyze(role):
 d=json.loads((out/(role.lower()+'-snapshot.json')).read_text(encoding='utf-8'));bs=blocks(d['ifconfig']['stdout']);rows=[]
 for v in vlans:
  name='vtnet0_vlan'+str(v);block=bs.get(name,'');ips=re.findall(r'\binet ([0-9.]+)',block);state=re.search(r'carp:\s*(MASTER|BACKUP|INIT)',block,re.I);vip='192.168.'+str(v)+'.1';expected='192.168.'+str(v)+('.2' if role=='Primary' else '.3')
  runtime=state.group(1).upper() if state and vip in ips else 'ABSENT' if block and not state and vip not in ips else 'ERROR' if d['ifconfig']['rc'] else 'UNKNOWN'
  rows.append(dict(vlan=v,interface=name,exists=bool(block),up=bool(re.search(r'<[^>]*\bUP\b',block)),ips=ips,expected=expected,vlan_match=expected in ips,carp_runtime=runtime,vip=vip,carp_detail=state.group(0) if state else None))
 ps=bs.get('pfsync0','');peer='10.255.255.2' if role=='Primary' else '10.255.255.1';up=bool(re.search(r'<[^>]*\bUP\b',ps));ok=bool(re.search(r'\bsyncok:\s*1\b',ps));dem=re.search(r'net.inet.carp.demotion:\s*(\d+)',d['carp_sysctl']['stdout']);dem=int(dem.group(1)) if dem else None
 ready=up and ok and 'syncdev: vtnet2' in ps and 'syncpeer: '+peer in ps and dem==0
 pf='READY' if ready else 'NOT READY' if ps and not up else 'DEGRADED' if ps else 'UNKNOWN'
 expected_names={'vtnet0','vtnet1','vtnet2','vtnet3','lo0','enc0','pfsync0','pflog0'}|{'vtnet0_vlan'+str(v) for v in vlans}
 actual=[v for v in d['vips'] if v.get('mode','').lower()=='carp' or v.get('vhid') not in [None,'','0']]
 return dict(role=role,config_sha256=d['config_sha256'],backup_sha256=d['backup_sha256'],backup_equal=d['backup_equal'],sections_equal=d['sections_equal'],config_unchanged=d['config_unchanged_during_read'],vlans=rows,sync=bs.get('vtnet2',''),unexpected_interfaces=sorted(set(bs)-expected_names),vips=actual,pfsync=dict(status=pf,runtime=ps,demotion=dem),probe_file_exists=d['probe_file_exists'])
if __name__=='__main__':
 d={r:analyze(r) for r in ['Primary','Secondary']};(out/'comparison-results.json').write_text(json.dumps(d,indent=2),encoding='utf-8');print(json.dumps(d,indent=2))
