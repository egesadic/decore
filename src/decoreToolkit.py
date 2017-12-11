# -*- coding: utf-8 -*-
"""Useful functions & utilites for DeCore programming."""
import subprocess
import sys
import os
import urllib2
import json
import httplib
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import collections
from random import shuffle
from os import listdir, path, unlink
from os.path import isfile, join
from subprocess import call
from decoreErrors import *

reload(sys)
sys.setdefaultencoding('utf8')
##########################################################################################################
#                                    GLOBAL VARIABLES START HERE                                         #
##########################################################################################################  

LOGGER = None
HAS_MEDIA = False
RESPONSE = None 
PROC = ""
VIDEO_EXT = ('.mp4', '.h264')
IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.gif')
SLIDE_PID = 0
FILELIST = []
FILES_CHANGED = "False"
IS_RANDOM = "False"
DELAY = 5
LOG_PATH = "/usr/decore/log/"
LOG_NAME = LOG_PATH + "decoreLog"
CFG_FOLDER = "/usr/decore/config/"
CFG_PATH = CFG_FOLDER + "cfgval.dc"
OND_PATH = CFG_FOLDER + "orderndelay"
MEDIA_PATH = "/usr/decore/media/"
SLIDE_PATH = "/usr/decore/slides/"
URL = "http://192.168.34.120:8082/"
COOLDOWN = 60

##########################################################################################################
#                                          CLASSESS START HERE                                           #
########################################################################################################## 



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

def sendjson(domain, data, method='POST'):
    try:
        global RESPONSE
        dest = URL + domain
        printmessage("JSON created with parameters: " + str(json.dumps(data)))
        
        #Sunucuya bağlan ve dosyaları talep et.
        request = urllib2.Request(dest, json.dumps(data), {'Content-Type': 'application/json'} )
        printmessage("JSON encoded. Starting server connection.")
        request.get_method = lambda: method
        printmessage("Connecting to URL: " + dest)
        tmp = urllib2.urlopen(request)
        printmessage("Successfully connected to: " + dest)
        RESPONSE = json.loads(tmp.read())
        return True
    except Exception as e:
        printmessage(e,"exception")
        return False

def removemedia(fname):
    if isfile(MEDIA_PATH + fname):
        os.remove(MEDIA_PATH + fname)    

def createcfgfile(url, adapter):
    """Connect to a local DeCore server to fetch device-id and store it in a config file under specified path. Default path to config file is '/usr/decore/config'."""    
    try:
        #Geçerli bir config dosyası olup olmadığını denetle.
        printmessage("Beginning creation of configuration file. Checking whether " + CFG_PATH + "exists.")
        if isfile(CFG_PATH) is False:
            printmessage("Configuration file does NOT exist. Assuming this is the first time the node boots up.", "debug")
            count = 0
            printmessage("Checking whether essential directories exist or not...")
            checkdir(CFG_FOLDER)
            checkdir(MEDIA_PATH)
            checkdir(SLIDE_PATH)
            checkdir(LOG_PATH)            
            while count < 4:
                mac = getmacadress(adapter)
                if count is 3:
                    printmessage("Cannot get MAC address properly. Please contact support.", "crtitcal")
                    quitdecore("CANNOT OBTAIN MAC ADDRESS", False)
                if mac == "00:00:00:00:00:00":
                    err = "Invalid MAC address, trying again. (MAC was " + mac + ")"
                    printmessage(err,"warning")
                    count += 1
                else:
                    printmessage("MAC address is: "+mac)                   
                    break
            
            usage = disk_usage('/')
            printmessage("Total storage on this device is " + str(bytes2human(usage.total)))
            printmessage("Free storage on this device is " + str(bytes2human(usage.free)))
            data = {
                    "Mac": mac,
                    "Storage": int(usage.total/1024),
                    "RemainingStorage": int(usage.free/1024)
            }       

            #Sunucuya bağlan ve ID talep et.
            request = urllib2.Request(url, json.dumps(data))
            printmessage("JSON encoded. Starting server connection.")
            request.add_header('Content-Type', 'application/json')
            printmessage("Connecting to URL: " + url)
            tmp = urllib2.urlopen(request)
            obj = json.loads(tmp.read())
            printmessage ("Connection to the DeCore server success! Reading response...")
            
            #Döndürülen yanıtı oku.
            response = obj
            value = response['value']
            printmessage (str(value)+" assigned as device ID")
            if value > 0:
                device_id = str(value)              
                newcfg = open(CFG_PATH, 'w')
                newcfg.write(device_id)
                newcfg.close()
                printmessage ("Config file has been created successfully!")
            elif value == -1:
                printmessage ("Could not connect to server, will try again in 30 seconds.")
                time.sleep(30)
                createcfgfile(url)
            elif value == -2:
                printmessage ("No MAC sent by device, will try again in 30 seconds.")
                time.sleep(30)
                createcfgfile(url)
            else:
                raise DecoreServerConnectionException('No value was returned from server. There might be problems with the server or with your connection.')
    
    except DecoreServerConnectionException as e:
        printmessage(e,"exception")
    except urllib2.HTTPError, e:
        #todo - bir daha cfg yaratıcıyı çağır
        printmessage(e,"exception")
    except urllib2.URLError, e:
        #todo - URL kontrol ettir
        printmessage(e,"exception")
    except httplib.HTTPException, e:
        printmessage(e,"exception")
    except Exception as e:
        #todo - Genel hata, yapacak bişey yok
        printmessage(e,"exception")

