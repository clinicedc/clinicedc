from tempfile import mkdtemp

from edc_randomization.randomizer import Randomizer

tmpdir = mkdtemp()


class CustomRandomizer(Randomizer):
    name = "custom_randomizer"
    model = "clinicedc_tests.customrandomizationlist"
    randomizationlist_folder = tmpdir
