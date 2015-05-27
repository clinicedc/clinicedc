In models define a proxy model packing list for each requisition model, like this

    from django.db import models
    from edc.audit.audit_trail import AuditTrail
    from lab_packing.models import PackingList


    class InfantPackingList(PackingList):
        
        history = AuditTrail()

        class Meta:
            proxy = True
            app_label = "tshipidi_lab"
            verbose_name = 'Infant Packing List' 


in the local xxxx_lab app add something like this to admin
for each packing list / requisition model defined in models. 


    from lab_packing.admin import PackingListAdmin

    class InfantPackingListAdmin(PackingListAdmin): 

        form = InfantPackingListForm
        requisition = InfantRequisition

    admin.site.register(InfantPackingList, InfantPackingListAdmin)

