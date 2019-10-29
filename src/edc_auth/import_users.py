import csv
import re

from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from mempass import PasswordGenerator
from string import Template
import pdb


class UserImporterError(Exception):
    pass


fieldnames = [
    "username",
    "password",
    "first_name",
    "last_name",
    "job_title",
    "email",
    "alternate_email",
    "mobile",
    "sites",
    "groups",
]


def import_users(
    path,
    resource_name=None,
    send_email_to_user=None,
    resend_as_newly_created=None,
    verbose=None,
    export_to_file=None,
    **kwargs,
):
    """Import users from a CSV file with columns:
        username
        first_name
        last_name
        job_title
        email
        alternate_email
        mobile
        sites: a comma-separated list of sites
        groups: a comma-separated list of groups
    """
    users = []
    with open(path) as f:
        reader = csv.DictReader(f, delimiter="|")
        for user_data in reader:
            opts = {}
            opts.update(username=user_data.get("username"))
            opts.update(site_names="")
            if user_data.get("sites"):
                opts.update(site_names=user_data.get(
                    "sites").lower().split(","))
            opts.update(group_names="")
            if user_data.get("groups"):
                opts.update(group_names=user_data.get(
                    "groups").lower().split(","))
            opts.update(first_name=user_data.get("first_name"))
            opts.update(last_name=user_data.get("last_name"))
            opts.update(mobile=user_data.get("mobile"))
            opts.update(email=user_data.get("email"))
            opts.update(alternate_email=user_data.get("alternate_email"))
            opts.update(job_title=user_data.get("job_title"))
            o = UserImporter(
                resource_name=resource_name,
                send_email_to_user=send_email_to_user,
                verbose=verbose,
                resend_as_newly_created=resend_as_newly_created,
                **kwargs,
            )
            users.append(
                {
                    "username": o.user.username,
                    "password": o.password,
                    "first_name": o.user.first_name,
                    "last_name": o.user.last_name,
                    "job_title": o.user.userprofile.job_title,
                    "email": o.user.email,
                    "alternate_email": o.user.userprofile.alternate_email,
                    "sites": o.site_names,
                    "groups": o.group_names,
                }
            )
    if export_to_file:
        with open(path + "new.csv", "w+") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for user in users:
                writer.writerow(user)


class UserImporter:
    resource_name = "example.com"
    password_nwords = 4
    created_email_template = Template(
        "Hi $first_name, \n\n"
        "Your $resource_name user account has been created.\n\n"
        "Your username is $username.\n\n"
        "Your password is:\n\n$password\n\n"
        "(Yes, that is your password)\n\n"
        "You are authorized to log into the following sites:\n\n$site_names.\n\n"
        "As a $job_title, you have been added to the following groups:\n\n$group_names\n\n"
        "Thanks.\n\n"
    )
    updated_email_template = Template(
        f"Hi $first_name, \n\n"
        f"Your $resource_name user account has been updated.\n\n"
        f"Your username is $username.\n\n"
        "Your new password is:\n\n$password\n\n"
        f"You are authorized to log into the following sites:\n\n$site_names.\n\n"
        f"As a $job_title, you have been added to the following groups:\n\n$group_names\n\n"
        f"Thanks.\n\n"
    )

    def __init__(
        self,
        username=None,
        first_name=None,
        last_name=None,
        job_title=None,
        email=None,
        alternate_email=None,
        mobile=None,
        site_names=None,
        group_names=None,
        resource_name=None,
        created_email_template=None,
        updated_email_template=None,
        send_email_to_user=None,
        test_email_address=None,
        resend_as_new=None,
        nwords=None,
        **kwargs,
    ):
        self._messages = []
        self._user = None
        self.created = False
        try:
            self.email, self.alternate_email = email.split(",")
        except (ValueError, AttributeError):
            self.email = email
            self.alternate_email = alternate_email
        self.first_name = first_name
        self.job_title = job_title
        self.group_names = group_names
        self.last_name = last_name
        self.mobile = mobile
        self.password_generator = PasswordGenerator(
            nwords=nwords or self.password_nwords, **kwargs
        )
        self.resource_name = resource_name or self.resource_name
        self.site_names = site_names
        self.resend_as_newly_created = resend_as_new
        self.test_email_address = test_email_address
        self.username = username
        if created_email_template:
            self.created_email_template = created_email_template
        if updated_email_template:
            self.updated_email_template = updated_email_template

        self.validate_username()

        self.update_user_sites()
        self.update_user_groups()

        self.user.save()
        self.user.userprofile.job_title = self.job_title
        self.user.userprofile.mobile = self.mobile
        self.user.userprofile.alternate_email = self.alternate_email
        self.user.userprofile.save()

        self.site_names = "\n".join(
            [s.name for s in self.user.userprofile.sites.all()])
        self.group_names = "\n".join([g.name for g in self.user.groups.all()])
        if send_email_to_user:
            try:
                self.email_message.send(fail_silently=False)
            except ConnectionRefusedError:
                print(self.email_message.body)

    def validate_username(self):
        if not self.username:
            raise UserImporterError(
                f"Invalid username. Got username={self.username}")
        if not re.match("^\w+$", self.username):
            raise UserImporterError(f"Invalid username. Got {self.username}")

    @property
    def user(self):
        if not self._user:
            try:
                self._user = User.objects.get(username=self.username)
            except ObjectDoesNotExist:
                self._user = User.objects.create(
                    username=self.username,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    email=self.email,
                    is_staff=True,
                    is_active=True,
                )
                self.password = self.password_generator.get_password()
                self._user.set_password(self.password)
                self._user.save()
                self.created = True
            else:
                self._user.first_name = self.first_name
                self._user.last_name = self.last_name
                self._user.email = self.email
                self.password = self.password_generator.get_password()
                self._user.set_password(self.password)
                self._user.save()
        return self._user

    def update_user_sites(self):
        self.user.userprofile.sites.clear()
        for site_name in self.site_names:
            try:
                site = Site.objects.get(name=site_name)
            except ObjectDoesNotExist:
                sites = [s.name for s in Site.objects.all()]
                raise UserImporterError(
                    f"Unknown site for user. Expected one of {sites}. "
                    f"Got {self.user.username}, {site_name}."
                )
            else:
                self.user.userprofile.sites.add(site)

    def update_user_groups(self):
        self.user.groups.clear()
        for group_name in self.group_names:
            try:
                group = Group.objects.get(name__iexact=group_name)
            except ObjectDoesNotExist:
                raise UserImporterError(
                    f"Unknown group for user. Got {self.user.username}, {group_name}"
                )
            else:
                self.user.groups.add(group)

    @property
    def email_message(self):
        if self.created or self.resend_as_newly_created:
            body = self.created_email_template
        else:
            body = self.updated_email_template
        return EmailMessage(
            f"Your {self.resource_name} user account is ready.",
            body=body.safe_substitute(self.__dict__),
            from_email="noreply@clinicedc.org",
            to=(self.test_email_address or self.user.email,),
        )