#Will get order AND delay of files
def orderNdelay():
    try:
        cfgfile = open(CFG_PATH, 'r')
        device_id = cfgfile.read()
        dest = URL + "v1/node/order/"+device_id

        # Sunucuya bağlan ve dosyaları talep et
        orderNdelayResponse = urllib2.urlopen(dest).read()

        changed=False

        if isfile(OND_PATH):
            alreadyOrderNDelay = open(OND_PATH, 'r').read()
            if alreadyOrderNDelay==orderNdelayResponse:
                printmessage("they are same","critical")
            else:
                changed=True
                printmessage("they are not same", "critical")
        else:
            changed=True

        if changed==True:
            #order or delay changed
            orderNdelayConfig = open(OND_PATH, 'w')
            orderNdelayConfig.write(orderNdelayResponse)

            orderNdelayResponse=json.loads(orderNdelayResponse)
            filesArray=orderNdelayResponse["pathsInOrder"]
            delaysArray= orderNdelayResponse["delaysInOrder"]

            #If they are None then they either has no file or something goes wrong
            if filesArray is None:
                printmessage("orderNdelay is none","warning")
                return
            if delaysArray is None:
                printmessage("orderNdelay is none", "warning")
                return

            if len(filesArray)!=len(delaysArray):
                printmessage("orderNdelay is fetched but their length not match","error")
                return

            delaysMap={}

            for index in range(0,len(filesArray)):
                delaysMap[str(filesArray[index])]=delaysArray[index]

            updateslide(True,filesArray,delaysMap)

    except UndefinedDeviceException as u:
        printmessage(u, "error")
    except JSONParseException as e:
        printmessage(e, "exception")
    except urllib2.HTTPError, e:
        printmessage(e, "exception")
    except urllib2.URLError, e:
        printmessage(e, "exception")
    except httplib.HTTPException, e:
        printmessage(e, "exception")
    except Exception as e:
        printmessage(e, "exception")

