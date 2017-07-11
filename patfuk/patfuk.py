#!/usr/bin/python
# patfuk
# Create predictable buffers and find the offset of substrings in it
#
# Fuk msf that's why I did my own one


import sys


def usage():
    print "Usage: python %s <opt>" % sys.argv[0]
    print "Where <opt> is:"
    print "\t-c <n>: create a predictable buffer of <n> length."
    print "\t-o <pattern>: find the offset of <pattern> in the predictable buffer"
    sys.exit(1)

i=1
ia=0x61
ib=0x61
ic=0x41
c=0
pattern=""
loop=False
offset=None

if len(sys.argv) != 3:
    usage()


if sys.argv[1] == '-c':
    loop=int(sys.argv[2])
elif sys.argv[1] == '-o':
    offset = str(sys.argv[2])
    if offset.find("0x") != -1:
        offset=offset.replace("0x","").decode("hex")
else:
    usage()


while True:
    if ia == 0x7a and ib == 0x7a and ic == 0x5a and c == 10:
        if sys.argv[1] == '-o':
            print "[!] Pattern not found. (yo)"
        if sys.argv[1] == '-c':
            print "[!] Longest unique pattern reached. (max 651040 yo)"
        sys.exit(-1)
    
    if ib == 0x7a and ic == 0x5a and c == 10:
        ia+=1
        ib=0x61
    
    if ic == 0x5a and c == 10:
        ic=0x41
        ib+=1
    
    if c == 10:
        c=0
        ic+=1
    
    if (i % 4) == 1:
        pattern+=chr(ia)
        i+=1
    elif (i % 4) == 2:
        pattern+=chr(ib)
        i+=1
    elif (i % 4) == 3:
        pattern+=chr(ic)
        i+=1
    elif (i % 4) == 0:
        pattern+=str(c)
        c+=1
        i+=1

    if sys.argv[1] == '-o':
        if len(pattern) >= len(offset):
            if pattern[(len(offset) * (-1)):] == offset:
                print "[!] Offset found at index %i" % (i - len(offset)-1)
                sys.exit(0)

    if loop and i > loop:
        break

print pattern
