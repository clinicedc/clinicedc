from datetime import datetime

from django.contrib import messages
from django.utils import timezone

from edc_lab.lab_profile.exceptions import SpecimenError
from edc_lab.lab_profile.classes import site_lab_profiles

from lab_requisition.requisition_label import RequisitionLabel
from lis.labeling.exceptions import LabelPrinterError


def flag_as_received(modeladmin, request, queryset, **kwargs):
    """ Flags specimen(s) as received and generates a globally
    specimen identifier and updates lab_clinic_api."""
    for qs in queryset:
        try:
            receive = None
            lab_profile = site_lab_profiles.get(qs._meta.object_name)
            receive = lab_profile().receive(qs)
            msg = 'Received {} as {}'.format(
                qs.requisition_identifier, receive.receive_identifier)
            messages.add_message(request, messages.SUCCESS, msg)
        except SpecimenError as e:
            messages.add_message(request, messages.ERROR, str(e))
            break
flag_as_received.short_description = "RECEIVE against requisition"


def flag_as_not_received(modeladmin, request, queryset):

    for qs in queryset:
        qs.is_receive = False
        qs.is_receive_datetime = datetime.today()
        qs.save(update_fields=['is_receive', 'is_receive_datetime'])
flag_as_not_received.short_description = "UNDO RECEIVE: flags as not received"


def flag_as_not_labelled(modeladmin, request, queryset):
    for qs in queryset:
        qs.is_labelled = False
        qs.save(update_fields=['is_labelled'])

flag_as_not_labelled.short_description = "UN-LABEL: flag as NOT labelled"


def print_requisition_label(modeladmin, request, requisitions):
    """ Prints a requisition label."""
    requisition_label = RequisitionLabel()
    try:
        for requisition in requisitions:
            if not requisition.requisition_identifier:
                messages.add_message(
                    request, messages.ERROR,
                    'Requisition identifier not set for {}. Cannot print label.'.format(requisition))
                break
            elif not requisition.is_receive:
                messages.add_message(request, messages.ERROR,
                                     'Requisition {0} has not been received. Labels '
                                     'cannot be printed until the specimen is '
                                     'received.'.format(requisition.requisition_identifier,))
                break
            else:
                requisition_label.print_label(request, requisition, copies=1)
                requisition.is_labelled = True
                requisition.is_labelled_datetime = timezone.now()
                requisition.save()
    except LabelPrinterError as e:
        messages.add_message(request, messages.ERROR, str(e))
print_requisition_label.short_description = "LABEL: print requisition label"
