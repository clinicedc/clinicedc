from typing import List, Union

from django.contrib import admin

from edc_visit_tracking.stubs import TSubjectVisitModelStub


class CrfModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to your
    visit model(s).
    """

    date_hierarchy = "report_datetime"

    def visit_reason(self, obj=None):
        return getattr(obj, self.visit_model_attr).reason

    def visit_code(self, obj=None):
        return getattr(obj, self.visit_model_attr).appointment.visit_code

    def subject_identifier(self, obj=None):
        return getattr(obj, self.visit_model_attr).subject_identifier

    def get_list_display(self: Union["CrfModelAdminMixin", admin.ModelAdmin], request) -> List:
        list_display = super().get_list_display(request)  # type: ignore
        fields = [self.visit_code, self.visit_reason]
        fields_first = [self.subject_identifier, "report_datetime"]
        list_display = list(list_display)
        try:
            list_display.remove("__str__")
        except ValueError:
            pass
        list_display = (
            [f for f in fields_first if f not in list_display]
            + list_display
            + [f for f in fields if f not in list_display]
        )
        return list_display

    def get_search_fields(self, request) -> tuple:
        search_fields = super().get_search_fields(request)
        fields = [f"{self.visit_model_attr}__appointment__subject_identifier"]
        search_fields = [f for f in fields if f not in search_fields] + list(search_fields)
        # this is weird but won't work without
        # self.search_fields = tuple(search_fields)
        return tuple(search_fields)

    def get_list_filter(self, request) -> tuple:
        list_filter = super().get_list_filter(request)
        fields = [
            f"{self.visit_model_attr}__report_datetime",
            f"{self.visit_model_attr}__visit_code",
            f"{self.visit_model_attr}__visit_code_sequence",
            f"{self.visit_model_attr}__reason",
        ]
        list_filter = [f for f in list_filter if f not in fields] + fields
        # this is weird but won't work without
        self.list_filter = tuple(list_filter)
        return self.list_filter

    @property
    def visit_model(self: admin.ModelAdmin) -> TSubjectVisitModelStub:
        return self.model.visit_model_cls()

    @property
    def visit_model_attr(self: admin.ModelAdmin) -> str:
        return self.model.visit_model_attr()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        if db_field.name == self.visit_model_attr and request.GET.get(self.visit_model_attr):
            if request.GET.get(self.visit_model_attr):
                kwargs["queryset"] = self.visit_model._default_manager.using(db).filter(
                    id__exact=request.GET.get(self.visit_model_attr)
                )
            else:
                kwargs["queryset"] = self.visit_model._default_manager.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)  # type: ignore

    def get_readonly_fields(self, request, obj=None) -> List:
        readonly_fields = super().get_readonly_fields(request, obj=obj)  # type: ignore
        if (
            not request.GET.get(self.visit_model_attr)
            and self.visit_model_attr not in readonly_fields
        ):
            readonly_fields = list(readonly_fields)
            readonly_fields.append(self.visit_model_attr)
        return readonly_fields
