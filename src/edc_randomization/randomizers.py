from .randomizer import Randomizer
from .site_randomizers import site_randomizers
from django.conf import settings

if getattr(settings, "EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER", True):
    site_randomizers.register(Randomizer)
