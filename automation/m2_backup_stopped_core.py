"""Run on EVE: copy only stopped Core overlay; no guest appliance or image writes."""
import datetime as dt
import glob
import hashlib
import json
import os
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

UUID = b'2b295168-b72e-4de7-b364-37298252dd9f'
LAB = Path('/opt/unetlab/labs/SOC-M2-Core-L2.unl')


def stopped():
    for path in glob.glob('/proc/[0-9]*/cmdline'):
        try:
            args = Path(path).read_bytes().split(b'\0')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        assert not (args and b'qemu-system' in args[0] and UUID in args), 'Core running; refuse backup'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    stopped()
    root = ET.parse(LAB).getroot()
    n = root.find('.//node')
    assert n.get('uuid').encode() == UUID and n.get('id') == '3'
    source = Path('/opt/unetlab/tmp/0') / root.get('id') / '3/virtioa.qcow2'
    assert source.is_file() and source.stat().st_size < 3 * 1024**3
    destination = Path('/root') / ('m2-stopped-backup-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    assert shutil.disk_usage('/root').free > source.stat().st_size + 2 * 1024**3
    destination.mkdir(mode=0o700)
    metadata = {'source': str(source), 'destination': str(destination),
                'clock': 'EVE UTC untrusted; use collector receipt time',
                'method': 'Stopped overlay byte copy; no writes to source QCOW2',
                'overlay_bytes': source.stat().st_size, 'overlay_sha256_before': sha(source)}
    stopped()
    with source.open('rb') as reader, (destination/'core-overlay.qcow2').open('xb') as writer:
        shutil.copyfileobj(reader, writer, 8 * 1024**2)
    os.chmod(destination/'core-overlay.qcow2', 0o600)
    stopped()
    metadata['overlay_sha256_after'] = sha(source)
    metadata['backup_sha256'] = sha(destination/'core-overlay.qcow2')
    assert len({metadata[k] for k in ['overlay_sha256_before','overlay_sha256_after','backup_sha256']}) == 1
    shutil.copy2(LAB, destination/'lab-before.unl')
    metadata['lab_sha256'] = sha(LAB)
    metadata['protected'] = {}
    for path in [Path('/opt/unetlab/addons/qemu/linux-ubuntu-24.04-soc-core-l2/virtioa.qcow2'),
                 *source.parent.glob('*.iso')]:
        metadata['protected'][str(path)] = sha(path)
    metadata['rollback_note'] = 'Restore overlay only after verified node shutdown, retaining current overlay as another backup; never overwrite running disk or original image. Online OVSDB rollback preferred for OVS-only changes.'
    (destination/'metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(metadata))


if __name__ == '__main__':
    main()
