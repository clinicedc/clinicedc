import sys

from django.conf import settings

if getattr(settings, "EDC_RANDOMIZATION_REGISTER_DEFAULT_RANDOMIZER", True):
    from .randomizer import Randomizer
    from .site_randomizers import site_randomizers

    site_randomizers.register(Randomizer)
else:
    sys.stdout.write("  -> skipping")
