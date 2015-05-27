

class VisitTrackingAdminMixin(object):
    """
    MRO requires this comes first.
    """
    def append_search_fields(self, model):
        """Extends search_fields."""
        self.search_fields = list(self.search_fields)
        item = '{}__appointment__registered_subject__subject_identifier'.format(self.visit_model_field_name)
        if item not in self.search_fields:
            self.search_fields.append(item)
        super(VisitTrackingAdminMixin, self).append_search_fields(model)

    def append_list_display(self, model):
        """Extends list display."""
        self.list_display = list(self.list_display)
        for item in [self.visit_model_field_name, 'created', 'modified', 'user_created', 'user_modified', ]:
            if item not in self.list_display:
                self.list_display.append(item)
        self.list_display = tuple(self.list_display)
        super(VisitTrackingAdminMixin, self).append_list_display(model)

    def append_list_filter(self, model):
        """Extends list filter."""
        self.list_filter = list(self.list_filter)
        extended_list_filter = [
            self.visit_model_field_name + '__report_datetime',
            self.visit_model_field_name + '__reason',
            self.visit_model_field_name + '__appointment__appt_status',
            self.visit_model_field_name + '__appointment__visit_definition__code',
            self.visit_model_field_name + '__appointment__registered_subject__site_code',
            'created',
            'modified',
            'user_created',
            'user_modified',
            'hostname_created']
        for item in extended_list_filter:
            if item not in self.list_filter:
                self.list_filter.append(item)
        self.list_filter = tuple(self.list_filter)
        super(VisitTrackingAdminMixin, self).append_list_filter(model)

#     @property
#     def visit_model_name(self):
#         """Returns the FK field attr that points a visit model or
#         any field with an appointment attribute."""
#         try:
#             default_name = 'subject_visit'
#             getattr(self.model, default_name).appointment
#             return default_name
#         except AttributeError:
#             pass
#         for field in self.model._meta.fields:
#             try:
#                 getattr(self.model, field.attr_name).appointment
#                 return field.name
#             except AttributeError:
#                 pass
#         raise ImproperlyConfigured(
#             'Admin expected {} to have a foreign key to a visit model. Got None.'.format(
#                 self.model._meta.object_name))
