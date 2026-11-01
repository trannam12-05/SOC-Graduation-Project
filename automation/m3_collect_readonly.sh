#!/bin/sh
# PREPARED ONLY, run inside a confirmed OPNsense guest, no config.xml export.
# Usage: sh m3_collect_readonly.sh Primary expected-hostname /root/m3-new-run
set -eu
test "$#" = 3
case "$1" in Primary|Secondary) ;; *) exit 2 ;; esac
test "$(id -u)" = 0
test "$(hostname)" = "$2"
command -v opnsense-version >/dev/null
case "$3" in /root/m3-*) ;; *) exit 2 ;; esac
test "${3%/*}" = /root
test ! -L "$3"
test ! -e "$3"
umask 077
mkdir "$3"
opnsense-version > "$3/version.txt"
ifconfig -a > "$3/interfaces.txt"
netstat -rn > "$3/routes.txt"
pfctl -si > "$3/pf-info.txt"
sysctl net.inet.carp.allow net.inet.carp.preempt net.inet.carp.demotion > "$3/carp-sysctl.txt"
date -u '+%Y-%m-%dT%H:%M:%SZ guest-clock-unverified' > "$3/guest-clock.txt"
printf '%s\n' "Role=$1; read-only collection only, CARP/pfsync/XMLRPC/DHCP/NAT acceptance NOT established" > "$3/scope.txt"
