"""Prepare one benign ICMP marker frame; no network call without both execute flags.

Future run only on EVE after Core/mirror validation. Frame generation is not
Suricata detection evidence or ping success. No IP is assigned to Core or host.
"""
import argparse
import json
import socket
import struct
from m2_tap_frame_test import guard, TAPS

MARKER=b'SOC-M4-TEST-20261101'


def checksum(data):
    if len(data)%2:data+=b'\0'
    total=sum(struct.unpack('!'+str(len(data)//2)+'H',data))
    while total>>16:total=(total&65535)+(total>>16)
    return (~total)&65535


def frame():
    icmp=struct.pack('!BBHHH',8,0,0,0x534f,1)+MARKER
    icmp=icmp[:2]+struct.pack('!H',checksum(icmp))+icmp[4:]
    ip=struct.pack('!BBHHHBBH4s4s',0x45,0,20+len(icmp),0x534f,0,64,1,0,
                   socket.inet_aton('192.168.30.101'),socket.inet_aton('192.168.30.102'))
    ip=ip[:10]+struct.pack('!H',checksum(ip))+ip[12:]
    return bytes.fromhex('02534f43123402534f4300000800')+ip+icmp


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute',action='store_true');p.add_argument('--resources-ready',action='store_true')
    a=p.parse_args();data=frame()
    result={'status':'PREPARED_NOT_SENT','marker':MARKER.decode(),'network_detection_pass':False,'proposed_addresses_unconfirmed':True}
    if a.execute:
        if not __debug__:raise RuntimeError('Do not run with Python -O')
        if not a.resources_ready:raise RuntimeError('Wait for user resource readiness and validated isolated lab')
        guard()
        with socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(3)) as s:
            s.bind((TAPS[0],0));result['bytes_sent']=s.send(data)
        result['status']='FRAME_SENT_ONLY_NOT_DETECTION_PASS'
    print(json.dumps(result))


if __name__=='__main__':main()
