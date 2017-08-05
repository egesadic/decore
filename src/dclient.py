import time
import os.path
import sys
import json
import urllib2
import decoretoolkit

def ConnectToServer():
    
    VER_NUM = "1.0"

    print("Welcome to DeCore v" + VER_NUM + "! Initialising...")

    url = "192.168.34.120:8080/v1/node/register"

    try:
        if os.path.isfile("/usr/decore/cfgval.dc") is False:
            count = 0
            mac = decoretoolkit.getMAC('enp2s0')
            for x in range(0, 4):
                if count is 3:
                    print("Cannot get MAC address, please contact support.")
                    sys.exit(-1)
                if mac is "00:00:00:00:00:00":
                    count += 1
                else:
                    print ("MAC address is: "+mac)
                    data = {
                        "Mac": mac
                    }
                    break

            request = urllib2.Request(url, json.dumps(data))
            request.add_header('Content-Type', 'application/json')
            r = urllib2.urlopen(request)
            print ("Connection success!")
            response = json.loads(r.read())
            print (response)
            value = response['value']
            print ("Got "+str(value)+" as device id")
            if value >= 0:
                device_id = str(value)
                newcfg = open("/home/sparkege/cfgval.dc", 'w')
                newcfg.write(device_id)
                newcfg.close()
                print ("File written and closed. GG!")
                exit(1)
            elif value == -1:
                print ("Could not connect to server, will try again in 30 seconds.")
                time.sleep(30)
                ConnectToServer()
            elif value == -2:
                print ("No MAC sent by device, will try again in 30 seconds.")
                time.sleep(30)
                ConnectToServer()
            else:
                pass
    except Exception as e:
        print (e)
        pass
