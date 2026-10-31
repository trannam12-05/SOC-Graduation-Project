"""Chụp console SOC-Core-L2 qua SSH/RFB; mặc định chỉ đọc framebuffer.

--command-file gửi một dòng lệnh theo phạm vi người dùng đã cho phép.
Phải kiểm tra ảnh và dấu nhắc đúng guest trước mỗi bước phụ thuộc.
Không thay vòng đời node, không truy cập ổ QCOW2; không gửi bí mật.
"""
import argparse
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

REMOTE = r'''
import base64, datetime, glob, json, os, re, socket, struct, subprocess, time, zlib
import xml.etree.ElementTree as ET
check = __CHECK__
custom_command = __CUSTOM_COMMAND__
lab = '/opt/unetlab/labs/SOC-M2-Core-L2.unl'
root = ET.parse(lab).getroot()
node = next(n for n in root.findall('.//node') if n.get('name') == 'SOC-Core-L2')
facts = {'lab': lab, 'lab_id': root.get('id'), 'node': dict(node.attrib),
         'interfaces': [n.attrib for n in node.findall('interface')],
         'networks': [n.attrib for n in root.findall('.//network')]}
processes = []
for path in glob.glob('/proc/[0-9]*/cmdline'):
    try:
        args = open(path, 'rb').read().split(bytes([0]))
        args = [a.decode(errors='replace') for a in args if a]
        if args and os.path.basename(args[0]) == 'qemu-system-x86_64' and node.get('uuid') in args:
            pid = path.split('/')[2]
            processes.append({'pid': pid, 'args': args, 'cwd': os.readlink('/proc/' + pid + '/cwd')})
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
if len(processes) != 1:
    raise RuntimeError('Can xac dinh duy nhat tien trinh QEMU dang chay; khong start node.')
facts['qemu'] = processes[0]
args = processes[0]['args']
display = args[args.index('-vnc') + 1]
match = re.fullmatch(r':(\d+)', display)
if not match:
    raise RuntimeError('VNC display khong thuoc dang da ho tro; dung, khong thay cau hinh.')
port = 5900 + int(match.group(1))
facts['vnc_port'] = port
facts['remote_clock_utc_untrusted'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
for label, command in [('host_clock', ['timedatectl','show','-p','Timezone','-p','NTPSynchronized']),
                       ('host_links', ['ip','-j','link','show'])]:
    result = subprocess.run(command, text=True, capture_output=True)
    facts[label] = {'command': command, 'returncode': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr}

def readn(sock, size):
    data = b''
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise RuntimeError('VNC dong ket noi')
        data += part
    return data

def chunk(kind, data):
    return struct.pack('>I',len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

with socket.create_connection(('127.0.0.1',port),timeout=10) as sock:
    sock.settimeout(15)
    protocol = readn(sock,12)
    if protocol != b'RFB 003.008\n':
        raise RuntimeError('RFB protocol chua ho tro: ' + repr(protocol))
    sock.sendall(protocol)
    types = readn(sock, readn(sock,1)[0])
    if 1 not in types:
        raise RuntimeError('Khong co che do VNC None; khong thu mat khau.')
    sock.sendall(bytes([1]))
    if struct.unpack('>I',readn(sock,4))[0]:
        raise RuntimeError('Loi bat tay VNC')
    sock.sendall(bytes([1]))  # shared viewer, khong ngat viewer hien co
    header = readn(sock,24)
    width,height = struct.unpack('>HH',header[:4])
    facts['vnc_name'] = readn(sock,struct.unpack('>I',header[20:])[0]).decode(errors='replace')
    if check or custom_command:
        for modifier in [0xffe1,0xffe2,0xffe3,0xffe4,0xffe9,0xffea]:
            sock.sendall(struct.pack('>BBHI',4,0,0,modifier))
            time.sleep(0.05)
        commands = {
          'cloud-init': 'cloud-init status --long',
          'system-info': "hostname; ip -br link; nproc; free -m; whoami; cloud-id",
          'ovs-presence': "command -v ovs-vsctl; dpkg-query --show openvswitch-switch"
        }
        command = custom_command or commands[check]
        facts['guest_command_sent'] = command
        # Ctrl+L chi ve lai man hinh terminal that truoc lenh moi; khong sua anh.
        sock.sendall(struct.pack('>BBHI',4,1,0,0xffe3))
        time.sleep(0.05)
        sock.sendall(struct.pack('>BBHI',4,1,0,ord('l')))
        time.sleep(0.05)
        sock.sendall(struct.pack('>BBHI',4,0,0,ord('l')))
        time.sleep(0.05)
        sock.sendall(struct.pack('>BBHI',4,0,0,0xffe3))
        facts['display_action'] = 'Ctrl+L redraw at verified idle shell before running the read-only command; no image editing'
        time.sleep(0.3)
        for char in command:
            shifted = {'~':'`','!':'1','@':'2','#':'3','$':'4','%':'5','^':'6','&':'7','*':'8','(':'9',')':'0','_':'-','+':'=','{':'[','}':']','|':'\\',':':';','"':"'",'<':',','>':'.','?':'/'}
            needs_shift = char in shifted or char.isupper()
            key = ord(char)
            if needs_shift:
                sock.sendall(struct.pack('>BBHI',4,1,0,0xffe1))
                time.sleep(0.015)
            sock.sendall(struct.pack('>BBHI',4,1,0,key) + struct.pack('>BBHI',4,0,0,key))
            time.sleep(0.015)
            if needs_shift:
                sock.sendall(struct.pack('>BBHI',4,0,0,0xffe1))
                time.sleep(0.015)
            time.sleep(0.015)
        sock.sendall(struct.pack('>BBHI',4,1,0,0xff0d) + struct.pack('>BBHI',4,0,0,0xff0d))
        time.sleep(3)
    else:
        facts['guest_command_sent'] = None
    pixel_format = struct.pack('>BBBBHHHBBB3x',32,24,0,1,255,255,255,16,8,0)
    sock.sendall(bytes([0,0,0,0]) + pixel_format)
    sock.sendall(struct.pack('>BBHi',2,0,1,0))
    screen = bytearray(width * height * 3)
    # Doc hai khung hinh lien tiep: QEMU co the tra khung hinh cu o lan dau
    # khi viewer moi ket noi. Khong ghep/chinh sua noi dung giua cac khung hinh.
    for refresh in range(2):
        if refresh:
            time.sleep(1)
        sock.sendall(struct.pack('>BBHHHH',3,0,0,0,width,height))
        while True:
            typ = readn(sock,1)[0]
            if typ == 2:
                continue
            if typ == 3:
                h = readn(sock,7)
                readn(sock,struct.unpack('>I',h[3:])[0])
                continue
            if typ != 0:
                raise RuntimeError('Thong diep RFB khong duoc ho tro')
            count = struct.unpack('>H',readn(sock,3)[1:])[0]
            for _ in range(count):
                x,y,w,h,encoding = struct.unpack('>HHHHi',readn(sock,12))
                if encoding != 0:
                    raise RuntimeError('Chi nhan raw encoding; khong thay noi dung anh')
                raw = readn(sock,w*h*4)
                for row in range(h):
                    offset = row*w*4
                    rgb = bytearray(w*3)
                    rgb[0::3] = raw[offset+2:offset+w*4:4]
                    rgb[1::3] = raw[offset+1:offset+w*4:4]
                    rgb[2::3] = raw[offset:offset+w*4:4]
                    start = ((y+row)*width+x)*3
                    screen[start:start+w*3] = rgb
            break
    scan = b''.join(bytes([0]) + screen[i*width*3:(i+1)*width*3] for i in range(height))
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0)) + chunk(b'IDAT',zlib.compress(scan)) + chunk(b'IEND',b'')
    facts['capture'] = {'width':width,'height':height,'source':'QEMU VNC raw framebuffer; full screen; no image content changes',
                        'png_base64':base64.b64encode(png).decode()}
print(json.dumps(facts))
'''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--check', choices=['cloud-init','system-info','ovs-presence'])
    parser.add_argument('--command-file', type=Path, help='Lệnh đã duyệt cho guest Core; không chứa bí mật')
    options = parser.parse_args()
    if not all(c.isalnum() or c in '-_' for c in options.label):
        parser.error('Nhan tep chi dung chu, so, dau - hoac _.')
    ssh = ['ssh.exe','-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes',
           '-o','ConnectTimeout=10','-o','PasswordAuthentication=no','-o','KbdInteractiveAuthentication=no',
           '-i',str(Path.home()/'.ssh'/'eve-ng-root-ed25519'),'root@192.168.220.143','python3','-']
    started = dt.datetime.now(dt.timezone(dt.timedelta(hours=7)))
    command = options.command_file.read_text(encoding='utf-8').strip() if options.command_file else None
    if command and ('\n' in command or '\r' in command):
        raise ValueError('Chỉ một dòng lệnh mỗi lần để xác minh console')
    result = subprocess.run(ssh,input=REMOTE.replace('__CHECK__',repr(options.check)).replace('__CUSTOM_COMMAND__',repr(command)),
                            capture_output=True,text=True,encoding='utf-8',timeout=55)
    if result.returncode:
        raise RuntimeError('SSH/read-only capture failed: ' + result.stderr + result.stdout)
    facts = json.loads(result.stdout)
    facts['collector_time_start'] = started.isoformat()
    facts['collector_time_end'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat()
    facts['time_basis'] = 'Collector Windows clock converted to UTC+07:00; EVE clock recorded separately, not trusted as capture timestamp.'
    png = base64.b64decode(facts['capture'].pop('png_base64'))
    facts['capture']['sha256'] = hashlib.sha256(png).hexdigest()
    output_dir = Path(options.output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    stem = options.label + '-' + started.strftime('%Y%m%dT%H%M%S%z')
    image_path = output_dir/(stem+'.png')
    json_path = output_dir/(stem+'.json')
    if image_path.exists() or json_path.exists():
        raise FileExistsError('Khong ghi de minh chung cu')
    facts['capture']['path'] = str(image_path)
    with image_path.open('xb') as target:
        target.write(png)
    with json_path.open('x',encoding='utf-8',newline='\n') as target:
        json.dump(facts,target,ensure_ascii=False,indent=2)
        target.write('\n')
    print(json.dumps({'image':str(image_path),'log':str(json_path),'sha256':facts['capture']['sha256'],
                      'node':facts['node'],'time':facts['collector_time_end']},ensure_ascii=False))

if __name__ == '__main__':
    main()
