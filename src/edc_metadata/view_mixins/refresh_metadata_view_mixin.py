from django.views.generic.base import ContextMixin


class RefreshMetadataViewMixin(ContextMixin):
    """
    Declare together with the edc_appointment.AppointmentViewMixin.

    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if self.appointment:
        #     pass
        return context
