from tempfile import mkdtemp

from edc_randomization.randomizer import Randomizer

tmpdir = mkdtemp()


class CustomRandomizer(Randomizer):
    name = "custom_randomizer"
    model = "edc_auth.customrandomizationlist"
    randomization_list_path = tmpdir
