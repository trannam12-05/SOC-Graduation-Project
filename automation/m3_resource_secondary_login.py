"""Tái dùng credential Secondary DPAPI có sẵn; không xuất/lưu plaintext."""
import sys,base64,json
import capture_m2_core_console as cap
from secondary_secure_console import PRIVATE,root_value
assert PRIVATE.is_file(),'Existing credential required; never generate a replacement'
values=['root',root_value()]
cap.REMOTE=cap.REMOTE.replace("n.get('name') == 'SOC-Core-L2'","n.get('name') == 'OPNsense-Secondary'")
encoded=base64.b64encode(json.dumps(values).encode()).decode()
injection='    private_values = json.loads(base64.b64decode('+repr(encoded)+'))\n'
injection+='    for private_value in private_values:\n        for c in private_value:\n            k=ord(c)\n            sock.sendall(struct.pack(">BBHI",4,1,0,k)+struct.pack(">BBHI",4,0,0,k))\n            time.sleep(0.04)\n        sock.sendall(struct.pack(">BBHI",4,1,0,0xff0d)+struct.pack(">BBHI",4,0,0,0xff0d))\n        time.sleep(1.5)\n    del private_values, private_value\n    time.sleep(2)\n'
cap.REMOTE=cap.REMOTE.replace('    pixel_format = struct.pack',injection+'    pixel_format = struct.pack')
sys.argv=['capture','--output-dir','docs/evidence/M3/resource-optimization-20261103','--label','secondary-authenticated']
cap.main()
