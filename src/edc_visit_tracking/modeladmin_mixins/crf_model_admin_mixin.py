
class CrfModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to your
    visit model(s).
    """

    date_hierarchy = "report_datetime"

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display = list(list_display)
        list_display.append(self.visit_model_attr)
        return list_display

    def get_search_fields(self, request):
        search_fields = super().get_search_fields(request)
        search_fields = list(search_fields)
        search_fields.extend(
            [f"{self.visit_model_attr}__appointment__subject_identifier"]
        )
        return search_fields

    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        list_filter = list(list_filter)
        list_filter.extend(
            [
                f"{self.visit_model_attr}__report_datetime",
                f"{self.visit_model_attr}__reason",
                f"{self.visit_model_attr}__appointment__appt_status",
                f"{self.visit_model_attr}__appointment__visit_code",
            ]
        )
        return list_filter

    @property
    def visit_model(self):
        return self.model.visit_model_cls()

    @property
    def visit_model_attr(self):
        return self.model.visit_model_attr()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        db = kwargs.get("using")
        if db_field.name == self.visit_model_attr and request.GET.get(
            self.visit_model_attr
        ):
            if request.GET.get(self.visit_model_attr):
                kwargs["queryset"] = self.visit_model._default_manager.using(db).filter(
                    id__exact=request.GET.get(self.visit_model_attr)
                )
            else:
                kwargs["queryset"] = self.visit_model._default_manager.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
