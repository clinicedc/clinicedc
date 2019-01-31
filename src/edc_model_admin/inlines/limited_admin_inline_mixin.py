class LimitedAdminInlineMixin:
    """Limit choices on a foreignkey field in an inline to a value
    on the parent model.

    From getresults_csv. For example, model CsvDictionary is an
    inline to CsvFormat. The inline has a foreignkey to model
    CsvFields. By using the mixin, csv_field is filtered by the
    value of csv_format instead of showing everything in CsvFields.

        class CsvDictionaryInline(LimitedAdminInlineMixin,
                                  admin.TabularInline):
            model = CsvDictionary
            form = CsvDictionaryForm
            extra = 0

            def get_filters(self, obj):
                if obj:
                    return (('csv_field', dict(csv_format=obj.id)),)
                else:
                    return ()

        class CsvFormatAdmin(admin.ModelAdmin):
            inlines = [CsvDictionaryInline]
        admin_site.register(CsvFormat, CsvFormatAdmin)
    """

    @staticmethod
    def limit_inline_choices(formset, field, empty=False, **filters):
        assert field in formset.form.base_fields
        qs = formset.form.base_fields[field].queryset
        if empty:
            formset.form.base_fields[field].queryset = qs.none()
        else:
            qs = qs.filter(**filters)
            formset.form.base_fields[field].queryset = qs

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(LimitedAdminInlineMixin, self).get_formset(
            request, obj, **kwargs
        )

        for (field, filters) in self.get_filters(obj):
            if obj:
                self.limit_inline_choices(formset, field, **filters)
            else:
                self.limit_inline_choices(formset, field, empty=True)

        return formset

    def get_filters(self, obj):
        return getattr(self, "filters", ())
