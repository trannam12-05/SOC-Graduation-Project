import sys,concurrent.futures
from pathlib import Path
out=Path(__file__).parent;sys.path.insert(0,str(out))
from stage_memory_reader import call
# Fresh shell was confirmed by reader-exit snapshots; no configuration commands.
def run(role):
 call(role,"ifconfig pfsync0; sysctl net.inet.carp.demotion; sha256 -q /conf/config.xml",'pfsync-proof')
 call(role,"ifconfig -a | grep -e vtnet0_vlan -e 'inet 192.168.' -e 'inet 10.255.' -e 'carp:'",'vlan-proof')
 call(role,"python3 -c 'import xml.etree.ElementTree as e; r=e.parse(\"/conf/config.xml\").getroot(); print(\"vip_count\",len(r.findall(\".//vip\"))); print(\"carp_nodes\",len([n for n in r.iter() if n.tag.lower()==\"mode\" and n.text==\"carp\"]))'",'persistent-vip-proof')
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,['Primary','Secondary']))
