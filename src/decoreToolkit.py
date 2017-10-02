# -*- coding: utf-8 -*-
"""Useful functions & utilites for DeCore programming."""
import subprocess
import sys
import os
import urllib2
import json
import httplib
import time
from random import shuffle
from os import listdir, path, unlink
from os.path import isfile, join
from subprocess import call
from decoreErrors import *
from abc import ABCMeta

##########################################################################################################
#                                    GLOBAL VARIABLES START HERE                                         #
##########################################################################################################  

SLIDE_PID = 0
FILELIST = []
FILES_CHANGED = "False"
IS_RANDOM = "False"
DELAY = 5
CFG_FOLDER = "/usr/decore/config/"
CFG_PATH = CFG_FOLDER + "cfgval.dc"
MEDIA_PATH = "/usr/decore/media/"
SLIDE_PATH = "/usr/decore/slides/"
URL = "http://192.168.34.120:8080/"
COOLDOWN = 5

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
            f = open(SLIDE_PATH+self.name, 'w')
            f.write(self.script+"done\nexit 0")
            f.close()
        except Exception as e:
            print e

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
        if isfile(CFG_PATH) is False:
            count = 0
            if os.path.isdir(MEDIA_PATH) is False:
                os.makedirs(MEDIA_PATH)
            if os.path.isdir(SLIDE_PATH) is False:
                os.makedirs(SLIDE_PATH)
            if os.path.isdir(CFG_FOLDER) is False:
                os.makedirs(CFG_FOLDER)
            mac = getmacadress(adapter)
            for count in range(0, 4):
                if count is 3:
                    printmessage("Cannot get MAC address, please contact support.")
                    exit(1)
                if mac is "00:00:00:00:00:00":
                    count += 1
                else:
                    printmessage ("MAC address is: "+mac)
                    data = {
                        "Mac": mac
                    }
                    break            
            #Sunucuya bağlan ve ID talep et.
            request = urllib2.Request(url, json.dumps(data))
            request.add_header('Content-Type', 'application/json')
            printmessage(url)
            tmp = urllib2.urlopen(request)
            obj = json.loads(tmp.read())
            printmessage ("Connection to the DeCore server success!")
            
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
    
    except DecoreServerConnectionException as u:
        print (u)
        sys.exit(1)
    except urllib2.HTTPError, e:
        #todo - bir daha cfg yaratıcıyı çağır
        print e
    except urllib2.URLError, e:
        #todo - URL kontrol ettir
        print e
    except httplib.HTTPException, e:
        print e
    except Exception as ex:
        #todo - Genel hata, yapacak bişey yok
        print ex

def sync():
    """Initiate a synchronisation between DeCore and the server. Requires config.json to be properly setup.""" 
    try:
        global FILES_CHANGED
        global IS_RANDOM
        global DELAY
        global OLD_FILES
        global NEW_FILES

        FILES_CHANGED = False

        if isfile(CFG_PATH):
            printmessage("Sync started with server!")
            cfgfile = open(CFG_PATH, 'r')
            device_id = cfgfile.read()
            filelist = [f for f in listdir(MEDIA_PATH) if isfile(join(MEDIA_PATH, f))]
            printmessage("Old files: "+str(filelist))
            data = {
                "Id": int(device_id), 
                "OldPaths": filelist
            }
            #print(json.loads(data))
            url = URL + "v1/node"
            
            #Sunucuya bağlan ve dosyaları talep et.
            request = urllib2.Request(url, json.dumps(data))
            request.add_header('Content-Type', 'application/json')
            FILES_CHANGED = False
            request.get_method = lambda: 'PUT'
            tmp = urllib2.urlopen(request)
                        
            #Döndürülen yanıtı oku.
            printmessage ("Connection success! Reading response...")
            response = json.loads(tmp.read())
            if response is not None:
                printmessage("Done! Getting randomization and delay values...")
                IS_RANDOM = str(response["data"]["IsRandom"])
                DELAY = str(response["data"]["Delay"])
                printmessage("Getting file list to be deleted...")
                tobedeleted = response["data"]["ToBeDeleted"]
                OLD_FILES = tobedeleted

                if tobedeleted is not None:
                    printmessage("Files to be deleted are: " +str(tobedeleted) )
                    #ToBeDeleted'den alınan dosyaları sil
                    for the_file in tobedeleted:
                        file_path = join(MEDIA_PATH, the_file)           
                        if isfile(file_path):
                            unlink(file_path)
                    printmessage ("Deleted " + str(len(tobedeleted)) + "files successfully.")
                    FILES_CHANGED = True
                else:
                    printmessage("No files to be deleted. Proceeding to add files...")

                #ToBeAdded'dan gelecek dosyaları indir ve metin dosyasına yaz
                tobeadded = response["data"]["ToBeAdded"]
                if tobeadded is not None:
                    addedFile = open(CFG_FOLDER + "ToBeAdded.txt", 'w')
                    content = ""
                    for the_file in tobeadded:
                        content = ''.join([content, URL, "v1/files/", str(the_file), '\n'])
                    addedFile.write(content)
                    addedFile.close()
                    printmessage("Fetching the files from server...")
                    fetchfiles()        
                    printmessage ("Added " + str(len(tobeadded)) + " files.")
                    FILES_CHANGED = True

                    #print("Files have been CHANGED!")
                else:
                    printmessage("No files to be added. Running .dpa file...")
                if FILES_CHANGED:
                    print("Media in this node has been changed! Rebuilding .dpa file...")
                    updateslide()            
            else:
                FILES_CHANGED = False
                raise JSONParseException("There has been a problem with the DeCore node. No changes were made.")            
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