def sync():
    """Initiate a synchronisation between DeCore and the server. Requires config.json to be properly setup.""" 
    try:
        global FILES_CHANGED
        global IS_RANDOM
        global DELAY
        global OLD_FILES

        FILES_CHANGED = False

        if isfile(CFG_PATH):
            printmessage("Syncronisation started with server!")
            cfgfile = open(CFG_PATH, 'r')
            device_id = cfgfile.read()            
            filelist = [f for f in listdir(MEDIA_PATH) if isfile(join(MEDIA_PATH, f))]
            printmessage("Current files: "+str(filelist))
            usage = disk_usage('/')
            data = {
                "Id": int(device_id), 
                "OldPaths": filelist,
                "RemainingStorage": int(usage.free/1024)
            }
            printmessage("Device ID is: " + str(device_id))
            printmessage("Free storage on this device is " + str(bytes2human(usage.free)))
            
            #print(json.loads(data))
            url = URL + "v1/node"
            
            #Sunucuya bağlan ve dosyaları talep et.
            printmessage("Attempting to connect to server...", "info")
            request = urllib2.Request(url, json.dumps(data))
            request.add_header('Content-Type', 'application/json')
            request.get_method = lambda: 'PUT'
            tmp = urllib2.urlopen(request)

            #Döndürülen yanıtı oku.
            printmessage ("Connection success! Reading response...")
            response = json.loads(tmp.read())
            if response is not None:
                IS_RANDOM = str(response["data"]["IsRandom"])
                DELAY = str(response["data"]["Delay"])
                printmessage("Random flag is " + str(IS_RANDOM), "debug")
                printmessage("Delay is " + str(DELAY), "debug")
                tobedeleted = response["data"]["ToBeDeleted"]
                tobeadded = response["data"]["ToBeAdded"]               
                OLD_FILES = tobedeleted
                
                #ToBeAdded'dan gelecek dosyaları metin dosyasına yaz ve indir                
                if tobeadded is not None:
                    printmessage("Files to be added: "+str(tobeadded))
                    printmessage("Writing new files names to TXT file.", "debug")
                    addedFile = open(CFG_FOLDER + "ToBeAdded.txt", 'w')
                    content = ""
                    for the_file in tobeadded:
                        content = ''.join([content, str(the_file) ,"\n"])
                    addedFile.write(content)
                    addedFile.close()
                    printmessage("Fetching the files from server...\n")
                    fetchfiles(device_id)        
                    printmessage ("Added " + str(len(tobeadded)) + " files.")
                    FILES_CHANGED = True
                else:
                    printmessage("No files to be added.")
                
                #ToBeDeleted'den alınan dosyaları sil
                if tobedeleted is not None:
                    printmessage("Files to be deleted are: " +str(tobedeleted) ) 
                    for the_file in tobedeleted:
                        file_path = join(MEDIA_PATH, the_file)           
                        if isfile(file_path):
                            unlink(file_path)
                    printmessage ("Deleted " + str(len(tobedeleted)) + "files successfully.")
                    FILES_CHANGED = True
                else:
                    printmessage("No files to be deleted.")

                if FILES_CHANGED:
                    printmessage("Media in this node has been changed! Rebuilding .dpa file...")
                    #Delete old orderNdelay if exist
                    orderNdelay_path = OND_PATH
                    if isfile(orderNdelay_path):
                        unlink(orderNdelay_path)
                    updateslide(False,None,None)
                else:
                    #No media was changed, check for orderNdelay
                    orderNdelay()
            else:
                raise JSONParseException("There has been a problem with the DeCore node. No changes were made.")            
        else:
            raise UndefinedDeviceException("This device is not properly configured. Forcing configuration file creation.")
    
    except UndefinedDeviceException as u:
        printmessage(u, "error")
        forcecfgcreate(URL + "v1/node/register")
        printmessage("Retrying syncronisation with the server...")
        sync()
    except JSONParseException as e:
        printmessage(e,"exception")
    except urllib2.HTTPError, e:
        printmessage(e,"exception")
    except urllib2.URLError, e:
        printmessage(e,"exception")
    except httplib.HTTPException, e:
        printmessage(e,"exception")
    except Exception as e:
        printmessage(e,"exception")

def mediacheck():
    global HAS_MEDIA
    
    if HAS_MEDIA:
        return True
    else:
        return False

def forcecfgcreate(url):
    """Forces a new config file creation. Use this only if needed."""
    if isfile(CFG_PATH):
        unlink(CFG_PATH)
        createcfgfile(url)
    else:
        createcfgfile(url)

def checksum(fname, did):
    try:
        bsize = str(os.path.getsize(MEDIA_PATH + fname))        
        sendjson("v1/files/checksum", {"Deviceid":int(did),"Filename":fname,"Bytesize":bsize})
        printmessage("eCode: " + str(RESPONSE["eCode"]))
        if RESPONSE["eCode"] is not 0:
            printmessage("File " + fname + " failed checksum. It will be deleted.\n", "error")
            os.remove(MEDIA_PATH + fname)                
        else:
            printmessage("File " + fname + " passed checksum.\n")
    except urllib2.HTTPError, e:
        printmessage(e,"exception")
        removemedia(fname) 
    except urllib2.URLError, e:
        printmessage(e,"exception")
        removemedia(fname) 
    except httplib.HTTPException, e:
        printmessage(e,"exception") 
        removemedia(fname) 
        
def fetchfiles(did):
    """Fetches files from the DeCore server."""
    x=[]  
    i=0
    log = LOG_PATH + "wgetLog" + str(time.strftime("%d-%m-%Y-%H:%M:%S")) + ".log"
    f = open(CFG_FOLDER + "ToBeAdded.txt",'r')
    for line in f.readlines():
        x.extend([str(line).replace('\n',"")])  
        f.close()
    for index in range(len(x)):
        item = str(x[index]).encode('utf8')
        cmd = "wget -T 60 " + URL + "v1/files/" + item.replace(' ', "\\ ") + "?id=" + str(did) + " -P " + MEDIA_PATH + " -o " + log + " -O " + MEDIA_PATH + item.replace(' ', "\\ ")
        os.system(cmd)
        printmessage("Current item: " + item)
        checksum(item,did)   
              
