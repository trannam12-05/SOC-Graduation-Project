"""Chạy bằng sudo python3 trong ĐÚNG Ubuntu guest; chưa được chạy trong phiên tiếp quản.

Chỉ cài OVS offline; không tạo bridge, VLAN, địa chỉ IP hay sửa kết nối vNIC.
Yêu cầu tệp m2-ovs-expected.json cùng thư mục (tạo từ manifest Windows đã kiểm tra).
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

VERSION = '3.3.9-0ubuntu0.24.04.1'
REPO = Path('/opt/ovs-offline')

def main():
    if os.geteuid() != 0:
        raise SystemExit('Chạy sudo python3; tự nhập mật khẩu trên console, không đưa vào lệnh/log.')
    if subprocess.check_output(['hostname'], text=True).strip() != 'soc-core-l2':
        raise SystemExit('Sai hostname; dừng để tránh cài nhầm EVE host hoặc guest khác.')
    if subprocess.check_output(['dpkg','--print-architecture'], text=True).strip() != 'amd64':
        raise SystemExit('Sai kiến trúc guest.')
    expected = json.loads(Path(__file__).with_name('m2-ovs-expected.json').read_text())
    work = Path(tempfile.mkdtemp(prefix='m2-ovs-', dir='/var/tmp'))
    os.chmod(work, 0o755)  # _apt cần đọc source và chỉ mục; không chứa bí mật.
    log = (work/'execution.log').open('x', buffering=1)

    def say(text):
        print(text, flush=True)
        log.write(text+'\n')

    def run(args, required=True):
        say('$ '+' '.join(args))
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, env={**os.environ, 'LC_ALL':'C',
                                               'DEBIAN_FRONTEND':'noninteractive',
                                               'SYSTEMD_PAGER':'cat', 'PAGER':'cat'})
        say(result.stdout)
        say('RETURN_CODE='+str(result.returncode))
        if required and result.returncode:
            raise RuntimeError('Dừng khi lệnh thất bại; xem log, không tự sửa mạng hoặc downgrade.')
        return result

    try:
        say('UTC guest clock (not collector time): '+datetime.datetime.now(datetime.timezone.utc).isoformat())
        say('Evidence directory: '+str(work))
        for args in [['hostnamectl'], ['uname','-r'], ['ip','-j','link'], ['lsblk'],
                     ['df','-h','/'], ['cloud-init','status','--long'], ['dpkg','--audit']]:
            run(args)
        shutil.copy2('/var/lib/dpkg/status', work/'dpkg-status.before')
        source = Path('/etc/apt/sources.list.d/soc-ovs-offline.list')
        if source.exists():
            shutil.copy2(source, work/'soc-ovs-offline.list.before')
        # Kiểm tra lại byte trong guest, không suy rộng hash Windows sang guest.
        for item in expected['indexes'] + expected['packages']:
            path = REPO/item['path']
            with path.open('rb') as stream:
                actual = hashlib.file_digest(stream, 'sha256').hexdigest()
            if actual != item['sha256']:
                raise RuntimeError('SHA256 không khớp: '+str(path))
            say('SHA256 OK '+item['path'])
        if len(list((REPO/'pool').rglob('*.deb'))) != 70:
            raise RuntimeError('Số lượng deb trong guest khác 70; cần kiểm tra.')
        for suite in ['noble','noble-updates','noble-security']:
            release = REPO/'dists'/suite/'InRelease'
            run(['gpgv','--keyring','/usr/share/keyrings/ubuntu-archive-keyring.gpg',str(release)])
            signed = release.read_text()
            for item in expected['indexes']:
                if item['path'].startswith('dists/'+suite+'/'):
                    relative = item['path'].split('/',2)[2]
                    if not re.search(r'^\s*'+re.escape(item['sha256'])+r'\s+\d+\s+'+re.escape(relative)+r'$', signed, re.M):
                        raise RuntimeError('Index không gắn với InRelease đã ký: '+relative)
        for item in expected['packages']:
            result = run(['dpkg-deb','-f',str(REPO/item['path']), 'Package','Version','Architecture'])
            fields = dict(line.split(': ',1) for line in result.stdout.splitlines() if ': ' in line)
            if any(fields.get(key) != item[key] for key in ['Package','Version','Architecture']):
                raise RuntimeError('Deb control khác manifest: '+item['path'])
        sources = work/'offline.list'
        sources.write_text(''.join('deb [signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:/opt/ovs-offline '+s+' main universe\n' for s in ['noble','noble-updates','noble-security']))
        (work/'lists/partial').mkdir(parents=True)
        options = ['-o','Dir::Etc::sourcelist='+str(sources), '-o','Dir::Etc::sourceparts=-',
                   '-o','Dir::State::lists='+str(work/'lists'), '-o','Acquire::Languages=none',
                   '-o','Acquire::IndexTargets::deb::CNF::DefaultEnabled=false',
                   '-o','Acquire::IndexTargets::deb::DEP-11::DefaultEnabled=false',
                   '-o','APT::Get::List-Cleanup=0', '-o','Acquire::Retries=0']
        # Dùng signed-by thay trusted=yes; không sửa nguồn APT hệ thống hoặc đồng hồ.
        run(['apt-get',*options,'-o','APT::Update::Error-Mode=any','update'])
        run(['apt-cache',*options,'policy','openvswitch-switch','openvswitch-common','python3-openvswitch'])
        target = ['openvswitch-switch='+VERSION,'openvswitch-common='+VERSION,'python3-openvswitch='+VERSION]
        plan = run(['apt-get',*options,'--simulate','--no-install-recommends','--no-remove','install',*target])
        if re.search(r'^Remv ', plan.stdout, re.M):
            raise RuntimeError('Kế hoạch gỡ gói ngoài phạm vi.')
        allowed = {(p['Package'],p['Version']) for p in expected['packages']}
        for name, version in re.findall(r'^Inst (\S+)(?: \[[^\]]+\])? \((\S+)', plan.stdout, re.M):
            if (name.split(':')[0], version) not in allowed:
                raise RuntimeError('Dependency ngoài bundle: '+name+' '+version)
        # Chỉ source file:, không truy vấn Internet; APT tự chọn dependency cần thiết.
        run(['apt-get',*options,'--yes','--no-install-recommends','--no-remove','install',*target])
        run(['dpkg-query','-W','-f=${Package} ${Version} ${Status}\n',
             'openvswitch-switch','openvswitch-common','python3-openvswitch'])
        run(['ovs-vsctl','--version'])
        run(['systemctl','--no-pager','status','openvswitch-switch','ovsdb-server','ovs-vswitchd'])
        run(['systemctl','is-active','ovsdb-server','ovs-vswitchd'])
        run(['ovs-vsctl','--timeout=10','show'])
        run(['journalctl','--no-pager','-b','-u','openvswitch-switch','-u','ovsdb-server','-u','ovs-vswitchd','-p','warning'])
        run(['dpkg','--audit'])
        say('Cài và kiểm tra dịch vụ hoàn tất. CHƯA kiểm chứng VLAN/trunk/mirror hoặc chuyển tiếp dữ liệu.')
    except Exception as exc:
        say('FAILED: '+str(exc))
        raise
    finally:
        say('Giữ nguyên toàn bộ log/backup tại '+str(work))
        log.close()

if __name__ == '__main__':
    main()
