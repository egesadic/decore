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

##########################################################################################################
#                                    GLOBAL VARIABLES START HERE                                         #
##########################################################################################################  

LOGGER = None
HAS_MEDIA = False
JSON = None
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
MEDIA_PATH = "/usr/decore/media/"
SLIDE_PATH = "/usr/decore/slides/"
URL = "http://192.168.34.11:8082/"
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
        printmessage(e,"critical")
    except urllib2.HTTPError, e:
        #todo - bir daha cfg yaratıcıyı çağır
        printmessage(e,"critical")
    except urllib2.URLError, e:
        #todo - URL kontrol ettir
        printmessage(e,"critical")
    except httplib.HTTPException, e:
        printmessage(e,"critical")
    except Exception as e:
        #todo - Genel hata, yapacak bişey yok
        printmessage(e,"critical")

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
                    printmessage("Fetching the files from server...")
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
                    printmessage("No files to be deleted. Running .dpa file...")

                if FILES_CHANGED:
                    printmessage("Media in this node has been changed! Rebuilding .dpa file...")
                    updateslide()            
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
        printmessage(e,"critical")
    except urllib2.HTTPError, e:
        printmessage(e,"critical")
    except urllib2.URLError, e:
        printmessage(e,"critical")
    except httplib.HTTPException, e:
        printmessage(e,"critical")
    except Exception as e:
        printmessage(e,"critical")

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
        cmd = "wget -T 60 " + URL + "v1/files/" + str(x[index]).replace(' ', "\\ ") + "?id=" + str(did) + " -P " + MEDIA_PATH + " -o " + log + " -O " + MEDIA_PATH + str(x[index]).replace(' ', "\\ ")
        os.system(cmd)
        bsize = os.path.getsize(MEDIA_PATH + str(x[index])) 
        sendjson("/v1/files/checksum", {"Deviceid":did,"Filename":str(x[index]),"Bytesize": bsize})
        if RESPONSE["ecode"] is 0:
            printmessage("File " + str(x[index] + " passed checksum"))
        else:
            printmessage("File " + str(x[index] + " failed checksum. It will be deleted.", "error"))
            os.remove(MEDIA_PATH + str(x[index]))

def sendjson(domain, data, method='POST')
    global RESPONSE
    dest = URL + domain

    json = json.dumps(data)
    printmessage("JSON created with parameters: " + str(json))

    #Sunucuya bağlan ve dosyaları talep et.
    request = urllib2.Request(dest, json, {'Content-Type': 'application/json'} )
    printmessage("JSON encoded. Starting server connection.")
    request.get_method = lambda: method
    printmessage("Connecting to URL: " + url)
    tmp = urllib2.urlopen(request)
    RESPONSE = json.loads(tmp.read())

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

def printmessage(text, lvl="info"):
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
    }

    if lvl is "critical":
        newline = "\n"
        errortxt = "Problem with deCore. Problem: " 

    logoptions[lvl](newline + str(lvl.upper() +' (' + str(time.strftime("%H:%M:%S") + '): ' +  errortxt + msg + newline)))

def updateslide():
    global SLIDE_PID
    global PROC 

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
    newslideshow(DELAY)
    printmessage("Slide updated successfully. Running slide.", "debug")
    runslide()

def emptymedia():
    subprocess.Popen("fbi --noverbose /home/pi/decore/src/resources/images/nomedia.jpg", shell=True)

