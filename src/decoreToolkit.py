# -*- coding: utf-8 -*-
"""Useful functions & utilites for DeCore programming."""
import sys
import os
import urllib2
import json
import httplib
import time
import tkMessageBox
from decoreErrors import UndefinedDeviceException, DecoreServerConnectionException
from abc import ABCMeta
from os import listdir, unlink
from os.path import isfile, join
##########################################################################################################
#                                    GLOBAL VARIABLES START HERE                                         #
##########################################################################################################  

CFG_PATH = "/usr/decore/config/cfgval.dc"
MEDIA_PATH = "/usr/decore/media/"
SLIDE_PATH = "/usr/decore/slides/"
##########################################################################################################
#                                          CLASSES START HERE                                            #
##########################################################################################################  

class decObject:
    """Base class for all decore objects."""
    __metaclass__ = ABCMeta
    def __init__(self, id = 0 ,name = ""):
        self.id = None
        self.name = name

class Node(decObject):
    """DeCore client, probably a RPi. Inherits Device class."""
    def __init__(self, name, address = '', parent = ""):
        self.id = 0
        self.name = name
        self.address = address
        self.parent = ""

class Slide(decObject):
    """DeCore slide object"""
    def __init__(self, id, name = "", node = Node, script = "" ):
        self.id = 0
        self.name = name
        self.node = None
        self.script = script

    def writeToFile(self):
        """Generates a .DPA file to be played in RPi."""
        try:
            cwd = os.getcwd()+'\slides/'
            f = open(cwd+self.name+'.dpa', 'w')
            f.write(self.script+"exit 0")
            f.close()
        except Exception as e:
            tkMessageBox.showinfo("this",e)

##########################################################################################################
#                                          FUNCTIONS START HERE                                          #
##########################################################################################################                                                                                          
def getmacadress(interface):
    """Gets the MAC address of specified device."""
    # Return the MAC address of interface
    try:
        mac = open('/sys/class/net/' + interface + '/address').read()
    except Exception:
        mac = "00:00:00:00:00:00"
    return mac[0:17]

def createcfgfile(url):
    """Connect to a local DeCore server to fetch device-id and store it in a config file under specified path. Default path to config file is '/usr/decore/config'."""    
    try:
        #Geçerli bir config dosyası olup olmadığını denetle.   
        if isfile(CFG_PATH) is False:
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
            if value > 0:
                device_id = str(value)
                newcfg = open(CFG_PATH, 'w')
                newcfg.write(device_id)
                newcfg.close()
                print ("File written and closed. GG!")
                exit(0)
            elif value == -1:
                print ("Could not connect to server, will try again in 30 seconds.")
                time.sleep(30)
                createcfgfile(url)
            elif value == -2:
                print ("No MAC sent by device, will try again in 30 seconds.")
                time.sleep(30)
                createcfgfile(url)
            else:
                raise DecoreServerConnectionException('No value was returned from server. There might be problems with the server or your connection.')
    
    except DecoreServerConnectionException as u:
        print (u)
        sys.exit(1)
    except urllib2.HTTPError, e:
        #todo - bir daha cfg yaratıcıyı çağır
        pass
    except urllib2.URLError, e:
        #todo - URL kontrol ettir
        pass
    except httplib.HTTPException, e:
        pass
    except Exception as ex:
        #todo - Genel hata, yapacak bişey yok
        pass

def sync():
    """Initiate a synchronisation between DeCore and the server. Requires config.json to be properly setup.""" 
    try:
        if isfile(CFG_PATH):
            cfgfile = open(CFG_PATH, 'r')
            cfg = json.load(cfgfile)
            device_id = cfg['ID']
            filelist = [f for f in listdir(MEDIA_PATH) if isfile(join(MEDIA_PATH, f))]
            data = {
                "Id": device_id, 
                "OldPaths": filelist
            }
            url = "http://192.168.34.128:8080/v1/node/" + str(device_id)
            
            #Sunucuya bağlan ve dosyaları talep et.
            request = urllib2.Request(url, json.dumps(data))
            request.add_header('Content-Type', 'application/json')
            tmp = urllib2.urlopen(request)
                        
            #Döndürülen yanıtı oku.
            print ("Connection success!")
            response = json.loads(tmp.read())
            tobedeleted = response["data"]["ToBeDeleted"]
            
            #ToBeDeleted'den alınan dosyaları sil
            for the_file in tobedeleted:
                file_path = join(MEDIA_PATH, the_file)           
                if isfile(file_path):
                    unlink(file_path)
            #ToBeAdded'dan gelecek dosyaları indir
            #{"data": {"Id": 1,"Paths": "{\"deneme1.jpg\": true}", "ToBeAdded": ["deneme1.jpg"], "ToBeDeleted": ["deneme2.jpg"] }}
        else:
            raise UndefinedDeviceException("This device is not properly configured. Reboot the device and try again.")
    
    except UndefinedDeviceException as u:
        print u
        sys.exit(1)
    except urllib2.HTTPError, e:
        pass
    except urllib2.URLError, e:
        pass
    except httplib.HTTPException, e:
        pass
    except Exception as e:
        print(e)
def forcecfgcreate(url):
    """Forces a new config file creation. Use this only if needed."""
    if isfile(CFG_PATH):
        unlink(CFG_PATH)
        createcfgfile(url)
    else:
        createcfgfile(url)
