import os

from tempfile import mkdtemp

from edc_randomization.randomizer import Randomizer

tmpdir = mkdtemp()


class CustomRandomizer(Randomizer):
    name = "custom_randomizer"
    model = "edc_auth.customrandomizationlist"

    @classmethod
    def get_randomization_list_path(cls):
        return os.path.join(tmpdir, "randomization_list.csv")
