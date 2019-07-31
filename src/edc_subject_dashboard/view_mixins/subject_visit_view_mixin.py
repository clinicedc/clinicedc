from django.views.generic.base import ContextMixin
from django.core.exceptions import ObjectDoesNotExist
from edc_visit_schedule.models import VisitSchedule


class SubjectVisitViewMixinError(Exception):
    pass


class SubjectVisitViewMixin(ContextMixin):

    """Mixin to add the subject visit instance to the view.

    Declare together with the edc_appointment.AppointmentViewMixin.
    """

    visit_attr = "subjectvisit"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_visit = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            appointment = self.appointment
        except AttributeError as e:
            raise SubjectVisitViewMixinError(
                f"Mixin must be declared together with AppointmentViewMixin. Got {e}"
            )
        else:
            if appointment:
                try:
                    self.subject_visit = appointment.related_visit_model_attr
                except AttributeError as e:
                    raise SubjectVisitViewMixinError(
                        f"Visit model must have a OneToOne relation to appointment. "
                        f"Got {e}"
                    )
                else:
                    try:
                        self.subject_visit = appointment.visit
                    except AttributeError:
                        pass
                context.update(
                    subject_visit=self.subject_visit,
                    visit_schedule_pk=str(self.get_visit_schedule_pk(appointment)),
                )

        return context

    def get_visit_schedule_pk(self, appointment):
        """Returns a str(pk) from the VisitSchedule model.
        """
        visit_schedule_pk = ""
        opts = dict(
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
        )
        try:
            obj = VisitSchedule.objects.get(**opts)
        except ObjectDoesNotExist:
            pass
        else:
            visit_schedule_pk = str(obj.pk)
        return visit_schedule_pk
