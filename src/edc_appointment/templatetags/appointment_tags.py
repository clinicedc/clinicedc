from django import template
from django.urls import reverse
from django.apps import apps as django_apps
from django.urls.exceptions import NoReverseMatch

register = template.Library()


class ContinuationAppointmentUrlError(Exception):
    pass


class ContinuationAppointmentAnchor(template.Node):
    """Returns a reverse url for a continuation appointment
    if the appointment does not already exist.
    """

    def __init__(self, appointment, dashboard_type, extra_url_context):
        self.unresolved_appointment = template.Variable(appointment)
        self.unresolved_dashboard_type = template.Variable(dashboard_type)
        self.unresolved_extra_url_context = template.Variable(
            extra_url_context)

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').appointment_model

    def render(self, context):
        self.appointment = self.unresolved_appointment.resolve(context)
        self.dashboard_type = self.unresolved_dashboard_type.resolve(context)
        self.registered_subject = self.appointment.registered_subject
        self.extra_url_context = self.unresolved_extra_url_context

        if not self.extra_url_context:
            self.extra_url_context = ''

        # does a continuation appointment exist? instance will be instance+1
        visit_code_sequences = []
        for appointment in self.appointment_model.objects.filter(
                registered_subject=self.appointment.registered_subject):
            visit_code_sequences.append(int(appointment.visit_code_sequence))
        if (int(self.appointment.visit_code_sequence) + 1) in visit_code_sequences:
            anchor = ''
        else:
            view = (f'admin:{self.appointment._meta.app_label}_'
                    f'{self.appointment._meta.module_name}_add')
            try:
                url = reverse(view)
            except NoReverseMatch as e:
                raise ContinuationAppointmentUrlError(
                    'ContinuationAppointmentUrl Tag: NoReverseMatch while '
                    'rendering reverse for {self.appointment._meta.module_name}. '
                    f'Is model registered in admin? Got {e}.')
            else:
                # TODO: resolve error when using extra_url_context...give back
                # variable name ???
                visit_code_sequence = str(
                    int(self.appointment.visit_code_sequence) + 1)
                rev_url = (
                    f'{url}?next=dashboard_url&dashboard_type={self.dashboard_type}'
                    f'&registered_subject={self.appointment.registered_subject.pk}'
                    f'&visit_definition={self.appointment.visit_definition.pk}'
                    f'&visit_code_sequence={visit_code_sequence}')
                anchor = f'<A href="{rev_url}">continuation</A>'
        return anchor


@register.tag(name='continuation_appointment_anchor')
def continuation_appointment_anchor(parser, token):
    """Compilation function for renderer ContinuationAppointmentUrl.
    """
    try:
        _, appointment, dashboard_type, extra_url_context = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly 3 arguments" % token.contents.split()[0])
    return ContinuationAppointmentAnchor(appointment, dashboard_type, extra_url_context)


@register.filter(name='appt_type')
def appt_type(value):
    """Filters appointment.appt_type.
    """
    if value == 'clinic':
        retval = 'Clin'
    elif value == 'telephone':
        retval = 'Tele'
    elif value == 'home':
        retval = 'Home'
    else:
        retval = None
    return retval
