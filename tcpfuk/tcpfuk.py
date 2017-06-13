#!/usr/bin/env python
# Ragnax' TCPFuk 
# TCP proxy for analizing weird protos
# Inspired by Black Hat Python book (https://www.amazon.com/Black-Hat-Python-Programming-Pentesters/dp/1593275900)

import sys
import socket
import threading

def run(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except:
        print "Failed to bind server to local host " + local_host + ":" + str(local_port)
        sys.exit(-1)
    print "Listening on " + local_host + ":" + str(local_port)
    
    server.listen(5)
    
    while True:
        client_sock, client_addr = server.accept()
        print "Incoming connection from %s:%d" % (client_addr[0], client_addr[1])
        proxy_thr = threading.Thread(target=proxy_handler, args=(client_sock, remote_host, remote_port, receive_first))
        proxy_thr.start()

def proxy_handler(client_sock, remote_host, remote_port, receive_first):
    remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_sock.connect((remote_host, remote_port))
    if receive_first:
        remote_buffer = receive_from(remote_sock)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print "Sending %d bytes to client." % len(remote_buffer)
            client_sock.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_sock)
        if len(local_buffer):
            print "Received %d bytes from client." % len(local_buffer)
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_sock.send(local_buffer)
            print "Sent to remote."
        remote_buffer = receive_from(remote_sock)

        if len(remote_buffer):
            print "Received %d bytes from remote." % len(remote_buffer)
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_sock.send(remote_buffer)
            print "Sent to client."

        if not len(local_buffer) or not len(remote_buffer):
            client_sock.close()
            remote_sock.close()
            print "No more data. Closing connections."
            break

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append( b"%04X> %-*s | %s" % (i, length*(digits + 1), hexa, text) )
    print b'\n'.join(result)

def receive_from(connection):
    buffer = ""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def request_handler(buffer):
    # if need packet modification
    return buffer

def response_handler(buffer):
    # if need packet modification
    return buffer

def main():
    if len(sys.argv[1:]) != 5:
        print "Usage: %s <local_host> <local_port> <remote_host> <remote_port> <receive_first>" % sys.argv[0]
        print "Example: %s 127.0.0.1 9000 91.121.173.72 900 True" % sys.argv[0]
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]
    
    receive_first = True if "true" in receive_first.lower() else False
    run(local_host, local_port, remote_host, remote_port, receive_first)

main()
