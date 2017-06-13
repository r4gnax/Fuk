#!/usr/bin/python
# Ragnax' HTTProxFuk!
# When you need to edit HTTP requests on the fly
# TODO: Add SSL support.

import socket
import select
import time
import sys
import os

server_host = '127.0.0.1'
server_port = 31337
bs = 4096

class Prox:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))

    def run(self):
        self.server.listen(200)
        while True:
            conn, client_addr = self.server.accept()
            try:
                while True:
                    data = conn.recv(bs)
                    if data:
                        resp=self.handle_req(conn, data)
                    else:
                        break
            finally:
                conn.close()

    def response_back(self, conn, resp):
        print "Sending response to client"
        conn.sendall(resp)

    def handle_req(self, conn, request):
        req_lines = request.strip().split("\r\n")
        get_line = req_lines[0].strip()
        method,url,proto=get_line.strip().split()
        if url.find("://") != -1:
            tmp_uri = url[(url.find("://")+3):]
        else:
            tmp_uri = url
        
        path_pos = tmp_uri.find("/")
        if path_pos == -1:
            path_pos = len(tmp_uri)
        
        port_pos = tmp_uri.find(":")
        target_host = ""
        target_port = -1
        if port_pos == -1 or path_pos < port_pos:
            target_port = 80
            target_host = tmp_uri[:path_pos]
        else:
            target_port = int((tmp_uri[(port_pos+1):])[:path_pos-port_pos-1])
            target_host = tmp_uri[:port_pos]

        print "New request to " + target_host + ":" + str(target_port) + ". Edit it?"
        if raw_input("> ").lower() in ("y", "yes"):
            request = self.edit_req(request)
        self.response_back(conn, resp)

    def edit_req(self, request):
        with open("/tmp/.tmp_req", "wb") as f:
            f.write(request)
        os.system("vim /tmp/.tmp_req")
        new_req=open("/tmp/.tmp_req", "rb").read()
        os.remove("/tmp/.tmp_req")
        return new_req

    def forward_req(self, target_host, target_port, request):
        print "Forwarding request to " + target_host + ":" + str(target_port) + "..."
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect((target_host, target_port))
        target.send(request)
        response = target.recv(bs)
        if response:
            return response
        else:
            return None


if __name__ == '__main__':
    server = Prox(server_host, server_port)
    try:
        server.run()
    except KeyboardInterrupt:
        print "Stopping server"
        sys.exit(0)
