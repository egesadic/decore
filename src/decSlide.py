from decObject import *
from decNode import *
import tkMessageBox
import os

class Slide(decObject):
    """DeCore slide object"""

    def __init__(self, id, name = "", node = Node, script = "" ):
        self.id = shortuuid.uuid()
        self.name = name
        self.node = None
        self.script = script

    def writeToFile(self):
        try:
            cwd = os.getcwd()+'\slides/'
            f = open(cwd+self.name+'.dpa', 'w')
            f.write(self.script+"exit 0")
            f.close()
        except Exception as e:
            tkMessageBox.showinfo("this",e)

