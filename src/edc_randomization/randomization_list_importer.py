import csv
import os
import sys
from pprint import pprint
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from tqdm import tqdm

from .randomization_list_verifier import RandomizationListVerifier

style = color_style()


class RandomizationListImportError(Exception):
    pass


class RandomizationListAlreadyImported(Exception):
    pass


class InvalidAssignment(Exception):
    pass


class RandomizationListImporter:
    """Imports upon instantiation a formatted randomization CSV file
    into model RandomizationList.

    default CSV file is the project's randomization_list.csv

    name: name of randomizer, e.g. "default"

    To import SIDS from CSV for the first time:

        from edc_randomization.randomization_list_importer import RandomizationListImporter

        RandomizationListImporter(name='default', add=False, dryrun=False)

        # note: if this is not the first time you will get:
        # RandomizationListImportError: Not importing CSV.
        # edc_randomization.randomizationlist model is not empty!

    To add additional sids from CSV without touching existing model instances:

        from edc_randomization.randomization_list_importer import RandomizationListImporter

        RandomizationListImporter(name='default', add=True, dryrun=False)


    Format:
        sid,assignment,site_name, orig_site, orig_allocation, orig_desc
        1,single_dose,gaborone
        2,two_doses,gaborone
        ...
    """

    required_csv_fieldnames = ["sid", "assignment", "site_name"]
    verifier_cls = RandomizationListVerifier

    def __init__(
        self,
        randomizer_model_cls=None,
        randomizer_name: str = None,
        randomizationlist_path: str = None,
        assignment_map: Dict[str, int] = None,
        verbose: bool = None,
        overwrite: bool = None,
        add: bool = None,
        dryrun: bool = None,
        username: str = None,
        revision: str = None,
        sid_count_for_tests: int = None,
        extra_csv_fieldnames: Optional[List[str]] = None,
        **kwargs,
    ):
        self.verify_messages: Optional[str] = None
        self.add = add
        self.overwrite = overwrite
        self.verbose = True if verbose is None else verbose
        self.dryrun = dryrun
        self.revision = revision
        self.user = username
        self.sid_count_for_tests = sid_count_for_tests
        self.randomizer_model_cls = randomizer_model_cls
        self.randomizer_name = randomizer_name
        self.assignment_map = assignment_map
        self.randomizationlist_path = randomizationlist_path
        self.required_csv_fieldnames.extend(extra_csv_fieldnames or [])

        if self.dryrun:
            sys.stdout.write(
                style.MIGRATE_HEADING("\n ->> Dry run. No changes will be made.\n")
            )
        if not self.get_site_names():
            raise RandomizationListImportError(
                "No sites have been imported. See sites module and ."
                'method "add_or_update_django_sites".'
            )
        if self.verbose and add:
            count = self.randomizer_model_cls.objects.all().count()
            sys.stdout.write(
                style.SUCCESS(
                    f"\n(*) Randolist model has {count} SIDs (count before import).\n"
                )
            )

    def import_list(self, **kwargs) -> Tuple[int, str]:
        """Imports CSV and verifies."""
        self._raise_on_empty_file()
        self._raise_on_invalid_header()
        self._raise_on_already_imported()
        self._raise_on_duplicates()
        if self.verbose:
            sys.stdout.write(
                style.SUCCESS(
                    "\nImport CSV data\n"
                    "  Randomizer:\n"
                    f"    -  Name: {self.randomizer_name}\n"
                    f"    -  Assignments: {self.assignment_map}\n"
                    f"    -  Model: {self.randomizer_model_cls._meta.label_lower}\n"
                    f"    -  Path: {self.randomizationlist_path}\n"
                )
            )
        rec_count = self._import_csv_to_model()
        self.verify_messages = self._verify_data(**kwargs)
        self._summarize_results()
        if self.verbose:
            sys.stdout.write(
                style.SUCCESS("\nDone.------------------------------------------------\n")
            )
        return rec_count, self.randomizationlist_path

    def _summarize_results(self):
        if self.verbose:
            count = self.randomizer_model_cls.objects.all().count()
            path = self.randomizationlist_path
            msg = (
                f"\n    - Imported {count} SIDs for randomizer "
                f"`{self.randomizer_name}` into model "
                f"`{self.randomizer_model_cls._meta.label_lower}` \n"
                f"      from {path}.\n"
            )
            sys.stdout.write(style.SUCCESS(msg))
            if self.verify_messages:
                sys.stdout.write(style.ERROR("\n    ! Verification failed. "))
            else:
                sys.stdout.write(style.SUCCESS("    - Verified OK. \n"))

    def _raise_on_empty_file(self):
        if int(os.path.getsize(self.randomizationlist_path)) < 1:
            raise RandomizationListImportError(
                f"File is empty. See {self.randomizer_name}. "
                f"Got {self.randomizationlist_path} (1)."
            )
        else:
            index = 0
            with open(self.randomizationlist_path, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for index, row in enumerate(reader):
                    if index == 0:
                        continue
            if index == 0:
                raise RandomizationListImportError(
                    f"File is empty. See {self.randomizer_name}. "
                    f"Got {self.randomizationlist_path} (2)."
                )

    def _raise_on_invalid_header(self):
        with open(self.randomizationlist_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for index, row in enumerate(reader):
                if index == 0:
                    for fieldname in self.required_csv_fieldnames:
                        if fieldname not in row:
                            raise RandomizationListImportError(
                                "Invalid header. Missing column " f"`{fieldname}`. Got {row}"
                            )
                elif index == 1:
                    if self.dryrun:
                        row_as_dict = {k: v for k, v in row.items()}
                        print(" -->  First row:")
                        print(f" -->  {list(row_as_dict.keys())}")
                        print(f" -->  {list(row_as_dict.values())}")
                        obj = self.randomizer_model_cls(**self.get_import_options(row))
                        pprint(obj.__dict__)
                else:
                    break

    def _raise_on_already_imported(self):
        if not self.dryrun:
            if self.overwrite:
                self.randomizer_model_cls.objects.all().delete()
            if self.randomizer_model_cls.objects.all().count() > 0 and not self.add:
                raise RandomizationListAlreadyImported(
                    "Not importing CSV. "
                    f"{self.randomizer_model_cls._meta.label_lower} "
                    "model is not empty!"
                )

    def get_sid_list(self) -> List[int]:
        with open(self.randomizationlist_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            sids = [row["sid"] for row in reader]
        if len(sids) != len(list(set(sids))):
            raise RandomizationListImportError("Invalid file. Detected duplicate SIDs")
        return sids

    def _raise_on_duplicates(self):
        self.get_sid_list()

    def _import_csv_to_model(self) -> int:
        """Imports a CSV to populate the "rando" model"""
        objs = []
        rec_count = 0

        if self.sid_count_for_tests is not None:
            sys.stdout.write(
                style.WARNING(
                    "\nNote: Importing a `subset` of the randomization list for tests "
                    f"({self.sid_count_for_tests}).\n"
                )
            )
            sid_count = self.sid_count_for_tests
        else:
            sid_count = len(self.get_sid_list())
        with open(self.randomizationlist_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in tqdm(reader, total=sid_count):
                if self.sid_count_for_tests and len(objs) == self.sid_count_for_tests:
                    break
                row = {k: v.strip() for k, v in row.items()}
                try:
                    self.randomizer_model_cls.objects.get(sid=row["sid"])
                except ObjectDoesNotExist:
                    opts = self.get_import_options(row)
                    opts.update(self.get_extra_import_options(row))
                    if self.user:
                        opts.update(user_created=self.user)
                    if self.revision:
                        opts.update(revision=self.revision)
                    obj = self.randomizer_model_cls(**opts)
                    objs.append(obj)
            if not self.dryrun:
                self.randomizer_model_cls.objects.bulk_create(objs)
                rec_count = self.randomizer_model_cls.objects.all().count()
                if not sid_count == rec_count:
                    raise RandomizationListImportError(
                        "Incorrect record count on import. "
                        f"Expected {sid_count}. Got {rec_count}."
                    )
            else:
                sys.stdout.write(
                    style.MIGRATE_HEADING(
                        "\n ->> this is a dry run. No changes were saved. **\n"
                    )
                )
        return rec_count

    def _verify_data(self, **kwargs) -> List[str]:
        verifier = self.verifier_cls(
            assignment_map=self.assignment_map,
            randomizationlist_path=self.randomizationlist_path,
            randomizer_model_cls=self.randomizer_model_cls,
            randomizer_name=self.randomizer_name,
            required_csv_fieldnames=self.required_csv_fieldnames,
            **kwargs,
        )
        return verifier.messages

    def get_assignment(self, row: dict, assignment_map: Dict[str, int]) -> str:
        """Returns assignment (text) after checking validity."""
        return self.valid_assignment_or_raise(row["assignment"], assignment_map)

    def get_allocation(self, row: dict, assignment_map: Dict[str, int]) -> int:
        """Returns an integer allocation for the given
        assignment or raises.
        """
        assignment = self.get_assignment(row, assignment_map)
        return assignment_map.get(assignment)

    def valid_assignment_or_raise(
        self, assignment: str, assignment_map: Dict[str, int]
    ) -> str:
        if assignment not in assignment_map:
            raise InvalidAssignment(
                f"Invalid assignment. Expected one of {list(assignment_map.keys())}. "
                f"Got `{assignment}`. "
                f"See randomizer `{self.randomizer_name}` {repr(self)}. "
            )
        return assignment

    def get_import_options(self, row):
        return dict(
            id=uuid4(),
            sid=row["sid"],
            assignment=self.get_assignment(row, self.assignment_map),
            allocation=str(self.get_allocation(row, self.assignment_map)),
            randomizer_name=self.randomizer_name,
            site_name=self.validate_site_name(row),
            **self.get_extra_import_options(row),
        )

    def get_extra_import_options(self, row):
        return {}

    @staticmethod
    def get_site_names() -> Dict[str, str]:
        """A dict of site names for the target randomizer.

        Default: All sites"""
        from django.contrib.sites.models import Site

        sites = {obj.name: obj.name for obj in Site.objects.all()}
        if not sites:
            raise RandomizationListImportError(
                "No sites have been imported. See sites module and ."
                'method "add_or_update_django_sites".'
            )
        return sites

    def validate_site_name(self, row) -> str:
        """Returns the site name or raises"""
        try:
            site_name = self.get_site_names()[row["site_name"]]
        except KeyError:
            raise RandomizationListImportError(
                f"Invalid site. Got {row['site_name']}. "
                f"Expected one of {self.get_site_names().keys()}"
            )
        return site_name
