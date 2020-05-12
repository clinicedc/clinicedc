from import_export.resources import ModelResource

from .models import Appointment


class AppointmentResource(ModelResource):
    class Meta:
        model = Appointment
