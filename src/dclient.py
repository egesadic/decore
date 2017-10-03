from decoreToolkit import *
from decoreErrors import *
from os.path import isfile

VER_NUM = "0.1.3"
print("Welcome to DeCore v" + VER_NUM + "! Initialising...")

url = URL +"v1/node/register"

mediaGot = False

try:
    while isfile(CFG_PATH) is False: 
        printmessage("Configuration file not found, creating new one.")
        while mediaGot is False:         
            createcfgfile(url,"wlan0")
            if isfile(CFG_PATH):
                mediaGot=True        

    while True:
        sync()
        print("Startup complete, listening to server for changes...")
        runslide()
        time.sleep(COOLDOWN)      

except DecoreServerConnectionException as ex:
    pass
except Exception as e:
    pass    

