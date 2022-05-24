import csv
import os
import re
from datetime import datetime
from string import Template
from typing import Any, List, Optional

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from edc_protocol import Protocol
from mempass import PasswordGenerator

from .auth_objects import ACCOUNT_MANAGER_ROLE, STAFF_ROLE
from .export_users import export_users
from .models import Role

required_role_names = {STAFF_ROLE: "Staff"}


class UserImporterError(Exception):
    pass


add_user_template = Template(
    "Hi $first_name, \n\n"
    "Your $resource_name user account has been created.\n\n"
    "Your username is $username.\n\n"
    "Your password is:\n\n$password\n\n"
    "(Yes, that is your password)\n\n"
    "You are authorized to log into the following sites:\n\n - $site_names.\n\n"
    "As a $job_title, you have been assigned the following roles:\n\n - $role_names.\n\n"
    "Thanks.\n\n"
    "$project_name"
)

change_user_template = Template(
    "Hi $first_name, \n\n"
    "Your `$resource_name` user account has been updated.\n\n"
    "Your username is `$username`.\n\n"
    "Your new password is:\n\n$password\n\n"
    "You are authorized to log into the following sites:\n\n - $site_names.\n\n"
    "As a $job_title, you have been assigned the following roles:\n\n - $role_names.\n\n"
    "Thanks.\n\n"
    "$project_name"
)


fieldnames = [
    "username",
    "password",
    "first_name",
    "last_name",
    "is_superuser",
    "is_staff",
    "is_active",
    "job_title",
    "email",
    "alternate_email",
    "mobile",
    "sites",
    "roles",
]


def import_users(
    path: str,
    resource_name: Optional[str] = None,
    send_email_to_user: Optional[Any] = None,
    resend_as_newly_created: Optional[Any] = None,
    verbose: Optional[Any] = None,
    export_to_file: Optional[Any] = None,
    limit_to_username: Optional[str] = None,
    **kwargs,
):
    """Import users from a CSV file with columns:
    username
    password
    is_staff
    is_active
    first_name
    last_name
    job_title
    email
    mobile
    alternate_email
    site_names: a comma-separated list of sites
    role_names: a comma-separated list of roles
    """
    path = os.path.expanduser(path)
    with open(path) as f:
        reader = csv.DictReader(f, delimiter="|")
        for csv_data in reader:
            opts: dict = {}
            if "username" not in csv_data:
                raise UserImporterError("Invalid file format. Check delimiter")
            if limit_to_username and limit_to_username != csv_data.get("username"):
                continue
            opts.update(username=csv_data.get("username"))
            opts.update(site_names="")
            if csv_data.get("site_names"):
                opts.update(site_names=csv_data.get("site_names").lower().split(","))
            opts.update(role_names="")
            if csv_data.get("role_names"):
                opts.update(role_names=csv_data.get("role_names").lower().split(","))
            opts.update(first_name=csv_data.get("first_name"))
            opts.update(last_name=csv_data.get("last_name"))
            opts.update(mobile=csv_data.get("mobile"))
            opts.update(email=csv_data.get("email"))
            opts.update(alternate_email=csv_data.get("alternate_email"))
            opts.update(job_title=csv_data.get("job_title"))
            opts.update(is_active=True if csv_data.get("is_active") == "True" else False)
            opts.update(is_staff=True if csv_data.get("is_staff") == "True" else False)
            UserImporter(
                resource_name=resource_name,
                send_email_to_user=send_email_to_user,
                verbose=verbose,
                resend_as_newly_created=resend_as_newly_created,
                **opts,
                **kwargs,
            )
    if export_to_file:
        export_users(f"edc_users_imported_{datetime.now().strftime('%Y%m%d%H%M%S')}")


