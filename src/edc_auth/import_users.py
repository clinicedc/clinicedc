import csv
import re

from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from string import Template

from .passwd import PasswordGenerator

fieldnames = ['username', 'first_name',
              'last_name', 'email',
              'sites', 'groups', 'job_title']


class UserImporterError(Exception):
    pass


def import_users(path, resource_name=None, send_email_to_user=None,
                 alternate_email=None, verbose=None,
                 export_to_file=None, **kwargs):
    """Import users from a CSV file with columns:
        username
        first_name
        last_name
        email
        sites: a comma-separated list of sites
        groups: a comma-separated list of groups
        job_title
    """
    users = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for user_data in reader:
            username = user_data.get('username')
            site_names = user_data.get('sites').lower().split(',')
            group_names = user_data.get('groups').lower().split(',')
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')
            email = user_data.get('email')
            o = UserImporter(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                site_names=site_names,
                group_names=group_names,
                resource_name=resource_name,
                send_email_to_user=send_email_to_user,
                alternate_email=alternate_email,
                verbose=verbose)
            users.append({'username': o.user.username,
                          'password': o.password,
                          'first_name': o.user.first_name,
                          'last_name': o.user.last_name,
                          'sites': o.site_names,
                          'groups': o.group_names})
    if export_to_file:
        fieldnames = ['username', 'password',
                      'first_name', 'last_name',
                      'sites', 'groups']
        with open(path + 'new.csv', 'w+') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for user in users:
                writer.writerow(user)


class UserImporter:
    resource_name = 'example.com'
    created_email_template = Template(
        'Hi $first_name, \n\n'
        'Your $resource_name} user account has been created.\n\n'
        'Your username is $username.\n\n'
        'Your password is:\n\n$password\n\n'
        '(Yes, that is your password)\n\n'
        'You are authorized to log into the following sites:\n\n$site_names.\n\n'
        'You belong to the following groups:\n\n$group_names\n\n'
        'Thanks.\n\n')
    updated_email_template = Template(
        f'Hi $first_name, \n\n'
        f'Your $resource_name user account has been updated.\n\n'
        f'Your username is $user.username.\n\n'
        f'You are authorized to log into the following sites:\n\n$site_names.\n\n'
        f'You belong to the following groups:\n\n$group_names\n\n'
        f'Thanks.\n\n')

    def __init__(self,
                 username=None,
                 first_name=None,
                 last_name=None,
                 email=None,
                 site_names=None,
                 group_names=None,
                 resource_name=None,
                 created_email_template=None,
                 updated_email_template=None,
                 send_email_to_user=None,
                 alternate_email=None, **kwargs):
        self._messages = []
        self._user = None
        self.alternate_email = alternate_email
        self.created = False
        self.email = email
        self.first_name = first_name
        self.group_names = group_names
        self.last_name = last_name
        self.password_generator = PasswordGenerator(**kwargs)
        self.resource_name = resource_name or self.resource_name
        self.site_names = site_names
        self.username = username
        if created_email_template:
            self.created_email_template = created_email_template
        if updated_email_template:
            self.updated_email_template = updated_email_template
        self.validate_username()

        self.update_user_sites()
        self.update_user_groups()
        self.user.save()
        self.site_names = "\n".join(
            [s.name for s in self.user.userprofile.sites.all()])
        self.group_names = "\n".join(
            [g.name for g in self.user.groups.all()])
        if send_email_to_user:
            self.email_message.send(fail_silently=False)

    def validate_username(self):
        if not self.username:
            raise UserImporterError(
                f'Invalid username. Got username={self.username}')
        if not re.match('^\w+$', self.username):
            raise UserImporterError(
                f'Invalid username. Got {self.username}')

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
                    is_active=True)
                self.password = self.password_generator.get_password()
                self._user.set_password(self.password)
                self._user.save()
                self.created = True
            else:
                self.password = None
        return self._user

    def update_user_sites(self):
        self.user.userprofile.sites.clear()
        for site_name in self.site_names:
            try:
                site = Site.objects.get(name=site_name)
            except ObjectDoesNotExist:
                sites = [s.name for s in Site.objects.all()]
                raise UserImporterError(
                    f'Unknown site for user. Expected one of {sites}. '
                    f'Got {self.user.username}, {site_name}.')
            else:
                self.user.userprofile.sites.add(site)

    def update_user_groups(self):
        self.user.groups.clear()
        for group_name in self.group_names:
            try:
                group = Group.objects.get(name__iexact=group_name)
            except ObjectDoesNotExist:
                raise UserImporterError(
                    f'Unknown group for user. Got {self.user.username}, {group_name}')
            else:
                self.user.groups.add(group)

    @property
    def email_message(self):
        body = self.created_email_template if self.created else self.updated_email_template
        return EmailMessage(
            f'Your {self.resource_name} user account is ready.',
            body=body.safe_substitute(self.__dict__),
            from_email='noreply@clinicedc.org',
            to=[self.alternate_email if self.alternate_email else self.user.email],
        )
