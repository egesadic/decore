import os.path
import sys
import json

VER_NUM="1.0"

print("Welcome to DeCore v"+VER_NUM+"! Initialising...")

try:
    def getMAC(interface):
      # Return the MAC address of interface
      try:
        str = open('/sys/class/net/' + interface + '/address').read()
      except:
        str = "00:00:00:00:00:00"
      return str[0:17]

    if os.path.isfile("/usr/decore/cfgval.dc") is False:
        count = 0
        mac = getMAC('wlan0')
        for x in range(0,4):
            if count is 3:
                print("Cannot get MAC address, please contact support.")
                sys.exit()
            if mac is "00:00:00:00:00:00":
                count+=1
            else:
                #mac.sendtoserver()
                newcfg = open("cfgval.dc",'w')
                newcfg.close()
    else:

