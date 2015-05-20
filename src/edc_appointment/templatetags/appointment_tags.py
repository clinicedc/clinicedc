from django import template
from django.core.urlresolvers import reverse
from edc_appointment import Appointment


register = template.Library()


class ContinuationAppointmentAnchor(template.Node):
    """return a reverse url for a continjuation edc_appointment if the edc_appointment does not already exist"""
    def __init__(self, appointment, dashboard_type, extra_url_context):
        self.unresolved_appointment = template.Variable(appointment)
        self.unresolved_dashboard_type = template.Variable(dashboard_type)
        self.unresolved_extra_url_context = template.Variable(extra_url_context)

    def render(self, context):
        self.appointment = self.unresolved_appointment.resolve(context)
        self.dashboard_type = self.unresolved_dashboard_type.resolve(context)
        self.registered_subject = self.appointment.registered_subject
        self.extra_url_context = self.unresolved_extra_url_context

        if not self.extra_url_context:
            self.extra_url_context = ''

        # does a continuation edc_appointment exist? instance will be instance+1
        if (int(self.appointment.visit_instance) + 1) in [int(appointment.visit_instance) for appointment in Appointment.objects.filter(registered_subject=self.appointment.registered_subject)]:
            anchor = ''
        else:
            view = 'admin:%s_%s_add' % (self.appointment._meta.app_label, self.appointment._meta.module_name)
            try:
                # TODO: resolve error when using extra_url_context...give back variable name ???
                # rev_url = '%s?next=dashboard_url&dashboard_type=%s&registered_subject=%s&visit_definition=%s&visit_instance=%s%s' % (reverse(view), self.dashboard_type, self.edc_appointment.registered_subject.pk,self.edc_appointment.visit_definition.pk, str(int(self.edc_appointment.visit_instance) + 1), self.extra_url_context)
                rev_url = '%s?next=dashboard_url&dashboard_type=%s&registered_subject=%s&visit_definition=%s&visit_instance=%s' % (reverse(view), self.dashboard_type, self.appointment.registered_subject.pk, self.appointment.visit_definition.pk, str(int(self.appointment.visit_instance) + 1))
                anchor = '<A href="%s">continuation</A>' % (rev_url)
            except:
                raise TypeError('ContinuationAppointmentUrl Tag: NoReverseMatch while rendering reverse for %s. Is model registered in admin?' % (self.appointment._meta.module_name))

        return anchor


@register.tag(name='continuation_appointment_anchor')
def continuation_appointment_anchor(parser, token):
    """Compilation function for renderer ContinuationAppointmentUrl"""
    try:
        tag_name, appointment, dashboard_type, extra_url_context = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly 3 arguments" % token.contents.split()[0])
    return ContinuationAppointmentAnchor(appointment, dashboard_type, extra_url_context)


@register.filter(name='appt_type')
def appt_type(value):
    """Filters edc_appointment.appt_type."""
    if value == 'clinic':
        retval = 'Clin'
    elif value == 'telephone':
        retval = 'Tele'
    elif value == 'home':
        retval = 'Home'
    else:
        retval = None
    return retval