def createlogfile():
    """Creates a log file each midnight."""
    global LOGGER

    LOGGER = logging.getLogger("decoreLog")
    LOGGER.setLevel(logging.DEBUG)
    handler = TimedRotatingFileHandler(LOG_NAME,
                                       when='midnight',
                                       interval=1,
                                       backupCount=7)
    LOGGER.addHandler(handler)

def printmessage(text, lvl='info'): 
    """Print specified message to log file."""
    newline = ""
    errortxt = ""
    msg = str(text)
    logoptions={
        "debug" : LOGGER.debug,
        "info" : LOGGER.info,
        "warning" : LOGGER.warning,
        "error" : LOGGER.error,
        "critical" : LOGGER.critical,
        "exception" : LOGGER.exception
    }

    if lvl is "exception":
        newline = "\n"
        errortxt = "Problem with deCore. Problem: " 

    logoptions[lvl](newline + str(lvl.upper() +' (' + str(time.strftime("%H:%M:%S") + '): ' +  errortxt + msg + newline)))

#If forceMode is set to True, then it will check orderNdelay
def updateslide(forceMode,filesArray,delaysMap):
    global SLIDE_PID
    global PROC

    if forceMode==True:
        printmessage("will Update slide for orderNdelay")

    printmessage("Updating slide..., current slide pid "+str(SLIDE_PID))

    if SLIDE_PID is not 0:   
        #Kill running slide and its child processes & Flush the framebuffer
        printmessage("Killing slide.dpa and related processes.", "debug")
        os.system("killall -9 slide.dpa")
        os.system("killall -9 fbi")
        os.system("killall -9 omxplayer")
        os.system("killall -9 omxplayer.bin")
        os.system("dd if=/dev/zero of=/dev/fb0")
        printmessage("Killed all processes and flushed the framebuffer.", "debug")
    printmessage("Updating slide.dpa...", "debug")
    newslideshow(DELAY,forceMode,filesArray,delaysMap)
    printmessage("Slide updated successfully. Running slide.", "debug")
    runslide()

def emptymedia():
    subprocess.Popen("fbi -a --noverbose /home/pi/decore/src/resources/images/nomedia.jpg", shell=True)


