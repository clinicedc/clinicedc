from django.contrib import admin
from django.test import TestCase, tag
from django.test.client import RequestFactory
from edc_appointment.models import Appointment
from edc_facility.import_holidays import import_holidays
from edc_model_admin import (
    ModelAdminAuditFieldsMixin,
    audit_fields,
)
from edc_visit_schedule.fieldsets import visit_schedule_fields
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..admin_site import edc_visit_tracking_admin
from ..constants import SCHEDULED
from ..modeladmin_mixins import CrfModelAdminMixin, VisitModelAdminMixin
from .helper import Helper
from .models import CrfOne, SubjectVisit
from .visit_schedule import visit_schedule1, visit_schedule2


@admin.register(SubjectVisit, site=edc_visit_tracking_admin)
class SubjectVisitModelAdmin(
        VisitModelAdminMixin,
        ModelAdminAuditFieldsMixin,
        admin.ModelAdmin):
    def get_field_queryset(self, db, db_field, request):
        return SubjectVisit.objects.all()


@admin.register(CrfOne, site=edc_visit_tracking_admin)
class CrfOneModelAdmin(
        CrfModelAdminMixin,
        ModelAdminAuditFieldsMixin,
        admin.ModelAdmin):
    def get_field_queryset(self, db, db_field, request):
        return CrfOne.objects.all()


class TestModelAdmin(TestCase):

    helper_cls = Helper

    def setUp(self):
        import_holidays()
        self.subject_identifier = "12345"
        self.helper = self.helper_cls(
            subject_identifier=self.subject_identifier)
        site_visit_schedules._registry = {}
        site_visit_schedules.register(visit_schedule=visit_schedule1)
        site_visit_schedules.register(visit_schedule=visit_schedule2)

    def test_adds_visit_model_to_list_display(self):
        factory = RequestFactory()
        request = factory.get("/")
        modeladmin = edc_visit_tracking_admin._registry.get(CrfOne)
        self.assertTrue("subject_visit", modeladmin.visit_model_attr)
        self.assertIn("subject_visit", modeladmin.get_list_display(request))

    def test_extends_list_filter(self):
        factory = RequestFactory()
        request = factory.get("/")
        modeladmin = edc_visit_tracking_admin._registry.get(CrfOne)
        self.assertIn(
            f"{modeladmin.visit_model_attr}__report_datetime", modeladmin.get_list_filter(
                request)
        )
        self.assertIn(f"{modeladmin.visit_model_attr}__reason",
                      modeladmin.get_list_filter(
                          request))
        self.assertIn(
            f"{modeladmin.visit_model_attr}__appointment__appt_status",
            modeladmin.get_list_filter(
                request),
        )
        self.assertIn(
            f"{modeladmin.visit_model_attr}__appointment__visit_code",
            modeladmin.get_list_filter(
                request),
        )

    def test_extends_search_fields(self):
        factory = RequestFactory()
        request = factory.get("/")
        modeladmin = edc_visit_tracking_admin._registry.get(CrfOne)
        self.assertIn(
            f"{modeladmin.visit_model_attr}__appointment__subject_identifier",
            modeladmin.get_search_fields(request),
        )

    def test_extends_fk_none(self):

        factory = RequestFactory()
        request = factory.get(
            "/?next=my_url_name,arg1,arg2&arg1=value1&arg2=value2&arg3=value3&arg4=value4"
        )
        modeladmin = edc_visit_tracking_admin._registry.get(CrfOne)

        class Fld:
            name = modeladmin.visit_model_attr

            def formfield(self, **kwargs):
                return kwargs

        db_field = Fld()

        kwargs = modeladmin.formfield_for_foreignkey(db_field, request)
        self.assertEqual(kwargs["queryset"].count(), 0)

    def test_extends_fk_not_none(self):

        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all(
        ).order_by("timepoint_datetime")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )

        factory = RequestFactory()
        request = factory.get(
            f"/?next=my_url_name,arg1,arg2&arg1=value1&arg2=value2&"
            f"subject_visit={str(subject_visit.id)}&arg4=value4"
        )
        modeladmin = edc_visit_tracking_admin._registry.get(CrfOne)

        CrfOne.objects.create(subject_visit=subject_visit)

        class Fld:
            name = modeladmin.visit_model_attr

            def formfield(self, **kwargs):
                return kwargs

        db_field = Fld()
        kwargs = modeladmin.formfield_for_foreignkey(db_field, request)
        self.assertGreater(kwargs["queryset"].count(), 0)

    def test_visit_extends_fk_not_none(self):

        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all(
        ).order_by("timepoint_datetime")[0]
        SubjectVisit.objects.create(appointment=appointment, reason=SCHEDULED)

        factory = RequestFactory()
        request = factory.get(
            f"/?next=my_url_name,arg1,arg2&arg1=value1&arg2=value2"
            f"&appointment={str(appointment.id)}"
        )
        modeladmin = edc_visit_tracking_admin._registry.get(SubjectVisit)

        class Fld:
            name = "appointment"

            related_model = Appointment

            def formfield(self, **kwargs):
                return kwargs

        db_field = Fld()
        kwargs = modeladmin.formfield_for_foreignkey(db_field, request)
        self.assertGreater(kwargs["queryset"].count(), 0)

    def test_crf_readonly(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all(
        ).order_by("timepoint_datetime")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )

        crf_one = CrfOne.objects.create(subject_visit=subject_visit)

        factory = RequestFactory()
        request = factory.get(
            f"/?next=my_url_name,arg1,arg2&arg1=value1&arg2=value2"
            f"&subject_visit={str(subject_visit.id)}"
        )
        modeladmin = edc_visit_tracking_admin._registry.get(CrfOne)
        for field in audit_fields:
            self.assertIn(field, modeladmin.get_readonly_fields(
                request, obj=crf_one))

    def test_visit_readonly(self):
        self.helper.consent_and_put_on_schedule()
        appointment = Appointment.objects.all(
        ).order_by("timepoint_datetime")[0]
        subject_visit = SubjectVisit.objects.create(
            appointment=appointment, reason=SCHEDULED
        )

        factory = RequestFactory()
        request = factory.get(
            f"/?next=my_url_name,arg1,arg2&arg1=value1&arg2=value2"
            f"&appointment={str(appointment.id)}"
        )
        modeladmin = edc_visit_tracking_admin._registry.get(SubjectVisit)
        for field in audit_fields:
            self.assertIn(
                field, modeladmin.get_readonly_fields(
                    request, obj=subject_visit)
            )
        for field in visit_schedule_fields:
            self.assertIn(
                field, modeladmin.get_readonly_fields(
                    request, obj=subject_visit)
            )
