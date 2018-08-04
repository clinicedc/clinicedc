from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist

import csv
from django.contrib.sites.models import Site
import string
import secrets

path = '/home/ambition/edc_users_201808.csv'
fieldnames = ['username', 'first_name',
              'last_name', 'email', 'sites', 'groups']


def create_users_from_list(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            get_or_create_user(row)


def get_password(length=None):
    length = length or 8
    alphabet = string.ascii_letters + string.digits + "$%#@&!-=+*"
    return ''.join(secrets.choice(alphabet) for i in range(length))


def get_or_create_user(row):
    user = None
    username = row.get('username')
    if username:
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            user = User.objects.create(
                username=username,
                first_name=row.get('first_name'),
                last_name=row.get('last_name'),
                email=row.get('email'),
                is_staff=True,
                is_active=True)
            password = get_password()
            user.set_password(password)
            print(f'create {username}, {password}')
            site_names = row.get('sites').lower().split(',')
            for site_name in site_names:
                try:
                    site = Site.objects.get(name=site_name)
                except ObjectDoesNotExist:
                    print(
                        f'Unknown site for user. Got {username}, {site_name}')
                else:
                    user.userprofile.sites.add(site)
            group_names = row.get('groups').lower().split(',')
            for group_name in group_names:
                try:
                    group = Group.objects.get(name__iexact=group_name)
                except ObjectDoesNotExist:
                    print(
                        f'Unknown group for user. Got {username}, {group_name}')
                else:
                    user.groups.add(group)

    return user
