from .randomizer import Randomizer
from .site_randomizers import site_randomizers


site_randomizers.register(Randomizer)
