
class ModelAdminBasicMixin:

    """Merge ModelAdmin attributes with the concrete class attributes
    fields, radio_fields, list_display, list_filter and search_fields.

    `mixin_exclude_fields` is a list of fields included in the mixin
    but not wanted on the concrete.

    Use for a ModelAdmin mixin prepared for an abstract models,
    e.g. edc_consent.models.BaseConsent.
    """

    mixin_fields = []

    mixin_radio_fields = {}

    mixin_list_display = []
    list_display_pos = []

    mixin_list_filter = []
    list_filter_pos = []

    mixin_search_fields = []

    mixin_exclude_fields = []

    def reorder(self, original_list):
        """Return an ordered list after inserting list items from the
        original that were passed tuples of (index, item).
        """
        new_list = []
        items_with_pos = []
        for index, item in enumerate(original_list):
            try:
                _, _ = item
                items_with_pos.append(item)
            except (ValueError, TypeError):
                new_list.append(item)
        for index, item in items_with_pos:
            try:
                new_list.pop(new_list.index(item))
            except ValueError:
                pass
            new_list.insert(index, item)
        return new_list

    def get_list_display(self, request):
        self.list_display = list(
            super(ModelAdminBasicMixin, self).get_list_display(request) or [])
        self.list_display = self.reorder(
            list(self.list_display) + list(self.list_display_pos or []))
        self.list_display = self.extend_from(
            self.list_display, self.mixin_list_display or [])
        self.list_display = self.remove_from(self.list_display)
        return tuple(self.list_display)

    def get_list_filter(self, request):
        self.list_filter = list(
            super(ModelAdminBasicMixin, self).get_list_filter(request) or [])
        self.list_filter = self.reorder(
            list(self.list_filter) + list(self.list_filter_pos or []))
        self.list_filter = self.update_from_mixin(
            self.list_filter, self.mixin_list_filter or [])
        return tuple(self.list_filter)

    def get_search_fields(self, request):
        self.search_fields = list(
            super(ModelAdminBasicMixin, self).get_search_fields(request) or [])
        self.search_fields = self.update_from_mixin(
            self.search_fields, self.mixin_search_fields or [])
        return tuple(self.search_fields)

    def get_fields(self, request, obj=None):
        self.radio_fields = self.get_radio_fields(request, obj)
        if self.mixin_fields:
            self.fields = self.update_from_mixin(
                self.fields, self.mixin_fields or [])
            return self.fields
        elif self.fields:
            return self.fields
        form = self.get_form(request, obj, fields=None)
        return list(form.base_fields) + list(self.get_readonly_fields(request, obj))

    def update_from_mixin(self, field_list, mixin_field_list):
        field_list = self.extend_from(field_list or [], mixin_field_list or [])
        field_list = self.remove_from(field_list or [])
        return tuple(field_list)

    def extend_from(self, field_list, mixin_field_list):
        return (list(field_list)
                + list([fld for fld in mixin_field_list if fld not in field_list]))

    def remove_from(self, field_list):
        field_list = list(field_list)
        for field in self.mixin_exclude_fields:
            try:
                field_list.remove(field)
            except ValueError:
                pass
        return tuple(field_list)

    def get_radio_fields(self, request, obj=None):
        self.radio_fields.update(self.mixin_radio_fields)
        for key in self.mixin_exclude_fields:
            try:
                del self.mixin_radio_fields[key]
            except KeyError:
                pass
        return self.radio_fields
