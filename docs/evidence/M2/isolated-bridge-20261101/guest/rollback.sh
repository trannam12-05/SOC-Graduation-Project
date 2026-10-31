#!/bin/sh
set -eu
[ "$(hostname)" = soc-core-l2 ]
ovsdb-client restore unix:/var/run/openvswitch/db.sock Open_vSwitch < /root/m2-isolated-20261101T0035/ovsdb.before
ovs-vsctl --timeout=10 show
