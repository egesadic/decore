# -*- coding: utf-8 -*-
from os.path import isfile
from decoreToolkit import CFG_PATH, createcfgfile, sync

VER_NUM = "1.0"
print "Welcome to DeCore v" + VER_NUM + "! Initialising..."
registerurl = "192.168.34.120:8080/v1/node/register"

#Geçerli bir config dosyası olup olmadığını denetle.      
if isfile(CFG_PATH) is False:
    createcfgfile(registerurl)
else:
    sync()