import os
import shortuuid
from abc import ABCMeta


class decObject:
    """Base class for all decore objects."""

    __metaclass__ = ABCMeta

    def __init__(self, id ,name):
        self.id = shortuuid.uuid()
        self.name = name


