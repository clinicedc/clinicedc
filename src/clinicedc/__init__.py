from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("clinicedc")
except PackageNotFoundError:
    __version__ = "develop"