class UserImporter:
    resource_name = "example.com"
    password_nwords = 4
    created_email_template = add_user_template
    updated_email_template = change_user_template

    def __init__(
        self,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        job_title: str = None,
        email: str = None,
        alternate_email: str = None,
        mobile: str = None,
        site_names: List[str] = None,
        role_names: List[str] = None,
        is_active: bool = None,
        is_staff: bool = None,
        resource_name: str = None,
        created_email_template: Optional[Template] = None,
        updated_email_template: Optional[Template] = None,
        send_email_to_user: Optional[Any] = None,
        test_email_address: Optional[Any] = None,
        resend_as_new: Optional[Any] = None,
        nwords: Optional[int] = None,
        **kwargs,
    ):
        self._messages: List[str] = []
        self._user = None
        self.created = False
        self.password = None
        try:
            self.email, self.alternate_email = email.split(",")
        except (ValueError, AttributeError):
            self.email = email
            self.alternate_email = alternate_email
        self.first_name = first_name
        self.job_title = job_title or "staff member"
        self.last_name = last_name
        self.mobile = mobile
        self.is_active = is_active or False
        self.is_staff = is_staff or False
        self.password_generator = PasswordGenerator(
            nwords=nwords or self.password_nwords, **kwargs
        )
        self.resource_name = resource_name or self.resource_name
        self.resend_as_newly_created = resend_as_new
        self.test_email_address = test_email_address
        self.username = username or self.get_username()
        self.created_email_template = created_email_template or self.created_email_template
        self.updated_email_template = updated_email_template or self.updated_email_template
        self.validate_username()
        if ACCOUNT_MANAGER_ROLE in role_names:
            site_names = [s.name for s in Site.objects.all()]
        self.update_user_sites(site_names or [])
        self.update_user_roles(role_names or [STAFF_ROLE])
        self.user.save()
        self.user.userprofile.job_title = self.job_title
        self.user.userprofile.mobile = self.mobile
        self.user.userprofile.alternate_email = self.alternate_email
        self.user.userprofile.save()

        self.site_names = (
            "\n  - ".join([s.name for s in self.user.userprofile.sites.all()])
            or "(You have not been granted access to any sites)"
        )
        self.role_names = "\n  - ".join(
            [g.display_name for g in self.user.userprofile.roles.all()]
        )
        self.project_name = Protocol().protocol_name
        if send_email_to_user:
            try:
                self.email_message.send(fail_silently=False)
            except ConnectionRefusedError:
                print(self.email_message.body)

    def validate_username(self) -> None:
        if not self.username:
            raise UserImporterError(f"Invalid username. Got username={self.username}")
        if not re.match(r"^\w+$", self.username):
            raise UserImporterError(f"Invalid username. Got {self.username}")

    @property
    def user(self) -> User:
        if not self._user:
            try:
                self._user = User.objects.get(username=self.username)
            except ObjectDoesNotExist:
                self._user = User.objects.create(
                    username=self.username,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    email=self.email,
                    is_staff=self.is_staff,
                    is_active=self.is_active,
                    is_superuser=False,
                )
                self.created = True
            else:
                self._user.first_name = self.first_name
                self._user.last_name = self.last_name
                self._user.email = self.email
                self._user.is_staff = self.is_staff
                self._user.is_active = self.is_active
            finally:
                self.password = self.password_generator.get_password()
                self._user.set_password(self.password)
                self._user.save()
        return self._user

    def update_user_sites(self, site_names: List[str]) -> None:
        self.user.userprofile.sites.clear()
        for site_name in site_names:
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

    def update_user_roles(self, role_names: List[str]) -> None:
        self.user.userprofile.roles.clear()
        role_names.extend(required_role_names)
        for role_name in role_names:
            try:
                role = Role.objects.get(name__iexact=role_name)
            except ObjectDoesNotExist:
                raise UserImporterError(
                    f"Unknown role for user. Got role `{role_name}` "
                    f"for user `{self.user.username}`"
                )
            else:
                self.user.userprofile.roles.add(role)

    @property
    def email_message(self) -> EmailMessage:
        if self.created or self.resend_as_newly_created:
            body = self.created_email_template
        else:
            body = self.updated_email_template
        return EmailMessage(
            f"{self.project_name}: Your {self.resource_name} user account is ready.",
            body=body.safe_substitute(self.__dict__),
            from_email="noreply@clinicedc.org",
            to=(self.test_email_address or self.user.email,),
        )

    def get_username(self) -> Optional[str]:
        if self.first_name and self.last_name:
            last_name = "".join(self.last_name.split(" ")).lower()
            return f"{self.first_name.lower()[0]}{last_name}"
        return None
