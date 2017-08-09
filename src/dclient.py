# -*- coding: utf-8 -*-
import time
import urllib2
from os import listdir, unlink
from os.path import isfile, join
import sys
import json
import httplib
from decoreToolkit import getmacadress
from decoreErrors import UndefinedDeviceException

VER_NUM = "1.0"
print("Welcome to DeCore v" + VER_NUM + "! Initialising...")

url = "192.168.34.120:8080/v1/node/register"
cfgpath = "/usr/decore/config/cfgval.dc"
mediapath = "/usr/decore/media"

def ConnectToServer():
    try:
        #Geçerli bir config dosyası olup olmadığını denetle.      
        if isfile(cfgpath) is False:
            count = 0
            mac = getmacadress('wlan0')
            for count in range(0, 4):
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
            
            #Sunucuya bağlan ve ID talep et.
            request = urllib2.Request(url, json.dumps(data))
            request.add_header('Content-Type', 'application/json')
            tmp = urllib2.urlopen(request)
            print ("Connection success!")
            
            #Döndürülen yanıtı oku.
            response = json.loads(tmp.read())
            value = response['value']
            print ("Got "+str(value)+" as device ID")
            if value >= 0:
                device_id = str(value)
                newcfg = open(cfgpath, 'w')
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
                raise UndefinedDeviceException('No value was given to this device. There might be problems with the server.')
        else:
            cfgfile = open(cfgpath, 'r')
            cfg = json.load(cfgfile)
            device_id = cfg['ID']
            filelist = [f for f in listdir(mediapath) if isfile(join(mediapath, f))]
            data = {
                "Id": device_id, 
                "OldPaths": filelist
            }
            
            #Sunucuya bağlan ve dosyaları talep et.
            request = urllib2.Request(url, json.dumps(data))
            request.add_header('Content-Type', 'application/json')
            tmp = urllib2.urlopen(request)
            print ("Connection success!")
            
            #Döndürülen yanıtı oku.
            response = json.loads(tmp.read())
            tobedeleted = response["data"]["ToBeDeleted"]
            
            #ToBeDeleted'den alınan dosyaları sil
            for the_file in tobedeleted:
                file_path = join(mediapath, the_file)           
            if isfile(file_path):
                unlink(file_path)
            #ToBeAdded'dan gelecek dosyaları indir

            #{"data": {"Id": 1,"Paths": "{\"deneme1.jpg\": true}", "ToBeAdded": ["deneme1.jpg"], "ToBeDeleted": ["deneme2.jpg"] }}

    except UndefinedDeviceException as u:
        print(u)
        sys.exit(1)
    except urllib2.HTTPError, e:
        pass
    except urllib2.URLError, e:
        pass
    except httplib.HTTPException, e:
        pass
    except Exception as e:
        print(e)