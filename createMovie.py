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
root.wm_title("Create New Movie Playlist")
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
        if name is "":
            tkMessageBox.showinfo("Warning", "Please name your slide.")
        elif path is "":
            tkMessageBox.showinfo("Warning", "Please select a path to your media.")
        else:
            cwd = os.getcwd()
            print(cwd)
            filepath = os.path.join(cwd+"/slides", name)
            f = open(filepath + '.dpa','w')
            f.write("#!/bin/sh\nsetterm -cursor off\nVIDEOPATH=\""+path+"\"\nSERVICE=\"omxplayer\"\nwhile [ \"x$keypress\" = \"x\" ] ; do\n\tfor entry in $VIDEOPATH/*\n\tdo\n\t\tclear\n\t\tomxplayer -r $entry\n\t\tif [[ $key = q ]]; then break; fi\n\t\texit 0\n\tdone\ndone")
            f.close()
            call("chmod +x "+name".dpa", shell=True)
            tkMessageBox.showinfo("Success", "Slideshow '"+name+"' has been successfully created.")
            root.destroy()
    except Exception as e:
         tkMessageBox.showwarning("Error", "Please try again.")
         tkMessageBox.showwarning(e)
         entryName.delete(0, END)

labelName = Label(root, text="Slideshow Name: ")
labelName.grid(row=0, column=0, columnspan=1, sticky="w", padx=10, pady=10)
entryName = Entry(root, width=30)
entryName.grid(row=0, column=1, columnspan=1, padx=10, pady=10)
entryName.focus_set()

labelNamePath = Label(root, text="Path to media: ")
labelNamePath.grid(row=1, column=0, columnspan=1, sticky="w", padx=10, pady=10)
buttonSelectFile = Button(root, textvariable=var , width = 12, command=getFileCallback)
buttonSelectFile.grid(row=1, column=1, columnspan=1,sticky="w", padx=10, pady=10)

#labelPath = Label(root, textvariable=var)
#labelPath.grid(row=1, column=1, columnspan=1, padx=10, pady=10)

#varRand = IntVar()
#checkRand = Checkbutton(root, text='Randomize Images', onvalue=1, offvalue=0, variable = varRand)
#checkRand.grid(row=3, column=1, columnspan=1, sticky="w", padx=10, pady=10)


buttonCreate = Button(root, text = "OK", width = 10, command = newImgSlideshow)
buttonCreate.grid(row=4, column=1, columnspan=1, sticky="e", padx=10, pady=10)

mainloop()
