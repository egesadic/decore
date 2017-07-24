from decDevice import *
from decPool import *

class Node(Device):
    """DeCore client, probably a RPi."""

    def __init__(self, id, name, pool = Pool, address = '', parent = ""):
        self.id = shortuuid.uuid()
        self.name = name
        self.pool = None
        self.address = address
        self.parent = ""
        


