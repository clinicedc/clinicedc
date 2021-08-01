import pdb
from unittest import skip

from django.apps import apps as django_apps
from django.contrib.auth import get_user_model
from django.urls.base import reverse
from django_webtest import WebTest
from edc_action_item.models.action_item import ActionItem
from edc_auth import CLINIC, DATA_MANAGER, EVERYONE
from edc_auth.group_permissions_updater import GroupPermissionsUpdater
from edc_lab.site_labs import site_labs
from edc_registration.models import RegisteredSubject
from edc_test_utils.webtest import login
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from model_bakery import baker

from data_manager_app.lab_profiles import lab_profile
from data_manager_app.reference_model_configs import register_to_site_reference_configs
from data_manager_app.visit_schedules import visit_schedule
from edc_data_manager.models import CrfDataDictionary, DataQuery
from edc_data_manager.models.user import DataManagerUser

User = get_user_model()


class AdminSiteTest(WebTest):
    def setUp(self):
        self.subject_identifier = "101-123456789"
        self.user = User.objects.create(
            username="user_login",
            email="u@example.com",
            password="pass",
            is_active=True,
            is_staff=True,
        )

        GroupPermissionsUpdater(
            excluded_app_labels=["django_celery_beat", "django_celery_results"],
            apps=django_apps,
        )
        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=lab_profile)

        register_to_site_reference_configs()
        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

    def test_default_rule_handler_names(self):
        """Assert default rule handler names on queryrule ADD form"""
        login(
            self,
            user=self.user,
            groups=[EVERYONE, DATA_MANAGER],
            redirect_url="admin:index",
        )
        url = reverse("data_manager_app:home_url")
        response = self.app.get(url, user=self.user, status=200)
        self.assertIn("You are home", response)

        url = reverse("edc_data_manager_admin:edc_data_manager_queryrule_add")
        response = self.app.get(url, user=self.user, status=200)

        self.assertIn('<option value="do_nothing"', response)
        self.assertIn('<option value="default"', response)

    @skip("need to fix permissions")
    def test_query_rule_questions_from_single_form(self):
        login(
            self,
            superuser=False,
            groups=[EVERYONE, DATA_MANAGER],
            redirect_url="admin:index",
        )

        query_rule = baker.make_recipe(
            "edc_data_manager.queryrule",
            sender=DataManagerUser.objects.get(username=self.user.username),
        )

        crf = CrfDataDictionary.objects.all()[0]
        query_rule.data_dictionaries.add(crf)
        crf = CrfDataDictionary.objects.all()[1]
        query_rule.data_dictionaries.add(crf)

        url = reverse(
            "edc_data_manager_admin:edc_data_manager_queryrule_change", args=(query_rule.pk,)
        )
        res = self.app.get(url, user=self.user)

        form = res.form
        res = form.submit()
        self.assertIn("Invalid. Select questions from one CRF only", str(res))

    @skip("need to fix permissions")
    def test_data_query_questions_from_single_form(self):
        login(
            self,
            superuser=False,
            groups=[EVERYONE, DATA_MANAGER],
            redirect_url="admin:index",
        )

        registered_subject = RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier
        )

        data_query = baker.make_recipe(
            "edc_data_manager.dataquery",
            registered_subject=registered_subject,
            sender=DataManagerUser.objects.get(username=self.user.username),
        )

        crf = CrfDataDictionary.objects.all()[0]
        data_query.data_dictionaries.add(crf)
        crf = CrfDataDictionary.objects.all()[1]
        data_query.data_dictionaries.add(crf)

        url = reverse(
            "edc_data_manager_admin:edc_data_manager_dataquery_change", args=(data_query.pk,)
        )
        res = self.app.get(url, user=self.user, status=200)

        form = res.form
        res = form.submit()
        self.assertIn("Invalid. Select questions from one CRF only", res)

    def test_data_query(self):
        login(
            self,
            superuser=False,
            groups=[EVERYONE, DATA_MANAGER],
            redirect_url="admin:index",
        )

        registered_subject = RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier
        )

        data_query = baker.make_recipe(
            "edc_data_manager.dataquery",
            registered_subject=registered_subject,
            sender=DataManagerUser.objects.get(username=self.user.username),
        )

        crf = CrfDataDictionary.objects.all()[0]
        data_query.data_dictionaries.add(crf)

        url = reverse(
            "edc_data_manager_admin:edc_data_manager_dataquery_change", args=(data_query.pk,)
        )
        form = self.app.get(url, user=self.user).form
        response = form.submit().follow()
        self.assertIn("was changed successfully", str(response.content))

        # try without a `data_dictionary` (list of crfs)
        data_query = baker.make_recipe(
            "edc_data_manager.dataquery",
            registered_subject=registered_subject,
            sender=DataManagerUser.objects.get(username=self.user.username),
        )

        url = reverse(
            "edc_data_manager_admin:edc_data_manager_dataquery_change", args=(data_query.pk,)
        )
        form = self.app.get(url, user=self.user).form
        response = form.submit().follow()
        self.assertIn("was changed successfully", str(response.content))

    def test_data_query_add_and_permissions(self):
        login(
            self,
            superuser=False,
            groups=[EVERYONE, DATA_MANAGER],
            redirect_url="admin:index",
        )

        registered_subject = RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier
        )

        url = reverse("edc_data_manager_admin:edc_data_manager_dataquery_add")
        form = self.app.get(
            (
                f"{url}?subject_identifier={self.subject_identifier}&"
                f"registered_subject={str(registered_subject.pk)}&"
                f"sender={str(DataManagerUser.objects.get(username=self.user.username).pk)}"
            ),
            user=self.user,
        ).form
        form["title"] = "My first query"
        form["query_text"] = "this is a query"
        response = form.submit().follow()

        self.assertIn("was added successfully", str(response))
        self.app.get(reverse("admin:logout"), user=self.user, status=200)

        login(
            self,
            superuser=False,
            groups=[EVERYONE, CLINIC],
            redirect_url="admin:index",
        )

        data_query = DataQuery.objects.get(title="My first query")
        url = reverse(
            "edc_data_manager_admin:edc_data_manager_dataquery_change", args=(data_query.pk,)
        )
        form = self.app.get(url, user=self.user).form
        response = form.submit().follow()
        self.assertIn("was changed successfully", str(response))

    def test_data_query_action_attrs(self):
        login(
            self,
            superuser=False,
            groups=[EVERYONE, DATA_MANAGER, CLINIC],
            redirect_url="admin:index",
        )

        registered_subject = RegisteredSubject.objects.create(
            subject_identifier=self.subject_identifier
        )

        data_query = baker.make_recipe(
            "edc_data_manager.dataquery",
            registered_subject=registered_subject,
            sender=DataManagerUser.objects.get(username=self.user.username),
        )

        crf = CrfDataDictionary.objects.all()[0]
        data_query.data_dictionaries.add(crf)

        ActionItem.objects.get(action_identifier=data_query.action_identifier)
        self.assertIn("SITE QUERY", data_query.action.get_display_name())
        self.assertIn("SITE QUERY", data_query.action.get_display_name())
