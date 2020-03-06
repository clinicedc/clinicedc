import csv
import os
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import OperationalError, ProgrammingError
from edc_randomization.site_randomizers import site_randomizers


class RandomizationListError(Exception):
    pass


class RandomizationListVerifier:

    """Verifies the RandomizationList upon instantiation.
    """

    default_fieldnames = ["sid", "assignment", "site_name"]

    def __init__(self, randomizer_name=None, fieldnames=None):
        self.messages = []

        self.randomizer = site_randomizers.get(randomizer_name)
        if not self.randomizer:
            raise RandomizationListError(
                f"Randomizer not registered. Got `{randomizer_name}`"
            )
        self.fieldnames = fieldnames or self.default_fieldnames
        try:
            self.count = self.randomizer.model_cls().objects.all().count()
        except (ProgrammingError, OperationalError) as e:
            self.messages.append(str(e))
        else:
            if self.count == 0:
                self.messages.append(
                    "Randomization list has not been loaded. "
                    "Run the 'import_randomization_list' management command "
                    "to load before using the system. "
                    "Resolve this issue before using the system."
                )

            else:
                if not self.randomizer.get_randomization_list_path() or not os.path.exists(
                    self.randomizer.get_randomization_list_path()
                ):
                    self.messages.append(
                        f"Randomization list file does not exist but SIDs "
                        f"have been loaded. Expected file "
                        f"{self.randomizer.get_randomization_list_path()}. "
                        f"Resolve this issue before using the system."
                    )
                else:
                    message = self.verify_list()
                    if message:
                        self.messages.append(message)
        if self.messages:
            if (
                "migrate" not in sys.argv
                and "makemigrations" not in sys.argv
                and "import_randomization_list" not in sys.argv
            ):
                raise RandomizationListError(", ".join(self.messages))

    def verify_list(self):

        message = None

        with open(self.randomizer.get_randomization_list_path(), "r") as f:
            reader = csv.DictReader(f)
            for index, row in enumerate(reader):
                row = {k: v.strip() for k, v in row.items() if k}
                if index == 0:
                    continue
                message = self.inspect_row(index, row)
                if message:
                    break
        if not message:
            if self.count != index + 1:
                message = (
                    f"Randomization list count is off. Expected {index + 1} (CSV). "
                    f"Got {self.count} (model_cls). See file "
                    f"{self.randomizer.get_randomization_list_path()}. "
                    f"Resolve this issue before using the system."
                )
        return message

    def inspect_row(self, index, row):
        message = None
        obj1 = self.randomizer.model_cls().objects.all().order_by("sid")[index]
        try:
            obj2 = self.randomizer.model_cls().objects.get(sid=row["sid"])
        except ObjectDoesNotExist:
            message = f"Randomization file has an invalid SID. Got {row['sid']}"
        else:
            if obj1.sid != obj2.sid:
                message = (
                    f"Randomization list has invalid SIDs. List has invalid SIDs. "
                    f"File data does not match model data. See file "
                    f"{self.randomizer.get_randomization_list_path()}. "
                    f"Resolve this issue before using the system. "
                    f"Problem started on line {index + 1}. "
                    f'Got \'{row["sid"]}\' != \'{obj1.sid}\'.'
                )
            if not message:
                assignment = self.randomizer.get_assignment(row)
                if obj2.assignment != assignment:
                    message = (
                        f"Randomization list does not match model. File data "
                        f"does not match model data. See file "
                        f"{self.randomizer.get_randomization_list_path()}. "
                        f"Resolve this issue before using the system. "
                        f"Got '{assignment}' != '{obj2.assignment}' for sid={obj2.sid}."
                    )
                elif obj2.site_name != row["site_name"]:
                    message = (
                        f"Randomization list does not match model. File data "
                        f"does not match model data. See file "
                        f"{self.randomizer.get_randomization_list_path()}. "
                        f"Resolve this issue before using the system. "
                        f'Got \'{obj2.site_name}\' != \'{row["site_name"]}\' '
                        f"for sid={obj2.sid}."
                    )
        return message
