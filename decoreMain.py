import os
import Tkinter
from PIL import Image, ImageTk
from tkFileDialog import askopenfilename
import sys
from subprocess import call
reload(sys)
sys.setdefaultencoding('utf-8')

root = Tkinter.Tk()
root.resizable(0,0)
root.wm_title("DeCORE")
#root.attributes("-fullscreen", True) -------FULLSCREEN

cwd = "/home/pi/Public/DeCore/"

img = ImageTk.PhotoImage(Image.open(cwd+"decore.png"))
background = Tkinter.Label(root, image = img)
background.grid(row=0, column=1, columnspan=2)
#background.place(x=0, y=0, relwidth=1, relheight=1) -----BACKGROUND CODE

optionsNormal = {}
optionsNormal ['defaultextension'] = '.dpa'
optionsNormal['filetypes'] = [('DeCore Files', '.dpa')]
optionsNormal ['initialdir'] = cwd+"/slides"

optionsPPT = {}
optionsPPT ['defaultextension'] = '.pptx'
optionsPPT['filetypes'] = [('.ppt Files', '.ppt'), ('.pptx Files', '.pptx'), ('.pps Files', '.pps'), ('.ppsx Files', '.ppsx')]
optionsPPT ['initialdir'] = cwd+"/slides"


def disableButtons():
    for w in root.winfo_children():
        w.configure(state="disabled")
def enableButtons():
    for wt in root.winfo_children():
        wt.configure(state="normal")

def startShow():
    try:
        disableButtons()
        root.wm_state('iconic')
        filename = askopenfilename(**optionsNormal)
        if not filename:
            print(filename)
            enableButtons()
        else:
            call(filename, shell=True)
            print(filename)
            enableButtons()
    except Exception as e:
        raise

def createShow():
    disableButtons()
    #os.system("python "+cwd+"createSlide.py")
    call("python "+ cwd+ "createSlide.py", shell=True)
    enableButtons()

def createMov():
    disableButtons()
    call("python "+ cwd+ "createMovie.py", shell=True)
    enableButtons()
    
def pptShow():
    disableButtons()
    filename = askopenfilename(**optionsPPT)
    print(filename)
    if not filename:
        enableButtons()
    else:
        call("soffice --show --invisible "+filename, shell=True)
        print(filename)
        enableButtons()


buttonStart = Tkinter.Button(root, text="Start Slideshow...", command=startShow)
buttonStart.grid(row=1, column=1, columnspan=2, sticky="W"+"E", padx=0, )
buttonCreate = Tkinter.Button(root, text="Create New Slideshow...", command=createShow)
buttonCreate.grid(row=2, column=1, columnspan=2, sticky="W"+"E", padx=0)
buttonMov = Tkinter.Button(root, text="Create New Playlist...", command=createMov)
buttonMov.grid(row=3, column=1, columnspan=2, sticky="W"+"E", padx=0)
buttonPPT = Tkinter.Button(root, text="Open .ppt/.pptx file...", command=pptShow)
buttonPPT.grid(row=4, column=1, columnspan=2, sticky="W"+"E", padx=0)


# Code to add widgets will go here...
root.mainloop()
