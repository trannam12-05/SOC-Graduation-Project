#!/bin/sh
# PREPARED ONLY. Chi tac dong interface noi bo br-core-l2, khong sua forwarding.
set -eu
test "$(hostname)" = soc-core-l2
test "$(id -u)" = 0
test "$(cat /proc/sys/net/ipv4/ip_forward)" = 0
test "$(cat /proc/sys/net/ipv6/conf/all/forwarding)" = 0
ovs-vsctl br-exists br-core-l2
for attempt in $(seq 1 45); do
    if test -d /sys/class/net/br-core-l2; then break; fi
    sleep 1
done
test -d /sys/class/net/br-core-l2
# Dung neu da co IP ngoai du kien; khong tu flush dia chi cua nguoi quan tri.
test -z "$(ip -o address show dev br-core-l2)"
ip link set dev br-core-l2 addrgenmode none
sysctl -w net.ipv6.conf.br-core-l2.disable_ipv6=1
ip link set dev br-core-l2 up
test -z "$(ip -o address show dev br-core-l2)"
test "$(cat /proc/sys/net/ipv4/ip_forward)" = 0
test "$(cat /proc/sys/net/ipv6/conf/all/forwarding)" = 0
