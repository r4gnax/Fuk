#!/usr/bin/python

import sys
import argparse
import time
from distorm3 import Decode

M32     = False
BIN     = ""
TYPE    = None
ONLY    = None



def log(status, msg):
    if status is 'e': # ERROR
        sys.stderr.write("\033[91m[x] ")
    elif status is 'w': # WARNING
        sys.stderr.write("\033[93m[!] ")
    elif status is 'i': # INFO
        sys.stderr.write("\033[92m[*] ")
    elif status is 's': # SUBINFO
        sys.stderr.write("\033[95m[~] ")
    sys.stderr.write(str(msg))
    sys.stderr.write('\033[0m\n')
    sys.stderr.flush()


def main():
    global M32
    global BIN
    global TYPE
    global ONLY

    t0 = time.time()
    (M32, BIN, TYPE, ONLY) = parse_arguments()

    log('i', "ROPfuk, let's find some gadgets!")
    if M32:
        from distorm3 import Decode32Bits as DecodeMode
    else:
        from distorm3 import Decode64Bits as DecodeMode

    log('s', 'mode %s loaded.' % ('32bits' if M32 else '64bits'))


    log('s', 'Decoding %s...' % BIN)
    decoded_bin = Decode(len(BIN), open(BIN, "rb").read(), DecodeMode)
    gadget_list = list()
    if ONLY is None:
        for i in range(0,len(decoded_bin)):
            for t in TYPE.split(";"):
                if decoded_bin[i][2].lower().find(t) != -1:
                    gadget_list.append(decoded_bin[i-10:i+1])
    else:
        ONLY=ONLY.split(";")
        for i in range(0, len(decoded_bin)):
            seq_flag = False
            for o in ONLY:
                if decoded_bin[i][2].lower().find(o) != -1:
                    seq_flag=True
                    i+=1
                else:
                    seq_flag=False
                    break
            if seq_flag:
                gadget_list.append(decoded_bin[(i-len(ONLY)):i])
    

    for gadget in gadget_list:
        print "-----------::| 0x%08x" % gadget[0][0]
        for inst in gadget:
            print "0x%08x %s" % (inst[0],inst[2].lower())
        print
    tf=time.time()
    log('s', '%s decoded. %i gadgets found! (took %i seconds)' % (BIN, len(gadget_list), (tf-t0)))

def parse_arguments():
    parser = argparse.ArgumentParser(description="GIMMI ROP!")
    parser.add_argument('-m32', action="store_true", dest="arg_m32", help="32b mode yo", default=False)
    parser.add_argument('bin', metavar="bin", type=str, action="store", help="Binary to decode")
    parser.add_argument('-t','--type', action="store", dest="arg_type", help="filter by gadget type (example: ret;call;jmp | default: all)", default="ret;call;jmp")
    parser.add_argument('-o','--only', action="store", dest="arg_only", help="Only certain typr of gadgets (ex: 'pop;pop;ret' or 'sub;call')", default=None)
    results = parser.parse_args()
    return (results.arg_m32, results.bin, results.arg_type, results.arg_only)

main()
