"""Nhập thông tin xác thực riêng Secondary qua RFB, không ghi vào log/ảnh.

Mật khẩu root mới được tạo ngẫu nhiên và mã hóa DPAPI CurrentUser ngoài repo.
Chỉ chạy sau khi đã xem đúng màn hình nhập liệu. Tài khoản installer dùng
thông tin mặc định công khai trong tài liệu cài đặt chính thức OPNsense.
"""
import argparse,base64,secrets,subprocess,sys
from pathlib import Path
import capture_m2_core_console as cap

PRIVATE=Path.home()/'.soc-private/secondary-root.dpapi'
def root_value():
 PRIVATE.parent.mkdir(exist_ok=True)
 if not PRIVATE.exists():
  value=secrets.token_hex(16)
  code='Add-Type -AssemblyName System.Security; $b=[Text.Encoding]::UTF8.GetBytes([Console]::In.ReadToEnd()); [Convert]::ToBase64String([Security.Cryptography.ProtectedData]::Protect($b,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser))'
  r=subprocess.run(['powershell.exe','-NoProfile','-Command',code],input=value,capture_output=True,text=True,check=True)
  PRIVATE.write_text(r.stdout.strip(),encoding='ascii');return value
 code='Add-Type -AssemblyName System.Security; $b=[Convert]::FromBase64String([Console]::In.ReadToEnd()); [Text.Encoding]::UTF8.GetString([Security.Cryptography.ProtectedData]::Unprotect($b,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser))'
 r=subprocess.run(['powershell.exe','-NoProfile','-Command',code],input=PRIVATE.read_text(),capture_output=True,text=True,check=True)
 return r.stdout.strip()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['installer-login','root-login','set-root-first','set-root-confirm']);p.add_argument('--label',required=True);a=p.parse_args()
 # These documented installer credentials are public, never user credentials.
 values=['installer','opnsense'] if a.mode=='installer-login' else ['root',root_value()] if a.mode=='root-login' else [root_value()]
 cap.REMOTE=cap.REMOTE.replace("n.get('name') == 'SOC-Core-L2'","n.get('name') == 'OPNsense-Secondary'")
 encoded=base64.b64encode(__import__('json').dumps(values).encode()).decode()
 injection='    private_values = json.loads(base64.b64decode('+repr(encoded)+'))\n'
 injection+='    for private_value in private_values:\n        for c in private_value:\n            k=ord(c)\n            sock.sendall(struct.pack(">BBHI",4,1,0,k)+struct.pack(">BBHI",4,0,0,k))\n            time.sleep(0.04)\n        sock.sendall(struct.pack(">BBHI",4,1,0,0xff0d)+struct.pack(">BBHI",4,0,0,0xff0d))\n        time.sleep(1.5)\n    del private_values, private_value\n    time.sleep(2)\n'
 cap.REMOTE=cap.REMOTE.replace('    pixel_format = struct.pack',injection+'    pixel_format = struct.pack')
 sys.argv=[sys.argv[0],'--output-dir','docs/evidence/M3/secondary-20261102','--label',a.label]
 cap.main()
