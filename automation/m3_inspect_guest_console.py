"""Chan doan chi doc trong shell Primary da xac thuc; khong cai dat/doi mang.

Phai xem anh console va xac nhan dau nhac shell root truoc khi dung.
Chi cac lenh co dinh khong chua bi mat; framebuffer va lenh duoc luu that.
"""
import argparse
from pathlib import Path
import sys
import capture_m2_core_console as capture

COMMANDS = {
    "disk": "gpart show vtbd0; diskinfo vtbd0; mount | head -5",
    "nics": "ifconfig vtnet0; ifconfig vtnet1; ifconfig vtnet2",
    "nic-summary": "ifconfig -a | grep -E '(^vtnet|ether |description:|inet )'",
    "nic-mac": "echo vtnet0; ifconfig vtnet0 | grep ether; echo vtnet1; ifconfig vtnet1 | grep ether; echo vtnet2; ifconfig vtnet2 | grep ether",
    "version": "opnsense-version; df -h; sysctl hw.physmem",
    "config-api": "command -v python3; ls /usr/local/etc/inc/config.inc; grep -n '^function interface_' /usr/local/etc/inc/interfaces.inc | head -12",
    "vlan-api": "grep -n 'function.*vlan' /usr/local/etc/inc/interfaces.inc; grep -n 'function.*configure' /usr/local/etc/inc/interfaces.inc | tail -8; ls /usr/local/opnsense/mvc/app/models/OPNsense/Interfaces",
    "vlan-schema": "head -22 /usr/local/opnsense/mvc/app/models/OPNsense/Interfaces/Vlan.xml",
    "vlan-runtime-api": "sed -n '110,128p' /usr/local/etc/inc/interfaces.inc",
    "interface-entry": "grep -n 'function interface[s]*_configure' /usr/local/etc/inc/interfaces.inc; tail -35 /usr/local/opnsense/mvc/app/models/OPNsense/Interfaces/Vlan.xml",
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=COMMANDS)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    source = args.output_dir / ("command-" + args.check + ".txt")
    if source.exists():
        assert source.read_text(encoding="utf-8") == COMMANDS[args.check]
    else:
        source.write_text(COMMANDS[args.check], encoding="utf-8")
    needle = "n.get('name') == 'SOC-Core-L2'"
    assert capture.REMOTE.count(needle) == 1
    capture.REMOTE = capture.REMOTE.replace(needle, "n.get('name') == 'OPNsense-Primary'")
    sys.argv = [sys.argv[0], "--output-dir", str(args.output_dir),
                "--label", "primary-" + args.check, "--command-file", str(source)]
    capture.main()
