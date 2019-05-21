from django.views.generic.base import ContextMixin


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
                context.update(subject_visit=self.subject_visit)
        return context
