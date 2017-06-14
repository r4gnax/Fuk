#!/usr/bin/python


from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random
import sys
import os
import subprocess
import socket
import time
import binascii
import base64
import random


def bin2hex(data):
    return binascii.hexlify(data)

def hex2bin(data):
    return binascii.unhexlify(data)

def random_string(length):
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_$/*#@+') for _ in range(length))

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

r=Random.new().read
privkey= RSA.generate(2048, r)
pubkey=privkey.publickey()
pubkey_der = pubkey.exportKey('DER')



s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1', 31337))
s.listen(20)

while True:
    try:
        client_conn, client_addr = s.accept()
        print client_addr[0]
        client_conn.send(bin2hex(pubkey_der))
        print "sent %s" % bin2hex(pubkey_der)
        ret=client_conn.recv(4096)
        secret = privkey.decrypt(ret)
        print "secret: %s" % secret
        while True:
            try:
                inp = raw_input(":> ")
                client_conn.send(AES_encode(secret, inp))
                ret = client_conn.recv(4096)
                ret = AES_decode(secret, ret)
                print ret
            except Exception, e:
                print "Error : %s" % e
                break
    except Exception, e:
        print e
        break
