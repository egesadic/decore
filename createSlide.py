# -*- coding: utf-8 -*-
from Tkinter import *
import tkMessageBox
import os
from os import listdir, path
from os.path import isfile, join
from tkFileDialog import askdirectory
import sys
from subprocess import call

reload(sys)
sys.setdefaultencoding('utf-8')

root = Tk()
root.wm_title("Create New Image Slideshow")
root.resizable(0,0)

var = StringVar()
tmp = StringVar()
var.set('Select Path...')

def disableButtons():
    for w in root.winfo_children():
        w.configure(state="disabled")
def enableButtons():
    for wt in root.winfo_children():
        wt.configure(state="normal")

#Acilan ikinci pencere kontrollerini disable ettim
def getFileCallback():
    disableButtons()
    filename = askdirectory() #askopenfilename() show an "Open" dialog box and return the path to the
                              #selected file
    var.set(filename)

    buttonSelectFile.config(width=len(var.get()))
    if buttonSelectFile.winfo_width() > 28:
        buttonSelectFile.config(width=28)
        tmp.set(filename)
        var.set(str(tmp.get())[:24] + "...")
    root.update_idletasks()
    enableButtons()
    print(filename)

def newSlideshow():
    try:
        name = entryName.get()
        cwd = os.getcwd()
        mediapath = cwd+"/media"
        imgCount = 0
        vidCount = 0
        index = 0
        temp = ""
        init = False
        filelist = [f for f in listdir(mediapath) if isfile(join(mediapath, f))]
        delay = int(str(entryDelay.get()))
        lol = ''.join(filelist)
        if lol is "":
            print("nothing here man")
        else:
            print ("Found " + str(len(filelist)) + " items: " + lol + " ")
        fullscript = "#!/bin/bash\n"
        imgScript = "DISPLAY=:0.0 XAUTHORITY=/home/pi/.Xauthority /usr/bin/feh --quiet --preload --reload 60 -Y --slideshow-delay " + str(delay) + ".0 --full-screen --cycle-once "	
        vidScript = "omxplayer " + mediapath + "/"
        if name is "":
            tkMessageBox.showinfo("Warning", "Please name your slide.")
            print("Slide was unnamed, name your slide.")
        elif path is "":
            tkMessageBox.showinfo("Warning", "Please select a path to your images.")
        elif delay is "0":
            tkMessageBox.showinfo("Warning", "Please indicate a valid delay between slides.")
            print("Invalid or unspecified delay interval, assuming 15 second interval")
        else:
            print(cwd)
            filepath = os.path.join(cwd + "/slides", name)
            slide = open(filepath + '.dpa','w')
            for file in filelist:
			    #check init flag
                print("Now processing: " + file)
                if init is False:
                    print ("init was false, this means this is the first media, flagging...")
					#generate image list and vid name after init
                    init = True
                    imgList = []
                    vidName = ""
                    if file.endswith(('.jpg', '.jpeg', '.png','.gif')):
                        print("first media is an image, combo started...\n")
                        imgList.append(str(file + " "))
                        imgCount += 1
                        filelist.pop(index)
                        index += 1
                        #print("img's appended, combo started with " + ''.join(imgList+ " "))
                    elif file.endswith(('.mp4','.h264')):
                        print("first media is a video, writing to bash file...\n")
                        vidName = ''.join([fullscript,vidScript, file, '\n'])
                        fullscript = vidName
                        vidCount += 1
                        filelist.pop(index)
                        index += 1
                    else:
                        print("nothing's here...")
                        tkMessageBox.showinfo("Warning", "No suitable media found.")
                else:
                    print("getting rest of the media...")
                    print("current status: ImageCount=" + str(imgCount) + " VidCount=" + str(vidCount))
					#stuff to do after init
					#if both counters are equal, break the loop.
                    if vidCount == imgCount:
                        print("nothing's here...")
                        tkMessageBox.showinfo("Warning", "No suitable media found.")
					#image list generator, break the combo if the next media in line isnt an
                    elif imgCount > vidCount:
                        print("image combo ongoing, populating image array...\n")
                        if file.endswith(('.jpg', '.jpeg', '.png','.gif')):
                            imgList.append(file+" ")
                            imgCount += 1
                            filelist.pop(index)
                            index += 1
                            print("Current combo: " + ''.join(imgList))
                        elif file.endswith((".mp4",".h264")):
                           print("combo broken!")
                           imgCount = 0
                           combinedImg = "".join(imgList+" ")                          
                           fullscript = ''.join([fullscript, imgScript, combinedImg, '\n', vidScript, file, '\n'])
                           vidCount += 1
                           filelist.pop(index)
                           index += 1
                        else:						
                            tkMessageBox.showinfo("Warning", "No suitable media found.")					
                    else:
                        if file.endswith(('.mp4','.h264')):
                            temp = ''.join([fullscript,vidScript, file, '\n'])
                            fullscript = temp
                            filelist.pop(index)
                            index += 1
                        elif file.endswith(('.jpg', '.jpeg', '.png','.gif')):
                            vidCount = 0
                            imgList = []
                            imgList.append(file + " ")
                            imgCount += 1
                            filelist.pop(index)
                            index += 1
                var = len(filelist)
                if var == 1:
                    combinedImg = "".join(imgList+" ")
                    fullscript = ''.join([fullscript, imgScript, combinedImg, '\n'])		
            slide.write(fullscript + "\nexit 0")	
            slide.close()
            call("chmod +x " + filepath + ".dpa", shell= True)
            tkMessageBox.showinfo("Success", "Slideshow '" + name + "' has been successfully created.")
            root.destroy()

    except Exception as e:
        tkMessageBox.showwarning("Error", e)
        print("There was a problem, aborted slide creation.")
        entryDelay.delete(0, END)
        entryName.delete(0, END)
        entryDelay.insert(0, 15)

labelName = Label(root, text = "Slideshow Name: ")
labelName.grid(row=0, column=0, columnspan=1, sticky="w", padx=10, pady=10)
entryName = Entry(root, width=30)
entryName.grid(row=0, column=1, columnspan=1, padx=10, pady=10)
entryName.focus_set()

labelNamePath = Label(root, text="Path to images: ")
labelNamePath.grid(row=1, column=0, columnspan=1, sticky="w", padx=10, pady=10)
buttonSelectFile = Button(root, textvariable=var , width = 12, command=getFileCallback)
buttonSelectFile.grid(row=1, column=1, columnspan=1,sticky="w", padx=10, pady=10)

#labelPath = Label(root, textvariable=var)
#labelPath.grid(row=1, column=1, columnspan=1, padx=10, pady=10)
labelDelay = Label(root, text="Delay(sec): ")
labelDelay.grid(row=2, column=0, columnspan=1,sticky="w",padx=10,pady=10)
entryDelay = Entry(root, width=10)
entryDelay.grid(row=2, column=1, columnspan=1,sticky="w",padx=10, pady=10)

#varFS = IntVar()
#checkFscreen = Checkbutton(root, text='Fullscreen', onvalue=1,
#offvalue=0,variable = varFS)
#checkFscreen.grid(row=3, column=0, columnspan=1,sticky="w", padx=10, pady=10)

#varRand = IntVar()
#checkRand = Checkbutton(root, text='Randomize Images', onvalue=1, offvalue=0,
#variable = varRand)
#checkRand.grid(row=3, column=1, columnspan=1, sticky="w", padx=10, pady=10)
buttonCreate = Button(root, text = "OK", width = 10, command = newSlideshow)
buttonCreate.grid(row=4, column=1, columnspan=1, sticky="e", padx=10, pady=10)

mainloop()
