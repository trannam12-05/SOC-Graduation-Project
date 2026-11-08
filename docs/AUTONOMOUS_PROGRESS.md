# M2 đã nghiệm thu — 03/11/2026, UTC+07:00

Mốc mới nhất: [tổng kết M2](M2/M2-final-summary-20261103.md), [SOC TO DO](SOC_TO_DO.md). Sáu hạng mục có bảng PASS/N/A; ba ca HTTP dương/âm có PCAP/counter. Core + Primary giữ chạy; DC tắt mềm; NIC/namespace client tạm đã gỡ. Không chuyển M3. Phần dưới là nhật ký lịch sử, giữ nguyên nội dung cũ.

# 1. Ti?n ?? t? ch? ? ti?p nh?n ng?y 02/11/2026

## 1.1. M?c 15:15?15:18 UTC+07:00

Ti?p t?c tr?n lab hi?n h?nh, kh?ng d?ng l?i: 10 node, 11 segment L2, 23 NIC ?? n?i. Ki?m tra c?u tr?c XML ??t, ch? Secondary v? Suricata ?ang ch?y; Primary/Core ?ang t?t. Minh ch?ng: `evidence/M2/topology-first-20261102/inventory-resume-1515.json` v? `validation-resume-1515.json`.

Ng??i d?ng b?o ?? c?i v? c?u h?nh Secondary: LAN 192.168.1.2/24; VLAN 30/40/50/60/99 l?n l??t 192.168.VLAN.3/24; SYNC vtnet2 10.255.255.2/30. ?nh console `evidence/M3/resume-20261102/secondary-current-20261102T151529+0700.png` x?c nh?n c?c ??a ch? ?? t?i th?i ?i?m thu.

?? sao l?u c?u h?nh hi?n h?nh b?n trong guest t?i `/root/soc-ha-backup-20261102-1516/config.xml` v?i umask 077; ch?a c?ng b? raw XML v? c? th? ch?a m?t kh?u hash/kh?a ri?ng. ?nh `secondary-config-backup-20261102T151606+0700.png` ghi checksum v? mount th?c t?. Ph?t hi?n quan tr?ng: root hi?n v?n l? `/dev/iso9660/OPNSENSE_INSTALL`; backup trong /root c?a Live ISO ch?a ???c xem l? b?n sao b?n v?ng ngo?i guest. ?ang ki?m tra ? ?? b?o to?n c?u h?nh m?i tr??c reboot. Kh?ng c?i l?i, format, reset ho?c thay overlay firewall.

Suricata c? minh ch?ng c? c?i 7.0.3, ki?m tra c?u h?nh PASS, service active v? capture kh?ng IP. Ch?a x?c minh ???ng mirror m?i. ?? g?i shutdown m?m sensor sau m?t ph?t ?? nh??ng RAM cho HA; ph?i ki?m ti?n tr?nh th?c t? tr??c khi b?t Primary.

## 1.2. Tr?ng th?i nghi?m thu

- TOPOLOGY_READY: ph?n node/NIC/segment ?? c? ??c t? ???c ki?m tra c?u tr?c; Wazuh/upstream v?n c? ?i?m c?n x?c nh?n trong gap analysis.
- CONFIGURED: Core theo b?ng ch?ng M2; Secondary c? IP xu?t hi?n tr?n console; Suricata ?? c?i v? ch?y theo b? xu?t console c? checksum.
- VERIFIED: ch? ph?m vi minh ch?ng t??ng ?ng. Ch?a VERIFIED HA/CARP/pfsync/XMLRPC, gateway end-to-end, mirror Core?Suricata ho?c Wazuh.

## 1.3. Vi?c ?ang th?c hi?n

B?o to?n c?u h?nh Live Secondary ra n?i b?n v?ng; x?c minh h? ?i?u h?nh tr?n ? v? boot option. Sau ?? ki?m ng?n s?ch RAM c?p firewall, SYNC/rules, r?i pfsync/XMLRPC/CARP khi ?? ?i?u ki?n. Kh?ng ch?y l?i 95 ca VLAN M2.

## 1.4. M?c 15:20?15:27 UTC+07:00

Sensor ?? shutdown m?m, x?c minh ch? c?p firewall ?ang ch?y (6 GiB RAM guest danh ngh?a); EVE available kho?ng 2,8 GiB sau boot, vmstat si/so = 0 trong m?u quan s?t. Kh?ng b?t Core ho?c node d?ch v? kh?c c?ng c?p HA.

