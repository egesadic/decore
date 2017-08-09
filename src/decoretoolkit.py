# -*- coding: utf-8 -*-
"""Useful functions & utilites for DeCore programming."""
import os
import tkMessageBox
from abc import ABCMeta
import shortuuid

class decObject:
    """Base class for all decore objects."""
    __metaclass__ = ABCMeta
    def __init__(self, id = shortuuid.ShortUUID ,name = ""):
        self.id = None
        self.name = name

class Pool(decObject):
    """Class for handling slide pools."""

class Device(decObject):
    """Base class for all DeCore devices."""
    def __init__(self, name, pool = Pool, address = ""):
        self.id = shortuuid.uuid()
        self.name = name
        self.pool = None
        self.address = address

class Server(Device):
    """DeCore local server class. Inherits Device class."""
    pass
class Node(Device):
    """DeCore client, probably a RPi. Inherits Device class."""
    def __init__(self, name, pool = Pool, address = '', parent = ""):
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
            
def getmacadress(interface):
    """Gets the MAC address of specified device."""
    # Return the MAC address of interface
    try:
        mac = open('/sys/class/net/' + interface + '/address').read()
    except Exception:
        mac = "00:00:00:00:00:00"
    return mac[0:17]