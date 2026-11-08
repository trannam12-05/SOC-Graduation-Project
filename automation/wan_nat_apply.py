"""Thêm đúng FW/SNAT một nguồn/đích, filter reload; giữ nguyên HA/hook và rule cũ."""
import pathlib,subprocess,json,hashlib,xml.etree.ElementTree as E,re,os
os.umask(0o077)
work=pathlib.Path('/root/soc-m3-wan-nat-20261106');before=pathlib.Path('/conf/config.xml').read_bytes();backup=work/'config.before-nat.xml'
assert not backup.exists(),'NAT stage already attempted; inspect before retry'
backup.write_bytes(before);backup.chmod(0o600)
root=E.fromstring(before)
def canonical(n):return None if n is None else [n.tag,sorted(n.attrib.items()),(n.text or '').strip(),[canonical(x) for x in n]]
protected={p:canonical(root.find(p)) for p in ['interfaces','virtualip','hasync']}
oldrules={n.get('uuid'):canonical(n) for n in root.findall('./OPNsense/Firewall/Filter/rules/rule')}
def run(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=45);return {'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
php=r'''<?php
require_once('/usr/local/etc/inc/config.inc');
$fw=new \OPNsense\Firewall\Filter();
foreach($fw->rules->rule->iterateItems() as $r)if((string)$r->description==='SOC M3 NAT EMPLOYEE HTTPS')throw new Exception('Existing rule; stop');
foreach($fw->snatrules->rule->iterateItems() as $r)if((string)$r->description==='SOC M3 SNAT EMPLOYEE HTTPS')throw new Exception('Existing SNAT; stop');
$r=$fw->rules->rule->Add();$r->setNodes(['enabled'=>'1','action'=>'pass','quick'=>'1','interface'=>'opt2','direction'=>'in','ipprotocol'=>'inet','protocol'=>'tcp','source_net'=>'192.168.40.110/32','destination_net'=>'1.1.1.1/32','destination_port'=>'443','log'=>'1','sequence'=>'320','description'=>'SOC M3 NAT EMPLOYEE HTTPS']);
$s=$fw->snatrules->rule->Add();$s->setNodes(['enabled'=>'1','sequence'=>'1','interface'=>'wan','ipprotocol'=>'inet','protocol'=>'tcp','source_net'=>'192.168.40.110/32','destination_net'=>'1.1.1.1/32','destination_port'=>'443','target'=>'','staticnatport'=>'0','log'=>'1','description'=>'SOC M3 SNAT EMPLOYEE HTTPS']);
$errors=[];foreach($fw->performValidation() as $e)$errors[]=['field'=>$e->getField(),'message'=>$e->getMessage()];
if($errors){echo json_encode(['status'=>'VALIDATION_FAILED','errors'=>$errors]);exit(2);}
$fw->serializeToConfig();$cfg=\OPNsense\Core\Config::getInstance();$cfg->object()->nat->outbound->mode='hybrid';$cfg->save();
echo json_encode(['status'=>'SAVED','mode'=>'hybrid','target'=>'egress interface address (empty target)','scope'=>'192.168.40.110/32 -> 1.1.1.1/32 TCP443']);
?>'''
p=work/'apply-nat.php';p.write_text(php);p.chmod(0o600)
steps=[];failed=None;after=None
try:
 for a in [['/usr/local/bin/php','-l',str(p)],['/usr/local/bin/php',str(p)]]:
  x=run(a);steps.append(x);assert x['rc']==0,x
 after=pathlib.Path('/conf/config.xml').read_bytes();rr=E.fromstring(after)
 assert all(canonical(rr.find(p))==v for p,v in protected.items()),'Protected HA/interfaces changed'
 for uid,n in oldrules.items():assert canonical(rr.find("./OPNsense/Firewall/Filter/rules/rule[@uuid='"+uid+"']"))==n,'Existing rule changed'
 assert rr.findtext('nat/outbound/mode')=='hybrid'
 x=run(['/usr/local/sbin/configctl','filter','reload']);steps.append(x);assert x['rc']==0,x
 fw=run(['/sbin/pfctl','-sr']);nat=run(['/sbin/pfctl','-sn'])
 newrule=next(n for n in rr.findall('./OPNsense/Firewall/Filter/rules/rule') if n.findtext('description')=='SOC M3 NAT EMPLOYEE HTTPS')
 newnat=next(n for n in rr.findall('./OPNsense/Firewall/Filter/snatrules/rule') if n.findtext('description')=='SOC M3 SNAT EMPLOYEE HTTPS')
 assert newrule.get('uuid') in fw['stdout'],'Firewall UUID not loaded'
 matches=[s for s in nat['stdout'].splitlines() if '192.168.40.110' in s and '1.1.1.1' in s]
 assert matches and any('vtnet1' in s and ('443' in s or 'https' in s) for s in matches),'Exact SNAT not loaded'
 d={'status':'APPLIED','backup':str(backup),'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(after).hexdigest(),'steps':steps,'firewall_uuid':newrule.get('uuid'),'snat_uuid':newnat.get('uuid'),'nat_runtime':matches,'firewall_runtime':[s for s in fw['stdout'].splitlines() if newrule.get('uuid') in s],'protected_unchanged':True,'old_rules_unchanged':True}
 (work/'nat-apply-result.json').write_text(json.dumps(d,indent=2))
except Exception as e:
 failed=str(e);current=pathlib.Path('/conf/config.xml').read_bytes()
 if current!=before:
  assert after is not None and current==after,'Config differs from owned after-image; stop for targeted rollback, do not overwrite'
  snapshot=work/'config.failed-nat.xml';snapshot.write_bytes(current);snapshot.chmod(0o600)
  # Use guarded atomic byte restore of our baseline; do not invoke HA services.
  assert pathlib.Path('/conf/config.xml').read_bytes()==current,'Concurrent config change; do not restore'
  tmp=pathlib.Path('/conf/config.soc-rollback.xml');tmp.write_bytes(before);tmp.chmod(0o600);os.chown(tmp,pathlib.Path('/conf/config.xml').stat().st_uid,pathlib.Path('/conf/config.xml').stat().st_gid);os.replace(tmp,'/conf/config.xml')
  steps.append(run(['/usr/local/sbin/configctl','filter','reload']))
 d={'status':'FAILED_ROLLED_BACK','error':failed,'steps':steps,'config_restored':pathlib.Path('/conf/config.xml').read_bytes()==before}
 (work/'nat-apply-result.json').write_text(json.dumps(d,indent=2))
