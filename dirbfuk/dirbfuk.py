#!/usr/bin/python3
#
# Let's bust some dirs!


import sys
import time
import asyncio
import concurrent.futures
import requests
from fake_useragent import UserAgent


HOST = None
WLIST = None

words = []
max_threads = 20

def usage():
    print("Usage: %s <host> [wordlist]")
    print("default wordlist: wordlists/common.txt")
    sys.exit(1)


def main():
    global HOST
    global WLIST
    global SSL

    t0 = time.time()
    WLIST="wordlists/common.txt"
    if len(sys.argv) > 2:
        WLIST = sys.argv[2]
    try:
        HOST = sys.argv[1]
    except:
        usage()

    if HOST[-1] != '/':
        HOST += '/'
    print("[*] Starting %s on %s..." % (sys.argv[0], HOST))
    print("[*] Loading %s..." % WLIST)
    for l in open(WLIST, "rb").readlines():
        words.append(l.strip().decode("utf-8"))
    print("[!] %i words extracted from the wordlist" % len(words))
    print()
    print("------")
    print()

    loop=asyncio.get_event_loop()
    loop.run_until_complete(req_handle())
    tf=time.time()
    print("[*] Over. (took %i seconds)" % (tf-t0))
    

async def req_handle():
    ua=UserAgent()
    def do_req(u):
        return requests.get(u, headers={'user-agent': ua.random})
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, do_req, HOST+w) for w in words
        ]
        for response in await asyncio.gather(*futures):
            if response.status_code < 400:
                if response.url[-1] == '/':
                    print("--DIR: %s - %i" % (response.url, response.status_code))
                else:
                    print("%s - %i (%i bytes)" % (response.url, response.status_code, len(response.content)))
            pass
main()
