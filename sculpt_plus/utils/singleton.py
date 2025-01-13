from collections import defaultdict

import bpy
from bpy.types import Context


class Singleton:
    _instance = None

    @classmethod
    def get(cls):
        """ Get a Singleton instance for this class. """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
