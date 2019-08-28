import csv
import os
import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from tqdm import tqdm
from uuid import uuid4

# from .models import RandomizationList
from .utils import get_assignment, get_allocation

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

    def __init__(self, model=None, path=None, verbose=None, overwrite=None, add=None):
        self.model = model
        verbose = True if verbose is None else verbose
        path = path or settings.RANDOMIZATION_LIST_PATH
        path = os.path.expanduser(path)
        if overwrite:
            self.randomization_list_model_cls.objects.all().delete()
        if self.randomization_list_model_cls.objects.all().count() > 0 and not add:
            raise RandomizationListImportError(
                f"Not importing CSV. {self.model} model is not empty!"
            )
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            sids = [row["sid"] for row in reader]
        if len(sids) != len(list(set(sids))):
            raise RandomizationListImportError(
                "Invalid file. Detected duplicate SIDs")
        self.sid_count = len(sids)
        self.site_names = {obj.name: obj.name for obj in Site.objects.all()}
        if not self.site_names:
            raise RandomizationListImportError(
                "No sites have been imported. See ambition-sites and ."
                'method "add_or_update_django_sites".'
            )

        objs = []
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in tqdm(reader, total=self.sid_count):
                row = {k: v.strip() for k, v in row.items()}

                try:
                    self.randomization_list_model_cls.objects.get(
                        sid=row["sid"])
                except ObjectDoesNotExist:
                    assignment = get_assignment(row)
                    obj = self.randomization_list_model_cls(
                        id=uuid4(),
                        sid=row["sid"],
                        assignment=assignment,
                        site_name=self.get_site_name(row),
                        allocation=get_allocation(row, assignment),
                    )
                    objs.append(obj)
            self.randomization_list_model_cls.objects.bulk_create(objs)
            assert self.sid_count == self.randomization_list_model_cls.objects.all().count()

        if verbose:
            count = self.randomization_list_model_cls.objects.all().count()
            sys.stdout.write(style.SUCCESS(
                f"(*) Imported {count} SIDs from {path}.\n"))

    @property
    def randomization_list_model_cls(self):
        return django_apps.get_model(self.model)

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
