from __future__ import annotations

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.urls import reverse
from django.utils.html import format_html
from edc_identifier import SubjectIdentifierError, is_subject_identifier_or_raise

from ..actions import flag_as_verified_against_paper, unflag_as_verified_against_paper


class ConsentModelAdminMixin:
    name_fields: list[str] = ["first_name", "last_name"]
    name_display_field: str = "first_name"
    actions = (flag_as_verified_against_paper, unflag_as_verified_against_paper)

    def __init__(self, *args):
        self.update_radio_fields()
        super().__init__(*args)

    def update_radio_fields(self) -> None:
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

    def get_fields(self, request, obj=None) -> tuple[str, ...]:
        original_fields = super().get_fields(request, obj=obj)
        return (
            "subject_identifier",
            *self.name_fields,
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
        ) + original_fields

    def get_readonly_fields(self, request, obj=None) -> tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj)
        fields = ("subject_identifier", "subject_identifier_as_pk")
        if obj:
            return (
                fields + ("consent_datetime", "identity", "confirm_identity") + readonly_fields
            )
        else:
            return fields + readonly_fields

    def get_search_fields(self, request) -> tuple[str, ...]:
        search_fields: tuple[str] = super().get_search_fields(request)
        name_fields: tuple[str] = tuple(self.name_fields)
        return tuple(
            set(search_fields + ("id", "subject_identifier", *name_fields, "identity"))
        )

    def get_list_display(self, request) -> tuple[str, ...]:
        list_display: tuple[str] = super().get_list_display(request)
        custom_fields = (
            "subject_identifier",
            "is_verified",
            "is_verified_datetime",
            self.name_display_field,
            "initials",
            "gender",
            "dob",
            "may_store_samples",
            "consent_datetime",
            "created",
            "modified",
            "user_created",
            "user_modified",
        )
        if request.user.has_perm("edc_data_manager.add_dataquery"):
            custom_fields = list(custom_fields)
            custom_fields.insert(3, self.queries)
        fields = tuple(custom_fields) + tuple(
            f for f in list_display if f not in custom_fields
        )
        return fields

    def get_list_filter(self, request) -> tuple[str, ...]:
        list_filter = super().get_list_filter(request)
        custom_fields = (
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
        )
        return custom_fields + tuple(f for f in list_filter if f not in custom_fields)

    def delete_view(self, request, object_id, extra_context=None):
        """Prevent deletion if SubjectVisit objects exist."""
        extra_context = extra_context or {}
        subject_consent_model_cls = django_apps.get_model(settings.SUBJECT_CONSENT_MODEL)
        related_visit_model_cls = django_apps.get_model(settings.SUBJECT_VISIT_MODEL)
        obj = subject_consent_model_cls.objects.get(id=object_id)
        try:
            protected = [
                related_visit_model_cls.objects.get(subject_identifier=obj.subject_identifier)
            ]
        except ObjectDoesNotExist:
            protected = None
        except MultipleObjectsReturned:
            protected = related_visit_model_cls.objects.filter(
                subject_identifier=obj.subject_identifier
            )
        extra_context.update({"protected": protected})
        return super().delete_view(request, object_id, extra_context)

    def get_next_options(self, request=None, **kwargs) -> dict:
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

    @admin.display(description="Open queries")
    def queries(self, obj=None) -> str:
        new_url = reverse(
            "edc_data_manager_admin:edc_data_manager_dataquery_add",
        )
        if obj.is_verified:
            formatted_html = None
        else:
            links = []
            for query_obj in obj.open_data_queries:
                url = reverse(
                    "edc_data_manager_admin:edc_data_manager_dataquery_change",
                    args=(query_obj.id,),
                )
                links.append(
                    f'<A title="go to query" href="{url}">'
                    f"{query_obj.action_identifier[-9:]}</A>"
                )
            if links:
                formatted_html = format_html(
                    "<BR>".join(links) + f'<BR><A title="New query" '
                    f'href="{new_url}">Add query</A>'
                )
            else:
                formatted_html = format_html(
                    f'<A title="New query" href="{new_url}?"'
                    f'subject_identifier={obj.subject_identifier}">Add query</A>'
                )
        return formatted_html


class ModelAdminConsentMixin(ConsentModelAdminMixin):
    pass
