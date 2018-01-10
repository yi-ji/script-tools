import json
import os
from urllib2 import Request, urlopen
from time import sleep, localtime, time, asctime
from scapy.all import srp1, Ether, ARP

class Target:

    class Device:

        def __init__(self, mac_addr, name):
            self.name = name
            self.mac_addr = mac_addr
            self.ip_addr = None
            self.online = False

        def report(self):
            print(self.name, self.mac_addr, self.ip_addr, self.online)

    def __init__(self, name, devices):
        self.name = name
        self.devices = devices

    def update(self, device, online):
        if device.online != online:
            device.online = online
            self.report()
            self.warn(device.name, online)

    def warn(self, device_name, online):
        now = asctime(localtime(time()))
        device_name = " (" + device_name + ")"
        if online:
            data = json.dumps({"text": "%s: %s is watching you\n" % (now, self.name+device_name)})
        else:
            data = json.dumps({"text": "%s: %s has left\n" % (now, self.name+device_name)})
        r = Request('https://hooks.slack.com/services/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',
                    data=data,
                    headers={'Content-Type': 'application/json'})
        urlopen(r)

    def report(self):
        print(self.name+' devices: '+str(len(self.devices)))
        for device in self.devices:
            device.report()

    def online_device_num(self):
        num = 0
        for device in self.devices:
            if device.online:
                num += 1
        return num

def arp_scan(target):
    for ipFix in range(2, 255):
        ip = "192.168.11." + str(ipFix)
        arpPkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip, hwdst="ff:ff:ff:ff:ff:ff")
        res = srp1(arpPkt, timeout=1, verbose=0)
        if res:
            for device in target.devices:
                if res.hwsrc == device.mac_addr:
                    device.ip_addr = res.psrc
                    target.update(device, online=True)

def ip_scan(target):
    while target.online_device_num() > 0:
        for device in target.devices:
            if device.ip_addr is not None:
                status = os.system("ping -c 1 " + device.ip_addr)
                mact = os.popen("arp -a "+ device.ip_addr).readlines()[0].find(device.mac_addr)
                if status == 0 and mact > 0:
                    print('wait 120s for next detection')
                    sleep(120)
                else:
                    device.ip_addr = None
                    target.update(device, online=False)
            else:
                target.update(device, online=False)

def main():
    target = Target(name="Your boss", devices=[Target.Device(name="laptop", mac_addr="00:28:f8:12:3b:3f"),
                                               Target.Device(name="phone", mac_addr="cc:08:8d:d5:ad:55")])
    while True:
        arp_scan(target)
        if target.online_device_num() > 0:
            ip_scan(target)
        print('wait 300s for next detection')
        sleep(300)

main()