Secondary c? GPT/UFS tr?n vtbd0p3. ?? mount read-only ?? ki?m tra, sau ?? t?m m? ghi **ch? ?? t?o t?p backup m?i** `/root/soc-ha-backup-20261102-1522/live-config.xml` tr?n filesystem ? c?i; kh?ng thay `/conf/config.xml` c?a ?. Hash backup b?n v?ng kh?p hash c?u h?nh Live: `6af39a6589a1edfee0ac354452c3037e8b32108d47652f3be74b711c7317550d`. ?? sync v? remount read-only. ?nh: `secondary-persistent-config-backup-20261102T152143+0700.png`.

??i chi?u cho th?y c?u h?nh **tr?n ?** v?n ch? c? WAN DHCP, LAN 192.168.1.1/24, ch?a c? n?m VLAN v? SYNC; c?u h?nh **Live** c? LAN .2, n?m VLAN .3 v? SYNC .2. V? v?y kh?ng reboot Secondary t?y ti?n tr??c khi b?o to?n/migrate ph?n c?u h?nh c?n thi?t. Ch?a s?a active config tr?n ?, ch?a ??i boot option v? kh?ng c?i l?i.

Primary ???c b?t ri?ng, boot banner x?c nh?n root `/dev/gpt/rootfs`; menu li?t k? VLAN .2 v? SYNC 10.255.255.1/30 ??ng th?ng tin ng??i d?ng. Hi?n t?i c?n login prompt, ?? y?u c?u ng??i d?ng ??ng nh?p tr?c ti?p v? ch?n Shell; kh?ng y?u c?u g?i m?t kh?u.

Th? SYNC t? Secondary: 3 g?i ping g?i, 0 nh?n; ARP th?y 10.255.255.1 ? MAC 50:00:00:01:00:02 tr?n vtnet2. K?t lu?n: li?n k?t L2 c? ??i t?c ??ng MAC; ch?a ??t ICMP/HA. Minh ch?ng `sync-pretest-result-20261102T152604+0700.png`. Ch?a c?u h?nh pfsync/XMLRPC/CARP v? ch?a ?? ?i?u ki?n.

## 1.5. M?c 15:36?16:14 UTC+07:00

?? th?m 3 rule HA SYNC tr?n t?ng firewall b?ng model Firewall/Filter c?a OPNsense: ICMP, pfsync, TCP 443; ch? peer /32 ? IP local /32 tr?n opt6/vtnet2, b?t log v? nosync=1. Script ki?m tra model tr??c l?u; x?c nh?n c?c ph?n interfaces/system/cert/ca/IPsec/OpenVPN/NAT/DHCP/hasync/virtualip gi? nguy?n hash khi th?m rule. Rule c? ???c gi? nguy?n. `configctl filter reload` th?c thi; Primary?Secondary ??t 3/3 ping v? TCP443 k?t n?i th?nh c?ng. C?c ?nh `primary-sync-after-rules-20261102T153822+0700.png`, `primary-sync-https-api-20261102T154234+0700.png` x?c nh?n k?t qu? v? rule PF th?c t?.

?? chuy?n ri?ng interfaces, VLAN v? 3 rule HA c?a ch?nh Secondary t? Live sang ? c?i, gi? nguy?n system/m?t kh?u/ch?ng th?/NAT/DHCP/hasync/VIP v? c?c rule kh?ng thu?c HA. C? backup c? c?u h?nh Live l?n c?u h?nh ? tr??c thay ??i. ?nh `secondary-network-preserved-on-disk-20261102T160608+0700.png` ghi k?t qu? ki?m tra v?ng b?o v?. Kh?ng sao ch?p c?u h?nh Primary sang Secondary.

Secondary ?? shutdown m?m. Backup overlay l?c d?ng t?i `/root/soc-secondary-installed-backup-20261102-resume/virtioa.qcow2`, 2491613184 byte; SHA256 ngu?n v? b?n sao kh?p `506422162ca81de0ca16f481ae262a6150eedbc322c9681c3f5b220fcb46c5da`. Ch? ??i boot order dc?c qua API EVE, gi? ISO, node kh?c v? link. Metadata `secondary-installed-disk-backup.json`.

Boot Secondary t? `/dev/gpt/rootfs` ?? x?c minh b?ng ?nh `secondary-disk-boot-check-20261102T161149+0700.png`; LAN .2, n?m VLAN .3 v? SYNC .2 xu?t hi?n ??y ?? sau boot ?. Ng??i d?ng ?? ??ng nh?p root v? m? Shell tr?n b?n c?i. Kh?ng c?i l?i ho?c reset firewall.

Pfsync ?ang tri?n khai; XMLRPC/CARP ch?a VERIFIED. M?t l?nh CLI ban ??u b? shell t? ch?i do history expansion, kh?ng th?c thi thay ??i; ?? ghi ?nh v? ch?nh c?ch g?i. G?i Wazuh manager 4.14.9-1 ?? chu?n b? offline v? x?c minh GPG/Packages/SHA256, ch?a c?i. Kh?ng g?i manager-only l? b? Wazuh ??y ??.
