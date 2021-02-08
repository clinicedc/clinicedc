import os
from tempfile import mkdtemp

from ..randomizer import Randomizer

tmpdir = mkdtemp()


class MyRandomizer(Randomizer):
    name = "my_randomizer"
    model = "edc_randomization.myrandomizationlist"

    @classmethod
    def get_randomization_list_path(cls):
        return os.path.join(tmpdir, "randomization_list.csv")
