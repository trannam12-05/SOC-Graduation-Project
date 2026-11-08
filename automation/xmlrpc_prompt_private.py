"""Chạy ở console Primary; người dùng nhập bí mật trực tiếp, không đưa vào log."""
import getpass,json,base64,ssl,socket,subprocess,xmlrpc.client
from pathlib import Path

class PrivateTransport(xmlrpc.client.SafeTransport):
 def __init__(self,value):
  super().__init__(context=ssl._create_unverified_context())
  self.auth=base64.b64encode(('root:'+value).encode()).decode()
 def send_headers(self,connection,headers):
  super().send_headers(connection,headers+[('Authorization','Basic '+self.auth)])

try:
 socket.setdefaulttimeout(15)
 secret=getpass.getpass('Nhap mat khau root cua Secondary (khong hien thi): ')
 server=xmlrpc.client.ServerProxy('https://10.255.255.2/xmlrpc.php',transport=PrivateTransport(secret),allow_none=True)
 version=server.opnsense.firmware_version()
 if not isinstance(version,(dict,list)):
  raise RuntimeError('Remote authentication/version response rejected')
 path=Path(__file__).with_name('private.php')
 response=subprocess.run(['php',str(path)],input=json.dumps({'secret':secret}),text=True,capture_output=True,timeout=30)
 del secret,server
 if response.returncode:raise RuntimeError('Configuration validation/save did not complete')
 print('XMLRPC_AUTHENTICATED_AND_CONFIGURED_ALIASES_ONLY')
except Exception as error:
 print('XMLRPC_NOT_CONFIGURED: '+type(error).__name__+'; no credential values logged')