#delaysMap-> ["a.jpg:10,"b.jpg":15,"c.mp4":0] (filename:delay {0 means default delay will be used})
#normalde videoda delay olmayacagi icin video icin gelen delayi gormezden gel
def newslideshow(dly, forceMode, filesArray, delaysMap):
    try:
        global HAS_MEDIA

        # Create file manifest.
        filelist = [f for f in listdir(MEDIA_PATH) if isfile(join(MEDIA_PATH, f))]
        printmessage("Files in order:" + str(filesArray))

        existingFilesInOrder = filelist
        if forceMode == True and len(filelist) >= len(filesArray):
            existingFilesInOrder = []
            for f1 in filesArray:
                doesExist = False
                for f2 in filelist:
                    if f1 == f2:
                        doesExist = True
                        break
                if doesExist == True:
                    existingFilesInOrder.append(f1)
        printmessage("Found " + str(len(existingFilesInOrder)) + " items: " + ' '.join(existingFilesInOrder) + " ")

        # If filelist is empty, print a message that indicates no media was found on the node.
        if not existingFilesInOrder:
            HAS_MEDIA = False
            emptymedia()
        else:
            os.system("killall -9 fbi")
            HAS_MEDIA = True
            # Check whether there are videos in current media.
            # Images will be played ONCE if there are any videos in deCore.
            isonce = ""
            for file in existingFilesInOrder:
                if file.endswith(VIDEO_EXT):
                    isonce = "-once "
                    break

            # Definition of variables used in function.
            name = "slide.dpa"
            filepath = SLIDE_PATH + name
            delay = str(dly)
            imgList = []
            vidName = ""
            imgCombo = False

            # Script bodies that will be used while creating the slide.
            fullscript = "#!/bin/bash\ncd " + MEDIA_PATH + "\nwhile true;\ndo\n"
            imgScript = "clear\nfbi --noverbose -a -t " + delay +" "+ isonce
            vidScript = "clear\nomxplayer " + MEDIA_PATH

            # Delay cannot be zero. 15 seconds is the default interval value.
            if str(dly) is "0":
                printmessage("Invalid or unspecified delay interval, assuming a 15 seconds interval")
                delay = str(15)
            else:
                printmessage("Delay is taken as "+str(dly))

            # Beginning of the slide creation.
            for file in existingFilesInOrder:
                printmessage("Now processing file: " + file)



                currentFilesDelay = delay

                if forceMode == True:
                    if delaysMap[file] != None and delaysMap[file] != 0:
                        currentFilesDelay = str(delaysMap[file])
                        printmessage("Current file's delay is: " + currentFilesDelay)
                    elif delaysMap[file] == 0 or delaysMap[file] == "0":
                        currentFilesDelay=str(dly)

                        # Check for file extentions and generate scripts according to filetypes.
                if file.endswith(IMAGE_EXT):

                    if currentFilesDelay!=delay:
                        # Means delay is changed, generate script and start over
                        if len(imgList)>0:
                            printmessage("Delay combo broken!")
                            combinedImg = "".join(imgList)
                            fullscript = ''.join([fullscript, imgScript, combinedImg, " >/dev/null 2>&1", '\n'])
                            imgList=[]

                        imgCombo = False
                        #Update imgScript
                        imgScript = "clear\nfbi --noverbose -a -t " + currentFilesDelay + " " + isonce

                    if imgCombo:
                        printmessage("Image combo started!")
                    else:
                        printmessage("Image combo ongoing, populating image array...")
                    imgList.append(str(file).replace(' ', "\\ ") + " ")
                    imgCombo = True
                elif file.endswith(VIDEO_EXT):
                    if imgCombo:
                        printmessage("Combo broken!")
                        combinedImg = "".join(imgList)
                        fullscript = ''.join(
                            [fullscript, imgScript, combinedImg, '\n', vidScript, str(file).replace(' ', "\\ "),
                             " >/dev/null 2>&1", '\n'])
                        imgCombo = False
                        imgList=[]

                    vidName = ''.join([fullscript, vidScript, str(file).replace(' ', "\\ "), " >/dev/null 2>&1", '\n'])
                    fullscript = vidName
                else:
                    printmessage("File " + file + " has an unknown (or undefined) file format.", "warning")

            if len(imgList) > 0:
                printmessage(
                    str(len(imgList)) + " images left in array after end of operation, writing them to file...")
                combinedImg = ''.join(imgList)
                fullscript = ''.join([fullscript, imgScript, combinedImg, " >/dev/null 2>&1", '\n'])
                printmessage("Done writing remainder files...\n")

            f = open(SLIDE_PATH + name, 'w')
            f.write(fullscript + "done\nexit 0")
            f.close()

            os.system("chmod +x " + filepath)
            printmessage("Success! Slideshow has been successfully created under " + filepath + ".", "info")

    except Exception as e:
        printmessage("Aborted slide creation.\nReason was: " + e, "exception")
        if os.path.exists(filepath):
            printmessage("Removing incomplete slide file...", "warning")
            slide.close()
            os.remove(filepath)
            printmessage("Removed file successfully.", "warning")

def runslide():
    """Exectues the slide script."""
    global PROC 
    global SLIDE_PID

    filelist = [f for f in listdir(MEDIA_PATH) if isfile(join(MEDIA_PATH, f))]

    if len(filelist) is not 0:
        if isfile(SLIDE_PATH + "slide.dpa"):
            printmessage("slide.dpa found, running file.", "debug")
            os.system("dd if=/dev/zero of=/dev/fb0")
            PROC = subprocess.Popen(SLIDE_PATH + "slide.dpa", shell=False)
            SLIDE_PID = PROC.pid
        else:
            printmessage("slide.dpa was not present in directory, recreating.", "warning")
            newslideshow(DELAY,False,None,None)
            os.system("dd if=/dev/zero of=/dev/fb0")
            PROC = subprocess.Popen(SLIDE_PATH + "slide.dpa", shell=False)
            SLIDE_PID = PROC.pid
    else:
        printmessage("No suitable media was found in device!", "warning")
        emptymedia()
    
def disk_usage(pth):
    _ntuple_diskusage = collections.namedtuple('usage', 'total used free')
   
    st = os.statvfs(pth)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(total, used, free)

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def checkdir(path):
    if not os.path.exists(path):
        printmessage(path + " does not exists. Creating dir...")
        os.makedirs(path)
        printmessage(path + " has been successfully created.")
    else:
         printmessage(path + " already exists.")

def checklogpath():
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

def quitdecore(msg, expect = True):
    expected = bool(expect)
    if expected is False:
        txt = "Exiting DeCore abruptly. Reason: " + str(msg)
        printmessage(txt, "critical")
        exit(1)
    else:
        printmessage(str(msg))
        exit(0)