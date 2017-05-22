# -*- coding: utf-8 -*-
from Tkinter import *
import tkMessageBox
import os
from tkFileDialog import askdirectory
import sys
from subprocess import call

reload(sys)
sys.setdefaultencoding('utf-8')

root = Tk()
root.wm_title("Create New Image Slideshow")
root.resizable(0,0)
#root.geometry('{}x{}'.format(600, 400))

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
    filename = askdirectory() #askopenfilename()  show an "Open" dialog box and return the path to the selected file
    var.set(filename)

    buttonSelectFile.config(width=len(var.get()))
    if buttonSelectFile.winfo_width()>28:
        buttonSelectFile.config(width=28)
        tmp.set(filename)
        var.set(str(tmp.get())[:24]+"...")
    root.update_idletasks()
    enableButtons()
    print(filename)

def newImgSlideshow():
    try:
        name = entryName.get()
        path = tmp.get()
        delay = int(str(entryDelay.get()))
        if name is "":
            tkMessageBox.showinfo("Warning", "Please name your slide.")
        elif path is "":
            tkMessageBox.showinfo("Warning", "Please select a path to your images.")
        elif delay is "":
            tkMessageBox.showinfo("Warning", "Please indicate a delay between slides.")
        else:
            cwd = os.getcwd()
            print(cwd)
            filepath = os.path.join(cwd+"/slides", name)
            f = open(filepath + '.dpa','w')

            if varRand.get():
                rand = " --randomize"
            else:
                rand = ""

            if varFS.get():
                fs = " --full-screen"
            else:
                fs = ""
            f.write("#!/bin/bash\nDISPLAY=:0.0 XAUTHORITY=/home/pi/.Xauthority /usr/bin/feh --quiet --preload --reload 60 -Y --slideshow-delay "+str(delay)+".0 "+fs+rand+" "+path)
            f.close()
            call("chmod +x "+name".dpa", shell=True)
            tkMessageBox.showinfo("Success", "Slideshow '"+name+"' has been successfully created.")
            root.destroy()
    except Exception as e:
         tkMessageBox.showwarning("Error", "Please try again.")
         entryDelay.delete(0, END)
         entryName.delete(0, END)
         entryDelay.insert(0, 15)

labelName = Label(root, text="Slideshow Name: ")
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

varFS = IntVar()
checkFscreen = Checkbutton(root, text='Fullscreen', onvalue=1, offvalue=0,variable = varFS)
checkFscreen.grid(row=3, column=0, columnspan=1,sticky="w", padx=10, pady=10)

varRand = IntVar()
checkRand = Checkbutton(root, text='Randomize Images', onvalue=1, offvalue=0, variable = varRand)
checkRand.grid(row=3, column=1, columnspan=1, sticky="w", padx=10, pady=10)


buttonCreate = Button(root, text = "OK", width = 10, command = newImgSlideshow)
buttonCreate.grid(row=4, column=1, columnspan=1, sticky="e", padx=10, pady=10)

mainloop()
