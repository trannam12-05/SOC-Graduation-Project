"""Tạo duy nhất Employee-Linux theo phê duyệt; không sửa WAN/HA hoặc VPCS."""
import pathlib,subprocess,json,uuid,os,hashlib,datetime,shutil,xml.etree.ElementTree as E
bundle=json.loads(BUNDLE)
lab=pathlib.Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl');raw=lab.read_bytes();root=E.fromstring(raw)
assert not any(n.get('name')=='Employee-Linux' for n in root.findall('.//node'))
assert any(n.get('name')=='Employee' and n.get('type')=='vpcs' for n in root.findall('.//node'))
assert any(n.get('id')=='7' and n.get('name')=='VLAN40-Employee' for n in root.findall('.//network')), 'Verify VLAN40 segment name'
mem={s.split(':')[0]:int(s.split()[1]) for s in pathlib.Path('/proc/meminfo').read_text().splitlines() if len(s.split())>1 and s.split()[1].isdigit()}
assert mem['MemAvailable']>(1024+1536)*1024, 'Insufficient memory reserve'
running=[]
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:
  a=[s.decode(errors='replace') for s in p.read_bytes().split(b'\0') if s]
  if a and 'qemu-system-' in a[0]:running.append({'pid':p.parent.name,'name':a[a.index('-name')+1],'ram':int(a[a.index('-m')+1])})
 except (OSError,ValueError):pass
assert sum(n['ram'] for n in running)+1024+1536<mem['MemTotal']//1024
work=pathlib.Path('/root/soc-employee-linux-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'));work.mkdir(mode=0o700)
shutil.copy2(lab,work/'lab-before.unl');(work/'lab-before.unl').chmod(0o600)
image=pathlib.Path('/opt/unetlab/addons/qemu/linux-soc-employee-20261106');assert not image.exists();image.mkdir(mode=0o755)
base='/opt/unetlab/addons/qemu/linux-ubuntu-24.04-ovs/virtioa.qcow2'
subprocess.run(['/opt/qemu-2.12.0/bin/qemu-img','create','-f','qcow2','-F','qcow2','-b',base,str(image/'virtioa.qcow2')],check=True,capture_output=True)
ident=str(uuid.uuid4());mac='02:55:'+':'.join(ident.replace('-','')[i:i+2] for i in range(0,8,2))
seed=work/'seed';seed.mkdir(mode=0o700)
config={'hostname':'employee-linux','preserve_hostname':False,'disable_root':True,'ssh_pwauth':False,'users':[{'name':'soc-admin','shell':'/bin/bash','groups':['adm','sudo'],'lock_passwd':True,'sudo':['ALL=(ALL) NOPASSWD:ALL']}],'package_update':False,'package_upgrade':False,'write_files':[{'path':'/opt/soc/employee_readiness.py','content':bundle['readiness'],'permissions':'0700'},{'path':'/etc/systemd/system/getty@tty1.service.d/soc-console.conf','content':'[Service]\nExecStart=\nExecStart=-/sbin/agetty --autologin soc-admin --noclear %I $TERM\n'}],'runcmd':[['systemctl','daemon-reload'],['systemctl','restart','getty@tty1.service'],['python3','/opt/soc/employee_readiness.py']]}
network={'version':2,'ethernets':{'employee0':{'match':{'macaddress':mac},'set-name':'employee0','dhcp4':True,'dhcp6':False,'accept-ra':False,'link-local':[]}}}
(seed/'user-data').write_text('#cloud-config\n'+json.dumps(config));(seed/'network-config').write_text(json.dumps(network));(seed/'meta-data').write_text(json.dumps({'instance-id':'iid-employee-'+ident,'local-hostname':'employee-linux'}))
subprocess.run(['genisoimage','-quiet','-volid','cidata','-joliet','-rock','-o',str(image/'cdrom.iso'),str(seed)],check=True,capture_output=True)
for p in image.iterdir():os.chown(p,33,33);p.chmod(0o600)
os.chown(image,33,33)
nodeid=str(max(int(n.get('id')) for n in root.findall('.//node'))+1)
attrs={'id':nodeid,'name':'Employee-Linux','type':'qemu','template':'linux','image':image.name,'console':'vnc','cpu':'1','cpulimit':'1','ram':'1024','ethernet':'1','uuid':ident,'firstmac':mac,'qemu_options':'-machine type=pc,accel=kvm -vga std -usbdevice tablet -boot order=c -cpu host -serial file:serial.log','qemu_version':'2.12.0','qemu_arch':'x86_64','qemu_nic':'virtio-net-pci','delay':'0','icon':'Server-2D-Linux-S.svg','config':'0','left':'420','top':'710'}
node=E.Element('node',attrs);E.SubElement(node,'interface',{'id':'0','name':'eth0','type':'ethernet','network_id':'7'})
assert raw.count(b'</nodes>')==1;new=raw.replace(b'</nodes>',E.tostring(node)+b'\n</nodes>')
assert lab.read_bytes()==raw,'Concurrent topology change'
tmp=lab.with_suffix('.employee-new');tmp.write_bytes(new);shutil.copystat(lab,tmp);os.chown(tmp,lab.stat().st_uid,lab.stat().st_gid);os.replace(tmp,lab)
p=subprocess.run(['/opt/unetlab/wrappers/unl_wrapper','-a','start','-T','0','-F',str(lab),'-D',nodeid],capture_output=True,text=True,timeout=45)
d={'backup':str(work/'lab-before.unl'),'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(new).hexdigest(),'node':attrs,'network':network,'running_before':running,'memory_before':{k:mem[k] for k in ['MemTotal','MemAvailable']},'start':{'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr},'scope':'Only new Employee-Linux overlay/seed/node; existing XML nodes/links preserved byte-for-byte; WAN/HA not changed'}
(work/'create-result.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
