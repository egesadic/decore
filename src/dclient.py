# -*- coding: utf-8 -*-
from decoreToolkit import *
from decoreErrors import *
from os.path import isfile

sys.setdefaultencoding('utf8')

global CONFIG
VER_NUM = "0.4"
mediaGot = False

checklogpath()
createlogfile()

try:
    os.system("clear")
    printmessage("Welcome to DeCore v" + VER_NUM + "! Initialising...")
    while isfile(CFG_PATH) is False: 
        printmessage("Configuration file not found, creating new one under " + CFG_PATH)
        while mediaGot is False:         
            createcfgfile(URL,"wlan0")
            if isfile(CFG_PATH):
                mediaGot=True

    #Cihaz ilk çalıştığında slide.dpa'yı çalıştır.
    CONFIG = open(CFG_PATH, 'r')  
    runslide()
    while True:
        sync()
        printmessage("Listening to server for changes. Checking for changes in " + str(COOLDOWN) + " seconds.\n")         
        time.sleep(COOLDOWN)      

except Exception as e:
    printmessage(e, "exception")