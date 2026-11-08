"""Mở monitor QEMU của Core qua hotkey để kiểm tra trước ACPI powerdown."""
import sys
import capture_m2_core_console as c
marker='    pixel_format = struct.pack'
injection='''    for k in [0xffe3,0xffe9,0x32]:
        sock.sendall(struct.pack('>BBHI',4,1,0,k));time.sleep(0.15)
    for k in [0x32,0xffe9,0xffe3]:
        sock.sendall(struct.pack('>BBHI',4,0,0,k));time.sleep(0.15)
    time.sleep(1)
'''
c.REMOTE=c.REMOTE.replace(marker,injection+marker)
sys.argv=[sys.argv[0],'--output-dir','docs/evidence/M2/resume-20261102','--label','core-qemu-monitor-before-acpi']
c.main()
