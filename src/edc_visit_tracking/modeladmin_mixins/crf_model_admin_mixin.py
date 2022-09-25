from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from edc_crf.model_mixins import CrfModelMixin

    from ..model_mixins import VisitModelMixin


class CrfModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to your
    visit model(s).
    """

    date_hierarchy = "report_datetime"
    report_datetime_field_attr = "report_datetime"

    def visit_reason(self, obj: CrfModelMixin | None = None) -> str:
        return getattr(obj, self.related_visit_model_attr).reason

    def visit_code(self, obj: CrfModelMixin | None = None) -> str:
        return getattr(obj, self.related_visit_model_attr).visit_code

    def visit_code_sequence(self, obj: CrfModelMixin | None = None) -> int:
        return getattr(obj, self.related_visit_model_attr).visit_code_sequence

    def subject_identifier(self, obj: CrfModelMixin | None = None) -> str:
        return getattr(obj, self.related_visit_model_attr).subject_identifier

    def get_list_display(self, request: WSGIRequest) -> Tuple[str, ...]:
        list_display = super().get_list_display(request)
        fields_first = (
            self.subject_identifier,
            self.report_datetime_field_attr,
            self.visit_code,
            self.visit_reason,
        )
        return fields_first + tuple(
            f for f in list_display if f not in fields_first + ("__str__",)
        )

    def get_search_fields(self, request: WSGIRequest) -> Tuple[str, ...]:
        search_fields = super().get_search_fields(request)
        field = (f"{self.related_visit_model_attr}__appointment__subject_identifier",)
        if field not in search_fields:
            return search_fields + field
        return search_fields

    def get_list_filter(self, request: WSGIRequest) -> Tuple[str, ...]:
        """Returns a tuple of list_filters.

        Not working?? Call `get_list_filter`, don't explicitly set `list_filter`
        in the concrete class or any of the mixins.
        """
        list_filter = super().get_list_filter(request)
        fields = (
            f"{self.related_visit_model_attr}__{self.report_datetime_field_attr}",
            f"{self.related_visit_model_attr}__visit_code",
            f"{self.related_visit_model_attr}__visit_code_sequence",
            f"{self.related_visit_model_attr}__reason",
        )
        return tuple(f for f in list_filter if f not in fields) + fields

    @property
    def related_visit_model_attr(self) -> str:
        return self.model.related_visit_model_attr()

    @property
    def related_visit_model_cls(self) -> VisitModelMixin:
        return self.model.related_visit_model_cls()

    def related_visit(self, request: WSGIRequest, obj=None) -> VisitModelMixin | None:
        """Returns the related_visit from the request object"""
        related_visit = self.related_visit_model_cls.objects.get(
            id=self.related_visit_id(request)
        )
        if not related_visit and obj:
            related_visit = getattr(obj, self.related_visit_model_attr)
        return related_visit

    def related_visit_id(self, request) -> str:
        """Returns the record id/pk for the related visit"""
        return request.GET.get(self.related_visit_model_attr)

    def formfield_for_foreignkey(self, db_field, request: WSGIRequest, **kwargs):
        db = kwargs.get("using")
        if db_field.name == self.related_visit_model_attr:
            if related_visit_id := self.related_visit_id(request):
                kwargs["queryset"] = self.related_visit_model_cls._default_manager.using(
                    db
                ).filter(id__exact=related_visit_id)
            else:
                kwargs["queryset"] = self.related_visit_model_cls._default_manager.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(
        self, request: WSGIRequest, obj: CrfModelMixin | None = None
    ) -> Tuple[str, ...]:
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        if (
            not self.related_visit_id(request)
            and self.related_visit_model_attr not in readonly_fields
        ):
            readonly_fields += (self.related_visit_model_attr,)
        return readonly_fields
