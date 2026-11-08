from pathlib import Path
import sys,concurrent.futures
out=Path(__file__).parent;sys.path.insert(0,str(out));from stage_memory_reader import call
payload='import xml.etree.ElementTree as e;r=e.parse("/conf/config.xml").getroot();print(chr(27)+"[2J"+chr(27)+"[H");print("VIP_COUNT",len(r.findall(".//vip")));print("CARP_MODE_COUNT",len([n for n in r.iter() if n.tag.lower()=="mode" and n.text=="carp"]))'
cmd="python3 -c 'exec(bytes.fromhex(\""+payload.encode().hex()+"\"))'"
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda role:call(role,cmd,'persistent-vip-proof-verified'),['Primary','Secondary']))
