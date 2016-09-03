from django.shortcuts import redirect

from edc_appointment.models import Appointment
from edc_constants.constants import UNKEYED
from edc_metadata.models import LabEntry
from edc_metadata.models import RequisitionMetaData


def additional_requisition(request):
    appointment_id = _get_param(request, 'appointment_id')
    lab_entry_id = _get_param(request, 'panel')

    appointment = Appointment.objects.get(pk=appointment_id)
    lab_entry = LabEntry.objects.get(pk=lab_entry_id)
    requisition_meta_data = RequisitionMetaData.objects.get(
        appointment=appointment, lab_entry=lab_entry)
    requisition_meta_data.entry_status = UNKEYED
    requisition_meta_data.save()

    dashboard_type = _get_param(request, 'dashboard_type')
    dashboard_model = _get_param(request, 'dashboard_model')
    dashboard_id = _get_param(request, 'dashboard_id')
    show = _get_param(request, 'show')
    url = _get_param(request, 'url')

    return redirect(url,
                    dashboard_type=dashboard_type,
                    dashboard_model=dashboard_model,
                    dashboard_id=dashboard_id,
                    show=show)


def _get_param(request, param_key):
    return request.GET[param_key]
