import csv
import os

from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core import mail
from django.test import TestCase, tag
from faker import Faker
from secrets import choice
from string import Template
from tempfile import mkdtemp

from ..import_users import import_users, fieldnames, UserImporter, UserImporterError
from ..password_setter import PasswordSetter
from ..role_names import CLINICIAN_ROLE, LAB_TECHNICIAN_ROLE

fake = Faker()

site_names = ["harare", "gaborone", "kampala"]


class TestUser(TestCase):
    @classmethod
    def setUpClass(cls):
        Group.objects.create(name="CLINIC")
        Group.objects.create(name="LAB")
        Group.objects.create(name="ACCOUNT_MANAGER")

        Site.objects.all().delete()
        for site_name in site_names:
            Site.objects.create(name=site_name, domain=f"{site_name}.example.com")
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        Site.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def setUp(self):
        self.user_count = 2
        folder = mkdtemp()
        self.filename = os.path.join(folder, "users.csv")
        with open(self.filename, "w") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|")
            writer.writeheader()
            for _ in range(0, self.user_count):
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

    def create_users(self, count, group_name=None, site_name=None):
        usernames = []
        for _ in range(0, count):
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
            group = Group.objects.get(
                name__iexact=group_name or choice(["CLINIC", "LAB"])
            )
            user.groups.add(group)
            user.save()
            usernames.append(user.username)
        self.user_count = User.objects.all().count()
        return usernames

    def test_import_users(self):
        # import new users
        import_users(self.filename, resource_name=None, send_email_to_user=True)
        self.assertEqual(len(mail.outbox), self.user_count)  # noqa
        self.assertEqual(
            mail.outbox[0].subject, "Your example.com user account is ready."
        )

        # update existing users
        import_users(self.filename, resource_name=None, send_email_to_user=True)
        self.assertEqual(len(mail.outbox), self.user_count * 2)  # noqa
        self.assertEqual(
            mail.outbox[0].subject, "Your example.com user account is ready."
        )

    def test_bad_username(self):
        self.assertRaises(
            UserImporterError,
            UserImporter,
            username=None,
            first_name=fake.first_name(),
            last_name=None,
            email=fake.email(),
            site_names=[],
            role_names=[],
            send_email_to_user=True,
        )

        self.assertRaises(
            UserImporterError,
            UserImporter,
            username="erik@",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            site_names=[],
            role_names=[],
            send_email_to_user=True,
        )

    def test_unknown_site(self):
        self.assertRaises(
            UserImporterError,
            UserImporter,
            username="erik",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            site_names=["blah"],
            role_names=["CLINICIAN_ROLE"],
            send_email_to_user=True,
        )

    def test_unknown_role(self):
        self.assertRaises(
            UserImporterError,
            UserImporter,
            username="erik",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            site_names=["harare"],
            role_names=["blah"],
            send_email_to_user=True,
        )

    @tag("1")
    def test_with_custom_templates(self):
        created_email_template = Template("Hi $first_name, \n\nStay Classy")
        updated_email_template = Template(
            "Hi $first_name, \n\nYou stay classy San Diego"
        )
        first_name = fake.first_name()
        UserImporter(
            username="erik",
            first_name=first_name,
            last_name=fake.last_name(),
            email=fake.email(),
            site_names=["harare"],
            role_names=[CLINICIAN_ROLE],
            send_email_to_user=True,
            created_email_template=created_email_template,
            updated_email_template=updated_email_template,
        )
        self.assertEqual(
            mail.outbox[0].body,
            created_email_template.safe_substitute(first_name=first_name),
        )
        UserImporter(
            username="erik",
            first_name=first_name,
            last_name=fake.last_name(),
            email=fake.email(),
            site_names=["harare"],
            role_names=[CLINICIAN_ROLE],
            send_email_to_user=True,
            created_email_template=created_email_template,
            updated_email_template=updated_email_template,
        )
        self.assertEqual(
            mail.outbox[1].body,
            updated_email_template.safe_substitute(first_name=first_name),
        )

    def test_password_setter_all(self):
        self.create_users(5)
        pwsetter = PasswordSetter()
        pwsetter.reset_all()
        self.assertEqual(len(mail.outbox), self.user_count)  # noqa

    def test_password_setter_groups(self):
        count = User.objects.filter(groups__name="CLINIC").count()
        self.create_users(5, group_name="CLINIC")
        pwsetter = PasswordSetter()
        pwsetter.reset_by_groups(["CLINIC"])
        self.assertEqual(len(mail.outbox), self.user_count + count)  # noqa

    def test_password_setter_sites(self):
        count = User.objects.filter(userprofile__sites__name="harare").count()
        self.create_users(5, site_name="harare")
        pwsetter = PasswordSetter()
        pwsetter.reset_by_sites(["harare"])
        self.assertEqual(len(mail.outbox), self.user_count + count)  # noqa

    def test_password_setter_user(self):
        usernames = self.create_users(5)
        pwsetter = PasswordSetter()
        pwsetter.reset_users(usernames)
        self.assertEqual(len(mail.outbox), 5)  # noqa
