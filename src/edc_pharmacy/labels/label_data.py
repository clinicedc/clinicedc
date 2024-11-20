import random
import string


class LabelData:

    def __init__(self):
        self.gender = random.choice(["M", "F"])  # nosec B311
        self.subject_identifier = "999-99-9999-9"  # nosec B311
        self.reference = "".join(
            random.choices(string.ascii_letters.upper() + "23456789", k=6)  # nosec B311
        )
        self.sid = "12345"
        self.site_name = "AMANA"
        self.pills_per_bottle = 128