def fetchfiles():
    """Fetches files from the DeCore server."""
    x=[]
    i=0
    f = open(CFG_FOLDER + "ToBeAdded.txt",'r')
    for line in f.readlines():
        print("Now fetching: " + str(line).replace('\n',""))
        x.extend([str(line).replace('\n',"")])  
        f.close()
    for index in range(len(x)):
        cmd="wget -c " + x[index] + " -P " + MEDIA_PATH
        print cmd
        os.system(cmd)
        
def printmessage(text, slp = 0.3):
    """Print specified message with a sensible delay."""
    print(text)
    time.sleep(slp)

def generatefilelist(path = MEDIA_PATH):
    if os.path.isdir(path):
        filelist = [f for f in listdir(path) if isfile(join(path, f))]
        return filelist
    else:
        printmessage("No such dir.")

def updateslide():
    global SLIDE_PID
    if SLIDE_PID is not 0:   
        call("kill -9 -"+str(SLIDE_PID), shell=True)
    print ("patlamadı")
    filelist = generatefilelist()
    newSlideshow(IS_RANDOM, DELAY)
    proc = subprocess.Popen(SLIDE_PATH+"slide.dpa", shell=True)
    SLIDE_PID = proc.pid
def emptymedia():
    sys.exit("No suitable media found in DeCore.")

def newSlideshow(rnd, dly):
    try:
        slide = Slide("",None,"")
        name = "slide.dpa"
        filepath = SLIDE_PATH + name
        isRandom = bool(rnd)
        delay = str(dly)
        imgCount = 0
        vidCount = 0
        temp = ""
        init = False
        filelist = generatefilelist()
        if not filelist:
            emptymedia()
        else:
            lol = ''.join(filelist)
            printmessage ("Found " + str(len(filelist)) + " items: " + lol + " ")
            if isRandom:
                printmessage("Random flag was on, randomizing file list...", 0.1)
                shuffle(filelist)
                lol = ''.join(filelist)
                printmessage("Randomized list: "+lol+"\n")     
            fullscript = "#!/bin/bash\ncd " + MEDIA_PATH + "\nwhile true;\ndo"
            imgScript = "clear\nfbi --noverbose -a -t " + delay + " -once "	
            vidScript = "clear\nomxplayer " + MEDIA_PATH 
            if delay is 0:
                printmessage("Invalid or unspecified delay interval, assuming a 15 seconds interval", 0.1)
                delay = 15
            else:
                #slide = open(filepath + '.dpa','w')
                for file in filelist:
			        #check init flag
                    printmessage("Now processing file: " + file, 0)
                    if init is False:
                        #print ("init was false, this means this is the first media, changing flag...")
				        #generate image list and vid name after init
                        init = True
                        imgList = []
                        vidName = ""
                        if file.endswith(('.jpg', '.jpeg', '.png','.gif')):
                            printmessage("first media is an image, combo started...\n", 0.1)
                            imgList.append(file + " ")
                            imgCount += 1
                            printmessage("img's appended to list, continuing process...\n", 0.1)
                        elif file.endswith(('.mp4','.h264')):
                            printmessage("first media is a video, writing to bash file...\n", 0.1)
                            vidName = ''.join([fullscript,vidScript, file, '\n'])
                            fullscript = vidName
                            vidCount += 1
                        else:
                            emptymedia()
                    else:
                        printmessage("getting rest of the media...", 0)
                        printmessage("current status: ImageCount=" + str(imgCount) + " VidCount=" + str(vidCount)+"\n", 0)
				        #stuff to do after init
				        #if both counters are equal, break the loop.
                        if vidCount == imgCount:
                            emptymedia()
				        #image list generator, break the combo if the next media in line isnt an
                        elif imgCount > vidCount:                            
                            if file.endswith(('.jpg', '.jpeg', '.png','.gif')):
                                printmessage("image combo ongoing, populating image array...", 0.1)
                                imgList.append(file + " ")
                                imgCount += 1
                                printmessage("Current combo: " + ''.join(imgList), 0)
                            elif file.endswith((".mp4",".h264")):
                                printmessage("combo broken!", 0.1)
                                imgCount = 0
                                combinedImg = "".join(imgList)                          
                                fullscript = ''.join([fullscript, imgScript, combinedImg, '\n', vidScript, file, '\n'])
                                vidCount += 1                          
                            else:						
                                emptymedia()					
                        else:
                            if file.endswith(('.mp4','.h264')):
                                temp = ''.join([fullscript,vidScript, file, '\n'])
                                fullscript = temp
                                vidCount += 1
                            elif file.endswith(('.jpg', '.jpeg', '.png','.gif')):
                                printmessage("img combo started...", 0.1)
                                vidCount = 0
                                imgList = []
                                imgList.append(file + " ")
                                imgCount += 1
                if len(imgList) > 0:
                    printmessage("\n"+str(len(imgList))+" images left in array after end of operation, writing them to file...", 0.1)
                    combinedImg = ''.join(imgList)
                    fullscript = ''.join([fullscript, imgScript, combinedImg, '\n'])
                    print("Done writing remainder files...\n")
                
                slide.name = name
                slide.script = fullscript
                slide.writeToFile()

                call("chmod +x " + filepath , shell= True)
                print("Slide created under dir '"+filepath)
                print("Success", "Slideshow '" + name + "' has been successfully created.")
                return 0

    except Exception as e:
        print e
        print("There was a problem, aborted slide creation.")
        if os.path.exists(filepath+'.dpa'):
            print("Removing slide file...")
            slide.close()
            os.remove(filepath+'.dpa')
            print("Removed!")
    except SystemExit as ex:
        print("No media here, stopping...")
        print ex
