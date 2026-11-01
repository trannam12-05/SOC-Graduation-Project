"""Gui phim dieu huong installer Primary va chup framebuffer that.

Chi dung sau khi da xem man hinh hien tai va xac minh buoc tiep theo.
Khong nhan chuoi dang nhap/mat khau; khong sua QCOW2 tu host.
Enter o man hinh xac nhan phan vung la thao tac ghi o trong guest:
phai co backup va da doi chieu vtbd0, khong tu dong chay chuoi dai.
"""
import argparse
import json
import sys
import capture_m2_core_console as capture

KEYS = {"Enter": 0xff0d, "Down": 0xff54, "Up": 0xff52,
        "Left": 0xff51, "Right": 0xff53, "Tab": 0xff09,
        "Space": 0x20, "Escape": 0xff1b}

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("keys", nargs="+", choices=KEYS)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--label", required=True)
    args = p.parse_args()
    assert len(args.keys) <= 6, "Review each installer screen"
    capture.REMOTE = capture.REMOTE.replace(
        "n.get('name') == 'SOC-Core-L2'", "n.get('name') == 'OPNsense-Primary'")
    capture.REMOTE = capture.REMOTE.replace("facts['qemu'] = processes[0]",
        "assert node.get('uuid') == 'fe606d13-1542-490b-b651-5c1c6289afde'\nfacts['qemu'] = processes[0]")
    marker = "    pixel_format = struct.pack"
    assert capture.REMOTE.count(marker) == 1
    injection = "    facts['installer_keys'] = " + repr(args.keys) + "\n"
    injection += "    for key in " + repr([KEYS[k] for k in args.keys]) + ":\n"
    injection += "        sock.sendall(struct.pack('>BBHI',4,1,0,key) + struct.pack('>BBHI',4,0,0,key))\n        time.sleep(0.4)\n    time.sleep(2)\n"
    capture.REMOTE = capture.REMOTE.replace(marker, injection + marker)
    sys.argv = [sys.argv[0], "--output-dir", args.output_dir, "--label", args.label]
    capture.main()
