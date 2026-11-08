"""Endpoint Linux thật: namespace VLAN40 qua NIC riêng; chỉ thử HTTP lab được duyệt."""
import datetime, hashlib, http.client, json, os, pathlib, subprocess, sys, time
SESSION='soc-m2-final-20261103'
BASE=pathlib.Path('/var/tmp')/SESSION
def run(a,timeout=15):
 p=subprocess.run(a,text=True,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError(repr(a)+': '+p.stderr)
 return p.stdout
def request(ip,dst,port,path='/'):
 c=http.client.HTTPConnection(dst,port,timeout=6,source_address=(ip,0))
 try:
  c.request('GET',path,headers={'Connection':'close','X-SOC-M2-Test':SESSION})
  r=c.getresponse();body=r.read()
  return {'result':'HTTP_RESPONSE','status':r.status,'reason':r.reason,'headers':r.getheaders(),'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'body_text':body.decode(errors='replace')[:500]}
 except Exception as e:return {'result':'NO_HTTP_RESPONSE','error_type':type(e).__name__,'error':str(e)}
 finally:c.close()
def emit(d):
 text=json.dumps(d,separators=(',',':'))
 (BASE/'result.json').write_text(text)
 print('SOC_M2_RESULT '+text,flush=True)
 with open('/dev/ttyS0','w') as f:f.write('SOC_M2_RESULT '+text+'\n')
assert os.geteuid()==0
BASE.mkdir(mode=0o700,exist_ok=False)
d={'session':SESSION,'scope':'Real HTTP via isolated VLAN40 Linux namespace, no firewall edits','start_guest_utc_untrusted':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':[]}
try:
 before=json.loads(run(['ip','-j','address','show']))
 routes=json.loads(run(['ip','-j','route','show']))
 (BASE/'network-before.json').write_text(json.dumps({'interfaces':before,'routes':routes}))
 d['server_interfaces_before']=before;d['server_routes_before']=routes
 assert any(a.get('local')=='192.168.30.10' and a.get('prefixlen')==24 for n in before for a in n.get('addr_info',[]))
 assert any(x.get('dst')=='default' and x.get('gateway')=='192.168.30.2' for x in routes)
 nic=next(n for n in before if n.get('address')=='02:54:bc:2f:0c:01')
 assert not nic.get('addr_info'), 'New client NIC already has addresses; inspect first'
 assert not run(['ip','netns','list']).strip(),'Existing namespaces; do not overwrite'
 run(['ip','netns','add','m2-client40'])
 run(['ip','link','set',nic['ifname'],'netns','m2-client40'])
 prefix=['ip','netns','exec','m2-client40']
 run(prefix+['ip','link','set',nic['ifname'],'name','client0'])
 run(prefix+['ip','link','set','lo','up']);run(prefix+['ip','link','set','client0','up'])
 run(prefix+['ip','address','add','192.168.40.100/24','dev','client0'])
 run(prefix+['ip','route','add','default','via','192.168.40.2'])
 d['client_interfaces']=json.loads(run(prefix+['ip','-j','address','show']))
 d['client_routes']=json.loads(run(prefix+['ip','-j','route','show']))
 d['client_route_to_dc']=json.loads(run(prefix+['ip','-j','route','get','192.168.30.10']))
 d['server_route_to_client']=json.loads(run(['ip','-j','route','get','192.168.40.100']))
 d['server_unit_active']=run(['systemctl','is-active','soc-lab-http.service']).strip()
 d['server_unit_enabled']=run(['systemctl','is-enabled','soc-lab-http.service']).strip()
 d['server_listener']=run(['ss','-lntp'])
 helper=BASE/'http-request.py'
 helper.write_text('''import sys,json,http.client,hashlib
c=http.client.HTTPConnection(sys.argv[2],int(sys.argv[3]),timeout=6,source_address=(sys.argv[1],0))
try:
 c.request('GET',sys.argv[4],headers={'Connection':'close'})
 r=c.getresponse();b=r.read()
 d={'result':'HTTP_RESPONSE','status':r.status,'reason':r.reason,'headers':r.getheaders(),'body_bytes':len(b),'body_sha256':hashlib.sha256(b).hexdigest(),'body_text':b.decode(errors='replace')[:500]}
except Exception as e:d={'result':'NO_HTTP_RESPONSE','error_type':type(e).__name__,'error':str(e)}
finally:c.close()
print(json.dumps(d))
''')
 pos=json.loads(run(prefix+['python3',str(helper),'192.168.40.100','192.168.30.10','8000','/?soc_m2='+SESSION],timeout=12))
 d['cases'].append({'name':'positive40_to30','source':'192.168.40.100','destination':'192.168.30.10','port':8000,'expected':'HTTP200','observed':pos,'pass':pos.get('status')==200 and 'SOC Data-Center' in pos.get('body_text','')})
 # Sai nguồn: cùng dịch vụ đã có đối chứng dương, không đổi rule.
 run(prefix+['ip','address','del','192.168.40.100/24','dev','client0'])
 run(prefix+['ip','address','add','192.168.40.101/24','dev','client0'])
 run(prefix+['ip','route','replace','default','via','192.168.40.2'])
 neg=json.loads(run(prefix+['python3',str(helper),'192.168.40.101','192.168.30.10','8000','/?soc_m2=negative-source'],timeout=12))
 d['cases'].append({'name':'negative_wrong_source','source':'192.168.40.101','destination':'192.168.30.10','port':8000,'expected':'DENY','observed':neg,'client_result_only':neg.get('error_type')=='TimeoutError'})
 run(prefix+['ip','address','del','192.168.40.101/24','dev','client0'])
 run(prefix+['ip','address','add','192.168.40.100/24','dev','client0'])
 run(prefix+['ip','route','replace','default','via','192.168.40.2'])
 # Server đối chứng tạm trong namespace để thử kết nối mới DC -> Employee bị deny.
 log=(BASE/'client-temp-http.log').open('w')
 p=subprocess.Popen(prefix+['python3','-m','http.server','8001','--bind','192.168.40.100','--directory','/var/www/soc-lab'],stdout=log,stderr=log)
 try:
  time.sleep(1)
  local=json.loads(run(prefix+['python3',str(helper),'192.168.40.100','192.168.40.100','8001','/'],timeout=12))
  reverse=request('192.168.30.10','192.168.40.100',8001,'/?soc_m2=negative-reverse')
  d['cases'].append({'name':'negative_reverse_new_flow','source':'192.168.30.10','destination':'192.168.40.100','port':8001,'expected':'DENY','local_server_control':local,'observed':reverse,'client_result_only':local.get('status')==200 and reverse.get('error_type')=='TimeoutError'})
 finally:p.terminate();p.wait(timeout=5);log.close()
 d['server_http_log_tail']=run(['journalctl','-u','soc-lab-http.service','-n','8','--no-pager'])
 d['client_final_ip']=json.loads(run(prefix+['ip','-j','address','show','client0']))
 d['state']='CLIENT_TESTS_COMPLETED_REQUIRE_PACKET_FIREWALL_CORRELATION'
except Exception as e:
 d['state']='ERROR';d['error_type']=type(e).__name__;d['error']=str(e)
emit(d)
