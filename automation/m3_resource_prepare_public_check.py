"""Mã chỉ đọc được gõ bằng hex chữ thường để tránh lệch Shift trên console."""
from m3_resource_optimization import OUT
code='import xml.etree.ElementTree as e; r=e.parse("/conf/config.xml").getroot(); print([(k,r.findtext("hasync/"+k)) for k in ["pfsyncinterface","pfsyncpeerip"]]); print("vip_count",len(r.findall(".//vip")))'
(OUT/'fw-persistent.txt').write_text("python3 -c 'exec(bytes.fromhex(\""+code.encode().hex()+"\"))'; ping -c 2 "+'__PEER__',encoding='ascii')
for role,peer in [('primary','10.255.255.2'),('secondary','10.255.255.1')]:
 (OUT/('fw-persistent-'+role+'.txt')).write_text((OUT/'fw-persistent.txt').read_text().replace('__PEER__',peer),encoding='ascii')
