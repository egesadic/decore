from Tkinter import *
import tkMessageBox
import os
from random import shuffle
from os import listdir, path
from os.path import isfile, join
from tkFileDialog import askdirectory
import sys
from subprocess import call

reload(sys)
sys.setdefaultencoding('utf-8')

root = Tk()
root.wm_title("Create New Slideshow")
root.resizable(0,0)

def emptymedia():
    sys.exit("No suitable media found in DeCore.")

def newSlideshow():
    try:
        name = entryName.get()
        name = name.strip()
        cwd = os.getcwd()
        filepath = os.path.join(cwd + "/slides", name)
        mediapath = cwd + "/media"
        imgCount = 0
        vidCount = 0
        temp = ""
        init = False
        filelist = [f for f in listdir(mediapath) if isfile(join(mediapath, f))]
        if not filelist:
            emptymedia()
        else:
            lol = ''.join(filelist)
            print ("Found " + str(len(filelist)) + " items: " + lol + " ")
            if varRand.get():
                print("Random flag was on, randomizing file list...")
                shuffle(filelist)
                lol = ''.join(filelist)
                print("Randomized list: "+lol+"\n")
            delay = int(entryDelay.get())      
            fullscript = "#!/bin/bash\ncd " + mediapath + "\n"
            imgScript = "feh --quiet --preload --reload 60 -Y --slideshow-delay " + str(delay) + ".0 --full-screen --cycle-once "	
            vidScript = "omxplayer " + mediapath + "/"
            if name is "":
                tkMessageBox.showinfo("Warning", "Please name your slide.")
                print("Slide was unnamed, name your slide.")
            elif delay is "0":
                tkMessageBox.showinfo("Warning", "Please indicate a valid delay between slides.")
                print("Invalid or unspecified delay interval, assuming 15 second interval")
            else:
                slide = open(filepath + '.dpa','w')
                for file in filelist:
			        #check init flag
                    print("Now processing: " + file)
                    if init is False:
                        print ("init was false, this means this is the first media, changing flag...")
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
                slide.write(fullscript + "exit 0")	
                slide.close()
                call("chmod +x " + filepath + ".dpa", shell= True)
                print("Slide created under dir '"+filepath+".dpa'")
                tkMessageBox.showinfo("Success", "Slideshow '" + name + "' has been successfully created.")
                root.destroy()
                return 0

    except Exception as e:
        tkMessageBox.showwarning("Error", e)
        print("There was a problem, aborted slide creation.")
        if os.path.exists(filepath+'.dpa'):
            print("Removing slide file...")
            slide.close()
            os.remove(filepath+'.dpa')
            print("Removed!")
        entryDelay.delete(0, END)
        entryName.delete(0, END)
        entryDelay.insert(0, 15)
    except SystemExit as ex:
        print("No media here, stopping...")
        tkMessageBox.showwarning("Error", ex)

labelName = Label(root, text = "Slideshow Name: ")
labelName.grid(row=0, column=0, columnspan=1, sticky="w", padx=10, pady=10)
entryName = Entry(root, width=30)
entryName.grid(row=0, column=1, columnspan=1, padx=10, pady=10)
entryName.focus_set()

labelDelay = Label(root, text="Delay(sec): ")
labelDelay.grid(row=2, column=0, columnspan=1,sticky="w",padx=10,pady=10)
entryDelay = Entry(root, width=10)
entryDelay.grid(row=2, column=1, columnspan=1,sticky="w",padx=10, pady=10)

varRand = IntVar()
checkRand = Checkbutton(root, text='Randomize Media', onvalue=1, offvalue=0,
variable = varRand)
checkRand.grid(row=3, column=1, columnspan=1, sticky="w", padx=10, pady=10)

buttonCreate = Button(root, text = "OK", width = 10, command = newSlideshow)
buttonCreate.grid(row=4, column=1, columnspan=1, sticky="e", padx=10, pady=10)

mainloop()
