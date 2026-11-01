"""Run on EVE as root after guest backup/verification, never on Windows.

Inject synthetic Ethernet into separate existing Core TAPs; no bridges, links,
addresses, images or VM lifecycle changes. Captures only this run's marker.
Execution requires --guest-ready after the operator verifies guest configuration.
No self-test or dry-run output constitutes switching evidence.
"""
import argparse
import datetime as dt
import glob
import json
import os
from pathlib import Path
import select
import socket
import struct
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET

TAPS = ['vunl0_3_' + str(i) for i in range(8)]
VLANS = [30, 40, 50, 60, 99]
LAB = '/opt/unetlab/labs/SOC-M2-Core-L2.unl'
UUID = '2b295168-b72e-4de7-b364-37298252dd9f'


def guard():
    root = ET.parse(LAB).getroot()
    nodes = root.findall('.//node')
    assert len(nodes) == 1 and nodes[0].get('name') == 'SOC-Core-L2'
    assert nodes[0].get('uuid') == UUID and nodes[0].get('id') == '3'
    assert not root.findall('.//network') and not nodes[0].findall('interface')
    matches = []
    for path in glob.glob('/proc/[0-9]*/cmdline'):
        try:
            args = Path(path).read_bytes().split(b'\0')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if args and b'qemu-system-x86_64' in args[0] and UUID.encode() in args:
            matches.append([x.decode() for x in args if x])
    assert len(matches) == 1, 'Expected exactly one designated Core VM'
    args = matches[0]
    for i, tap in enumerate(TAPS):
        assert any('ifname=' + tap + ',' in a for a in args), 'Unexpected QEMU TAP'
        assert any('mac=02:53:45:f2:19:' + format(i, '02x') in a.lower() for a in args)
    links = json.loads(subprocess.check_output(['ip', '-j', 'link', 'show']))
    selected = [x for x in links if x['ifname'] in TAPS]
    assert len(selected) == 8
    assert all(not x.get('master') and 'UP' in x['flags'] for x in selected)
    assert all(not (Path('/sys/class/net') / tap / 'master').exists() for tap in TAPS)
    return {'qemu_args': args, 'links': selected}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--guest-ready', action='store_true', required=True)
    p.add_argument('--mirror', action='store_true', help='Only after ens10 mirror verified')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert os.geteuid() == 0
    initial = guard()
    a.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    sockets = {}
    for tap in TAPS:
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
        s.setsockopt(263, 8, 1)  # SOL_PACKET, PACKET_AUXDATA: detect VLAN offload
        s.bind((tap, 0))
        s.setblocking(False)
        sockets[s] = tap
    by_tap = {name: s for s, name in sockets.items()}
    run_id = uuid.uuid4().hex
    marker = ('SOC-M2-' + run_id + '-').encode()
    captures = {tap: (a.output / (tap + '.pcap')).open('xb') for tap in TAPS}
    for f in captures.values():
        f.write(struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))
    events = []
    results = []

    def receive(seconds, test_marker=None):
        deadline = time.monotonic() + seconds
        found = []
        while time.monotonic() < deadline:
            ready, _, _ = select.select(list(sockets), [], [], max(0, deadline - time.monotonic()))
            for s in ready:
                frame, ancillary, _, addr = s.recvmsg(65535, 1024)
                if marker not in frame or addr[2] == 4:  # exclude PACKET_OUTGOING injection
                    continue
                for level, kind, value in ancillary:
                    if level == 263 and kind == 8 and len(value) >= 20:
                        status, _, _, _, _, tci, tpid = struct.unpack('=IIIHHHH', value[:20])
                        if status & (1 << 4):  # TP_STATUS_VLAN_VALID
                            frame = frame[:12] + struct.pack('!HH', tpid if status & (1 << 6) else 0x8100, tci) + frame[12:]
                stamp = time.time()
                sec = int(stamp)
                captures[sockets[s]].write(struct.pack('<IIII', sec, int((stamp-sec)*1000000), len(frame), len(frame)) + frame)
                vlan = struct.unpack('!H', frame[14:16])[0] & 4095 if frame[12:14] == b'\x81\x00' else None
                event = {'time_untrusted': stamp, 'tap': sockets[s], 'vlan': vlan,
                         'packet_type': addr[2], 'hex': frame.hex()}
                events.append(event)
                if test_marker and test_marker in frame:
                    found.append(event)
        return found

    def case(name, ingress, vlan, expected, mirror=False, destination=None):
        receive(0.03)
        token = marker + name.encode() + b'!'
        src = bytes.fromhex('02534f4300' + format(ingress, '02x'))
        frame = (destination if destination is not None else b'\xff'*6) + src
        frame += struct.pack('!HHH', 0x8100, vlan, 0x88b5) if vlan is not None else b'\x88\xb5'
        frame = (frame + token).ljust(128, b'.')
        tx_at = dt.datetime.now(dt.timezone.utc).isoformat()
        count = by_tap[TAPS[ingress]].send(frame)
        assert count == len(frame)
        observed = receive(0.5, token)
        actual = {(e['tap'], e['vlan']) for e in observed if e['tap'] != TAPS[7]}
        wanted = {(TAPS[i], v) for i, v in expected.items()}
        mirror_events = [e for e in observed if e['tap'] == TAPS[7]]
        ok = actual == wanted and bool(mirror_events) == mirror
        result = {'case': name, 'tx_time_untrusted': tx_at, 'ingress': TAPS[ingress],
                  'tx_vlan': vlan, 'tx_hex': frame.hex(), 'expected': sorted(wanted, key=str),
                  'observed': sorted(actual, key=str), 'mirror_frames': len(mirror_events),
                  'status': 'PASS' if ok else 'FAIL', 'received': observed}
        results.append(result)
        print(name, result['status'], flush=True)

    try:
        # Positive delivery and negative cross-VLAN observations in every case.
        for i, vlan in enumerate(VLANS):
            case('access-' + str(vlan), i, None, {5: vlan, 6: vlan}, a.mirror)
        for trunk in [5, 6]:
            for i, vlan in enumerate(VLANS):
                case('trunk' + str(trunk) + '-' + str(vlan), trunk, vlan,
                     {i: None, 11-trunk: vlan}, a.mirror)
            case('trunk' + str(trunk) + '-denied100', trunk, 100, {})
            case('trunk' + str(trunk) + '-untagged', trunk, None, {})
        case('access30-wrongtag40', 0, 40, {})
        for i, vlan in enumerate(VLANS):
            case('known-unicast-trunk-to-access-' + str(vlan), 5, vlan,
                 {i: None}, a.mirror, bytes.fromhex('02534f4300' + format(i, '02x')))
            case('known-unicast-access-to-trunk-' + str(vlan), i, None,
                 {5: vlan}, a.mirror, bytes.fromhex('02534f430005'))
        if a.mirror:
            case('mirror-no-ingress-switching', 7, 30, {})
        case('positive-control-final', 0, None, {5: 30, 6: 30}, a.mirror)
    finally:
        for f in captures.values():
            f.close()
        for s in sockets:
            s.close()
        try:
            final = guard()
            guard_error = None
        except Exception as exc:
            final = None
            guard_error = str(exc)
        report = {'run_id': run_id, 'method': 'AF_PACKET separate TAP injection; guest egress only; no host bridge',
                  'mirror_enabled_expected': a.mirror, 'initial': initial, 'final': final, 'final_guard_error':guard_error,
                  'cases': results, 'events': events, 'clock': 'EVE time untrusted; collector must timestamp receipt',
                  'limitations': 'Synthetic L2 broadcast tests, not IP routing, unicast performance, reboot or HA tests'}
        (a.output/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    assert not guard_error and results and all(r['status'] == 'PASS' for r in results), 'Frame test failed; inspect evidence'


if __name__ == '__main__':
    main()
