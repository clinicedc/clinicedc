import csv
import os

from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from edc_sites.models import SiteProfile
from faker import Faker
from secrets import choice
from tempfile import mkdtemp

from ..import_users import fieldnames
from ..role_names import CLINICIAN_ROLE, LAB_TECHNICIAN_ROLE

fake = Faker()
group_names = ["CLINIC", "LAB"]
site_names = ["harare", "gaborone", "kampala"]


class EdcAuthTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        SiteProfile.objects.all().delete()
        Site.objects.all().delete()
        for site_name in site_names:
            Site.objects.create(name=site_name, domain=f"{site_name}.example.com")
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        Site.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()


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
        site = Site.objects.get(name=site_name or choice(site_names))
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
    user_count=None, filename=None,
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
                    "first_name": first_name,
                    "last_name": last_name,
                    "job_title": "Research Assistant",
                    "email": fake.email(),
                    "mobile": fake.phone_number(),
                    "sites": choice(site_names),
                    "roles": f"{CLINICIAN_ROLE},{LAB_TECHNICIAN_ROLE}",
                }
            )
    return filename
