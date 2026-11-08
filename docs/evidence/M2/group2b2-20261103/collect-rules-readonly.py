"""Chỉ đọc cấu hình/rules; chỉ lưu dữ liệu công khai vào tệp tạm truyền minh chứng."""
import base64, hashlib, json, pathlib, subprocess, zlib
import xml.etree.ElementTree as E

path = pathlib.Path('/conf/config.xml')
raw = path.read_bytes()
root = E.fromstring(raw)
assert root.findtext('interfaces/opt1/ipaddr') == '192.168.30.2'
assert root.findtext('interfaces/opt6/ipaddr') == '10.255.255.1'

def fields(node, names):
    return {k: node.findtext(k) for k in names.split() if node.find(k) is not None}

def endpoint(node):
    if node is None:
        return None
    return fields(node, 'any network address port not')

def run(args):
    p = subprocess.run(args, text=True, capture_output=True, timeout=25)
    return {'rc': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}

legacy = []
for i, n in enumerate(root.findall('filter/rule'), 1):
    row = fields(n, 'type interface ipprotocol protocol direction floating quick disabled log descr tracker statetype')
    row.update(position=i, source=endpoint(n.find('source')), destination=endpoint(n.find('destination')))
    legacy.append(row)
modern = []
for i, n in enumerate(root.findall('OPNsense/Firewall/Filter/rules/rule'), 1):
    row = fields(n, 'enabled action quick interface direction ipprotocol protocol source_net source_not source_port destination_net destination_not destination_port log sequence description nosync statetype icmptype')
    row.update(position=i, uuid=n.get('uuid'))
    modern.append(row)
aliases = []
for n in root.findall('aliases/alias') + root.findall('OPNsense/Firewall/Alias/aliases/alias'):
    row = fields(n, 'name type enabled')
    if row.get('type') in ['host', 'network', 'port', 'mac']:
        row.update(fields(n, 'address content'))
    else:
        row['content_omitted'] = 'Không xuất URL hoặc kiểu alias có thể chứa thông tin xác thực'
    aliases.append(row)
interfaces = [{'assignment': n.tag, **fields(n, 'if ipaddr subnet ipaddrv6 subnetv6 enable descr')} for n in root.findall('interfaces/*')]
groups = [fields(n, 'ifname members descr') for n in root.findall('ifgroups/ifgroupentry')]
pf = run(['/sbin/pfctl', '-vvsr'])
anchors = run(['/sbin/pfctl', '-a', '*', '-sr'])
tables = run(['/sbin/pfctl', '-s', 'Tables'])
public = {'config_sha256_before': hashlib.sha256(raw).hexdigest(), 'interfaces': interfaces,
          'legacy_rules': legacy, 'modern_rules': modern, 'aliases': aliases, 'interface_groups': groups,
          'webgui': fields(root.find('system/webgui'), 'protocol port interfaces') if root.find('system/webgui') is not None else {},
          'anti_lockout_disabled': root.find('system/disableantilockout') is not None,
          'ssh': fields(root.find('system/ssh'), 'enable port interfaces') if root.find('system/ssh') is not None else {},
          'sync': fields(root.find('hasync'), 'pfsyncinterface pfsyncpeerip pfsyncenabled synchronizefilter') if root.find('hasync') is not None else {},
          'pf_rules_verbose': pf, 'pf_anchor_filter_rules': anchors, 'pf_tables_names_only': tables,
          'version': run(['/usr/local/sbin/opnsense-version']),
          'config_sha256_after': hashlib.sha256(path.read_bytes()).hexdigest(),
          'scope': 'READ_ONLY_CONFIG_AND_PF; no reload, state reset, traffic test or configuration save'}
public['config_unchanged'] = public['config_sha256_before'] == public['config_sha256_after']
encoded = base64.b64encode(zlib.compress(json.dumps(public).encode(), 9)).decode()
pathlib.Path('/var/tmp/soc-2b2-public-rules.b64').write_text(encoded)
print('PUBLIC_RULES_READY', len(encoded), hashlib.sha256(encoded.encode()).hexdigest(),
      'legacy', len(legacy), 'modern', len(modern), 'config_unchanged', public['config_unchanged'])
