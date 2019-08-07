from data_manager_app.lab_profiles import lab_profile
from data_manager_app.visit_schedules import visit_schedule
from django.contrib.auth import get_user_model
from django.core import serializers
from django.test import TestCase, tag
from edc_data_manager.models.requisition_panel import RequisitionPanel
from edc_data_manager.models.user import DataManagerUser, QueryUser
from edc_lab.site_labs import site_labs
from edc_visit_schedule.apps import populate_visit_schedule
from edc_visit_schedule.constants import HOURS
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ...models import CrfDataDictionary, QueryRule, QueryVisitSchedule


class TestSerializer(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            "user_login", "u@example.com", "pass"
        )

        site_labs._registry = {}
        site_labs.loaded = False
        site_labs.register(lab_profile=lab_profile)

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)
        populate_visit_schedule()

    def test_(self):

        self.assertGreater(QueryVisitSchedule.objects.all().count(), 0)
        self.assertGreater(CrfDataDictionary.objects.all().count(), 0)
        self.assertGreater(DataManagerUser.objects.all().count(), 0)
        self.assertGreater(QueryUser.objects.all().count(), 0)
        self.assertGreater(RequisitionPanel.objects.all().count(), 0)

        all_objects = [
            QueryVisitSchedule.objects.all(),
            CrfDataDictionary.objects.all(),
            RequisitionPanel.objects.all(),
            DataManagerUser.objects.all(),
            QueryUser.objects.all(),
        ]
        json_data = []
        for qs in all_objects:
            json_data.append(
                serializers.serialize(
                    "json",
                    qs,
                    indent=4,
                    use_natural_foreign_keys=True,
                    use_natural_primary_keys=False,
                    object_count=1,
                )
            )

            qs.model.objects.all().delete()

        for data in json_data:
            for deserialized_object in serializers.deserialize(
                "json",
                data,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=False,
            ):
                deserialized_object.save()

        # create a rule
        question1 = CrfDataDictionary.objects.get(
            model="data_manager_app.crfone", field_name="f1"
        )
        question2 = CrfDataDictionary.objects.get(
            model="data_manager_app.crftwo", field_name="f1"
        )

        visit_schedule1 = QueryVisitSchedule.objects.get(visit_code="1000")
        visit_schedule2 = QueryVisitSchedule.objects.get(visit_code="2000")

        opts = dict(title="test rule", sender=self.user, timing=48, timing_units=HOURS)
        query_rule = QueryRule.objects.create(**opts)
        query_rule.data_dictionaries.add(question1)
        query_rule.data_dictionaries.add(question2)
        query_rule.visit_schedule.add(visit_schedule1)
        query_rule.visit_schedule.add(visit_schedule2)
        query_rule.save()

        json_text = serializers.serialize(
            "json",
            QueryRule.objects.all(),
            indent=4,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=False,
            object_count=1,
        )

        QueryRule.objects.all().delete()

        for deserialized_object in serializers.deserialize(
            "json",
            json_text,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=False,
        ):
            deserialized_object.save()

        self.assertGreater(QueryRule.objects.all().count(), 0)
        self.assertGreater(QueryVisitSchedule.objects.all().count(), 0)
        self.assertGreater(CrfDataDictionary.objects.all().count(), 0)
        self.assertGreater(DataManagerUser.objects.all().count(), 0)
        self.assertGreater(QueryUser.objects.all().count(), 0)
        self.assertGreater(RequisitionPanel.objects.all().count(), 0)
