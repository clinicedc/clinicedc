from .constants import REQUIRED
from .metadata import CrfMetadataGetter, RequisitionMetadataGetter


def get_next_required_form(model_obj=None, appointment=None, model=None):
    """Returns the next required form based on the metadata.

    A form is a Crf or Requisition object from edc_visit_schedule.
    """
    next_form = None
    if model_obj:
        appointment = model_obj.visit.appointment
        model = model_obj._meta.label_lower
        visit = model_obj.visit.visit
    else:
        visit = appointment.visit.visit
    this_form = visit.get_form(model=model)
    for MetadataGetter in [CrfMetadataGetter, RequisitionMetadataGetter]:
        getter = MetadataGetter(appointment=appointment)
        metadata_obj = getter.next_object(
            show_order=this_form.show_order, entry_status=REQUIRED)
        if metadata_obj:
            next_form = visit.get_form(metadata_obj.model)
            return next_form
    return next_form
