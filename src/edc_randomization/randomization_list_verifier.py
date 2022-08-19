import csv
import os
import sys
from typing import List, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from django.db.utils import OperationalError, ProgrammingError

from .site_randomizers import site_randomizers

style = color_style()


class RandomizationListError(Exception):
    pass


class InvalidAssignment(Exception):
    pass


class RandomizationListVerifier:

    """Verifies the Randomization List against the CSV file."""

    def __init__(
        self,
        randomizer_name=None,
        randomizationlist_path=None,
        randomizer_model_cls=None,
        assignment_map=None,
        fieldnames=None,
        sid_count_for_tests=None,
        required_csv_fieldnames: Optional[List[str]] = None,
        **kwargs,
    ):
        self.count: int = 0
        self.messages: List[str] = []
        self.randomizer_name: str = randomizer_name
        self.randomizer_model_cls = randomizer_model_cls
        self.randomizationlist_path: str = randomizationlist_path
        self.assignment_map: dict = assignment_map
        self.sid_count_for_tests: Optional[int] = sid_count_for_tests
        self.required_csv_fieldnames = required_csv_fieldnames

        randomizer_cls = site_randomizers.get(randomizer_name)
        if not randomizer_cls:
            raise RandomizationListError(f"Randomizer not registered. Got `{randomizer_name}`")
        self.fieldnames = fieldnames or self.required_csv_fieldnames
        try:
            self.count = self.randomizer_model_cls.objects.all().count()
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
                if not self.randomizationlist_path or not os.path.exists(
                    self.randomizationlist_path
                ):
                    self.messages.append(
                        f"Randomization list file does not exist but SIDs "
                        f"have been loaded. Expected file "
                        f"{self.randomizationlist_path}. "
                        f"Resolve this issue before using the system."
                    )
                else:
                    if message := self.verify():
                        self.messages.append(message)
        if self.messages:
            if (
                "migrate" not in sys.argv
                and "makemigrations" not in sys.argv
                and "import_randomization_list" not in sys.argv
            ):
                raise RandomizationListError(", ".join(self.messages))

    def verify(self) -> Optional[str]:
        message = None
        with open(self.randomizationlist_path, "r") as f:
            reader = csv.DictReader(f)
            for index, row in enumerate(reader, start=1):
                row = {k: v.strip() for k, v in row.items() if k}
                message = self.inspect_row(index - 1, row)
                if message:
                    break
                if self.sid_count_for_tests and index == self.sid_count_for_tests:
                    break
        if not message:
            if self.count != index:
                message = (
                    f"Randomization list count is off. Expected {index} (CSV). "
                    f"Got {self.count} (model_cls). See file "
                    f"{self.randomizationlist_path}. "
                    f"Resolve this issue before using the system."
                )
        return message

    def inspect_row(self, index: int, row) -> Optional[str]:
        """Checks SIDS, site_name, assignment, ...

        Note:Index is zero-based
        """
        message = None
        obj1 = self.randomizer_model_cls.objects.all().order_by("sid")[index]
        try:
            obj2 = self.randomizer_model_cls.objects.get(sid=row["sid"])
        except ObjectDoesNotExist:
            message = f"Randomization file has an invalid SID. Got {row['sid']}"
        else:
            if obj1.sid != obj2.sid:
                message = (
                    f"Randomization list has invalid SIDs. List has invalid SIDs. "
                    f"File data does not match model data. See file "
                    f"{self.randomizationlist_path}. "
                    f"Resolve this issue before using the system. "
                    f"Problem started on line {index + 1}. "
                    f'Got \'{row["sid"]}\' != \'{obj1.sid}\'.'
                )
            if not message:
                assignment = self.get_assignment(row)
                if obj2.assignment != assignment:
                    message = (
                        f"Randomization list does not match model. File data "
                        f"does not match model data. See file "
                        f"{self.randomizationlist_path}. "
                        f"Resolve this issue before using the system. "
                        f"Got '{assignment}' != '{obj2.assignment}' for sid={obj2.sid}."
                    )
                elif obj2.site_name != row["site_name"]:
                    message = (
                        f"Randomization list does not match model. File data "
                        f"does not match model data. See file "
                        f"{self.randomizationlist_path}. "
                        f"Resolve this issue before using the system. "
                        f'Got \'{obj2.site_name}\' != \'{row["site_name"]}\' '
                        f"for sid={obj2.sid}."
                    )
        return message

    def get_assignment(self, row) -> str:
        """Returns assignment (text) after checking validity."""
        assignment = row["assignment"]
        if assignment not in self.assignment_map:
            raise InvalidAssignment(
                "Invalid assignment. Expected one of "
                f"{list(self.assignment_map.keys())}. "
                f"Got `{assignment}`. "
                f"See randomizer `{self.randomizer_name}`. "
            )
        return assignment

    def get_allocation(self, row) -> int:
        """Returns an integer allocation for the given
        assignment or raises.
        """
        assignment = self.get_assignment(row)
        return self.assignment_map.get(assignment)
