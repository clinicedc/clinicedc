import csv
import sys
from pprint import pprint
from uuid import uuid4

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from tqdm import tqdm

style = color_style()


class RandomizationListImportError(Exception):
    pass


class RandomizationListImporter:
    """Imports upon instantiation a formatted randomization CSV file
    into model RandomizationList.

    default CSV file is the projects randomization_list.csv

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

    default_fieldnames = ["sid", "assignment", "site_name"]

    def __init__(
        self,
        randomizer_cls=None,
        verbose=None,
        overwrite=None,
        add=None,
        dryrun=None,
        user=None,
        revision=None,
        sid_count_for_tests=None,
    ):
        self.sid_count = 0
        self.randomizer_cls = randomizer_cls
        self.add = add
        self.overwrite = overwrite
        self.verbose = True if verbose is None else verbose
        self.dryrun = True if dryrun and dryrun.lower() == "yes" else False
        self.revision = revision
        self.user = user
        self.sid_count_for_tests = sid_count_for_tests

        if self.dryrun:
            sys.stdout.write(
                style.MIGRATE_HEADING("\n ->> Dry run. No changes will be made.\n")
            )
        sys.stdout.write(
            style.SUCCESS(
                f"(*) Loaded randomizer {self.randomizer_cls}.\n"
                f"    -  Name: {self.randomizer_cls.name}\n"
                f"    -  Assignments: {self.randomizer_cls.assignment_map}\n"
                f"    -  Blinded trial:  {self.randomizer_cls.is_blinded_trial}\n"
                f"    -  CSV file:  {self.randomizer_cls.filename}\n"
                f"    -  Model: {self.randomizer_cls.model}\n"
                f"    -  Path: {self.randomizer_cls.randomization_list_path}\n"
            )
        )
        if not self.get_site_names():
            raise RandomizationListImportError(
                "No sites have been imported. See sites module and ."
                'method "add_or_update_django_sites".'
            )
        if self.verbose and add:
            count = self.randomizer_cls.model_cls().objects.all().count()
            sys.stdout.write(
                style.SUCCESS(f"(*) Randolist model has {count} SIDs (count before import).\n")
            )

    def import_list(self):
        self._raise_on_invalid_header()
        self._raise_on_already_imported()
        self._raise_on_duplicates()
        self._import_to_model()
        self._summarize_results()
        return self.randomizer_cls.get_randomization_list_fullpath()

    def _summarize_results(self):
        if self.verbose:
            count = self.randomizer_cls.model_cls().objects.all().count()
            path = self.randomizer_cls.get_randomization_list_fullpath()
            sys.stdout.write(
                style.SUCCESS(
                    f"(*) Imported {count} SIDs for randomizer "
                    f"`{self.randomizer_cls.name}` into model "
                    f"`{self.randomizer_cls.model_cls()._meta.label_lower}` \n"
                    f"    from {path} (count after import).\n"
                )
            )
        if not self.randomizer_cls.get_randomization_list_fullpath():
            raise RandomizationListImportError("No randomization list to imported!")

    def _raise_on_invalid_header(self):
        with open(self.randomizer_cls.get_randomization_list_fullpath(), "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for index, row in enumerate(reader):
                if index == 0:
                    for fieldname in self.default_fieldnames:
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
                        obj = self.randomizer_cls.model_cls()(**self.get_import_options(row))
                        pprint(obj.__dict__)
                else:
                    break

    def _raise_on_already_imported(self):
        if not self.dryrun:
            if self.overwrite:
                self.randomizer_cls.model_cls().objects.all().delete()
            if self.randomizer_cls.model_cls().objects.all().count() > 0 and not self.add:
                raise RandomizationListImportError(
                    f"Not importing CSV. "
                    f"{self.randomizer_cls.model_cls()._meta.label_lower} model is not empty!"
                )

    def _raise_on_duplicates(self):
        with open(self.randomizer_cls.get_randomization_list_fullpath(), "r") as csvfile:
            reader = csv.DictReader(csvfile)
            sids = [row["sid"] for row in reader]
        if len(sids) != len(list(set(sids))):
            raise RandomizationListImportError("Invalid file. Detected duplicate SIDs")
        self.sid_count = len(sids)

    def _import_to_model(self):
        """Imports a CSV to populate the "rando" model"""
        objs = []
        with open(self.randomizer_cls.get_randomization_list_fullpath(), "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in tqdm(reader, total=self.sid_count_for_tests or self.sid_count):
                row = {k: v.strip() for k, v in row.items()}
                try:
                    self.randomizer_cls.model_cls().objects.get(sid=row["sid"])
                except ObjectDoesNotExist:
                    opts = self.get_import_options(row)
                    opts.update(self.get_extra_import_options(row))
                    if self.user:
                        opts.update(user_created=self.user)
                    if self.revision:
                        opts.update(revision=self.revision)
                    obj = self.randomizer_cls.model_cls()(**opts)
                    objs.append(obj)
            if not self.dryrun:
                sys.stdout.write(
                    style.SUCCESS(
                        f"\n    -  bulk creating {self.sid_count_for_tests or self.sid_count} "
                        "model instances ...\r"
                    )
                )
                self.randomizer_cls.model_cls().objects.bulk_create(objs)
                sys.stdout.write(
                    style.SUCCESS(
                        f"    -  bulk creating {self.sid_count_for_tests or self.sid_count} "
                        "model instances ... done\n"
                    )
                )
                assert self.sid_count == self.randomizer_cls.model_cls().objects.all().count()
                sys.stdout.write(
                    style.SUCCESS(
                        "    Important: You may wish to run the randomization list "
                        "verifier before going LIVE on production systems."
                    )
                )

            else:
                sys.stdout.write(
                    style.MIGRATE_HEADING(
                        "\n ->> this is a dry run. No changes were saved. **\n"
                    )
                )

    def get_import_options(self, row):
        return dict(
            id=uuid4(),
            sid=row["sid"],
            assignment=self.randomizer_cls.get_assignment(row),
            allocation=str(self.randomizer_cls.get_allocation(row)),
            randomizer_name=self.randomizer_cls.name,
            site_name=self.validate_site_name(row),
            **self.get_extra_import_options(row),
        )

    def get_extra_import_options(self, row):
        return {}

    @staticmethod
    def get_site_names():
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

    def validate_site_name(self, row):
        """Returns the site name or raises"""
        try:
            site_name = self.get_site_names()[row["site_name"]]
        except KeyError:
            raise RandomizationListImportError(
                f"Invalid site. Got {row['site_name']}. "
                f"Expected one of {self.get_site_names().keys()}"
            )
        return site_name
