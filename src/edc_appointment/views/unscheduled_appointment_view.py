from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from django.views.generic.base import View

from ..creators import AppointmentInProgressError
from ..creators import InvalidParentAppointmentMissingVisitError
from ..creators import InvalidParentAppointmentStatusError
from ..creators import UnscheduledAppointmentCreator
from ..creators import UnscheduledAppointmentError


class UnscheduledAppointmentView(View):

    """A view that creates an unscheduled appointment and redirects to
    the subject dashboard.

    Source Url is usually reversed in the Appointment model wrapper.
    Redirect url name comes in kwargs.
    """

    unscheduled_appointment_cls = UnscheduledAppointmentCreator
    dashboard_template = 'subject_dashboard_template'

    def get(self, request, *args, **kwargs):
        try:
            creator = self.unscheduled_appointment_cls(**kwargs)
        except (ObjectDoesNotExist, UnscheduledAppointmentError,
                InvalidParentAppointmentMissingVisitError,
                InvalidParentAppointmentStatusError,
                AppointmentInProgressError) as e:
            messages.error(self.request, str(e))
        else:
            messages.success(
                self.request, mark_safe(
                    f'Appointment {creator.appointment} was created successfully.'))
            messages.warning(
                self.request, mark_safe(
                    f'Remember to adjust the appointment date and time on '
                    f'appointment {creator.appointment}.'))
        return HttpResponseRedirect(
            reverse(self.kwargs.get('redirect_url'),
                    kwargs={'subject_identifier': kwargs.get('subject_identifier')}))
