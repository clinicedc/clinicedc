from django.apps import apps as django_apps

from .next_url_mixin import NextUrlMixin


class AppointmentMixin(NextUrlMixin):

    """A view mixin to handle appointments on the dashboard.

    Expects `subject_identifier` or (`subject_identifier` and `appointment.pk`) from the url.

    For example:
        url(r'^dashboard/(?P<subject_identifier>' + subject_identifier + ')/(?P<appointment>[0-9a-f-]+)/',
            DashboardView.as_view(), name='dashboard_url'),
        url(r'^dashboard/(?P<subject_identifier>' + subject_identifier + ')/(?P<page>\d+)/',
            DashboardView.as_view(), name='dashboard_url'),
        url(r'^dashboard/(?P<subject_identifier>' + subject_identifier + ')/',
    """

    reverse_relation_visit_attr_name = 'subjectvisit'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.appointment = None

    def get(self, request, *args, **kwargs):
        """Overidden to appointment to the view instance."""
        try:
            appointment = self.appointment_model.objects.get(
                id=kwargs.get('appointment'))
        except self.appointment_model.DoesNotExist:
            pass
        else:
            self.appointment = self.appointment_wrapper(appointment)
            self.kwargs['appointment'] = self.appointment
        return super().get(request, *args, **kwargs)

    @property
    def next_url_parameters(self):
        """Add these additional parameters to the next url"""
        parameters = super().next_url_parameters
        parameters.update({
            'appointment': ['subject_identifier', 'appointment'],
            'visit': ['subject_identifier', 'appointment']})
        return parameters

    def appointment_wrapper(self, obj, **options):
        """Add next_url and if has a visit instance, wraps that too."""
        options.update({k: v for k, v in self.kwargs.items() if k not in options})
        obj.next_url = self.get_next_url('appointment', **options)
        obj = self.visit_wrapper(obj, **options)
        return obj

    def visit_wrapper(self, obj, **options):
        """Wraps visit instance attr of appointment and sets \'appointment.visit\' ."""
        options.update({k: v for k, v in self.kwargs.items() if k not in options})
        try:
            obj.visit = getattr(obj, self.reverse_relation_visit_attr_name)
        except AttributeError:
            obj.visit = None
        obj.visit_next_url = self.get_next_url('visit', **options)
        return obj

    @property
    def appointment_model(self):
        return django_apps.get_app_config('edc_appointment').model

    @property
    def appointments(self):
        """Returns a queryset of all appointments for this subject."""
        appointments = self.appointment_model.objects.filter(
            subject_identifier=self.subject_identifier).order_by('visit_code')
        return [self.appointment_wrapper(obj) for obj in appointments]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            appointments=self.appointments,
            appointment=self.appointment)
        return context
