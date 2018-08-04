import csv
import os
from faker import Faker
from django.test import TestCase

from ..create_from_list import create_users_from_list, fieldnames
from tempfile import mkdtemp
from random import choice
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group

fake = Faker()

site_names = ['harare', 'gaborone', 'kampala']


class TestUser(TestCase):

    @classmethod
    def setUpClass(cls):
        Group.objects.create(name='CLINIC')
        Group.objects.create(name='LAB')
        Group.objects.create(name='ACCOUNT_MANAGER')
        for site_name in site_names:
            Site.objects.create(
                name=site_name, domain=f'{site_name}.clinicedc.org')
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        Site.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def setUp(self):
        folder = mkdtemp()
        self.filename = os.path.join(folder, 'users.csv')
        with open(self.filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(0, 10):
                first_name = fake.first_name()
                last_name = fake.last_name()
                username = (first_name[0] + last_name).lower()
                writer.writerow({
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': fake.email(),
                    'sites': choice(site_names),
                    'groups': 'CLINIC'})

    def test_(self):
        create_users_from_list(path=self.filename)
