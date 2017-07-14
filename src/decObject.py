import os
import shortuuid
from abc import ABCMeta


class decObject:
    """Base class for all decore objects."""

    __metaclass__ = ABCMeta

    def __init__(self, id = shortuuid.ShortUUID ,name = ""):
        self.id = None
        self.name = name


