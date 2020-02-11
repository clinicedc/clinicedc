import pdb

from django.conf import settings

from .site_randomizers import site_randomizers

if getattr(settings, "EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER", True):
    from .randomizer import Randomizer

    site_randomizers.register(Randomizer)
