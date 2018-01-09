import json
import os
from urllib2 import Request, urlopen
from time import sleep, localtime, time, asctime
from scapy.all import srp1, Ether, ARP

class Target:
    status = None # 1 for present, 0 for not
    name = None
    mac_addr = None

    def __init__(self, name, mac_addr):
        self.name = name
        self.mac_addr = mac_addr

    def report(self):
        print(self.name+' status: '+str(self.status))

def update(target, new_status):
    if target.status is None or target.status != new_status:
        target.status = new_status
        warning(target.name, new_status)
        target.report()

def warning(who, flag):
    now = asctime(localtime(time()))
    if flag:
        data = json.dumps({"text": "%s: %s is watching you\n" % (now,who)})
    else:
        data = json.dumps({"text": "%s: %s has left\n" % (now,who)})
    r = Request('https://hooks.slack.com/services/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',
                data=data,
                headers={'Content-Type': 'application/json'})
    urlopen(r)

def arpscan(target):
    for ipFix in range(1, 254):
        ip = "192.168.11." + str(ipFix)
        arpPkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip, hwdst="ff:ff:ff:ff:ff:ff")
        res = srp1(arpPkt, timeout=1, verbose=0)
        if res and res.hwsrc == target.mac_addr:
            return res.psrc
    return 0

def ipscan(IP, target):
    while True:
        status = os.system("ping -c 1 " + IP)
        mact = os.popen("arp -a "+ IP).readlines()[0].find(target.mac_addr)
        if status == 0 and mact > 0:
            print('wait 300s for next detection')
            sleep(300)
        else:
            update(target, 0)
            return 0

def main():
    target = Target(name="Your boss", mac_addr="00:28:f8:12:3b:3f")
    while True:
        IP = arpscan(target)
        print('got ip: '+str(IP))
        if IP:
            update(target, 1)
            ipscan(IP, target)
        else:
            update(target, 0)
        print('wait 600s for next detection')
        sleep(600)

main()