from decoreToolkit import Slide, MEDIA_PATH, SLIDE_PATH, IS_RANDOM, DELAY, printmessage
import os
from random import shuffle
from os import listdir, path
from os.path import isfile, join
import sys
from subprocess import call

def emptymedia():
    sys.exit("No suitable media found in DeCore.")

def newSlideshow(rnd, dly):
    try:
        slide = Slide("",None,"")
        name = "slide.dpa"
        filepath = SLIDE_PATH + name
        isRandom = bool(rnd)
        delay = int(dly)
        imgCount = 0
        vidCount = 0
        temp = ""
        init = False
        filelist = [f for f in listdir(MEDIA_PATH) if isfile(join(MEDIA_PATH, f))]
        if not filelist:
            emptymedia()
        else:
            lol = ''.join(filelist)
            print ("Found " + str(len(filelist)) + " items: " + lol + " ")
            if isRandom:
                print("Random flag was on, randomizing file list...")
                shuffle(filelist)
                lol = ''.join(filelist)
                print("Randomized list: "+lol+"\n")     
            fullscript = "#!/bin/bash\ncd " + MEDIA_PATH + "\nwhile true;\ndo"
            imgScript = "clear\nfbi --noverbose -a -t " + str(delay) + " -once "	
            vidScript = "clear\nomxplayer " + MEDIA_PATH 
            if delay is 0:
                print("Invalid or unspecified delay interval, assuming a 15 seconds interval")
                delay = 15
            else:
                #slide = open(filepath + '.dpa','w')
                for file in filelist:
			        #check init flag
                    print("Now processing file: " + file)
                    if init is False:
                        #print ("init was false, this means this is the first media, changing flag...")
				        #generate image list and vid name after init
                        init = True
                        imgList = []
                        vidName = ""
                        if file.endswith(('.jpg', '.jpeg', '.png','.gif')):
                            print("first media is an image, combo started...\n")
                            imgList.append(file + " ")
                            imgCount += 1
                            print("img's appended to list, continuing process...\n")
                        elif file.endswith(('.mp4','.h264')):
                            print("first media is a video, writing to bash file...\n")
                            vidName = ''.join([fullscript,vidScript, file, '\n'])
                            fullscript = vidName
                            vidCount += 1
                        else:
                            emptymedia()
                    else:
                        print("getting rest of the media...")
                        print("current status: ImageCount=" + str(imgCount) + " VidCount=" + str(vidCount)+"\n")
				        #stuff to do after init
				        #if both counters are equal, break the loop.
                        if vidCount == imgCount:
                            emptymedia()
				        #image list generator, break the combo if the next media in line isnt an
                        elif imgCount > vidCount:                            
                            if file.endswith(('.jpg', '.jpeg', '.png','.gif')):
                                print("image combo ongoing, populating image array...")
                                imgList.append(file + " ")
                                imgCount += 1
                                print("Current combo: " + ''.join(imgList))
                            elif file.endswith((".mp4",".h264")):
                                print("combo broken!")
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
                                print("img combo started...")
                                vidCount = 0
                                imgList = []
                                imgList.append(file + " ")
                                imgCount += 1
                if len(imgList) > 0:
                    print("\n"+str(len(imgList))+" images left in array after end of operation, writing them to file...")
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
