from edc.subject.appointment.models import Appointment
from edc.subject.registration.admin import BaseRegisteredSubjectModelAdmin


class BaseOffStudyModelAdmin(BaseRegisteredSubjectModelAdmin):

    def save_model(self, request, obj, form, change):

        # delete future appointments
        visit_model_field = '%s__isnull' % self.visit_model_name
        Appointment.objects.filter(
            registered_subject=obj.registered_subject,
            appt_datetime__gt=obj.offstudy_date,
            **{visit_model_field: True}
        ).delete()

        super(BaseOffStudyModelAdmin, self).save_model(request, obj, form, change)
