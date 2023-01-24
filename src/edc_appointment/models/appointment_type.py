from edc_list_data.model_mixins import ListModelMixin


class AppointmentType(ListModelMixin):
    class Meta:
        verbose_name = "Appointment Type"
        verbose_name_plural = "Appointment Types"
