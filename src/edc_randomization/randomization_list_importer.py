import csv
import os
import sys
from pprint import pprint
from uuid import uuid4

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from tqdm import tqdm

from .site_randomizers import site_randomizers

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
        name=None,
        verbose=None,
        overwrite=None,
        add=None,
        dryrun=None,
        user=None,
        revision=None,
        sid_count_for_tests=None,
    ):
        verbose = True if verbose is None else verbose
        self.dryrun = True if dryrun and dryrun.lower() == "yes" else False
        self.revision = revision
        self.user = user
        self.sid_count_for_tests = sid_count_for_tests

        if self.dryrun:
            sys.stdout.write(
                style.MIGRATE_HEADING("\n ->> Dry run. No changes will be made.\n")
            )
        randomizer = site_randomizers.get(name)
        if not randomizer:
            names = "`, `".join(list(site_randomizers.registry.keys()))
            raise RandomizationListImportError(
                f"Randomizer not registered or invalid name. Got `{name}`. "
                f"Expected one of `{names}`",
                "See `site_randomizers`.",
            )
        else:
            sys.stdout.write(
                style.SUCCESS(
                    f"(*) Loaded randomizer {randomizer}.\n"
                    f"    -  Name: {randomizer.name}\n"
                    f"    -  Assignments: {randomizer.assignment_map}\n"
                    f"    -  Blinded trial:  {randomizer.is_blinded_trial}\n"
                    f"    -  CSV file:  {randomizer.filename}\n"
                    f"    -  Model: {randomizer.model}\n"
                    f"    -  Path: {settings.EDC_RANDOMIZATION_LIST_PATH}\n"
                )
            )

        self.site_names = {obj.name: obj.name for obj in Site.objects.all()}
        if not self.site_names:
            raise RandomizationListImportError(
                "No sites have been imported. See sites module and ."
                'method "add_or_update_django_sites".'
            )
        if verbose and add:
            count = randomizer.model_cls().objects.all().count()
            sys.stdout.write(
                style.SUCCESS(f"(*) Randolist model has {count} SIDs (count before import).\n")
            )

        self.import_list(randomizer=randomizer, verbose=verbose, overwrite=overwrite, add=add)

    def import_list(self, randomizer=None, verbose=None, overwrite=None, add=None):
        path = os.path.expanduser(randomizer.get_randomization_list_path())
        self.raise_on_invalid_header(path, randomizer)
        self.raise_on_already_imported(randomizer, add, overwrite)
        self.raise_on_duplicates(path)
        self._import_to_model(path, randomizer)
        if verbose:
            count = randomizer.model_cls().objects.all().count()
            sys.stdout.write(
                style.SUCCESS(
                    f"(*) Imported {count} SIDs for randomizer `{randomizer.name}` into model "
                    f"`{randomizer.model_cls()._meta.label_lower}` \n"
                    f"    from {path} (count after import).\n"
                )
            )
        if not path:
            raise RandomizationListImportError("No randomization list to imported!")
        return path

    def get_site_name(self, row):
        """Returns the site name or raises."""
        try:
            site_name = self.site_names[row["site_name"]]
        except KeyError:
            raise RandomizationListImportError(
                f'Invalid site. Got {row["site_name"]}. '
                f"Expected one of {self.site_names.keys()}"
            )
        return site_name

    def raise_on_invalid_header(self, path, randomizer):
        with open(path, "r") as csvfile:
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
                        assignment = randomizer.get_assignment(row)
                        allocation = randomizer.get_allocation(row)
                        try:
                            randomizer_name = row["randomizer_name"]
                        except KeyError:
                            randomizer_name = "default"
                        obj = randomizer.model_cls()(
                            id=uuid4(),
                            sid=row["sid"],
                            assignment=assignment,
                            site_name=self.get_site_name(row),
                            allocation=str(allocation),
                            randomizer_name=randomizer_name,
                        )
                        pprint(obj.__dict__)
                    try:
                        Site.objects.get(name=row["site_name"])
                    except ObjectDoesNotExist:
                        site_names = [obj.name for obj in Site.objects.all()]
                        raise ObjectDoesNotExist(
                            f"Invalid site name. Expected on of {site_names}. "
                            f"Got {row['site_name']}"
                        )
                else:
                    break

    def raise_on_already_imported(self, randomizer, add, overwrite):
        if not self.dryrun:
            if overwrite:
                randomizer.model_cls().objects.all().delete()
            if randomizer.model_cls().objects.all().count() > 0 and not add:
                raise RandomizationListImportError(
                    f"Not importing CSV. "
                    f"{randomizer.model_cls()._meta.label_lower} model is not empty!"
                )

    def raise_on_duplicates(self, path):
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            sids = [row["sid"] for row in reader]
        if len(sids) != len(list(set(sids))):
            raise RandomizationListImportError("Invalid file. Detected duplicate SIDs")
        self.sid_count = len(sids)

    def _import_to_model(self, path, randomizer):
        objs = []
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in tqdm(reader, total=self.sid_count_for_tests or self.sid_count):
                row = {k: v.strip() for k, v in row.items()}
                try:
                    randomizer.model_cls().objects.get(sid=row["sid"])
                except ObjectDoesNotExist:
                    assignment = randomizer.get_assignment(row)
                    allocation = randomizer.get_allocation(row)
                    try:
                        randomizer_name = row["randomizer_name"]
                    except KeyError:
                        randomizer_name = "default"
                    opts = dict(
                        id=uuid4(),
                        sid=row["sid"],
                        assignment=assignment,
                        site_name=self.get_site_name(row),
                        allocation=str(allocation),
                        randomizer_name=randomizer_name,
                    )
                    if self.user:
                        opts.update(user_created=self.user)
                    if self.revision:
                        opts.update(revision=self.revision)
                    obj = randomizer.model_cls()(**opts)
                    objs.append(obj)
            if not self.dryrun:
                sys.stdout.write(
                    style.SUCCESS(
                        f"\n    -  bulk creating {self.sid_count_for_tests or self.sid_count} "
                        "model instances ...\r"
                    )
                )
                randomizer.model_cls().objects.bulk_create(objs)
                sys.stdout.write(
                    style.SUCCESS(
                        f"    -  bulk creating {self.sid_count_for_tests or self.sid_count} "
                        "model instances ... done\n"
                    )
                )
                assert self.sid_count == randomizer.model_cls().objects.all().count()
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
