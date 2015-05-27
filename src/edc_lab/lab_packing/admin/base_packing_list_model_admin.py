from edc_base.modeladmin.admin import BaseModelAdmin


class BasePackingListModelAdmin(BaseModelAdmin):

    fields = ('destination', 'list_items', 'list_comment',)
    list_display = ('reference', 'view_list_items', 'list_datetime',
                    'list_comment', 'destination', 'received', )
    list_filter = ('list_datetime', 'destination', 'received', 'list_comment')
    search_fields = ('id', )
