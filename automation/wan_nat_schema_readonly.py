import pathlib,xml.etree.ElementTree as E,json
p=pathlib.Path('/usr/local/opnsense/mvc/app/models/OPNsense/Firewall/Filter.xml');r=E.fromstring(p.read_bytes());items=r.find('items')
d={'schema_file':str(p),'nat_settings':E.tostring(items.find('settings/nat'),encoding='unicode') if items.find('settings/nat') is not None else None,'snat_rule_fields':[(n.tag,dict(n.attrib),n.findtext('Default')) for n in items.findall('snatrules/rule/*')],'snat_target':E.tostring(items.find('snatrules/rule/target'),encoding='unicode') if items.find('snatrules/rule/target') is not None else None}
