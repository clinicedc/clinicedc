from edc_lab.models import Panel


class RequisitionPanel(Panel):
    class Meta:
        proxy = True
        default_permissions = ("view",)
        verbose_name = "Requisition Panel"
        verbose_name_plural = "Requisition Panels"
