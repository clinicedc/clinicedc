from tempfile import mkdtemp

from ..randomizer import Randomizer

tmpdir = mkdtemp()


class MyRandomizer(Randomizer):
    name = "my_randomizer"
    model = "edc_randomization.myrandomizationlist"
    randomization_list_path = tmpdir


class MyOtherRandomizer(Randomizer):
    name = "my_other_randomizer"
    model = "edc_randomization.myotherrandomizationlist"
    randomization_list_path = tmpdir
