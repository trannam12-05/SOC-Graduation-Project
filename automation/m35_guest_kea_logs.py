import pathlib,subprocess
def run(command):
 p=subprocess.run(command,shell=True,capture_output=True,text=True,timeout=20)
 return {'rc':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-2000:]}
d={'logs':run("find /var/log -maxdepth 2 -type f | sort | head -100"),
   'kea_messages':run("tail -160 /var/log/kea/kea_20261105.log 2>/dev/null"),
   'dnsmasq_config':run("grep -n -E '^(port|interface|dhcp|except|no-dhcp|bind)' /usr/local/etc/dnsmasq.conf | head -120"),
   'ifconfig40':run("ifconfig vtnet0_vlan40"),
   'carp':run("ifconfig -g carp")}
