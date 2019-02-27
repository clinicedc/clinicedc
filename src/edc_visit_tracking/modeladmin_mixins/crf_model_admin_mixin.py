from edc_model_admin.model_admin_audit_fields_mixin import audit_fields


class CrfModelAdminMixin:

    """ModelAdmin subclass for models with a ForeignKey to your
    visit model(s).
    """

    date_hierarchy = "report_datetime"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display = list(self.list_display)
        self.list_display.append(self.visit_model_attr)
        self.list_display = tuple(self.list_display)
        self.extend_search_fields()
        self.extend_list_filter()

    @property
    def visit_model(self):
        return self.model.visit_model_cls()

    @property
    def visit_model_attr(self):
        return self.model.visit_model_attr()

    def extend_search_fields(self):
        self.search_fields = list(self.search_fields)
        self.search_fields.extend(
            [f"{self.visit_model_attr}__appointment__subject_identifier"]
        )
        self.search_fields = tuple(set(self.search_fields))

    def extend_list_filter(self):
        """Extends list filter with additional values from the visit
        model.
        """
        self.list_filter = list(self.list_filter)
        self.list_filter.extend(
            [
                f"{self.visit_model_attr}__report_datetime",
                f"{self.visit_model_attr}__reason",
                f"{self.visit_model_attr}__appointment__appt_status",
                f"{self.visit_model_attr}__appointment__visit_code",
            ]
        )
        self.list_filter = tuple(self.list_filter)

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

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj=obj)
        return fields + audit_fields
