import csv
import os
import sys

from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from tqdm import tqdm
from uuid import uuid4

# from .models import RandomizationList
from .site_randomizers import site_randomizers

style = color_style()


class RandomizationListImportError(Exception):
    pass


class RandomizationListImporter:

    """Imports upon instantiation a formatted randomization CSV file
    into model RandomizationList.

    Format:
        sid,assignment,site_name, orig_site, orig_allocation, orig_desc
        1,single_dose,gaborone
        2,two_doses,gaborone
        ...
    """

    def __init__(self, randomizers=None, verbose=None, overwrite=None, add=None):
        verbose = True if verbose is None else verbose
        randomizers = randomizers or site_randomizers.registry.values()
        if not randomizers:
            raise RandomizationListImportError(
                "No randomizers defined. See `site_randomizers`."
            )
        self.site_names = {obj.name: obj.name for obj in Site.objects.all()}
        if not self.site_names:
            raise RandomizationListImportError(
                "No sites have been imported. See sites module and ."
                'method "add_or_update_django_sites".'
            )
        paths = []
        for randomizer in randomizers:
            paths.append(
                self.import_list(
                    randomizer=randomizer, verbose=verbose, overwrite=overwrite, add=add
                )
            )
        if not paths:
            raise RandomizationListImportError("No randomization lists imported!")

    def import_list(self, randomizer=None, verbose=None, overwrite=None, add=None):
        path = os.path.expanduser(randomizer.get_randomization_list_path())
        if overwrite:
            randomizer.model_cls().objects.all().delete()
        if randomizer.model_cls().objects.all().count() > 0 and not add:
            raise RandomizationListImportError(
                f"Not importing CSV. {randomizer.model} model is not empty!"
            )
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            sids = [row["sid"] for row in reader]
        if len(sids) != len(list(set(sids))):
            raise RandomizationListImportError("Invalid file. Detected duplicate SIDs")
        self.sid_count = len(sids)

        objs = []
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in tqdm(reader, total=self.sid_count):
                row = {k: v.strip() for k, v in row.items()}

                try:
                    randomizer.model_cls().objects.get(sid=row["sid"])
                except ObjectDoesNotExist:
                    assignment = randomizer.get_assignment(row)
                    allocation = randomizer.get_allocation(row)
                    obj = randomizer.model_cls()(
                        id=uuid4(),
                        sid=row["sid"],
                        assignment=assignment,
                        site_name=self.get_site_name(row),
                        allocation=str(allocation),
                    )
                    objs.append(obj)
            randomizer.model_cls().objects.bulk_create(objs)
            assert self.sid_count == randomizer.model_cls().objects.all().count()

        if verbose:
            count = randomizer.model_cls().objects.all().count()
            sys.stdout.write(style.SUCCESS(f"(*) Imported {count} SIDs from {path}.\n"))
        return path

    def get_site_name(self, row):
        """Returns the site name or raises.
        """
        try:
            site_name = self.site_names[row["site_name"]]
        except KeyError:
            raise RandomizationListImportError(
                f'Invalid site. Got {row["site_name"]}. '
                f"Expected one of {self.site_names.keys()}"
            )
        return site_name
