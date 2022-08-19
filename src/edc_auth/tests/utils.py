import csv
import os
from importlib import import_module
from secrets import choice
from tempfile import mkdtemp

from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_lab.auth_objects import LAB_TECHNICIAN_ROLE
from edc_randomization.randomizer import Randomizer
from edc_randomization.site_randomizers import site_randomizers
from edc_sites.models import SiteProfile
from faker import Faker
from mempass import mkpassword

from edc_auth.auth_objects import CLINICIAN_ROLE
from edc_auth.site_auths import site_auths
from edc_auth.tests.randomizers import CustomRandomizer

from ..import_users import fieldnames

fake = Faker()
group_names = ["CLINIC", "LAB"]
sites = {10: "harare", 20: "gaborone", 30: "kampala"}


class EdcAuthTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteProfile.objects.all().delete()
        Site.objects.all().delete()
        for site_id, site_name in sites.items():
            Site.objects.create(id=site_id, name=site_name, domain=f"{site_name}.example.com")
        site_randomizers._registry = {}
        site_randomizers.register(Randomizer)
        site_randomizers.register(CustomRandomizer)
        site_auths.initialize()
        import_module("edc_navbar.auths")
        import_module("edc_dashboard.auths")
        import_module("edc_review_dashboard.auths")
        import_module("edc_randomization.auths")


def create_users(count=None, group_name=None, site_name=None):
    usernames = []
    for _ in range(0, count or 2):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = (first_name[0] + last_name).lower()
        user_data = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": fake.email(),
            "is_active": True,
            "is_staff": True,
            "is_superuser": False,
        }
        user = User.objects.create(**user_data)
        user.userprofile.job_title = "Research Assistant"
        site = Site.objects.get(name=site_name or choice([v for v in sites.values()]))
        user.userprofile.sites.add(site)
        user.userprofile.save()
        if group_name:
            try:
                group = Group.objects.get(name__iexact=group_name)
            except ObjectDoesNotExist:
                group = Group.objects.create(name=group_name)
            user.groups.add(group)
            user.save()
        usernames.append(user.username)
    return usernames


def create_user_csv_file(
    user_count=None,
    filename=None,
    include_passwords=None,
):
    folder = mkdtemp()
    filename = filename or os.path.join(folder, "users.csv")
    with open(filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
        writer.writeheader()
        for _ in range(0, user_count or 2):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name[0]}{''.join(last_name.split(' '))}".lower()
            writer.writerow(
                {
                    "username": username,
                    "password": mkpassword(3) if include_passwords else None,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_staff": True,
                    "is_active": True,
                    "job_title": "Research Assistant",
                    "email": fake.email(),
                    "alternate_email": fake.email(),
                    "mobile": fake.phone_number(),
                    "sites": choice([v for v in sites.values()]),
                    "roles": f"{CLINICIAN_ROLE},{LAB_TECHNICIAN_ROLE}",
                }
            )
    return filename
