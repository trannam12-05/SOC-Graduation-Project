"""Dùng Git Credential Manager trong bộ nhớ; không in/lưu token vào tệp hoặc URL.

Chỉ hỗ trợ tài khoản/repository đích đã được người dùng chỉ định.
create-private xác minh owner, visibility; không đổi repo public thành private.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

OWNER='trannam12-05'
NAME='SOC-Graduation-Project'
ROOT=Path(__file__).resolve().parents[1]

def credential():
    result=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\nusername='+OWNER+'\n\n',
       capture_output=True,text=True,timeout=25,env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GCM_INTERACTIVE':'Never'})
    values=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
    if result.returncode or not values.get('password'):raise RuntimeError('Không có thông tin xác thực GitHub cục bộ khả dụng; không yêu cầu/in token.')
    return values['password']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['verify','create-private'])
    options=parser.parse_args();token=credential()
    def api(path,body=None):
        request=urllib.request.Request('https://api.github.com'+path,
           data=json.dumps(body).encode() if body is not None else None,
           headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
                    'User-Agent':'SOC-Project-Backup','X-GitHub-Api-Version':'2022-11-28'},
           method='POST' if body is not None else 'GET')
        with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
    user=api('/user');assert user['login']==OWNER,'Sai tài khoản GitHub; dừng.'
    created=False
    try:repo=api('/repos/'+OWNER+'/'+NAME)
    except urllib.error.HTTPError as exc:
        if exc.code!=404 or options.action!='create-private':raise RuntimeError('Chưa xác minh được repository, HTTP '+str(exc.code)) from None
        repo=api('/user/repos',{'name':NAME,'private':True,'auto_init':False,
             'description':'Đồ án SOC: Ubuntu Open vSwitch Layer 2, OPNsense HA và minh chứng triển khai.'})
        created=True
    repo=api('/repos/'+OWNER+'/'+NAME)
    assert repo['owner']['login']==OWNER and repo['name']==NAME
    assert repo['private'] is True and repo['visibility']=='private','Repository chưa private; không commit/push.'
    assert repo.get('permissions',{}).get('push') is True,'Chưa có quyền push.'
    safe={'owner':OWNER,'name':NAME,'url':repo['html_url'],'clone_url':repo['clone_url'],
          'private':repo['private'],'visibility':repo['visibility'],'push_permission':True,
          'created_in_this_call':created,'default_branch':repo['default_branch']}
    destination=ROOT/'staging/github-backup';destination.mkdir(parents=True,exist_ok=True)
    (destination/'repository-verified.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(safe,ensure_ascii=False))

if __name__=='__main__':main()
