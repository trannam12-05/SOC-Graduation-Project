"""Offline address sanity checks only; never configure OPNsense or query host nets."""
import argparse
import ipaddress as ip
import json
from pathlib import Path


def validate(data):
    networks=[]
    for row in data['vlans']:
        net=ip.ip_network(row['subnet'],strict=True)
        addresses=[ip.ip_address(row[k]) for k in ['primary','secondary','vip']]
        if len(set(addresses))!=3 or any(a not in net or a in [net.network_address,net.broadcast_address] for a in addresses):
            raise ValueError('Invalid or duplicate Primary/Secondary/VIP')
        pool=row['dhcp_proposed']
        if pool:
            lo,hi=map(ip.ip_address,pool)
            if not net.network_address<lo<=hi<net.broadcast_address or any(lo<=a<=hi for a in addresses):
                raise ValueError('Invalid DHCP pool or reserved address overlap')
        networks.append(net)
    sync=data['sync_proposed'];sn=ip.ip_network(sync['subnet'])
    if ip.ip_address(sync['primary'])==ip.ip_address(sync['secondary']):raise ValueError('SYNC IP duplicate')
    if any(ip.ip_address(sync[k]) not in sn or ip.ip_address(sync[k]) in [sn.network_address,sn.broadcast_address] for k in ['primary','secondary']):raise ValueError('Invalid SYNC host')
    networks.append(sn)
    for i,a in enumerate(networks):
        if any(a.overlaps(b) for b in networks[i+1:]):raise ValueError('Proposed subnet overlap')
        if any(a.overlaps(ip.ip_network(b)) for b in data['forbidden_known_networks']):raise ValueError('Known environment subnet overlap')
    return {'scope':'OFFLINE_DESIGN_CONSISTENCY_ONLY','design_checks_ok':True,'network_runtime_pass':False,
            'deployable':False,'unresolved':['User confirmation of addresses','WAN subnet/IP/gateway/VIP capability',
            'Actual firewall NIC/MAC assignments','Labtainer/VPN overlap review','DHCP backend/DNS/HA behavior','Image version and resources']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('proposal',type=Path)
    print(json.dumps(validate(json.loads(p.parse_args().proposal.read_text(encoding='utf-8'))),ensure_ascii=False,indent=2))
