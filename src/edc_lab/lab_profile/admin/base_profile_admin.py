from edc_base.modeladmin.admin import BaseModelAdmin


class BaseProfileAdmin(BaseModelAdmin):

    list_display = ('name', 'aliquot_type', 'created', 'modified', 'user_created', 'user_modified')

    search_fields = ('name', 'aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code')

    list_filter = ('aliquot_type__name', 'aliquot_type__alpha_code', 'aliquot_type__numeric_code', 'created', 'modified', 'user_created', 'user_modified')

    # add this when you create the class
    #inlines = [ProfileItemInlineAdmin]
