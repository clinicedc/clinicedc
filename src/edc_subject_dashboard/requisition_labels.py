from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import NO
from edc_lab.labels import RequisitionLabel


class RequisitionLabels:

    label_cls = RequisitionLabel
    label_template_name = "requisition"

    def __init__(
        self, requisition_metadata=None, panel_names=None, appointment=None, user=None
    ):
        zpl_datas = []
        self.requisitions_not_printed = []
        self.appointment = appointment
        for metadata in requisition_metadata.filter(panel_name__in=panel_names):
            panel = [
                r
                for r in appointment.related_visit.visit.all_requisitions
                if r.panel.name == metadata.panel_name
            ][0].panel
            requisition = self.get_or_create_requisition(panel=panel, user=user)
            if requisition.is_drawn != NO:
                item_count = requisition.item_count or 1
                for item in range(1, item_count + 1):
                    label = self.label_cls(requisition=requisition, user=user, item=item)
                    zpl_datas.append(label.render_as_zpl_data(copies=1))
            else:
                self.requisitions_not_printed.append(requisition)
        self.zpl_data = b"".join(zpl_datas)

    def get_or_create_requisition(self, panel=None, user=None):
        """Gets or creates a requisition.

        If created, the requisition created is incomplete; that is,
        is_drawn and drawn_datetime are None.
        """
        requisition_model_cls = django_apps.get_model(panel.requisition_model)
        related_visit_model_attr = requisition_model_cls.related_visit_model_attr()
        try:
            requisition_model_obj = requisition_model_cls.objects.get(
                panel=panel.panel_model_obj,
                **{f"{related_visit_model_attr}__appointment": self.appointment},
            )
        except ObjectDoesNotExist:
            requisition_model_obj = requisition_model_cls(
                user_created=user.username,
                panel=panel.panel_model_obj,
                **{related_visit_model_attr: self.appointment.visit},
            )
            requisition_model_obj.get_requisition_identifier()
            requisition_model_obj.save()
        return requisition_model_obj
