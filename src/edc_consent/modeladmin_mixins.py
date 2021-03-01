from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from edc_identifier import SubjectIdentifierError, is_subject_identifier_or_raise

from .actions import flag_as_verified_against_paper, unflag_as_verified_against_paper


class ModelAdminConsentMixin(admin.ModelAdmin):
    def __init__(self, *args):
        self.get_radio_fields()
        super().__init__(*args)

    actions = [flag_as_verified_against_paper, unflag_as_verified_against_paper]

    def get_radio_fields(self):
        self.radio_fields.update(
            {
                "language": admin.VERTICAL,
                "gender": admin.VERTICAL,
                "is_dob_estimated": admin.VERTICAL,
                "identity_type": admin.VERTICAL,
                "is_incarcerated": admin.VERTICAL,
                "may_store_samples": admin.VERTICAL,
                "consent_reviewed": admin.VERTICAL,
                "study_questions": admin.VERTICAL,
                "assessment_score": admin.VERTICAL,
                "consent_copy": admin.VERTICAL,
                "is_literate": admin.VERTICAL,
            }
        )

    def get_fields(self, request, obj=None):
        return [
            "subject_identifier",
            "first_name",
            "last_name",
            "initials",
            "language",
            "is_literate",
            "witness_name",
            "consent_datetime",
            "gender",
            "dob",
            "is_dob_estimated",
            "guardian_name",
            "identity",
            "identity_type",
            "confirm_identity",
            "is_incarcerated",
            "may_store_samples",
            "comment",
            "consent_reviewed",
            "study_questions",
            "assessment_score",
            "consent_copy",
        ] + super().get_fields(request, obj=obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        fields = ["subject_identifier", "subject_identifier_as_pk"]
        if obj:
            fields.append("consent_datetime")
            return fields + list(readonly_fields)
        else:
            return fields + list(readonly_fields)

    def get_search_fields(self, request):
        search_fields = list(super().get_search_fields(request))
        return list(search_fields) + [
            "id",
            "subject_identifier",
            "first_name",
            "last_name",
            "identity",
        ]

    def get_list_display(self, request):
        return [
            "subject_identifier",
            "is_verified",
            "is_verified_datetime",
            "first_name",
            "initials",
            "gender",
            "dob",
            "may_store_samples",
            "consent_datetime",
            "created",
            "modified",
            "user_created",
            "user_modified",
        ] + list(super().get_list_display(request))

    def get_list_filter(self, request):
        super().get_list_filter(request)
        fields = [
            "gender",
            "is_verified",
            "is_verified_datetime",
            "language",
            "may_store_samples",
            "is_literate",
            "consent_datetime",
            "created",
            "modified",
            "user_created",
            "user_modified",
            "hostname_created",
        ]
        self.list_filter = [f for f in fields if f not in self.list_filter] + list(
            self.list_filter
        )
        return self.list_filter

    def delete_view(self, request, object_id, extra_context=None):
        """Prevent deletion if SubjectVisit objects exist."""
        extra_context = extra_context or {}
        subject_consent_model_cls = django_apps.get_model(settings.SUBJECT_CONSENT_MODEL)
        subject_visit_model_cls = django_apps.get_model(settings.SUBJECT_VISIT_MODEL)
        obj = subject_consent_model_cls.objects.get(id=object_id)
        try:
            protected = [
                subject_visit_model_cls.objects.get(subject_identifier=obj.subject_identifier)
            ]
        except ObjectDoesNotExist:
            protected = None
        except MultipleObjectsReturned:
            protected = subject_visit_model_cls.objects.filter(
                subject_identifier=obj.subject_identifier
            )
        extra_context.update({"protected": protected})
        return super().delete_view(request, object_id, extra_context)

    def get_next_options(self, request=None, **kwargs):
        """Returns the key/value pairs from the "next" querystring
        as a dictionary.
        """
        subject_screening_model_cls = django_apps.get_model(settings.SUBJECT_SCREENING_MODEL)
        next_options = super().get_next_options(request=request, **kwargs)
        try:
            is_subject_identifier_or_raise(next_options["subject_identifier"])
        except SubjectIdentifierError:
            next_options["subject_identifier"] = subject_screening_model_cls.objects.get(
                subject_identifier_as_pk=next_options["subject_identifier"]
            ).subject_identifier
        except KeyError:
            pass
        return next_options
