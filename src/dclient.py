import decoreToolkit
from decoreErrors import *
from os.path import isfile

VER_NUM = "0.1.0"
print("Welcome to DeCore v" + VER_NUM + "! Initialising...")

url = decoreToolkit.URL +"v1/node/register"

if isfile(decoreToolkit.CFG_PATH):
    decoreToolkit.sync()
else:
    mediaGot = False
    while mediaGot is False:
        try:               
            decoreToolkit.createcfgfile(url)
            if isfile(decoreToolkit.CFG_PATH):
                print(".cfg file found, syncing...")
                decoreToolkit.sync()
                mediaGot=True
        except DecoreServerConnectionException as ex:
            pass
        except Exception as e:
            pass