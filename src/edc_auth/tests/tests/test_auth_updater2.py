from copy import copy

from django.contrib.auth.models import Group
from django.test import TestCase, override_settings, tag

from edc_auth.auth_updater import AuthUpdater
from edc_auth.site_auths import site_auths


@tag("auth")
@override_settings(
    EDC_AUTH_SKIP_SITE_AUTHS=True,
    EDC_AUTH_SKIP_AUTH_UPDATER=False,
)
class TestAuthUpdater2(TestCase):
    def test_add_group(self):
        codenames = [
            "clinicedc_tests.add_testmodel",
            "clinicedc_tests.change_testmodel",
            "clinicedc_tests.delete_testmodel",
            "clinicedc_tests.view_testmodel",
        ]
        site_auths.clear()
        site_auths.add_group(*codenames, name="GROUP")
        AuthUpdater()
        group = Group.objects.get(name="GROUP")
        self.assertEqual(
            [
                p.codename
                for p in group.permissions.filter(
                    content_type__app_label="clinicedc_tests"
                )
            ],
            [c.split(".")[1] for c in codenames],
        )

    def test_add_group_with_callable(self):
        def codenames_callable() -> list[str]:
            return [
                "clinicedc_tests.add_subjectrequisition",
                "clinicedc_tests.change_subjectrequisition",
                "clinicedc_tests.delete_subjectrequisition",
                "clinicedc_tests.view_subjectrequisition",
            ]

        codenames = [
            "clinicedc_tests.add_testmodel",
            "clinicedc_tests.change_testmodel",
            "clinicedc_tests.delete_testmodel",
            "clinicedc_tests.view_testmodel",
        ]
        codenames_with_callable: list = copy(codenames)
        codenames_with_callable.append(codenames_callable)
        site_auths.clear()
        site_auths.add_group(*codenames_with_callable, name="GROUP")
        AuthUpdater(verbose=False, warn_only=True)
        group = Group.objects.get(name="GROUP")

        codenames.extend(codenames_callable())
        codenames.sort()
        self.assertEqual(
            [
                p.codename
                for p in group.permissions.filter(
                    content_type__app_label="clinicedc_tests"
                ).order_by("codename")
            ],
            [c.split(".")[1] for c in codenames],
        )

    def test_add_group_view_only(self):
        codenames = [
            "clinicedc_tests.add_testmodel",
            "clinicedc_tests.change_testmodel",
            "clinicedc_tests.delete_testmodel",
            "clinicedc_tests.view_testmodel",
        ]
        site_auths.clear()
        site_auths.add_group(*codenames, name="GROUP_VIEW_ONLY", view_only=True)
        AuthUpdater(verbose=False, warn_only=True)
        group = Group.objects.get(name="GROUP_VIEW_ONLY")
        self.assertEqual(
            [
                p.codename
                for p in group.permissions.filter(
                    content_type__app_label="clinicedc_tests"
                )
            ],
            ["view_testmodel"],
        )

    def test_add_group_view_only_with_callable(self):
        def more_codenames():
            return [
                "clinicedc_tests.add_subjectrequisition",
                "clinicedc_tests.change_subjectrequisition",
                "clinicedc_tests.delete_subjectrequisition",
                "clinicedc_tests.view_subjectrequisition",
            ]

        codenames = [
            "clinicedc_tests.add_testmodel",
            "clinicedc_tests.change_testmodel",
            "clinicedc_tests.delete_testmodel",
            "clinicedc_tests.view_testmodel",
            more_codenames,
        ]
        site_auths.clear()
        site_auths.add_group(*codenames, name="GROUP_VIEW_ONLY", view_only=True)
        AuthUpdater(verbose=False, warn_only=True)
        group = Group.objects.get(name="GROUP_VIEW_ONLY")
        self.assertEqual(
            [
                p.codename
                for p in group.permissions.filter(
                    content_type__app_label="clinicedc_tests"
                )
            ],
            ["view_subjectrequisition", "view_testmodel"],
        )

    def test_add_group_convert_to_export_with_callable(self):
        def more_codenames():
            return [
                "clinicedc_tests.add_subjectrequisition",
                "clinicedc_tests.change_subjectrequisition",
                "clinicedc_tests.delete_subjectrequisition",
                "clinicedc_tests.view_subjectrequisition",
            ]

        codenames = [
            "clinicedc_tests.add_testmodel",
            "clinicedc_tests.change_testmodel",
            "clinicedc_tests.delete_testmodel",
            "clinicedc_tests.view_testmodel",
            more_codenames,
        ]

        site_auths.clear()
        # export permissions are custom, you need to add to the
        # permissions model if not already on the model
        for model, codename in [
            (
                "clinicedc_tests.subjectrequisition",
                "clinicedc_tests.export_subjectrequisition",
            ),
            ("clinicedc_tests.testmodel", "clinicedc_tests.export_testmodel"),
        ]:
            site_auths.add_custom_permissions_tuples(
                model=model,
                codename_tuples=((codename, f"Can access {codename.split('.')[1]}"),),
            )
        site_auths.add_group(*codenames, name="GROUP_EXPORT", convert_to_export=True)
        AuthUpdater(verbose=False, warn_only=True)
        group = Group.objects.get(name="GROUP_EXPORT")
        self.assertEqual(
            [
                p.codename
                for p in group.permissions.filter(
                    content_type__app_label="clinicedc_tests"
                )
            ],
            ["export_subjectrequisition", "export_testmodel"],
        )

    def test_add_group_remove_delete_with_callable(self):
        def more_codenames():
            return [
                "clinicedc_tests.add_subjectrequisition",
                "clinicedc_tests.change_subjectrequisition",
                "clinicedc_tests.delete_subjectrequisition",
                "clinicedc_tests.view_subjectrequisition",
            ]

        codenames = [
            "clinicedc_tests.add_testmodel",
            "clinicedc_tests.change_testmodel",
            "clinicedc_tests.delete_testmodel",
            "clinicedc_tests.view_testmodel",
            more_codenames,
        ]
        site_auths.clear()
        site_auths.add_group(*codenames, name="GROUP_NO_DELETE", no_delete=True)
        AuthUpdater(verbose=False, warn_only=True)
        group = Group.objects.get(name="GROUP_NO_DELETE")

        codenames = [
            "add_subjectrequisition",
            "add_testmodel",
            "change_subjectrequisition",
            "change_testmodel",
            "view_subjectrequisition",
            "view_testmodel",
        ]
        self.assertEqual(
            [
                p.codename
                for p in group.permissions.filter(
                    content_type__app_label="clinicedc_tests"
                ).order_by("codename")
            ],
            codenames,
        )
