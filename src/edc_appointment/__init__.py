import os
from importlib.metadata import version

__version__ = version(os.getcwd().split(os.sep)[-1])
