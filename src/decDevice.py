from decPool import Pool, decObject

class Device(decObject):
    """Base class for all DeCore devices."""

    def __init__(self, name, pool = Pool, address = ""):
        super(self.__class__, self).__init__(id)
        self.name = name
        self.pool = None
        self.address = address

