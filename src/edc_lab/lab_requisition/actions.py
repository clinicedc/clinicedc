from datetime import datetime

from django.contrib import messages
from django.contrib.messages.api import MessageFailure

from edc.lab.lab_profile.exceptions import SpecimenError
from edc.lab.lab_profile.classes import site_lab_profiles

from lis.exim.lab_export.classes import ExportDmis
from lis.labeling.exceptions import LabelPrinterError


def flag_as_received(modeladmin, request, queryset, **kwargs):
    """ Flags specimen(s) as received and generates a globally specimen identifier and updates lab_clinic_api."""
    for qs in queryset:
        try:
            receive = None
            lab_profile = site_lab_profiles.get(qs._meta.object_name)
            receive = lab_profile().receive(qs)
            msg = 'Received {} as {}'.format(
                qs.requisition_identifier, receive.receive_identifier)
            try:
                messages.add_message(request, messages.SUCCESS, msg)
            except MessageFailure:  # except to get past testing with request=None
                print msg
        except SpecimenError as e:
            try:
                messages.add_message(request, messages.ERROR, str(e))
            except MessageFailure:  # except to get past testing with request=None
                print msg
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


def receive_on_dmis(modeladmin, request, queryset):
    export_dmis = ExportDmis()
    for qs in queryset:
        qs.comment, qs.is_lis = export_dmis.receive(qs)
        qs.save(update_fields=['is_lis'])
flag_as_not_labelled.short_description = "DMIS-receive: receive sample on the dmis (for BHHRL LAB STAFF ONLY)"


def print_requisition_label(modeladmin, request, requisitions):
    """ Prints a specimen label for a received specimen using the :func:`print_label`
    method attached to the requisition model.

    Requisitions must be 'received' before a label can be printed."""
    try:
        for requisition in requisitions:
            if requisition.is_receive:
                requisition.print_label(request)
            else:
                messages.add_message(request, messages.ERROR,
                                     'Requisition {0} has not been received. Labels '
                                     'cannot be printed until the specimen is '
                                     'received.'.format(requisition.requisition_identifier,))
    except LabelPrinterError as e:
        messages.add_message(request, messages.ERROR, e.value)

print_requisition_label.short_description = "LABEL: print requisition label"
