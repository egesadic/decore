# -*- coding: utf-8 -*-
import os
import shortuuid
import tkMessageBox
from abc import ABCMeta

class decObject:
    """Base class for all decore objects."""
    __metaclass__ = ABCMeta
    def __init__(self, id = shortuuid.ShortUUID ,name = ""):
        self.id = None
        self.name = name

class Pool(decObject):
    """description of class"""

class Device(decObject):
    """Base class for all DeCore devices."""
    def __init__(self, name, pool = Pool, address = ""):
        self.id = shortuuid.uuid()
        self.name = name
        self.pool = None
        self.address = address

class Server(decObject):
    """description of class"""
    pass
class Node(Device):
    """DeCore client, probably a RPi."""
    def __init__(self, id, name, pool = Pool, address = '', parent = ""):
        self.id = shortuuid.uuid()
        self.name = name
        self.pool = None
        self.address = address
        self.parent = ""

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