def newslideshow(dly):
    try:
        global HAS_MEDIA

        #Create file manifest.
        filelist = [f for f in listdir(MEDIA_PATH) if isfile(join(MEDIA_PATH, f))]
        printmessage ("Found " + str(len(filelist)) + " items: " + ' '.join(filelist) + " ")
           
        #If filelist is empty, print a message that indicates no media was found on the node.
        if not filelist:
            HAS_MEDIA = False
            emptymedia()
        else:
            os.system("killall -9 fbi")
            HAS_MEDIA = True
            #Check whether if there are videos in current media.
            #Images will be played ONCE if there are any.
            isonce = ""
            for file in filelist:
                if file.endswith(VIDEO_EXT):
                    isonce = " -once "
                    break

            #Definition of variables used in function.
            name = "slide.dpa"
            filepath = SLIDE_PATH + name
            #isRandom = bool(rnd)
            delay = str(dly) + " "
            imgCount = 0
            imgList = []
            vidCount = 0
            vidName = ""            
            temp = ""       

            #Script bodies that will be used while creating the slide. 
            fullscript = "#!/bin/bash\ncd " + MEDIA_PATH + "\nwhile true;\ndo\n"
            imgScript = "clear\nfbi --noverbose -a -t " + delay + isonce
            vidScript = "clear\nomxplayer " + MEDIA_PATH

            #Delay cannot be zero. 15 seconds is the default interval value.
            if str(dly) is "0":
                    printmessage("Invalid or unspecified delay interval, assuming a 15 seconds interval")
                    delay = str(15)
            
            #Files are randomized in order if the RANDOM flag was set.
            ''' if isRandom:
                printmessage("Random flag was on, randomizing file list...", 0.1)
                shuffle(filelist)
                printmessage("Randomized list: " + ''.join(filelist) + "\n") '''

            #Beginning of the slide creation.                                                    
            for file in filelist:
                printmessage("Now processing file: " + file)
                printmessage("current status: ImageCount=" + str(imgCount) + " VidCount=" + str(vidCount)+"\n")
                
                if imgCount == vidCount:                  
                    if file.endswith(IMAGE_EXT):
                        #printmessage("first media is an image, combo started...\n", 0.1)
                        imgList.append(str(file).replace(' ', "\\ ")  + " ")
                        imgCount += 1
                        #printmessage("img's appended to list, continuing process...\n", 0.1)
                    elif file.endswith(VIDEO_EXT):
                        #printmessage("first media is a video, writing to bash file...\n", 0.1)
                        vidName = ''.join([fullscript,vidScript, str(file).replace(' ', "\\ ") ," >/dev/null 2>&1" , '\n'])
                        fullscript = vidName
                        vidCount += 1
                    else:
                        printmessage("File " + file + "has an unknown (or undefined) file format.", "warning")
                
                #image list generator, break the combo if the next media in line isnt an
                elif imgCount > vidCount:                            
                    if file.endswith(IMAGE_EXT):
                        printmessage("image combo ongoing, populating image array...")
                        imgList.append(str(file).replace(' ', "\\ ") + " ")
                        imgCount += 1
                        printmessage("Current combo: " + ''.join(imgList))
                    elif file.endswith(VIDEO_EXT):
                        printmessage("combo broken!")
                        imgCount = 0
                        combinedImg = "".join(imgList)                          
                        fullscript = ''.join([fullscript, imgScript, combinedImg, '\n', vidScript, str(file).replace(' ', "\\ "), " >/dev/null 2>&1" , '\n'])
                        vidCount += 1                          
                    else:						
                        printmessage("File " + file + "has an unknown (or undefined) file format.", "warning")

                elif vidCount > imgCount:
                    if file.endswith(VIDEO_EXT):
                        temp = ''.join([fullscript,vidScript, str(file).replace(' ', "\\ "), " >/dev/null 2>&1", '\n'])
                        fullscript = temp
                        vidCount += 1
                    elif file.endswith(IMAGE_EXT):
                        printmessage("img combo started...")
                        vidCount = 0
                        imgList = []
                        imgList.append(str(file).replace(' ', "\\ ")  + " ")
                        imgCount += 1
                    else:						
                        printmessage("File " + file + "has an unknown (or undefined) file format.", "warning")
            
            if len(imgList) > 0:
                printmessage(str(len(imgList))+" images left in array after end of operation, writing them to file...")
                combinedImg = ''.join(imgList)
                fullscript = ''.join([fullscript, imgScript, combinedImg, " >/dev/null 2>&1", '\n'])
                printmessage("Done writing remainder files...\n")
            
            f = open(SLIDE_PATH + name, 'w')
            f.write(fullscript + "done\nexit 0")
            f.close()

            os.system("chmod +x " + filepath)
            printmessage("Success! Slideshow " + name + " has been successfully created under " + filepath + ".", "info")

    except Exception as e:
        printmessage("Aborted slide creation.\nReason was: " + e, "critical")
        if os.path.exists(filepath):
            printmessage("Removing incomplete slide file...", "warning")
            slide.close()
            os.remove(filepath)
            printmessage("Removed file successfully.", "warning")
    except SystemExit as ex:
        printmessage(ex, "warning")

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
            newslideshow(DELAY)
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