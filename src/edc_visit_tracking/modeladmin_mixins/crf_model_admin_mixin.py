from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from django.contrib import admin

if TYPE_CHECKING:
    from ..model_mixins import VisitModelMixin, VisitTrackingCrfModelMixin


class CrfModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to your
    visit model(s).
    """

    date_hierarchy = "report_datetime"

    def visit_reason(self, obj: VisitTrackingCrfModelMixin | None = None) -> str:
        return getattr(obj, self.related_visit_model_attr()).reason

    def visit_code(self, obj: VisitTrackingCrfModelMixin | None = None) -> str:
        return getattr(obj, self.related_visit_model_attr()).appointment.visit_code

    def subject_identifier(self, obj: VisitTrackingCrfModelMixin | None = None) -> str:
        return getattr(obj, self.related_visit_model_attr()).subject_identifier

    def get_list_display(self, request) -> Tuple[str, ...]:
        list_display = super().get_list_display(request)
        fields_first = (
            self.subject_identifier,
            "report_datetime",
            self.visit_code,
            self.visit_reason,
        )
        return fields_first + tuple(
            f for f in list_display if f not in fields_first + ("__str__",)
        )

    def get_search_fields(self, request) -> Tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        field = (f"{self.related_visit_model_attr()}__appointment__subject_identifier",)
        if field not in search_fields:
            return search_fields + field
        return search_fields

    def get_list_filter(self, request) -> Tuple[str, ...]:
        """Returns a tuple of list_filters.

        Not working?? Call `get_list_filter`, don't explicitly set `list_filter`
        in the concrete class or any of the mixins.
        """
        list_filter = super().get_list_filter(request)
        fields = (
            f"{self.related_visit_model_attr()}__report_datetime",
            f"{self.related_visit_model_attr()}__visit_code",
            f"{self.related_visit_model_attr()}__visit_code_sequence",
            f"{self.related_visit_model_attr()}__reason",
        )
        return tuple(f for f in list_filter if f not in fields) + fields

    @property
    def visit_model(self: admin.ModelAdmin) -> VisitModelMixin:
        return self.model.related_visit_model_cls()

    def related_visit_model_attr(self: admin.ModelAdmin) -> str:
        return self.model.related_visit_model_attr()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        if db_field.name == self.related_visit_model_attr() and request.GET.get(
            self.related_visit_model_attr()
        ):
            if request.GET.get(self.related_visit_model_attr()):
                kwargs["queryset"] = self.visit_model._default_manager.using(db).filter(
                    id__exact=request.GET.get(self.related_visit_model_attr())
                )
            else:
                kwargs["queryset"] = self.visit_model._default_manager.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        if (
            not request.GET.get(self.related_visit_model_attr())
            and self.related_visit_model_attr() not in readonly_fields
        ):
            readonly_fields += (self.related_visit_model_attr(),)
        return readonly_fields
