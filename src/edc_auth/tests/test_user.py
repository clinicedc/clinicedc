from django.contrib.auth.models import User
from django.core import mail
from django.test import tag
from faker import Faker
from string import Template

from ..group_names import CLINIC
from ..import_users import import_users, UserImporter, UserImporterError
from ..password_setter import PasswordSetter
from ..role_names import CLINICIAN_ROLE
from .utils import create_users, create_user_csv_file, EdcAuthTestCase

fake = Faker()

site_names = ["harare", "gaborone", "kampala"]


class TestUser(EdcAuthTestCase):
    def setUp(self):
        self.filename = create_user_csv_file(user_count=2)

    def test_import_users(self):
        # import new users
        import_users(self.filename, resource_name=None, send_email_to_user=True)
        self.assertEqual(len(mail.outbox), User.objects.all().count())  # noqa
        self.assertEqual(
            mail.outbox[0].subject, "Your example.com user account is ready."
        )

        # update existing users
        import_users(self.filename, resource_name=None, send_email_to_user=True)
        user_count = User.objects.all().count()
        self.assertEqual(len(mail.outbox), user_count * 2)  # noqa
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
        create_users(5)
        pwsetter = PasswordSetter()
        pwsetter.reset_all()
        self.assertEqual(len(mail.outbox), User.objects.all().count())  # noqa

    def test_password_setter_groups(self):
        count = User.objects.filter(groups__name=CLINIC).count()
        create_users(5, group_name=CLINIC)
        pwsetter = PasswordSetter()
        pwsetter.reset_by_groups([CLINIC])
        self.assertEqual(len(mail.outbox), User.objects.all().count() + count)  # noqa

    def test_password_setter_sites(self):
        count = User.objects.filter(userprofile__sites__name="harare").count()
        create_users(5, site_name="harare")
        pwsetter = PasswordSetter()
        pwsetter.reset_by_sites(["harare"])
        self.assertEqual(len(mail.outbox), User.objects.all().count() + count)  # noqa

    def test_password_setter_user(self):
        usernames = create_users(5)
        pwsetter = PasswordSetter()
        pwsetter.reset_users(usernames)
        self.assertEqual(len(mail.outbox), 5)  # noqa
