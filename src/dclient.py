# -*- coding: utf-8 -*-
from decoreToolkit import *
from decoreErrors import *
from os.path import isfile

VER_NUM = "0.4"

url = URL +"v1/node/register"
mediaGot = False
checklogpath()
createlogfile()

try:
    os.system("clear")
    printmessage("Welcome to DeCore v" + VER_NUM + "! Initialising...")
    while isfile(CFG_PATH) is False: 
        printmessage("Configuration file not found, creating new one under " + CFG_PATH)
        while mediaGot is False:         
            createcfgfile(url,"wlan0")
            if isfile(CFG_PATH):
                mediaGot=True        
    
    #Cihaz ilk çalıştığında slide.dpa'yı çalıştır.
    runslide()
    while True:
        sync()
        printmessage("Listening to server for changes. Checking for changes in " + str(COOLDOWN) + " seconds.\n")         
        time.sleep(COOLDOWN)      

except DecoreServerConnectionException as ex:
    pass
except Exception as e:
    printmessage(e, "critical")  

