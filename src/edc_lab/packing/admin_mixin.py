from django.contrib import admin


class PackingListModelAdminMixin(admin.ModelAdmin):

    fields = ('destination', 'list_items', 'list_comment',)

    list_display = (
        'reference',
        'view_list_items',
        'list_datetime',
        'list_comment',
        'destination',
        'received', )

    list_filter = (
        'list_datetime',
        'destination',
        'received',
        'list_comment')

    search_fields = ('id', 'list_comment')


class PackingListItemModelAdminMixin(admin.ModelAdmin):

    search_fields = ('packing_list__pk', 'packing_list__timestamp', 'item_description', 'item_reference', )
    list_display = ('specimen', 'priority', 'panel', 'description', 'gender',
                    'drawn_datetime', 'clinician', 'view_packing_list', 'received', 'received_datetime',)
    list_filter = ('created', 'panel', 'received', 'received_datetime',)

    def delete_model(self, request, obj):

        if not isinstance(self.subject_requisition, list):
            self.subject_requisition = [self.subject_requisition, ]
        for requisition in self.requisition:
            if requisition.objects.filter(specimen_identifier=obj.item_reference):
                subject_requisition = requisition.objects.get(specimen_identifier=obj.item_reference)
                subject_requisition.is_packed = False
                subject_requisition.save()
        super(PackingListItemModelAdminMixin, self).delete_model(request, obj)
