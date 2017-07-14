from decDevice import *
from decPool import *

class Node(Device):
    """DeCore client, probably a RPi."""

    def __init__(self, name, pool = Pool, address = '', parent = ""):
        super(self.__class__, self).__init__(id)
        self.name = name
        self.pool = None
        self.address = address
        self.parent = ""
        


