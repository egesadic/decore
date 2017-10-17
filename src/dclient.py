# -*- coding: utf-8 -*-
from decoreToolkit import *
from decoreErrors import *
from os.path import isfile

VER_NUM = "0.1.5"
print("Welcome to DeCore v" + VER_NUM + "! Initialising...")

url = URL +"v1/node/register"
mediaGot = False
logging.basicConfig(filename= LOG_PATH + "decore-" + str(time.strftime("%d-%m-%Y")) + ".log", level=logging.INFO)

try:
    while isfile(CFG_PATH) is False: 
        printmessage("Configuration file not found, creating new one.")
        while mediaGot is False:         
            createcfgfile(url,"wlan0")
            if isfile(CFG_PATH):
                mediaGot=True        
    
    #Cihaz ilk çalıştığında slide.dpa'yı çalıştır.
    runslide()

    while True:
        sync()
        print("Startup complete, listening to server for changes...")        
        time.sleep(COOLDOWN)      

except DecoreServerConnectionException as ex:
    pass
except Exception as e:
    pass    

