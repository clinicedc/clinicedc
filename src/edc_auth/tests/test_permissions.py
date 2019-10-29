from django.test import TestCase, tag

from ..update import (
    update_group_permissions,
    create_or_update_groups,
    default_codenames,
    create_edc_dashboard_permissions,
    create_edc_navbar_permissions,
)


class TestPermissions(TestCase):
    def test_create_or_update_groups(self):
        create_or_update_groups(list(default_codenames.keys()), verbose=True)

    def test_create_dashboard_permissions(self):
        create_edc_dashboard_permissions()

    #         pprint(
    #             [f"{obj.content_type.app_label}.{obj.codename}"
    #              for obj in Permission.objects.filter(
    #                  content_type__app_label="edc_dashboard")])

    def test_create_navbar_permissions(self):
        create_edc_navbar_permissions()

    #         pprint(
    #             [f"{obj.content_type.app_label}.{obj.codename}"
    #              for obj in Permission.objects.filter(
    #                  content_type__app_label="edc_navbar")])

    def test_(self):
        update_group_permissions(verbose=True)


#         for group in Group.objects.all():
#             print(group)
#             pprint(
#                 [f"{obj.content_type.app_label}.{obj.codename}"
#                  for obj in group.permissions.all()])
