import csv
import sys
from itertools import islice
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from django.db.utils import OperationalError, ProgrammingError

from .exceptions import InvalidAssignment, RandomizationListError
from .site_randomizers import site_randomizers

style = color_style()

__all__ = ["RandomizationListVerifier"]


class RandomizationListVerifier:
    """Verifies the Randomization List against the CSV file."""

    def __init__(
        self,
        randomizer_name=None,
        randomizationlist_path: Path | str | None = None,
        randomizer_model_cls=None,
        assignment_map=None,
        fieldnames=None,
        sid_count_for_tests=None,
        required_csv_fieldnames: tuple[str, ...] | None = None,
        **kwargs,  # noqa: ARG002
    ):
        self.count: int = 0
        self.messages: list[str] = []
        self.randomizer_name: str = randomizer_name
        self.randomizer_model_cls = randomizer_model_cls
        self.randomizationlist_path: Path = Path(randomizationlist_path)
        self.assignment_map: dict = assignment_map
        self.sid_count_for_tests: int | None = sid_count_for_tests
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

            elif not self.randomizationlist_path or not self.randomizationlist_path.exists():
                self.messages.append(
                    f"Randomization list file does not exist but SIDs "
                    f"have been loaded. Expected file "
                    f"{self.randomizationlist_path}. "
                    f"Resolve this issue before using the system."
                )
            elif message := self.verify():
                self.messages.append(message)
        if self.messages and (
            "migrate" not in sys.argv
            and "makemigrations" not in sys.argv
            and "import_randomization_list" not in sys.argv
        ):
            raise RandomizationListError(", ".join(self.messages))

    def verify(self) -> str | None:
        message = None
        # read and sort from CSV file
        with self.randomizationlist_path.open(mode="r") as f:
            reader = csv.DictReader(f)
            if self.sid_count_for_tests:
                reader = islice(reader, self.sid_count_for_tests)
            all_rows = [{k: v.strip() for k, v in row.items() if k} for row in reader]
            sorted_rows = sorted(
                all_rows,
                key=lambda row: (row.get("site_name", ""), int(row.get("sid", 0))),
            )
        # compare sorted CSV length with DB
        if len(sorted_rows) != self.randomizer_model_cls.objects.all().count():
            expected_cnt = len(sorted_rows)
            actual_cnt = self.randomizer_model_cls.objects.all().count()
            message = (
                f"Randomization list count is off. Expected {expected_cnt} (CSV). "
                f"Got {actual_cnt} (model_cls). See file "
                f"{self.randomizationlist_path}. "
                f"Resolve this issue before using the system."
            )
        if not message:
            # compare sorted CSV data to DB
            for index, row in enumerate(sorted_rows, start=1):
                sys.stdout.write(f"Index: {index}, SID: {row.get('sid')}, Row: {row}\n")
                message = self.inspect_row(index - 1, row)
                if message:
                    break
        return message

    def inspect_row(self, index: int, row) -> str | None:
        """Checks SIDS, site_name, assignment, ...

        Note:Index is zero-based
        """
        message = None
        obj1 = self.randomizer_model_cls.objects.all().order_by("site_name", "sid")[index]
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
                    f"Got '{row['sid']}' != '{obj1.sid}'."
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
                        f"Got '{obj2.site_name}' != '{row['site_name']}' "
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
