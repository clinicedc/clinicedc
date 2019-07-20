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

    def get_list_display(self, request):
        super().get_list_display(request)
        fields = [self.visit_code, self.visit_reason]
        fields_first = [self.subject_identifier, "report_datetime"]
        self.list_display = list(self.list_display)
        try:
            self.list_display.remove("__str__")
        except ValueError:
            pass
        self.list_display = (
            [f for f in fields_first if f not in self.list_display]
            + self.list_display
            + [f for f in fields if f not in self.list_display]
        )
        return self.list_display

    def get_search_fields(self, request):
        super().get_search_fields(request)
        fields = [f"{self.visit_model_attr}__appointment__subject_identifier"]
        self.search_fields = [f for f in fields if f not in self.search_fields] + list(
            self.search_fields
        )
        return self.search_fields

    def get_list_filter(self, request):
        super().get_list_filter(request)
        fields = [
            f"{self.visit_model_attr}__report_datetime",
            f"{self.visit_model_attr}__appointment__visit_code",
            f"{self.visit_model_attr}__reason",
            f"{self.visit_model_attr}__appointment__appt_status",
        ]
        self.list_filter = list(self.list_filter) + [
            f for f in fields if f not in self.list_filter
        ]
        return self.list_filter

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
