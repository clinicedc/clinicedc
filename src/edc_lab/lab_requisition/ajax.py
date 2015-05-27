from django.template.loader import render_to_string
from django.db.models import get_model
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register


@dajaxice_register
def print_label(request, app_label, model_name, requisition_identifier, message_label='print_message'):
    dajax = Dajax()
    requisition_model = get_model(app_label, model_name)
    if requisition_model.objects.filter(
                                requisition_identifier=requisition_identifier,
                                specimen_identifier__isnull=False,
                                ):
        requisition = requisition_model.objects.get(requisition_identifier=requisition_identifier)
        requisition_model.objects.print_label(requisition=requisition, remote_addr=request.META['REMOTE_ADDR'])

    elif requisition_model.objects.filter(
                            requisition_identifier=requisition_identifier,
                            specimen_identifier__isnull=True,
                            ):
        print_message = 'Label did not print, receive the specimen first to generate a specimen identifier.'
        li_class = "error"

    else:
        print_message = 'Label did not print, complete the requisition first.'
        li_class = "error"
    rendered = render_to_string('print_message.html', {'print_message': print_message, 'li_class': li_class})
    dajax.assign('#' + message_label, 'innerHTML', rendered)
    return dajax.json()
