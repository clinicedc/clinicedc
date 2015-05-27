from django.contrib.auth.decorators import login_required
from lab_requisition.classes import ClinicRequisitionLabel


@login_required
def ajax_print(request, requisition_identifier, requisition_model):
    if request.is_ajax():
        if requisition_identifier is not None:
            requisition = requisition_model.objects.get(requisition_identifier=requisition_identifier)
            for cnt in range(requisition.item_count_total, 0, -1):
                label = ClinicRequisitionLabel(
                    item_count=cnt,
                    requisition=requisition)
                label.print_label()
    return None
