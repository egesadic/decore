import decoreToolkit
import createSlide
from decoreErrors import *
from os.path import isfile

VER_NUM = "0.1.1"
print("Welcome to DeCore v" + VER_NUM + "! Initialising...")

url = decoreToolkit.URL +"v1/node/register"

if isfile(decoreToolkit.CFG_PATH):
    decoreToolkit.sync()
    if decoreToolkit.FILES_CHANGED is True:
        print("Media in this node has been changed! Rebuilding .dpa file...")
        createSlide.newSlideshow(decoreToolkit.IS_RANDOM, decoreToolkit.DELAY)
    else:
        print("Startup complete, listening to server for changes...")
        decoreToolkit.time.sleep(30)      
else:
    mediaGot = False
    while mediaGot is False:
        try:               
            decoreToolkit.createcfgfile(url,"wlan0")
            decoreToolkit.time.sleep(5)
            if isfile(decoreToolkit.CFG_PATH):
                print(".cfg file found, syncing...")
                decoreToolkit.sync()                
                createSlide.newSlideshow(decoreToolkit.IS_RANDOM, decoreToolkit.DELAY)  
                mediaGot=True
        except DecoreServerConnectionException as ex:
            pass
        except Exception as e:
            pass

