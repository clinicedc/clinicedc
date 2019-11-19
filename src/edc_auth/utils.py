from django.contrib.auth.models import Group
from pprint import pprint


def compare_codenames_for_group(group_name=None, expected=None):
    group = Group.objects.get(name=group_name)
    codenames = [p.codename for p in group.permissions.all()]
    new_expected = []
    for c in expected:
        try:
            c = c.split(".")[1]
        except IndexError:
            pass
        new_expected.append(c)

    compared = [c for c in new_expected if c not in codenames]
    if compared:
        print(group.name, "missing from codenames")
        pprint(compared)
    compared = [c for c in codenames if c not in new_expected]
    if compared:
        print(group.name, "extra codenames")
        pprint(compared)
