import json
import os
import urllib3
import sys
from time import sleep,localtime,time,asctime
from datetime import datetime
from scapy.all import *

def warning(who,flag):
    now = asctime(localtime(time()))
    if flag:
        data = json.dumps({"text": "%s:%s is watching you\n"%(now,who)})
    else:
        data = json.dumps({"text": "%s:%s is away\n"%(now,who)})
    req = urllib3.PoolManager()
    r = req.request('POST', 'https://hooks.slack.com/services/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 ',
                    body=data,
                    headers={'Content-Type': 'application/json'})

def arpscan(mac,name):
    for ipFix in range(1,254):
        ip = "192.168.11."+str(ipFix)
        arpPkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip, hwdst="ff:ff:ff:ff:ff:ff")
        res = srp1(arpPkt, timeout=1, verbose=0)
        if res and res.hwsrc == mac:
            warning(name,1)
#             print("warning")
            return res.psrc
    return 0

def ipscan(IP,name,mac):
    print("I am watching, he is coming" + IP)
    while 1:
        status = os.system("ping -c 1 "+ IP)
        mact= os.popen("arp -a "+ IP).readlines()[0].find(mac)
#         print(status)
#         print(mact)
        if status == 0 and mact>0:
            sleep(300)
        else:
            warning(name,0)
            return 0

def main():
    mac="00:28:f8:12:3b:3f"
    name="Your boss"
    round = 6*(21-datetime.now().hour)
    if round <= 0:
        sleep(43200+round)
        round = 6*(21-datetime.now().hour)
    while round>0:
        IP=arpscan(mac,name)
        if IP:
            ipscan(IP,name,mac)
            round=6*(21-datetime.now().hour)
        else:
            sleep(600)
            round = round-1

main()